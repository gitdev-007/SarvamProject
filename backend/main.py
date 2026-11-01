import os
from contextlib import asynccontextmanager

from app.database import Base, SessionLocal, engine
from app.routers import (
    company,
    documents,
    proposal,
    requirements,
    risks,
    tenders,
    voice,
)
from app.seed_data import seed_database
from app.services.sarvam_service import is_sarvam_configured
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def initialize_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


# Ensure tables and seed exist on import
initialize_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    yield


app = FastAPI(
    title="TenderGuard API",
    description="AI-powered tender intelligence, compliance, and bid-readiness platform powered by Sarvam AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware for Vercel and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(tenders.router)
app.include_router(documents.router)
app.include_router(requirements.router)
app.include_router(company.router)
app.include_router(risks.router)
app.include_router(proposal.router)
app.include_router(voice.router)


@app.get("/")
def read_root():
    return {
        "product": "TenderGuard",
        "tagline": "Understand the tender. Verify your evidence. Find the gaps before submission.",
        "status": "online",
        "sarvam_configured": is_sarvam_configured(),
        "docs_url": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "sarvam_configured": is_sarvam_configured(),
        "database": "sqlite/tenderguard.db (active)",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
