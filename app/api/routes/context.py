import os
from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.agentic.coordinator_agent import CoordinatorAgent
from app.models.context import AnalyzeResponse, ClientContext
import tempfile


router = APIRouter(prefix="/context", tags=["context"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    client_name: str | None = Form(default=None),
    raw_text_blocks: str | None = Form(default=None),  # JSON string or line-separated
    files: List[UploadFile] | None = File(default=None),
    enrich_allowed: bool = Form(default=False)
):
    coordinator = CoordinatorAgent()
    # If files are uploaded, save to temp and run pipeline
    if files:
        if len(files) > 5:
            return {"detail": "You can upload up to 5 files only."}
        temp_paths = []
        for f in files:
            suffix = os.path.splitext(f.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await f.read())
                temp_paths.append(tmp.name)
        # Process all files together
        result = await coordinator.run_pipeline(file_paths=temp_paths, enrich_allowed=enrich_allowed)
        # Clean up temp files
        for path in temp_paths:
            os.remove(path)
        # Convert result to AnalyzeResponse
        return _to_analyze_response(result, client_name)

    # If raw text blocks are provided, write to temp txt and run pipeline
    if raw_text_blocks:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(raw_text_blocks)
            tmp_path = tmp.name
        result = await coordinator.run_pipeline(file_path=tmp_path, enrich_allowed=enrich_allowed)
        os.remove(tmp_path)
        return _to_analyze_response(result, client_name)

    return {"detail": "No input provided."}


# Helper to convert pipeline output to AnalyzeResponse
def _to_analyze_response(result, client_name):
    final = result.get("final_json", {})
    ctx = ClientContext(**{k: final.get(k) for k in ClientContext.model_fields})
    return AnalyzeResponse(
        analysis_id="autogen-pipeline",
        status="completed" if final else "error",
        summary=ctx
    )
