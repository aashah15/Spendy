import sqlite3
from datetime import datetime
from database.db import get_db

def _build_date_filter(user_id, start_date=None, end_date=None):
    """
    Helper to build the WHERE clause and parameters for date filtering.
    """
    params = [user_id]
    clause = "WHERE user_id = ?"
    if start_date:
        clause += " AND date >= ?"
        params.append(start_date)
    if end_date:
        clause += " AND date <= ?"
        params.append(end_date)
    return clause, params

def get_user_by_id(user_id):
    """
    Fetches a user by their ID and formats the membership date.

    Returns:
        dict: {"name": str, "email": str, "member_since": str} or None
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name, email, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        # created_at is stored as 'YYYY-MM-DD HH:MM:SS' or similar
        # Format to "Month YYYY"
        date_str = row["created_at"]
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            member_since = dt.strftime("%B %Y")
        else:
            member_since = "Unknown"

        return {
            "name": row["name"],
            "email": row["email"],
            "member_since": member_since
        }

    return None

def get_summary_stats(user_id: int, start_date: str = None, end_date: str = None):
    """
    Returns summary stats for the given user, optionally filtered by date range.

    Returns:
        dict: {"total_spent": float, "transaction_count": int, "top_category": str}
    """
    # Handle logical impossibility: start_date > end_date
    if start_date and end_date and start_date > end_date:
        return {"total_spent": 0.0, "transaction_count": 0, "top_category": "—"}

    conn = get_db()
    cursor = conn.cursor()

    where_clause, query_params = _build_date_filter(user_id, start_date, end_date)

    # Total spent and transaction count
    cursor.execute(
        f"SELECT SUM(amount), COUNT(*) FROM expenses {where_clause}",
        tuple(query_params)
    )
    row = cursor.fetchone()
    total_spent = row[0] if row and row[0] else 0.0
    transaction_count = row[1] if row and row[1] else 0

    # Top category
    cursor.execute(
        f"SELECT category FROM expenses {where_clause} GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        tuple(query_params)
    )
    top_cat_row = cursor.fetchone()
    top_category = top_cat_row[0] if top_cat_row else "—"

    conn.close()
    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "top_category": top_category
    }

def get_category_breakdown(user_id: int, start_date: str = None, end_date: str = None):
    """
    Returns a category breakdown for the given user, optionally filtered by date range.

    Returns:
        list: [{"name": str, "amount": float, "pct": int}, ...]
    """
    # Handle logical impossibility: start_date > end_date
    if start_date and end_date and start_date > end_date:
        return []

    conn = get_db()
    cursor = conn.cursor()

    where_clause, query_params = _build_date_filter(user_id, start_date, end_date)

    # Get totals per category
    cursor.execute(
        f"SELECT category, SUM(amount) as total FROM expenses {where_clause} GROUP BY category ORDER BY total DESC",
        tuple(query_params)
    )
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return []

    # Calculate total sum for percentage calculation
    total_sum = sum(row["total"] for row in rows)

    breakdown = []
    sum_pcts = 0

    for row in rows:
        category_total = row["total"]
        # Rounding rule: calculate percentage
        pct = round((category_total / total_sum) * 100) if total_sum > 0 else 0

        breakdown.append({
            "name": row["category"],
            "amount": category_total,
            "pct": pct
        })
        sum_pcts += pct

    # Adjust the largest category (index 0) to absorb the remainder
    remainder = 100 - sum_pcts
    if breakdown:
        breakdown[0]["pct"] += remainder

    conn.close()
    return breakdown

def get_recent_transactions(user_id: int, limit: int = 10, start_date: str = None, end_date: str = None):
    """
    Fetches the most recent transactions for a user, optionally filtered by date range.

    Returns:
        list: A list of dicts containing date, description, category, and amount.
    """
    # Handle logical impossibility: start_date > end_date
    if start_date and end_date and start_date > end_date:
        return []

    conn = get_db()
    cursor = conn.cursor()

    where_clause, query_params = _build_date_filter(user_id, start_date, end_date)

    cursor.execute(
        f"SELECT date, description, category, amount FROM expenses {where_clause} ORDER BY date DESC LIMIT ?",
        tuple(query_params + [limit])
    )
    rows = cursor.fetchall()
    conn.close()

    transactions = []
    for row in rows:
        # Format date from 'YYYY-MM-DD' to 'MMM D, YYYY'
        date_str = row["date"]
        formatted_date = date_str
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = dt.strftime("%b %d, %Y")
            except ValueError:
                pass

        transactions.append({
            "date": formatted_date,
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"]
        })

    return transactions
