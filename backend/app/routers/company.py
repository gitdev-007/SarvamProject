import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.database import get_db
from app.models import AuditEvent, CompanyProfile, EvidenceDocument
from app.schemas import CompanyProfileOut, CompanyProfileUpdate, EvidenceOut, PresignedUrlResponse
from app.services.storage_service import (
    delete_file_from_neon,
    generate_object_key,
    generate_presigned_download_url,
    is_storage_configured,
    upload_file_to_neon,
)

router = APIRouter(prefix="/api", tags=["Company Profile & Vault"])


@router.get("/company", response_model=CompanyProfileOut)
def get_company_profile(db: Session = Depends(get_db)):
    company = db.query(CompanyProfile).first()
    if not company:
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


@router.post("/company/evidence/upload", response_model=EvidenceOut)
async def upload_evidence_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    issuer: str | None = Form(None),
    issue_date: str | None = Form(None),
    expiry_date: str | None = Form(None),
    document_number: str | None = Form(None),
    claims_summary: str | None = Form(None),
    db: Session = Depends(get_db),
):
    content = await file.read()
    file_size = len(content)

    storage_key = None
    if is_storage_configured():
        storage_key = generate_object_key(tender_id=None, original_filename=file.filename)
        content_type = file.content_type or ("application/pdf" if file.filename.lower().endswith(".pdf") else "application/octet-stream")
        upload_file_to_neon(file_bytes=content, object_key=storage_key, content_type=content_type)
        file_path_value = storage_key
    else:
        dest_file = UPLOAD_DIR / f"vault_{file.filename}"
        with open(dest_file, "wb") as buffer:
            buffer.write(content)
        file_path_value = str(dest_file)

    ev = EvidenceDocument(
        title=title,
        category=category,
        issuer=issuer,
        issue_date=issue_date,
        expiry_date=expiry_date,
        document_number=document_number,
        file_path=file_path_value,
        verification_status="Verified" if not expiry_date else "Needs Review",
        claims_summary=claims_summary,
    )
    db.add(ev)

    audit = AuditEvent(
        action="EVIDENCE_UPLOAD",
        details=f"Uploaded evidence '{title}' ({file_size} bytes) to {'Neon Object Storage (' + storage_key + ')' if storage_key else 'Local Storage'}",
    )
    db.add(audit)

    db.commit()
    db.refresh(ev)
    return ev


@router.get("/company/evidence/{ev_id}/download", response_model=PresignedUrlResponse)
def get_evidence_download_url(ev_id: int, db: Session = Depends(get_db)):
    ev = db.query(EvidenceDocument).filter(EvidenceDocument.id == ev_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence document not found")

    if not ev.file_path:
        raise HTTPException(status_code=404, detail="No storage file uploaded for this evidence record")

    if is_storage_configured() and (ev.file_path.startswith("vault/") or ev.file_path.startswith("tenders/")):
        presigned_url = generate_presigned_download_url(ev.file_path, expiration_seconds=3600)
        return PresignedUrlResponse(
            download_url=presigned_url,
            filename=f"{ev.title}.pdf" if not ev.title.lower().endswith(".pdf") else ev.title,
            expires_in=3600,
            storage_key=ev.file_path,
        )

    if os.path.exists(ev.file_path):
        return PresignedUrlResponse(
            download_url=f"/api/company/evidence/{ev_id}/raw",
            filename=f"{ev.title}.pdf",
            expires_in=0,
            storage_key=ev.file_path,
        )

    raise HTTPException(status_code=404, detail="File object not found in storage")


@router.get("/company/evidence/{ev_id}/raw")
def download_evidence_raw(ev_id: int, db: Session = Depends(get_db)):
    ev = db.query(EvidenceDocument).filter(EvidenceDocument.id == ev_id).first()
    if not ev or not ev.file_path or not os.path.exists(ev.file_path):
        raise HTTPException(status_code=404, detail="Local file not found")
    return FileResponse(ev.file_path, filename=f"{ev.title}.pdf")


@router.delete("/company/evidence/{ev_id}")
def delete_evidence_document(ev_id: int, db: Session = Depends(get_db)):
    ev = db.query(EvidenceDocument).filter(EvidenceDocument.id == ev_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")

    if ev.file_path and (ev.file_path.startswith("vault/") or ev.file_path.startswith("tenders/")):
        delete_file_from_neon(ev.file_path)
    elif ev.file_path and os.path.exists(ev.file_path):
        try:
            os.remove(ev.file_path)
        except OSError:
            pass

    audit = AuditEvent(
        action="EVIDENCE_DELETE",
        details=f"Deleted evidence document '{ev.title}' (ID: {ev.id})",
    )
    db.add(audit)

    db.delete(ev)
    db.commit()
    return {"message": "Evidence deleted", "id": ev_id}
