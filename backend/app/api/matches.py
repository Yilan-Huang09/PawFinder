from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify

from ..extensions import db
from ..models.lost_case import LostCase
from ..models.match import CaseSightingMatch
from ..schemas.match import MatchReviewRequest
from ..security import active_user_required, get_current_user
from ..services.matching import recalculate_for_case
from .errors import APIError
from .utils import parse_json


matches_bp = Blueprint("matches", __name__)


def _owner_case(case_id: int) -> LostCase:
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    user = get_current_user()
    if lost_case.pet.owner_id != user.user_id and lost_case.publisher_id != user.user_id:
        raise APIError("MATCH_ACCESS_DENIED", "只有事件主人可以查看或核实匹配", 403)
    return lost_case


@matches_bp.get("/cases/<int:case_id>/matches")
@active_user_required
def list_case_matches(case_id: int):
    _owner_case(case_id)
    matches = (
        CaseSightingMatch.query.filter_by(case_id=case_id)
        .order_by(CaseSightingMatch.total_score.desc(), CaseSightingMatch.generated_at.desc())
        .all()
    )
    return jsonify({"data": [item.to_dict() for item in matches], "message": "获取成功"})


@matches_bp.post("/cases/<int:case_id>/recalculate")
@active_user_required
def recalculate_case_matches(case_id: int):
    lost_case = _owner_case(case_id)
    if lost_case.status != "SEARCHING":
        raise APIError("CASE_NOT_SEARCHING", "只有寻找中的事件可以重新匹配", 409)
    match_ids = recalculate_for_case(case_id)
    return jsonify(
        {
            "data": {"case_id": case_id, "match_ids": match_ids, "count": len(match_ids)},
            "message": "候选线索已重新计算",
        }
    )


@matches_bp.patch("/matches/<int:match_id>/review")
@active_user_required
def review_match(match_id: int):
    match = db.session.get(CaseSightingMatch, match_id)
    if match is None:
        raise APIError("MATCH_NOT_FOUND", "匹配结果不存在", 404)
    _owner_case(match.case_id)
    payload = parse_json(MatchReviewRequest)
    match.review_status = payload.review_status
    match.reviewed_by = get_current_user().user_id
    match.reviewed_at = datetime.now()
    db.session.commit()
    return jsonify({"data": match.to_dict(), "message": "匹配核实状态已更新"})
