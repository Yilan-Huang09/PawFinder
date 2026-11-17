from __future__ import annotations

from flask_jwt_extended import create_access_token

from ..api.errors import APIError
from ..extensions import db
from ..models.user import User
from ..security import hash_password, verify_password


def create_user(
    username: str,
    password: str,
    phone: str | None = None,
    email: str | None = None,
) -> User:
    if User.query.filter_by(username=username).first() is not None:
        raise APIError("USERNAME_ALREADY_EXISTS", "用户名已被使用", 409)
    if phone and User.query.filter_by(phone=phone).first() is not None:
        raise APIError("PHONE_ALREADY_EXISTS", "手机号已被使用", 409)
    if email and User.query.filter_by(email=email).first() is not None:
        raise APIError("EMAIL_ALREADY_EXISTS", "邮箱已被使用", 409)

    user = User(
        username=username,
        password_hash=hash_password(password),
        phone=phone,
        email=email,
        role="USER",
        status="ACTIVE",
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(username: str, password: str) -> User:
    user = User.query.filter_by(username=username).first()
    if user is None or not verify_password(user.password_hash, password):
        raise APIError("INVALID_CREDENTIALS", "用户名或密码错误", 401)
    if user.status != "ACTIVE":
        raise APIError("ACCOUNT_DISABLED", "账号已被停用", 403)
    return user


def issue_access_token(user: User) -> str:
    return create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role},
    )
