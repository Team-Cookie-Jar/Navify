# app/routers/context.py

from fastapi import APIRouter, HTTPException
from app.models.context_model import ContextRequest, SuggestionResponse
from app.models.util_model import Location
import requests
from dateutil import parser as dt_parser

# Use on Linux
"""
try:
    from app.core.opening_hours import OpeningHours
except ImportError:
    OpeningHours = None  # Fallback if the package isn't installed
"""

# Alternative

class OpeningHours:
    def __init__(self, opening_hours_str):
        self.opening_hours_str = opening_hours_str

    def is_open(self, user_time):
        return True


router = APIRouter()

OVERPASS_URL = "http://overpass-api.de/api/interpreter"
amenities = ["language_schools", "job_centre", "hospital", "social_facility", "lawyer", "community_centre",
    "place_of_worship", "shop", "supermarket", "school", "bank", "internet_cafe"]

def query_overpass(location: Location, radius: int = 100, amenity_type: str = "bank"):
    lat = location.lat
    lng = location.lng
    """
    Query the Overpass API for amenities of the given type around the lat/lng within the radius (meters).
    """
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="{amenity_type}"](around:{radius},{lat},{lng});
      way["amenity"="{amenity_type}"](around:{radius},{lat},{lng});
      relation["amenity"="{amenity_type}"](around:{radius},{lat},{lng});
    );
    out center tags;
    """
    response = requests.post(OVERPASS_URL, data={"data": query})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail={"error": "Failed to fetch data from Overpass API"})
    
    return response.json()

def is_open_now(opening_hours_str, user_time_iso):
    if not opening_hours_str or not OpeningHours:
        return True  # Assume open if no info or lib not installed
    try:
        oh = OpeningHours(opening_hours_str)
        user_time = dt_parser.isoparse(user_time_iso)
        return oh.is_open(user_time)
    except Exception:
        return True  # Fallback to open if parsing fails

def generate_suggestion(tags, time, env):
    suggestions = []
    amenity = tags.get('amenity', '')
    name = tags.get("name", "Unknown")
    opening_hours = tags.get("opening_hours", None)

    # Check if amenity is open
    if not is_open_now(opening_hours, time):
        return suggestions  # Don't suggest if closed

    if amenity == "bank" and getattr(env, "in_bank", False):
        suggestions.append(f"Need help filling a bank form at {name}?")
        suggestions.append("Tap to scan your document for quick assistance.")
    elif amenity == "hospital":
        suggestions.append(f"Nearby hospital: {name}. Need help with health insurance or emergency contacts?")
    elif amenity == "job_centre":
        suggestions.append(f"Job centre nearby: {name}. Want tips for job applications?")
    elif amenity == "language_school":
        suggestions.append(f"Language School nearby: {name}. Need help with language learning resources?")
    elif amenity == "social_facility":
        suggestions.append(f"Social facility nearby: {name}. ")
    elif amenity == "lawyer":
        suggestions.append(f"Lawyer nearby: {name}. ")
    elif amenity == "community_centre":
        suggestions.append(f"Community Centre nearby: {name}. ")
    elif amenity == "place_of_worship":
        suggestions.append(f"Place of worship nearby: {name}. ")
    elif amenity == "shop":
        suggestions.append(f"Stall nearby: {name}. ")
    elif amenity == "supermarket":
        suggestions.append(f"Supermarket nearby: {name}. ")
    elif amenity == "internet_cafe":
        suggestions.append(f"Internet cafe nearby: {name}. ")
    return suggestions


@router.post("/context/detect", response_model=SuggestionResponse)
async def detect_context(req: ContextRequest):
    suggestions = []
    location = req.location
    time = req.time
    env = req.env_field

    for amenity in amenities:
        data = query_overpass(location=location, radius=100, amenity_type=amenity)
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            if element.get("type") in ("way", "relation"):
                loc = element.get("center", {})
            else:
                loc = {"lat": element.get("lat"), "lon": element.get("lon")}

            if not loc.get("lat") or not loc.get("lon"):
                continue

            suggestions.extend(generate_suggestion(tags, time, env))

    suggestions = [s for s in set(suggestions) if s]

    return SuggestionResponse(
        list = suggestions
    )