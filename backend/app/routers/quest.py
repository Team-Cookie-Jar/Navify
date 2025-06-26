# app/routers/quest.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.utils import User, translate_to_languages
from app.core.db import db
import datetime

router = APIRouter()

@router.get(path="/quest/daily", response_model=dict)
def get_daily_quests(lang: str = "en"):
    today = datetime.date.today().isoformat()
    quest = db.collection("quests").document(today).get()
    if not quest.exists:
        return JSONResponse(status_code=404, content={"error": "No quest defined for today"})

    qdata = quest.to_dict()
    if qdata is None:
        return JSONResponse(status_code=404, content={"error": "Quest data is empty"})

    localized = translate_to_languages(qdata["task"], [lang, "en", "fr", "de", "es", "it", "pt", "ru", "zh-CN", "ja", "ko"])
    if localized is None:
        return JSONResponse(status_code=404, content={"error": "Translation failed"})

    return {"id": qdata["id"], "tasks": localized, "reward": qdata["reward"]}

@router.get(path="/quest/weekly", response_model=dict)
def get_weekly_quests(lang: str = "en"):
    today = datetime.date.today().isoformat()
    week_start = (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.timedelta(days=datetime.datetime.strptime(today, "%Y-%m-%d").weekday())).date()
    week_start_str = week_start.isoformat()

    quest = db.collection("quests").document(week_start_str).get()
    if not quest.exists:
        return JSONResponse(status_code=404, content={"error": "No weekly quest defined"})

    qdata = quest.to_dict()
    if qdata is None:
        return JSONResponse(status_code=404, content={"error": "Quest data is empty"})

    localized = translate_to_languages(qdata["task"], [lang, "en", "fr", "de", "es", "it", "pt", "ru", "zh-CN", "ja", "ko"])
    if localized is None:
        return JSONResponse(status_code=404, content={"error": "Translation failed"})

    return {"id": qdata["id"], "tasks": localized, "reward": qdata["reward"]}

@router.post(path="/quest/daily/submit", response_model=dict)
def submit_daily_quest(user_id: str, quest_id: str):
    user = User()
    user.fromUUID(user_id)
    return user.submit_daily_quest(quest_id)

@router.post(path="/quest/weekly/submit", response_model=dict)
def submit_weekly_quest(user_id: str, quest_id: str):
    user = User()
    user.fromUUID(user_id)
    return user.submit_weekly_quest(quest_id)

@router.post(path="quest/redeem-reward/{reward_id}")
def redeem_reward(reward_id: str, user_id):
    user = User()
    user.fromUUID(user_id)
    return user.redeem_reward(reward_id)

@router.get(path="/leaderboard")
def get_leaderboard(limit: int = 10):
    users = db.collection("users_progress").order_by("xp", direction="DESENDING").limit(limit).stream()
    return [
        {"user_id": u.id, "xp": u.to_dict().get("xp", 0), "streak": u.to_dict().get("current_streak", 0)}
        for u in users
    ]
    
@router.post(path="/quest/daily/add", response_model=dict)
def add_daily_quest(quest_id: str, task: str, reward: int):
    today = datetime.date.today().isoformat()
    quest_ref = db.collection("quests").document(today)
    
    if quest_ref.get().exists:
        return JSONResponse(status_code=400, content={"error": "Daily quest already exists for today"})

    quest_ref.set({
        "id": quest_id,
        "task": task,
        "reward": reward,
        "type": "daily"
    })
    
    return {"status": "success", "message": "Daily quest added successfully"}

@router.post(path="/quest/weekly/add", response_model=dict)
def add_weekly_quest(quest_id: str, task: str, reward: int):
    today = datetime.date.today().isoformat()
    week_start = (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.timedelta(days=datetime.datetime.strptime(today, "%Y-%m-%d").weekday())).date()
    week_start_str = week_start.isoformat()
    
    quest_ref = db.collection("quests").document(week_start_str)
    
    if quest_ref.get().exists:
        return JSONResponse(status_code=400, content={"error": "Weekly quest already exists for this week"})

    quest_ref.set({
        "id": quest_id,
        "task": task,
        "reward": reward,
        "type": "weekly"
    })
    
    return {"status": "success", "message": "Weekly quest added successfully"}