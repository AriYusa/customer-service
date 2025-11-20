"""Returns and refunds data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


# class IssueClass(str, Enum):
#     """Types of issues from the wiki."""

#     MANUFACTURING_DEFECT = "manufacturing_defect_or_shipping_damage"
#     WRONG_ITEM = "wrong_item_received"
#     MISSING_COMPONENTS = "missing_components"
#     CHANGED_MIND = "changed_mind_sealed_unopened"
#     OTHER = "other"


# class Resolution(str, Enum):
#     """Types of resolutions."""

#     REFUND_WITHOUT_RETURN = "refund_without_return"
#     REFUND_WITH_RETURN = "refund_with_return"
#     REPLACEMENT_WITH_RETURN = "replacement_with_return"
#     REPLACEMENT_WITHOUT_RETURN = "replacement_without_return"
#     DECLINED = "declined"


class ReturnInitiationResult(BaseModel):
    """Result of return initiation."""

    success: bool
    return_id: str
    return_label_url: str
    instructions: str
    estimated_refund: float
    refund_eta: str


class ReturnEligibility(BaseModel):
    """Return eligibility information."""

    eligible: bool
    reason: str
    return_window_days: int
    conditions: list[str]
    exceptions: str


class ReturnStatusEvent(BaseModel):
    """Single return status update event."""

    date: str
    status: str
    description: str


class ReturnTrackingInfo(BaseModel):
    """Return tracking information."""

    return_id: str
    status: str
    tracking_number: str
    current_location: str
    received_date: str = ""
    refund_status: str
    refund_amount: float
    history: list[ReturnStatusEvent]


class ReturnCancellationResult(BaseModel):
    """Result of return cancellation."""

    success: bool
    message: str


class ExchangeResult(BaseModel):
    """Result of exchange request."""

    success: bool
    exchange_id: str
    return_label_url: str
    price_difference: float
    new_order_id: str
    estimated_delivery: str


class RefundBreakdown(BaseModel):
    """Refund amount breakdown."""

    items: float
    shipping: float
    tax: float
    total: float


class RefundStatus(BaseModel):
    """Refund status information."""

    order_id: str
    refund_status: str
    refund_amount: float
    refund_method: str
    refund_date: str
    expected_arrival: str
    breakdown: RefundBreakdown


class StoreCreditResult(BaseModel):
    """Store credit request result."""

    success: bool
    credit_amount: float
    bonus_percentage: int
    total_credit: float
    credit_code: str
    expiration_date: str


class EscalationResult(BaseModel):
    """Return issue escalation result."""

    success: bool
    ticket_id: str
    assigned_to: str
    priority: str
    expected_response: str


class ContactInfo(BaseModel):
    """Contact information."""

    phone: str
    email: str
    hours: str


class ReturnPolicy(BaseModel):
    """Return policy information."""

    return_window_days: int
    refund_method: str
    restocking_fee: float
    conditions: list[str]
    non_returnable_items: list[str]
    exchange_policy: str
    contact_info: ContactInfo


class AttachmentCheckResult(BaseModel):
    """Result of checking customer attachments."""

    has_attachments: bool
    attachments_confirm_issue: bool
    attachment_count: int
    notes: str


class InstantRefundResult(BaseModel):
    """Result of instant refund processing."""

    success: bool
    customer_id: str
    refund_amount: float
    transaction_id: str
    message: str


class PrepaidLabelResult(BaseModel):
    """Result of prepaid label creation."""

    success: bool
    customer_id: str
    tracking_number: str
    message: str


class ReplacementOrderResult(BaseModel):
    """Result of replacement order creation."""

    success: bool
    new_osrder_id: str
