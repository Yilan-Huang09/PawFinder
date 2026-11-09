from __future__ import annotations


def test_health_check_returns_service_status(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": {
            "service": "pawfinder-api",
            "status": "ok",
            "version": "1.0.0",
        },
        "message": "PawFinder API is healthy",
    }
    assert response.headers["X-Request-ID"]


def test_unknown_api_route_uses_standard_error_shape(client):
    response = client.get("/api/v1/not-a-route")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["code"] == "RESOURCE_NOT_FOUND"
    assert payload["message"] == "请求的资源不存在"
    assert payload["details"] == {}
    assert payload["request_id"] == response.headers["X-Request-ID"]
