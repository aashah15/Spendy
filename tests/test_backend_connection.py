import pytest
import os
import sqlite3
from unittest.mock import patch
from app import app
from database.db import init_db, seed_db, get_db
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)

@pytest.fixture
def client(tmp_path):
    # Use a temporary database file for tests to avoid locking and integrity errors
    db_file = str(tmp_path / "test_spendly.db")

    # Patch the DB_NAME in database.db to use the temporary file
    with patch("database.db.DB_NAME", db_file):
        with app.app_context():
            init_db()
            seed_db()

        with app.test_client() as client:
            yield client

def test_get_user_by_id(client):
    # The seed user has ID 1 (usually)
    user = get_user_by_id(1)
    assert user is not None
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert "member_since" in user

    # Non-existent user
    assert get_user_by_id(999) is None

def test_get_summary_stats(client):
    # Seed user (ID 1) expenses: 45.5+25+120+60+35+89.99+50+15.75 = 441.24
    stats = get_summary_stats(1)
    assert stats["total_spent"] == 441.24
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"

    # User with no expenses
    # Create a new user without expenses
    from database.db import create_user
    user_id = create_user("No Expense User", "noexpense@example.com", "password123")
    stats_empty = get_summary_stats(user_id)
    assert stats_empty["total_spent"] == 0.0
    assert stats_empty["transaction_count"] == 0
    assert stats_empty["top_category"] == "—"

def test_get_recent_transactions(client):
    txs = get_recent_transactions(1)
    assert len(txs) > 0
    # Verify date format "MMM D, YYYY"
    import re
    date_pattern = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$")
    assert date_pattern.match(txs[0]["date"])

    # Verify newest first (seed data has April 18 as latest)
    assert txs[0]["date"] == "Apr 18, 2026"

    # User with no expenses
    from database.db import create_user
    user_id = create_user("No Expense User 2", "noexpense2@example.com", "password123")
    assert get_recent_transactions(user_id) == []

def test_get_category_breakdown(client):
    breakdown = get_category_breakdown(1)
    assert len(breakdown) == 7
    # Verify sum of percentages is 100
    total_pct = sum(cat["pct"] for cat in breakdown)
    assert total_pct == 100
    # Verify sorted by amount desc
    for i in range(len(breakdown) - 1):
        assert breakdown[i]["amount"] >= breakdown[i+1]["amount"]

    # User with no expenses
    from database.db import create_user
    user_id = create_user("No Expense User 3", "noexpense3@example.com", "password123")
    assert get_category_breakdown(user_id) == []

def test_profile_route_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.location == "/login"

def test_profile_route_authenticated(client):
    # Login as seed user
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"}, follow_redirects=True)

    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Demo User" in response.data
    assert b"demo@spendly.com" in response.data
    assert b"\xe2\x82\xb9" in response.data
    assert b"441.24" in response.data
    assert b"8" in response.data
    assert b"Bills" in response.data
