"""
routes_menu.py
API endpoints for menu item retrieval, searching, category & dietary filtering,
and administrator CRUD operations.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from database import get_db_connection
from auth import login_required, role_required
from models import MenuItem

menu_bp = Blueprint("menu", __name__, url_prefix="/api/menu")


@menu_bp.route("", methods=["GET"])
def get_menu_items():
    """
    Retrieves menu items with optional filtering by:
    - category (Breakfast, Lunch, Snacks, Beverages, Healthy)
    - dietary (veg, non-veg, vegan)
    - search (substring match on name or description)
    - available_only (1/true)
    """
    category = request.args.get("category", "all")
    dietary = request.args.get("dietary", "all")
    search_query = request.args.get("search", "").strip()
    available_only = request.args.get("available_only", "0") == "1"

    query = "SELECT * FROM menu_items WHERE 1=1"
    params = []

    if category and category.lower() != "all":
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)

    if dietary and dietary.lower() != "all":
        query += " AND LOWER(dietary_type) = LOWER(?)"
        params.append(dietary)

    if available_only:
        query += " AND is_available = 1 AND stock_quantity > 0"

    if search_query:
        query += " AND (name LIKE ? OR description LIKE ?)"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard])

    query += " ORDER BY category ASC, name ASC"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    items = [dict(r) for r in rows]
    return jsonify({"success": True, "count": len(items), "items": items})


@menu_bp.route("/<int:item_id>", methods=["GET"])
def get_single_menu_item(item_id):
    """Fetches details for a specific menu item."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "Item not found"}), 404
    return jsonify({"success": True, "item": dict(row)})


@menu_bp.route("", methods=["POST"])
@login_required
@role_required(["admin"])
def create_menu_item():
    """Creates a new menu item (Admin role required)."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    category = data.get("category", "Snacks").strip()
    description = data.get("description", "").strip()
    price = data.get("price")
    stock_quantity = data.get("stock_quantity", 50)
    dietary_type = data.get("dietary_type", "veg")
    image_url = data.get("image_url", "/static/images/burger.jpg")
    prep_time = data.get("prep_time_minutes", 10)
    calories = data.get("calories", 300)

    if not name or price is None:
        return jsonify({"success": False, "error": "Name and price are required"}), 400

    try:
        price = float(price)
        if price <= 0:
            return jsonify({"success": False, "error": "Price must be positive"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Invalid price format"}), 400

    now_str = datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO menu_items (name, category, description, price, is_available, stock_quantity, dietary_type, image_url, prep_time_minutes, calories, rating, created_at)
    VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, 5.0, ?)
    """, (name, category, description, price, int(stock_quantity), dietary_type, image_url, int(prep_time), int(calories), now_str))
    new_id = cursor.lastrowid
    conn.commit()

    row = conn.execute("SELECT * FROM menu_items WHERE id = ?", (new_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Menu item created successfully", "item": dict(row)}), 201


@menu_bp.route("/<int:item_id>", methods=["PUT"])
@login_required
@role_required(["admin"])
def update_menu_item(item_id):
    """Updates an existing menu item (Admin role required)."""
    data = request.get_json(silent=True) or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"success": False, "error": "Menu item not found"}), 404

    name = data.get("name", existing["name"]).strip()
    category = data.get("category", existing["category"]).strip()
    description = data.get("description", existing["description"]).strip()
    price = float(data.get("price", existing["price"]))
    is_available = int(data.get("is_available", existing["is_available"]))
    stock_quantity = int(data.get("stock_quantity", existing["stock_quantity"]))
    dietary_type = data.get("dietary_type", existing["dietary_type"])
    image_url = data.get("image_url", existing["image_url"])
    prep_time = int(data.get("prep_time_minutes", existing["prep_time_minutes"]))
    calories = int(data.get("calories", existing["calories"]))

    conn.execute("""
    UPDATE menu_items
    SET name=?, category=?, description=?, price=?, is_available=?, stock_quantity=?, dietary_type=?, image_url=?, prep_time_minutes=?, calories=?
    WHERE id=?
    """, (name, category, description, price, is_available, stock_quantity, dietary_type, image_url, prep_time, calories, item_id))
    conn.commit()

    updated = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Item updated successfully", "item": dict(updated)})


@menu_bp.route("/<int:item_id>", methods=["DELETE"])
@login_required
@role_required(["admin"])
def delete_menu_item(item_id):
    """Deletes a menu item (Admin role required)."""
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"success": False, "error": "Item not found"}), 404

    conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Item deleted successfully"})


@menu_bp.route("/<int:item_id>/toggle-stock", methods=["PATCH"])
@login_required
@role_required(["staff", "admin"])
def toggle_stock(item_id):
    """Toggles availability on/off for kitchen or admin staff."""
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"success": False, "error": "Item not found"}), 404

    new_status = 0 if existing["is_available"] else 1
    conn.execute("UPDATE menu_items SET is_available = ? WHERE id = ?", (new_status, item_id))
    conn.commit()
    conn.close()

    status_text = "In Stock" if new_status else "Out of Stock"
    return jsonify({"success": True, "message": f"Item marked as {status_text}", "is_available": new_status})
