"""
Data Models for Ground-Truth Field Evidence (Potholes, Structural Damage, Progress).
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EvidenceType(str, Enum):
    POTHOLE_CLUSTER = "POTHOLE_CLUSTER"
    SURFACE_CRACKING = "SURFACE_CRACKING"
    WATERLOGGING_DRAINAGE = "WATERLOGGING_DRAINAGE"
    STRUCTURAL_DEFORMATION = "STRUCTURAL_DEFORMATION"
    WORK_ABANDONED_STALLED = "WORK_ABANDONED_STALLED"
    COMPLETED_SMOOTH_STRETCH = "COMPLETED_SMOOTH_STRETCH"


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED_GROUND_TRUTH = "VERIFIED_GROUND_TRUTH"
    REJECTED_OUT_OF_BOUNDS = "REJECTED_OUT_OF_BOUNDS"
    REJECTED_STALE_TIMESTAMP = "REJECTED_STALE_TIMESTAMP"
    REJECTED_DUPLICATE_IMAGE = "REJECTED_DUPLICATE_IMAGE"
    REJECTED_SPOOFED_TAMPERED = "REJECTED_SPOOFED_TAMPERED"


class FieldEvidence(BaseModel):
    id: str
    tender_id: str
    submitter_id: str
    submitter_tier: str  # CITIZEN, CIVIL_ENGINEER, etc.
    latitude: float
    longitude: float
    captured_at: datetime
    submitted_at: datetime
    image_hash: str
    image_url: str
    evidence_type: EvidenceType
    severity_level: int = Field(ge=1, le=5, description="1 minor, 5 dangerous structural fault")
    description: str
    verification_status: VerificationStatus = VerificationStatus.PENDING
    distance_to_corridor_meters: Optional[float] = None
    reputation_points_delta: int = 0
    verification_notes: Optional[str] = None
