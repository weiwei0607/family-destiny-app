"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ---------- Profile Schemas ----------

class ProfileCreate(BaseModel):
    name: Optional[str] = None
    gender: str = "女"
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(default="12:00", description="HH:MM")
    location: str = Field(default="taipei", description="taipei/taichung/kaohsiung/other")
    lang: str = Field(default="zh-TW", description="zh-TW/zh-CN/en/ja")
    tier: str = Field(default="standard", description="lite/standard/premium")

class ProfileOut(BaseModel):
    id: int
    name: Optional[str]
    gender: str
    birth_date: str
    birth_time: str
    chart_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}

# ---------- Chart Schemas ----------

class BasicChartResponse(BaseModel):
    """Free tier: basic chart data"""
    name: str
    gender: str
    bazi: Dict[str, Any]
    astrology: Dict[str, Any]
    ziwei: Dict[str, Any]
    humandesign: Dict[str, Any]
    xingxiu: str
    energy_score: int
    summary: str
    interpretations: Dict[str, Any] = Field(default={}, description="Human-readable interpretations for each system")

class FullReportResponse(BaseModel):
    """Premium tier: AI-generated full report"""
    basic: BasicChartResponse
    integrated_profile: str  # AI narrative
    strengths_weaknesses: Dict[str, Any]
    life_lessons: str
    prescription: List[Dict[str, str]]
    
# ---------- Compatibility Schemas ----------

class CompatibilityBasicRequest(BaseModel):
    person1: ProfileCreate
    person2: ProfileCreate
    lang: str = Field(default="zh-TW", description="zh-TW/zh-CN/en/ja")
    tier: str = Field(default="standard", description="lite/standard/premium")

class CompatibilityBasicResponse(BaseModel):
    """Free tier: basic compatibility"""
    overall_score: float
    stars: str
    summary: str
    dimensions: Dict[str, Any]
    person1_summary: str
    person2_summary: str

class CompatibilityDeepResponse(BaseModel):
    """Premium tier: deep compatibility with AI narrative"""
    basic: CompatibilityBasicResponse
    relationship_narrative: str  # AI generated
    conflict_points: List[str]
    communication_guide: Dict[str, Any]
    prescription: List[Dict[str, str]]

# ---------- User Schemas ----------

class UserCreate(BaseModel):
    device_id: str

class UserOut(BaseModel):
    id: int
    device_id: str
    is_premium: bool
    premium_expires_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}

# ---------- RevenueCat Webhook ----------

class RevenueCatWebhook(BaseModel):
    event: Dict[str, Any]

# ---------- Q&A Schemas ----------

class AskRequest(BaseModel):
    """Ask a question based on chart data"""
    chart: Dict[str, Any] = Field(..., description="Full chart data from /api/free/chart")
    question: str = Field(..., description="User's question, e.g. '我適合做設計師嗎？'")
    lang: str = Field(default="zh-TW", description="zh-TW/zh-CN/en")
    tier: str = Field(default="standard", description="lite/standard/premium")

class AskResponse(BaseModel):
    """AI answer to a chart-based question"""
    answer: str
    relevant_systems: List[str] = Field(default=[], description="Which systems support this answer")
    confidence: str = Field(default="中", description="高/中/低")
    disclaimer: str = Field(default="本回答僅供參考，請理性判斷並以自身實際情況為準。")

# ---------- Family Schemas ----------

class FamilyMember(BaseModel):
    """A family member with basic info"""
    name: Optional[str] = None
    gender: str = "女"
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(default="12:00", description="HH:MM")
    location: str = Field(default="taipei", description="taipei/taichung/kaohsiung/other")
    role: str = Field(default="member", description="father/mother/child/grandparent")

class FamilyRequest(BaseModel):
    """Family constellation request"""
    members: List[FamilyMember] = Field(..., min_length=2, description="At least 2 family members")
    lang: str = Field(default="zh-TW", description="zh-TW/zh-CN/en")
    tier: str = Field(default="standard", description="lite/standard/premium")

class FamilyMemberReport(BaseModel):
    """Report for a single family member within the family context"""
    name: str
    role: str
    chart_summary: str
    family_role: str  # e.g. "情緒穩定器", "創意發想者"

class FamilyResponse(BaseModel):
    """AI-generated family constellation report"""
    family_narrative: str  # Overall family dynamic story
    member_reports: List[FamilyMemberReport]
    relationship_matrix: List[Dict[str, Any]]  # Pairwise dynamics
    family_prescription: List[Dict[str, str]]
    communication_guide: Dict[str, str]

# ---------- Annual Schemas ----------

class AnnualRequest(BaseModel):
    """Annual destiny report request"""
    name: Optional[str] = None
    gender: str = "女"
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(default="12:00", description="HH:MM")
    location: str = Field(default="taipei")
    year: int = Field(default=2026, description="Target year for the report")
    lang: str = Field(default="zh-TW", description="zh-TW/zh-CN/en")
    tier: str = Field(default="standard", description="lite/standard/premium")

class MonthInsight(BaseModel):
    """Insight for a specific month"""
    month: int
    theme: str
    advice: str
    energy: str  # high/medium/low

class AnnualResponse(BaseModel):
    """AI-generated annual destiny report"""
    year_theme: str  # e.g. "轉變之年", "扎根之年"
    yearly_overview: str
    bazi_luck: Dict[str, Any]  # Annual luck pillars
    key_opportunities: List[str]
    key_challenges: List[str]
    monthly_insights: List[MonthInsight]
    annual_prescription: List[Dict[str, str]]
