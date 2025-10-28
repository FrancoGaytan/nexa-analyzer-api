from fastapi.testclient import TestClient
from app.main import app
import json
import os

# Ensure OPENAI_API_KEY present for agent initialization during tests
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.services.agentic.coordinator_agent import CoordinatorAgent

def _fake_pipeline_result(client_name: str):
    return {
        "final_json": {
            "client_name": client_name,
            "industry": "Logistics",
            "location": "Unknown",
            "engagement_age": 0,
            "business_overview": "Synthetic overview for tests",
            "objectives": ["Reducir costos", "Optimizar cadena"],
            "company_info": None,
            "additional_context_questions": ["¿Cuál es el presupuesto?"],
            "potential_future_opportunities": ["Analítica avanzada"],
        },
        "log": ["Ingest", "Extract", "Validate"]
    }

async def _mock_run_pipeline(self, file_path=None, url=None, enrich_allowed=False):
    # Use file_path/url only to derive client name optionally, else default
    return _fake_pipeline_result("ACME Corp" if file_path or url else "ACME Corp")

CoordinatorAgent.run_pipeline = _mock_run_pipeline

client = TestClient(app)

def test_context_single_endpoint_text_blocks():
    blocks = ["ACME busca optimizar su cadena de suministro."]
    r = client.post(
        "/context/analyze",
        data={
            "client_name": "ACME Corp",
            "raw_text_blocks": json.dumps(blocks),
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME Corp"
    assert data["summary"]["business_overview"] == "Synthetic overview for tests"
    assert data["summary"]["potential_future_opportunities"] == ["Analítica avanzada"]

def test_context_single_endpoint_file_upload_txt():
    content = "ACME quiere integrar ERP SAP y reducir costos"
    files = {"files": ("brief.txt", content, "text/plain")}
    r = client.post("/context/analyze", data={"client_name": "ACME"}, files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME Corp"
    assert data["summary"]["objectives"] == ["Reducir costos", "Optimizar cadena"]
