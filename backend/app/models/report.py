"""Report model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.sql import func
from app.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    report_type = Column(String, nullable=False)  # personal_full, compatibility_deep, family, annual
    
    # Input profile IDs
    profile_ids = Column(JSON, nullable=False)  # list of profile IDs
    
    # Structured data (free tier)
    structured_data = Column(JSON, nullable=True)
    
    # AI-generated narrative (premium tier)
    ai_narrative = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)  # model, tokens, cost
    
    # Pricing
    price_paid = Column(Float, default=0.0)
    currency = Column(String, default="TWD")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
