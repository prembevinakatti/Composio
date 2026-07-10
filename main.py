import os
import logging
from dotenv import load_dotenv

from agents.researcher import ResearchAgent
from agents.verifier import VerificationAgent
from agents.insights import InsightsGenerator
from agents.report_generator import ReportGenerator

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting AI Product Ops Assessment Pipeline...")
    
    # Configuration
    MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "yes")
    SEED_CSV = "data/apps_seed.csv"
    APPS_CSV = "data/apps.csv"
    APPS_JSON = "data/apps.json"
    VERIFICATION_REPORT = "data/verification.json"
    HUMAN_REVIEW_CSV = "data/human_review.csv"
    INSIGHTS_JSON = "data/insights.json"
    CASE_STUDY_TEMPLATE = "case_study_template.html"
    CASE_STUDY_OUTPUT = "reports/case_study.html"

    # 1. Research Phase
    logger.info("--- PHASE 1: RESEARCH ---")
    researcher = ResearchAgent(mock=MOCK_MODE)
    researcher.run_pipeline(SEED_CSV, APPS_CSV, APPS_JSON, limit=100)

    # 2. Verification Phase
    logger.info("--- PHASE 2: VERIFICATION ---")
    verifier = VerificationAgent(mock=MOCK_MODE)
    verifier.run_pipeline(APPS_JSON, VERIFICATION_REPORT, HUMAN_REVIEW_CSV)

    # 3. Insights Generation Phase
    logger.info("--- PHASE 3: INSIGHTS ---")
    insights_gen = InsightsGenerator()
    insights_gen.generate_insights(APPS_JSON, INSIGHTS_JSON)

    # 4. Report Generation Phase
    logger.info("--- PHASE 4: REPORT GENERATION ---")
    report_gen = ReportGenerator(template_dir="reports")
    report_gen.generate_report(
        template_name=CASE_STUDY_TEMPLATE,
        apps_json=APPS_JSON,
        insights_json=INSIGHTS_JSON,
        verification_json=VERIFICATION_REPORT,
        output_html=CASE_STUDY_OUTPUT
    )

    logger.info(f"Pipeline completed successfully. Check {CASE_STUDY_OUTPUT} for the final case study.")

if __name__ == "__main__":
    main()
