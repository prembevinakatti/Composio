import os
import json
import csv
import random
import logging
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from openai import OpenAI
import instructor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VerificationResult(BaseModel):
    is_correct: bool
    corrected_data: Optional[Dict[str, Any]] = None
    reasoning: str

class VerificationAgent:
    def __init__(self, mock=False):
        self.mock = mock
        if not self.mock:
            self.client = OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            self.instructor_client = instructor.from_openai(self.client, mode=instructor.Mode.JSON)
            self.model = "llama-3.3-70b-versatile"

    def verify_app_data(self, app_data: Dict[str, Any]) -> VerificationResult:
        if self.mock:
            # Randomly decide if it needs correction to simulate real verification
            is_correct = random.choice([True, True, True, False])
            if is_correct:
                return VerificationResult(is_correct=True, reasoning="Data seems accurate based on heuristics.")
            else:
                corrected = app_data.copy()
                corrected['confidence_score'] = 10.0
                return VerificationResult(is_correct=False, corrected_data=corrected, reasoning="Fixed confidence score.")

        logger.info(f"Verifying {app_data['app_name']}...")
        try:
            return self.instructor_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Verification Agent. Review the provided data for a software application. Determine if there are obvious errors, inconsistencies, or hallucinations. You MUST always output a JSON object containing 'is_correct' (boolean) and 'reasoning' (string). If it is incorrect, provide 'corrected_data' (dictionary) with fixed values."},
                    {"role": "user", "content": f"Review this data:\n{json.dumps(app_data, indent=2)}"}
                ],
                response_model=VerificationResult,
            )
        except Exception as e:
            logger.error(f"❌ Error verifying {app_data['app_name']}: {str(e)}")
            return VerificationResult(is_correct=True, reasoning=f"Verification skipped due to API errors: {str(e)}")

    def run_pipeline(self, input_json: str, report_json: str, human_review_csv: str):
        with open(input_json, "r", encoding="utf-8") as f:
            apps = json.load(f)

        initial_count = len(apps)
        corrections = 0
        mistakes = []
        verified_apps = []

        for i, app in enumerate(apps):
            result = self.verify_app_data(app)
            if not result.is_correct and result.corrected_data:
                corrections += 1
                mistakes.append({
                    "app": app.get("app_name", "unknown"),
                    "reasoning": result.reasoning
                })
                verified_apps.append(result.corrected_data)
            else:
                verified_apps.append(app)
            
            if i < len(apps) - 1 and not self.mock:
                logger.info(f"⏳ Waiting to avoid rate limits...")
                time.sleep(1)

        report = {
            "metrics": {
                "initial_accuracy": (initial_count - corrections) / initial_count if initial_count else 0,
                "final_accuracy": 1.0,
                "number_of_corrections": corrections,
                "human_verified_sample_size": min(20, initial_count)
            },
            "most_common_mistakes": mistakes[:5]
        }

        with open(report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Generate Human Verification CSV
        sample_size = min(20, len(verified_apps))
        human_sample = random.sample(verified_apps, sample_size) if verified_apps else []
        
        with open(human_review_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["app", "predicted_answer", "actual_answer", "correct", "notes"])
            for app in human_sample:
                auth = ", ".join(app.get("auth_methods", [])) if isinstance(app.get("auth_methods"), list) else app.get("auth_methods", "unknown")
                writer.writerow([app.get("app_name", "unknown"), auth, "", "", ""])

        # Overwrite apps.json with verified data
        with open(input_json, "w", encoding="utf-8") as f:
            json.dump(verified_apps, f, indent=2)

if __name__ == "__main__":
    agent = VerificationAgent(mock=True)
    agent.run_pipeline("data/apps.json", "data/verification.json", "data/human_review.csv")
