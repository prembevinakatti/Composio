import os
from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv(override=True)

class AppResearch(BaseModel):
    app_name: str
    website: str
    category: str
    one_line_description: str
    auth_methods: List[str]
    self_serve_or_gated: str
    gating_reason: Optional[str] = None
    api_type: str
    api_surface_size: str
    public_documentation: str
    mcp_available: bool
    mcp_link: Optional[str] = None
    buildability_verdict: str
    primary_blocker: Optional[str] = None
    evidence_links: List[str]
    confidence_score: float

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
instructor_client = instructor.from_openai(client, mode=instructor.Mode.JSON)

try:
    resp = instructor_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior AI engineer."},
            {"role": "user", "content": "Extract the required data fields for the application 'Salesforce'. Use your internal knowledge."}
        ],
        response_model=AppResearch,
    )
    print(resp.model_dump_json(indent=2))
except Exception as e:
    print(f"Error: {e}")
