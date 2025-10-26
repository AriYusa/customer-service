"""Account related data models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ProfileData(BaseModel):
    first_name: str
    last_name: str
    phone: str | None = None
    birthdate: str | None = None
    account_number: str | None = None
    customer_start_date: str | None = None


class OrderItem(BaseModel):
    product_id: str
    name: str
    quantity: int
    unit_price: float | None = None


class UserPreferences(BaseModel):
    language: str
    currency: str
    notifications: bool | None = None
    time_zone: str | None = None


class SubscriptionPreferences(BaseModel):
    marketing: bool
    newsletters: bool | None = None
    product_updates: bool | None = None


class ResetPasswordResponse(BaseModel):
    success: bool
    reset_link: str


class PaymentInfo(BaseModel):
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    token: str | None = None


class AddressData(BaseModel):
    line1: str
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


AddressAction = Literal["add", "update", "delete", "list"]
VerificationMethod = Literal["sms", "email", "knowledge"]


class Address(BaseModel):
    id: str
    line1: str
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class PaymentMethod(BaseModel):
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    token: str | None = None


class Order(BaseModel):
    id: str
    date: str
    total: float
    items: list[OrderItem] = []


class LoyaltyBalance(BaseModel):
    points: int = 0
    tier: str = "bronze"
    rewards: list[str] = []


class CustomerRecord(BaseModel):
    id: str
    email: str
    profile: ProfileData = ProfileData(first_name="", last_name="")
    addresses: list[Address] = []
    payment_methods: list[PaymentMethod] = []
    orders: list[Order] = []
    loyalty: LoyaltyBalance = LoyaltyBalance()
    preferences: UserPreferences = UserPreferences(language="en", currency="USD")
    subscriptions: SubscriptionPreferences = {"marketing": True}
    locked: bool = False
    deleted: bool = False


class CommunicationPreferences(BaseModel):
    """Communication preferences for notifications."""

    email: bool
    sms: bool
    push_notifications: bool
