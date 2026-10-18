from .tenders_router import router as tenders_router
from .contractors_router import router as contractors_router
from .evidence_router import router as evidence_router
from .reviews_router import router as reviews_router

__all__ = [
    "tenders_router",
    "contractors_router",
    "evidence_router",
    "reviews_router",
]
