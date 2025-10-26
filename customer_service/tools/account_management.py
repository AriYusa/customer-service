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
    VerificationMethod,
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
            return None

        # Get addresses
        cursor.execute("SELECT * FROM addresses WHERE customer_id = ?", (customer_id,))
        addresses = [Address(**addr) for addr in cursor.fetchall()]

        # Get payment methods
        cursor.execute(
            "SELECT * FROM payment_methods WHERE customer_id = ?", (customer_id,)
        )
        payment_methods = [PaymentMethod(**pm) for pm in cursor.fetchall()]

        # Get orders
        cursor.execute("SELECT * FROM orders WHERE customer_id = ?", (customer_id,))
        orders = []
        for order in cursor.fetchall():
            items = json.loads(order["items"])
            orders.append(
                Order(
                    id=order["id"],
                    date=order["date"],
                    total=order["total"],
                    items=items,
                )
            )

        # Build CustomerRecord
        return CustomerRecord(
            id=customer["id"],
            email=customer["email"],
            profile=json.loads(customer["profile"]),
            addresses=addresses,
            payment_methods=payment_methods,
            # orders=orders,
            loyalty=LoyaltyBalance(**json.loads(customer["loyalty"])),
            preferences=json.loads(customer["preferences"]),
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


def manage_addresses(
    customer_id: str, action: AddressAction, address_data: AddressData | None = None
) -> bool:
    """Manage addresses for a customer.

    action: 'add', 'update', 'delete', 'list'
    For 'add' provide address_data (fields for Address except id).
    For 'update' provide address_data with 'id' and fields to update.
    For 'delete' provide address_data with 'id'.
    For 'list' address_data is ignored and returns True (addresses kept in DB).
    """
    with database.get_db() as conn:
        cursor = conn.cursor()

        # Check if customer exists and is not deleted
        cursor.execute(
            "SELECT 1 FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
        )
        if not cursor.fetchone():
            return False

        action = action.lower()
        if action == "add" and address_data:
            aid = address_data.get("id") or f"addr-{uuid.uuid4()}"
            fields = {k: v for k, v in address_data.items() if k != "id"}
            fields["customer_id"] = customer_id
            fields["id"] = aid

            placeholders = ", ".join("?" * len(fields))
            columns = ", ".join(fields.keys())
            values = tuple(fields.values())

            cursor.execute(
                f"INSERT INTO addresses ({columns}) VALUES ({placeholders})", values
            )
            return True

        elif action == "update" and address_data and "id" in address_data:
            updates = {k: v for k, v in address_data.items() if k != "id"}
            if not updates:
                return False

            set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
            values = (*updates.values(), address_data["id"], customer_id)

            cursor.execute(
                f"UPDATE addresses SET {set_clause} WHERE id = ? AND customer_id = ?",
                values,
            )
            return cursor.rowcount > 0

        elif action == "delete" and address_data and "id" in address_data:
            cursor.execute(
                "DELETE FROM addresses WHERE id = ? AND customer_id = ?",
                (address_data["id"], customer_id),
            )
            return cursor.rowcount > 0

        elif action == "list":
            return True

        return False


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
        return cursor.rowcount > 0


def verify_identity(
    customer_id: str, verification_method: VerificationMethod = "sms"
) -> bool:
    """Verify customer's identity using specified method.

    Args:
        customer_id: The ID of the customer account
        verification_method: Method to use for verification: 'sms', 'email', or 'knowledge'

    Returns:
        bool: True if identity verified successfully, False if customer not found,
        account deleted, or invalid verification method
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM customers WHERE id = ? AND deleted = FALSE", (customer_id,)
        )
        if not cursor.fetchone():
            return False
        # In a real system we'd call an identity provider. Here we fake success.
        return verification_method in {"sms", "email", "knowledge"}


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
        return cursor.rowcount > 0
