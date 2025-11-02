"""Payment and billing data models."""

from __future__ import annotations

from pydantic import BaseModel


class PaymentMethodResult(BaseModel):
    """Result of adding/removing/updating payment method."""

    success: bool
    message: str
    payment_method_id: str = ""

class RefundResult(BaseModel):
    """Result of refund processing."""

    success: bool
    refund_id: str
    amount: float
    estimated_arrival: str
    method: str


class Invoice(BaseModel):
    """Invoice details."""

    invoice_id: str
    order_id: str
    date: str
    items: list[dict]  # OrderItemWithInfo dict representation
    subtotal: float
    tax: float
    shipping: float
    total: float
    download_url: str


class DisputeResult(BaseModel):
    """Result of charge dispute."""

    success: bool
    dispute_id: str
    status: str
    expected_resolution_date: str


class PromoCodeResult(BaseModel):
    """Result of applying promo code."""

    success: bool
    discount_amount: float
    new_total: float
    message: str


class BillingRecord(BaseModel):
    """Single billing history record."""

    date: str
    description: str
    amount: float
    status: str
    invoice_id: str


class BillingAddressResult(BaseModel):
    """Result of billing address update."""

    success: bool
    message: str
