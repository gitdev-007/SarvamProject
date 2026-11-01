import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class TenderProject(Base):
    __tablename__ = "tender_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    buyer = Column(String(255), nullable=False)
    tender_reference = Column(String(100), nullable=False)
    publication_date = Column(String(50), nullable=True)
    submission_deadline = Column(String(50), nullable=False)
    estimated_value = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship(
        "Document", back_populates="tender", cascade="all, delete-orphan"
    )
    requirements = relationship(
        "Requirement", back_populates="tender", cascade="all, delete-orphan"
    )
    compliance_items = relationship(
        "ComplianceAssessment", back_populates="tender", cascade="all, delete-orphan"
    )
    risks = relationship(
        "RiskFinding", back_populates="tender", cascade="all, delete-orphan"
    )
    proposals = relationship(
        "ProposalSection", back_populates="tender", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tender_projects.id"), nullable=True)
    document_type = Column(
        String(50), default="RFP"
    )  # RFP, BOQ, Corrigendum, Technical, Other
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, default=0)
    parsed_text = Column(Text, nullable=True)
    page_count = Column(Integer, default=1)
    processing_status = Column(
        String(50), default="completed"
    )  # pending, processing, completed, failed
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    tender = relationship("TenderProject", back_populates="documents")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tender_projects.id"), nullable=False)
    code = Column(String(50), nullable=False)  # e.g. REQ-FIN-01
    category = Column(
        String(100), nullable=False
    )  # Financial, Experience, Technical, Legal, Compliance
    requirement_text = Column(Text, nullable=False)
    normalized_summary = Column(Text, nullable=False)
    mandatory_level = Column(
        String(50), default="Mandatory"
    )  # Mandatory, Desirable, Ambiguous
    source_document = Column(String(255), nullable=False)
    source_page = Column(String(50), nullable=False)
    source_excerpt = Column(Text, nullable=True)
    condition_threshold = Column(String(255), nullable=True)
    review_status = Column(String(50), default="Pending Review")

    tender = relationship("TenderProject", back_populates="requirements")
    compliance_item = relationship(
        "ComplianceAssessment",
        back_populates="requirement",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(Integer, primary_key=True, index=True)
    legal_name = Column(String(255), nullable=False)
    business_type = Column(
        String(100), nullable=False
    )  # Private Limited, Partnership, MSME
    msme_status = Column(String(50), default="Micro")  # Micro, Small, Medium, Large
    udyam_number = Column(String(100), nullable=True)
    gstin = Column(String(50), nullable=True)
    pan = Column(String(50), nullable=True)
    registered_address = Column(Text, nullable=True)
    turnover_json = Column(
        Text, nullable=True
    )  # JSON string of FY turnovers e.g. {"2023-24": 62, "2022-23": 55, "2021-22": 41}
    technical_capabilities = Column(Text, nullable=True)
    past_projects_json = Column(Text, nullable=True)  # JSON string of past work orders
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class EvidenceDocument(Base):
    __tablename__ = "evidence_vault"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(
        String(100), nullable=False
    )  # Financial, Past Experience, Certificate, Registration, Undertaking
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    document_number = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=True)
    verification_status = Column(
        String(50), default="Verified"
    )  # Verified, Expired, Needs Review
    claims_summary = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)


class ComplianceAssessment(Base):
    __tablename__ = "compliance_assessments"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tender_projects.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    status = Column(
        String(50), default="Needs Review"
    )  # Evidence found, Potentially satisfied, Missing evidence, Expired evidence, Potentially not satisfied
    company_response = Column(Text, nullable=True)
    supporting_evidence = Column(Text, nullable=True)
    source_page = Column(String(50), nullable=True)
    deterministic_notes = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, default=False)

    tender = relationship("TenderProject", back_populates="compliance_items")
    requirement = relationship("Requirement", back_populates="compliance_item")


class RiskFinding(Base):
    __tablename__ = "risk_findings"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tender_projects.id"), nullable=False)
    requirement_code = Column(String(50), nullable=True)
    severity = Column(
        String(50), nullable=False
    )  # Critical, High, Medium, Low, Informational
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True)
    recommended_action = Column(Text, nullable=False)
    status = Column(String(50), default="Unresolved")  # Unresolved, Mitigated, Accepted

    tender = relationship("TenderProject", back_populates="risks")


class ProposalSection(Base):
    __tablename__ = "proposal_sections"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tender_projects.id"), nullable=False)
    section_title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    evidence_references_json = Column(Text, nullable=True)
    has_unsupported_claims = Column(Boolean, default=False)
    status = Column(String(50), default="Draft")  # Draft, Reviewed, Approved
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    tender = relationship("TenderProject", back_populates="proposals")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
