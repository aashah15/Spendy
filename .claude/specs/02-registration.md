# Spec: Registration

## Overview

Implement user registration so new visitors can create a Spendly account. This step upgrades the existing stub GET /register route into a fully functional form that accepts a POST, validates input, hashes the password, and inserts a new row into the users table. On success the user is shown with a success message and then redirected to the login page. This is the entry point for all authenticated features that follow.

---

## Depends on

- Step 1 (Database Setup) — the `users` table must exist with the correct schema

---

## Routes

- **POST /register** — handles form submission for new user registration — public
- **GET /register** — displays the registration form template — public (already exists)

---

## Database Changes

No new tables or columns. The existing users table (id, name, email, password_hash, created_at) covers all requirements.

A new DB helper must be added to database/db.py:

create_user(name, email, password) — hashes the password with werkzeug, inserts a row into users, returns the new user's id. Raises sqlite3.IntegrityError if the email is already taken (UNIQUE constraint).

---

## Templates

Modify: templates/register.html
Change the form action to url_for('register') with method="post"
Add name attributes to all inputs: name, email, password, confirm_password
Add a block to display a flash error message (e.g. "Email already registered", "Passwords do not match")
Keep all existing visual design

---

## Files to Change
app.py — upgrade register() to handle GET and POST; add flash + redirect logic
database/db.py — add create_user() helper
templates/register.html — wire up form action/method and flash message display
---

## Files to Create

None.

---

## New Dependencies

No new dependencies — use existing `werkzeug.security` for password hashing.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — use raw SQLite with parameterized queries only
- Passwords must be hashed using `werkzeug.security.generate_password_hash`
- All templates must extend `base.html`
- Use CSS variables for styling — never hardcode hex values
- Validate all form inputs server-side:
  - Name: required, non-empty
  - Email: required, valid format, unique
  - Password: required, minimum length
- Display user-friendly error messages for validation failures
- On successful registration, redirect to `/login` page
- Handle duplicate email attempts gracefully with clear error message

---

## Definition of Done

- [ ] Registration form displays at `/register` with name, email, and password fields
- [ ] Form submission (POST /register) creates new user in database
- [ ] Password is hashed before storing in database
- [ ] Duplicate email is rejected with clear error message
- [ ] Missing or invalid fields show validation errors
- [ ] Successful registration redirects to `/login` page
- [ ] All SQL queries use parameterized statements (no string formatting)
- [ ] Template extends `base.html` and uses CSS variables for styling
- [ ] App runs without errors after implementation
