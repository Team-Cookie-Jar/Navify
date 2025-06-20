# app/core/db.py

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import base64

load_dotenv()
"""
firebase_key_base64 = os.getenv("FIREBASE_KEY")

if not firebase_key_base64:
    raise ValueError("FIREBASE_KEY environment variable is not set.")

try:
    firebase_key_json = base64.b64decode(firebase_key_base64).decode('utf-8')

except Exception as e:
    raise ValueError("FIREBASE_KEY is not a valid base64 encoded string.") from e

try:
    firebase_key = json.loads("firebase_key.json")
except json.JSONDecodeError as e:
    raise ValueError("Decoded FIREBASE_KEY is not a valid JSON string.") from e
"""
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/SHARON/cookies_projects/Navify/backend/app/core/firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()