"""Free tier APIs - no auth required, no AI, pure code"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import ProfileCreate, BasicChartResponse, CompatibilityBasicRequest, CompatibilityBasicResponse
from app.services.chart_service import compute_basic_chart, compute_compatibility_basic

router = APIRouter(prefix="/api/free", tags=["free"])


@router.post("/chart", response_model=BasicChartResponse)
async def get_basic_chart(
    data: ProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Free tier: Get basic chart data for a single person.
    No authentication required. Pure code computation.
    """
    try:
        payload = data.model_dump()
        result = compute_basic_chart(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chart computation failed: {str(e)}")


@router.post("/compatibility", response_model=CompatibilityBasicResponse)
async def get_basic_compatibility(
    data: CompatibilityBasicRequest,
    db: Session = Depends(get_db)
):
    """
    Free tier: Get basic compatibility between two people.
    Returns 5-dimension score + one-line summary.
    No authentication required. Pure code computation.
    """
    try:
        result = compute_compatibility_basic(
            data.person1.model_dump(),
            data.person2.model_dump()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compatibility computation failed: {str(e)}")
