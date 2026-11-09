from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from ..extensions import db
from ..models.lost_case import LostCase
from ..models.pet import Pet
from ..schemas.case import CaseCreateRequest, CaseUpdateRequest
from ..security import active_user_required, get_current_user
from ..services.matching import recalculate_for_case
from .errors import APIError
from .utils import parse_json


cases_bp = Blueprint("cases", __name__, url_prefix="/cases")


def _case_for_owner(case_id: int) -> LostCase:
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    user = get_current_user()
    if lost_case.pet.owner_id != user.user_id and lost_case.publisher_id != user.user_id:
        raise APIError("CASE_ACCESS_DENIED", "无权操作该走失事件", 403)
    return lost_case


@cases_bp.get("")
def list_cases():
    try:
        page = max(1, int(request.args.get("page", "1")))
        per_page = min(100, max(1, int(request.args.get("per_page", "12"))))
    except ValueError as exc:
        raise APIError("INVALID_PAGINATION", "分页参数必须是整数", 422) from exc

    query = LostCase.query.join(Pet)
    status = request.args.get("status", "SEARCHING").upper()
    if status != "ALL":
        if status not in {"SEARCHING", "REUNITED", "CLOSED"}:
            raise APIError("INVALID_CASE_STATUS", "走失事件状态筛选无效", 422)
        query = query.filter(LostCase.status == status)
    species = request.args.get("species")
    if species:
        query = query.filter(Pet.species == species.upper())
    keyword = request.args.get("keyword", "").strip()
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(Pet.name.like(pattern), LostCase.address.like(pattern)))

    pagination = query.order_by(LostCase.lost_time.desc(), LostCase.case_id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    return jsonify(
        {
            "data": [item.to_dict(reveal_contact=False) for item in pagination.items],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
            "message": "获取成功",
        }
    )


@cases_bp.post("")
@active_user_required
def create_case():
    payload = parse_json(CaseCreateRequest)
    user = get_current_user()
    pet = db.session.get(Pet, payload.pet_id)
    if pet is None:
        raise APIError("PET_NOT_FOUND", "宠物档案不存在", 404)
    if pet.owner_id != user.user_id:
        raise APIError("PET_ACCESS_DENIED", "只能为自己的宠物发布走失事件", 403)
    if pet.status != "ACTIVE":
        raise APIError("PET_INACTIVE", "已停用的宠物档案不能发布走失事件", 409)
    active_case = LostCase.query.filter_by(pet_id=pet.pet_id, status="SEARCHING").first()
    if active_case is not None:
        raise APIError("ACTIVE_CASE_ALREADY_EXISTS", "该宠物已有寻找中的事件", 409)

    lost_case = LostCase(
        publisher_id=user.user_id,
        status="SEARCHING",
        **payload.model_dump(),
    )
    db.session.add(lost_case)
    db.session.commit()
    recalculate_for_case(lost_case.case_id)
    return jsonify({"data": lost_case.to_dict(True), "message": "走失事件已发布"}), 201


@cases_bp.get("/<int:case_id>")
def get_case(case_id: int):
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    return jsonify({"data": lost_case.to_dict(False), "message": "获取成功"})


@cases_bp.patch("/<int:case_id>")
@active_user_required
def update_case(case_id: int):
    lost_case = _case_for_owner(case_id)
    if lost_case.status != "SEARCHING":
        raise APIError("CASE_NOT_EDITABLE", "只有寻找中的事件可以修改", 409)
    payload = parse_json(CaseUpdateRequest)
    for field_name in payload.model_fields_set:
        value = getattr(payload, field_name)
        setattr(lost_case, field_name, value)
    if payload.status == "CLOSED":
        lost_case.closed_at = datetime.now()
    db.session.commit()
    if lost_case.status == "SEARCHING":
        recalculate_for_case(lost_case.case_id)
    return jsonify({"data": lost_case.to_dict(True), "message": "走失事件已更新"})
