# app/routers/voice.py

from fastapi import APIRouter, HTTPException
from app.models.assistant_model import *
from app.core.chat import get_reply_from_ai, get_chat_history, append_chat_history
from app.core.utils import generate_uuid

router = APIRouter()

@router.post("/voice/assistant", response_model=FromVoiceResponse)
async def voiceAssistant(req: FromVoiceRequest):
    try:
        history = get_chat_history(req.user_id) if hasattr(req, "user_id") else None
        if history is not None and isinstance(history, dict):
            history = [history]
        
        reply = get_reply_from_ai(req.msg, history=history)
        msgId = generate_uuid()
        if hasattr(req, "user_id"):
            append_chat_history(req.user_id, [
                { "id": req.user_id, "msg": req.msg, "time": req.time, "msgId": msgId },
                { "id": 0, "msg": reply["msg"], "time": req.time, "msgId": reply["msgId"] }
            ])

        return {"response": reply["msg"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
    
@router.post("/doc/scan", response_model=FromDocResponse)
async def docScan(req: FromDocRequest):
    try:
        # Placeholder for document processing logic
        # In a real application, this would involve extracting text from the document URL
        # and generating key clauses and summary.
        return {
            "doc_type": "example_type",
            "Key_clauses": ["Example clause 1", "Example clause 2"],
            "summary": "This is a summary of the document."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
