"""Order management utilities using SQLite database."""

from __future__ import annotations

import json

from ..database import database
from ..datamodels.account import Order, OrderItem, OrderItemWithInfo
from ..datamodels.orders import (
    AddressUpdateResult,
    OrderCancellationResult,
    OrderModificationResult,
    OrderStatus,
)


def get_order_history(customer_id: str) -> list[Order]:
    """Get customer's complete order history.

    Args:
        customer_id: The ID of the customer account

    Returns:
        List[Order]: List of customer's past orders with full details including items.
        Empty list if customer not found or account deleted.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()

        # Check if customer exists and is not deleted
        cursor.execute(
            "SELECT 1 FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
        )
        if not cursor.fetchone():
            return []

        cursor.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY date_ordered DESC",
            (customer_id,),
        )
        orders = []
        for order in cursor.fetchall():
            # Fetch order items from order_items and products tables
            cursor.execute("""
                SELECT oi.product_id, p.name, oi.quantity, p.unit_price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            """, (order["id"],))
            
            items = [
                OrderItemWithInfo(
                    product_id=item["product_id"],
                    name=item["name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"]
                )
                for item in cursor.fetchall()
            ]
            
            orders.append(
                Order(
                    id=order["id"],
                    date_ordered=order["date_ordered"],
                    date_delivered=order.get("date_delivered", ""),
                    total=order["total"],
                    status=order["status"],
                    items=items,
                )
            )
        return orders


def get_order_details(customer_id: str, order_id: str) -> dict:
    """Get detailed information about a specific order.

    Args:
        order_id: The unique identifier of the order

    Returns:
        Order with complete order information, or None if not found
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ? and customer_id = ?", (order_id, customer_id))
        order = cursor.fetchone()

        if not order:
            return {}

        # Fetch order items from order_items and products tables
        cursor.execute("""
            SELECT oi.product_id, p.name, oi.quantity, p.unit_price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        order_items = [
            OrderItemWithInfo(
                product_id=item["product_id"],
                name=item["name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            for item in cursor.fetchall()
        ]

        order = Order(
            id=order["id"],
            date_ordered=order["date_ordered"],
            date_delivered=order.get("date_delivered", ""),
            status=order["status"],
            items=order_items,
            total=order["total"],
            shipping_address="123 Garden Lane, Greenfield, CA 90210",
            payment_method="Visa ending in 4242",
        )
        return order.model_dump()

# def track_order(order_id: str) -> OrderTrackingInfo | None:
#     """Track the status and location of an order.

#     Args:
#         order_id: The unique identifier of the order to track

#     Returns:
#         OrderTrackingInfo containing order tracking details, or None if order not found
#     """
#     with database.get_db() as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
#         order = cursor.fetchone()

#         if not order:
#             return None

#         # Mock tracking data
#         return OrderTrackingInfo(
#             order_id=order_id,
#             status="shipped",
#             tracking_number=f"TRACK{order_id[-6:].upper()}",
#             estimated_delivery="2025-10-28",
#             current_location="Distribution Center - Your City",
#             history=[
#                 TrackingEvent(
#                     date="2025-10-24", status="Order placed", location="Online"
#                 ),
#                 TrackingEvent(
#                     date="2025-10-25", status="Processing", location="Warehouse"
#                 ),
#                 TrackingEvent(
#                     date="2025-10-26", status="Shipped", location="Distribution Center"
#                 ),
#             ],
#         )


def cancel_order(order_id: str, reason: str) -> OrderCancellationResult:
    """Cancel an order if it hasn't shipped yet.

    Args:
        order_id: The unique identifier of the order to cancel
        reason: Reason for cancellation

    Returns:
        OrderCancellationResult with cancellation details
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

        if not order:
            return OrderCancellationResult(
                success=False,
                message="Order not found",
                refund_amount=0.0,
            )

        # Check if order can be cancelled (not shipped or delivered)
        if order["status"] in [OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value]:
            return OrderCancellationResult(
                success=False,
                message=f"Order cannot be cancelled because it has already been {order['status']}",
                refund_amount=0.0,
            )

        # Cancel the order (in reality, would update status to 'cancelled')
        return OrderCancellationResult(
            success=True,
            message="Order cancelled successfully",
            refund_amount=order["total"],
        )


def modify_order_list(order_id: str, updated_items: list[OrderItem]) -> OrderModificationResult:
    """Modify an order before it ships change items / quantities.

    Args:
        order_id: The unique identifier of the order to modify
        updated_items: Updated list of items

    Returns:
        OrderModificationResult with modification details
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

        if not order:
            return OrderModificationResult(
                success=False, message="Order not found", updated_total=0.0
            )
        
        # Check if order can be modified (only processing orders)
        if order["status"] != OrderStatus.PROCESSING.value:
            return OrderModificationResult(
                success=False,
                message=f"Order cannot be modified because it is already {order['status']}",
                updated_total=order["total"]
            )
        
        # Get prices from database for each item
        new_total = 0.0
        for item in updated_items:
            cursor.execute("SELECT unit_price FROM products WHERE id = ?", (item.product_id,))
            product = cursor.fetchone()
            if product:
                new_total += product["unit_price"] * item.quantity
            else:
                return OrderModificationResult(
                    success=False,
                    message=f"Product {item.product_id} not found",
                    updated_total=order["total"]
                )

        # Mock update logic - in reality would update DB
        return OrderModificationResult(
            success=True,
            message="Order modified successfully",
            updated_total=new_total,
        )


# def estimate_delivery(order_id: str) -> DeliveryEstimate | None:
#     """Get estimated delivery date and time for an order.

#     Args:
#         order_id: The unique identifier of the order

#     Returns:
#         DeliveryEstimate with delivery information, or None if order not found
#     """
#     with database.get_db() as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
#         order = cursor.fetchone()

#         if not order:
#             return None

#         return DeliveryEstimate(
#             order_id=order_id,
#             estimated_date="2025-10-28",
#             estimated_time_window="9 AM - 5 PM",
#             expedited_options=[
#                 ShippingOption(
#                     method="Next Day Air", cost=25.00, delivery="2025-10-26"
#                 ),
#                 ShippingOption(
#                     method="2-Day Express", cost=15.00, delivery="2025-10-27"
#                 ),
#             ],
#         )


def change_delivery_address(order_id: str, new_address: dict) -> AddressUpdateResult:
    """Update the delivery address for an order before it ships.

    Args:
        order_id: The unique identifier of the order
        new_address: Dict containing address fields:
            - line1: Street address
            - line2: Apartment, suite, etc. (optional)
            - city: City name
            - state: State/province
            - postal_code: ZIP/postal code
            - country: Country

    Returns:
        AddressUpdateResult with update status
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

        if not order:
            return AddressUpdateResult(success=False, message="Order not found")

        # Mock address update
        return AddressUpdateResult(
            success=True, message="Delivery address updated successfully"
        )
