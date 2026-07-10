import os
import json
import logging
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, template_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_report(self, template_name: str, apps_json: str, insights_json: str, verification_json: str, output_html: str):
        logger.info("Loading data for report generation...")
        
        with open(apps_json, "r", encoding="utf-8") as f:
            apps = json.load(f)
            
        with open(insights_json, "r", encoding="utf-8") as f:
            insights = json.load(f)
            
        with open(verification_json, "r", encoding="utf-8") as f:
            verification = json.load(f)

        logger.info(f"Rendering template {template_name}...")
        template = self.env.get_template(template_name)
        
        html_content = template.render(
            apps=apps,
            insights=insights,
            verification=verification
        )

        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Report generated successfully at {output_html}")

if __name__ == "__main__":
    generator = ReportGenerator(template_dir="reports")
    generator.generate_report(
        template_name="case_study_template.html",
        apps_json="data/apps.json",
        insights_json="data/insights.json",
        verification_json="data/verification.json",
        output_html="reports/case_study.html"
    )
