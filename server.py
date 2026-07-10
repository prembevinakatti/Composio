import os
import logging
import asyncio
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import json

# Import your existing pipeline classes
from agents.researcher import ResearchAgent
from agents.verifier import VerificationAgent
from agents.insights import InsightsGenerator
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Main loop reference for threadsafe queue inserts
main_loop = None
log_queue = None
log_history = []

@app.on_event("startup")
async def startup_event():
    global main_loop, log_queue
    main_loop = asyncio.get_running_loop()
    log_queue = asyncio.Queue()

# Custom Log Handler
class SSEHandler(logging.Handler):
    def emit(self, record):
        if main_loop is None or log_queue is None: return
        log_entry = self.format(record)
        log_history.append(log_entry)
        # Put the log string into the queue safely from any thread
        asyncio.run_coroutine_threadsafe(log_queue.put(log_entry), main_loop)

# Set up the SSE logger
sse_handler = SSEHandler()
sse_handler.setFormatter(logging.Formatter('%(message)s'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Don't add multiple times if hot-reloading
if not any(isinstance(h, SSEHandler) for h in logger.handlers):
    logger.addHandler(sse_handler)

# Create static dir if doesn't exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

def run_pipeline_task(mock_mode: bool):
    try:
        SEED_CSV = "data/apps_seed.csv"
        APPS_CSV = "data/apps.csv"
        APPS_JSON = "data/apps.json"
        VERIFICATION_REPORT = "data/verification.json"
        HUMAN_REVIEW_CSV = "data/human_review.csv"
        INSIGHTS_JSON = "data/insights.json"

        # 1. Research Phase
        logging.info("--- PHASE 1: RESEARCH ---")
        researcher = ResearchAgent(mock=mock_mode)
        researcher.run_pipeline(SEED_CSV, APPS_CSV, APPS_JSON, limit=100)

        # 2. Verification Phase
        logging.info("--- PHASE 2: VERIFICATION ---")
        verifier = VerificationAgent(mock=mock_mode)
        verifier.run_pipeline(APPS_JSON, VERIFICATION_REPORT, HUMAN_REVIEW_CSV)

        # 3. Insights Generation Phase
        logging.info("--- PHASE 3: INSIGHTS ---")
        insights_gen = InsightsGenerator()
        insights_gen.generate_insights(APPS_JSON, INSIGHTS_JSON)

        logging.info("PIPELINE_COMPLETE")
    except Exception as e:
        logging.error(f"Error during pipeline execution: {e}")
        logging.info("PIPELINE_ERROR")

@app.post("/upload")
async def upload_and_start(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    global log_history
    log_history.clear()
    if log_queue:
        while not log_queue.empty():
            log_queue.get_nowait()
            
    # Save the uploaded CSV
    os.makedirs("data", exist_ok=True)
    file_location = f"data/apps_seed.csv"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Check if mock mode is on
    mock_mode = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "yes")
    
    # Start the pipeline in the background
    background_tasks.add_task(run_pipeline_task, mock_mode)
    
    return {"message": "Pipeline started"}

async def log_generator():
    if log_queue is None: return
    
    # Yield history first to avoid race conditions
    for msg in log_history:
        yield f"data: {msg}\n\n"
        
    while True:
        log_message = await log_queue.get()
        yield f"data: {log_message}\n\n"
        if log_message == "PIPELINE_COMPLETE" or log_message == "PIPELINE_ERROR":
            break

@app.get("/stream")
async def stream_logs():
    return StreamingResponse(log_generator(), media_type="text/event-stream")

@app.get("/results")
async def get_results():
    try:
        with open("data/apps.json", "r") as f:
            apps = json.load(f)
        with open("data/insights.json", "r") as f:
            insights = json.load(f)
        with open("data/verification.json", "r") as f:
            verification = json.load(f)
            
        return {
            "apps": apps,
            "insights": insights,
            "verification": verification
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
