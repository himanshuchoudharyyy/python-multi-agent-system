import json

from app.models.ticket import (
    SupportTicket,
    TicketCategory,
    TicketPriority,
)
from app.services.llm_service import gemini_service


class TriageAgent:

    def analyze_ticket(self, ticket: SupportTicket) -> dict:

        prompt = f"""
You are a fintech customer support ticket triage specialist.

Analyze the following customer support ticket.

TICKET:
{ticket.model_dump_json(indent=2)}

Your responsibilities:
1. Identify the correct ticket category.
2. Assign priority: low, medium, high, or critical.
3. Identify financial or security risks.
4. Decide whether human intervention is required.
5. Explain your classification.

Return ONLY valid JSON in this exact structure:

{{
    "category": "payment",
    "priority": "high",
    "risk_detected": true,
    "requires_human_approval": true,
    "escalation_reason": "Financial transaction requires investigation",
    "reasoning": "Payment was deducted but merchant did not receive it."
}}

Allowed categories:
payment, refund, wallet, kyc, transaction_dispute, account, technical, other.

Do not assume that a refund or transaction reversal has happened.
"""

        response = gemini_service.generate_response(prompt)

        # Remove optional Markdown code fences.
        cleaned_response = response.strip()

        if cleaned_response.startswith("```"):
            lines = cleaned_response.splitlines()

            if lines[-1].strip() == "```":
                lines = lines[1:-1]

            cleaned_response = "\n".join(lines).strip()

        # Parse the Gemini response.
        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Triage agent returned invalid JSON."
            ) from exc

        # Validate the response structure.
        if not isinstance(result, dict):
            raise ValueError(
                "Triage result must be a JSON object."
            )

        required_fields = {
            "category",
            "priority",
            "risk_detected",
            "requires_human_approval",
            "escalation_reason",
            "reasoning",
        }

        if not required_fields.issubset(result):
            raise ValueError(
                "Triage agent returned incomplete data."
            )

        # Validate category and priority.
        try:
            result["category"] = TicketCategory(result["category"])
            result["priority"] = TicketPriority(result["priority"])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "Triage agent returned an invalid category or priority."
            ) from exc

        # Validate Boolean fields.
        if not isinstance(result["risk_detected"], bool):
            raise ValueError(
                "Triage agent returned an invalid risk_detected value."
            )

        if not isinstance(result["requires_human_approval"], bool):
            raise ValueError(
                "Triage agent returned an invalid human approval value."
            )

        # Validate text fields.
        for field in ("escalation_reason", "reasoning"):
            if not isinstance(result[field], str):
                raise ValueError(
                    f"Triage agent returned an invalid {field} value."
                )

        return result
