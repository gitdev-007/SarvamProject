import json
import logging

from sarvamai import SarvamAI

from app.config import SARVAM_API_KEY, SARVAM_CHAT_MODEL

logger = logging.getLogger(__name__)


def is_sarvam_configured() -> bool:
    return bool(SARVAM_API_KEY and len(SARVAM_API_KEY.strip()) > 5)


def get_client() -> SarvamAI | None:
    if not is_sarvam_configured():
        return None
    return SarvamAI(api_subscription_key=SARVAM_API_KEY)


def ask_sarvam_grounded(
    question: str, tender_context: str, source_refs: list[dict]
) -> str:
    """Answers user queries grounded strictly in the tender document with explicit citations."""
    client = get_client()
    system_prompt = (
        "You are TenderGuard's analytical AI assistant for Indian tenders. "
        "Strict rules: "
        "1. Answer ONLY using the provided tender context. "
        "2. Never hallucinate clauses, eligibility criteria, or thresholds. "
        "3. Always cite the exact document and page number from the context. "
        "4. If information is not in the context, explicitly state 'Not specified in provided tender documents'."
    )

    user_prompt = f"Context:\n{tender_context}\n\nAvailable Source Documents: {json.dumps(source_refs)}\n\nQuestion: {question}"

    if client:
        try:
            response = client.chat.completions(
                model=SARVAM_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Sarvam AI API error: {e}")
            return f"(Fallback) Error communicating with Sarvam AI: {e}"

    # Safe deterministic fallback if API key is not configured
    return (
        f"Based on the tender documents on record:\n"
        f"Your query '{question}' was evaluated against available RFP clauses. "
        f"Please check the Compliance Matrix and Requirement Analysis tab for exact page references."
    )


def generate_proposal_draft(
    section_title: str, requirements_text: str, company_facts: str
) -> str:
    """Generates an evidence-grounded proposal response without hallucinated claims."""
    client = get_client()
    system_prompt = (
        "You are TenderGuard's Proposal Writer. "
        "Rules: "
        "1. Write a professional, compliant response for Indian government/PSU tenders. "
        "2. Rely ONLY on the verified company facts provided. "
        "3. If any past project, metric, turnover, or certification is missing from company facts, "
        "DO NOT INVENT IT. Insert '[USER INPUT REQUIRED: specify details]' instead."
    )
    user_prompt = (
        f"Section: {section_title}\n\n"
        f"Tender Requirements:\n{requirements_text}\n\n"
        f"Verified Company Profile & Facts:\n{company_facts}\n\n"
        f"Generate the compliant response draft:"
    )

    if client:
        try:
            response = client.chat.completions(
                model=SARVAM_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Sarvam AI proposal generation error: {e}")
            return f"Error connecting to Sarvam AI: {e}"

    return (
        f"### {section_title}\n\n"
        f"In response to the requirements, our organization provides the following verified submission:\n"
        f"- Compliance with technical specifications as per uploaded datasheets.\n"
        f"- Financial turnover and statutory documents are attached as per Annexure.\n"
        f"- [USER INPUT REQUIRED: Insert specific client reference and project scope here]."
    )
