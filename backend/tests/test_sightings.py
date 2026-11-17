from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _sighting_payload(address: str = "西南大学北门公交站") -> dict:
    return {
        "species": "DOG",
        "breed_guess": "Border Collie",
        "primary_color": "BLACK",
        "secondary_color": "WHITE",
        "gender_guess": "FEMALE",
        "size_guess": "MEDIUM",
        "seen_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="seconds"),
        "latitude": 29.8278,
        "longitude": 106.4278,
        "address": address,
        "direction": "向东",
        "confidence": 5,
        "description": "黑白边牧，戴红色项圈。",
    }


def test_sighting_is_independent_and_publicly_listed(client, user_factory, login):
    user_factory("sighting_reporter")
    token = login("sighting_reporter")

    create_response = client.post(
        "/api/v1/sightings",
        json=_sighting_payload(),
        headers=_headers(token),
    )
    assert create_response.status_code == 201
    sighting = create_response.get_json()["data"]
    assert "case_id" not in sighting
    assert sighting["status"] == "ACTIVE"

    list_response = client.get("/api/v1/sightings?species=DOG")
    assert list_response.status_code == 200
    assert len(list_response.get_json()["data"]) == 1
    assert list_response.get_json()["data"][0]["address"] == "西南大学北门公交站"


def test_only_reporter_can_edit_or_invalidate_sighting(
    client, user_factory, login
):
    user_factory("first_reporter")
    user_factory("other_reporter")
    first_token = login("first_reporter")
    other_token = login("other_reporter")
    sighting_id = client.post(
        "/api/v1/sightings",
        json=_sighting_payload(),
        headers=_headers(first_token),
    ).get_json()["data"]["sighting_id"]

    denied = client.patch(
        f"/api/v1/sightings/{sighting_id}",
        json={"description": "不允许修改"},
        headers=_headers(other_token),
    )
    assert denied.status_code == 403
    assert denied.get_json()["code"] == "SIGHTING_ACCESS_DENIED"

    update = client.patch(
        f"/api/v1/sightings/{sighting_id}",
        json={"description": "补充：红色项圈很明显"},
        headers=_headers(first_token),
    )
    assert update.status_code == 200

    delete = client.delete(
        f"/api/v1/sightings/{sighting_id}",
        headers=_headers(first_token),
    )
    assert delete.status_code == 200
    assert delete.get_json()["data"]["status"] == "INVALID"


def test_sighting_rejects_future_time_and_bad_confidence(
    client, user_factory, login
):
    user_factory("sighting_validation")
    token = login("sighting_validation")
    payload = _sighting_payload()
    payload["seen_time"] = (datetime.now() + timedelta(hours=1)).isoformat()
    payload["confidence"] = 6

    response = client.post(
        "/api/v1/sightings",
        json=payload,
        headers=_headers(token),
    )
    assert response.status_code == 422
    assert response.get_json()["code"] == "VALIDATION_ERROR"


def test_reporter_can_upload_sighting_photo(client, user_factory, login):
    user_factory("sighting_photo_reporter")
    token = login("sighting_photo_reporter")
    sighting_id = client.post(
        "/api/v1/sightings",
        json=_sighting_payload(),
        headers=_headers(token),
    ).get_json()["data"]["sighting_id"]

    response = client.post(
        f"/api/v1/sightings/{sighting_id}/photos",
        data={
            "photo": (
                BytesIO(b"\xff\xd8\xff\xe0" + b"sighting-photo"),
                "sighting.jpg",
            )
        },
        headers=_headers(token),
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    assert response.get_json()["data"]["photo_url"].startswith("sightings/")
