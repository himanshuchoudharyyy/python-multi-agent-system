from app.agents.triage_agent import TriageAgent
from app.agents.draft_agent import DraftAgent
from app.agents.note_agent import NoteAgent
from app.agents.review_agent import ReviewAgent
from app.agents.revise_agent import ReviseAgent

from app.models.ticket import (
    SupportTicket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


class WorkflowOrchestrator:

    MAX_REVISION_ATTEMPTS = 1

    HUMAN_REVIEW_CATEGORIES = {
        TicketCategory.PAYMENT,
        TicketCategory.REFUND,
        TicketCategory.WALLET,
        TicketCategory.TRANSACTION_DISPUTE,
        TicketCategory.KYC,
        TicketCategory.ACCOUNT,
    }

    def __init__(self):
        self.triage_agent = TriageAgent()
        self.draft_agent = DraftAgent()
        self.note_agent = NoteAgent()
        self.review_agent = ReviewAgent()
        self.revise_agent = ReviseAgent()

    def process_ticket(self, ticket: SupportTicket) -> dict:

        # Step 1: Analyze and classify the ticket.
        triage_result = self.triage_agent.analyze_ticket(ticket)

        ticket = ticket.model_copy(update={
            "category": triage_result["category"],
            "priority": triage_result["priority"],
        })

        # Step 2: Generate customer-facing response.
        customer_draft = self.draft_agent.generate_draft(
            ticket,
            triage_result
        )

        # Step 3: Generate internal support note.
        internal_note = self.note_agent.generate_internal_note(
            ticket,
            triage_result
        )

        # Step 4: Review generated outputs.
        review_result = self.review_agent.review_response(
            ticket,
            triage_result,
            customer_draft,
            internal_note
        )

        revision_result = None

        # Step 5: Revise only within the configured attempt limit.
        for _ in range(self.MAX_REVISION_ATTEMPTS):

            if (
                review_result["approved"]
                or not review_result["revision_required"]
            ):
                break

            revision_result = self.revise_agent.revise_response(
                ticket,
                customer_draft,
                internal_note,
                review_result
            )

            customer_draft = revision_result["customer_response"]
            internal_note = revision_result["internal_note"]

            # Review the revised outputs.
            review_result = self.review_agent.review_response(
                ticket,
                triage_result,
                customer_draft,
                internal_note
            )

        # Step 6: Enforce mandatory human approval using Python.
        # LLM approval cannot override these rules.
        requires_human_approval = (
            triage_result["requires_human_approval"]
            or ticket.category in self.HUMAN_REVIEW_CATEGORIES
            or ticket.priority == TicketPriority.CRITICAL
        )

        # Step 7: Determine final workflow status.
        if not review_result["approved"]:
            final_status = TicketStatus.ESCALATED
            escalation_reason = (
                "AI review did not approve the response "
                "within the permitted revision attempts."
            )

        elif requires_human_approval:
            final_status = TicketStatus.WAITING_FOR_APPROVAL
            escalation_reason = (
                triage_result.get("escalation_reason")
                or "Human approval is required before proceeding."
            )

        else:
            final_status = TicketStatus.IN_PROGRESS
            escalation_reason = None

        # Step 8: Update the ticket.
        ticket = ticket.model_copy(update={
            "ai_draft_response": customer_draft,
            "internal_note": internal_note,
            "requires_human_approval": requires_human_approval,
            "status": final_status,
            "escalation_reason": escalation_reason,
        })

        # Step 9: Return the complete workflow result.
        return {
            "ticket": ticket.model_dump(mode="json"),
            "triage_result": {
                key: value.value if hasattr(value, "value") else value
                for key, value in triage_result.items()
            },
            "customer_response": customer_draft,
            "internal_note": internal_note,
            "review_result": review_result,
            "revision_result": revision_result,
            "workflow_status": final_status.value,
            "requires_human_approval": requires_human_approval,
        }
