from __future__ import annotations


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _pet_payload(name: str = "豆包") -> dict:
    return {
        "name": name,
        "species": "DOG",
        "breed": "Border Collie",
        "primary_color": "BLACK",
        "secondary_color": "WHITE",
        "gender": "FEMALE",
        "size": "MEDIUM",
        "birth_date": "2022-05-12",
        "distinctive_features": "胸口白色心形毛",
    }


def test_owner_can_create_list_update_and_deactivate_pet(
    client, user_factory, login
):
    user_factory("pet_owner")
    token = login("pet_owner")

    create_response = client.post(
        "/api/v1/pets",
        json=_pet_payload(),
        headers=_headers(token),
    )
    assert create_response.status_code == 201
    pet = create_response.get_json()["data"]
    assert pet["name"] == "豆包"
    assert pet["status"] == "ACTIVE"
    pet_id = pet["pet_id"]

    list_response = client.get("/api/v1/pets", headers=_headers(token))
    assert list_response.status_code == 200
    assert [item["pet_id"] for item in list_response.get_json()["data"]] == [pet_id]

    update_response = client.patch(
        f"/api/v1/pets/{pet_id}",
        json={"name": "豆豆", "distinctive_features": "胸口白毛，红色项圈"},
        headers=_headers(token),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["name"] == "豆豆"

    delete_response = client.delete(
        f"/api/v1/pets/{pet_id}",
        headers=_headers(token),
    )
    assert delete_response.status_code == 200
    assert delete_response.get_json()["data"]["status"] == "INACTIVE"

    active_list = client.get("/api/v1/pets", headers=_headers(token))
    assert active_list.get_json()["data"] == []

    all_list = client.get(
        "/api/v1/pets?include_inactive=1",
        headers=_headers(token),
    )
    assert len(all_list.get_json()["data"]) == 1


def test_other_user_cannot_modify_pet(client, user_factory, login):
    user_factory("first_owner")
    user_factory("second_owner")
    first_token = login("first_owner")
    second_token = login("second_owner")

    pet_id = client.post(
        "/api/v1/pets",
        json=_pet_payload("年糕"),
        headers=_headers(first_token),
    ).get_json()["data"]["pet_id"]

    response = client.patch(
        f"/api/v1/pets/{pet_id}",
        json={"name": "不允许修改"},
        headers=_headers(second_token),
    )
    assert response.status_code == 403
    assert response.get_json()["code"] == "PET_ACCESS_DENIED"


def test_pet_validation_rejects_invalid_gender(client, user_factory, login):
    user_factory("validation_owner")
    token = login("validation_owner")
    payload = _pet_payload()
    payload["gender"] = "INVALID"

    response = client.post(
        "/api/v1/pets",
        json=payload,
        headers=_headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["code"] == "VALIDATION_ERROR"
