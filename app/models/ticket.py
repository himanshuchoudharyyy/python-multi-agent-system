from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketCategory(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    WALLET = "wallet"
    KYC = "kyc"
    TRANSACTION_DISPUTE = "transaction_dispute"
    ACCOUNT = "account"
    TECHNICAL = "technical"
    OTHER = "other"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class SupportTicket(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)

    ticket_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    customer_name: Optional[str] = None

    subject: str = Field(min_length=1)
    description: str = Field(min_length=1)

    category: TicketCategory = TicketCategory.OTHER
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN

    transaction_id: Optional[str] = None
    transaction_amount: Optional[float] = Field(
        default=None,
        gt=0
    )

    ai_draft_response: Optional[str] = None
    internal_note: Optional[str] = None

    requires_human_approval: bool = False
    escalation_reason: Optional[str] = None
