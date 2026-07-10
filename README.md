# AI Product Ops Assessment

An autonomous research pipeline that evaluates software applications for API surfaces, authentication patterns, and MCP readiness. The system extracts data using the Composio SDK and Groq models, verifies facts, generates insights, and produces a beautiful single-page HTML case study.

## Architecture

1. **Research Agent** (`agents/researcher.py`): Scrapes web and documentation using Composio SDK tools (e.g., Tavily or Exa integration via `ComposioToolSet`) to extract structured data into JSON/CSV.
2. **Verification Agent** (`agents/verifier.py`): Performs a second-pass review to check for hallucinations and correct mistakes using Groq.
3. **Insights Generator** (`agents/insights.py`): Analyzes the verified dataset to identify trends and opportunities.
4. **Report Generator** (`agents/report_generator.py`): Renders a custom HTML case study using Jinja2 templates and rich modern aesthetics.

## Setup Instructions

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Mac/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Composio**:
   You need to authenticate Composio and ensure the required apps are connected for the research agent.
   ```bash
   # Install Composio CLI (if not already installed)
   pip install composio-core
   
   # Login to Composio
   composio login
   
   # Add necessary integrations (e.g., Tavily, Exa, or standard web tools)
   composio add tavily
   ```

4. Configure Environment Variables. Ensure your `.env` file contains:
   ```env
   GROQ_API_KEY=your_groq_api_key
   # MOCK_MODE=True will bypass actual API calls and use mock data for testing
   MOCK_MODE=False
   ```

## How to Run

1. Ensure `data/apps_seed.csv` exists with a list of applications (has `app_name` column).
2. Run the pipeline:
   ```bash
   python main.py
   ```

## Output Artifacts

The system will generate several artifacts in the `data/` and `reports/` directories:
- `data/apps.json`: Raw extracted findings.
- `data/verification.json`: Verification report metrics.
- `data/insights.json`: Structured aggregations.
- `reports/case_study.html`: A beautiful, interactive dashboard visualizing the data.

## Deployment Instructions

The final deliverable is a static HTML dashboard located at `reports/case_study.html`.
Simply open `reports/case_study.html` in any modern web browser to view it locally, or deploy it to Vercel/Netlify.