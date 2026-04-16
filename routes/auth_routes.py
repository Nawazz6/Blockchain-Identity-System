from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.otp_utils import generate_otp
from utils.userid_utils import generate_user_id
from utils.db_utils import get_db_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        entered_otp = request.form.get("entered_otp", "").strip()
        generated_otp = request.form.get("generated_otp", "").strip()

        if entered_otp != generated_otp:
            flash("Invalid OTP. Please try again.", "error")
            return render_template(
                "register.html",
                demo_otp=generated_otp,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        existing_user = cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("auth.login"))

        user_id = generate_user_id()

        while cursor.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone():
            user_id = generate_user_id()

        cursor.execute("""
            INSERT INTO users (
                first_name, last_name, email, phone, password, user_id, otp, otp_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, password, user_id, generated_otp, 1))

        conn.commit()
        conn.close()

        flash(f"Registration successful. Your User ID is {user_id}", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/generate-otp", methods=["POST"])
def generate_otp_route():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "").strip()

    demo_otp = generate_otp()

    return render_template(
        "register.html",
        demo_otp=demo_otp,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE user_id = ? AND password = ?",
            (user_id, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["first_name"]
            flash("Login successful.", "success")
            return redirect(url_for("user.user_dashboard"))
        else:
            flash("Invalid User ID or Password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("landing"))