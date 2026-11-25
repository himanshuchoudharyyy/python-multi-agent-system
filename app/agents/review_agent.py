import json

from app.models.ticket import SupportTicket
from app.services.llm_service import gemini_service


class ReviewAgent:

    def review_response(
        self,
        ticket: SupportTicket,
        triage_result: dict,
        customer_draft: str,
        internal_note: str
    ) -> dict:

        prompt = f"""
You are a senior quality assurance reviewer
for a fintech customer support system.

Review the following AI-generated outputs.

CUSTOMER TICKET:
{ticket.model_dump_json(indent=2)}

TRIAGE RESULT:
{triage_result}

CUSTOMER RESPONSE:
{customer_draft}

INTERNAL NOTE:
{internal_note}

Review for:

1. Factual accuracy.
2. Customer communication quality.
3. Unsupported promises or claims.
4. Incorrect transaction details.
5. Financial and security risks.
6. Whether human approval is respected.
7. Whether internal information is exposed to the customer.

IMPORTANT SAFETY RULES:

- Never approve an unverified refund claim.
- Never approve an unsupported transaction status.
- Never approve an action that bypasses human approval.
- Customer messages must not expose internal investigation notes.
- Do not approve a response that claims an investigation has
  occurred unless the supplied evidence confirms it.

Return ONLY valid JSON:

{{
    "approved": false,
    "issues_found": [
        "Description of any issue"
    ],
    "review_summary": "Short explanation",
    "revision_required": true
}}

If everything is acceptable, return approved=true,
an empty issues_found list, and revision_required=false.
"""

        response = gemini_service.generate_response(prompt)

        # Remove optional Markdown code fences.
        cleaned_response = response.strip()

        if cleaned_response.startswith("```"):
            lines = cleaned_response.splitlines()

            if lines[-1].strip() == "```":
                lines = lines[1:-1]

            cleaned_response = "\n".join(lines).strip()

        # Parse JSON response.
        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Review agent returned invalid JSON."
            ) from exc

        # Validate response structure.
        if not isinstance(result, dict):
            raise ValueError("Review result must be a JSON object.")

        required_fields = {
            "approved",
            "issues_found",
            "review_summary",
            "revision_required"
        }

        if not required_fields.issubset(result):
            raise ValueError(
                "Review agent returned an incomplete result."
            )

        if not isinstance(result["approved"], bool):
            raise ValueError("Invalid approval value.")

        if not isinstance(result["revision_required"], bool):
            raise ValueError("Invalid revision value.")

        if not isinstance(result["issues_found"], list):
            raise ValueError("Invalid issues_found value.")

        if not all(
            isinstance(issue, str)
            for issue in result["issues_found"]
        ):
            raise ValueError("Review issues must be strings.")

        if not isinstance(result["review_summary"], str):
            raise ValueError("Invalid review summary.")

        return result
