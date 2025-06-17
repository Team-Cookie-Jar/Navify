# app/models/assistant_model.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FromVoiceRequest(BaseModel):
    user_id: Optional[str] = None
    time: datetime
    msg: str

class FromVoiceResponse(BaseModel):
    response: str

class FromDocRequest(BaseModel):
    dataUrl: str

class FromDocResponse(BaseModel):
    doc_type: str
    Key_clauses: List[str]
    summary: str
