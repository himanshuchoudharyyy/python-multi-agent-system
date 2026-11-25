import logging

from fastapi import APIRouter, HTTPException

from app.models.ticket import SupportTicket
from app.workflow.orchestrator import WorkflowOrchestrator


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["Tickets"]
)

orchestrator = WorkflowOrchestrator()

# Temporary in-memory ticket storage.
ticket_store = {}


@router.post("/")
def create_ticket(ticket: SupportTicket):

    if ticket.ticket_id in ticket_store:
        raise HTTPException(
            status_code=409,
            detail="A ticket with this ID already exists."
        )

    try:
        result = orchestrator.process_ticket(ticket)

        ticket_store[ticket.ticket_id] = result

        return {
            "message": "Ticket processed successfully.",
            "result": result
        }

    except Exception as exc:
        logger.exception("Ticket processing failed for ticket %s", ticket.ticket_id)

        raise HTTPException(
            status_code=503,
            detail="Ticket processing is temporarily unavailable."
        ) from exc


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str):

    ticket = ticket_store.get(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found."
        )

    return ticket
