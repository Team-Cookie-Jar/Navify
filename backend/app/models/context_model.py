# app/models/context_model.py

from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.util_model import UtilsState, Location

class ContextRequest(BaseModel):
    location: Location
    time: datetime
    env_field: UtilsState

class SuggestionResponse(BaseModel):
    list: List[str]
