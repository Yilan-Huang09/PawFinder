from __future__ import annotations

from datetime import datetime, timedelta


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_case(client, token: str) -> int:
    pet = client.post(
        "/api/v1/pets",
        json={
            "name": "豆包",
            "species": "DOG",
            "breed": "Border Collie",
            "primary_color": "BLACK",
            "secondary_color": "WHITE",
            "gender": "FEMALE",
            "size": "MEDIUM",
            "distinctive_features": "胸口白毛，红色项圈",
        },
        headers=_headers(token),
    ).get_json()["data"]
    lost_case = client.post(
        "/api/v1/cases",
        json={
            "pet_id": pet["pet_id"],
            "lost_time": (datetime.now() - timedelta(hours=3)).isoformat(timespec="seconds"),
            "latitude": 29.8269,
            "longitude": 106.4253,
            "address": "西南大学北门",
            "description": "戴红色项圈",
        },
        headers=_headers(token),
    ).get_json()["data"]
    return lost_case["case_id"]


def _create_sighting(client, token: str, latitude: float = 29.8278) -> int:
    response = client.post(
        "/api/v1/sightings",
        json={
            "species": "DOG",
            "breed_guess": "Border Collie",
            "primary_color": "BLACK",
            "secondary_color": "WHITE",
            "gender_guess": "FEMALE",
            "size_guess": "MEDIUM",
            "seen_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="seconds"),
            "latitude": latitude,
            "longitude": 106.4278,
            "address": "西南大学北门公交站",
            "confidence": 5,
            "description": "胸口有白毛，戴红色项圈",
        },
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]["sighting_id"]


def test_new_sighting_generates_explainable_match(client, user_factory, login):
    user_factory("match_owner")
    user_factory("match_reporter")
    owner_token = login("match_owner")
    reporter_token = login("match_reporter")
    case_id = _create_case(client, owner_token)
    sighting_id = _create_sighting(client, reporter_token)

    response = client.get(
        f"/api/v1/cases/{case_id}/matches",
        headers=_headers(owner_token),
    )
    assert response.status_code == 200
    matches = response.get_json()["data"]
    assert len(matches) == 1
    match = matches[0]
    assert match["sighting_id"] == sighting_id
    assert match["algorithm_version"] == "rule-v1"
    assert match["total_score"] >= 75
    assert match["appearance_score"] <= 100
    assert match["distance_km"] > 0
    assert "距离" in match["match_reason"]


def test_recalculation_is_idempotent_and_low_candidates_are_ignored(
    client, user_factory, login
):
    user_factory("recalc_owner")
    user_factory("recalc_reporter")
    owner_token = login("recalc_owner")
    reporter_token = login("recalc_reporter")
    case_id = _create_case(client, owner_token)
    _create_sighting(client, reporter_token)

    first = client.post(
        f"/api/v1/cases/{case_id}/recalculate",
        headers=_headers(owner_token),
    )
    second = client.post(
        f"/api/v1/cases/{case_id}/recalculate",
        headers=_headers(owner_token),
    )
    assert first.status_code == 200
    assert second.status_code == 200

    matches = client.get(
        f"/api/v1/cases/{case_id}/matches",
        headers=_headers(owner_token),
    ).get_json()["data"]
    assert len(matches) == 1

    _create_sighting(client, reporter_token, latitude=31.0)
    matches_after_far_sighting = client.get(
        f"/api/v1/cases/{case_id}/matches",
        headers=_headers(owner_token),
    ).get_json()["data"]
    assert len(matches_after_far_sighting) == 1


def test_only_case_owner_can_review_match(client, user_factory, login):
    user_factory("review_owner")
    user_factory("review_reporter")
    user_factory("review_other")
    owner_token = login("review_owner")
    reporter_token = login("review_reporter")
    other_token = login("review_other")
    case_id = _create_case(client, owner_token)
    _create_sighting(client, reporter_token)
    match_id = client.get(
        f"/api/v1/cases/{case_id}/matches",
        headers=_headers(owner_token),
    ).get_json()["data"][0]["match_id"]

    denied = client.patch(
        f"/api/v1/matches/{match_id}/review",
        json={"review_status": "CONFIRMED"},
        headers=_headers(other_token),
    )
    assert denied.status_code == 403
    assert denied.get_json()["code"] == "MATCH_ACCESS_DENIED"

    confirmed = client.patch(
        f"/api/v1/matches/{match_id}/review",
        json={"review_status": "CONFIRMED"},
        headers=_headers(owner_token),
    )
    assert confirmed.status_code == 200
    assert confirmed.get_json()["data"]["review_status"] == "CONFIRMED"
    assert confirmed.get_json()["data"]["reviewed_at"] is not None
