from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CompanyProfile, EvidenceDocument
from app.schemas import CompanyProfileOut, CompanyProfileUpdate, EvidenceOut

router = APIRouter(prefix="/api", tags=["Company Profile & Vault"])


@router.get("/company", response_model=CompanyProfileOut)
def get_company_profile(db: Session = Depends(get_db)):
    company = db.query(CompanyProfile).first()
    if not company:
        # Default placeholder
        company = CompanyProfile(
            legal_name="My Company",
            business_type="Private Limited",
            msme_status="Micro",
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    return company


@router.put("/company", response_model=CompanyProfileOut)
def update_company_profile(
    payload: CompanyProfileUpdate, db: Session = Depends(get_db)
):
    company = db.query(CompanyProfile).first()
    if not company:
        company = CompanyProfile(
            legal_name=payload.legal_name or "My Company",
            business_type="Private Limited",
        )
        db.add(company)

    for field, val in payload.dict(exclude_unset=True).items():
        setattr(company, field, val)

    db.commit()
    db.refresh(company)
    return company


@router.get("/company/evidence", response_model=list[EvidenceOut])
def get_evidence_vault(db: Session = Depends(get_db)):
    return db.query(EvidenceDocument).order_by(EvidenceDocument.id.desc()).all()


@router.post("/company/evidence", response_model=EvidenceOut)
def add_evidence_document(
    title: str,
    category: str,
    issuer: str | None = None,
    issue_date: str | None = None,
    expiry_date: str | None = None,
    document_number: str | None = None,
    claims_summary: str | None = None,
    db: Session = Depends(get_db),
):
    ev = EvidenceDocument(
        title=title,
        category=category,
        issuer=issuer,
        issue_date=issue_date,
        expiry_date=expiry_date,
        document_number=document_number,
        verification_status="Verified" if not expiry_date else "Needs Review",
        claims_summary=claims_summary,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.delete("/company/evidence/{ev_id}")
def delete_evidence_document(ev_id: int, db: Session = Depends(get_db)):
    ev = db.query(EvidenceDocument).filter(EvidenceDocument.id == ev_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    db.delete(ev)
    db.commit()
    return {"message": "Evidence deleted"}
