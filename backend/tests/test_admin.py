from __future__ import annotations

from datetime import datetime, timedelta


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_statistics_are_protected_and_return_counts(
    client, user_factory, login
):
    user_factory("stats_admin", role="ADMIN")
    user_factory("stats_regular")
    admin_token = login("stats_admin")
    regular_token = login("stats_regular")

    denied = client.get(
        "/api/v1/admin/statistics",
        headers=_headers(regular_token),
    )
    assert denied.status_code == 403

    response = client.get(
        "/api/v1/admin/statistics",
        headers=_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["users"]["total"] == 2
    assert data["users"]["active"] == 2
    assert data["cases"]["searching"] == 0


def test_admin_can_hide_sighting_and_close_case(client, user_factory, login):
    user_factory("content_admin", role="ADMIN")
    user_factory("content_user")
    admin_token = login("content_admin")
    user_token = login("content_user")
    pet_id = client.post(
        "/api/v1/pets",
        json={"name": "管理测试宠物", "species": "DOG", "primary_color": "WHITE"},
        headers=_headers(user_token),
    ).get_json()["data"]["pet_id"]
    case_id = client.post(
        "/api/v1/cases",
        json={
            "pet_id": pet_id,
            "lost_time": (datetime.now() - timedelta(hours=3)).isoformat(),
            "latitude": 30.27,
            "longitude": 120.15,
            "address": "管理测试地址",
        },
        headers=_headers(user_token),
    ).get_json()["data"]["case_id"]
    sighting_id = client.post(
        "/api/v1/sightings",
        json={
            "species": "CAT",
            "primary_color": "GRAY",
            "seen_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "latitude": 30.28,
            "longitude": 120.16,
            "address": "无效线索地址",
        },
        headers=_headers(user_token),
    ).get_json()["data"]["sighting_id"]

    hide_response = client.patch(
        f"/api/v1/admin/content/sightings/{sighting_id}/status",
        json={"status": "HIDDEN"},
        headers=_headers(admin_token),
    )
    assert hide_response.status_code == 200
    assert hide_response.get_json()["data"]["status"] == "HIDDEN"

    close_response = client.patch(
        f"/api/v1/admin/content/cases/{case_id}/status",
        json={"status": "CLOSED"},
        headers=_headers(admin_token),
    )
    assert close_response.status_code == 200
    assert close_response.get_json()["data"]["status"] == "CLOSED"


def test_admin_lists_users_and_all_content_states(client, user_factory, login, app):
    user_factory("list_admin", role="ADMIN")
    regular = user_factory("list_regular")
    admin_token = login("list_admin")
    regular_token = login("list_regular")

    from app.extensions import db
    from app.models.sighting import Sighting

    with app.app_context():
        hidden = Sighting(
            reporter_id=regular.user_id,
            species="CAT",
            primary_color="GRAY",
            seen_time=datetime.now() - timedelta(hours=1),
            latitude=30.28,
            longitude=120.16,
            address="管理员可见的隐藏线索",
            status="HIDDEN",
        )
        db.session.add(hidden)
        db.session.commit()

    denied = client.get("/api/v1/admin/users", headers=_headers(regular_token))
    assert denied.status_code == 403

    users = client.get("/api/v1/admin/users", headers=_headers(admin_token))
    sightings = client.get(
        "/api/v1/admin/content/sightings",
        headers=_headers(admin_token),
    )
    cases = client.get(
        "/api/v1/admin/content/cases",
        headers=_headers(admin_token),
    )
    assert users.status_code == 200
    assert {item["username"] for item in users.get_json()["data"]} == {
        "list_admin",
        "list_regular",
    }
    assert sightings.get_json()["data"][0]["status"] == "HIDDEN"
    assert cases.status_code == 200
