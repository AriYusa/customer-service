"""Order management data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .account import OrderItemWithInfo


class OrderStatus(str, Enum):
    """Order status enum."""
    
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


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


class OrderModificationResult(BaseModel):
    """Result of order modification."""

    success: bool
    message: str
    updated_total: float


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
    items: list[OrderItemWithInfo]
    total: float
