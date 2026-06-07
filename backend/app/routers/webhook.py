"""RevenueCat webhook handlers"""
import os
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import RevenueCatWebhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_revenuecat_signature(body: bytes, signature: Optional[str]) -> bool:
    secret = os.environ.get("REVENUECAT_WEBHOOK_SECRET", "")
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


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
    body = await request.body()
    if not _verify_revenuecat_signature(body, x_revenuecat_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event", {})
    event_type = event.get("type")

    # TODO: Update user subscription status in database

    return {"status": "ok", "event_type": event_type}
