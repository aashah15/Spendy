import pytest
import sqlite3
from app import app as flask_app
from database.db import init_db, get_db

import pytest
import sqlite3
import os
import tempfile
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    # Create a temporary file for the SQLite database
    db_fd, db_path = tempfile.mkstemp()

    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    # Patch the DB_NAME in database.db so get_db() uses the temp file
    import database.db
    original_db_name = database.db.DB_NAME
    database.db.DB_NAME = db_path

    with flask_app.app_context():
        init_db()
        yield flask_app

    # Clean up
    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)
    database.db.DB_NAME = original_db_name

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    return client

class TestAddExpense:

    def test_add_expense_logged_out_redirects_to_login(self, client):
        """Accessing add expense page while logged out should redirect to login."""
        response = client.get('/expenses/add', follow_redirects=False)
        assert response.status_code == 302
        assert response.location == '/login'

        response = client.post('/expenses/add', data={'amount': '10.0', 'category': 'Food', 'date': '2026-05-16'}, follow_redirects=False)
        assert response.status_code == 302
        assert response.location == '/login'

    def test_add_expense_logged_in_renders_form(self, auth_client):
        """Authenticated user should be able to see the add expense form."""
        response = auth_client.get('/expenses/add')
        assert response.status_code == 200
        assert b'Add Expense' in response.data
        assert b'amount' in response.data.lower()
        assert b'category' in response.data.lower()
        assert b'date' in response.data.lower()

    def test_add_expense_valid_submission_creates_record_and_redirects(self, auth_client, app):
        """Valid submission should create a DB record and redirect to profile."""
        expense_data = {
            'amount': '42.50',
            'category': 'Shopping',
            'date': '2026-05-16',
            'description': 'New book'
        }

        response = auth_client.post('/expenses/add', data=expense_data, follow_redirects=True)

        # Check for success message and redirect
        assert response.status_code == 200
        assert b'Expense added successfully!' in response.data
        # Check that we ended up at profile
        assert response.request.path == '/profile' or response.request.url == 'http://localhost/profile'

        # Verify DB side effect
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT amount, category, date, description FROM expenses ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()

            assert row is not None
            assert row['amount'] == 42.50
            assert row['category'] == 'Shopping'
            assert row['date'] == '2026-05-16'
            assert row['description'] == 'New book'

    def test_add_expense_valid_submission_without_description_works(self, auth_client, app):
        """Submitting without a description should still work."""
        expense_data = {
            'amount': '15.00',
            'category': 'Food',
            'date': '2026-05-16',
            'description': ''
        }

        response = auth_client.post('/expenses/add', data=expense_data, follow_redirects=True)
        assert b'Expense added successfully!' in response.data

        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT description FROM expenses WHERE amount = 15.00 AND category = 'Food'")
            row = cursor.fetchone()
            assert row is not None
            assert row['description'] == '' or row['description'] is None

    @pytest.mark.parametrize("missing_field", [
        {'amount': '', 'category': 'Food', 'date': '2026-05-16'},
        {'amount': '10.0', 'category': '', 'date': '2026-05-16'},
        {'amount': '10.0', 'category': 'Food', 'date': ''},
        {}, # All missing
    ])
    def test_add_expense_missing_required_fields_returns_error(self, auth_client, missing_field):
        """Missing required fields should return a validation error."""
        response = auth_client.post('/expenses/add', data=missing_field)
        assert response.status_code == 200
        assert b'Amount, category, and date are required' in response.data

    @pytest.mark.parametrize("invalid_amount", [
        '0',
        '-10.50',
        'abc',
        '10,00'
    ])
    def test_add_expense_invalid_amount_returns_error(self, auth_client, invalid_amount):
        """Non-positive or non-numeric amounts should return an error."""
        expense_data = {
            'amount': invalid_amount,
            'category': 'Food',
            'date': '2026-05-16'
        }
        response = auth_client.post('/expenses/add', data=expense_data)
        assert response.status_code == 200
        # Check for either positive number error or valid number error
        assert any(msg in response.data for msg in [b'Amount must be a positive number', b'Amount must be a valid number'])

    @pytest.mark.parametrize("invalid_date", [
        '16-05-2026',
        '2026/05/16',
        'May 16 2026',
        'not-a-date'
    ])
    def test_add_expense_invalid_date_format_returns_error(self, auth_client, invalid_date):
        """Dates not in YYYY-MM-DD format should return an error."""
        expense_data = {
            'amount': '10.0',
            'category': 'Food',
            'date': invalid_date
        }
        response = auth_client.post('/expenses/add', data=expense_data)
        assert response.status_code == 200
        assert b'Invalid date format. Please use YYYY-MM-DD' in response.data
