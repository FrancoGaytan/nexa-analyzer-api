import uuid
from typing import List
from app.models.context import AnalyzeRequest, AnalyzeResponse, ClientContext

SUPPORTED_TEXT_EXT = {"txt", "text"}
SUPPORTED_PDF_EXT = {"pdf"}
SUPPORTED_DOCX_EXT = {"docx"}


def _extract_text_from_upload(filename: str, content_type: str, data: bytes) -> str:
    name_lower = filename.lower()
    # TXT
    if any(name_lower.endswith(f".{ext}") for ext in SUPPORTED_TEXT_EXT):
        try:
            return data.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="ignore")
    # PDF
    if any(name_lower.endswith(f".{ext}") for ext in SUPPORTED_PDF_EXT):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except Exception:
            return ""
    # DOCX
    if any(name_lower.endswith(f".{ext}") for ext in SUPPORTED_DOCX_EXT):
        try:
            import io
            from docx import Document
            doc = Document(io.BytesIO(data))
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paras)
        except Exception:
            return ""
    return ""


def _heuristic_objectives(text: str) -> List[str]:
    text_lower = text.lower()
    objectives = []
    if "optim" in text_lower:
        objectives.append("Optimizar procesos operativos")
    if "cost" in text_lower or "costo" in text_lower:
        objectives.append("Reducir costos")
    if "integr" in text_lower:
        objectives.append("Integrar sistemas existentes")
    if not objectives:
        objectives.append("Identificar objetivos clave del cliente")
    return objectives


def _heuristic_tech_reqs(text: str) -> List[str]:
    reqs = []
    tl = text.lower()
    if "api" in tl:
        reqs.append("Necesidad de APIs para integración")
    if "sap" in tl:
        reqs.append("Integración con ERP SAP")
    if "datos" in tl or "data" in tl:
        reqs.append("Gestión y calidad de datos")
    if not reqs:
        reqs.append("Identificar requerimientos técnicos detallados")
    return reqs


def _heuristic_future_ops(text: str) -> List[str]:
    ops = ["Automatizar análisis avanzados", "Explorar módulos predictivos"]
    if "machine learning" in text.lower():
        ops.append("Implementar modelos ML personalizados")
    return ops


def complete_analysis(client_name: str | None, raw_blocks: List[str]) -> AnalyzeResponse:
    combined = "\n".join(raw_blocks)
    ctx = ClientContext(
        client_name=client_name,
        business_overview=(combined[:500] + ("..." if len(combined) > 500 else "")) or "Sin contenido",
        objectives=_heuristic_objectives(combined),
        company_info=None,
        technical_requirements=_heuristic_tech_reqs(combined),
        project_timeline=None,
        additional_context_questions=["¿Cuáles son los KPIs específicos?", "¿Cuál es el presupuesto máximo?"] if combined else [],
        potential_future_opportunities=_heuristic_future_ops(combined),
    )
    return AnalyzeResponse(analysis_id=str(uuid.uuid4()), status="completed", summary=ctx)


def analyze_from_files(client_name: str | None, uploads: List[tuple[str, str, bytes]]) -> AnalyzeResponse:
    texts = []
    for filename, content_type, data in uploads:
        extracted = _extract_text_from_upload(filename, content_type, data)
        if extracted:
            texts.append(extracted)
    return complete_analysis(client_name, texts)
