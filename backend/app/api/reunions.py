from __future__ import annotations

from flask import Blueprint, jsonify

from ..extensions import db
from ..models.lost_case import LostCase
from ..schemas.reunion import ReunionCreateRequest
from ..security import active_user_required, get_current_user
from ..services.reunion_service import confirm_reunion
from .errors import APIError
from .utils import parse_json


reunions_bp = Blueprint("reunions", __name__)


@reunions_bp.post("/cases/<int:case_id>/reunion")
@active_user_required
def create_reunion(case_id: int):
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    user = get_current_user()
    if user.user_id not in {lost_case.pet.owner_id, lost_case.publisher_id}:
        raise APIError("REUNION_ACCESS_DENIED", "只有宠物主人或事件发布者可以确认寻回", 403)
    if lost_case.status != "SEARCHING":
        raise APIError("CASE_NOT_SEARCHING", "只有寻找中的事件可以确认寻回", 409)

    payload = parse_json(ReunionCreateRequest)
    record = confirm_reunion(
        case_id,
        user.user_id,
        payload.model_dump(),
    )
    return jsonify({"data": record.to_dict(), "message": "宠物已确认寻回"}), 201
