from __future__ import annotations

from datetime import datetime, timedelta


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _setup_case_and_task(client, owner_token: str, volunteer_token: str) -> tuple[int, int]:
    pet_id = client.post(
        "/api/v1/pets",
        json={
            "name": "寻回测试宠物",
            "species": "CAT",
            "primary_color": "ORANGE",
            "gender": "MALE",
            "size": "MEDIUM",
        },
        headers=_headers(owner_token),
    ).get_json()["data"]["pet_id"]
    case_id = client.post(
        "/api/v1/cases",
        json={
            "pet_id": pet_id,
            "lost_time": (datetime.now() - timedelta(hours=8)).isoformat(timespec="seconds"),
            "latitude": 30.26,
            "longitude": 120.17,
            "address": "文化广场",
        },
        headers=_headers(owner_token),
    ).get_json()["data"]["case_id"]
    area = client.post(
        f"/api/v1/cases/{case_id}/areas",
        json={
            "area_name": "地库区域",
            "center_latitude": 30.261,
            "center_longitude": 120.171,
            "radius_meters": 500,
        },
        headers=_headers(owner_token),
    ).get_json()["data"]
    task_id = area["task"]["task_id"]
    client.post(f"/api/v1/tasks/{task_id}/claim", headers=_headers(volunteer_token))
    return case_id, task_id


def _reunion_payload(finder_id: int | None = None) -> dict:
    return {
        "finder_id": finder_id,
        "reunion_time": (datetime.now() - timedelta(minutes=10)).isoformat(timespec="seconds"),
        "latitude": 30.262,
        "longitude": 120.172,
        "address": "文化广场停车场",
        "method": "志愿者发现",
        "note": "健康状况良好",
    }


def test_owner_confirms_reunion_and_archives_case_and_tasks(
    client, user_factory, login
):
    owner = user_factory("reunion_api_owner")
    finder = user_factory("reunion_api_finder")
    owner_token = login("reunion_api_owner")
    finder_token = login("reunion_api_finder")
    case_id, task_id = _setup_case_and_task(client, owner_token, finder_token)

    response = client.post(
        f"/api/v1/cases/{case_id}/reunion",
        json=_reunion_payload(finder.user_id),
        headers=_headers(owner_token),
    )
    assert response.status_code == 201
    reunion = response.get_json()["data"]
    assert reunion["case_id"] == case_id

    case_response = client.get(f"/api/v1/cases/{case_id}")
    assert case_response.get_json()["data"]["status"] == "REUNITED"
    assert case_response.get_json()["data"]["closed_at"] is not None

    tasks_response = client.get(
        "/api/v1/tasks?scope=all",
        headers=_headers(owner_token),
    )
    task = next(item for item in tasks_response.get_json()["data"] if item["task_id"] == task_id)
    assert task["status"] == "CANCELLED"


def test_duplicate_and_unauthorized_reunion_are_rejected(
    client, user_factory, login
):
    user_factory("duplicate_owner")
    finder = user_factory("duplicate_finder")
    user_factory("duplicate_other")
    owner_token = login("duplicate_owner")
    finder_token = login("duplicate_finder")
    other_token = login("duplicate_other")
    case_id, _ = _setup_case_and_task(client, owner_token, finder_token)

    unauthorized = client.post(
        f"/api/v1/cases/{case_id}/reunion",
        json=_reunion_payload(finder.user_id),
        headers=_headers(other_token),
    )
    assert unauthorized.status_code == 403
    assert unauthorized.get_json()["code"] == "REUNION_ACCESS_DENIED"

    first = client.post(
        f"/api/v1/cases/{case_id}/reunion",
        json=_reunion_payload(finder.user_id),
        headers=_headers(owner_token),
    )
    assert first.status_code == 201

    duplicate = client.post(
        f"/api/v1/cases/{case_id}/reunion",
        json=_reunion_payload(finder.user_id),
        headers=_headers(owner_token),
    )
    assert duplicate.status_code == 409
    assert duplicate.get_json()["code"] == "CASE_NOT_SEARCHING"
