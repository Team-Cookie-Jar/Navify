# app/models/crisis_model.py

from pydantic import BaseModel
from typing import List
from app.models.util_model import Location, UserContacts

class CrisisTriggerRequest(BaseModel):
    user_id: int
    location: Location
    crisis_type: str

class CrisisTriggerResponse(BaseModel):
    steps: List[str]
    contacts: List[UserContacts]
