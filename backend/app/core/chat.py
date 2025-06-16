# app/core/chat.py

import requests
import os
import re
from datetime import datetime
from typing import Optional, List, Dict
from app.core.utils import generate_uuid

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.0-flash-exp:free"

def get_reply_from_ai(message: str, history: Optional[List[Dict]] = None) -> Dict[str, str]:
    if history is None:
        history = []

    system_prompt = f"""You are a helpful immigrant assistant.
    
    Structure your response as follows:
    1. If the user asks for information, provide a concise answer.
    2. If the user asks for a suggestion, provide a list of suggestions.
    3. If the user asks for help, provide a step-by-step guide.
    4. Mention warnings or important notes if necessary.
    5. Always end with a friendly note.

    Current conversation history:
    {history}

    Keep responses short and to the point, using simple language.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": message}
    ]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "content-type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            },
            timeout = 10
        )

        response.raise_for_status()

        raw_content = response.json()["choices"][0]["message"]["content"]
        return structure_response(raw_content)
    except requests.RequestException as e:
        raise Exception(f"Error communicating with AI model: {str(e)}")

def structure_response(raw_content: str) -> Dict[str, str]:
    # Process the raw content to extract structured information
    # This is a placeholder function. In a real application, this would parse the response.

    cleaned_response = re.sub(r'\*\*', '', raw_content)
    sections = re.split(r'(?<=[.!?])\s+', cleaned_response)
    lines = []
    for i, section in enumerate(sections):
        if i < len(sections):
            section = section.strip()
            if section:
                lines.append(section)
                
    response = {
        "msg": "\n".join(lines),
        "time": datetime.now().isoformat(),
        "msgId": generate_uuid()
    }
    return response

def get_chat_history(user_id):
    # Connect to the firebase db to retrieve chat history
    # This is a placeholder function. In a real application, this would query the database.
    return {}  # Return an empty list for now

def append_chat_history(user_id, messages):
    # Connect to the firebase db to append chat history
    # This is a placeholder function. In a real application, this would update the database.
    pass  # Do nothing for now, as this is just a placeholder