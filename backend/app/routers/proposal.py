from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CompanyProfile, ProposalSection, Requirement, TenderProject
from app.schemas import ProposalGenerateRequest, ProposalOut, ProposalUpdate
from app.services.sarvam_service import generate_proposal_draft

router = APIRouter(prefix="/api", tags=["Proposal Studio"])


@router.get("/tenders/{tender_id}/proposals", response_model=list[ProposalOut])
def get_proposals(tender_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ProposalSection).filter(ProposalSection.tender_id == tender_id).all()
    )


@router.post("/tenders/{tender_id}/proposals/generate", response_model=ProposalOut)
def generate_proposal_section(
    tender_id: int,
    payload: ProposalGenerateRequest,
    db: Session = Depends(get_db),
):
    tender = db.query(TenderProject).filter(TenderProject.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    company = db.query(CompanyProfile).first()
    company_facts = (
        f"Legal Name: {company.legal_name if company else 'Apex Renewable Energy'}\n"
    )
    if company and company.turnover_json:
        company_facts += f"Turnover: {company.turnover_json}\n"
    if company and company.past_projects_json:
        company_facts += f"Past Projects: {company.past_projects_json}\n"

    reqs = db.query(Requirement).filter(Requirement.tender_id == tender_id).all()
    reqs_text = "\n".join(
        [f"- [{r.code}] {r.normalized_summary} ({r.mandatory_level})" for r in reqs]
    )

    draft_content = generate_proposal_draft(
        payload.section_title, reqs_text, company_facts
    )
    has_unsupported = "[USER INPUT REQUIRED" in draft_content

    proposal = ProposalSection(
        tender_id=tender_id,
        section_title=payload.section_title,
        content=draft_content,
        evidence_references_json="[]",
        has_unsupported_claims=has_unsupported,
        status="Draft",
        version=1,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.patch("/proposals/{prop_id}", response_model=ProposalOut)
def update_proposal_section(
    prop_id: int, payload: ProposalUpdate, db: Session = Depends(get_db)
):
    prop = db.query(ProposalSection).filter(ProposalSection.id == prop_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal section not found")
    if payload.content is not None:
        prop.content = payload.content
        prop.has_unsupported_claims = "[USER INPUT REQUIRED" in payload.content
    if payload.status is not None:
        prop.status = payload.status
    db.commit()
    db.refresh(prop)
    return prop
