import shutil

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.database import get_db
from app.models import Document, TenderProject
from app.schemas import DocumentOut

router = APIRouter(prefix="/api", tags=["Documents"])


@router.get("/tenders/{tender_id}/documents", response_model=list[DocumentOut])
def get_tender_documents(tender_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.tender_id == tender_id).all()


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

    dest_file = UPLOAD_DIR / f"{tender_id}_{file.filename}"
    with open(dest_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    page_count = 1
    extracted_text = ""
    # Try parsing PDF if applicable
    if file.filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(str(dest_file))
            page_count = len(reader.pages)
            for i in range(min(5, page_count)):
                extracted_text += (
                    f"--- Page {i + 1} ---\n"
                    + (reader.pages[i].extract_text() or "")
                    + "\n"
                )
        except Exception:
            extracted_text = "Standard PDF Document Uploaded."
    else:
        extracted_text = f"Uploaded document {file.filename}."

    doc = Document(
        tender_id=tender_id,
        document_type=document_type,
        original_filename=file.filename,
        file_path=str(dest_file),
        file_size=dest_file.stat().st_size,
        page_count=page_count,
        parsed_text=extracted_text[:10000],  # store first chunk safely
        processing_status="completed",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
