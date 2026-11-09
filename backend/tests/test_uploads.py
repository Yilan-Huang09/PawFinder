from __future__ import annotations

from io import BytesIO


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_pet(client, token: str) -> int:
    response = client.post(
        "/api/v1/pets",
        json={
            "name": "照片测试宠物",
            "species": "CAT",
            "primary_color": "ORANGE",
            "gender": "UNKNOWN",
            "size": "MEDIUM",
        },
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]["pet_id"]


def _jpeg(name: str = "pet.jpg"):
    return BytesIO(b"\xff\xd8\xff\xe0" + b"demo-jpeg-content"), name


def _png(name: str = "pet.png"):
    return BytesIO(b"\x89PNG\r\n\x1a\n" + b"demo-png-content"), name


def test_first_photo_becomes_cover_and_cover_can_change(
    client, user_factory, login
):
    user_factory("photo_owner")
    token = login("photo_owner")
    pet_id = _create_pet(client, token)

    first_response = client.post(
        f"/api/v1/pets/{pet_id}/photos",
        data={"photo": _jpeg("first.jpg")},
        headers=_headers(token),
        content_type="multipart/form-data",
    )
    assert first_response.status_code == 201
    first_photo = first_response.get_json()["data"]
    assert first_photo["is_cover"] is True

    second_response = client.post(
        f"/api/v1/pets/{pet_id}/photos",
        data={"photo": _png("second.png")},
        headers=_headers(token),
        content_type="multipart/form-data",
    )
    assert second_response.status_code == 201
    second_photo = second_response.get_json()["data"]
    assert second_photo["is_cover"] is False

    cover_response = client.put(
        f"/api/v1/pets/{pet_id}/photos/{second_photo['photo_id']}/cover",
        headers=_headers(token),
    )
    assert cover_response.status_code == 200

    detail_response = client.get(
        f"/api/v1/pets/{pet_id}",
        headers=_headers(token),
    )
    photos = detail_response.get_json()["data"]["photos"]
    assert [photo["is_cover"] for photo in photos] == [False, True]


def test_upload_rejects_spoofed_or_unsupported_file(client, user_factory, login):
    user_factory("unsafe_upload_owner")
    token = login("unsafe_upload_owner")
    pet_id = _create_pet(client, token)

    spoofed_response = client.post(
        f"/api/v1/pets/{pet_id}/photos",
        data={"photo": (BytesIO(b"not-an-image"), "fake.jpg")},
        headers=_headers(token),
        content_type="multipart/form-data",
    )
    assert spoofed_response.status_code == 422
    assert spoofed_response.get_json()["code"] == "INVALID_IMAGE_CONTENT"

    unsupported_response = client.post(
        f"/api/v1/pets/{pet_id}/photos",
        data={"photo": (BytesIO(b"GIF89a"), "pet.gif")},
        headers=_headers(token),
        content_type="multipart/form-data",
    )
    assert unsupported_response.status_code == 422
    assert unsupported_response.get_json()["code"] == "UNSUPPORTED_IMAGE_TYPE"


def test_delete_photo_removes_record_and_promotes_next_cover(
    client, user_factory, login, app
):
    user_factory("delete_photo_owner")
    token = login("delete_photo_owner")
    pet_id = _create_pet(client, token)

    first = client.post(
        f"/api/v1/pets/{pet_id}/photos",
        data={"photo": _jpeg("first.jpg")},
        headers=_headers(token),
        content_type="multipart/form-data",
    ).get_json()["data"]
    second = client.post(
        f"/api/v1/pets/{pet_id}/photos",
        data={"photo": _png("second.png")},
        headers=_headers(token),
        content_type="multipart/form-data",
    ).get_json()["data"]

    response = client.delete(
        f"/api/v1/pets/{pet_id}/photos/{first['photo_id']}",
        headers=_headers(token),
    )
    assert response.status_code == 200

    detail = client.get(
        f"/api/v1/pets/{pet_id}",
        headers=_headers(token),
    ).get_json()["data"]
    assert detail["photos"] == [
        {
            **second,
            "is_cover": True,
        }
    ]
