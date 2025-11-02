"""Payment and billing utilities using SQLite database."""

from __future__ import annotations

import json
import uuid

from ..database import database
from ..datamodels.account import PaymentMethod
from ..datamodels.payments import (
    BillingRecord,
    DisputeResult,
    Invoice,
    PaymentMethodResult,
    PromoCodeResult,
    RefundResult,
)


def remove_payment_method(
    customer_id: str, payment_method_id: str
) -> PaymentMethodResult:
    """Remove a payment method from customer's account.

    Args:
        customer_id: The ID of the customer account
        payment_method_id: The ID of the payment method to remove

    Returns:
        PaymentMethodResult with removal status
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM payment_methods WHERE id = ? AND customer_id = ?",
            (payment_method_id, customer_id),
        )

        if cursor.rowcount > 0:
            return PaymentMethodResult(
                success=True,
                message="Payment method removed successfully",
            )
        return PaymentMethodResult(
            success=False, message="Payment method not found"
        )


def get_payment_methods(customer_id: str) -> list[PaymentMethod]:
    """Get all payment methods for a customer.

    Args:
        customer_id: The ID of the customer account

    Returns:
        List[PaymentMethod]: List of customer's payment methods.
        Empty list if customer not found or no payment methods.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM payment_methods WHERE customer_id = ?", (customer_id,)
        )
        methods = cursor.fetchall()
        return [PaymentMethod(**m) for m in methods]


def process_refund(
    order_id: str, amount: float | None = None, reason: str = ""
) -> RefundResult:
    """Process a refund for an order.

    Args:
        order_id: The unique identifier of the order
        amount: Amount to refund (None for full refund)
        reason: Reason for the refund

    Returns:
        RefundResult with refund processing details
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

        if not order:
            return RefundResult(
                success=False, refund_id="", amount=0.0, estimated_arrival="", method=""
            )

        refund_amount = amount if amount is not None else order["total"]
        refund_id = f"refund-{uuid.uuid4()}"

        return RefundResult(
            success=True,
            refund_id=refund_id,
            amount=refund_amount,
            estimated_arrival="3-5 business days",
            method="Original payment method",
        )


def get_invoice(order_id: str) -> Invoice:
    """Retrieve invoice details for an order.

    Args:
        order_id: The unique identifier of the order

    Returns:
        Invoice with complete invoice details, or None if order not found
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
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
        
        items = [
            {
                "product_id": item["product_id"],
                "name": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"]
            }
            for item in cursor.fetchall()
        ]
        
        subtotal = order["total"] * 0.85  # Mock calculation
        tax = order["total"] * 0.10
        shipping = order["total"] * 0.05

        return Invoice(
            invoice_id=f"INV-{order_id}",
            order_id=order_id,
            date=order["date"],
            items=items,
            subtotal=round(subtotal, 2),
            tax=round(tax, 2),
            shipping=round(shipping, 2),
            total=order["total"],
            download_url=f"https://example.com/invoices/{order_id}.pdf",
        )


def dispute_charge(order_id: str, reason: str, details: str) -> DisputeResult:
    """File a dispute for a charge.

    Args:
        order_id: The unique identifier of the order to dispute
        reason: Reason for dispute (unauthorized, duplicate, defective, etc.)
        details: Detailed explanation of the dispute

    Returns:
        DisputeResult with dispute filing details
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

        if not order:
            return DisputeResult(
                success=False, dispute_id="", status="", expected_resolution_date=""
            )

        dispute_id = f"dispute-{uuid.uuid4()}"

        return DisputeResult(
            success=True,
            dispute_id=dispute_id,
            status="under_review",
            expected_resolution_date="2025-11-15",
        )


def apply_promo_code(order_id: str, promo_code: str) -> PromoCodeResult:
    """Apply a promotional code to an order.

    Args:
        order_id: The unique identifier of the order
        promo_code: The promotional code to apply

    Returns:
        PromoCodeResult with promo code application details
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

        if not order:
            return PromoCodeResult(
                success=False,
                discount_amount=0.0,
                new_total=0.0,
                message="Order not found",
            )

        # Mock promo code validation
        valid_codes = {
            "SAVE10": {"type": "percentage", "value": 10},
            "SAVE20": {"type": "percentage", "value": 20},
            "FREESHIP": {"type": "free_shipping", "value": 0},
        }

        if promo_code not in valid_codes:
            return PromoCodeResult(
                success=False,
                discount_amount=0.0,
                new_total=order["total"],
                message="Invalid promo code",
            )

        promo = valid_codes[promo_code]
        if promo["type"] == "percentage":
            discount = order["total"] * (promo["value"] / 100)
            new_total = order["total"] - discount
            message = f"{promo['value']}% off applied"
        else:
            discount = 5.00  # Mock shipping cost
            new_total = order["total"] - discount
            message = "Free shipping applied"

        return PromoCodeResult(
            success=True,
            discount_amount=round(discount, 2),
            new_total=round(new_total, 2),
            message=message,
        )


def get_billing_history(customer_id: str, months: int = 6) -> list[BillingRecord]:
    """Get customer's billing history.

    Args:
        customer_id: The ID of the customer account
        months: Number of months of history to retrieve (default: 6)

    Returns:
        List of BillingRecord objects
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY date DESC",
            (customer_id,),
        )
        orders = cursor.fetchall()

        billing_records = []
        for order in orders:
            billing_records.append(
                BillingRecord(
                    date=order["date"],
                    description=f"Order {order['id']}",
                    amount=order["total"],
                    status="paid",
                    invoice_id=f"INV-{order['id']}",
                )
            )

        return billing_records
