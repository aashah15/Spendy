# Spec: Login and Logout

## Overview

This feature implements user authentication for Spendly. It converts the /login stub into a functional POST handler that verifies credentials against the database, stores the authenticated user's ID in the session, and redirects to the dashboard (or a suitable landing page). It also implements the /logout stub, which clears the session and redirects to the landing page. After this step, the app can distinguish logged-in users from guests, which is a prerequisite for all expense features. 

---

## Depends on

- Step 1 (Database Setup) — the `users` table must exist with the correct schema
- Step 2 (Registration) — users must be able to create accounts before they can log in

---

## Routes

- **POST /login** — handles form submission, validates credentials, creates session — public
- **GET /login** — displays the login form template — public (already exists)
- **GET /logout** — clears session and redirects to landing page — logged-in users

---

## Database Changes

No new tables or columns. The existing `users` table (id, name, email, password_hash, created_at) covers all requirements.

A new DB helper must be added to `database/db.py`:

`get_user_by_email(email)` — fetches a user row by email address. Returns the user dict if found, None otherwise. Used during login to retrieve the stored password hash.

---

## Templates

**Create:** None

**Modify:** templates/login.html
- Add `action="{{ url_for('login') }}"` to the form (currently uses hardcoded `/login`)
- Add a flash message block to display error messages (e.g., "Invalid email or password")
- Keep all existing visual design and structure

---

## Files to Change

- **app.py** — upgrade `login()` to handle POST requests, validate credentials, and manage sessions; implement `logout()` to clear session and redirect
- **database/db.py** — add `get_user_by_email()` helper function
- **templates/login.html** — wire up form action with url_for and add flash message display

---

## Files to Create

None.

---

## New Dependencies

No new dependencies — use Flask's built-in `session` object for session management.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — use raw SQLite with parameterized queries only
- Passwords must be verified using `werkzeug.security.check_password_hash`
- All templates must extend `base.html`
- Use CSS variables for styling — never hardcode hex values
- Validate login credentials server-side:
  - Email: required, must exist in database
  - Password: required, must match stored hash
- On successful login, redirect to `/profile` (or `/` if profile not yet implemented)
- On failed login, display generic error message ("Invalid email or password") — do not reveal whether email exists
- Session must store user_id for authenticated requests
- Logout must clear the session and redirect to landing page
- Handle missing/invalid sessions gracefully on protected routes

---

## Definition of Done

- [ ] Login form at `/login` accepts POST submission with email and password
- [ ] Valid credentials create a session and redirect to profile/landing page
- [ ] Invalid credentials display error message without revealing which field failed
- [ ] Password verification uses `werkzeug.security.check_password_hash`
- [ ] Logout route clears session and redirects to landing page
- [ ] All SQL queries use parameterized statements (no string formatting)
- [ ] Login template extends `base.html` and uses CSS variables for styling
- [ ] App runs without errors after implementation
- [ ] Session persists across page requests for logged-in users
