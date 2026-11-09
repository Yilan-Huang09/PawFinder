from __future__ import annotations


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_lists_and_reads_only_own_notifications(
    client, app, user_factory, login
):
    first = user_factory("notification_first")
    second = user_factory("notification_second")
    first_token = login("notification_first")
    second_token = login("notification_second")

    from app.extensions import db
    from app.models.notification import Notification

    with app.app_context():
        own = Notification(
            user_id=first.user_id,
            type="SYSTEM",
            title="测试通知",
            content="这是第一位用户的通知。",
            is_read=False,
        )
        other = Notification(
            user_id=second.user_id,
            type="SYSTEM",
            title="其他通知",
            content="这是第二位用户的通知。",
            is_read=False,
        )
        db.session.add_all([own, other])
        db.session.commit()
        own_id = own.notification_id

    list_response = client.get("/api/v1/notifications", headers=_headers(first_token))
    assert list_response.status_code == 200
    assert len(list_response.get_json()["data"]) == 1
    assert list_response.get_json()["meta"]["unread_count"] == 1

    denied = client.patch(
        f"/api/v1/notifications/{own_id}/read",
        headers=_headers(second_token),
    )
    assert denied.status_code == 404

    read_response = client.patch(
        f"/api/v1/notifications/{own_id}/read",
        headers=_headers(first_token),
    )
    assert read_response.status_code == 200
    assert read_response.get_json()["data"]["is_read"] is True
    assert read_response.get_json()["data"]["read_at"] is not None


def test_claiming_task_notifies_case_owner(client, user_factory, login):
    from datetime import datetime, timedelta

    user_factory("notify_owner")
    user_factory("notify_volunteer")
    owner_token = login("notify_owner")
    volunteer_token = login("notify_volunteer")
    pet_id = client.post(
        "/api/v1/pets",
        json={
            "name": "通知测试宠物",
            "species": "DOG",
            "primary_color": "BLACK",
        },
        headers=_headers(owner_token),
    ).get_json()["data"]["pet_id"]
    case_id = client.post(
        "/api/v1/cases",
        json={
            "pet_id": pet_id,
            "lost_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "latitude": 30.27,
            "longitude": 120.15,
            "address": "通知测试地址",
        },
        headers=_headers(owner_token),
    ).get_json()["data"]["case_id"]
    area = client.post(
        f"/api/v1/cases/{case_id}/areas",
        json={
            "area_name": "通知测试区域",
            "center_latitude": 30.271,
            "center_longitude": 120.151,
            "radius_meters": 500,
        },
        headers=_headers(owner_token),
    ).get_json()["data"]

    client.post(
        f"/api/v1/tasks/{area['task']['task_id']}/claim",
        headers=_headers(volunteer_token),
    )

    notifications = client.get(
        "/api/v1/notifications",
        headers=_headers(owner_token),
    ).get_json()["data"]
    assert any(item["type"] == "TASK_STATUS" for item in notifications)
