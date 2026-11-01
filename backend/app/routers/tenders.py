from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ComplianceAssessment, RiskFinding, TenderProject
from app.schemas import DashboardStats, TenderCreate, TenderOut
from app.services.sarvam_service import is_sarvam_configured

router = APIRouter(prefix="/api", tags=["Tenders"])


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    active_count = (
        db.query(TenderProject).filter(TenderProject.status == "active").count()
    )

    # Missing evidence count
    missing_ev = (
        db.query(ComplianceAssessment)
        .filter(
            ComplianceAssessment.status.in_(
                ["Missing evidence", "Expired evidence", "Potentially not satisfied"]
            )
        )
        .count()
    )

    # Critical risks
    critical_risks = (
        db.query(RiskFinding)
        .filter(
            RiskFinding.severity.in_(["Critical", "High"]),
            RiskFinding.status == "Unresolved",
        )
        .count()
    )

    total_reqs = db.query(ComplianceAssessment).count()
    satisfied_reqs = (
        db.query(ComplianceAssessment)
        .filter(
            ComplianceAssessment.status.in_(["Potentially satisfied", "Evidence found"])
        )
        .count()
    )

    compliance_rate = (
        round((satisfied_reqs / total_reqs * 100), 1) if total_reqs > 0 else 0.0
    )

    return DashboardStats(
        active_tenders=active_count,
        upcoming_deadlines=active_count,
        missing_evidence_count=missing_ev,
        critical_risks_count=critical_risks,
        compliance_rate=compliance_rate,
        sarvam_configured=is_sarvam_configured(),
    )


@router.get("/tenders", response_model=list[TenderOut])
def list_tenders(db: Session = Depends(get_db)):
    return db.query(TenderProject).order_by(TenderProject.id.desc()).all()


@router.post("/tenders", response_model=TenderOut)
def create_tender(payload: TenderCreate, db: Session = Depends(get_db)):
    tender = TenderProject(
        title=payload.title,
        buyer=payload.buyer,
        tender_reference=payload.tender_reference,
        publication_date=payload.publication_date,
        submission_deadline=payload.submission_deadline,
        estimated_value=payload.estimated_value,
        category=payload.category,
        status="active",
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender


@router.get("/tenders/{tender_id}", response_model=TenderOut)
def get_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(TenderProject).filter(TenderProject.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.delete("/tenders/{tender_id}")
def delete_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(TenderProject).filter(TenderProject.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    db.delete(tender)
    db.commit()
    return {"message": "Tender deleted successfully"}
