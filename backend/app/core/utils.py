# app/core/utils.py

from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.core.mail import send_html_email
from app.models.util_model import UserData
from app.models.user_model import RegisterForm, LoginForm
from app.core.db import db
from PIL import Image
from datetime import datetime, date, timedelta
import random
import json
import base64
import bcrypt
import uuid
import os
import io


BADGE_RULES = {
    "7-Day Streak": lambda progress: progress["current_streak"] >= 7,
    "14-Day Streak": lambda progress: progress["current_streak"] >= 14,
    "21-Day Streak": lambda progress: progress["current_streak"] >= 21,
    "28-Day Streak": lambda progress: progress["current_streak"] >= 28,
    "50-Day Streak": lambda progress: progress["current_streak"] >= 50,
    "100-Day Streak": lambda progress: progress["current_streak"] >= 100,

    "First Quest": lambda progress: progress["completed"] >= 1,
    "10x Quests": lambda progress: progress["completed"] >= 10,
    "Quest Master": lambda progress: progress["completed"] >=  50,

    "XP Pro": lambda progress: progress["xp"] >= 50,
    "XP Master": lambda progress: progress["xp"] >= 100,
    "XP GrandMaster": lambda progress: progress["xp"] >= 150
}

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_uuid():
    return str(uuid.uuid4())

def decode_base64_json(data: str) -> dict:
    decoded_bytes = base64.b64decode(data)
    return json.loads(decoded_bytes.decode("utf-8"))

def calculate_age(dob):
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

async def upload_image(filename: str, path_to_upload: str, file: UploadFile = File(...)):
    try:
        os.makedirs(path_to_upload, exist_ok=True)
        contents = await file.read()

        try:
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            
        except Exception as e:
            raise HTTPException(status_code=400, detail={"error": "Invalid image file"})
    
        file_path = os.path.join(path_to_upload, filename)
        image.save(file_path, format="JPEG")
        return {"filename": filename, "path": file_path}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Directory not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

def encode_image_as_base64(file_path: str):
    with open(file_path, "rb") as img:
        b64 = base64.b64encode(img.read()).decode("utf-8")
    return b64

