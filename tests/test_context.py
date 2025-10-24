from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_context_single_endpoint_text_blocks():
    blocks = [
        "ACME busca optimizar su cadena de suministro.",
        "El presupuesto es limitado y hay restricciones de tiempo.",
    ]
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
    assert "business_overview" in data["summary"]
    assert "potential_future_opportunities" in data["summary"]

def test_context_single_endpoint_file_upload_txt():
    content = "ACME quiere integrar ERP SAP y reducir costos"
    files = {"files": ("brief.txt", content, "text/plain")}
    r = client.post("/context/analyze", data={"client_name": "ACME"}, files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["summary"]["client_name"] == "ACME"
    assert any("SAP" in obj or "Integrar" in obj for obj in data["summary"]["objectives"]) or len(data["summary"]["objectives"]) > 0
