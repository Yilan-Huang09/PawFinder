from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify

from ..extensions import db
from ..models.lost_case import LostCase
from ..models.match import CaseSightingMatch
from ..models.reunion import ReunionRecord
from ..models.search import SearchArea, SearchTask
from ..models.sighting import Sighting
from ..models.user import User
from ..schemas.admin import CaseStatusRequest, SightingStatusRequest
from ..security import admin_required
from .errors import APIError
from .utils import parse_json


admin_bp = Blueprint("admin", __name__)


def _status_count(model, status: str) -> int:
    return model.query.filter_by(status=status).count()


@admin_bp.get("/admin/statistics")
@admin_required
def admin_statistics():
    data = {
        "users": {
            "total": User.query.count(),
            "active": _status_count(User, "ACTIVE"),
            "disabled": _status_count(User, "DISABLED"),
        },
        "cases": {
            "total": LostCase.query.count(),
            "searching": _status_count(LostCase, "SEARCHING"),
            "reunited": _status_count(LostCase, "REUNITED"),
            "closed": _status_count(LostCase, "CLOSED"),
        },
        "sightings": {
            "total": Sighting.query.count(),
            "active": _status_count(Sighting, "ACTIVE"),
            "hidden": _status_count(Sighting, "HIDDEN"),
            "invalid": _status_count(Sighting, "INVALID"),
        },
        "matches": {
            "total": CaseSightingMatch.query.count(),
            "pending": CaseSightingMatch.query.filter_by(review_status="PENDING").count(),
            "high_score": CaseSightingMatch.query.filter(
                CaseSightingMatch.total_score >= 75
            ).count(),
        },
        "tasks": {
            "total": SearchTask.query.count(),
            "available": _status_count(SearchTask, "AVAILABLE"),
            "in_progress": _status_count(SearchTask, "IN_PROGRESS"),
            "completed": _status_count(SearchTask, "COMPLETED"),
        },
        "reunions": {"total": ReunionRecord.query.count()},
    }
    return jsonify({"data": data, "message": "统计数据获取成功"})


@admin_bp.patch("/admin/content/sightings/<int:sighting_id>/status")
@admin_required
def update_sighting_status(sighting_id: int):
    payload = parse_json(SightingStatusRequest)
    sighting = db.session.get(Sighting, sighting_id)
    if sighting is None:
        raise APIError("SIGHTING_NOT_FOUND", "目击线索不存在", 404)
    sighting.status = payload.status
    db.session.commit()
    return jsonify({"data": sighting.to_dict(), "message": "线索状态已更新"})


@admin_bp.patch("/admin/content/cases/<int:case_id>/status")
@admin_required
def update_case_status(case_id: int):
    payload = parse_json(CaseStatusRequest)
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    if lost_case.status == "REUNITED":
        raise APIError("REUNITED_CASE_IMMUTABLE", "已寻回事件不能由内容管理改为其他状态", 409)

    lost_case.status = payload.status
    lost_case.closed_at = datetime.now() if payload.status == "CLOSED" else None
    if payload.status == "CLOSED":
        areas = SearchArea.query.filter_by(case_id=case_id).all()
        for area in areas:
            area.status = "CLOSED"
            if area.task and area.task.status != "COMPLETED":
                area.task.status = "CANCELLED"
    db.session.commit()
    return jsonify(
        {
            "data": lost_case.to_dict(reveal_contact=True),
            "message": "事件状态已更新",
        }
    )
