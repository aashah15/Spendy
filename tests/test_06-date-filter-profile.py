import pytest
from app import app as flask_app
from database.db import init_db, get_db

import pytest
import os
import uuid
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    # Use a unique temporary file for each test to avoid locks and persistence issues
    db_name = f"test_{uuid.uuid4()}.db"
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_name,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    import database.db
    database.db.DB_NAME = db_name

    with flask_app.app_context():
        init_db()
        yield flask_app

    # Cleanup the temporary database file after the test
    if os.path.exists(db_name):
        os.remove(db_name)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    })
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass123'})
    return client

@pytest.fixture
def seed_test_expenses(app):
    """Fixture to add specific expenses for the authenticated user."""
    def _seed(expenses):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()[0]

        cursor.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            [(user_id, *exp) for exp in expenses]
        )
        conn.commit()
        conn.close()
    return _seed

class TestDateFilterProfile:

    def test_profile_auth_guard(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_filter_range_happy_path(self, auth_client, seed_test_expenses):
        """Verify that only expenses within the date range are displayed."""
        seed_test_expenses([
            (10.0, "Food", "2026-01-01", "Early"),
            (20.0, "Food", "2026-01-10", "Inside"),
            (30.0, "Food", "2026-01-20", "Late"),
        ])

        response = auth_client.get('/profile?start_date=2026-01-05&end_date=2026-01-15')

        assert response.status_code == 200
        assert b"Inside" in response.data
        assert b"Early" not in response.data
        assert b"Late" not in response.data
        # Summary stat check: Total should be 20.0
        assert b"20.0" in response.data

    def test_filter_start_date_only(self, auth_client, seed_test_expenses):
        """Verify that providing only start_date filters everything from that date forward."""
        seed_test_expenses([
            (10.0, "Food", "2026-01-01", "Old"),
            (20.0, "Food", "2026-02-01", "New"),
        ])

        response = auth_client.get('/profile?start_date=2026-01-15')

        assert response.status_code == 200
        assert b"New" in response.data
        assert b"Old" not in response.data

    def test_filter_end_date_only(self, auth_client, seed_test_expenses):
        """Verify that providing only end_date filters everything up to that date."""
        seed_test_expenses([
            (10.0, "Food", "2026-01-01", "Old"),
            (20.0, "Food", "2026-02-01", "New"),
        ])

        response = auth_client.get('/profile?end_date=2026-01-15')

        assert response.status_code == 200
        assert b"Old" in response.data
        assert b"New" not in response.data

    def test_filter_no_results_range(self, auth_client, seed_test_expenses):
        """Verify that a range with no results renders correctly without crashing."""
        seed_test_expenses([(10.0, "Food", "2026-01-01", "Test")])

        response = auth_client.get('/profile?start_date=2027-01-01&end_date=2027-01-31')

        assert response.status_code == 200
        # Total spending should be 0.0 or similar
        assert b"0.0" in response.data or b"0" in response.data

    def test_filter_invalid_date_format(self, auth_client, seed_test_expenses):
        """Verify that invalid date strings do not crash the application."""
        seed_test_expenses([(10.0, "Food", "2026-01-01", "Test")])

        response = auth_client.get('/profile?start_date=not-a-date&end_date=invalid')

        assert response.status_code == 200

    def test_clear_filters_shows_all(self, auth_client, seed_test_expenses):
        """Verify that clearing the date filters reverts to showing all transactions."""
        seed_test_expenses([
            (10.0, "Food", "2026-01-01", "Exp 1"),
            (20.0, "Food", "2026-02-01", "Exp 2"),
        ])

        # First apply a filter
        auth_client.get('/profile?start_date=2026-01-01&end_date=2026-01-15')

        # Then clear it
        response = auth_client.get('/profile?start_date=&end_date=')

        assert response.status_code == 200
        assert b"Exp 1" in response.data
        assert b"Exp 2" in response.data

    def test_date_order_swapped(self, auth_client, seed_test_expenses):
        """Verify that start_date > end_date results in no transactions."""
        seed_test_expenses([(10.0, "Food", "2026-01-05", "SwappedTest")])

        response = auth_client.get('/profile?start_date=2026-01-10&end_date=2026-01-01')

        assert response.status_code == 200
        assert b"SwappedTest" not in response.data
