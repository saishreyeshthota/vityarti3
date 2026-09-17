"""
tests/test_menu.py
Unit tests for menu items catalog, filtering, search, and stock updates.
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


def test_get_menu_items(client):
    """Verifies that the menu API returns the seeded catalog."""
    response = client.get("/api/menu")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["count"] >= 12
    assert any(item["name"] == "Royal Mysore Masala Dosa" for item in data["items"])


def test_category_filter(client):
    """Verifies that filtering by category returns only items in that category."""
    response = client.get("/api/menu?category=Beverages")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    for item in data["items"]:
        assert item["category"] == "Beverages"


def test_dietary_filter(client):
    """Verifies that filtering by dietary type works correctly."""
    response = client.get("/api/menu?dietary=vegan")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    for item in data["items"]:
        assert item["dietary_type"] == "vegan"


def test_search_menu(client):
    """Verifies that text search matches dish names or descriptions."""
    response = client.get("/api/menu?search=Burger")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert any("Burger" in item["name"] for item in data["items"])


def test_toggle_stock_staff(client):
    """Verifies that staff/admin can toggle availability status."""
    # Switch to staff persona
    client.post("/api/auth/switch-role", json={"role": "staff"})

    # Toggle stock of item #1
    response = client.patch("/api/menu/1/toggle-stock")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "is_available" in data
