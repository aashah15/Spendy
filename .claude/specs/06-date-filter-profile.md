# Spec: Date Filter for Profile Page

## Overview
This feature adds a date range filter to the profile page, allowing users to view their spending patterns, summary statistics, and transaction history for a specific time period. This improves the utility of the profile page by enabling users to analyze their finances over custom intervals (e.g., a specific month or year).

## Depends on
- 04-profile-page
- 05-backend-routes-for-profile-page

## Routes
Modify existing route:
- GET /profile — Update to accept optional `start_date` and `end_date` query parameters and pass them to the database queries.

## Database changes
No database changes.

## Templates
Modify:
- `templates/profile.html` — Add a date filter form (two date inputs and a submit button) above the stats and transaction sections.

## Files to change
- `app.py` — Update the `/profile` route to handle date query parameters.
- `database/queries.py` — Update `get_recent_transactions`, `get_summary_stats`, and `get_category_breakdown` to support date range filtering.
- `templates/profile.html` — Add the UI for the date filter.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html
- Handle cases where `start_date` or `end_date` are missing (default to all time or a reasonable default like the current month).
- Ensure date inputs use the `date` type for a native browser date picker.

## Definition of done
- [ ] The profile page displays a date filter with "Start Date" and "End Date" inputs.
- [ ] Selecting a date range and submitting the form updates the summary stats (Total Spending, etc.) to reflect only expenses within that range.
- [ ] The transaction list updates to show only expenses within the selected date range.
- [ ] The category breakdown chart/list updates to reflect spending within the selected date range.
- [ ] Clearing the dates and submitting reverts the view to show all transactions.
- [ ] The page does not crash when invalid or empty dates are provided.
