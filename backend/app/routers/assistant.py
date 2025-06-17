# app/routers/voice.py

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from app.models.assistant_model import *
from app.core.chat import get_reply_from_ai, get_chat_history, append_chat_history
from app.core.utils import generate_uuid
from transformers import pipeline
import pytesseract
import io

router = APIRouter()

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
classifier = pipeline("zero-shot-classification")

DOCUMENT_TYPES = ["Lease Agreement", "Non-Disclosure Agreement", "employment Contract", "Invoice", "Purchase Order"]
CLAUSES = ["Payment Terms", "Termination", "Confidentiality", "Liability", "Governing Law", "Obligations"]

@router.post("/voice/assist", response_model=FromVoiceResponse)
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
        return JSONResponse(status_code=500, content={"error": str(e)})


async def analyze_document(text):
    classification = classifier(text, DOCUMENT_TYPES)
    if hasattr(classification, '__next__'):
        classification = next(classification)
    elif hasattr(classification, '__iter__') and not isinstance(classification, dict):
        classification = list(classification)[0]
    if not isinstance(classification, dict):
        classification = dict(classification)
    doc_type = classification["labels"][0]

    clause_results = classifier(text, CLAUSES, multi_label=True)
    if hasattr(clause_results, '__next__'):
        clause_results = next(clause_results)
    elif hasattr(clause_results, '__iter__') and not isinstance(clause_results, dict):
        clause_results = list(clause_results)[0]
    if not isinstance(clause_results, dict):
        clause_results = dict(clause_results)
    detected_clauses = {
        label: score for label, score in zip(clause_results.get("labels", []), clause_results.get("scores", [])) if score > 0.5
    }

    try:
        chunks = [text[i:i + 1000] for i in range(0, len(text), 1000)]
        summaries = summarizer(chunks)
        if summaries is not None:
            summary = " ".join(s["summary_text"] for s in summaries if s is not None and "summary_text" in s)
        else:
            summary = "Summarization failed: summarizer returned None."
    except Exception as e:
        summary = f"text too short or summariztion failed: {e}."

    return {
        "document_type": doc_type,
        "key_clauses": detected_clauses,
        "summary": summary.strip(),
        "raw_text": text.strip()
    }


@router.post("/doc/scan", response_model=dict)
async def extract_text_from_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        try:
            text = pytesseract.image_to_string(image)
            analyzed_document = analyze_document(text)

            return {
                "filename": file.filename,
                "text": text.strip(),
                "analyzier": analyzed_document
            }

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
