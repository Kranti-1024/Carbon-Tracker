from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db, limiter
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def _is_safe_url(target):
    """Ensure redirect target is a relative path on this host."""
    if not target:
        return False
    parsed = urlparse(target)
    return parsed.scheme == '' and parsed.netloc == ''


@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit('10/minute')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in every field.", "error")
            return render_template("auth/signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/signup.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists. Try logging in.", "error")
            return render_template("auth/signup.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome, {name.split()[0]}. Let's log your first activity.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit('10/minute')
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Incorrect email or password.", "error")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        if not _is_safe_url(next_page):
            next_page = None
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("main.landing"))
