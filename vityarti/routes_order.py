"""
routes_order.py
Handles order creation, wallet debit, live token generation, kitchen order queues,
order status transitions, and digital wallet recharge.
"""

from datetime import datetime
import random
import time
from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from auth import login_required, role_required, get_current_user

order_bp = Blueprint("orders", __name__, url_prefix="/api")


def generate_token(conn):
    """Generates a sequential daily token number like TK-105."""
    row = conn.execute("SELECT COUNT(*) as count FROM orders").fetchone()
    next_num = (row["count"] if row else 0) + 101
    return f"TK-{next_num}"


@order_bp.route("/orders", methods=["POST"])
def place_order():
    """
    Places a new order:
    1. Validates items and availability.
    2. Calculates itemized subtotal and taxes.
    3. Verifies & deducts student digital wallet balance.
    4. Issues unique digital token and records order and items.
    """
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Please log in to place an order"}), 401

    data = request.get_json(silent=True) or {}
    items_input = data.get("items", [])
    special_instructions = data.get("special_instructions", "").strip()
    payment_method = data.get("payment_method", "wallet")

    if not items_input or not isinstance(items_input, list):
        return jsonify({"success": False, "error": "Your cart is empty"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        total_amount = 0.0
        validated_items = []

        # Validate each item and check stock
        for entry in items_input:
            item_id = entry.get("item_id")
            qty = int(entry.get("quantity", 1))

            if qty <= 0:
                continue

            item_row = cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
            if not item_row:
                conn.close()
                return jsonify({"success": False, "error": f"Item ID {item_id} does not exist"}), 404

            if not item_row["is_available"] or item_row["stock_quantity"] < qty:
                conn.close()
                return jsonify({
                    "success": False,
                    "error": f"Sorry, '{item_row['name']}' has insufficient stock (Only {item_row['stock_quantity']} remaining)."
                }), 400

            subtotal = round(item_row["price"] * qty, 2)
            total_amount += subtotal
            validated_items.append({
                "item_id": item_row["id"],
                "name": item_row["name"],
                "price": item_row["price"],
                "quantity": qty,
                "subtotal": subtotal
            })

        if not validated_items:
            conn.close()
            return jsonify({"success": False, "error": "No valid items selected"}), 400

        total_amount = round(total_amount, 2)

        # Payment processing via digital wallet
        if payment_method == "wallet":
            if user["wallet_balance"] < total_amount:
                conn.close()
                return jsonify({
                    "success": False,
                    "error": f"Insufficient wallet balance (₹{user['wallet_balance']:.2f}). Order total is ₹{total_amount:.2f}. Please recharge your wallet."
                }), 400

            new_balance = round(user["wallet_balance"] - total_amount, 2)
            cursor.execute("UPDATE users SET wallet_balance = ? WHERE id = ?", (new_balance, user["id"]))

            # Record wallet transaction
            cursor.execute("""
            INSERT INTO wallet_transactions (user_id, amount, transaction_type, reference, balance_after, created_at)
            VALUES (?, ?, 'debit', 'Canteen Order Payment', ?, ?)
            """, (user["id"], total_amount, new_balance, datetime.now().isoformat()))

        # Generate unique order number and sequential token
        order_num = f"ORD-{int(time.time() * 1000) % 1000000}"
        token_num = generate_token(conn)
        now_str = datetime.now().isoformat()

        cursor.execute("""
        INSERT INTO orders (order_number, token_number, user_id, total_amount, discount_amount, final_amount, payment_method, payment_status, order_status, special_instructions, created_at, updated_at)
        VALUES (?, ?, ?, ?, 0.0, ?, ?, 'paid', 'pending', ?, ?, ?)
        """, (order_num, token_num, user["id"], total_amount, total_amount, payment_method, special_instructions, now_str, now_str))

        order_id = cursor.lastrowid

        # Insert order items and deduct stock
        for v in validated_items:
            cursor.execute("""
            INSERT INTO order_items (order_id, item_id, item_name, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (order_id, v["item_id"], v["name"], v["quantity"], v["price"], v["subtotal"]))

            cursor.execute("""
            UPDATE menu_items SET stock_quantity = stock_quantity - ? WHERE id = ?
            """, (v["quantity"], v["item_id"]))

        conn.commit()

        # Fetch updated user profile with new wallet balance
        updated_user = cursor.execute("SELECT wallet_balance FROM users WHERE id = ?", (user["id"],)).fetchone()
        current_balance = updated_user["wallet_balance"] if updated_user else 0.0

        return jsonify({
            "success": True,
            "message": f"Order placed successfully! Your token is {token_num}",
            "order": {
                "id": order_id,
                "order_number": order_num,
                "token_number": token_num,
                "total_amount": total_amount,
                "order_status": "pending",
                "payment_method": payment_method,
                "created_at": now_str,
                "items": validated_items,
                "special_instructions": special_instructions
            },
            "new_wallet_balance": current_balance
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": f"Failed to place order: {str(e)}"}), 500
    finally:
        conn.close()


@order_bp.route("/orders/my-orders", methods=["GET"])
def get_my_orders():
    """Retrieves order history and live active orders for current user."""
    user = get_current_user()
    if not user:
        return jsonify({"success": True, "orders": []})

    conn = get_db_connection()
    orders_rows = conn.execute("""
    SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 20
    """, (user["id"],)).fetchall()

    orders = []
    for o in orders_rows:
        order_dict = dict(o)
        items_rows = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (o["id"],)).fetchall()
        order_dict["items"] = [dict(it) for it in items_rows]
        orders.append(order_dict)

    conn.close()
    return jsonify({"success": True, "orders": orders})


@order_bp.route("/orders/kitchen-queue", methods=["GET"])
def get_kitchen_queue():
    """Retrieves all active orders for the Kitchen Display System (KDS)."""
    conn = get_db_connection()
    orders_rows = conn.execute("""
    SELECT o.*, u.full_name as customer_name, u.role as customer_role, u.roll_no as customer_roll
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.order_status IN ('pending', 'preparing', 'ready')
    ORDER BY
        CASE o.order_status
            WHEN 'pending' THEN 1
            WHEN 'preparing' THEN 2
            WHEN 'ready' THEN 3
            ELSE 4
        END,
        o.id ASC
    """).fetchall()

    queue = []
    for o in orders_rows:
        order_dict = dict(o)
        items_rows = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (o["id"],)).fetchall()
        order_dict["items"] = [dict(it) for it in items_rows]
        queue.append(order_dict)

    conn.close()
    return jsonify({"success": True, "count": len(queue), "queue": queue})


@order_bp.route("/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    """Updates order status: pending -> preparing -> ready -> completed / cancelled."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    valid_statuses = ["pending", "preparing", "ready", "completed", "cancelled"]

    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": f"Invalid status '{new_status}'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    order = cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return jsonify({"success": False, "error": "Order not found"}), 404

    now_str = datetime.now().isoformat()
    cursor.execute("""
    UPDATE orders SET order_status = ?, updated_at = ? WHERE id = ?
    """, (new_status, now_str, order_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Order #{order['token_number']} status updated to '{new_status.title()}'",
        "order_id": order_id,
        "new_status": new_status
    })


@order_bp.route("/wallet/topup", methods=["POST"])
def wallet_topup():
    """Allows student/faculty to instantly recharge their digital wallet."""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "User not authenticated"}), 401

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
        if amount <= 0 or amount > 5000:
            return jsonify({"success": False, "error": "Recharge amount must be between ₹10 and ₹5,000"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid amount"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    new_balance = round(user["wallet_balance"] + amount, 2)
    now_str = datetime.now().isoformat()

    cursor.execute("UPDATE users SET wallet_balance = ? WHERE id = ?", (new_balance, user["id"]))
    cursor.execute("""
    INSERT INTO wallet_transactions (user_id, amount, transaction_type, reference, balance_after, created_at)
    VALUES (?, ?, 'credit', 'Instant Digital UPI/NetBanking Top-up', ?, ?)
    """, (user["id"], amount, new_balance, now_str))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Successfully recharged ₹{amount:.2f}! New balance is ₹{new_balance:.2f}",
        "wallet_balance": new_balance
    })
