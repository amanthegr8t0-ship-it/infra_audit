"""
In-Memory Mock Database seeded with realistic Indian Public Infrastructure Procurement Records.
Includes NHAI, MoRTH, and State PWD projects, along with contractor profiles, bids, and evidence.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List
from models.tender import Tender, TenderStatus, TenderCategory, BidDetail, GeoPoint
from models.contractor import Contractor, PastProjectRecord
from models.evidence import FieldEvidence, EvidenceType, VerificationStatus
from models.review import CitizenReview, ReviewerTier, AIReasoningAssessment


class MockDatabase:
    def __init__(self):
        self.tenders: Dict[str, Tender] = {}
        self.contractors: Dict[str, Contractor] = {}
        self.evidence: Dict[str, List[FieldEvidence]] = {}
        self.reviews: Dict[str, List[CitizenReview]] = {}
        self._seed_data()

    def _seed_data(self):
        # 1. Seed Contractors
        c1 = Contractor(
            id="CONT-001",
            name="Eastern Infracon Projects Ltd",
            registration_number="ROC-WB-98231",
            year_established=2008,
            total_projects_completed=18,
            projects_completed_on_time=15,
            average_delay_rate_pct=16.6,
            average_delay_months=2.4,
            average_cost_overrun_pct=4.2,
            blacklisted=False,
            historical_quality_rating=4.3,
            financial_stability_score=88.5,
            past_projects=[
                PastProjectRecord(
                    project_id="P-101",
                    project_name="NH-12 Ranaghat 4-Laning",
                    authority="NHAI",
                    contract_value_crores=340.0,
                    planned_duration_months=24,
                    actual_duration_months=26,
                    delay_months=2,
                    cost_overrun_pct=3.1,
                    post_completion_defect_score=1.5
                )
            ]
        )

        c2 = Contractor(
            id="CONT-002",
            name="Apex Highway & Metro Builders",
            registration_number="ROC-DL-44129",
            year_established=2014,
            total_projects_completed=12,
            projects_completed_on_time=5,
            average_delay_rate_pct=58.3,
            average_delay_months=8.5,
            average_cost_overrun_pct=19.4,
            blacklisted=False,
            historical_quality_rating=2.7,
            financial_stability_score=62.0,
            past_projects=[
                PastProjectRecord(
                    project_id="P-202",
                    project_name="Durgapur Expressway Flyover",
                    authority="WB PWD",
                    contract_value_crores=185.0,
                    planned_duration_months=18,
                    actual_duration_months=31,
                    delay_months=13,
                    cost_overrun_pct=22.5,
                    post_completion_defect_score=6.8
                )
            ]
        )

        c3 = Contractor(
            id="CONT-003",
            name="Vistara Structural Bridges Corp",
            registration_number="ROC-MH-77182",
            year_established=2011,
            total_projects_completed=9,
            projects_completed_on_time=2,
            average_delay_rate_pct=77.8,
            average_delay_months=14.0,
            average_cost_overrun_pct=34.0,
            blacklisted=True,
            blacklist_reason="Disqualified by MoRTH in 2023 for catastrophic girder sag due to substandard grade concrete.",
            historical_quality_rating=1.4,
            financial_stability_score=31.0,
            past_projects=[]
        )

        c4 = Contractor(
            id="CONT-004",
            name="Bengal State Roads & Civil Infrastructure",
            registration_number="ROC-WB-11209",
            year_established=2003,
            total_projects_completed=26,
            projects_completed_on_time=21,
            average_delay_rate_pct=19.2,
            average_delay_months=3.1,
            average_cost_overrun_pct=6.5,
            blacklisted=False,
            historical_quality_rating=4.1,
            financial_stability_score=82.0,
            past_projects=[]
        )

        self.contractors = {c.id: c for c in [c1, c2, c3, c4]}

        # 2. Seed Tenders
        now = datetime.now(timezone.utc)

        t1 = Tender(
            id="TND-2026-NHAI-091",
            reference_number="NHAI/RO-KOL/NH-34/4L/2026/091",
            title="4-Laning of NH-34 Stretch (Barasat to Krishnanagar Km 28.000 to Km 54.000)",
            authority="National Highways Authority of India (NHAI)",
            category=TenderCategory.HIGHWAY,
            state="West Bengal",
            district="North 24 Parganas & Nadia",
            corridor_start=GeoPoint(latitude=22.7210, longitude=88.4820),
            corridor_end=GeoPoint(latitude=23.4010, longitude=88.5020),
            estimated_cost_crores=425.0,
            target_duration_months=30,
            published_date=now - timedelta(days=45),
            bid_opening_date=now - timedelta(days=12),
            award_date=now - timedelta(days=2),
            awarded_contractor_id="CONT-002",
            awarded_amount_crores=322.0,  # -24.2% below estimate (Abnormally Low Bid)
            status=TenderStatus.AWARDED,
            bids=[
                BidDetail(
                    bidder_id="CONT-002",
                    bidder_name="Apex Highway & Metro Builders",
                    quoted_amount_crores=322.0,
                    technical_score=78.5,
                    is_l1=True,
                    deviation_from_estimate_pct=-24.24,
                    submission_date=now - timedelta(days=14)
                ),
                BidDetail(
                    bidder_id="CONT-001",
                    bidder_name="Eastern Infracon Projects Ltd",
                    quoted_amount_crores=398.0,
                    technical_score=94.0,
                    is_l1=False,
                    deviation_from_estimate_pct=-6.35,
                    submission_date=now - timedelta(days=15)
                ),
                BidDetail(
                    bidder_id="CONT-004",
                    bidder_name="Bengal State Roads & Civil Infrastructure",
                    quoted_amount_crores=412.0,
                    technical_score=89.5,
                    is_l1=False,
                    deviation_from_estimate_pct=-3.06,
                    submission_date=now - timedelta(days=13)
                ),
            ],
            specification_summary="Bituminous Concrete (BC) wearing course 50mm over Dense Bituminous Macadam (DBM) 100mm, with 6 underpasses and storm water box drains."
        )

        t2 = Tender(
            id="TND-2026-PWD-404",
            reference_number="WB/PWD/KOL/FLY/2026/04",
            title="Construction of 4-Lane Elevated Corridor on EM Bypass connecting New Town Connector",
            authority="West Bengal Public Works Department (WB PWD)",
            category=TenderCategory.FLYOVER,
            state="West Bengal",
            district="Kolkata",
            corridor_start=GeoPoint(latitude=22.5180, longitude=88.3990),
            corridor_end=GeoPoint(latitude=22.5690, longitude=88.4320),
            estimated_cost_crores=280.0,
            target_duration_months=24,
            published_date=now - timedelta(days=20),
            bid_opening_date=now - timedelta(days=1),
            status=TenderStatus.FINANCIAL_BID_OPENED,
            bids=[
                BidDetail(
                    bidder_id="CONT-001",
                    bidder_name="Eastern Infracon Projects Ltd",
                    quoted_amount_crores=271.5,
                    technical_score=92.0,
                    is_l1=True,
                    deviation_from_estimate_pct=-3.04,
                    submission_date=now - timedelta(days=3)
                ),
                BidDetail(
                    bidder_id="CONT-004",
                    bidder_name="Bengal State Roads & Civil Infrastructure",
                    quoted_amount_crores=276.0,
                    technical_score=90.0,
                    is_l1=False,
                    deviation_from_estimate_pct=-1.43,
                    submission_date=now - timedelta(days=4)
                ),
            ],
            specification_summary="Pre-stressed concrete (PSC) I-girders with elastomeric bearings and noise barriers across residential sectors."
        )

        t3 = Tender(
            id="TND-2026-MORTH-811",
            reference_number="MoRTH/BR/TEESTA/2026/811",
            title="High-Level 4-Lane Bridge over River Teesta with Approaches on NH-31D",
            authority="Ministry of Road Transport and Highways (MoRTH)",
            category=TenderCategory.BRIDGE,
            state="West Bengal",
            district="Jalpaiguri",
            corridor_start=GeoPoint(latitude=26.5400, longitude=88.7100),
            corridor_end=GeoPoint(latitude=26.5650, longitude=88.7350),
            estimated_cost_crores=560.0,
            target_duration_months=36,
            published_date=now - timedelta(days=8),
            bid_opening_date=now + timedelta(days=22),
            status=TenderStatus.PUBLISHED_BIDDING,
            bids=[],
            specification_summary="Cable-stayed navigation span with seismic dampers and deep well foundation in active alluvial riverbed."
        )

        self.tenders = {t.id: t for t in [t1, t2, t3]}

        # 3. Seed Evidence for T1
        ev1 = FieldEvidence(
            id="EV-901",
            tender_id="TND-2026-NHAI-091",
            submitter_id="USR-CITIZEN-412",
            submitter_tier="CITIZEN",
            latitude=22.7420,
            longitude=88.4845,
            captured_at=now - timedelta(hours=14),
            submitted_at=now - timedelta(hours=12),
            image_hash="hash_a8f9b2311400e",
            image_url="https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600",
            evidence_type=EvidenceType.POTHOLE_CLUSTER,
            severity_level=4,
            description="Deep crater-like potholes recurring at Km 31 marker right after light rain. Sub-base aggregate visibly exposed.",
            verification_status=VerificationStatus.VERIFIED_GROUND_TRUTH,
            distance_to_corridor_meters=42.0,
            reputation_points_delta=5,
            verification_notes="Verified: Coordinates within 42m of corridor. Fresh timestamp. +5 rep."
        )

        ev2 = FieldEvidence(
            id="EV-902",
            tender_id="TND-2026-NHAI-091",
            submitter_id="USR-ENG-881",
            submitter_tier="CIVIL_ENGINEER",
            latitude=22.8105,
            longitude=88.4910,
            captured_at=now - timedelta(hours=28),
            submitted_at=now - timedelta(hours=26),
            image_hash="hash_77c1d09e32f5a",
            image_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?w=600",
            evidence_type=EvidenceType.SURFACE_CRACKING,
            severity_level=3,
            description="Longitudinal surface cracking detected along 200m section. Indicates inadequate bitumen binder grade or delayed compaction.",
            verification_status=VerificationStatus.VERIFIED_GROUND_TRUTH,
            distance_to_corridor_meters=35.5,
            reputation_points_delta=5,
            verification_notes="Verified: Civil engineer site report. Within 35m of corridor."
        )

        self.evidence = {
            "TND-2026-NHAI-091": [ev1, ev2],
            "TND-2026-PWD-404": [],
            "TND-2026-MORTH-811": []
        }

        # 4. Seed Reviews for T1
        r1 = CitizenReview(
            id="REV-01",
            tender_id="TND-2026-NHAI-091",
            contractor_id="CONT-002",
            reviewer_id="USR-ENG-881",
            reviewer_tier=ReviewerTier.CIVIL_ENGINEER,
            rating=2.0,
            submitted_at=now - timedelta(days=1),
            text_reasoning="Apex Builders quoted -24% below the MoRTH standard schedule of rates. At this margin, they cannot procure VG-30 grade bitumen and have omitted necessary cross-drainage culverts between Km 32-35, leading to immediate waterlogging.",
            ai_assessment=AIReasoningAssessment(
                is_substantive=True,
                contains_unsubstantiated_defamation=False,
                cites_verifiable_metrics=True,
                reasoning_quality_score=92.0,
                sentiment_balance="HIGH_QUALITY_ANALYTICAL",
                moderation_verdict="APPROVED",
                feedback_notes="Approved: Highly substantive technical feedback citing specific materials (VG-30 bitumen) and locations."
            ),
            approved_for_public_display=True,
            effective_weight=5.0
        )

        r2 = CitizenReview(
            id="REV-02",
            tender_id="TND-2026-NHAI-091",
            contractor_id="CONT-002",
            reviewer_id="USR-CITIZEN-412",
            reviewer_tier=ReviewerTier.CITIZEN,
            rating=1.5,
            submitted_at=now - timedelta(hours=8),
            text_reasoning="The road surface at the Barasat junction is already peeling off just two weeks after initial tarring. Huge dust and loose aggregate stones are flying into commuter windshields.",
            ai_assessment=AIReasoningAssessment(
                is_substantive=True,
                contains_unsubstantiated_defamation=False,
                cites_verifiable_metrics=True,
                reasoning_quality_score=78.0,
                sentiment_balance="OBJECTIVE",
                moderation_verdict="APPROVED",
                feedback_notes="Approved: Observable ground-truth testimony."
            ),
            approved_for_public_display=True,
            effective_weight=1.0
        )

        self.reviews = {
            "TND-2026-NHAI-091": [r1, r2],
            "TND-2026-PWD-404": [],
            "TND-2026-MORTH-811": []
        }


# Singleton database instance
db = MockDatabase()
