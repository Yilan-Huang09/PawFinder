from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models.lost_case import LostCase
from ..models.search import SearchArea, SearchTask
from ..schemas.search import SearchAreaCreateRequest, TaskProgressRequest
from ..security import active_user_required, get_current_user
from ..services.search_service import claim_task, release_task, update_task_progress
from .errors import APIError
from .utils import parse_json


search_bp = Blueprint("search", __name__)


def _owner_case(case_id: int) -> LostCase:
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    user = get_current_user()
    if lost_case.pet.owner_id != user.user_id and lost_case.publisher_id != user.user_id:
        raise APIError("SEARCH_AREA_ACCESS_DENIED", "只有事件主人可以管理搜寻区域", 403)
    return lost_case


@search_bp.get("/cases/<int:case_id>/areas")
def list_search_areas(case_id: int):
    if db.session.get(LostCase, case_id) is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    areas = SearchArea.query.filter_by(case_id=case_id).order_by(SearchArea.area_id).all()
    return jsonify({"data": [area.to_dict() for area in areas], "message": "获取成功"})


@search_bp.post("/cases/<int:case_id>/areas")
@active_user_required
def create_search_area(case_id: int):
    lost_case = _owner_case(case_id)
    if lost_case.status != "SEARCHING":
        raise APIError("CASE_NOT_SEARCHING", "只有寻找中的事件可以创建搜寻区域", 409)
    payload = parse_json(SearchAreaCreateRequest)
    area = SearchArea(
        case_id=case_id,
        created_by=get_current_user().user_id,
        status="OPEN",
        **payload.model_dump(),
    )
    area.task = SearchTask(status="AVAILABLE")
    db.session.add(area)
    db.session.commit()
    return jsonify({"data": area.to_dict(), "message": "搜寻区域已创建"}), 201


@search_bp.get("/tasks")
@active_user_required
def list_tasks():
    scope = request.args.get("scope", "available")
    query = SearchTask.query
    if scope == "available":
        query = query.filter_by(status="AVAILABLE")
    elif scope == "mine":
        query = query.filter_by(volunteer_id=get_current_user().user_id)
    elif scope != "all":
        raise APIError("INVALID_TASK_SCOPE", "任务筛选范围无效", 422)
    tasks = query.order_by(SearchTask.updated_at.desc(), SearchTask.task_id.desc()).all()
    return jsonify({"data": [task.to_dict(include_area=True) for task in tasks], "message": "获取成功"})


@search_bp.post("/tasks/<int:task_id>/claim")
@active_user_required
def claim_search_task(task_id: int):
    task = claim_task(task_id, get_current_user().user_id)
    return jsonify({"data": task.to_dict(include_area=True), "message": "任务认领成功"})


@search_bp.patch("/tasks/<int:task_id>/progress")
@active_user_required
def update_search_task(task_id: int):
    payload = parse_json(TaskProgressRequest)
    task = update_task_progress(
        task_id,
        get_current_user().user_id,
        payload.status,
        payload.report,
    )
    return jsonify({"data": task.to_dict(include_area=True), "message": "任务进度已更新"})


@search_bp.post("/tasks/<int:task_id>/release")
@active_user_required
def release_search_task(task_id: int):
    task = release_task(task_id, get_current_user().user_id)
    return jsonify({"data": task.to_dict(include_area=True), "message": "任务已释放"})
