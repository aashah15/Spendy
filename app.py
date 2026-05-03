from flask import Flask, render_template, request, flash, redirect, url_for, session
from database.db import init_db, seed_db, create_user, get_user_by_email
from database.queries import get_user_by_id, get_recent_transactions, get_summary_stats, get_category_breakdown
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "spendly-secret-key-change-in-production"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Redirect if already logged in
    if session.get("user_id"):
        flash("You are already logged in", "info")
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate inputs
        error = None

        if not name:
            error = "Name is required"
        elif not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"
        elif len(password) < 8:
            error = "Password must be at least 8 characters"
        elif password != confirm_password:
            error = "Passwords do not match"

        if error:
            return render_template("register.html", error=error)

        # Try to create the user
        try:
            create_user(name, email, password)
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception:
            # Catch duplicate email (sqlite3.IntegrityError)
            return render_template("register.html", error="Email already registered")

    # GET request - display the form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect if already logged in
    if session.get("user_id"):
        flash("You are already logged in", "info")
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Extract form data
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validate inputs
        error = None

        if not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"

        if error:
            return render_template("login.html", error=error)

        # Try to authenticate the user
        user = get_user_by_email(email)

        if user is None:
            return render_template("login.html", error="Invalid email or password")

        # Verify password
        if not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password")

        # Successful login - store user_id in session
        session["user_id"] = user["id"]
        flash("Welcome back!", "success")
        return redirect(url_for("landing"))

    # GET request - display the form
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    # Auth guard - redirect if not logged in
    if not session.get("user_id"):
        flash("Please log in to view your profile", "info")
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    # Get real user data from database
    user = get_user_by_id(user_id)
    if not user:
        flash("User profile not found", "error")
        return redirect(url_for("login"))

    # Summary stats from database
    stats = get_summary_stats(user_id)

    # Hardcoded transaction history
    transactions = get_recent_transactions(user_id)

    # Category breakdown from database
    categories = get_category_breakdown(user_id)

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
