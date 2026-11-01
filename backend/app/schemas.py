from pydantic import BaseModel


class TenderCreate(BaseModel):
    title: str
    buyer: str
    tender_reference: str
    publication_date: str | None = None
    submission_deadline: str
    estimated_value: str | None = None
    category: str | None = None


class TenderOut(BaseModel):
    id: int
    title: str
    buyer: str
    tender_reference: str
    publication_date: str | None = None
    submission_deadline: str
    estimated_value: str | None = None
    category: str | None = None
    status: str

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: int
    tender_id: int | None
    document_type: str
    original_filename: str
    file_path: str | None = None
    file_size: int
    page_count: int
    processing_status: str

    class Config:
        from_attributes = True


class RequirementOut(BaseModel):
    id: int
    tender_id: int
    code: str
    category: str
    requirement_text: str
    normalized_summary: str
    mandatory_level: str
    source_document: str
    source_page: str
    source_excerpt: str | None = None
    condition_threshold: str | None = None
    review_status: str

    class Config:
        from_attributes = True


class RequirementUpdate(BaseModel):
    normalized_summary: str | None = None
    mandatory_level: str | None = None
    review_status: str | None = None


class ComplianceOut(BaseModel):
    id: int
    tender_id: int
    requirement_id: int
    status: str
    company_response: str | None = None
    supporting_evidence: str | None = None
    source_page: str | None = None
    deterministic_notes: str | None = None
    reviewer_notes: str | None = None
    is_reviewed: bool
    requirement: RequirementOut | None = None

    class Config:
        from_attributes = True


class ComplianceUpdate(BaseModel):
    status: str | None = None
    reviewer_notes: str | None = None
    is_reviewed: bool | None = None


class RiskOut(BaseModel):
    id: int
    tender_id: int
    requirement_code: str | None = None
    severity: str
    title: str
    explanation: str
    why_it_matters: str | None = None
    source_reference: str | None = None
    recommended_action: str
    status: str

    class Config:
        from_attributes = True


class RiskUpdate(BaseModel):
    status: str


class ProposalOut(BaseModel):
    id: int
    tender_id: int
    section_title: str
    content: str
    evidence_references_json: str | None = None
    has_unsupported_claims: bool
    status: str
    version: int

    class Config:
        from_attributes = True


class ProposalUpdate(BaseModel):
    content: str | None = None
    status: str | None = None


class ProposalGenerateRequest(BaseModel):
    section_title: str
    requirement_ids: list[int] | None = None


class CompanyProfileOut(BaseModel):
    id: int
    legal_name: str
    business_type: str
    msme_status: str
    udyam_number: str | None = None
    gstin: str | None = None
    pan: str | None = None
    registered_address: str | None = None
    turnover_json: str | None = None
    technical_capabilities: str | None = None
    past_projects_json: str | None = None

    class Config:
        from_attributes = True


class CompanyProfileUpdate(BaseModel):
    legal_name: str | None = None
    business_type: str | None = None
    msme_status: str | None = None
    udyam_number: str | None = None
    gstin: str | None = None
    pan: str | None = None
    registered_address: str | None = None
    turnover_json: str | None = None
    technical_capabilities: str | None = None
    past_projects_json: str | None = None


class EvidenceOut(BaseModel):
    id: int
    title: str
    category: str
    issuer: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    document_number: str | None = None
    file_path: str | None = None
    verification_status: str
    claims_summary: str | None = None

    class Config:
        from_attributes = True


class PresignedUrlResponse(BaseModel):
    download_url: str
    filename: str
    expires_in: int
    storage_key: str | None = None


class VoiceQueryRequest(BaseModel):
    tender_id: int
    question: str
    language: str | None = "en-IN"


class VoiceQueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[dict]
    model: str


class DashboardStats(BaseModel):
    active_tenders: int
    upcoming_deadlines: int
    missing_evidence_count: int
    critical_risks_count: int
    compliance_rate: float
    sarvam_configured: bool

