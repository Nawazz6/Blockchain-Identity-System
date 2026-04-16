import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from utils.db_utils import get_db_connection
from utils.hash_utils import generate_sha256
from utils.encryption_utils import encrypt_file
from blockchain.blockchain_utils import store_hash_on_blockchain

user_bp = Blueprint("user", __name__)

@user_bp.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    aadhaar_record = conn.execute(
        "SELECT * FROM aadhaar_records WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (session["user_id"],)
    ).fetchone()

    requests = conn.execute(
        "SELECT * FROM bank_requests WHERE target_user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "user_dashboard.html",
        user_id=session.get("user_id"),
        user_name=session.get("user_name"),
        aadhaar_record=aadhaar_record,
        requests=requests
    )


@user_bp.route("/user/upload-aadhaar", methods=["POST"])
def upload_aadhaar():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    aadhaar_number = request.form.get("aadhaar_number", "").strip()
    uploaded_file = request.files.get("aadhaar_file")

    if not aadhaar_number:
        flash("Please enter Aadhaar number.", "error")
        return redirect(url_for("user.user_dashboard"))

    if not uploaded_file or uploaded_file.filename == "":
        flash("Please upload an Aadhaar file.", "error")
        return redirect(url_for("user.user_dashboard"))

    original_filename = secure_filename(uploaded_file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    encrypted_folder = current_app.config["ENCRYPTED_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(encrypted_folder, exist_ok=True)

    saved_filename = f"{session['user_id']}_{original_filename}"
    saved_file_path = os.path.join(upload_folder, saved_filename)

    uploaded_file.save(saved_file_path)

    sha256_hash = generate_sha256(saved_file_path)

    encrypted_filename = f"enc_{session['user_id']}_{original_filename}.bin"
    encrypted_file_path = os.path.join(encrypted_folder, encrypted_filename)
    encrypt_file(saved_file_path, encrypted_file_path)

    try:
        blockchain_txn_hash = store_hash_on_blockchain(sha256_hash)
    except Exception as e:
        flash(f"Blockchain storage failed: {str(e)}", "error")
        return redirect(url_for("user.user_dashboard"))

    conn = get_db_connection()

    uidai_match = conn.execute(
        "SELECT * FROM mock_uidai WHERE aadhaar_number = ?",
        (aadhaar_number,)
    ).fetchone()

    uidai_verified = 1 if uidai_match else 0

    existing_record = conn.execute(
        "SELECT * FROM aadhaar_records WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if existing_record:
        conn.execute("""
            UPDATE aadhaar_records
            SET aadhaar_number = ?, original_filename = ?, encrypted_filename = ?,
                sha256_hash = ?, blockchain_txn_hash = ?, uidai_verified = ?
            WHERE user_id = ?
        """, (
            aadhaar_number,
            original_filename,
            encrypted_filename,
            sha256_hash,
            blockchain_txn_hash,
            uidai_verified,
            session["user_id"]
        ))
    else:
        conn.execute("""
            INSERT INTO aadhaar_records (
                user_id, aadhaar_number, original_filename, encrypted_filename,
                sha256_hash, blockchain_txn_hash, uidai_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            aadhaar_number,
            original_filename,
            encrypted_filename,
            sha256_hash,
            blockchain_txn_hash,
            uidai_verified
        ))

    conn.commit()
    conn.close()

    if uidai_verified:
        flash("Aadhaar uploaded, encrypted, hashed, stored on blockchain, and UIDAI verified successfully.", "success")
    else:
        flash("Aadhaar uploaded, encrypted, hashed, and stored on blockchain, but UIDAI verification failed.", "error")

    return redirect(url_for("user.user_dashboard"))


@user_bp.route("/user/request-action/<int:request_id>/<action>")
def request_action(request_id, action):
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    if action not in ["approve", "reject"]:
        flash("Invalid action.", "error")
        return redirect(url_for("user.user_dashboard"))

    new_status = "Approved" if action == "approve" else "Rejected"

    conn = get_db_connection()

    req = conn.execute(
        "SELECT * FROM bank_requests WHERE id = ? AND target_user_id = ?",
        (request_id, session["user_id"])
    ).fetchone()

    if not req:
        conn.close()
        flash("Request not found.", "error")
        return redirect(url_for("user.user_dashboard"))

    conn.execute(
        "UPDATE bank_requests SET status = ? WHERE id = ?",
        (new_status, request_id)
    )
    conn.commit()
    conn.close()

    flash(f"Request {new_status.lower()} successfully.", "success")
    return redirect(url_for("user.user_dashboard"))