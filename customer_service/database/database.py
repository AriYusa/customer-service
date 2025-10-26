"""Database implementation using SQLite."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "customer_service.db"

DEFAULT_CUSTOMER_ID = "cust-1"


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Convert SQLite row to dictionary."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = dict_factory
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database schema."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Create customers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            profile JSON,
            loyalty JSON,
            subscriptions JSON,
            communication_preferences JSON,
            locked BOOLEAN DEFAULT FALSE,
            deleted BOOLEAN DEFAULT FALSE
        )
        """)

        # Create addresses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            line1 TEXT NOT NULL,
            line2 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """)

        # Create payment_methods table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            brand TEXT NOT NULL,
            last4 TEXT NOT NULL,
            exp_month INTEGER NOT NULL,
            exp_year INTEGER NOT NULL,
            token TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """)

        # Create orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            date TEXT NOT NULL,
            total REAL NOT NULL,
            items JSON,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """)

        conn.commit()


def populate_sample_data():
    """Populate the database with sample data."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Add a sample customer
        cursor.execute(
            f"""
        INSERT OR IGNORE INTO customers (
            id, email, profile, loyalty, subscriptions, communication_preferences, locked, deleted
        ) VALUES (
            '{DEFAULT_CUSTOMER_ID}',
            'alice@example.com',
            ?,
            ?,
            ?,
            ?,
            FALSE,
            FALSE
        )
        """,
            (
                json.dumps(
                    {
                        "first_name": "Alice",
                        "last_name": "Example",
                        "account_number": "A123456",
                        "customer_start_date": "2023-01-15",
                    }
                ),
                json.dumps(
                    {
                        "points": 120,
                        "tier": "silver",
                        "rewards": ["5%_off_next_purchase"],
                    }
                ),
                json.dumps({"marketing": True}),
                json.dumps({"email": True, "sms": True, "push_notifications": True}),
            ),
        )

        # Add sample address
        cursor.execute("""
        INSERT OR IGNORE INTO addresses (
            id, customer_id, line1, city, state, postal_code, country
        ) VALUES (
            'addr-1',
            'cust-1',
            '123 Garden Lane',
            'Greenfield',
            'CA',
            '90210',
            'USA'
        )
        """)

        # Add sample payment method
        cursor.execute("""
        INSERT OR IGNORE INTO payment_methods (
            id, customer_id, brand, last4, exp_month, exp_year
        ) VALUES (
            'pm-1',
            'cust-1',
            'Visa',
            '4242',
            12,
            2026
        )
        """)

        # Add sample order
        cursor.execute(
            """
        INSERT OR IGNORE INTO orders (
            id, customer_id, date, total, items
        ) VALUES (
            'ord-1',
            'cust-1',
            '2024-06-01',
            39.43,
            ?
        )
        """,
            (
                json.dumps(
                    [
                        {
                            "product_id": "123",
                            "name": "VP Vinyl Record - The Best of 80s",
                            "quantity": 1,
                            "unit_price": 25.98,
                        }
                    ]
                ),
                json.dumps(
                    [
                        {
                            "product_id": "2o972",
                            "name": "Louis Armstrong Greatest Hits - CD",
                            "quantity": 1,
                            "unit_price": 13.45,
                        }
                    ]
                ),
            ),
        )

        conn.commit()


# Initialize database and sample data
init_db()
populate_sample_data()
