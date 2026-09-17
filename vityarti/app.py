"""
app.py
CampusBite - Next-Gen Smart Canteen Management System.
Main application factory, Blueprint orchestrator, and web route handlers.
"""

import os
from flask import Flask, render_template, session, redirect, url_for, jsonify, send_from_directory, request
from database import init_db, get_db_connection
from auth import auth_bp, get_current_user
from routes_menu import menu_bp
from routes_order import order_bp
from routes_admin import admin_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.secret_key = os.environ.get("SECRET_KEY", "campusbite_super_secret_session_key_2026")

# Register API blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Explicit static file serving for serverless deployments."""
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)


@app.context_processor
def inject_global_vars():
    """Provides session and user info to all Jinja templates automatically."""
    user = get_current_user()
    return {
        "current_user": user,
        "active_role": session.get("user_role", "student"),
        "app_title": "CampusBite | Smart Canteen POS & Ordering"
    }


def _get_active_menu_items():
    """Helper to safely fetch available items with automatic DB initialization fallback."""
    try:
        conn = get_db_connection()
        items = conn.execute("SELECT * FROM menu_items WHERE is_available = 1").fetchall()
        conn.close()
        return [dict(r) for r in items]
    except Exception as e:
        print(f"Notice during menu fetch: {e}")
        try:
            init_db()
            conn = get_db_connection()
            items = conn.execute("SELECT * FROM menu_items WHERE is_available = 1").fetchall()
            conn.close()
            return [dict(r) for r in items]
        except Exception:
            return []


@app.route("/")
@app.route("/api/index.py")
def index():
    """Main Student/Customer ordering portal with interactive menu & cart."""
    items = _get_active_menu_items()
    return render_template("index.html", initial_items=items)


@app.route("/kitchen")
def kitchen_view():
    """Live Kitchen Display System (KDS) for canteen kitchen staff."""
    return render_template("kitchen.html")


@app.route("/admin")
def admin_view():
    """Management, sales metrics, and inventory dashboard for canteen admin."""
    return render_template("admin.html")


@app.route("/my-orders")
def my_orders_view():
    """Customer order tracking and digital receipt history."""
    return render_template("orders.html")


@app.route("/api/health")
def health():
    """Health check probe."""
    return jsonify({"status": "healthy", "service": "CampusBite", "version": "1.0.0"})


@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": f"API endpoint not found: {request.path}"}), 404
    items = _get_active_menu_items()
    return render_template("index.html", initial_items=items), 404


@app.errorhandler(500)
def handle_500(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error occurred"}), 500
    items = _get_active_menu_items()
    return render_template("index.html", initial_items=items), 500


if __name__ == "__main__":
    # Ensure database is initialized with full schema and seed data
    init_db()
    port = int(os.environ.get("PORT", 5050))
    print(f"🚀 CampusBite Smart Canteen Management System starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
