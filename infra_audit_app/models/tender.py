"""
Data Models for Tenders, Bidders, and Procurement Status.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TenderStatus(str, Enum):
    PUBLISHED_BIDDING = "PUBLISHED_BIDDING"
    TECHNICAL_EVALUATION = "TECHNICAL_EVALUATION"
    FINANCIAL_BID_OPENED = "FINANCIAL_BID_OPENED"
    AWARDED = "AWARDED"
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TenderCategory(str, Enum):
    HIGHWAY = "HIGHWAY"
    BRIDGE = "BRIDGE"
    FLYOVER = "FLYOVER"
    RURAL_ROAD = "RURAL_ROAD"
    URBAN_ARTERY = "URBAN_ARTERY"


class BidDetail(BaseModel):
    bidder_id: str
    bidder_name: str
    quoted_amount_crores: float
    technical_score: float = Field(ge=0.0, le=100.0)
    is_l1: bool = False
    deviation_from_estimate_pct: float
    submission_date: datetime


class GeoPoint(BaseModel):
    latitude: float
    longitude: float


class Tender(BaseModel):
    id: str
    reference_number: str
    title: str
    authority: str  # e.g., NHAI, MoRTH, WB PWD, CPWD
    category: TenderCategory
    state: str
    district: str
    corridor_start: GeoPoint
    corridor_end: GeoPoint
    estimated_cost_crores: float
    target_duration_months: int
    published_date: datetime
    bid_opening_date: datetime
    award_date: Optional[datetime] = None
    awarded_contractor_id: Optional[str] = None
    awarded_amount_crores: Optional[float] = None
    status: TenderStatus
    bids: List[BidDetail] = Field(default_factory=list)
    specification_summary: str
