# app/models/util_model.py

from pydantic import BaseModel
from fastapi import Query
from typing import Optional
from datetime import datetime

class UtilsState(BaseModel):
    in_bank: Optional[bool] = False
    using_camera: Optional[bool] = False
    using_mic: Optional[bool] = False

class Location(BaseModel):
    lat: float = Query(..., description="Latitude of the user's location")
    lng: float = Query(..., description="Longitude of the user's location")

class DocImageJSON(BaseModel):
    img: str

class UserData(BaseModel):
    id: str
    firstname: str
    lastname: str
    email: str
    phone: str
    age: int
    DOB: datetime
    user_profile: str


class UserContacts(BaseModel):
    name: str
    phone: str
