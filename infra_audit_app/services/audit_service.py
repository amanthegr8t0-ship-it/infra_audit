"""
Civic Infrastructure Audit & Composite Scoring Service.

Aggregates multi-tier expert & citizen reviews using weighted mathematical formulas,
computes on-ground road distress indices from verified evidence, and tracks
predicted timelines vs real execution milestones.
"""

from typing import List, Dict, Any, Optional
from models.review import CitizenReview, ReviewerTier
from models.evidence import FieldEvidence, VerificationStatus
from models.tender import Tender
from config import REVIEWER_TIER_WEIGHTS


class AuditService:
    def __init__(self, tier_weights: Dict[str, float] = REVIEWER_TIER_WEIGHTS):
        self.tier_weights = tier_weights

    def calculate_weighted_quality_score(self, reviews: List[CitizenReview]) -> Dict[str, Any]:
        """
        Calculates the composite quality score:
        Composite Score = SUM(Rating_i * Weight_tier) / SUM(Weight_tier)
        """
        approved_reviews = [r for r in reviews if r.approved_for_public_display]

        if not approved_reviews:
            return {
                "composite_score": None,
                "total_reviews": 0,
                "tier_breakdown": {},
                "weighted_confidence_index": 0.0,
            }

        weighted_sum = 0.0
        total_weight = 0.0
        tier_counts: Dict[str, int] = {}

        for rev in approved_reviews:
            weight = self.tier_weights.get(rev.reviewer_tier.value, 1.0)
            weighted_sum += rev.rating * weight
            total_weight += weight
            tier_name = rev.reviewer_tier.value
            tier_counts[tier_name] = tier_counts.get(tier_name, 0) + 1

        composite = round(weighted_sum / total_weight, 2)
        confidence_index = round(min(100.0, (total_weight / 30.0) * 100.0), 1)

        return {
            "composite_score": composite,
            "total_reviews": len(approved_reviews),
            "tier_breakdown": tier_counts,
            "total_weighted_volume": round(total_weight, 1),
            "weighted_confidence_index": confidence_index,
        }

    def compute_ground_distress_index(self, evidence_list: List[FieldEvidence]) -> Dict[str, Any]:
        """
        Calculates an empirical road distress score (0-100) based on verified field evidence.
        0 = Pristine / Smooth, 100 = Catastrophic breakdown.
        """
        verified = [e for e in evidence_list if e.verification_status == VerificationStatus.VERIFIED_GROUND_TRUTH]

        if not verified:
            return {
                "distress_index": 0.0,
                "verified_incidents_count": 0,
                "severity_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "status_label": "NO_VERIFIED_DEFECTS_RECORDED"
            }

        total_severity_points = sum(e.severity_level for e in verified)
        # Scaled distress index: 5 high-severity defects approach high distress
        distress_score = round(min(100.0, (total_severity_points / (len(verified) * 5.0)) * min(100.0, len(verified) * 20.0)), 1)

        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for e in verified:
            distribution[e.severity_level] += 1

        label = "ACCEPTABLE"
        if distress_score > 60:
            label = "CRITICAL_DEFECTS_DETECTED"
        elif distress_score > 30:
            label = "MODERATE_WEAR_AND_TEAR"

        return {
            "distress_index": distress_score,
            "verified_incidents_count": len(verified),
            "severity_distribution": distribution,
            "status_label": label
        }

    def assess_prediction_vs_reality(
        self, tender: Tender, predicted_delay_risk_pct: float, evidence_list: List[FieldEvidence]
    ) -> Dict[str, Any]:
        """
        Compares pre-award risk prediction against real-world ground-truth delivery status.
        """
        distress = self.compute_ground_distress_index(evidence_list)

        # Audit verdict comparing prediction with actual performance
        alignment = "ON_TRACK"
        if predicted_delay_risk_pct > 50.0 and distress["distress_index"] > 40.0:
            alignment = "CONFIRMED_HIGH_RISK_FAILURE: Pre-award risk warnings matched post-construction defect surge."
        elif predicted_delay_risk_pct <= 25.0 and distress["distress_index"] <= 20.0:
            alignment = "CONSISTENT_HIGH_QUALITY: Low risk prediction validated by sound ground conditions."
        elif predicted_delay_risk_pct > 50.0 and distress["distress_index"] <= 15.0:
            alignment = "OVERPERFORMANCE: Contractor managed to exceed historical delay expectations."

        return {
            "tender_id": tender.id,
            "tender_title": tender.title,
            "target_duration_months": tender.target_duration_months,
            "predicted_delay_risk_pct": predicted_delay_risk_pct,
            "ground_distress_index": distress["distress_index"],
            "verified_evidence_count": distress["verified_incidents_count"],
            "audit_verdict": alignment
        }
