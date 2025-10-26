"""Product information utilities."""

from __future__ import annotations

from ..datamodels.products import (
    ItemAvailability,
    ProductAvailability,
    ProductBasic,
    ProductComparison,
    ProductDetails,
    ProductSpecDetail,
    ProductSpecifications,
)


def search_products(
    query: str, category: str | None = None, max_results: int = 10
) -> list[ProductBasic]:
    """Search for products by name, description, or category.

    Args:
        query: Search term or keyword
        category: Optional category filter ()
        max_results: Maximum number of results to return (default: 10)

    Returns:
        List of ProductBasic objects with product information
    """
    # Mock product catalog
    products = [
        ProductBasic(
            product_id="123",
            name="VP Vinyl Record - The Best of 80s",
            description="High-quality vinyl record featuring the best hits of the 1980s.",
            price=25.98,
            category="vinyl",
            in_stock=True,
            rating=4.5,
            image_url="https://example.com/products/123.jpg",
        ),
        ProductBasic(
            product_id="2o972",
            name="Louis Armstrong Greatest Hits - CD",
            description="A collection of the greatest hits by Louis Armstrong.",
            price=13.45,
            category="cd",
            in_stock=True,
            rating=4.3,
            image_url="https://example.com/products/2o972.jpg",
        ),
        ProductBasic(
            product_id="028789",
            name="Protection file for Vinyl Records",
            description="10 sleeves. Keep your vinyl records safe and scratch-free with these protective sleeves.",
            price=2.50,
            category="accessories",
            in_stock=True,
            rating=4.7,
            image_url="https://example.com/products/028789.jpg",
        ),
        ProductBasic(
            product_id="jh1888",
            name="Hozier (10th Anniversary) Custard Colour 2LP",
            description="""Side A
1. Take Me To Church
2. Angel of Small Death & The Codeine Scene
3. Jackie and Wilson
4. Someone New
5. To Be Alone

Side B
1. From Eden
2. In A Week
3. Sedated
4. Work Song

Side C
1. Like Real People Do
2. It Will Come Back
3. Foreigner's God
4. Cherry Wine (Live)

Side D
1. In The Woods Somewhere
2. Run
3. Arsonist's Lullabye
4. My Love Will Never Die""",
            price=34.99,
            category="vinyl",
            in_stock=False,
            rating=4.6,
            image_url="https://example.com/products/jh1888.jpg",
        ),
    ]

    # Filter by category if provided
    if category:
        products = [p for p in products if p.category.lower() == category.lower()]

    # Simple search by query
    query_lower = query.lower()
    results = [
        p
        for p in products
        if query_lower in p.name.lower() or query_lower in p.description.lower()
    ]

    return results[:max_results]


def get_product_details(product_id: str) -> ProductDetails | None:
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
            "specifications": {
                "weight": "20 lbs",
                "volume": "1.5 cubic feet",
                "ph_level": "6.0-7.0",
                "organic": True,
            },
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
            "specifications": {
                "npk_ratio": "10-10-10",
                "weight": "5 lbs",
                "coverage": "2,500 sq ft",
                "organic": False,
            },
            "images": ["https://example.com/products/fertilizer-456.jpg"],
            "related_products": ["soil-123", "fertilizer-457"],
        },
    }

    product_data = products_data.get(product_id)
    if not product_data:
        return None

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
        specifications=ProductSpecifications(**product_data["specifications"]),
        images=product_data["images"],
        related_products=product_data["related_products"],
    )


def compare_products(product_ids: list[str]) -> ProductComparison:
    """Compare multiple products side by side.

    Args:
        product_ids: List of product IDs to compare (2-4 products recommended)

    Returns:
        ProductComparison with comparison details
    """
    products = []
    for pid in product_ids:
        product = get_product_details(pid)
        if product:
            products.append(product)

    if not products:
        return ProductComparison(products=[], comparison_table={}, recommendation="")

    # Create comparison table
    comparison_table = {
        "price": [p.price for p in products],
        "rating": [p.rating for p in products],
        "in_stock": [p.in_stock for p in products],
    }

    # Simple recommendation logic
    best_value = min(products, key=lambda p: p.price / p.rating)

    return ProductComparison(
        products=products,
        comparison_table=comparison_table,
        recommendation=f"{best_value.name} offers the best value",
    )


def check_product_availability(
    product_id: str, zip_code: str | None = None
) -> ProductAvailability:
    """Check product availability and delivery options for a location.

    Args:
        product_id: The unique identifier of the product
        zip_code: Optional ZIP code to check local availability

    Returns:
        ProductAvailability with availability information
    """
    product = get_product_details(product_id)

    if not product:
        return ProductAvailability(
            available=False,
            stock_level="out_of_stock",
            online_available=False,
            store_pickup_available=False,
            delivery_options=[],
            estimated_delivery="",
        )

    return ProductAvailability(
        available=product.in_stock,
        stock_level="in_stock" if product.stock_quantity > 20 else "low_stock",
        online_available=True,
        store_pickup_available=True,
        delivery_options=["standard", "express", "next_day"],
        estimated_delivery="2025-10-28",
    )


def get_product_specifications(product_id: str) -> ProductSpecDetail | None:
    """Get detailed technical specifications for a product.

    Args:
        product_id: The unique identifier of the product

    Returns:
        ProductSpecDetail with detailed specifications, or None if not found
    """
    product = get_product_details(product_id)

    if not product:
        return None

    return ProductSpecDetail(
        product_id=product_id,
        product_name=product.name,
        specifications=product.specifications,
        dimensions="12 x 8 x 6 inches",
        weight=product.specifications.weight or "N/A",
        materials="Various",
        care_instructions="Store in a cool, dry place",
        warranty="30-day satisfaction guarantee",
    )


def check_item_availability(product_id: str, quantity: int = 1) -> ItemAvailability:
    """Check if a product is available and in stock.

    Args:
        product_id: The unique identifier of the product
        quantity: Quantity to check (default: 1)

    Returns:
        ItemAvailability with availability details
    """
    # Mock inventory check
    inventory = {
        "soil-123": 150,
        "fertilizer-456": 75,
        "seeds-789": 200,
        "tools-101": 50,
    }

    available_qty = inventory.get(product_id, 0)

    return ItemAvailability(
        available=available_qty >= quantity,
        quantity_available=available_qty,
        next_restock_date="2025-11-01" if available_qty < quantity else None,
        alternative_products=["soil-124", "soil-125"]
        if available_qty < quantity
        else [],
    )
