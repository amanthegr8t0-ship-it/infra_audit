"""
Reviews API Router.
Handles citizen and expert reviews, enforcing the 5-day observation window
and executing AI reasoning moderation against slander/defamation.
"""

from typing import List, Optional
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from models.review import CitizenReview, ReviewerTier
from data.mock_database import db
from services.ai_moderator import AIReasoningModerator
from config import VerificationRules, REVIEWER_TIER_WEIGHTS

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])
ai_moderator = AIReasoningModerator()


class ReviewSubmissionRequest(BaseModel):
    tender_id: str
    contractor_id: Optional[str] = None
    reviewer_id: str
    reviewer_tier: ReviewerTier = ReviewerTier.CITIZEN
    rating: float = Field(ge=1.0, le=5.0)
    text_reasoning: str


@router.post("/submit", response_model=CitizenReview)
def submit_review(payload: ReviewSubmissionRequest):
    tender = db.tenders.get(payload.tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Enforce 5-day observation window from tender bid opening / publishing
    now = datetime.now(timezone.utc)
    days_since_bid_opening = (now - tender.bid_opening_date).total_seconds() / 86400.0

    if days_since_bid_opening < VerificationRules.OBSERVATION_WINDOW_DAYS:
        remaining_days = round(VerificationRules.OBSERVATION_WINDOW_DAYS - days_since_bid_opening, 1)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Observation window active. Public opinion opens {remaining_days} days later "
                f"to allow field verification and prevent premature speculation."
            )
        )

    # Run AI reasoning moderation
    assessment = ai_moderator.evaluate_reasoning(payload.text_reasoning)

    is_approved = assessment.moderation_verdict == "APPROVED"
    effective_weight = REVIEWER_TIER_WEIGHTS.get(payload.reviewer_tier.value, 1.0)

    review = CitizenReview(
        id=f"REV-{uuid.uuid4().hex[:6].upper()}",
        tender_id=payload.tender_id,
        contractor_id=payload.contractor_id,
        reviewer_id=payload.reviewer_id,
        reviewer_tier=payload.reviewer_tier,
        rating=payload.rating,
        submitted_at=now,
        text_reasoning=payload.text_reasoning,
        ai_assessment=assessment,
        approved_for_public_display=is_approved,
        effective_weight=effective_weight
    )

    if payload.tender_id not in db.reviews:
        db.reviews[payload.tender_id] = []
    db.reviews[payload.tender_id].append(review)

    return review


@router.get("/tender/{tender_id}", response_model=List[CitizenReview])
def get_tender_reviews(tender_id: str):
    return db.reviews.get(tender_id, [])
