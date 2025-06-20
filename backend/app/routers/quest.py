# app/routers/quest.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.utils import User
from app.models.util_model import UserData
import random

router = APIRouter()

@router.post(path="/quest/daily", response_model=dict)
async def fetch_daily_quests(user_id: str):
    user = User()
    user.fromUUID(user_id)
    quests = user.fetch_data("quests")["uncompleted"]
    return quests[random.randint(0, quests.len())]
    