# app/core/utils.py

from app.models.util_model import UserData
from datetime import datetime
import json
import base64

def generate_uuid():
    import uuid
    return str(uuid.uuid4())

def decode_base64_json(data: str) -> dict:
    decoded_bytes = base64.b64decode(data)
    return json.loads(decoded_bytes.decode("utf-8"))

class User:
    def __init__(self):
        self.uuid = generate_uuid()

    def fetch_userdata(self):
        return UserData(
            id = "f9bdc335-4840-4a29-a511-c05ec661c972",
            firstname = "John",
            lastname = "Doe",
            email = "johndoe@example.com",
            phone = "+012345678901",
            age = 37,
            DOB = datetime(day=1,month=1,year=1970),
            user_profile = "url_to_profile_pic?",
        )

    def fromUUID(self, uuid: str):
        self.uuid = uuid
        return self.fetch_userdata()
