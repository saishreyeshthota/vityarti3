"""
tests/test_orders.py
Unit tests for order placement, token creation, wallet balance deductions,
KDS queue flow, and status transitions.
"""

import pytest
import tempfile
import os
from app import app
from database import init_db


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            init_db(db_path)
            import database
            orig_path = database.DEFAULT_DB_PATH
            database.DEFAULT_DB_PATH = db_path

        yield client

        database.DEFAULT_DB_PATH = orig_path
        os.close(db_fd)
        os.unlink(db_path)


def test_place_order_success(client):
    """Verifies that a student can place an order, get a token, and wallet balance is debited."""
    # Authenticate as student (balance ₹450)
    client.post("/api/auth/switch-role", json={"role": "student"})

    order_payload = {
        "items": [
            {"item_id": 1, "quantity": 1},  # Burger combo ₹120
            {"item_id": 3, "quantity": 1}   # Iced coffee ₹95
        ],
        "payment_method": "wallet",
        "special_instructions": "Less ice in coffee"
    }
    response = client.post("/api/orders", json=order_payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["success"] is True
    assert "TK-" in data["order"]["token_number"]
    assert data["order"]["total_amount"] == 215.00
    assert data["new_wallet_balance"] == 450.00 - 215.00


def test_insufficient_wallet_balance(client):
    """Verifies that an order is rejected if the total exceeds user wallet balance."""
    # Set up user as student (balance ₹450)
    client.post("/api/auth/switch-role", json={"role": "student"})

    # Order 5 burgers = ₹600 > ₹450
    order_payload = {
        "items": [{"item_id": 1, "quantity": 5}],
        "payment_method": "wallet"
    }
    response = client.post("/api/orders", json=order_payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data["success"] is False
    assert "Insufficient wallet balance" in data["error"]


def test_order_status_lifecycle(client):
    """Verifies kitchen can progress an order: pending -> preparing -> ready -> completed."""
    # Place an order as student
    client.post("/api/auth/switch-role", json={"role": "student"})
    order_res = client.post("/api/orders", json={"items": [{"item_id": 2, "quantity": 1}]})
    order_id = order_res.get_json()["order"]["id"]

    # Kitchen staff updates to 'preparing'
    p_res = client.patch(f"/api/orders/{order_id}/status", json={"status": "preparing"})
    assert p_res.get_json()["new_status"] == "preparing"

    # Kitchen staff updates to 'ready'
    r_res = client.patch(f"/api/orders/{order_id}/status", json={"status": "ready"})
    assert r_res.get_json()["new_status"] == "ready"

    # Staff hands over order -> 'completed'
    c_res = client.patch(f"/api/orders/{order_id}/status", json={"status": "completed"})
    assert c_res.get_json()["new_status"] == "completed"


def test_wallet_topup(client):
    """Verifies that student can recharge their digital wallet."""
    client.post("/api/auth/switch-role", json={"role": "student"})
    response = client.post("/api/wallet/topup", json={"amount": 200})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["wallet_balance"] == 650.00  # 450 + 200
