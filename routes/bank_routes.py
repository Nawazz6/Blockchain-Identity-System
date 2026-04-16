from flask import Blueprint, render_template, request, flash, redirect, url_for
from utils.db_utils import get_db_connection

bank_bp = Blueprint("bank", __name__)

@bank_bp.route("/bank", methods=["GET", "POST"])
def bank_portal():
    user = None
    latest_request = None
    aadhaar_record = None
    identity_verified = False
    verification_message = None

    searched_user_id = ""
    bank_name = ""

    # ✅ HANDLE POST (only actions)
    if request.method == "POST":
        action = request.form.get("action", "").strip()
        searched_user_id = request.form.get("target_user_id", "").strip()
        bank_name = request.form.get("bank_name", "").strip()

        conn = get_db_connection()

        if not searched_user_id:
            conn.close()
            flash("Please enter User ID.", "error")
            return redirect(url_for("bank.bank_portal"))

        user = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (searched_user_id,)
        ).fetchone()

        if not user:
            conn.close()
            flash("User ID not found.", "error")
            return redirect(url_for("bank.bank_portal"))

        if action == "send_request":
            if not bank_name:
                conn.close()
                flash("Please enter organization or bank name.", "error")
                return redirect(url_for("bank.bank_portal"))

            existing_pending = conn.execute(
                """
                SELECT * FROM bank_requests
                WHERE target_user_id = ? AND bank_name = ? AND status = 'Pending'
                ORDER BY id DESC LIMIT 1
                """,
                (searched_user_id, bank_name)
            ).fetchone()

            if existing_pending:
                flash("A pending request already exists for this user.", "error")
            else:
                conn.execute(
                    """
                    INSERT INTO bank_requests (bank_name, target_user_id, status)
                    VALUES (?, ?, ?)
                    """,
                    (bank_name, searched_user_id, "Pending")
                )
                conn.commit()
                flash("Request sent successfully.", "success")

        conn.close()

        # 🔥 IMPORTANT FIX: redirect after POST
        return redirect(url_for("bank.bank_portal", user_id=searched_user_id, bank_name=bank_name))

    # ✅ HANDLE GET (fetch fresh data)
    searched_user_id = request.args.get("user_id", "")
    bank_name = request.args.get("bank_name", "")

    if searched_user_id:
        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (searched_user_id,)
        ).fetchone()

        aadhaar_record = conn.execute(
            "SELECT * FROM aadhaar_records WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (searched_user_id,)
        ).fetchone()

        if bank_name:
            latest_request = conn.execute(
                """
                SELECT * FROM bank_requests
                WHERE target_user_id = ? AND bank_name = ?
                ORDER BY id DESC LIMIT 1
                """,
                (searched_user_id, bank_name)
            ).fetchone()
        else:
            latest_request = conn.execute(
                """
                SELECT * FROM bank_requests
                WHERE target_user_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (searched_user_id,)
            ).fetchone()

        # same logic
        if latest_request:
            if latest_request["status"] == "Approved":
                if aadhaar_record and aadhaar_record["uidai_verified"] == 1:
                    identity_verified = True
                    verification_message = "User approved the request and Aadhaar is UIDAI verified."
                elif aadhaar_record and aadhaar_record["uidai_verified"] == 0:
                    verification_message = "Request approved, but Aadhaar is not UIDAI verified."
                else:
                    verification_message = "Request approved, but Aadhaar record is not available."
            elif latest_request["status"] == "Rejected":
                verification_message = "Request was rejected by the user."
            elif latest_request["status"] == "Pending":
                verification_message = "Request sent. Waiting for user approval."
        else:
            if aadhaar_record:
                if aadhaar_record["uidai_verified"] == 1:
                    verification_message = "User found. Aadhaar is uploaded and UIDAI verified."
                else:
                    verification_message = "User found. Aadhaar is uploaded but not UIDAI verified."
            else:
                verification_message = "User found. No Aadhaar uploaded yet."

        conn.close()

    return render_template(
        "bank_portal.html",
        user=user,
        latest_request=latest_request,
        aadhaar_record=aadhaar_record,
        identity_verified=identity_verified,
       
        verification_message=verification_message,
        searched_user_id=searched_user_id,
        bank_name=bank_name
    )