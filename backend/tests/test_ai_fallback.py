from __future__ import annotations

import requests


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_description_optimization_uses_local_template_without_key(
    client, user_factory, login
):
    user_factory("ai_local_user")
    token = login("ai_local_user")

    response = client.post(
        "/api/v1/ai/optimize-description",
        json={"text": " 黑白边牧   戴红色项圈 "},
        headers=_headers(token),
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["source"] == "local"
    assert data["text"] == "黑白边牧 戴红色项圈。"
    assert data["suggestions"]


def test_remote_timeout_falls_back_to_local_template(
    client, app, user_factory, login, monkeypatch
):
    user_factory("ai_timeout_user")
    token = login("ai_timeout_user")
    app.config.update(
        AI_API_BASE_URL="https://example.invalid/v1",
        AI_API_KEY="test-key",
        AI_MODEL="test-model",
    )

    def timeout(*args, **kwargs):
        raise requests.Timeout("simulated timeout")

    monkeypatch.setattr("app.services.ai_service.requests.post", timeout)

    response = client.post(
        "/api/v1/ai/optimize-description",
        json={"text": "橘猫 左耳有缺口"},
        headers=_headers(token),
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["source"] == "local_fallback"


def test_case_summary_reports_match_counts(client, user_factory, login):
    from datetime import datetime, timedelta

    user_factory("summary_owner")
    token = login("summary_owner")
    pet_id = client.post(
        "/api/v1/pets",
        json={"name": "摘要宠物", "species": "CAT", "primary_color": "GRAY"},
        headers=_headers(token),
    ).get_json()["data"]["pet_id"]
    case_id = client.post(
        "/api/v1/cases",
        json={
            "pet_id": pet_id,
            "lost_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "latitude": 30.28,
            "longitude": 120.16,
            "address": "摘要测试地址",
        },
        headers=_headers(token),
    ).get_json()["data"]["case_id"]

    response = client.post(
        "/api/v1/ai/summarize-case",
        json={"case_id": case_id},
        headers=_headers(token),
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["source"] == "local"
    assert "摘要宠物" in data["text"]
    assert "0 条候选线索" in data["text"]
