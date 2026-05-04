"""Premium tier APIs - requires subscription, uses AI"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import (
    ProfileCreate, FullReportResponse, CompatibilityBasicRequest, CompatibilityDeepResponse,
    AskRequest, AskResponse, FamilyRequest, FamilyResponse, AnnualRequest, AnnualResponse
)
from app.services.chart_service import compute_basic_chart, compute_compatibility_basic
from app.services.ai_service import (
    generate_personal_report, generate_compatibility_report, generate_answer,
    generate_family_report, generate_annual_report
)

router = APIRouter(prefix="/api/premium", tags=["premium"])


def _check_premium(authorization: Optional[str] = Header(None)):
    """
    Check if user has premium access.
    In production, this validates RevenueCat subscriber status.
    For development, pass 'Bearer dev-premium' to bypass.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Development bypass
    if authorization == "Bearer dev-premium":
        return True
    
    # TODO: Implement RevenueCat subscriber validation
    # 1. Extract subscriber ID from token
    # 2. Call RevenueCat API to check entitlements
    # 3. Return True if active subscription exists
    
    raise HTTPException(status_code=403, detail="Premium subscription required")


@router.post("/full-report", response_model=FullReportResponse)
async def get_full_report(
    data: ProfileCreate,
    db: Session = Depends(get_db),
    is_premium: bool = Depends(_check_premium)
):
    """
    Premium tier: Get AI-generated full personal report.
    Includes integrated profile, life lessons, and personalized prescription.
    """
    try:
        # Compute basic chart (code)
        payload = data.model_dump()
        basic = compute_basic_chart(payload)
        lang = data.lang
        
        # Generate AI narrative based on tier
        tier = data.tier
        ai_report = await generate_personal_report(basic, lang=lang, tier=tier)
        
        result = {
            "basic": basic,
            "tier": tier,
            "integrated_profile": ai_report.get("integrated_profile", ""),
            "strengths_weaknesses": ai_report.get("strengths_weaknesses", {}),
            "life_lessons": ai_report.get("life_lessons", ""),
            "prescription": ai_report.get("prescription", [])
        }
        if "relationship_tips" in ai_report:
            result["relationship_tips"] = ai_report["relationship_tips"]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/compatibility-deep", response_model=CompatibilityDeepResponse)
async def get_deep_compatibility(
    data: CompatibilityBasicRequest,
    db: Session = Depends(get_db),
    is_premium: bool = Depends(_check_premium)
):
    """
    Premium tier: Get AI-generated deep compatibility report.
    Includes relationship narrative, conflict analysis, and communication guide.
    """
    try:
        # Compute basic compatibility (code)
        basic = compute_compatibility_basic(
            data.person1.model_dump(),
            data.person2.model_dump()
        )
        
        # Compute individual charts for AI context
        chart1 = compute_basic_chart(data.person1.model_dump())
        chart2 = compute_basic_chart(data.person2.model_dump())
        
        # Generate AI narrative based on tier
        lang = data.lang
        tier = data.tier
        ai_report = await generate_compatibility_report(chart1, chart2, basic, lang=lang, tier=tier)
        
        result = {
            "basic": basic,
            "tier": tier,
            "relationship_narrative": ai_report.get("relationship_narrative", ""),
            "conflict_points": ai_report.get("conflict_points", []),
            "communication_guide": ai_report.get("communication_guide", {}),
            "prescription": ai_report.get("prescription", [])
        }
        if "growth_plan" in ai_report:
            result["growth_plan"] = ai_report["growth_plan"]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep compatibility generation failed: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    data: AskRequest,
    db: Session = Depends(get_db),
    is_premium: bool = Depends(_check_premium)
):
    """
    Premium tier: Ask a specific question based on chart data.
    The AI will analyze the question through the lens of all five systems.
    """
    try:
        ai_result = await generate_answer(
            chart=data.chart,
            question=data.question,
            lang=data.lang,
            tier=data.tier
        )
        
        return {
            "answer": ai_result.get("answer", ""),
            "relevant_systems": ai_result.get("relevant_systems", []),
            "confidence": ai_result.get("confidence", "中"),
            "disclaimer": ai_result.get("disclaimer", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")


@router.post("/family", response_model=FamilyResponse)
async def get_family_report(
    data: FamilyRequest,
    db: Session = Depends(get_db),
    is_premium: bool = Depends(_check_premium)
):
    """
    Premium tier: Get AI-generated family constellation report.
    Analyzes multiple family members' charts to reveal family dynamics.
    """
    try:
        # Compute charts for all members
        members_with_charts = []
        for member in data.members:
            m = member.model_dump()
            chart = compute_basic_chart(m)
            members_with_charts.append({
                "name": m.get("name", ""),
                "role": m.get("role", "member"),
                "chart": chart
            })
        
        # Generate AI family report
        ai_report = await generate_family_report(
            members=members_with_charts,
            lang=data.lang,
            tier=data.tier
        )
        
        return {
            "family_narrative": ai_report.get("family_narrative", ""),
            "member_reports": ai_report.get("member_reports", []),
            "relationship_matrix": ai_report.get("relationship_matrix", []),
            "family_prescription": ai_report.get("family_prescription", []),
            "communication_guide": ai_report.get("communication_guide", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Family report generation failed: {str(e)}")


@router.post("/annual", response_model=AnnualResponse)
async def get_annual_report(
    data: AnnualRequest,
    db: Session = Depends(get_db),
    is_premium: bool = Depends(_check_premium)
):
    """
    Premium tier: Get AI-generated annual destiny report.
    Analyzes the year's energy flow based on birth chart.
    """
    try:
        # Compute birth chart
        payload = {
            "name": data.name,
            "gender": data.gender,
            "date": data.date,
            "time": data.time,
            "location": data.location
        }
        chart = compute_basic_chart(payload)
        
        # Generate AI annual report
        ai_report = await generate_annual_report(
            chart=chart,
            year=data.year,
            lang=data.lang,
            tier=data.tier
        )
        
        return {
            "year_theme": ai_report.get("year_theme", ""),
            "yearly_overview": ai_report.get("yearly_overview", ""),
            "bazi_luck": ai_report.get("bazi_luck", {}),
            "key_opportunities": ai_report.get("key_opportunities", []),
            "key_challenges": ai_report.get("key_challenges", []),
            "monthly_insights": ai_report.get("monthly_insights", []),
            "annual_prescription": ai_report.get("annual_prescription", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annual report generation failed: {str(e)}")
