import sqlite3
from datetime import datetime
from database.db import get_db

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

def get_summary_stats(user_id: int):
    """
    Returns summary stats for the given user.

    Returns:
        dict: {"total_spent": float, "transaction_count": int, "top_category": str}
    """
    conn = get_db()
    cursor = conn.cursor()

    # Total spent and transaction count
    cursor.execute(
        "SELECT SUM(amount), COUNT(*) FROM expenses WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    total_spent = row[0] if row and row[0] else 0.0
    transaction_count = row[1] if row and row[1] else 0

    # Top category
    cursor.execute(
        "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        (user_id,)
    )
    top_cat_row = cursor.fetchone()
    top_category = top_cat_row[0] if top_cat_row else "—"

    conn.close()
    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "top_category": top_category
    }

def get_category_breakdown(user_id: int):
    """
    Returns a category breakdown for the given user.

    Returns:
        list: [{"name": str, "amount": float, "pct": int}, ...]
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get totals per category
    cursor.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,)
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

def get_recent_transactions(user_id: int, limit: int = 10):
    """
    Fetches the most recent transactions for a user.

    Returns:
        list: A list of dicts containing date, description, category, and amount.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
        (user_id, limit)
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
