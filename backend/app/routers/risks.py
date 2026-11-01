from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    CompanyProfile,
    ComplianceAssessment,
    EvidenceDocument,
    RiskFinding,
    TenderProject,
)
from app.schemas import RiskOut, RiskUpdate
from app.services.compliance_engine import run_deterministic_evaluations

router = APIRouter(prefix="/api", tags=["Risks & Readiness"])


@router.get("/tenders/{tender_id}/risks", response_model=list[RiskOut])
def get_tender_risks(tender_id: int, db: Session = Depends(get_db)):
    return db.query(RiskFinding).filter(RiskFinding.tender_id == tender_id).all()


@router.patch("/risks/{risk_id}", response_model=RiskOut)
def update_risk_status(
    risk_id: int, payload: RiskUpdate, db: Session = Depends(get_db)
):
    risk = db.query(RiskFinding).filter(RiskFinding.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk finding not found")
    risk.status = payload.status
    db.commit()
    db.refresh(risk)
    return risk


@router.get("/tenders/{tender_id}/readiness")
def get_readiness_assessment(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(TenderProject).filter(TenderProject.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    company = db.query(CompanyProfile).first()
    evidence_list = db.query(EvidenceDocument).all()
    compliance_items = (
        db.query(ComplianceAssessment)
        .filter(ComplianceAssessment.tender_id == tender_id)
        .all()
    )

    # Deterministic checks
    evaluations = run_deterministic_evaluations(company, evidence_list, tender)

    # Calculate status counts
    status_counts = {}
    for item in compliance_items:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1

    critical_count = (
        db.query(RiskFinding)
        .filter(
            RiskFinding.tender_id == tender_id,
            RiskFinding.severity == "Critical",
            RiskFinding.status == "Unresolved",
        )
        .count()
    )

    total_reqs = len(compliance_items)
    satisfied_count = status_counts.get("Potentially satisfied", 0) + status_counts.get(
        "Evidence found", 0
    )
    score = round((satisfied_count / total_reqs * 100), 1) if total_reqs > 0 else 0.0

    return {
        "tender_id": tender_id,
        "readiness_score": score,
        "score_label": "Internal Heuristic (Decision Support)",
        "has_critical_blocker": critical_count > 0,
        "critical_blockers_count": critical_count,
        "status_breakdown": status_counts,
        "deterministic_evaluations": evaluations,
    }
