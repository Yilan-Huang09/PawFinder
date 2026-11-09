from __future__ import annotations


def test_register_login_and_read_current_user(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "new_owner",
            "password": "SecurePass123!",
            "phone": "13900000001",
            "email": "owner@example.com",
        },
    )

    assert register_response.status_code == 201
    register_data = register_response.get_json()["data"]
    assert register_data["user"]["username"] == "new_owner"
    assert register_data["user"]["role"] == "USER"
    assert "password_hash" not in register_data["user"]
    assert register_data["access_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "new_owner", "password": "SecurePass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["data"]["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.get_json()["data"]["username"] == "new_owner"


def test_registration_rejects_duplicate_username_and_invalid_password(client):
    payload = {"username": "duplicate", "password": "SecurePass123!"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    duplicate_response = client.post("/api/v1/auth/register", json=payload)
    assert duplicate_response.status_code == 409
    assert duplicate_response.get_json()["code"] == "USERNAME_ALREADY_EXISTS"

    invalid_response = client.post(
        "/api/v1/auth/register",
        json={"username": "short_password", "password": "abc"},
    )
    assert invalid_response.status_code == 422
    assert invalid_response.get_json()["code"] == "VALIDATION_ERROR"


def test_login_rejects_wrong_password_and_disabled_account(client, user_factory):
    user_factory("active_user")
    user_factory("disabled_user", status="DISABLED")

    wrong_response = client.post(
        "/api/v1/auth/login",
        json={"username": "active_user", "password": "not-the-password"},
    )
    assert wrong_response.status_code == 401
    assert wrong_response.get_json()["code"] == "INVALID_CREDENTIALS"

    disabled_response = client.post(
        "/api/v1/auth/login",
        json={"username": "disabled_user", "password": "Password123!"},
    )
    assert disabled_response.status_code == 403
    assert disabled_response.get_json()["code"] == "ACCOUNT_DISABLED"


def test_change_password_invalidates_old_password(client, user_factory, login):
    user_factory("password_user")
    token = login("password_user")

    response = client.put(
        "/api/v1/auth/password",
        json={
            "current_password": "Password123!",
            "new_password": "NewSecure456!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"username": "password_user", "password": "Password123!"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"username": "password_user", "password": "NewSecure456!"},
    )
    assert new_login.status_code == 200


def test_missing_token_uses_standard_error_shape(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.get_json()["code"] == "AUTHORIZATION_REQUIRED"
