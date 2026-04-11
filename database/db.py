import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "spendly.db"


def get_db():
    """
    Opens connection to the SQLite database.
    Sets row_factory for dictionary-like access and enables foreign keys.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Creates the users and expenses tables if they don't exist.
    Safe to call multiple times.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    """
    Inserts sample demo user and expenses if they don't already exist.
    Safe to call multiple times without duplicating data.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check if users table already has data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Insert demo user
    demo_password_hash = generate_password_hash("demo123")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, ("Demo User", "demo@spendly.com", demo_password_hash))

    # Get the demo user's ID
    cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",))
    user_id = cursor.fetchone()[0]

    # Insert 8 sample expenses across different categories
    # Dates spread across April 2026
    sample_expenses = [
        (user_id, 45.50, "Food", "2026-04-01", "Lunch at cafe"),
        (user_id, 25.00, "Transport", "2026-04-03", "Uber ride"),
        (user_id, 120.00, "Bills", "2026-04-05", "Electric bill"),
        (user_id, 60.00, "Health", "2026-04-07", "Pharmacy"),
        (user_id, 35.00, "Entertainment", "2026-04-10", "Movie tickets"),
        (user_id, 89.99, "Shopping", "2026-04-12", "New shirt"),
        (user_id, 50.00, "Other", "2026-04-15", "Gift for friend"),
        (user_id, 15.75, "Food", "2026-04-18", "Coffee and snacks"),
    ]

    cursor.executemany("""
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, sample_expenses)

    conn.commit()
    conn.close()


def create_user(name, email, password):
    """
    Creates a new user in the database.

    Args:
        name: User's full name
        email: User's email address
        password: User's plain text password

    Returns:
        The new user's id

    Raises:
        sqlite3.IntegrityError: If email already exists (UNIQUE constraint)
    """
    conn = get_db()
    cursor = conn.cursor()

    # Hash the password
    password_hash = generate_password_hash(password)

    # Insert new user
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, created_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (name, email, password_hash))

    # Get the new user's ID
    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return user_id
