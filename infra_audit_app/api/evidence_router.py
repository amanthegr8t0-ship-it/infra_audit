"""
Evidence API Router.
Handles ground-truth field evidence submissions (potholes, structural cracks),
executing automatic geo-fencing, EXIF timestamp verification, and reputation adjustments.
"""

from typing import List
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from models.evidence import FieldEvidence, EvidenceType, VerificationStatus
from data.mock_database import db
from services.verification_engine import VerificationEngine

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])
verification_engine = VerificationEngine()


class EvidenceSubmissionRequest(BaseModel):
    tender_id: str
    submitter_id: str
    submitter_tier: str = "CITIZEN"
    latitude: float
    longitude: float
    captured_at: datetime
    image_hash: str
    image_url: str
    evidence_type: EvidenceType
    severity_level: int = Field(ge=1, le=5)
    description: str


@router.post("/submit", response_model=FieldEvidence)
def submit_evidence(payload: EvidenceSubmissionRequest):
    tender = db.tenders.get(payload.tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    new_evidence = FieldEvidence(
        id=f"EV-{uuid.uuid4().hex[:6].upper()}",
        tender_id=payload.tender_id,
        submitter_id=payload.submitter_id,
        submitter_tier=payload.submitter_tier,
        latitude=payload.latitude,
        longitude=payload.longitude,
        captured_at=payload.captured_at,
        submitted_at=datetime.now(timezone.utc),
        image_hash=payload.image_hash,
        image_url=payload.image_url,
        evidence_type=payload.evidence_type,
        severity_level=payload.severity_level,
        description=payload.description,
        verification_status=VerificationStatus.PENDING
    )

    # Run geometric and freshness verification
    verified = verification_engine.verify_submission(new_evidence, tender)

    # Store in database
    if payload.tender_id not in db.evidence:
        db.evidence[payload.tender_id] = []
    db.evidence[payload.tender_id].append(verified)

    return verified


@router.get("/tender/{tender_id}", response_model=List[FieldEvidence])
def get_tender_evidence(tender_id: str):
    return db.evidence.get(tender_id, [])
