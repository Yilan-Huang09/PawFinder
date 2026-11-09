from __future__ import annotations

from datetime import datetime, timedelta


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_case(client, token: str) -> int:
    pet = client.post(
        "/api/v1/pets",
        json={
            "name": "搜寻测试宠物",
            "species": "DOG",
            "primary_color": "GOLDEN",
            "gender": "MALE",
            "size": "LARGE",
        },
        headers=_headers(token),
    ).get_json()["data"]
    return client.post(
        "/api/v1/cases",
        json={
            "pet_id": pet["pet_id"],
            "lost_time": (datetime.now() - timedelta(hours=4)).isoformat(timespec="seconds"),
            "latitude": 30.21,
            "longitude": 120.22,
            "address": "江晖路公园",
        },
        headers=_headers(token),
    ).get_json()["data"]["case_id"]


def _create_area(client, token: str, case_id: int) -> dict:
    response = client.post(
        f"/api/v1/cases/{case_id}/areas",
        json={
            "area_name": "公园东区",
            "center_latitude": 30.211,
            "center_longitude": 120.221,
            "radius_meters": 900,
            "description": "沿公园出口巡查",
        },
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def test_owner_creates_area_and_single_volunteer_claims_task(
    client, user_factory, login
):
    user_factory("search_owner")
    user_factory("volunteer_one")
    user_factory("volunteer_two")
    owner_token = login("search_owner")
    first_token = login("volunteer_one")
    second_token = login("volunteer_two")
    case_id = _create_case(client, owner_token)
    area = _create_area(client, owner_token, case_id)
    assert area["task"]["status"] == "AVAILABLE"
    task_id = area["task"]["task_id"]

    first_claim = client.post(
        f"/api/v1/tasks/{task_id}/claim",
        headers=_headers(first_token),
    )
    assert first_claim.status_code == 200
    assert first_claim.get_json()["data"]["status"] == "CLAIMED"

    second_claim = client.post(
        f"/api/v1/tasks/{task_id}/claim",
        headers=_headers(second_token),
    )
    assert second_claim.status_code == 409
    assert second_claim.get_json()["code"] == "TASK_ALREADY_CLAIMED"


def test_volunteer_progress_release_and_reclaim(client, user_factory, login):
    user_factory("progress_owner")
    user_factory("progress_first")
    user_factory("progress_second")
    owner_token = login("progress_owner")
    first_token = login("progress_first")
    second_token = login("progress_second")
    task_id = _create_area(
        client,
        owner_token,
        _create_case(client, owner_token),
    )["task"]["task_id"]
    client.post(f"/api/v1/tasks/{task_id}/claim", headers=_headers(first_token))

    progress = client.patch(
        f"/api/v1/tasks/{task_id}/progress",
        json={"status": "IN_PROGRESS", "report": "开始沿绿道巡查"},
        headers=_headers(first_token),
    )
    assert progress.status_code == 200
    assert progress.get_json()["data"]["started_at"] is not None

    denied = client.patch(
        f"/api/v1/tasks/{task_id}/progress",
        json={"status": "COMPLETED", "report": "不允许代替完成"},
        headers=_headers(second_token),
    )
    assert denied.status_code == 403

    release = client.post(
        f"/api/v1/tasks/{task_id}/release",
        headers=_headers(first_token),
    )
    assert release.status_code == 200
    assert release.get_json()["data"]["status"] == "AVAILABLE"

    reclaim = client.post(
        f"/api/v1/tasks/{task_id}/claim",
        headers=_headers(second_token),
    )
    assert reclaim.status_code == 200


def test_non_owner_cannot_create_search_area(client, user_factory, login):
    user_factory("area_owner")
    user_factory("area_other")
    owner_token = login("area_owner")
    other_token = login("area_other")
    case_id = _create_case(client, owner_token)

    response = client.post(
        f"/api/v1/cases/{case_id}/areas",
        json={
            "area_name": "越权区域",
            "center_latitude": 30.21,
            "center_longitude": 120.22,
            "radius_meters": 500,
        },
        headers=_headers(other_token),
    )
    assert response.status_code == 403
    assert response.get_json()["code"] == "SEARCH_AREA_ACCESS_DENIED"
