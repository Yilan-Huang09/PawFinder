from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..extensions import db
from ..models.sighting import Sighting
from ..models.sighting_photo import SightingPhoto
from ..schemas.sighting import SightingCreateRequest, SightingUpdateRequest
from ..security import active_user_required, get_current_user
from ..services.matching import recalculate_for_sighting
from ..services.upload_service import delete_uploaded_file, save_uploaded_image
from .errors import APIError
from .utils import parse_json


sightings_bp = Blueprint("sightings", __name__, url_prefix="/sightings")


def _owned_sighting(sighting_id: int) -> Sighting:
    sighting = db.session.get(Sighting, sighting_id)
    if sighting is None:
        raise APIError("SIGHTING_NOT_FOUND", "目击线索不存在", 404)
    if sighting.reporter_id != get_current_user().user_id:
        raise APIError("SIGHTING_ACCESS_DENIED", "无权操作该目击线索", 403)
    return sighting


@sightings_bp.get("")
def list_sightings():
    try:
        page = max(1, int(request.args.get("page", "1")))
        per_page = min(100, max(1, int(request.args.get("per_page", "20"))))
    except ValueError as exc:
        raise APIError("INVALID_PAGINATION", "分页参数必须是整数", 422) from exc
    query = Sighting.query.filter_by(status="ACTIVE")
    species = request.args.get("species")
    if species:
        query = query.filter(Sighting.species == species.upper())
    pagination = query.order_by(Sighting.seen_time.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    return jsonify(
        {
            "data": [item.to_dict() for item in pagination.items],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
            "message": "获取成功",
        }
    )


@sightings_bp.post("")
@active_user_required
def create_sighting():
    payload = parse_json(SightingCreateRequest)
    sighting = Sighting(
        reporter_id=get_current_user().user_id,
        status="ACTIVE",
        **payload.model_dump(),
    )
    db.session.add(sighting)
    db.session.commit()
    recalculate_for_sighting(sighting.sighting_id)
    return jsonify({"data": sighting.to_dict(), "message": "目击线索已提交"}), 201


@sightings_bp.get("/<int:sighting_id>")
def get_sighting(sighting_id: int):
    sighting = db.session.get(Sighting, sighting_id)
    if sighting is None or sighting.status != "ACTIVE":
        raise APIError("SIGHTING_NOT_FOUND", "目击线索不存在", 404)
    return jsonify({"data": sighting.to_dict(), "message": "获取成功"})


@sightings_bp.patch("/<int:sighting_id>")
@active_user_required
def update_sighting(sighting_id: int):
    sighting = _owned_sighting(sighting_id)
    if sighting.status != "ACTIVE":
        raise APIError("SIGHTING_NOT_EDITABLE", "无效线索不能修改", 409)
    payload = parse_json(SightingUpdateRequest)
    for field_name in payload.model_fields_set:
        setattr(sighting, field_name, getattr(payload, field_name))
    db.session.commit()
    recalculate_for_sighting(sighting.sighting_id)
    return jsonify({"data": sighting.to_dict(), "message": "目击线索已更新"})


@sightings_bp.delete("/<int:sighting_id>")
@active_user_required
def invalidate_sighting(sighting_id: int):
    sighting = _owned_sighting(sighting_id)
    sighting.status = "INVALID"
    db.session.commit()
    return jsonify({"data": sighting.to_dict(), "message": "目击线索已撤销"})


@sightings_bp.post("/<int:sighting_id>/photos")
@active_user_required
def upload_sighting_photo(sighting_id: int):
    sighting = _owned_sighting(sighting_id)
    photo_count = SightingPhoto.query.filter_by(sighting_id=sighting.sighting_id).count()
    if photo_count >= int(current_app.config["MAX_SIGHTING_PHOTOS"]):
        raise APIError("PHOTO_LIMIT_REACHED", "每条线索最多上传4张照片", 409)
    upload = request.files.get("photo")
    if upload is None:
        raise APIError("PHOTO_REQUIRED", "请选择要上传的图片", 422)
    relative_path = save_uploaded_image(upload, "sightings")
    photo = SightingPhoto(
        sighting_id=sighting.sighting_id,
        photo_url=relative_path,
        sort_order=photo_count,
    )
    try:
        db.session.add(photo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_uploaded_file(relative_path)
        raise
    return jsonify({"data": photo.to_dict(), "message": "线索照片上传成功"}), 201
