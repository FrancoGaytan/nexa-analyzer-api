from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.models.context import AnalyzeResponse
from app.services.context_analyzer_service import analyze_from_files, complete_analysis

router = APIRouter(prefix="/context", tags=["context"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    client_name: str | None = Form(default=None),
    raw_text_blocks: str | None = Form(default=None),  # JSON string or line-separated
    files: List[UploadFile] | None = File(default=None)
):
    uploads = []
    if files:
        for f in files:
            data = await f.read()
            uploads.append((f.filename, f.content_type or "application/octet-stream", data))
        return analyze_from_files(client_name, uploads)

    blocks: List[str] = []
    if raw_text_blocks:
        # Try to parse as JSON array; if fails, split lines
        import json
        try:
            parsed = json.loads(raw_text_blocks)
            if isinstance(parsed, list):
                blocks = [str(x) for x in parsed]
            else:
                blocks = [str(parsed)]
        except Exception:
            blocks = [s for s in raw_text_blocks.splitlines() if s.strip()]

    return complete_analysis(client_name, blocks)
