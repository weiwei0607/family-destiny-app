"""Birth profile model"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Basic info
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)  # 男/女
    birth_date = Column(String, nullable=False)  # YYYY-MM-DD
    birth_time = Column(String, nullable=False)  # HH:MM
    birth_lat = Column(Float, default=25.0330)
    birth_lon = Column(Float, default=121.5654)
    
    # Computed chart data (cached)
    chart_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
