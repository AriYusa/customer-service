"""Product information utilities."""

from __future__ import annotations

from ..datamodels.products import (
    ItemAvailability,
    ProductDetails,
)


def get_product_details(product_id: str) -> ProductDetails:
    """Get detailed information about a specific product.

    Args:
        product_id: The unique identifier of the product

    Returns:
        ProductDetails with complete product information, or None if not found
    """
    # Mock product database
    products_data = {
        "soil-123": {
            "product_id": "soil-123",
            "name": "Premium Organic Potting Soil",
            "description": "High-quality organic potting mix perfect for indoor and outdoor plants. "
            "Contains coconut coir, perlite, and aged compost for optimal drainage and nutrition.",
            "price": 25.98,
            "category": "soil",
            "in_stock": True,
            "stock_quantity": 150,
            "rating": 4.5,
            "reviews_count": 342,
            "images": [
                "https://example.com/products/soil-123-1.jpg",
                "https://example.com/products/soil-123-2.jpg",
            ],
            "related_products": ["soil-124", "fertilizer-456"],
        },
        "fertilizer-456": {
            "product_id": "fertilizer-456",
            "name": "All-Purpose Plant Fertilizer",
            "description": "Balanced 10-10-10 NPK fertilizer suitable for all plant types.",
            "price": 15.99,
            "category": "fertilizer",
            "in_stock": True,
            "stock_quantity": 75,
            "rating": 4.3,
            "reviews_count": 189,
            "images": ["https://example.com/products/fertilizer-456.jpg"],
            "related_products": ["soil-123", "fertilizer-457"],
        },
    }

    product_data = products_data.get(product_id)
    if not product_data:
        return {}

    return ProductDetails(
        product_id=product_data["product_id"],
        name=product_data["name"],
        description=product_data["description"],
        price=product_data["price"],
        category=product_data["category"],
        in_stock=product_data["in_stock"],
        stock_quantity=product_data["stock_quantity"],
        rating=product_data["rating"],
        reviews_count=product_data["reviews_count"],
        images=product_data["images"],
        related_products=product_data["related_products"],
    )


def check_item_availability(product_id: str, quantity: int = 1) -> ItemAvailability:
    """Check if a product is available and in stock.

    Args:
        product_id: The unique identifier of the product
        quantity: Quantity to check (default: 1)

    Returns:
        ItemAvailability with availability details
    """
    from ..database.database import get_db
    
    # Query database for product stock quantity
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stock_quantity FROM products WHERE id = ?",
            (product_id,)
        )
        result = cursor.fetchone()
    
    available_qty = result["stock_quantity"] if result else 0

    return ItemAvailability(
        available=available_qty >= quantity,
        next_restock_date="2025-11-01" if available_qty < quantity else "",
    )
