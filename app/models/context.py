from typing import List, Optional
from pydantic import BaseModel

class ClientContext(BaseModel):
    client_name: Optional[str] = None
    business_overview: str
    objectives: List[str] = []
    company_info: Optional[str] = None
    technical_requirements: List[str] = []
    project_timeline: Optional[str] = None
    additional_context_questions: List[str] = []
    potential_future_opportunities: List[str] = []

class AnalyzeRequest(BaseModel):
    client_name: Optional[str] = None
    raw_text_blocks: List[str] = []

class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: str
    summary: ClientContext