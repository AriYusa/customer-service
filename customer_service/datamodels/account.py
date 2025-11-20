"""Account related data models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


class ProfileData(BaseModel):
    first_name: str
    last_name: str
    phone: str = ""
    birthdate: str = ""
    account_number: str = ""
    customer_start_date: str = ""
    
    @field_validator('phone', 'birthdate', 'account_number', 'customer_start_date', mode='before')
    @classmethod
    def convert_none_to_empty(cls, v):
        return v if v is not None else ""


class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderItemWithInfo(OrderItem):
    name: str
    unit_price: float


# class UserPreferences(BaseModel):
#     language: str
#     currency: str
#     notifications: bool | None = None
#     time_zone: str | None = None


class SubscriptionPreferences(BaseModel):
    marketing: bool
    newsletters: bool = False
    product_updates: bool = False
    
    @field_validator('newsletters', 'product_updates', mode='before')
    @classmethod
    def convert_none_to_false(cls, v):
        return v if v is not None else False


class ResetPasswordResponse(BaseModel):
    success: bool
    reset_link: str


class PaymentInfo(BaseModel):
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    token: str = ""
    
    @field_validator('token', mode='before')
    @classmethod
    def convert_none_to_empty(cls, v):
        return v if v is not None else ""


class AddressData(BaseModel):
    line1: str
    line2: str = ""
    city: str = ""
    state: str = ""
    postal_code: str
    country: str = ""

    @field_validator('line2', 'city', 'state', 'postal_code', 'country', mode='before')
    @classmethod
    def convert_none_to_empty(cls, v):
        return v if v is not None else ""

class Address(AddressData):
    id: str

AddressAction = Literal["add", "update", "delete", "list"]
VerificationMethod = Literal["sms", "email", "knowledge"]


class PaymentMethod(BaseModel):
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    token: str = ""

    @field_validator('token', mode='before')
    @classmethod
    def convert_none_to_empty(cls, v):
        return v if v is not None else ""


class Order(BaseModel):
    id: str
    date_ordered: str
    date_delivered: str = ""
    total: float
    status: str = "processing"
    items: list[OrderItemWithInfo] = []
    shipping_address: str = ""
    payment_method: str = ""

    @field_validator('date_delivered', mode='before')
    @classmethod
    def convert_none_to_empty(cls, v):
        return v if v is not None else ""



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
    # preferences: UserPreferences = UserPreferences(language="en", currency="USD")
    subscriptions: SubscriptionPreferences = {"marketing": True}
    locked: bool = False
    deleted: bool = False


class CommunicationPreferences(BaseModel):
    """Communication preferences for notifications."""

    email: bool
    sms: bool
    push_notifications: bool
