---
name: add-expense
description: Specification for implementing the add expense feature
metadata:
  type: project
---

# Spec: Add Expense

## Overview
This feature allows authenticated users to log new expenses. It provides a form to enter the amount, category, date, and an optional description. This is a core functionality of the Spendly app, enabling users to start tracking their spending.

## Depends on
- Step 03: User Registration
- Step 04: User Login
- Step 01: Database Setup

## Routes
- GET /expenses/add — Display the add expense form — logged-in
- POST /expenses/add — Process and save the new expense — logged-in

## Database changes
No database changes.

## Templates
- Create: `templates/add_expense.html`
- Modify: `templates/base.html` (add a link to the add expense page in the navigation)

## Files to change
- `app.py`
- `database/queries.py`

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html
- Ensure a valid user ID is used (from session)
- Validate that amount is a positive number and date is in YYYY-MM-DD format.

## Definition of done
- A logged-in user can navigate to `/expenses/add`.
- The add expense form is displayed and follows the project's design.
- Submitting the form with valid data creates a new record in the `expenses` table.
- Submitting the form with invalid data (e.g., negative amount, empty category) shows an appropriate error message.
- After successful submission, the user is redirected to their profile page with a success message.
- The new expense appears in the transaction history on the profile page.
