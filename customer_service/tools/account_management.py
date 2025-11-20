"""Account management utilities using SQLite database."""

from __future__ import annotations

import json
import uuid

from ..database import database
from ..datamodels.account import (
    Address,
    AddressAction,
    AddressData,
    CommunicationPreferences,
    CustomerRecord,
    LoyaltyBalance,
    Order,
    PaymentMethod,
    SubscriptionPreferences,
)


def _get_customer_record(customer_id: str) -> CustomerRecord | None:
    """Get a customer record from the database."""
    with database.get_db() as conn:
        cursor = conn.cursor()

        # Get customer data
        cursor.execute(
            "SELECT * FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
        )
        customer = cursor.fetchone()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found or account deleted")

        # Get addresses
        cursor.execute("SELECT * FROM addresses WHERE customer_id = ?", (customer_id,))
        addresses = [Address(**addr) for addr in cursor.fetchall()]

        # Get payment methods
        cursor.execute(
            "SELECT * FROM payment_methods WHERE customer_id = ?", (customer_id,)
        )
        payment_methods = [PaymentMethod(**pm) for pm in cursor.fetchall()]

        # Get orders with items
        cursor.execute("SELECT * FROM orders WHERE customer_id = ?", (customer_id,))
        orders = []
        for order in cursor.fetchall():
            # # Fetch order items from order_items and products tables
            # cursor.execute("""
            #     SELECT oi.product_id, p.name, oi.quantity, p.unit_price
            #     FROM order_items oi
            #     JOIN products p ON oi.product_id = p.id
            #     WHERE oi.order_id = ?
            # """, (order["id"],))
            
            # items = [
            #     {
            #         "product_id": item["product_id"],
            #         "name": item["name"],
            #         "quantity": item["quantity"],
            #         "unit_price": item["unit_price"]
            #     }
            #     for item in cursor.fetchall()
            # ]
            
            orders.append(
                Order(
                    id=order["id"],
                    date_ordered=order["date_ordered"],
                    date_delivered=order.get("date_delivered", ""),
                    total=order["total"],
                    status=order["status"],
                    # items=items,
                )
            )

        # Build CustomerRecord
        return CustomerRecord(
            id=customer["id"],
            email=customer["email"],
            profile=json.loads(customer["profile"]),
            addresses=addresses,
            payment_methods=payment_methods,
            orders=orders,
            loyalty=LoyaltyBalance(**json.loads(customer["loyalty"])),
            subscriptions=json.loads(customer["subscriptions"]),
            locked=customer["locked"],
            deleted=customer["deleted"],
        )


def reset_password(email: str) -> dict:
    """Reset a customer's password by sending them a password reset link.

    Sends a reset password link to the provided email address. For security,
    always returns success=True even if email not found to prevent account enumeration.

    Args:
        email: The email address associated with the account

    Returns:
        ResetPasswordResponse containing:
            - success: True if email found and link generated
            - reset_link: URL with reset token (empty if email not found)
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM customers WHERE email = ? AND deleted = FALSE",
            (email.lower(),),
        )
        customer = cursor.fetchone()

        if customer:
            token = str(uuid.uuid4())
            link = (
                f"https://example.com/reset-password?token={token}&uid={customer['id']}"
            )
            # In a real system we'd persist token and expiry
            return {"success": True, "reset_link": link}

    return {"success": False, "reset_link": ""}


def update_email(customer_id: str, new_email: str) -> bool:
    """Update a customer's email address.

    Args:
        customer_id: The ID of the customer account
        new_email: The new email address to set

    Returns:
        bool: True if email was updated successfully, False if customer not found or account deleted
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET email = ? WHERE id = ? AND deleted = FALSE",
            (new_email, customer_id),
        )
        # conn.commit()
        return cursor.rowcount > 0


