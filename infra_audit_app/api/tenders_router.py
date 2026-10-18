"""
Tenders API Router.
Handles endpoints for querying public tenders, bids, risk scores, and audit summaries.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.tender import Tender, TenderStatus
from data.mock_database import db
from services.risk_analyzer import RiskAnalyzer
from services.audit_service import AuditService

router = APIRouter(prefix="/api/tenders", tags=["Tenders"])
risk_analyzer = RiskAnalyzer()
audit_service = AuditService()


@router.get("", response_model=List[Tender])
def list_tenders(
    authority: Optional[str] = Query(None, description="Filter by authority e.g. NHAI, WB PWD, MoRTH"),
    status: Optional[TenderStatus] = Query(None, description="Filter by tender status"),
    state: Optional[str] = Query(None, description="Filter by state e.g. West Bengal")
):
    results = list(db.tenders.values())
    if authority:
        results = [t for t in results if authority.lower() in t.authority.lower()]
    if status:
        results = [t for t in results if t.status == status]
    if state:
        results = [t for t in results if state.lower() in t.state.lower()]
    return results


@router.get("/{tender_id}", response_model=Tender)
def get_tender(tender_id: str):
    tender = db.tenders.get(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.get("/{tender_id}/risk-analysis")
def get_tender_risk_analysis(tender_id: str):
    tender = db.tenders.get(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    bid_risk = risk_analyzer.evaluate_tender_bids(tender)

    # Delay predictions for bidders
    delay_predictions = []
    for bid in tender.bids:
        contractor = db.contractors.get(bid.bidder_id)
        if contractor:
            pred = risk_analyzer.predict_project_delay_risk(tender, contractor)
            delay_predictions.append(pred)

    return {
        "tender_id": tender.id,
        "bid_analysis": bid_risk,
        "contractor_delay_predictions": delay_predictions
    }


@router.get("/{tender_id}/audit-summary")
def get_tender_audit_summary(tender_id: str):
    tender = db.tenders.get(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    reviews = db.reviews.get(tender_id, [])
    evidence = db.evidence.get(tender_id, [])

    weighted_score = audit_service.calculate_weighted_quality_score(reviews)
    distress = audit_service.compute_ground_distress_index(evidence)

    # Get predicted risk if contractor awarded
    delay_prob = 35.0
    if tender.awarded_contractor_id:
        c = db.contractors.get(tender.awarded_contractor_id)
        if c:
            pred = risk_analyzer.predict_project_delay_risk(tender, c)
            delay_prob = pred["delay_probability_pct"]

    reality_check = audit_service.assess_prediction_vs_reality(tender, delay_prob, evidence)

    return {
        "tender_id": tender.id,
        "weighted_quality_score": weighted_score,
        "ground_distress_index": distress,
        "prediction_vs_reality": reality_check,
        "total_verified_evidence_items": len([e for e in evidence if e.verification_status.value == "VERIFIED_GROUND_TRUTH"])
    }
