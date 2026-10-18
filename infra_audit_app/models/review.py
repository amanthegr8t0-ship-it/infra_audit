"""
Data Models for Moderated Civic Feedback, AI Reasoning Quality, and Tiered Reviews.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReviewerTier(str, Enum):
    CITIZEN = "CITIZEN"
    CIVIL_ENGINEER = "CIVIL_ENGINEER"
    ROAD_QUALITY_INSPECTOR = "ROAD_QUALITY_INSPECTOR"
    STRUCTURAL_ENGINEER = "STRUCTURAL_ENGINEER"


class AIReasoningAssessment(BaseModel):
    is_substantive: bool
    contains_unsubstantiated_defamation: bool
    cites_verifiable_metrics: bool
    reasoning_quality_score: float = Field(ge=0.0, le=100.0)
    sentiment_balance: str  # OBJECTIVE, EMOTIVE, SPAM
    moderation_verdict: str  # APPROVED, REJECTED, FLAGGED_FOR_MANUAL_REVIEW
    feedback_notes: str


class CitizenReview(BaseModel):
    id: str
    tender_id: str
    contractor_id: Optional[str] = None
    reviewer_id: str
    reviewer_tier: ReviewerTier
    rating: float = Field(ge=1.0, le=5.0)
    submitted_at: datetime
    text_reasoning: str
    ai_assessment: Optional[AIReasoningAssessment] = None
    approved_for_public_display: bool = False
    effective_weight: float = 1.0
