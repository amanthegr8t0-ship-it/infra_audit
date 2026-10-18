"""
Data Models for Contractors and Historical Track Records.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PastProjectRecord(BaseModel):
    project_id: str
    project_name: str
    authority: str
    contract_value_crores: float
    planned_duration_months: int
    actual_duration_months: int
    delay_months: int
    cost_overrun_pct: float
    post_completion_defect_score: float = Field(ge=0.0, le=10.0, description="0 is flawless, 10 is severe defects")


class Contractor(BaseModel):
    id: str
    name: str
    registration_number: str
    year_established: int
    total_projects_completed: int
    projects_completed_on_time: int
    average_delay_rate_pct: float
    average_delay_months: float = 0.0
    average_cost_overrun_pct: float
    blacklisted: bool = False
    blacklist_reason: Optional[str] = None
    historical_quality_rating: float = Field(ge=0.0, le=5.0)
    financial_stability_score: float = Field(ge=0.0, le=100.0)
    past_projects: List[PastProjectRecord] = Field(default_factory=list)
