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
    # Accept file_paths for multi-file support
    def get_client_name():
        if file_path or url:
            return "ACME Corp"
        if hasattr(self, 'file_paths') or 'file_paths' in self.__dict__:
            return "ACME Corp"
        return "ACME Corp"
    return _fake_pipeline_result(get_client_name())

async def _mock_run_pipeline(self, file_path=None, file_paths=None, url=None, enrich_allowed=False):
    # Use file_path, file_paths, or url to derive client name optionally, else default
    return _fake_pipeline_result("ACME Corp")

CoordinatorAgent.run_pipeline = _mock_run_pipeline
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


def test_context_multiple_file_upload_txt():
    contents = [
        ("brief1.txt", "ACME wants to reduce costs and integrate SAP ERP", "text/plain"),
        ("brief2.txt", "ACME seeks advanced analytics and supply chain optimization", "text/plain"),
    ]
    files = [("files", (name, content, mime)) for name, content, mime in contents]
    r = client.post(
        "/context/analyze",
        data={"client_name": "ACME"},
        files=files
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME Corp"
    assert "Synthetic overview for tests" in data["summary"]["business_overview"]
    assert isinstance(data["summary"]["objectives"], list)
    assert r.status_code == 200
    data = r.json()


    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME Corp"
    assert data["summary"]["objectives"] == ["Reducir costos", "Optimizar cadena"]


# Test multiple file upload (up to 5)
def test_context_multiple_file_upload_txt():
    contents = [
        ("brief1.txt", "ACME wants to reduce costs and integrate SAP ERP", "text/plain"),
        ("brief2.txt", "ACME seeks advanced analytics and supply chain optimization", "text/plain"),
    ]
    files = [("files", (name, content, mime)) for name, content, mime in contents]
    r = client.post(
        "/context/analyze",
        data={"client_name": "ACME"},
        files=files
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME Corp"
    assert "Synthetic overview for tests" in data["summary"]["business_overview"]
    assert isinstance(data["summary"]["objectives"], list)


def test_context_multiple_file_upload_txt():
    contents = [
        ("brief1.txt", "ACME wants to reduce costs and integrate SAP ERP", "text/plain"),
        ("brief2.txt", "ACME seeks advanced analytics and supply chain optimization", "text/plain"),
    ]
    files = [("files", (name, content, mime)) for name, content, mime in contents]
    r = client.post(
        "/context/analyze",
        data={"client_name": "ACME"},
        files=files
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME Corp"
    assert "Synthetic overview for tests" in data["summary"]["business_overview"]
    assert isinstance(data["summary"]["objectives"], list)
