import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_turnover_average(turnover_dict: dict) -> float:
    """Calculates the mathematical average of annual turnover figures (in Lakhs INR)."""
    if not turnover_dict:
        return 0.0
    try:
        values = [float(v) for v in turnover_dict.values()]
        return round(sum(values) / len(values), 2)
    except Exception as e:
        logger.error(f"Error calculating turnover average: {e}")
        return 0.0


def check_date_expired(
    expiry_str: str | None, reference_date_str: str | None = None
) -> bool:
    """Checks whether an evidence document's expiry date has passed relative to today or the tender deadline."""
    if not expiry_str:
        return False
    try:
        # Standard formats: YYYY-MM-DD or DD-MM-YYYY
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                exp_date = datetime.strptime(expiry_str.strip(), fmt)
                ref_date = datetime.utcnow()
                if reference_date_str:
                    try:
                        ref_date = datetime.strptime(reference_date_str.strip(), fmt)
                    except ValueError:
                        pass
                return exp_date < ref_date
            except ValueError:
                continue
    except Exception as e:
        logger.warning(f"Date parse error for {expiry_str}: {e}")
    return False


def run_deterministic_evaluations(company_profile, evidence_list, tender) -> list[dict]:
    """
    Evaluates company evidence deterministically according to Section 15 of PRD:
    - Turnover threshold comparison.
    - Completed project count comparison.
    - Certificate expiry checks.
    """
    results = []
    turnover_data = {}
    if company_profile and company_profile.turnover_json:
        try:
            turnover_data = json.loads(company_profile.turnover_json)
        except Exception:
            turnover_data = {}

    past_projects = []
    if company_profile and company_profile.past_projects_json:
        try:
            past_projects = json.loads(company_profile.past_projects_json)
        except Exception:
            past_projects = []

    # Financial evaluation (e.g. ₹50 Lakh requirement)
    avg_turnover = calculate_turnover_average(turnover_data)
    results.append(
        {
            "category": "Financial",
            "avg_turnover_lakhs": avg_turnover,
            "is_sufficient": avg_turnover >= 50.0,
            "details": f"3-Year Average: ₹{avg_turnover} Lakhs (FY21-22: ₹{turnover_data.get('2021-22', 0)}L, FY22-23: ₹{turnover_data.get('2022-23', 0)}L, FY23-24: ₹{turnover_data.get('2023-24', 0)}L).",
        }
    )

    # Past experience evaluation (e.g. Minimum 3 similar completed projects)
    project_count = len(past_projects)
    results.append(
        {
            "category": "Experience",
            "project_count": project_count,
            "required_count": 3,
            "is_sufficient": project_count >= 3,
            "details": f"Found {project_count} completion certificates on record (Tender specifies minimum 3 projects).",
        }
    )

    # Certificate checks
    expired_docs = []
    for doc in evidence_list:
        if doc.expiry_date and check_date_expired(
            doc.expiry_date, tender.submission_deadline if tender else None
        ):
            expired_docs.append(doc.title)

    results.append(
        {
            "category": "Certificates",
            "expired_documents": expired_docs,
            "has_expired": len(expired_docs) > 0,
        }
    )

    return results
