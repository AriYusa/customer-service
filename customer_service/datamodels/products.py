"""Product information data models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ProductBasic(BaseModel):
    """Basic product information for search results."""

    product_id: str
    name: str
    description: str
    price: float
    category: str
    in_stock: bool
    rating: float
    image_url: str


class ProductSpecifications(BaseModel):
    """Product technical specifications."""

    weight: str | None = None
    volume: str | None = None
    dimensions: str | None = None
    ph_level: str | None = None
    npk_ratio: str | None = None
    coverage: str | None = None
    organic: bool | None = None


class ProductDetails(BaseModel):
    """Detailed product information."""

    product_id: str
    name: str
    description: str
    price: float
    category: str
    in_stock: bool
    stock_quantity: int
    rating: float
    reviews_count: int
    specifications: ProductSpecifications
    images: list[str]
    related_products: list[str]


class ProductComparison(BaseModel):
    """Product comparison result."""

    products: list[ProductDetails]
    comparison_table: dict[str, list[Any]]
    recommendation: str


class ProductReview(BaseModel):
    """Customer product review."""

    review_id: str
    customer_name: str
    rating: int
    title: str
    comment: str
    date: str
    verified_purchase: bool
    helpful_count: int


class DeliveryOption(BaseModel):
    """Delivery method option."""

    method: str
    cost: float | None = None
    delivery: str | None = None


class ProductAvailability(BaseModel):
    """Product availability information."""

    available: bool
    stock_level: str
    online_available: bool
    store_pickup_available: bool
    delivery_options: list[str]
    estimated_delivery: str


class ProductRecommendation(BaseModel):
    """Product recommendation with reason."""

    product_id: str
    name: str
    price: float
    rating: float
    reason: str


class ProductSpecDetail(BaseModel):
    """Detailed product specifications."""

    product_id: str
    product_name: str
    specifications: ProductSpecifications
    dimensions: str
    weight: str
    materials: str
    care_instructions: str
    warranty: str


class ItemAvailability(BaseModel):
    """Item availability check result."""

    available: bool
    quantity_available: int
    next_restock_date: str | None
    alternative_products: list[str]
