"""Unit and integration tests for authentication, Argon2id, and JWT issuance."""

from fastapi.testclient import TestClient
from app.core.security import hash_password, verify_password
from app.models.user import User


def test_argon2_password_hashing():
    """Verify Argon2id hashing and verification logic."""
    pwd = "Secure_Password_123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert hashed.startswith("$argon2id$")
    assert verify_password(pwd, hashed) is True
    assert verify_password("Wrong_Password_123!", hashed) is False


def test_login_success(client: TestClient, admin_user: User):
    """Test successful login returns valid JWT access token."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.internal", "password": "admin_secret_123!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@test.internal"
    assert data["user"]["role"] == "admin"


def test_login_invalid_credentials(client: TestClient, admin_user: User):
    """Test invalid password and nonexistent user rejection."""
    # Wrong password
    res1 = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.internal", "password": "wrong_password!"},
    )
    assert res1.status_code == 401
    assert res1.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # Nonexistent user
    res2 = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.internal", "password": "some_password!"},
    )
    assert res2.status_code == 401


def test_get_current_user_profile(client: TestClient, admin_headers: dict):
    """Test /auth/me returns authenticated caller profile."""
    res = client.get("/api/v1/auth/me", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "admin@test.internal"


def test_admin_create_user(client: TestClient, admin_headers: dict, analyst_headers: dict):
    """Verify only admin can create new users."""
    payload = {
        "email": "newanalyst@test.internal",
        "password": "strong_analyst_password_123!",
        "full_name": "New Analyst",
        "role": "analyst",
    }

    # Unauthorized caller (analyst trying to create user)
    res_forbidden = client.post("/api/v1/auth/users", json=payload, headers=analyst_headers)
    assert res_forbidden.status_code == 403

    # Authorized admin caller
    res_success = client.post("/api/v1/auth/users", json=payload, headers=admin_headers)
    assert res_success.status_code == 201
    assert res_success.json()["email"] == "newanalyst@test.internal"
