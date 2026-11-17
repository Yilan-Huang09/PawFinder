from __future__ import annotations

from flask import Blueprint, jsonify

from ..extensions import db
from ..schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest
from ..security import active_user_required, get_current_user, hash_password, verify_password
from ..services.auth_service import authenticate, create_user, issue_access_token
from .errors import APIError
from .utils import parse_json


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    payload = parse_json(RegisterRequest)
    user = create_user(
        username=payload.username,
        password=payload.password,
        phone=payload.phone,
        email=payload.email,
    )
    return (
        jsonify(
            {
                "data": {
                    "user": user.to_dict(),
                    "access_token": issue_access_token(user),
                },
                "message": "注册成功",
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    payload = parse_json(LoginRequest)
    user = authenticate(payload.username, payload.password)
    return jsonify(
        {
            "data": {
                "user": user.to_dict(),
                "access_token": issue_access_token(user),
            },
            "message": "登录成功",
        }
    )


@auth_bp.get("/me")
@active_user_required
def current_user():
    return jsonify({"data": get_current_user().to_dict(), "message": "获取成功"})


@auth_bp.put("/password")
@active_user_required
def change_password():
    payload = parse_json(ChangePasswordRequest)
    user = get_current_user()
    if not verify_password(user.password_hash, payload.current_password):
        raise APIError("CURRENT_PASSWORD_INCORRECT", "当前密码不正确", 422)
    user.password_hash = hash_password(payload.new_password)
    db.session.commit()
    return jsonify({"data": None, "message": "密码修改成功"})
