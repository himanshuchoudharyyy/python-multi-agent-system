from app.models.ticket import SupportTicket
from app.services.llm_service import gemini_service


class NoteAgent:

    def generate_internal_note(
        self,
        ticket: SupportTicket,
        triage_result: dict
    ) -> str:

        prompt = f"""
You are an internal fintech support operations specialist.

Generate a structured internal case note for the support team.

CUSTOMER TICKET:
{ticket.model_dump_json(indent=2)}

TRIAGE RESULT:
{triage_result}

Include these sections:

1. Issue Summary
2. Transaction Details
3. Risk Assessment
4. Investigation Required
5. Recommended Next Steps
6. Human Approval Requirements

Instructions:

1. Clearly distinguish customer-reported information from
   independently verified information.
2. Treat the customer's description as a report, not as
   independently confirmed transaction evidence.
3. Include transaction ID and amount only when available.
4. Never assume a currency if the ticket does not specify one.
5. Do not invent transaction statuses, ledger entries,
   gateway responses, merchant confirmations, or investigation results.
6. Possible causes may be listed as hypotheses only.
   Clearly label them as unverified possibilities.
7. Do not claim that an investigation, refund, reversal,
   or ledger correction has already happened unless confirmed.
8. Identify financial and security risks based on the
   information actually provided.
9. Recommend investigation and verification steps without
   implying that those steps have already been performed.
10. Clearly state when human approval is required.
11. Keep the note professional, concise, and operational.
12. Do not write this as a customer-facing response.

Return only the internal note.
"""

        return gemini_service.generate_response(prompt)