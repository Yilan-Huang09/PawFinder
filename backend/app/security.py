from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

from flask import Flask
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from .api.errors import APIError, error_response
from .extensions import db, jwt
from .models.user import User


ViewFunction = TypeVar("ViewFunction", bound=Callable[..., Any])


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256:600000")


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def get_current_user() -> User:
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError) as exc:
        raise APIError("INVALID_TOKEN", "登录凭证无效", 401) from exc

    user = db.session.get(User, user_id)
    if user is None:
        raise APIError("USER_NOT_FOUND", "登录用户不存在", 401)
    if user.status != "ACTIVE":
        raise APIError("ACCOUNT_DISABLED", "账号已被停用", 403)
    return user


def active_user_required(function: ViewFunction) -> ViewFunction:
    @wraps(function)
    @jwt_required()
    def wrapped(*args, **kwargs):
        get_current_user()
        return function(*args, **kwargs)

    return cast(ViewFunction, wrapped)


def admin_required(function: ViewFunction) -> ViewFunction:
    @wraps(function)
    @jwt_required()
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if user.role != "ADMIN":
            raise APIError("ADMIN_REQUIRED", "该操作需要管理员权限", 403)
        return function(*args, **kwargs)

    return cast(ViewFunction, wrapped)


def register_jwt_handlers(app: Flask) -> None:
    @jwt.unauthorized_loader
    def missing_token(reason: str):
        return error_response(
            "AUTHORIZATION_REQUIRED",
            "请先登录后再进行该操作",
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token(reason: str):
        return error_response("INVALID_TOKEN", "登录凭证无效", 401)

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return error_response("TOKEN_EXPIRED", "登录凭证已过期", 401)

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        return error_response("TOKEN_REVOKED", "登录凭证已失效", 401)