def add_address(customer_id: str, address_data: AddressData) -> dict:
    """Add a new address for a customer.

    Args:
        customer_id: The ID of the customer account
        address_data: Address information including line1, city, state, etc.

    Returns:
        dict with 'success' (bool) and 'address_id' (str) if successful, empty string if failed
    """
    with database.get_db() as conn:
        cursor = conn.cursor()

        # Check if customer exists and is not deleted
        cursor.execute(
            "SELECT 1 FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
        )
        if not cursor.fetchone():
            return {"success": False, "address_id": ""}

        address_id = f"addr-{uuid.uuid4()}"
        cursor.execute(
            """
            INSERT INTO addresses (id, customer_id, line1, line2, city, state, postal_code, country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                address_id,
                customer_id,
                address_data.line1,
                address_data.line2 or "",
                address_data.city or "",
                address_data.state or "",
                address_data.postal_code or "",
                address_data.country or "",
            ),
        )
        conn.commit()
        return {"success": True, "address_id": address_id}


def update_address(customer_id: str, address_id: str, address_data: AddressData) -> bool:
    """Update an existing address for a customer.

    Args:
        customer_id: The ID of the customer account
        address_id: The ID of the address to update
        address_data: Updated address information

    Returns:
        bool: True if address was updated successfully, False otherwise
    """
    with database.get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE addresses 
            SET line1 = ?, line2 = ?, city = ?, state = ?, postal_code = ?, country = ?
            WHERE id = ? AND customer_id = ?
            """,
            (
                address_data.line1,
                address_data.line2 or "",
                address_data.city or "",
                address_data.state or "",
                address_data.postal_code or "",
                address_data.country or "",
                address_id,
                customer_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_address(customer_id: str, address_id: str) -> bool:
    """Delete an address for a customer.

    Args:
        customer_id: The ID of the customer account
        address_id: The ID of the address to delete

    Returns:
        bool: True if address was deleted successfully, False otherwise
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM addresses WHERE id = ? AND customer_id = ?",
            (address_id, customer_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def list_addresses(customer_id: str) -> list[Address]:
    """List all addresses for a customer.

    Args:
        customer_id: The ID of the customer account

    Returns:
        list[Address]: List of all addresses for the customer. Empty list if customer not found or has no addresses.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        
        # Check if customer exists and is not deleted
        cursor.execute(
            "SELECT 1 FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
        )
        if not cursor.fetchone():
            return []
        
        # Get all addresses for the customer
        cursor.execute("SELECT * FROM addresses WHERE customer_id = ?", (customer_id,))
        addresses = [Address(**addr) for addr in cursor.fetchall()]
        return addresses


def get_loyalty_balance(customer_id: str) -> LoyaltyBalance:
    """Get customer's loyalty program status and points.

    Args:
        customer_id: The ID of the customer account

    Returns:
        LoyaltyBalance: Customer's current loyalty points, tier level, and available rewards.
        If customer not found, returns default LoyaltyBalance (0 points, bronze tier)
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT loyalty FROM customers WHERE id = ? AND deleted = FALSE",
            (customer_id,),
        )
        result = cursor.fetchone()
        if result:
            loyalty_data = json.loads(result["loyalty"])
            return LoyaltyBalance(**loyalty_data)
    return LoyaltyBalance()


def delete_account(customer_id: str, confirmation: bool) -> bool:
    """Delete/deactivate a customer's account.

    Args:
        customer_id: The ID of the customer account
        confirmation: Must be True to confirm deletion

    Returns:
        bool: True if account was deleted (soft-delete), False if customer not found
        or confirmation not provided
    """
    if not confirmation:
        return False

    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET deleted = TRUE WHERE id = ?", (customer_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def unlock_account(customer_id: str) -> bool:
    """Unlock a locked customer account.

    Args:
        customer_id: The ID of the customer account

    Returns:
        bool: True if account was unlocked successfully, False if customer not found
        or account deleted
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET locked = FALSE WHERE id = ? AND deleted = FALSE",
            (customer_id,),
        )
        conn.commit()
        return cursor.rowcount > 0


# def verify_identity(
#     customer_id: str, verification_method: VerificationMethod = "sms"
# ) -> bool:
#     """Verify customer's identity using specified method.

#     Args:
#         customer_id: The ID of the customer account
#         verification_method: Method to use for verification: 'sms', 'email', or 'knowledge'

#     Returns:
#         bool: True if identity verified successfully, False if customer not found,
#         account deleted, or invalid verification method
#     """
#     with database.get_db() as conn:
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT 1 FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
#         )
#         if not cursor.fetchone():
#             return False
#         # In a real system we'd call an identity provider. Here we fake success.
#         return verification_method in {"sms", "email", "knowledge"}


def manage_email_subscriptions(
    customer_id: str, preferences: SubscriptionPreferences
) -> bool:
    """Update customer's email subscription preferences.

    Args:
        customer_id: The ID of the customer account
        preferences: SubscriptionPreferences containing settings for marketing emails,
            newsletters, and product updates

    Returns:
        bool: True if preferences were updated successfully, False if customer not found
        or account deleted
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET subscriptions = ? WHERE id = ? AND deleted = FALSE",
            (json.dumps(preferences), customer_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def update_communication_preferences(
    customer_id: str, preferences: CommunicationPreferences
) -> bool:
    """Update customer's communication preferences.

    Args:
        customer_id: The ID of the customer account
        preferences: CommunicationPreferences containing settings for email, SMS,
            and push notifications

    Returns:
        bool: True if preferences were updated successfully, False if customer not found
        or account deleted
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET communication_preferences = ? WHERE id = ? AND deleted = FALSE",
            (json.dumps(preferences), customer_id),
        )
        conn.commit()
        return cursor.rowcount > 0
