"""
routes_admin.py
Provides comprehensive canteen administration, sales analytics, top-seller tracking,
low-stock monitoring, and CSV report export for auditing.
"""

import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from database import get_db_connection
from auth import login_required, role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """
    Computes real-time canteen operational metrics:
    - Total gross revenue and total completed/paid orders
    - Active kitchen orders count (pending, preparing, ready)
    - Average Order Value (AOV)
    - Top 5 selling items by quantity
    - Revenue distribution by category
    - Stock inventory warning alerts
    """
    conn = get_db_connection()

    # 1. High level KPI totals
    kpi = conn.execute("""
    SELECT 
        COUNT(CASE WHEN order_status != 'cancelled' THEN 1 END) as total_orders,
        COALESCE(SUM(CASE WHEN order_status != 'cancelled' THEN final_amount ELSE 0 END), 0.0) as total_revenue,
        COUNT(CASE WHEN order_status IN ('pending', 'preparing', 'ready') THEN 1 END) as active_orders,
        COUNT(CASE WHEN order_status = 'completed' THEN 1 END) as completed_orders
    FROM orders
    """).fetchone()

    total_orders = kpi["total_orders"]
    total_revenue = round(kpi["total_revenue"], 2)
    active_orders = kpi["active_orders"]
    completed_orders = kpi["completed_orders"]
    avg_order_value = round((total_revenue / total_orders), 2) if total_orders > 0 else 0.0

    # 2. Top 5 selling items
    top_items_rows = conn.execute("""
    SELECT 
        oi.item_name,
        SUM(oi.quantity) as total_quantity,
        SUM(oi.subtotal) as total_sales,
        m.category,
        m.image_url
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    LEFT JOIN menu_items m ON oi.item_id = m.id
    WHERE o.order_status != 'cancelled'
    GROUP BY oi.item_name
    ORDER BY total_quantity DESC
    LIMIT 5
    """).fetchall()

    top_items = [dict(r) for r in top_items_rows]

    # 3. Category distribution
    cat_rows = conn.execute("""
    SELECT 
        COALESCE(m.category, 'Other') as category,
        COUNT(oi.id) as item_orders_count,
        SUM(oi.quantity) as total_qty,
        COALESCE(SUM(oi.subtotal), 0.0) as total_sales
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    LEFT JOIN menu_items m ON oi.item_id = m.id
    WHERE o.order_status != 'cancelled'
    GROUP BY m.category
    ORDER BY total_sales DESC
    """).fetchall()

    category_stats = [dict(r) for r in cat_rows]

    # 4. Low stock inventory alerts
    low_stock_rows = conn.execute("""
    SELECT id, name, category, stock_quantity, price, is_available
    FROM menu_items
    WHERE stock_quantity <= 35 OR is_available = 0
    ORDER BY stock_quantity ASC
    """).fetchall()

    low_stock = [dict(r) for r in low_stock_rows]

    # 5. Recent orders list with customer names
    recent_orders_rows = conn.execute("""
    SELECT o.*, u.full_name as customer_name, u.role as customer_role
    FROM orders o
    JOIN users u ON o.user_id = u.id
    ORDER BY o.id DESC
    LIMIT 10
    """).fetchall()

    recent_orders = [dict(r) for r in recent_orders_rows]

    conn.close()

    return jsonify({
        "success": True,
        "metrics": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "avg_order_value": avg_order_value,
        },
        "top_items": top_items,
        "category_stats": category_stats,
        "low_stock": low_stock,
        "recent_orders": recent_orders
    })


@admin_bp.route("/export-csv", methods=["GET"])
def export_csv():
    """Generates and downloads a complete CSV audit report of all canteen orders."""
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT 
        o.order_number,
        o.token_number,
        u.full_name as customer_name,
        u.role as customer_role,
        u.roll_no as roll_or_id,
        o.total_amount,
        o.order_status,
        o.payment_method,
        o.payment_status,
        o.created_at
    FROM orders o
    JOIN users u ON o.user_id = u.id
    ORDER BY o.id DESC
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Order Number",
        "Token Number",
        "Customer Name",
        "Role",
        "Roll/ID",
        "Total Amount (INR)",
        "Order Status",
        "Payment Method",
        "Payment Status",
        "Timestamp"
    ])

    for r in rows:
        writer.writerow([
            r["order_number"],
            r["token_number"],
            r["customer_name"],
            r["customer_role"],
            r["roll_or_id"] or "N/A",
            f"{r['total_amount']:.2f}",
            r["order_status"].title(),
            r["payment_method"].upper(),
            r["payment_status"].title(),
            r["created_at"]
        ])

    csv_data = output.getvalue()
    filename = f"canteen_orders_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