class User:
    def __init__(self):
        self.uuid = generate_uuid()
        self.profile_picture_url = ""

    def fetch_userdata(self):
        return UserData(
            id = self.uuid,
            firstname = self.firstname,
            lastname = self.lastname,
            email = self.email,
            phone = self.phone,
            age = self.age,
            DOB = self.DOB,
            confirm_email = self.confirm_email,
            profile_picture_url = self.profile_picture_url,
        )

    def update_db(self):
        user_data = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "phone": self.phone,
            "age": self.age,
            "DOB": self.DOB,
            "confirm_email": self.confirm_email,
            "profile_picture_url": self.profile_picture_url,
        }

        user = db.collection("users").document(self.uuid)
        if not user.get().exists:
            return JSONResponse(status_code=404, content={"error": "Invalid user ID"})

        user.update(user_data)
        return {"status": "success", "userdata": user_data}

    def add_user(self):
        user_data = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "psw": self.psw,
            "phone": self.phone,
            "age": self.age,
            "DOB": self.DOB,
            "confirm_email": False,
            "profile_picture_url": ""
        }

        try:
            existing_user = db.collection("users").where(field_path="email", op_string="==", value=self.email).get()
            if existing_user:
                raise HTTPException(status_code=400, detail={"error": "Email already registered"})

            db.collection("users").document(self.uuid).set(user_data)

            self.request_confirm_email()
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

    def from_register(self, form: RegisterForm):
        self.uuid = generate_uuid()
        self.firstname = form.firstname
        self.lastname = form.lastname
        self.email = form.email
        self.psw = hash_password(form.psw)
        self.phone = form.phone
        self.age = calculate_age(form.DOB)
        self.DOB = form.DOB
        self.profile_picture_url = ""
        self.confirm_email = False

        return self.add_user()

    def request_confirm_email(self):
        email_code = round(random.randint(100000, 999999))
        try:
            existing_request = db.collection("email_codes").document(self.uuid)
            if existing_request.get().exists:
                existing_request.delete()

            email_code_request = {
                "id": self.uuid,
                "datetime": datetime.now(),
                "digits": email_code
            }

            db.collection("email_codes").document(self.uuid).set(email_code_request)

            #code_html = f"""<div style='display: flex;height: 61px;width: 249px;justify-content: space-between;align-items: center;flex-direction: row;line-height: 14px;'>{"".join(f"<div style='display: flex;height: 11px;padding: 19px 6px;border: 2px solid #6f67d9;border-radius: 7px;background-color: #f5f5f5;color: #000;font-size: 40px;'>{str(email_code)[i]}</div>" for i in range(len(str(email_code))))}</div>"""

            """html_content = [
                {
                    "type": "table",
                    "content": [    
                        {
                            "type": "table",
                            "content": [
                                {"type": "image", "content": "image/logo.png"},
                                {"type": "header", "content": "Verify Your Email Address"},
                                {"type": "text", "content": "We just need to verify your email address to activate your Navify account. Here's your verification code:"},
                                {"type": "html", "content": code_html},
                                {"type": "html", "content": "This code expires within 5 minutes"},
                                {"type": "text", "content": "Only enter this code on the Navify website or app. Don't share it with anyone. We'll never ask for it outside any of our platforms."},
                                {"type": "text", "content": "Welcome aboard!"},
                                {"type": "text", "content": "Navify Team"}
                            ]
                        }
                    ]
                },
                {
                    "type": "table",
                    "content": [
                        {"type": "text", "content": "This email was sent to you by Navify because you signed up for a Navify account.break-linePlease let us know if you feel that this email was sent to you by error."},
                        {"type": "text", "content": "© 2025 Navify"},
                        {"type": "list", "content": [
                            {"type": "hyperlink", "content": "Privacy Policy", "link": "#"},
                            {"type": "hyperlink", "content": "Personal Data Protection and Privacy Policy", "link": "#"},
                            {"type": "hyperlink", "content": "Acceptable Use Policy", "link": "#"},
                        ]}
                    ]
                }
            ]

            send_html_email(to_email=self.email, to_name=f"{self.firstname} {self.lastname}", subject="Verify your email - Navify", html_content=html_content)"""

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

    def from_login(self, form: LoginForm):

        query = db.collection("users").where(field_path="email", op_string="==", value=form.email).get()
        if not query:
            raise HTTPException(status_code=404, detail={"error": "Invalid email, please register with this email"})

        user_data = query[0].to_dict()
        if user_data is None:
            raise HTTPException(status_code=404, detail={"error": "User data not found"})

        if not verify_password(form.psw, user_data["psw"]):
            raise HTTPException(status_code=400, detail={"error": "Incorrect password"})

        self.uuid = query[0].id
        self.firstname = user_data["firstname"]
        self.lastname = user_data["lastname"]
        self.email = user_data["email"]
        self.psw = user_data["psw"]
        self.phone = user_data["phone"]
        self.age = user_data["age"]
        self.DOB = user_data["DOB"]
        self.profile_picture_url = user_data["profile_picture_url"]
        self.confirm_email = user_data["confirm_email"]

        return self.fetch_userdata().model_dump()

    def from_userdata(self, userdata: UserData, should_update: bool = False):
        self.uuid = userdata.id
        self.firstname = userdata.firstname
        self.lastname = userdata.lastname
        self.email = userdata.email
        self.phone = userdata.phone
        self.age = userdata.age
        self.DOB = userdata.DOB
        self.profile_picture_url = userdata.profile_picture_url
        self.confirm_email = userdata.confirm_email

        if should_update:
            return self.update_db()

    def fromUUID(self, uuid: str):
        self.uuid = uuid
        query = db.collection("users").document(self.uuid).get()
        if not query:
            raise HTTPException(status_code=404, detail={"error": "Invalid user ID"})

        user = query.to_dict()
        if user is None:
            raise HTTPException(status_code=500, detail={"error": "User data not found"})
        
        self.firstname = user["firstname"]
        self.lastname = user["lastname"]
        self.email = user["email"]
        self.psw = user["psw"]
        self.phone = user["phone"]
        self.age = user["age"]
        self.DOB = user["DOB"]
        self.profile_picture_url = user["profile_picture_url"]
        self.confirm_email : bool = user["confirm_email"]
        
        return self.fetch_userdata()

    def fetch_data(self, data: str):
        uuid = self.uuid
        query = db.collection(data).document(uuid).get()
        if not query:
            raise HTTPException(status_code=404, detail={"error": f"Invalid user ID"})

        result = query.to_dict()
        if result is None:
            raise HTTPException(status_code=500, detail={"error": f"cannot fetch {data} with user ID"})

        return result

    def request_password_reset(self):
        reset_code = random.randint(10000, 99999)
        code_html = f"""<div style='display: flex;height: 61px;width: 249px;justify-content: space-between;align-items: center;flex-direction: row;line-height: 14px;'>{"".join(f"<div style='display: flex;height: 11px;padding: 19px 6px;border: 2px solid #6f67d9;border-radius: 7px;background-color: #f5f5f5;color: #000;font-size: 40px;'>{str(reset_code)[i]}</div>" for i in range(len(str(reset_code))))}</div>"""

        html_content = [
            {
                "type": "table",
                "content": [    
                    {
                        "type": "table",
                        "content": [
                            {"type": "image", "content": "image/logo.png"},
                            {"type": "header", "content": "Reset Your Password"},
                            {"type": "text", "content": "We just need to verify it you before you can reset your password, here's your reset code:"},
                            {"type": "html", "content": code_html},
                            {"type": "html", "content": "This code expires within 5 minutes"},
                            {"type": "text", "content": "Only enter this code on the Navify website or app. Don't share it with anyone. We'll never ask for it outside any of our platforms."},
                            {"type": "text", "content": "If you see this email and you didn't request a password reset, click below to go to \"Acccount Management\" to secure your account"},
                            {"type": "button", "content": "Account Management", "hyperlink": "#"}
                        ]
                    }
                ]
            },
            {
                "type": "table",
                "content": [
                    {"type": "text", "content": "This email was sent to you by Navify because you signed up for a Navify account.break-linePlease let us know if you feel that this email was sent to you by error."},
                    {"type": "text", "content": "© 2025 Navify"},
                    {"type": "list", "content": [
                        {"type": "hyperlink", "content": "Privacy Policy", "link": "#"},
                        {"type": "hyperlink", "content": "Personal Data Protection and Privacy Policy", "link": "#"},
                        {"type": "hyperlink", "content": "Acceptable Use Policy", "link": "#"},
                    ]}
                ]
            }
        ]


        send_html_email(to_email=self.email, to_name=f"{self.firstname} {self.lastname}", subject="Verify your email - Navify", html_content=html_content)

        user_reset_request = {
            "id": self.uuid,
            "datetime": datetime.now(),
            "reset_code": reset_code
        }

        try:
            existing_request = db.collection("reset_psw_request").document(self.uuid)
            if existing_request.get().exists:
                existing_request.delete()

            db.collection("reset_psw_request").document(self.uuid).set(user_reset_request)
            
            return {"status": "success"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    def validate_password_request(self, reset_code: int):
        reset_key = generate_uuid()
        try:
            code = self.fetch_data("reset_psw_request")

            now = datetime.now()
            minutes = now.minute - code["datetime"].minute - (now.second < code["datetime"].second)
            if minutes >= 5:
                return JSONResponse(status_code=400, content={"error": "Code expired, request another one"})
            
            else:
                if code["reset_code"] == reset_code:
                    try:
                        user_reset_key = {
                            "id": self.uuid,
                            "datetime": datetime.now(),
                            "reset_key": reset_key
                        }

                        existing_request = db.collection("reset_psw_key").document(self.uuid)
                        if existing_request.get().exists:
                            existing_request.delete()

                        request = db.collection("reset_psw_key").document(self.uuid).set(user_reset_key)
                        return {"status": "success", "reset_key": reset_key}

                    except Exception as e:
                        return JSONResponse(status_code=500, content={"error": str(e)})
                                
                else:
                    return JSONResponse(status_code=400, content={"error": "Invalid code"})

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    def update_psw(self, change_key: str, new_password_unsafe: str):
        new_password = hash_password(new_password_unsafe)

        try:
            reset_key = self.fetch_data("reset_key")

            now = datetime.now()
            minutes = now.minute - reset_key["datetime"].minute - (now.month < reset_key["datetime"])
            if minutes >= 5:
                return JSONResponse(status_code=400, content={"error": "Code expired, request another one"})

            else:
                if change_key == reset_key["reset_key"]:
                    user_data = {
                        "psw": new_password
                    }

                    user = db.collection("users").document(self.uuid)
                    if not user.get().exists:
                        return JSONResponse(status_code=404, content={"error": "Invalid user ID"})

                    user.update(user_data)
                    return {"status": "success"}

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
        
    def submit_quest(self):
        user_ref = db.collection("users_progress").document(self.uuid)
        user_data = user_ref.get().to_dict() or {
            "completed_quests": [],
            "current_streak": 0,
            "xp": 0,
            "badges": [],
            "last_quest_data": None   
        }

        today = date.today()
        last_date = user_data["last_quest_date"]
        quest_id = f"quest_{today.strftime('%Y%m%d')}"

        if quest_id in user_data["completed_quests"]:
            raise HTTPException(400, "Quest already completed.")

        yesterday = today - timedelta(days=1)
        if last_date == yesterday.isoformat():
            user_data["current_streak"] = 1
        
        else:
            user_data["current_streak"] = 1

        quest = db.collection("quests").document(today.isoformat()).get()
        if quest.exists:
            data = quest.to_dict()

            if data is None:
                raise HTTPException(status_code=404, detail="Quest data not found")
            
            xp_reward = data["reward"]
        else:
            xp_reward = 5
            data = {
                "id": quest_id,
                "tasks": "Complete today's quest",
                "reward": xp_reward
            }
        
        user_data["completed_quests"].append(quest_id)
        user_data["xp"] += xp_reward
        user_data["last_quest_date"] = today.isoformat()

        for badge, rule in BADGE_RULES.items():
            if badge not in user_data["badges"] and rule(user_data):
                user_data["badges"].append(badge)

        user_ref.set(user_data)
        return JSONResponse(status_code=200, content={"message": "Quest submitted", "badges": user_data["badges"]})

    def redeem_reward(self, reward_id: str):
        reward_doc = db.collection("rewards").document(reward_id).get()
        if not reward_doc.exists:
            raise HTTPException(status_code=404, detail="Reward not found")

        reward = reward_doc.to_dict()
        if reward is None:
            raise HTTPException(status_code=404, detail="Reward data not found")

        user_ref = db.collection("user_progress").document(self.uuid)
        user_data = user_ref.get().to_dict()

        if user_data is None:
            raise HTTPException(status_code=404, detail="User progress not found")

        if user_data["xp"] < reward["cost"]:
            raise HTTPException(status_code=400, detail="Not enough XP")

        user_data["xp"] -= reward["cost"]
        user_data.setdefault("redeem_rewards", []).append(reward_id)

        user_ref.set(user_data)
        return JSONResponse(status_code=200, content={"message": "Reward redeemed"})
