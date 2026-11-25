import json

from app.models.ticket import SupportTicket
from app.services.llm_service import gemini_service


class ReviseAgent:

    def revise_response(
        self,
        ticket: SupportTicket,
        customer_draft: str,
        internal_note: str,
        review_result: dict
    ) -> dict:

        prompt = f"""
You are a senior fintech customer support response editor.

Your task is to revise AI-generated support content
based on the reviewer's feedback.

CUSTOMER TICKET:
{ticket.model_dump_json(indent=2)}

ORIGINAL CUSTOMER RESPONSE:
{customer_draft}

ORIGINAL INTERNAL NOTE:
{internal_note}

REVIEW FEEDBACK:
{review_result}

INSTRUCTIONS:

1. Correct every issue identified by the reviewer.
2. Preserve accurate transaction details.
3. Use professional customer-friendly language.
4. Remove unsupported claims and promises.
5. Never claim that an unverified refund has happened.
6. Never invent transaction statuses or investigation results.
7. Preserve human approval requirements.
8. Keep internal notes separate from customer communication.
9. Do not execute financial operations.

Return ONLY valid JSON in this structure:

{{
    "customer_response": "Revised customer-facing response",
    "internal_note": "Revised internal support note",
    "revision_summary": "Explanation of corrections made"
}}
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
                "Revision agent returned invalid JSON."
            ) from exc

        # Validate response structure.
        if not isinstance(result, dict):
            raise ValueError(
                "Revision result must be a JSON object."
            )

        required_fields = {
            "customer_response",
            "internal_note",
            "revision_summary"
        }

        if not required_fields.issubset(result):
            raise ValueError(
                "Revision agent returned incomplete data."
            )

        for field in required_fields:
            if not isinstance(result[field], str):
                raise ValueError(
                    f"Invalid value for {field}."
                )

        return result
