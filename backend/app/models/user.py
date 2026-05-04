"""User model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    # RevenueCat subscriber info
    revenuecat_id = Column(String, unique=True, index=True, nullable=True)
    # Subscription status (cached from RevenueCat)
    is_premium = Column(Boolean, default=False)
    premium_expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
