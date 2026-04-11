# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly is a personal expense tracking web application built with Flask and SQLite. Users can log expenses, view spending patterns by category, and manage their personal finances.

## Commands

```bash
# Run the application
python app.py

# Run tests
pytest
```

## Architecture

- **app.py** — Main Flask application with routes for authentication, expense management, and static pages
- **database/db.py** — SQLite database layer (students implement `get_db()`, `init_db()`, `seed_db()`)
- **templates/** — Jinja2 templates extending `base.html` (landing, auth, legal pages)
- **static/css/style.css** — Application styles
- **static/js/main.js** — Client-side JavaScript (currently empty, students add features here)

## Development Context

This is a student project with step-by-step implementation markers in the code. Key files contain comments indicating what students will build:

- `database/db.py`: Database setup (Step 1)
- `app.py`: Placeholder routes for logout, profile, expense CRUD operations (Steps 3-9)
- `static/js/main.js`: JavaScript features to be added

The app uses SQLite for data storage with foreign key support enabled.
