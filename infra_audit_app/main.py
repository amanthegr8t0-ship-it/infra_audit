"""
Main FastAPI Application Entrypoint for InfraAudit India.
Civic Infrastructure Procurement Transparency & Field Evidence Audit Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.tenders_router import router as tenders_router
from api.contractors_router import router as contractors_router
from api.evidence_router import router as evidence_router
from api.reviews_router import router as reviews_router

app = FastAPI(
    title="InfraAudit India - Civic Procurement & Ground Truth Platform",
    description=(
        "Public infrastructure procurement transparency system aggregating NHAI, MoRTH, "
        "and PWD tenders, contractor track records, AI reasoning-moderated citizen reviews, "
        "and EXIF/GPS-verified ground-truth field evidence."
    ),
    version="1.0.0"
)

# Enable CORS for browser integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(tenders_router)
app.include_router(contractors_router)
app.include_router(evidence_router)
app.include_router(reviews_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "InfraAudit India Core Engine",
        "governance_mode": "Objective Audit & Ground-Truth Verification"
    }


# Mount static directory if it exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
