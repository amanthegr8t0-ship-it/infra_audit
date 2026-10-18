"""
InfraAudit Platform - Core Configuration & Domain Constants

Defines governance thresholds, observation delays, geo-fencing tolerances,
reputation penalties/bonuses, and reviewer weighting tiers.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationRules:
    # Minimum observation buffer in days before citizen opinion ratings are unlocked
    OBSERVATION_WINDOW_DAYS: int = 5

    # Geo-fencing tolerance radius in meters from the road corridor/bounding coordinates
    GEO_TOLERANCE_METERS: float = 250.0

    # Maximum age of field evidence photos in hours from EXIF capture timestamp
    MAX_PHOTO_AGE_HOURS: int = 72

    # Reputation scoring deltas
    REP_BONUS_VERIFIED_EVIDENCE: int = 5
    REP_PENALTY_UNVERIFIED_EVIDENCE: int = -15
    REP_PENALTY_FAKE_OR_SPOOFED: int = -50


@dataclass(frozen=True)
class ProcurementRiskRules:
    # If L1 bid is more than 20% below estimated cost, flag as Aggressive Underbidding
    ABNORMAL_LOW_BID_THRESHOLD_PCT: float = -20.0

    # If L1 bid is more than 15% above estimated cost, flag as Escalated Budget
    ABNORMAL_HIGH_BID_THRESHOLD_PCT: float = 15.0

    # Threshold for contractor historical delay rate (in %) that triggers high risk warning
    CONTRACTOR_DELAY_RISK_THRESHOLD_PCT: float = 25.0


# Expert review weighting factors established in the governance framework
REVIEWER_TIER_WEIGHTS: Dict[str, float] = {
    "CITIZEN": 1.0,
    "CIVIL_ENGINEER": 5.0,
    "ROAD_QUALITY_INSPECTOR": 8.0,
    "STRUCTURAL_ENGINEER": 10.0,
}
