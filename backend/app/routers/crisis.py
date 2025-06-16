# app/routers/crisis.py

from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

@router.post("/crisis/trigger", response_model=dict)
def trigger_crisis(
    user_id: str = Query(..., description="User ID of the person in crisis"),
    location: str = Query(..., description="Location of the user in crisis"),
    crisis_type: str = Query(..., description="Type of crisis (e.g., 'detained', 'scammed')")
):
    try:
        # Placeholder for actual crisis handling logic
        if not user_id or not location or not crisis_type:
            raise HTTPException(status_code=400, detail={"error": "User ID, location, and crisis type are required"})

        # Simulated response
        return {
            "steps": ["Stay calm", "Do not sign anything", "Request legal aid"],
            "contacts": [
                { "name": "A. Okonkwo, Esq", "phone": "+1-202-555-0101" }
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

