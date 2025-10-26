"""Order management data models."""

from __future__ import annotations

from pydantic import BaseModel

from .account import OrderItem


class TrackingEvent(BaseModel):
    """Single tracking event in order history."""

    date: str
    status: str
    location: str


class OrderTrackingInfo(BaseModel):
    """Order tracking information."""

    order_id: str
    status: str
    tracking_number: str
    estimated_delivery: str
    current_location: str
    history: list[TrackingEvent]


class OrderCancellationResult(BaseModel):
    """Result of order cancellation."""

    success: bool
    message: str
    refund_amount: float
    refund_eta: str


class OrderModificationResult(BaseModel):
    """Result of order modification."""

    success: bool
    message: str
    updated_total: float


class OrderDetails(BaseModel):
    """Detailed order information."""

    id: str
    date: str
    status: str
    items: list[OrderItem]
    total: float
    shipping_address: str
    payment_method: str


class ShippingOption(BaseModel):
    """Expedited shipping option."""

    method: str
    cost: float
    delivery: str


class DeliveryEstimate(BaseModel):
    """Delivery estimation information."""

    order_id: str
    estimated_date: str
    estimated_time_window: str
    expedited_options: list[ShippingOption]


class AddressUpdateResult(BaseModel):
    """Result of address update."""

    success: bool
    message: str


class ReorderResult(BaseModel):
    """Result of reordering previous order."""

    success: bool
    new_order_id: str
    items: list[OrderItem]
    total: float
