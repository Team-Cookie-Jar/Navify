# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import context, crisis, login, quest, register, visa

app = FastAPI(title="Navify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6723", "https://narvify.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(assistant.router) Not on my PC, NO
app.include_router(context.router)
app.include_router(crisis.router)
app.include_router(login.router)
app.include_router(quest.router)
app.include_router(register.router)
app.include_router(visa.router)

app.mount("/profile_pictures", StaticFiles(directory="profile_pictures"), name="profile_pictures")

@app.get("/")
async def root():
    return {"message": "Navify"}

