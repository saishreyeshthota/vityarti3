"""
auth.py
Authentication routines, session helpers, password verification, and role-based access
control (RBAC) decorators for the CampusBite Canteen Management System.
"""

from functools import wraps
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def login_required(f):
    """Decorator requiring an active user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    """Decorator requiring a specific user role (e.g. ['admin'], ['staff', 'admin'])."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                return jsonify({"success": False, "error": "Forbidden: Insufficient privileges"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """Fetches full record of the currently logged-in session user."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates a user via username/email and password."""
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier", "").strip().lower()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"success": False, "error": "Identifier and password are required"}), 400

    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?",
        (identifier, identifier)
    ).fetchone()
    conn.close()

    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    session["user_id"] = row["id"]
    session["username"] = row["username"]
    session["user_name"] = row["full_name"]
    session["user_role"] = row["role"]

    user_dict = dict(row)
    del user_dict["password_hash"]

    return jsonify({
        "success": True,
        "message": f"Welcome back, {row['full_name']}!",
        "user": user_dict
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Terminates the current user session."""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
def me():
    """Returns the current user profile including live wallet balance."""
    user = get_current_user()
    if not user:
        # Fallback to default demo student if session is fresh
        conn = get_db_connection()
        default_user = conn.execute("SELECT * FROM users WHERE role = 'student' LIMIT 1").fetchone()
        conn.close()
        if default_user:
            session["user_id"] = default_user["id"]
            session["username"] = default_user["username"]
            session["user_name"] = default_user["full_name"]
            session["user_role"] = default_user["role"]
            user = dict(default_user)

    if user and "password_hash" in user:
        del user["password_hash"]

    return jsonify({"success": True, "user": user})


@auth_bp.route("/switch-role", methods=["POST"])
def switch_role():
    """
    Demo/Evaluator feature: Allows switching between roles with one click
    (student, faculty, staff, admin) for seamless demonstration and evaluation.
    """
    data = request.get_json(silent=True) or {}
    target_role = data.get("role", "student").lower()

    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE role = ? LIMIT 1", (target_role,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "error": f"No user with role '{target_role}' found"}), 404

    session["user_id"] = row["id"]
    session["username"] = row["username"]
    session["user_name"] = row["full_name"]
    session["user_role"] = row["role"]

    user_dict = dict(row)
    del user_dict["password_hash"]

    return jsonify({
        "success": True,
        "message": f"Switched active persona to {row['full_name']} ({row['role'].title()})",
        "user": user_dict
    })
