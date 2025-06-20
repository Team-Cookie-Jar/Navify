# app/routers/visa.py

from fastapi import APIRouter, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
import base64
from app.core.ai_engine import analyze_document, simulate_what_if
from app.core.utils import decode_base64_json

router = APIRouter()

class DocumentInput(BaseModel):
    document_json: Optional[dict] = None
    document_base64: Optional[str] = None
    scenario: Optional[dict] = None

@router.post("/visa/analyse", response_model=Dict)
def analyse_visa_document(doc: DocumentInput):
    try:
        # Decode if base64
        if doc.document_base64:
            document_data = decode_base64_json(doc.document_base64)

        else:
            document_data = doc.document_json

        if not document_data:
            return JSONResponse(status_code=400, content={"error": "Invalid or missing document."})

        result = analyze_document(document_data)

        return {
            "status": "success",
            "issues": result["issues"],
            "confidence": result["confidence"],
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/visa/simulate", response_model=Dict)
def simulate_visa_path(doc: DocumentInput):
    try:

        document_data = {}
        # Decode if base64
        if doc.document_base64:
            document_data = decode_base64_json(doc.document_base64)

        else:
            document_data = doc.document_json


        # Placeholder for actual simulation logic
        if not doc.scenario:
            return JSONResponse(status_code=400, content={"error": "User scenario is required"})

        # Simulated response
        simulation = simulate_what_if(document_data or {}, doc.scenario or {})

        return {
            "current_path": "Green Card in 2 years",
            "new_path": "Green Card in 6 months",
            "legal_basis": "Marriage-based fast track clause 245(i)",
            "what_if": simulation
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
