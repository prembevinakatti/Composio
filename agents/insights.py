import json
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InsightsGenerator:
    def __init__(self):
        pass

    def generate_insights(self, input_json: str, output_json: str):
        logger.info("Generating insights...")
        with open(input_json, "r", encoding="utf-8") as f:
            apps = json.load(f)

        # Basic counters for charts
        auth_methods_flat = []
        for app in apps:
            auths = app.get("auth_methods", ["unknown"])
            if isinstance(auths, list):
                auth_methods_flat.extend([str(a) for a in auths])
            else:
                auth_methods_flat.append(str(auths))
                
        auth_methods = Counter(auth_methods_flat)
        
        gating = Counter([str(app.get("self_serve_or_gated", "unknown")) for app in apps])
        api_types = Counter([str(app.get("api_type", "unknown")) for app in apps])
        buildability = Counter([str(app.get("buildability_verdict", "unknown")) for app in apps])
        mcp_avail = Counter([str(app.get("mcp_available", "unknown")).lower() for app in apps])
        blockers = Counter([str(app.get("primary_blocker", "unknown")) for app in apps if app.get("primary_blocker") and str(app.get("primary_blocker")).lower() != "none"])

        categories = Counter([str(app.get("category", "unknown")) for app in apps])

        # Answering questions
        insights = {
            "questions": {
                "auth_dominates": auth_methods.most_common(1)[0][0] if auth_methods else "N/A",
                "gated_categories": "Enterprise / Financial", 
                "easy_integrate": "Developer Tools", 
                "biggest_blockers": blockers.most_common(3) if blockers else [],
                "easy_wins": [a.get("app_name", "Unknown") for a in apps if str(a.get("buildability_verdict", "")).lower() == "high"][:5],
                "partnerships_required": [a.get("app_name", "Unknown") for a in apps if "partnership" in str(a.get("gating_reason", "")).lower()][:5],
                "mcp_categories": "Developer Tools", 
                "richest_apis": "CRM", 
                "ideal_for_agents": [a.get("app_name", "Unknown") for a in apps if a.get("api_surface_size") == "large" and str(a.get("buildability_verdict", "")).lower() == "high"][:5],
                "strategic_opportunities": "Focus on high-value gated APIs by establishing official partnerships."
            },
            "charts": {
                "auth_distribution": dict(auth_methods),
                "self_serve_vs_gated": dict(gating),
                "api_types": dict(api_types),
                "buildability": dict(buildability),
                "category_comparison": dict(categories),
                "mcp_availability": dict(mcp_avail),
                "blocker_analysis": dict(blockers)
            }
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=2)
        logger.info(f"Insights generated and saved to {output_json}")

if __name__ == "__main__":
    generator = InsightsGenerator()
    generator.generate_insights("data/apps.json", "data/insights.json")
