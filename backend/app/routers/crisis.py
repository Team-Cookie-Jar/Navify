# app/routers/crisis.py

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Literal
from app.core.utils import User
from app.models.util_model import Location, UserContacts
import logging

router = APIRouter()

CRISIS_GUIDES = {
    "detained": [
        "Stay calm.",
        "Do not resist authorities.",
        "Contact your embassy or consulate.",
        "Request legal aid or a translator.",
        "Share your location with a trusted contact."
    ],
    "scammed": [
        "Do not send more money.",
        "Record all contact details of the scammer.",
        "Report the scam to local police.",
        "Contact your bank to block transactions.",
        "Inform your embassy if identity documents were compromised."
    ],
    "lost": [
        "Move to a safe, well-lit area.",
        "Use your phone to identify landmarks.",
        "Ask for help at a hotel or police station.",
        "Share your location with a trusted contact."
    ]
}

class CrisisRequest(BaseModel):
    uuid: str = Query(..., description="User ID of the person in crisis")
    location: Location = Query(..., description="Location of the user in crisis")
    crisis_type: Literal["detained", "scammed", "lost"] = Query(..., description="Type of crisis (e.g., 'detained', 'scammed')")


class CrisisResponse(BaseModel):
    steps: List[str]
    contacts: List[UserContacts]


@router.post("/crisis/trigger", response_model=CrisisResponse)
def generate_crisis_response(request: CrisisRequest):

    lat = request.location.lat
    lng = request.location.lng
    logging.info(f"User {request.uuid} requested help for '{request.crisis_type}' at {lat},{lng}")

    try:
        if not request.uuid or not request.location or not request.crisis_type:
            return JSONResponse(status_code=400, content={"error": "User ID, location, and crisis type are required"})


        user = User()
        userdata = user.fromUUID(uuid=request.uuid)
        steps = CRISIS_GUIDES.get(request.crisis_type.lower())
        contacts = {"name": f"{userdata.firstname} {userdata.lastname}", "phone": userdata.phone}

        if not steps:
            steps = ["We are unable to provide specific guidance at this time. Please seek local help immediately."]
        
        return {
            "steps": steps,
            "contacts": [contacts]
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

