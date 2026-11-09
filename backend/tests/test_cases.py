from __future__ import annotations

from datetime import datetime, timedelta


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_pet(client, token: str, name: str = "豆包", species: str = "DOG") -> int:
    response = client.post(
        "/api/v1/pets",
        json={
            "name": name,
            "species": species,
            "primary_color": "BLACK" if species == "DOG" else "ORANGE",
            "gender": "UNKNOWN",
            "size": "MEDIUM",
        },
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]["pet_id"]


def _case_payload(pet_id: int, address: str = "文三路地铁站") -> dict:
    return {
        "pet_id": pet_id,
        "lost_time": (datetime.now() - timedelta(hours=2)).isoformat(timespec="seconds"),
        "latitude": 30.2741,
        "longitude": 120.1551,
        "address": address,
        "description": "散步时走失，戴红色项圈。",
        "contact_phone": "13900000010",
    }


def test_owner_can_publish_and_public_can_filter_cases(client, user_factory, login):
    user_factory("case_owner")
    token = login("case_owner")
    dog_id = _create_pet(client, token, "豆包", "DOG")
    cat_id = _create_pet(client, token, "橘子", "CAT")

    dog_response = client.post(
        "/api/v1/cases",
        json=_case_payload(dog_id, "文三路地铁站"),
        headers=_headers(token),
    )
    assert dog_response.status_code == 201
    dog_case = dog_response.get_json()["data"]
    assert dog_case["status"] == "SEARCHING"
    assert dog_case["pet"]["name"] == "豆包"

    assert client.post(
        "/api/v1/cases",
        json=_case_payload(cat_id, "武林广场"),
        headers=_headers(token),
    ).status_code == 201

    public_response = client.get("/api/v1/cases?species=DOG&page=1&per_page=10")
    assert public_response.status_code == 200
    payload = public_response.get_json()
    assert len(payload["data"]) == 1
    assert payload["data"][0]["pet"]["name"] == "豆包"
    assert payload["data"][0]["contact_phone"] == "139****0010"
    assert payload["meta"]["total"] == 1


def test_user_cannot_publish_case_for_another_users_pet(
    client, user_factory, login
):
    user_factory("pet_owner_case")
    user_factory("case_intruder")
    owner_token = login("pet_owner_case")
    intruder_token = login("case_intruder")
    pet_id = _create_pet(client, owner_token)

    response = client.post(
        "/api/v1/cases",
        json=_case_payload(pet_id),
        headers=_headers(intruder_token),
    )

    assert response.status_code == 403
    assert response.get_json()["code"] == "PET_ACCESS_DENIED"


def test_case_rejects_future_time_and_invalid_coordinates(
    client, user_factory, login
):
    user_factory("case_validation_owner")
    token = login("case_validation_owner")
    pet_id = _create_pet(client, token)

    payload = _case_payload(pet_id)
    payload["lost_time"] = (datetime.now() + timedelta(days=1)).isoformat()
    payload["latitude"] = 100

    response = client.post(
        "/api/v1/cases",
        json=payload,
        headers=_headers(token),
    )
    assert response.status_code == 422
    assert response.get_json()["code"] == "VALIDATION_ERROR"


def test_only_owner_can_edit_and_closed_case_is_immutable(
    client, user_factory, login
):
    user_factory("edit_case_owner")
    user_factory("edit_case_other")
    owner_token = login("edit_case_owner")
    other_token = login("edit_case_other")
    pet_id = _create_pet(client, owner_token)
    case_id = client.post(
        "/api/v1/cases",
        json=_case_payload(pet_id),
        headers=_headers(owner_token),
    ).get_json()["data"]["case_id"]

    denied = client.patch(
        f"/api/v1/cases/{case_id}",
        json={"description": "不应被修改"},
        headers=_headers(other_token),
    )
    assert denied.status_code == 403
    assert denied.get_json()["code"] == "CASE_ACCESS_DENIED"

    close_response = client.patch(
        f"/api/v1/cases/{case_id}",
        json={"status": "CLOSED"},
        headers=_headers(owner_token),
    )
    assert close_response.status_code == 200
    assert close_response.get_json()["data"]["closed_at"] is not None

    immutable = client.patch(
        f"/api/v1/cases/{case_id}",
        json={"description": "关闭后修改"},
        headers=_headers(owner_token),
    )
    assert immutable.status_code == 409
    assert immutable.get_json()["code"] == "CASE_NOT_EDITABLE"
