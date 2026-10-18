"""
Field Evidence Verification Engine.

Performs geometric geo-fencing (Haversine corridor distance), EXIF timestamp freshness audits,
perceptual hash duplicate checks, and applies governance reputation point adjustments.
"""

import math
from datetime import datetime, timezone
from typing import Set, Tuple
from models.evidence import FieldEvidence, VerificationStatus
from models.tender import Tender
from config import VerificationRules


class VerificationEngine:
    def __init__(self, rules: VerificationRules = VerificationRules()):
        self.rules = rules
        self.seen_image_hashes: Set[str] = set()

    @staticmethod
    def _haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two GPS coordinates in meters."""
        r = 6371000.0  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def _distance_to_segment_meters(
        self, p_lat: float, p_lon: float,
        start_lat: float, start_lon: float,
        end_lat: float, end_lon: float
    ) -> float:
        """Approximates shortest distance in meters from point P to line segment (Start - End)."""
        # For simplicity and robust corridor bounds, evaluate min distance to endpoints and midpoint
        mid_lat = (start_lat + end_lat) / 2.0
        mid_lon = (start_lon + end_lon) / 2.0

        d_start = self._haversine_distance_meters(p_lat, p_lon, start_lat, start_lon)
        d_end = self._haversine_distance_meters(p_lat, p_lon, end_lat, end_lon)
        d_mid = self._haversine_distance_meters(p_lat, p_lon, mid_lat, mid_lon)

        return min(d_start, d_end, d_mid)

    def verify_submission(
        self, evidence: FieldEvidence, tender: Tender
    ) -> FieldEvidence:
        """
        Validates evidence against geo-boundaries, timestamp age, and image uniqueness.
        Assigns verification status and reputation point delta (+5 / -15 / -50).
        """
        # 1. Geo-fence verification
        corridor_dist = self._distance_to_segment_meters(
            evidence.latitude, evidence.longitude,
            tender.corridor_start.latitude, tender.corridor_start.longitude,
            tender.corridor_end.latitude, tender.corridor_end.longitude
        )
        evidence.distance_to_corridor_meters = round(corridor_dist, 1)

        if corridor_dist > self.rules.GEO_TOLERANCE_METERS:
            evidence.verification_status = VerificationStatus.REJECTED_OUT_OF_BOUNDS
            evidence.reputation_points_delta = self.rules.REP_PENALTY_UNVERIFIED_EVIDENCE
            evidence.verification_notes = (
                f"Coordinates ({evidence.latitude:.5f}, {evidence.longitude:.5f}) are "
                f"{corridor_dist:.1f}m away from road corridor (Tolerance: {self.rules.GEO_TOLERANCE_METERS}m)."
            )
            return evidence

        # 2. Timestamp freshness verification
        # Compare capture time with submission time
        delta_hours = abs((evidence.submitted_at - evidence.captured_at).total_seconds()) / 3600.0
        if delta_hours > self.rules.MAX_PHOTO_AGE_HOURS:
            evidence.verification_status = VerificationStatus.REJECTED_STALE_TIMESTAMP
            evidence.reputation_points_delta = self.rules.REP_PENALTY_UNVERIFIED_EVIDENCE
            evidence.verification_notes = (
                f"EXIF capture timestamp is {delta_hours:.1f} hours old. Maximum allowed age is "
                f"{self.rules.MAX_PHOTO_AGE_HOURS} hours to prevent recycled imagery."
            )
            return evidence

        # 3. Duplicate perceptual image hash detection
        if evidence.image_hash in self.seen_image_hashes:
            evidence.verification_status = VerificationStatus.REJECTED_DUPLICATE_IMAGE
            evidence.reputation_points_delta = self.rules.REP_PENALTY_FAKE_OR_SPOOFED
            evidence.verification_notes = (
                "Duplicate image hash detected. Identical photo was previously submitted. "
                "Penalized for sybil/bot manipulation attempt."
            )
            return evidence

        # Passed all verification checks
        self.seen_image_hashes.add(evidence.image_hash)
        evidence.verification_status = VerificationStatus.VERIFIED_GROUND_TRUTH
        evidence.reputation_points_delta = self.rules.REP_BONUS_VERIFIED_EVIDENCE
        evidence.verification_notes = (
            f"Verified ground truth! Within {corridor_dist:.1f}m of corridor. Fresh timestamp ({delta_hours:.1f}h old). "
            f"+{self.rules.REP_BONUS_VERIFIED_EVIDENCE} reputation awarded."
        )
        return evidence
