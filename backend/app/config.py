"""Application configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Family Destiny API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./family_destiny.db"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # RevenueCat
    REVENUECAT_API_KEY: str = ""
    REVENUECAT_WEBHOOK_SECRET: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
