from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app():
    application = create_app(
        "testing",
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
            "JWT_SECRET_KEY": "test-only-jwt-secret",
        },
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
