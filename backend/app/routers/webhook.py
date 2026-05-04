"""RevenueCat webhook handlers"""
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import RevenueCatWebhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/revenuecat")
async def revenuecat_webhook(
    request: Request,
    x_revenuecat_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle RevenueCat webhook events.
    Events: INITIAL_PURCHASE, RENEWAL, CANCELLATION, EXPIRATION
    """
    # TODO: Verify webhook signature
    # TODO: Update user subscription status in database
    
    payload = await request.json()
    event = payload.get("event", {})
    event_type = event.get("type")
    
    # Log for now
    print(f"RevenueCat webhook received: {event_type}")
    print(f"Payload: {payload}")
    
    return {"status": "ok", "event_type": event_type}
