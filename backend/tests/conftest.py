from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    application = create_app(
        "testing",
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
            "JWT_SECRET_KEY": "test-only-jwt-secret-at-least-32-bytes-long",
        },
    )
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_factory(app):
    from app.models.user import User
    from app.security import hash_password

    created_users = []

    def create_user(
        username: str,
        password: str = "Password123!",
        role: str = "USER",
        status: str = "ACTIVE",
        phone: str | None = None,
    ) -> User:
        with app.app_context():
            user = User(
                username=username,
                password_hash=hash_password(password),
                role=role,
                status=status,
                phone=phone,
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            db.session.expunge(user)
            created_users.append(user.user_id)
            return user

    return create_user


@pytest.fixture()
def login(client):
    def perform(username: str, password: str = "Password123!") -> str:
        response = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert response.status_code == 200
        return response.get_json()["data"]["access_token"]

    return perform
