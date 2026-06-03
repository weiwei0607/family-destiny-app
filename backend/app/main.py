"""Family Destiny API - FastAPI backend"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.routers import free, premium, webhook

# Create database tables
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="Family Destiny API",
    description="五系統命理分析 API：免費基礎盤 + 付費 AI 深度報告",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(free.router)
app.include_router(premium.router)
app.include_router(webhook.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "family-destiny-api"}
