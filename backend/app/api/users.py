from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy import or_

from ..extensions import db
from ..models.user import User
from ..schemas.auth import UpdateProfileRequest, UpdateUserStatusRequest
from ..security import active_user_required, admin_required, get_current_user
from .errors import APIError
from .utils import parse_json


users_bp = Blueprint("users", __name__)


@users_bp.patch("/users/me")
@active_user_required
def update_profile():
    payload = parse_json(UpdateProfileRequest)
    user = get_current_user()

    duplicate_filters = []
    changed_fields = payload.model_fields_set
    if "phone" in changed_fields and payload.phone:
        duplicate_filters.append(User.phone == payload.phone)
    if "email" in changed_fields and payload.email:
        duplicate_filters.append(User.email == payload.email)
    if duplicate_filters:
        duplicate = User.query.filter(
            User.user_id != user.user_id,
            or_(*duplicate_filters),
        ).first()
        if duplicate is not None:
            raise APIError("PROFILE_IDENTITY_ALREADY_EXISTS", "手机号或邮箱已被使用", 409)

    if "phone" in changed_fields:
        user.phone = payload.phone
    if "email" in changed_fields:
        user.email = payload.email
    if "avatar_url" in changed_fields:
        user.avatar_url = payload.avatar_url
    db.session.commit()
    return jsonify({"data": user.to_dict(), "message": "个人资料已更新"})


@users_bp.patch("/admin/users/<int:user_id>/status")
@admin_required
def update_user_status(user_id: int):
    payload = parse_json(UpdateUserStatusRequest)
    administrator = get_current_user()
    if administrator.user_id == user_id and payload.status == "DISABLED":
        raise APIError("CANNOT_DISABLE_SELF", "管理员不能停用自己的账号", 409)

    user = db.session.get(User, user_id)
    if user is None:
        raise APIError("USER_NOT_FOUND", "用户不存在", 404)
    user.status = payload.status
    db.session.commit()
    return jsonify({"data": user.to_dict(), "message": "账号状态已更新"})
