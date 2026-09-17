"""
tests/test_auth.py
Unit tests for user authentication, role switching, session handling, and RBAC guards.
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
            # Patch default db path for test run
            import database
            orig_path = database.DEFAULT_DB_PATH
            database.DEFAULT_DB_PATH = db_path

        yield client

        # Teardown
        database.DEFAULT_DB_PATH = orig_path
        os.close(db_fd)
        os.unlink(db_path)


def test_login_success(client):
    """Verifies that a registered student can authenticate with valid credentials."""
    response = client.post("/api/auth/login", json={
        "identifier": "student@campus.edu",
        "password": "password123"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["user"]["username"] == "aarav"
    assert data["user"]["role"] == "student"


def test_login_invalid_password(client):
    """Verifies that login fails when given incorrect password."""
    response = client.post("/api/auth/login", json={
        "identifier": "student@campus.edu",
        "password": "wrongpassword"
    })
    data = response.get_json()
    assert response.status_code == 401
    assert data["success"] is False
    assert "Invalid credentials" in data["error"]


def test_demo_role_switcher(client):
    """Verifies that the demo role-switcher can switch active persona to faculty or admin."""
    response = client.post("/api/auth/switch-role", json={"role": "admin"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["user"]["role"] == "admin"

    # Verify /api/auth/me returns current persona
    me_resp = client.get("/api/auth/me")
    me_data = me_resp.get_json()
    assert me_data["user"]["role"] == "admin"
