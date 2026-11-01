import json

from sqlalchemy.orm import Session

from app.models import (
    AuditEvent,
    CompanyProfile,
    ComplianceAssessment,
    Document,
    EvidenceDocument,
    ProposalSection,
    Requirement,
    RiskFinding,
    TenderProject,
)


def seed_database(db: Session):
    """Initializes the golden demonstration scenario as required by PRD Section 15."""
    # Check if data already exists
    if db.query(TenderProject).first():
        return

    # 1. Company Profile
    turnover = {"2021-22": 41.0, "2022-23": 55.0, "2023-24": 62.0}
    past_projects = [
        {
            "client": "Maharashtra State Power Gen Co (MAHAGENCO)",
            "title": "1.5 MW Rooftop Solar Array Installation at Nagpur Depot",
            "completion_year": "2023",
            "value_inr": "₹1.85 Cr",
            "certificate_ref": "CC-MAHA-2023-098",
        },
        {
            "client": "Pune Municipal Corporation",
            "title": "800 kW Grid-Connected Solar Plant Installation",
            "completion_year": "2022",
            "value_inr": "₹92 Lakhs",
            "certificate_ref": "PMC-ENG-2022-441",
        },
    ]

    company = CompanyProfile(
        legal_name="Apex Renewable Energy Technologies Pvt Ltd (Demo MSME)",
        business_type="Private Limited Company",
        msme_status="Micro Enterprise (Class A)",
        udyam_number="UDYAM-MH-02-0089211",
        gstin="27AAACA9981B1ZG",
        pan="AAACA9981B",
        registered_address="Plot 14, MIDC Bhosari Industrial Area, Pune, Maharashtra 411026",
        turnover_json=json.dumps(turnover),
        technical_capabilities="Design, EPC, and O&M of Grid-Tied Solar Photovoltaic Systems, Inverters, and SCADA monitoring.",
        past_projects_json=json.dumps(past_projects),
    )
    db.add(company)
    db.commit()

    # 2. Company Evidence Vault Documents
    evidence_items = [
        EvidenceDocument(
            title="CA Certified 3-Year Audited Balance Sheet & P&L",
            category="Financial",
            issuer="K. S. Joshi & Associates, Chartered Accountants",
            issue_date="2024-07-15",
            expiry_date=None,
            document_number="UDIN-24098231BGFT198",
            verification_status="Verified",
            claims_summary="Turnover: FY 2023-24 = ₹62L, FY 2022-23 = ₹55L, FY 2021-22 = ₹41L. 3-Year Average = ₹52.67 Lakhs.",
        ),
        EvidenceDocument(
            title="Project Completion Certificate 1: MAHAGENCO 1.5 MW",
            category="Past Experience",
            issuer="Maharashtra State Power Generation Co. Ltd.",
            issue_date="2023-11-20",
            expiry_date=None,
            document_number="CC-MAHA-2023-098",
            verification_status="Verified",
            claims_summary="Satisfactorily executed and commissioned 1.5 MW solar PV installation within project schedule.",
        ),
        EvidenceDocument(
            title="Project Completion Certificate 2: PMC 800 kW Solar",
            category="Past Experience",
            issuer="Pune Municipal Corporation Engineering Dept",
            issue_date="2022-09-10",
            expiry_date=None,
            document_number="PMC-ENG-2022-441",
            verification_status="Verified",
            claims_summary="Commissioned 800 kW solar array with 3-year performance ratio guarantee.",
        ),
        EvidenceDocument(
            title="ISO 9001:2015 Quality Management System Certificate",
            category="Certificate",
            issuer="TUV Nord Quality Assurance India",
            issue_date="2021-03-01",
            expiry_date="2024-02-28",  # EXPIRED as per PRD scenario!
            document_number="TUV-IN-9001-88412",
            verification_status="Expired",
            claims_summary="Quality management system certification for solar EPC operations. (EXPIRED: Requires renewal recertification).",
        ),
        EvidenceDocument(
            title="Udyam MSME Registration Certificate",
            category="Registration",
            issuer="Ministry of Micro, Small and Medium Enterprises",
            issue_date="2020-08-14",
            expiry_date=None,
            document_number="UDYAM-MH-02-0089211",
            verification_status="Verified",
            claims_summary="Registered as Micro Enterprise under NIC Code 35105 (Electric power generation using solar energy).",
        ),
    ]
    for ev in evidence_items:
        db.add(ev)
    db.commit()

    # 3. Tender Project
    tender = TenderProject(
        title="Design, Supply, Installation & 5-Year Comprehensive O&M of 3.0 MW Rooftop Grid-Connected Solar PV Systems",
        buyer="Solar Energy Corporation of India (SECI) / MNRE",
        tender_reference="SECI/MNRE/2026/SOLAR-PV-ROOFTOP/04",
        publication_date="2026-10-15",
        submission_deadline="2026-12-10",
        estimated_value="₹4.20 Crores",
        category="Renewable Energy EPC",
        status="active",
    )
    db.add(tender)
    db.commit()

    # 4. Tender Documents
    docs = [
        Document(
            tender_id=tender.id,
            document_type="RFP",
            original_filename="SECI_RFP_Solar_Rooftop_Volume_I.pdf",
            file_size=4289000,
            page_count=64,
            parsed_text="Volume I: Commercial Eligibility, Turnover Conditions, EMD, and General Conditions of Contract.",
            processing_status="completed",
        ),
        Document(
            tender_id=tender.id,
            document_type="Technical Specification",
            original_filename="SECI_Technical_Specs_Volume_II.pdf",
            file_size=2890000,
            page_count=42,
            parsed_text="Volume II: Technical Specifications of Solar PV Modules (Mono PERC / Bifacial), Inverters, Net Metering.",
            processing_status="completed",
        ),
        Document(
            tender_id=tender.id,
            document_type="Corrigendum",
            original_filename="SECI_Corrigendum_No_1.pdf",
            file_size=820000,
            page_count=4,
            parsed_text="Corrigendum No. 1: Extension of bid submission deadline from 20 Nov 2026 to 10 Dec 2026.",
            processing_status="completed",
        ),
    ]
    for d in docs:
        db.add(d)
    db.commit()

    # 5. Requirements
    requirements_data = [
        {
            "code": "REQ-FIN-01",
            "category": "Financial Eligibility",
            "text": "The bidder must have achieved a minimum Annual Average Turnover (AATO) of ₹50 Lakhs (Rupees Fifty Lakhs) across the last three audited financial years (FY 2021-22, 2022-23, and 2023-24).",
            "summary": "Minimum 3-Year Average Annual Turnover of ₹50.00 Lakhs.",
            "mandatory": "Mandatory",
            "doc": "SECI_RFP_Solar_Rooftop_Volume_I.pdf",
            "page": "Page 14, Clause 4.2.1",
            "excerpt": "AATO for the last 3 financial years ending 31st March 2024 shall not be less than INR 50,00,000/-. Chartered Accountant certificate with valid UDIN is compulsory.",
            "condition": "Average Turnover >= ₹50,00,000",
            "status": "Potentially satisfied",
            "comp_resp": "Our CA audited turnover is: FY21-22: ₹41L, FY22-23: ₹55L, FY23-24: ₹62L. The 3-year mathematical average is ₹52.67 Lakhs, which exceeds the mandatory ₹50.00 Lakhs threshold.",
            "evidence": "CA Certified Balance Sheet with UDIN (UDIN-24098231BGFT198)",
            "det_notes": "Calculation: (41 + 55 + 62) / 3 = 52.67 Lakhs. Result: Passed (+₹2.67 Lakhs above threshold).",
        },
        {
            "code": "REQ-EXP-02",
            "category": "Past Experience",
            "text": "The bidder must have successfully executed and commissioned at least THREE (3) similar rooftop or ground-mount grid-tied solar projects of minimum 500 kW capacity each in the last five financial years.",
            "summary": "Completion of at least 3 similar solar projects (min 500 kW each).",
            "mandatory": "Mandatory",
            "doc": "SECI_RFP_Solar_Rooftop_Volume_I.pdf",
            "page": "Page 15, Clause 4.3.2",
            "excerpt": "Bidder must submit copy of work orders and client-issued project completion certificates confirming commissioning of 3 similar works.",
            "condition": "Project Count >= 3",
            "status": "Potentially not satisfied",
            "comp_resp": "We have submitted 2 project completion certificates (1.5 MW at MAHAGENCO and 800 kW at PMC). Third project completion record is pending.",
            "evidence": "CC-MAHA-2023-098 and PMC-ENG-2022-441 (Total 2 documents)",
            "det_notes": "Count Check: 2 uploaded vs 3 required. Deficit: 1 certificate missing.",
        },
        {
            "code": "REQ-QLT-03",
            "category": "Quality Certification",
            "text": "Bidder must hold an active ISO 9001:2015 Quality Management System Certification valid on the date of bid submission.",
            "summary": "Valid ISO 9001:2015 certificate on submission date.",
            "mandatory": "Mandatory",
            "doc": "SECI_RFP_Solar_Rooftop_Volume_I.pdf",
            "page": "Page 18, Clause 4.5.1",
            "excerpt": "ISO 9001:2015 valid certificate must be uploaded. Expired certificates or application receipts will not be entertained.",
            "condition": "ISO 9001 Expiry > 10 Dec 2026",
            "status": "Expired evidence",
            "comp_resp": "Uploaded certificate TUV-IN-9001-88412 shows expiry date of 28 February 2024. Recertification audit certificate needed.",
            "evidence": "TUV Nord ISO 9001:2015 Certificate (Expired)",
            "det_notes": "Validity Check: Expiry 2024-02-28 < Submission Deadline 2026-12-10. Status: Expired.",
        },
        {
            "code": "REQ-MSME-04",
            "category": "Statutory Registration",
            "text": "Bidders claiming EMD exemption and tender fee concession must submit a valid Udyam Registration Certificate under the relevant NIC classification.",
            "summary": "Valid Udyam Certificate for EMD and Fee Exemption.",
            "mandatory": "Mandatory (for Exemption)",
            "doc": "SECI_RFP_Solar_Rooftop_Volume_I.pdf",
            "page": "Page 7, Clause 2.4.3",
            "excerpt": "MSEs registered under Udyam are exempted from submission of EMD. Valid Udyam number must be provided.",
            "condition": "Valid Udyam Registered",
            "status": "Evidence found",
            "comp_resp": "Udyam Registration Certificate UDYAM-MH-02-0089211 uploaded. Classified as Micro Enterprise under NIC Code 35105.",
            "evidence": "Ministry of MSME Udyam Certificate",
            "det_notes": "Verified. Eligible for 100% EMD exemption.",
        },
        {
            "code": "REQ-DEC-05",
            "category": "Undertakings & Declarations",
            "text": "The bidder must submit an undertaking on company letterhead confirming that the firm has not been blacklisted or debarred by any Central/State Government Ministry, PSU, or SECI as on the date of submission.",
            "summary": "Non-Blacklisting Undertaking on Company Letterhead.",
            "mandatory": "Mandatory",
            "doc": "SECI_RFP_Solar_Rooftop_Volume_I.pdf",
            "page": "Page 48, Annexure-IV",
            "excerpt": "Self-declaration undertaking as per Form 4 format must be signed by authorized signatory with official stamp.",
            "condition": "Signed Annexure-IV attached",
            "status": "Missing evidence",
            "comp_resp": "Declaration document has not yet been prepared or uploaded to the vault.",
            "evidence": "None (Pending user upload)",
            "det_notes": "Document missing in submission package.",
        },
    ]

    for req_data in requirements_data:
        req = Requirement(
            tender_id=tender.id,
            code=req_data["code"],
            category=req_data["category"],
            requirement_text=req_data["text"],
            normalized_summary=req_data["summary"],
            mandatory_level=req_data["mandatory"],
            source_document=req_data["doc"],
            source_page=req_data["page"],
            source_excerpt=req_data["excerpt"],
            condition_threshold=req_data["condition"],
            review_status="Needs Review"
            if "not" in req_data["status"]
            or "Missing" in req_data["status"]
            or "Expired" in req_data["status"]
            else "Verified",
        )
        db.add(req)
        db.flush()

        comp = ComplianceAssessment(
            tender_id=tender.id,
            requirement_id=req.id,
            status=req_data["status"],
            company_response=req_data["comp_resp"],
            supporting_evidence=req_data["evidence"],
            source_page=req_data["page"],
            deterministic_notes=req_data["det_notes"],
            reviewer_notes="Automated deterministic check complete. Pending human approval."
            if "Review" in req.review_status
            else "Verified against audited certificates.",
            is_reviewed=False,
        )
        db.add(comp)
    db.commit()

    # 6. Risk Findings (PRD Section 9 & 15)
    risks_data = [
        {
            "code": "REQ-DEC-05",
            "severity": "Critical",
            "title": "Missing Mandatory Non-Blacklisting Declaration (Annexure-IV)",
            "explanation": "Tender clause 2.8 specifies that bids submitted without the non-blacklisting undertaking on company letterhead are summarily rejected during technical scrutiny.",
            "why": "Government portal procurement guidelines mandate self-declaration against debarment prior to opening technical envelopes.",
            "ref": "SECI_RFP_Solar_Rooftop_Volume_I.pdf, Page 48",
            "action": "Download Form-IV template, execute on company letterhead, sign and stamp with authorized signatory, and upload to Document Vault.",
        },
        {
            "code": "REQ-QLT-03",
            "severity": "High",
            "title": "Expired ISO 9001:2015 Quality Management Certificate",
            "explanation": "The uploaded ISO certificate (TUV-IN-9001-88412) expired on 28-Feb-2024. SECI RFP explicitly disallows expired certificates or renewal receipts.",
            "why": "Technical evaluation committee awards 0 marks or disqualifies bids with non-compliant QA certificates.",
            "ref": "SECI_RFP_Solar_Rooftop_Volume_I.pdf, Page 18",
            "action": "Obtain the renewed ISO 9001:2026 certificate from TUV Nord or upload valid renewal endorsement before bid submission deadline.",
        },
        {
            "code": "REQ-EXP-02",
            "severity": "High",
            "title": "Experience Deficit: Only 2 of 3 Required Completion Certificates Available",
            "explanation": "Tender mandates completion certificates for 3 similar solar projects (min 500 kW each). Currently, only 2 project certificates are uploaded in the company vault.",
            "why": "Missing the minimum qualifying quantity in past experience leads to technical rejection during envelope opening.",
            "ref": "SECI_RFP_Solar_Rooftop_Volume_I.pdf, Page 15",
            "action": "Upload third work completion certificate from client or consider formal Consortium/JV partner with qualifying credentials.",
        },
        {
            "code": "REQ-FIN-01",
            "severity": "Low",
            "title": "Turnover Margin is Close to Minimum Threshold (+5.3% Buffer)",
            "explanation": "Company's 3-year average turnover is ₹52.67 Lakhs against ₹50.00 Lakhs required. While legally compliant, the margin is narrow.",
            "why": "Any calculation discrepancy by tender evaluation auditors could challenge compliance.",
            "ref": "SECI_RFP_Solar_Rooftop_Volume_I.pdf, Page 14",
            "action": "Ensure the CA certificate includes explicit year-wise breakdown and verifiable UDIN registered on the ICAI portal.",
        },
    ]

    for r_data in risks_data:
        risk = RiskFinding(
            tender_id=tender.id,
            requirement_code=r_data["code"],
            severity=r_data["severity"],
            title=r_data["title"],
            explanation=r_data["explanation"],
            why_it_matters=r_data["why"],
            source_reference=r_data["ref"],
            recommended_action=r_data["action"],
            status="Unresolved",
        )
        db.add(risk)
    db.commit()

    # 7. Proposal Draft (PRD Section 10 & 15)
    proposals_data = [
        {
            "title": "Section 1: Executive Summary & MSME Capability Statement",
            "content": (
                "Apex Renewable Energy Technologies Pvt Ltd is pleased to submit this proposal for the 'Design, Supply, Installation & 5-Year Comprehensive O&M of 3.0 MW Rooftop Grid-Connected Solar PV Systems' (Ref: SECI/MNRE/2026/SOLAR-PV-ROOFTOP/04).\n\n"
                "As an authorized Micro Enterprise registered under Udyam (UDYAM-MH-02-0089211), we bring proven field expertise in turnkey industrial solar solutions across Maharashtra. Over the past three audited financial years, our firm has achieved a consistent Annual Average Turnover of ₹52.67 Lakhs (verified via UDIN: 24098231BGFT198), exceeding the financial threshold outlined in Clause 4.2.1.\n\n"
                "Our engineering team has delivered over 2.3 MW of commissioned grid-tied installations, including 1.5 MW for MAHAGENCO and 800 kW for Pune Municipal Corporation."
            ),
            "evidence": json.dumps(
                [
                    "UDYAM-MH-02-0089211",
                    "UDIN-24098231BGFT198",
                    "CC-MAHA-2023-098",
                    "PMC-ENG-2022-441",
                ]
            ),
            "unsupported": False,
            "status": "Reviewed",
        },
        {
            "title": "Section 2: Technical Compliance & Past Performance Matrix",
            "content": (
                "In compliance with Clause 4.3.2 (Past Experience):\n\n"
                "1. Project 1: 1.5 MW Rooftop Solar Array for MAHAGENCO at Nagpur Depot (Completion Certificate CC-MAHA-2023-098 attached).\n"
                "2. Project 2: 800 kW Grid-Connected Solar Installation for Pune Municipal Corporation (Completion Certificate PMC-ENG-2022-441 attached).\n"
                "3. Project 3: [USER INPUT REQUIRED: Please upload third project completion certificate of minimum 500 kW capacity to fulfill SECI mandatory requirement].\n\n"
                "Quality Assurance:\n"
                "- [USER INPUT REQUIRED: Upload renewed ISO 9001:2026 certification. Current certificate expired on 28-Feb-2024]."
            ),
            "evidence": json.dumps(["CC-MAHA-2023-098", "PMC-ENG-2022-441"]),
            "unsupported": True,  # Has [USER INPUT REQUIRED] as mandated by PRD Section 10!
            "status": "Draft",
        },
    ]

    for p_data in proposals_data:
        proposal = ProposalSection(
            tender_id=tender.id,
            section_title=p_data["title"],
            content=p_data["content"],
            evidence_references_json=p_data["evidence"],
            has_unsupported_claims=p_data["unsupported"],
            status=p_data["status"],
            version=1,
        )
        db.add(proposal)
    db.commit()

    # 8. Audit Log
    db.add(
        AuditEvent(
            action="INITIAL_SEED",
            details="Initialized Golden Evaluation scenario for SECI 3MW Rooftop Tender with deterministic checks.",
        )
    )
    db.commit()
