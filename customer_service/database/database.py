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
        # Delete existing tables for fresh initialization
        cursor.execute("DROP TABLE IF EXISTS order_items")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS payment_methods")
        cursor.execute("DROP TABLE IF EXISTS addresses")
        cursor.execute("DROP TABLE IF EXISTS customers")
        cursor.execute("DROP TABLE IF EXISTS products")

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

        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            unit_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
        """)

        # Create orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            date TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'processing',
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """)

        # Create order_items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """)
        
        conn.commit()


def populate_sample_data():
    """Populate the database with sample data."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Delete all existing data (in reverse order of dependencies)
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM payment_methods")
        cursor.execute("DELETE FROM addresses")
        cursor.execute("DELETE FROM customers")
        cursor.execute("DELETE FROM products")


        # # Check if database already has data
        # cursor.execute("SELECT COUNT(*) as count FROM customers")
        # result = cursor.fetchone()
        # if result and result["count"] > 0:
        #     # Database already has data, skip population
        #     return

        # Add sample products
        cursor.execute("""
        INSERT INTO products (id, name, description, category, unit_price, stock_quantity)
        VALUES 
            ('123', 'VP Vinyl Record - The Best of 80s', 'Classic 80s hits compilation on vinyl', 'Vinyl', 25.98, 50),
            ('2o972', 'Louis Armstrong Greatest Hits - CD', 'Louis Armstrong greatest hits collection', 'CD', 13.45, 30),
            ('456', 'The Beatles - Abbey Road Vinyl LP', 'The Beatles iconic Abbey Road album on vinyl', 'Vinyl', 32.99, 25),
            ('457', 'Record Cleaning Kit', 'Professional vinyl record cleaning kit', 'Accessories', 14.94, 100),
            ('789', 'Pink Floyd - Dark Side of the Moon Vinyl', 'Pink Floyd classic album on vinyl', 'Vinyl', 29.99, 40),
            ('101', 'Miles Davis - Kind of Blue CD', 'Miles Davis legendary jazz album', 'CD', 15.99, 35),
            ('102', 'Fleetwood Mac - Rumours Vinyl', 'Fleetwood Mac bestselling album on vinyl', 'Vinyl', 30.94, 20)
        """)

        # Add a sample customer
        cursor.execute(
            f"""
        INSERT INTO customers (
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

        # Add second customer
        cursor.execute(
            """
        INSERT INTO customers (
            id, email, profile, loyalty, subscriptions, communication_preferences, locked, deleted
        ) VALUES (
            'cust-2',
            'bob@example.com',
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
                        "first_name": "Bob",
                        "last_name": "Smith",
                        "account_number": "B789012",
                        "customer_start_date": "2023-03-20",
                    }
                ),
                json.dumps(
                    {
                        "points": 250,
                        "tier": "gold",
                        "rewards": ["10%_off_next_purchase", "free_shipping"],
                    }
                ),
                json.dumps({"marketing": True}),
                json.dumps({"email": True, "sms": False, "push_notifications": True}),
            ),
        )

        # Add sample address
        cursor.execute("""
        INSERT INTO addresses (
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

        # Add address for second customer
        cursor.execute("""
        INSERT INTO addresses (
            id, customer_id, line1, line2, city, state, postal_code, country
        ) VALUES (
            'addr-2',
            'cust-2',
            '456 Oak Street',
            'Apt 12B',
            'Springfield',
            'NY',
            '10001',
            'USA'
        )
        """)

        # Add sample payment method
        cursor.execute("""
        INSERT INTO payment_methods (
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

        # Add payment method for second customer
        cursor.execute("""
        INSERT INTO payment_methods (
            id, customer_id, brand, last4, exp_month, exp_year
        ) VALUES (
            'pm-2',
            'cust-2',
            'Mastercard',
            '5555',
            8,
            2027
        )
        """)

        # Add sample orders
        cursor.execute("""
        INSERT INTO orders (id, customer_id, date, total, status)
        VALUES 
            ('ord-1', 'cust-1', '2024-06-01', 39.43, 'delivered'),
            ('ord-2', 'cust-2', '2024-05-15', 47.93, 'delivered'),
            ('ord-3', 'cust-2', '2024-07-10', 76.92, 'shipped'),
            ('ord-4', 'cust-1', '2024-10-25', 62.93, 'processing')
        """)

        # Add order items
        cursor.execute("""
        INSERT INTO order_items (order_id, product_id, quantity)
        VALUES 
            ('ord-1', '123', 1),
            ('ord-1', '2o972', 1),
            ('ord-2', '456', 1),
            ('ord-2', '457', 1),
            ('ord-3', '789', 1),
            ('ord-3', '101', 1),
            ('ord-3', '102', 1),
            ('ord-4', '456', 1),
            ('ord-4', '789', 1)
        """)

        conn.commit()
