from pydantic import BaseModel, EmailStr
from datetime import datetime

class RegisterForm(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    country: str
    DOB: datetime
    psw: str

class LoginForm(BaseModel):
    email: EmailStr
    psw: str

class UserInDB(BaseModel):
    id: str
    email: EmailStr