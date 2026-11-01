import io
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.database import get_db
from app.models import AuditEvent, Document, TenderProject
from app.schemas import DocumentOut, PresignedUrlResponse
from app.services.storage_service import (
    delete_file_from_neon,
    generate_object_key,
    generate_presigned_download_url,
    is_storage_configured,
    upload_file_to_neon,
)

router = APIRouter(prefix="/api", tags=["Documents"])


@router.get("/tenders/{tender_id}/documents", response_model=list[DocumentOut])
def get_tender_documents(tender_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.tender_id == tender_id).order_by(Document.id.desc()).all()


@router.post("/tenders/{tender_id}/documents", response_model=DocumentOut)
async def upload_document(
    tender_id: int,
    file: UploadFile = File(...),
    document_type: str = Form("RFP"),
    db: Session = Depends(get_db),
):
    tender = db.query(TenderProject).filter(TenderProject.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    content = await file.read()
    file_size = len(content)

    page_count = 1
    extracted_text = ""
    # Parse text from memory
    if file.filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))
            page_count = len(reader.pages)
            for i in range(min(5, page_count)):
                page_text = reader.pages[i].extract_text() or ""
                extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"
        except Exception:
            extracted_text = "PDF Document Uploaded."
    else:
        try:
            extracted_text = content.decode("utf-8", errors="ignore")[:5000]
        except Exception:
            extracted_text = f"Uploaded document {file.filename}."

    # Upload to Neon Object Storage if configured, else local fallback
    storage_key = None
    if is_storage_configured():
        storage_key = generate_object_key(tender_id=tender_id, original_filename=file.filename)
        content_type = file.content_type or ("application/pdf" if file.filename.lower().endswith(".pdf") else "application/octet-stream")
        upload_file_to_neon(file_bytes=content, object_key=storage_key, content_type=content_type)
        file_path_value = storage_key
    else:
        dest_file = UPLOAD_DIR / f"{tender_id}_{file.filename}"
        with open(dest_file, "wb") as buffer:
            buffer.write(content)
        file_path_value = str(dest_file)

    doc = Document(
        tender_id=tender_id,
        document_type=document_type,
        original_filename=file.filename,
        file_path=file_path_value,
        file_size=file_size,
        page_count=page_count,
        parsed_text=extracted_text[:10000],
        processing_status="completed",
    )
    db.add(doc)

    audit = AuditEvent(
        action="DOCUMENT_UPLOAD",
        details=f"Uploaded document '{file.filename}' ({file_size} bytes) to {'Neon Object Storage (' + storage_key + ')' if storage_key else 'Local Storage'}",
    )
    db.add(audit)

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents/{doc_id}/download", response_model=PresignedUrlResponse)
def get_document_download_url(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.file_path:
        raise HTTPException(status_code=404, detail="No storage path recorded for this document")

    # If stored in Neon Object Storage
    if is_storage_configured() and (doc.file_path.startswith("tenders/") or doc.file_path.startswith("vault/")):
        presigned_url = generate_presigned_download_url(doc.file_path, expiration_seconds=3600)
        return PresignedUrlResponse(
            download_url=presigned_url,
            filename=doc.original_filename,
            expires_in=3600,
            storage_key=doc.file_path,
        )

    # Local fallback
    if os.path.exists(doc.file_path):
        return PresignedUrlResponse(
            download_url=f"/api/documents/{doc_id}/raw",
            filename=doc.original_filename,
            expires_in=0,
            storage_key=doc.file_path,
        )

    raise HTTPException(status_code=404, detail="File object not found in storage")


@router.get("/documents/{doc_id}/raw")
def download_document_raw(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Local file not found")
    return FileResponse(doc.file_path, filename=doc.original_filename)


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from Neon Object Storage
    if doc.file_path and (doc.file_path.startswith("tenders/") or doc.file_path.startswith("vault/")):
        delete_file_from_neon(doc.file_path)
    elif doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    audit = AuditEvent(
        action="DOCUMENT_DELETE",
        details=f"Deleted document '{doc.original_filename}' (ID: {doc.id})",
    )
    db.add(audit)

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "id": doc_id}
