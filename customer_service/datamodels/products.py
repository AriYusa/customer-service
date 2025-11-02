"""Product information data models."""

from __future__ import annotations

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
    images: list[str]
    related_products: list[str]


class ItemAvailability(BaseModel):
    """Item availability check result."""

    available: bool
    next_restock_date: str = ""
