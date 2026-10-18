"""
Contractors API Router.
Provides contractor track record metrics, past delays, and blacklisting status.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from models.contractor import Contractor
from data.mock_database import db

router = APIRouter(prefix="/api/contractors", tags=["Contractors"])


@router.get("", response_model=List[Contractor])
def list_contractors():
    return list(db.contractors.values())


@router.get("/{contractor_id}", response_model=Contractor)
def get_contractor(contractor_id: str):
    contractor = db.contractors.get(contractor_id)
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    return contractor
