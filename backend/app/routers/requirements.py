from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ComplianceAssessment, Requirement
from app.schemas import (
    ComplianceOut,
    ComplianceUpdate,
    RequirementOut,
    RequirementUpdate,
)

router = APIRouter(prefix="/api", tags=["Requirements & Compliance"])


@router.get("/tenders/{tender_id}/requirements", response_model=list[RequirementOut])
def get_requirements(tender_id: int, db: Session = Depends(get_db)):
    return db.query(Requirement).filter(Requirement.tender_id == tender_id).all()


@router.patch("/requirements/{req_id}", response_model=RequirementOut)
def update_requirement(
    req_id: int, payload: RequirementUpdate, db: Session = Depends(get_db)
):
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    if payload.normalized_summary is not None:
        req.normalized_summary = payload.normalized_summary
    if payload.mandatory_level is not None:
        req.mandatory_level = payload.mandatory_level
    if payload.review_status is not None:
        req.review_status = payload.review_status
    db.commit()
    db.refresh(req)
    return req


@router.get("/tenders/{tender_id}/compliance", response_model=list[ComplianceOut])
def get_compliance_matrix(tender_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ComplianceAssessment)
        .filter(ComplianceAssessment.tender_id == tender_id)
        .all()
    )


@router.patch("/compliance/{comp_id}", response_model=ComplianceOut)
def update_compliance_assessment(
    comp_id: int, payload: ComplianceUpdate, db: Session = Depends(get_db)
):
    comp = (
        db.query(ComplianceAssessment)
        .filter(ComplianceAssessment.id == comp_id)
        .first()
    )
    if not comp:
        raise HTTPException(status_code=404, detail="Compliance item not found")
    if payload.status is not None:
        comp.status = payload.status
    if payload.reviewer_notes is not None:
        comp.reviewer_notes = payload.reviewer_notes
    if payload.is_reviewed is not None:
        comp.is_reviewed = payload.is_reviewed
    db.commit()
    db.refresh(comp)
    return comp
