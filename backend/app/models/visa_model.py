# app/models/visa_model.py

from pydantic import BaseModel
from typing import Optional, List
from app.models.util_model import DocImageJSON

class ViseAnalysisRequest(BaseModel):
    docJSON: Optional[DocImageJSON] = None
    docDataUrl: Optional[str] = None

class VisAnalysisResponse(BaseModel):
    status: str
    issus: List[str]
    confidence: float

class VisaSimulateRequest(BaseModel):
    some_user_changes: Optional[bool] = False

class VisaSimulateResponse(BaseModel):
    current_path: str
    new_path: str
    legal_basis: str
