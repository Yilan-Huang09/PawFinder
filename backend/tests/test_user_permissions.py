from __future__ import annotations


def test_user_can_update_own_profile(client, user_factory, login):
    user_factory("profile_user")
    token = login("profile_user")

    response = client.patch(
        "/api/v1/users/me",
        json={"phone": "13900000002", "email": "profile@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["phone"] == "13900000002"

    partial_response = client.patch(
        "/api/v1/users/me",
        json={"phone": "13900000003"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert partial_response.status_code == 200
    assert partial_response.get_json()["data"]["phone"] == "13900000003"
    assert partial_response.get_json()["data"]["email"] == "profile@example.com"


def test_regular_user_cannot_change_account_status(client, user_factory, login):
    target = user_factory("target_user")
    user_factory("regular_user")
    token = login("regular_user")

    response = client.patch(
        f"/api/v1/admin/users/{target.user_id}/status",
        json={"status": "DISABLED"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json()["code"] == "ADMIN_REQUIRED"


def test_admin_can_disable_user_but_not_self(client, user_factory, login):
    target = user_factory("disable_target")
    admin = user_factory("admin_user", role="ADMIN")
    token = login("admin_user")

    response = client.patch(
        f"/api/v1/admin/users/{target.user_id}/status",
        json={"status": "DISABLED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["status"] == "DISABLED"

    disabled_login = client.post(
        "/api/v1/auth/login",
        json={"username": "disable_target", "password": "Password123!"},
    )
    assert disabled_login.status_code == 403

    self_response = client.patch(
        f"/api/v1/admin/users/{admin.user_id}/status",
        json={"status": "DISABLED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert self_response.status_code == 409
    assert self_response.get_json()["code"] == "CANNOT_DISABLE_SELF"


def test_disabled_user_cannot_use_existing_token(client, user_factory, login, app):
    user = user_factory("later_disabled")
    token = login("later_disabled")

    from app.extensions import db
    from app.models.user import User

    with app.app_context():
        stored_user = db.session.get(User, user.user_id)
        stored_user.status = "DISABLED"
        db.session.commit()

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.get_json()["code"] == "ACCOUNT_DISABLED"
