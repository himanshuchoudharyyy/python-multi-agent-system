from app.models.ticket import SupportTicket
from app.services.llm_service import gemini_service


class DraftAgent:

    def generate_draft(self, ticket: SupportTicket, triage_result: dict) -> str:

        prompt = f"""
You are a professional fintech customer support representative.

Generate a customer-facing response for the following support ticket.

CUSTOMER TICKET:
{ticket.model_dump_json(indent=2)}

TRIAGE RESULT:
{triage_result}

Instructions:

1. Start with a polite and appropriate greeting.
2. Acknowledge the customer's reported problem.
3. Show empathy and professionalism.
4. Explain the appropriate next steps clearly.
5. Never claim that an investigation has started unless this is
   explicitly confirmed in the supplied information.
6. Never claim that a refund, reversal, or payment correction
   has happened unless explicitly confirmed.
7. Never promise a specific resolution time unless provided.
8. Never invent transaction details, investigation results,
   payment statuses, or operational activities.
9. Use a currency symbol or currency name only when explicitly
   provided in the ticket.
10. If only a numeric transaction amount is available, retain
    the number without assuming its currency.
11. Do not expose internal risk assessments or investigation notes.
12. Do not promise email updates or other communication methods
    unless they are explicitly confirmed.
13. Keep the response concise, clear, and easy to understand.

Return only the customer-facing message.
"""

        return gemini_service.generate_response(prompt)