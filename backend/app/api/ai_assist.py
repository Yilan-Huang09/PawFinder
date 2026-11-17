from __future__ import annotations

from flask import Blueprint, jsonify

from ..extensions import db
from ..models.lost_case import LostCase
from ..schemas.ai import CaseSummaryRequest, DescriptionOptimizeRequest
from ..security import active_user_required, get_current_user
from ..services.ai_service import optimize_description, summarize_case
from .errors import APIError
from .utils import parse_json


ai_assist_bp = Blueprint("ai_assist", __name__)


@ai_assist_bp.post("/ai/optimize-description")
@active_user_required
def optimize_description_endpoint():
    payload = parse_json(DescriptionOptimizeRequest)
    return jsonify(
        {
            "data": optimize_description(payload.text),
            "message": "描述已优化",
        }
    )


@ai_assist_bp.post("/ai/summarize-case")
@active_user_required
def summarize_case_endpoint():
    payload = parse_json(CaseSummaryRequest)
    lost_case = db.session.get(LostCase, payload.case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    user = get_current_user()
    if (
        user.role != "ADMIN"
        and user.user_id != lost_case.pet.owner_id
        and user.user_id != lost_case.publisher_id
    ):
        raise APIError("CASE_SUMMARY_ACCESS_DENIED", "无权生成该事件摘要", 403)
    return jsonify(
        {
            "data": summarize_case(lost_case),
            "message": "事件摘要已生成",
        }
    )
