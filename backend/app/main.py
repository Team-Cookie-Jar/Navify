# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import context, crisis, login, quest, register, visa
from backend.app.routers import assistant
# from dotenv import load_dotenv

app = FastAPI(title="Navify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6723", "https://narvify.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assistant.router)
app.include_router(context.router)
app.include_router(crisis.router)
app.include_router(login.router)
app.include_router(quest.router)
app.include_router(register.router)
app.include_router(visa.router)

@app.get("/")
async def root():
    return {"message": "Navify"}

