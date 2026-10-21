"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine
from app.config import TELEGRAM_BOT_TOKEN
from app import models  # noqa: F401 — register ORM tables on Base before create_all
from app.routers import debtors, payments, students

# Create tables at import time (SQLite + uvicorn/gunicorn are safe here).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Center Payments", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "bot_enabled": bool(TELEGRAM_BOT_TOKEN)}


app.include_router(students.router)
app.include_router(payments.router)
app.include_router(debtors.router)

# Mobile-friendly web UI (Part 2-B), served last so API routes win.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
