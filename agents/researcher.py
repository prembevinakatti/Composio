import os
import csv
import json
import logging
import time
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from openai import OpenAI
import instructor
from composio import Composio
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppResearch(BaseModel):
    app_name: str = Field(description="Name of the application")
    website: str = Field(description="URL of the main website")
    category: str = Field(description="Broad category (e.g. CRM, Developer Tools, Analytics)")
    one_line_description: str = Field(description="A concise one-line description")
    auth_methods: List[str] = Field(description="List of authentication methods (e.g. ['OAuth2', 'API Key'])")
    self_serve_or_gated: str = Field(description="'self-serve' or 'gated'")
    gating_reason: Optional[str] = Field(None, description="Reason if gated (e.g. 'Enterprise only', 'Partnership required')")
    api_type: str = Field(description="Type of API (e.g. 'REST', 'GraphQL', 'SDK', 'none')")
    api_surface_size: str = Field(description="'small', 'medium', or 'large'")
    public_documentation: str = Field(description="URL to the official developer or API documentation")
    mcp_available: bool = Field(description="Whether a Model Context Protocol (MCP) server is available")
    mcp_link: Optional[str] = Field(None, description="URL to the MCP repository or documentation if available")
    buildability_verdict: str = Field(description="'high', 'medium', or 'low' indicating ease of turning into an AI agent toolkit today")
    primary_blocker: Optional[str] = Field(None, description="Main reason preventing easy integration, if any")
    evidence_links: List[str] = Field(description="List of URLs proving the claims")
    confidence_score: float = Field(description="Confidence score from 0.0 to 10.0")

class ResearchAgent:
    def __init__(self, mock=False):
        self.mock = mock
        if not self.mock:
            self.client = OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            self.instructor_client = instructor.from_openai(self.client, mode=instructor.Mode.JSON)
            self.model = "llama-3.3-70b-versatile"

    def research_app(self, app_name: str) -> AppResearch:
        if self.mock:
            return AppResearch(
                app_name=app_name,
                website=f"https://{app_name.lower().replace(' ', '')}.com",
                category="Developer Tools",
                one_line_description=f"A powerful platform for {app_name}",
                auth_methods=["OAuth2", "API Key"],
                self_serve_or_gated="self-serve",
                gating_reason=None,
                api_type="REST",
                api_surface_size="medium",
                public_documentation=f"https://docs.{app_name.lower().replace(' ', '')}.com",
                mcp_available=False,
                mcp_link=None,
                buildability_verdict="high",
                primary_blocker=None,
                evidence_links=[f"https://docs.{app_name.lower().replace(' ', '')}.com/api"],
                confidence_score=9.0
            )

        logger.info(f"Researching {app_name} with Groq...")
        try:

            logger.info(f"Extracting structured findings for {app_name}...")
            return self.instructor_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior AI engineer researching software applications for an AI Product Ops Assessment. Be honest when confidence is low. Never fabricate information. If information cannot be found, use 'unknown' (or empty/false) and explain why. Prioritize accuracy over completeness."},
                    {"role": "user", "content": f"Extract the required data fields for the application '{app_name}'. Use your internal knowledge."}
                ],
                response_model=AppResearch,
            )
        except Exception as e:
            logger.error(f"❌ Error researching {app_name}: {str(e)}")
            return AppResearch(
                app_name=app_name, website="unknown", category="unknown", one_line_description="unknown",
                auth_methods=["unknown"], self_serve_or_gated="unknown", gating_reason="unknown",
                api_type="none", api_surface_size="unknown", public_documentation="unknown",
                mcp_available=False, mcp_link=None, buildability_verdict="low",
                primary_blocker=f"Error encountered: {str(e)}", evidence_links=[], confidence_score=0.0
            )

    def run_pipeline(self, input_csv: str, output_csv: str, output_json: str, limit: int = None):
        apps = []
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'app_name' in row:
                    apps.append(row)

        if limit:
            apps = apps[:limit]

        results = []
        for i, row in enumerate(apps):
            app = row['app_name']
            data = self.research_app(app)
            
            data_dict = data.model_dump()
            # Merge original row data to ensure we return the original data
            for k, v in row.items():
                if v:
                    data_dict[k] = v
                    
            results.append(data_dict)
            
            if i < len(apps) - 1 and not self.mock:
                logger.info("⏳ Waiting to avoid rate limits...")
                time.sleep(3)

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        if results:
            with open(output_csv, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

if __name__ == "__main__":
    agent = ResearchAgent(mock=True)
    agent.run_pipeline("data/apps_seed.csv", "data/apps.csv", "data/apps.json", limit=2)
