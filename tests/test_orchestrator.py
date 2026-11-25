from unittest.mock import Mock

from app.workflow.orchestrator import WorkflowOrchestrator
from app.models.ticket import (
    SupportTicket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


def create_ticket():
    return SupportTicket(
        ticket_id="TKT-001",
        customer_id="CUS-101",
        subject="Payment deducted but transaction failed",
        description="Amount was deducted but merchant did not receive payment.",
        transaction_id="TXN-12345",
        transaction_amount=1500,
    )


def create_orchestrator():
    orchestrator = WorkflowOrchestrator()

    orchestrator.triage_agent = Mock()
    orchestrator.draft_agent = Mock()
    orchestrator.note_agent = Mock()
    orchestrator.review_agent = Mock()
    orchestrator.revise_agent = Mock()

    orchestrator.triage_agent.analyze_ticket.return_value = {
        "category": TicketCategory.PAYMENT,
        "priority": TicketPriority.HIGH,
        "risk_detected": True,
        "requires_human_approval": True,
        "escalation_reason": "Payment discrepancy requires investigation.",
        "reasoning": "Payment was deducted but merchant did not receive it.",
    }

    orchestrator.draft_agent.generate_draft.return_value = (
        "We understand your concern. Your payment issue will be reviewed."
    )

    orchestrator.note_agent.generate_internal_note.return_value = (
        "Verify transaction records before any adjustment."
    )

    orchestrator.review_agent.review_response.return_value = {
        "approved": True,
        "issues_found": [],
        "review_summary": "Outputs passed review.",
        "revision_required": False,
    }

    return orchestrator


def test_financial_ticket_requires_human_approval():
    orchestrator = create_orchestrator()

    result = orchestrator.process_ticket(create_ticket())

    assert result["workflow_status"] == TicketStatus.WAITING_FOR_APPROVAL.value
    assert result["requires_human_approval"] is True
    assert result["ticket"]["category"] == TicketCategory.PAYMENT.value
    assert result["customer_response"] != ""
    assert result["internal_note"] != ""


def test_rejected_response_is_revised_once_and_reviewed_again():
    orchestrator = create_orchestrator()

    orchestrator.review_agent.review_response.side_effect = [
        {
            "approved": False,
            "issues_found": ["Unsupported refund claim."],
            "review_summary": "Refund claim must be removed.",
            "revision_required": True,
        },
        {
            "approved": True,
            "issues_found": [],
            "review_summary": "Revised response passed review.",
            "revision_required": False,
        },
    ]

    orchestrator.revise_agent.revise_response.return_value = {
        "customer_response": "Your payment issue will be reviewed. No refund has been confirmed.",
        "internal_note": "Verify transaction records before any adjustment.",
        "revision_summary": "Removed the unsupported refund claim.",
    }

    result = orchestrator.process_ticket(create_ticket())

    assert orchestrator.revise_agent.revise_response.call_count == 1
    assert orchestrator.review_agent.review_response.call_count == 2
    assert result["review_result"]["approved"] is True
    assert result["revision_result"] is not None
    assert "No refund has been confirmed" in result["customer_response"]
    assert result["workflow_status"] == TicketStatus.WAITING_FOR_APPROVAL.value


def test_ticket_escalates_when_revised_response_still_fails_review():
    orchestrator = create_orchestrator()

    orchestrator.review_agent.review_response.side_effect = [
        {
            "approved": False,
            "issues_found": ["Unsupported claim."],
            "review_summary": "Initial review failed.",
            "revision_required": True,
        },
        {
            "approved": False,
            "issues_found": ["Unsupported claim remains."],
            "review_summary": "Revised response still fails review.",
            "revision_required": True,
        },
    ]

    orchestrator.revise_agent.revise_response.return_value = {
        "customer_response": "Revised customer response.",
        "internal_note": "Revised internal note.",
        "revision_summary": "Attempted correction.",
    }

    result = orchestrator.process_ticket(create_ticket())

    assert orchestrator.revise_agent.revise_response.call_count == 1
    assert orchestrator.review_agent.review_response.call_count == 2
    assert result["review_result"]["approved"] is False
    assert result["workflow_status"] == TicketStatus.ESCALATED.value
    assert result["requires_human_approval"] is True

def test_low_risk_technical_ticket_does_not_require_human_approval():
    orchestrator = create_orchestrator()

    orchestrator.triage_agent.analyze_ticket.return_value = {
        "category": TicketCategory.TECHNICAL,
        "priority": TicketPriority.MEDIUM,
        "risk_detected": False,
        "requires_human_approval": False,
        "escalation_reason": None,
        "reasoning": "Customer reports a transaction history loading issue.",
    }

    result = orchestrator.process_ticket(create_ticket())

    assert result["ticket"]["category"] == TicketCategory.TECHNICAL.value
    assert result["ticket"]["priority"] == TicketPriority.MEDIUM.value
    assert result["requires_human_approval"] is False
    assert result["workflow_status"] == TicketStatus.IN_PROGRESS.value
    assert result["review_result"]["approved"] is True
    assert orchestrator.revise_agent.revise_response.call_count == 0
