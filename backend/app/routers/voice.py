from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import SARVAM_CHAT_MODEL
from app.database import get_db
from app.models import Requirement, TenderProject
from app.schemas import VoiceQueryRequest, VoiceQueryResponse
from app.services.sarvam_service import ask_sarvam_grounded

router = APIRouter(prefix="/api/voice", tags=["Voice & Language Assistant"])


@router.post("/ask", response_model=VoiceQueryResponse)
def ask_tender_question(payload: VoiceQueryRequest, db: Session = Depends(get_db)):
    tender = (
        db.query(TenderProject).filter(TenderProject.id == payload.tender_id).first()
    )
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    reqs = (
        db.query(Requirement).filter(Requirement.tender_id == payload.tender_id).all()
    )

    # Compile tender context
    context_lines = [
        f"Tender: {tender.title}",
        f"Buyer: {tender.buyer}",
        f"Reference: {tender.tender_reference}",
        f"Submission Deadline: {tender.submission_deadline}",
        "Clauses & Requirements:",
    ]
    citations = []
    for r in reqs:
        context_lines.append(
            f"- [{r.code}] (Document: {r.source_document}, {r.source_page}): {r.requirement_text}"
        )
        citations.append(
            {"code": r.code, "document": r.source_document, "page": r.source_page}
        )

    tender_context = "\n".join(context_lines)

    answer = ask_sarvam_grounded(payload.question, tender_context, citations)

    return VoiceQueryResponse(
        question=payload.question,
        answer=answer,
        citations=citations,
        model=SARVAM_CHAT_MODEL,
    )
