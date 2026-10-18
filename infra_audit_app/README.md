# InfraAudit India - Civic Infrastructure & Procurement Transparency Platform

A modular platform designed to monitor public infrastructure tenders (NHAI, MoRTH, State PWDs), evaluate contractor track records, detect procurement risks (e.g., abnormally low bids), collect geotagged field evidence (potholes, structural defects), and gather citizen feedback with AI-driven reasoning moderation.

---

## 1. Architectural & Legal Philosophy
As established during the system design discussion:
1. **No "Tender Judge" Black-Box**: Direct crowd-voting on which contractor "should win" an open government tender violates public procurement laws, exposes operators to defamation lawsuits, and is vulnerable to astroturfing.
2. **Objective Civic Oversight**: Instead of declaring winners, the platform surfaces objective facts:
   - **Tender Data**: Official engineer estimates, quoted bidder prices, and L1 deviation percentages.
   - **Risk Signals**: Automated flags for aggressive underbidding (>20% below estimate) and cartel-like bidding clusters.
   - **Historical Performance**: Historical delay rates, cost overruns, and official blacklisting status.
   - **Ground-Truth Field Evidence**: Geotagged, timestamped photo evidence checked via geometric corridor geo-fencing (Haversine formula) and perceptual image hashing.
   - **Tiered Multi-Stakeholder Reviews**: Weighted opinion calculation (Citizen = 1x, Civil Engineer = 5x, Road Quality Inspector = 8x, Structural Engineer = 10x).
   - **AI Reasoning Quality Filter**: Enforces 5-day observation windows and checks feedback against defamation/slander while rewarding technical substance.

---

## 2. Directory Structure
```
infra_audit_app/
├── config.py                     # Governance rules, thresholds, reputation bonuses, tier weights
├── main.py                       # FastAPI entrypoint, middleware, static mount
├── requirements.txt              # Production dependencies
├── models/                       # Domain data models (Pydantic)
│   ├── tender.py                 # Tender, BidDetail, GeoPoint, TenderStatus
│   ├── contractor.py             # Contractor profile, PastProjectRecord
│   ├── evidence.py               # FieldEvidence, EvidenceType, VerificationStatus
│   └── review.py                 # CitizenReview, ReviewerTier, AIReasoningAssessment
├── services/                     # Core business logic & algorithms
│   ├── risk_analyzer.py          # L1 underbid analysis, delay risk probability
│   ├── verification_engine.py    # Haversine distance geofencing, EXIF check, hash deduplication
│   ├── ai_moderator.py           # NLP reasoning evaluator, defamation filter
│   └── audit_service.py          # Weighted composite scores, distress index, prediction vs reality
├── api/                          # FastAPI REST endpoints
│   ├── tenders_router.py         # /api/tenders, /api/tenders/{id}/risk-analysis
│   ├── contractors_router.py     # /api/contractors
│   ├── evidence_router.py        # /api/evidence/submit
│   └── reviews_router.py         # /api/reviews/submit (5-day gate & AI filter)
├── data/
│   └── mock_database.py          # Pre-seeded Indian infrastructure database (NHAI, MoRTH, PWD)
└── static/
    └── index.html                # Interactive single-page web application
```

---

## 3. Running the Backend
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Open `http://localhost:8000` to interact with the application and view API documentation at `http://localhost:8000/docs`.
