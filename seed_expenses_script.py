import sqlite3
import random
from datetime import datetime, timedelta
from database.db import get_db

def seed_expenses(user_id, count, months):
    categories = {
        "Food": {"range": (50, 800), "weight": 30, "desc": ["Dinner at Taj", "Street Food", "Grocery shopping", "Coffee with friends", "Quick snack"]},
        "Transport": {"range": (20, 500), "weight": 20, "desc": ["Uber ride", "Auto rickshaw", "Petrol refill", "Metro card recharge", "Parking fee"]},
        "Bills": {"range": (200, 3000), "weight": 15, "desc": ["Electric bill", "Water bill", "Internet recharge", "Phone bill", "Rent"]},
        "Health": {"range": (100, 2000), "weight": 10, "desc": ["Pharmacy", "Clinic visit", "Medicine", "Health checkup", "Dentist"]},
        "Entertainment": {"range": (100, 1500), "weight": 10, "desc": ["Movie tickets", "Netflix subscription", "Gaming zone", "Concert ticket", "Book purchase"]},
        "Shopping": {"range": (200, 5000), "weight": 10, "desc": ["New clothes", "Electronics", "Home decor", "Shoes", "Amazon order"]},
        "Other": {"range": (50, 1000), "weight": 5, "desc": ["Gift", "Donation", "Miscellaneous", "Stationery", "Laundry"]}
    }

    category_names = list(categories.keys())
    weights = [categories[cat]["weight"] for cat in category_names]

    conn = get_db()
    cursor = conn.cursor()

    try:
        inserted_records = []
        start_date = datetime.now() - timedelta(days=months * 30)
        end_date = datetime.now()

        for _ in range(count):
            cat = random.choices(category_names, weights=weights)[0]
            amount = round(random.uniform(*categories[cat]["range"]), 2)
            description = random.choice(categories[cat]["desc"])

            random_days = random.randint(0, months * 30)
            date_obj = start_date + timedelta(days=random_days)
            date_str = date_obj.strftime("%Y-%m-%d")

            cursor.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, cat, date_str, description)
            )
            inserted_records.append((date_str, description, cat, amount))

        conn.commit()

        dates = [r[0] for r in inserted_records]
        min_date = min(dates)
        max_date = max(dates)

        print(f"Successfully inserted {len(inserted_records)} expenses.")
        print(f"Date range: {min_date} to {max_date}")
        print("\nSample records:")
        for r in inserted_records[:5]:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")

    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_expenses(10, 5, 6)
