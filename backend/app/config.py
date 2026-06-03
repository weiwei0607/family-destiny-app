"""Application configuration"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Family Destiny API"
    DEBUG: bool = True

    # CORS — comma-separated origins, e.g. "https://app.example.com,http://localhost:3000"
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:8000")

    # Database
    DATABASE_URL: str = "sqlite:///./family_destiny.db"

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # RevenueCat
    REVENUECAT_API_KEY: str = ""
    REVENUECAT_WEBHOOK_SECRET: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
