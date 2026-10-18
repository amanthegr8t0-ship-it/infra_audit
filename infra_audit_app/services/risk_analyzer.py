"""
Procurement Risk Analysis Service.

Evaluates bid competitiveness, identifies aggressive underbidding (which correlates
with quality shortcuts or project stalls), detects bidding anomalies, and predicts
delay probabilities based on historical contractor performance.
"""

from typing import Dict, Any, List
from models.tender import Tender, BidDetail
from models.contractor import Contractor
from config import ProcurementRiskRules


class RiskAnalyzer:
    def __init__(self, rules: ProcurementRiskRules = ProcurementRiskRules()):
        self.rules = rules

    def evaluate_tender_bids(self, tender: Tender) -> Dict[str, Any]:
        """
        Analyzes all bids submitted for a tender and produces objective risk indicators.
        """
        if not tender.bids:
            return {
                "tender_id": tender.id,
                "status": "NO_BIDS_SUBMITTED",
                "risk_flags": [],
                "l1_bid": None,
                "bid_spread_pct": 0.0,
            }

        sorted_bids = sorted(tender.bids, key=lambda b: b.quoted_amount_crores)
        l1 = sorted_bids[0]
        l1.is_l1 = True

        risk_flags: List[str] = []
        is_aggressive_underbid = l1.deviation_from_estimate_pct <= self.rules.ABNORMAL_LOW_BID_THRESHOLD_PCT

        if is_aggressive_underbid:
            risk_flags.append(
                f"ABNORMALLY_LOW_BID: L1 quote (₹{l1.quoted_amount_crores:.2f} Cr) is "
                f"{abs(l1.deviation_from_estimate_pct):.1f}% below official engineer estimate. "
                f"High correlation with sub-base thickness reduction and contractor liquidity strain."
            )

        if l1.deviation_from_estimate_pct >= self.rules.ABNORMAL_HIGH_BID_THRESHOLD_PCT:
            risk_flags.append(
                f"INFLATED_BID: L1 quote is {l1.deviation_from_estimate_pct:.1f}% above engineer estimate. "
                f"Indicates uncompetitive market or excessive risk premium."
            )

        # Check for cartel-like tightly clustered bidding if 3+ bidders
        spread = 0.0
        if len(sorted_bids) >= 3:
            quotes = [b.quoted_amount_crores for b in sorted_bids]
            spread = ((max(quotes) - min(quotes)) / min(quotes)) * 100
            if spread < 1.8:
                risk_flags.append(
                    f"TIGHT_BID_CLUSTER: Quoted bids across {len(quotes)} companies differ by only "
                    f"{spread:.2f}%. Signals potential bid-rigging or cover bidding."
                )

        return {
            "tender_id": tender.id,
            "estimated_cost_crores": tender.estimated_cost_crores,
            "l1_bidder": l1.bidder_name,
            "l1_quoted_amount_crores": l1.quoted_amount_crores,
            "l1_deviation_from_estimate_pct": l1.deviation_from_estimate_pct,
            "is_aggressive_underbid": is_aggressive_underbid,
            "bid_spread_pct": round(spread, 2),
            "risk_flags": risk_flags,
            "recommendation": (
                "Subject L1 to mandatory rate-analysis audit and enhanced performance guarantee before LOA issuance."
                if is_aggressive_underbid else "Procurement spread within standard competitive bounds."
            )
        }

    def predict_project_delay_risk(self, tender: Tender, contractor: Contractor) -> Dict[str, Any]:
        """
        Calculates empirical delay probability and estimated delay months based on
        contractor history and bid discount pressure.
        """
        # Baseline probability from contractor track record
        base_delay_prob = contractor.average_delay_rate_pct

        # Escalation factor if contractor underbid aggressively
        discount_penalty = 0.0
        l1_bid = next((b for b in tender.bids if b.bidder_id == contractor.id), None)
        if l1_bid and l1_bid.deviation_from_estimate_pct < -15.0:
            discount_penalty = abs(l1_bid.deviation_from_estimate_pct + 15.0) * 1.2

        composite_risk_prob = min(95.0, round(base_delay_prob + discount_penalty, 1))

        # Expected delay in months
        expected_delay_months = round(
            (composite_risk_prob / 100.0) * contractor.average_delay_months * 1.1, 1
        )

        risk_category = "LOW"
        if composite_risk_prob >= 50.0:
            risk_category = "HIGH"
        elif composite_risk_prob >= 25.0:
            risk_category = "MODERATE"

        return {
            "tender_id": tender.id,
            "contractor_id": contractor.id,
            "contractor_name": contractor.name,
            "delay_probability_pct": composite_risk_prob,
            "expected_delay_months": expected_delay_months,
            "risk_category": risk_category,
            "historical_on_time_rate_pct": round(
                (contractor.projects_completed_on_time / max(1, contractor.total_projects_completed)) * 100, 1
            ),
            "cost_overrun_risk_pct": contractor.average_cost_overrun_pct,
            "is_blacklisted": contractor.blacklisted,
        }
