from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..extensions import db
from ..models.pet import Pet
from ..models.pet_photo import PetPhoto
from ..schemas.pet import PetCreateRequest, PetUpdateRequest
from ..security import active_user_required, get_current_user
from ..services.upload_service import delete_uploaded_file, save_uploaded_image
from .errors import APIError
from .utils import parse_json


pets_bp = Blueprint("pets", __name__, url_prefix="/pets")


def _owned_pet(pet_id: int) -> Pet:
    pet = db.session.get(Pet, pet_id)
    if pet is None:
        raise APIError("PET_NOT_FOUND", "宠物档案不存在", 404)
    if pet.owner_id != get_current_user().user_id:
        raise APIError("PET_ACCESS_DENIED", "无权操作该宠物档案", 403)
    return pet


@pets_bp.get("")
@active_user_required
def list_pets():
    user = get_current_user()
    query = Pet.query.filter_by(owner_id=user.user_id)
    if request.args.get("include_inactive") != "1":
        query = query.filter_by(status="ACTIVE")
    pets = query.order_by(Pet.created_at.desc(), Pet.pet_id.desc()).all()
    return jsonify({"data": [pet.to_dict() for pet in pets], "message": "获取成功"})


@pets_bp.post("")
@active_user_required
def create_pet():
    payload = parse_json(PetCreateRequest)
    pet = Pet(
        owner_id=get_current_user().user_id,
        **payload.model_dump(),
        status="ACTIVE",
    )
    db.session.add(pet)
    db.session.commit()
    return jsonify({"data": pet.to_dict(), "message": "宠物档案已创建"}), 201


@pets_bp.get("/<int:pet_id>")
@active_user_required
def get_pet(pet_id: int):
    pet = _owned_pet(pet_id)
    return jsonify({"data": pet.to_dict(), "message": "获取成功"})


@pets_bp.patch("/<int:pet_id>")
@active_user_required
def update_pet(pet_id: int):
    pet = _owned_pet(pet_id)
    payload = parse_json(PetUpdateRequest)
    for field_name in payload.model_fields_set:
        setattr(pet, field_name, getattr(payload, field_name))
    db.session.commit()
    return jsonify({"data": pet.to_dict(), "message": "宠物档案已更新"})


@pets_bp.delete("/<int:pet_id>")
@active_user_required
def deactivate_pet(pet_id: int):
    pet = _owned_pet(pet_id)
    pet.status = "INACTIVE"
    db.session.commit()
    return jsonify({"data": pet.to_dict(), "message": "宠物档案已停用"})


@pets_bp.post("/<int:pet_id>/photos")
@active_user_required
def upload_pet_photo(pet_id: int):
    pet = _owned_pet(pet_id)
    photo_count = PetPhoto.query.filter_by(pet_id=pet.pet_id).count()
    if photo_count >= int(current_app.config["MAX_PET_PHOTOS"]):
        raise APIError("PHOTO_LIMIT_REACHED", "每只宠物最多上传6张照片", 409)
    upload = request.files.get("photo")
    if upload is None:
        raise APIError("PHOTO_REQUIRED", "请选择要上传的图片", 422)

    relative_path = save_uploaded_image(upload, "pets")
    photo = PetPhoto(
        pet_id=pet.pet_id,
        photo_url=relative_path,
        is_cover=photo_count == 0,
        sort_order=photo_count,
    )
    try:
        db.session.add(photo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_uploaded_file(relative_path)
        raise
    return jsonify({"data": photo.to_dict(), "message": "照片上传成功"}), 201


@pets_bp.put("/<int:pet_id>/photos/<int:photo_id>/cover")
@active_user_required
def set_cover_photo(pet_id: int, photo_id: int):
    pet = _owned_pet(pet_id)
    photo = PetPhoto.query.filter_by(photo_id=photo_id, pet_id=pet.pet_id).first()
    if photo is None:
        raise APIError("PHOTO_NOT_FOUND", "宠物照片不存在", 404)
    PetPhoto.query.filter_by(pet_id=pet.pet_id).update(
        {PetPhoto.is_cover: False},
        synchronize_session="fetch",
    )
    photo.is_cover = True
    db.session.commit()
    return jsonify({"data": photo.to_dict(), "message": "封面照片已更新"})


@pets_bp.delete("/<int:pet_id>/photos/<int:photo_id>")
@active_user_required
def delete_pet_photo(pet_id: int, photo_id: int):
    pet = _owned_pet(pet_id)
    photo = PetPhoto.query.filter_by(photo_id=photo_id, pet_id=pet.pet_id).first()
    if photo is None:
        raise APIError("PHOTO_NOT_FOUND", "宠物照片不存在", 404)

    relative_path = photo.photo_url
    was_cover = photo.is_cover
    db.session.delete(photo)
    db.session.flush()
    if was_cover:
        replacement = (
            PetPhoto.query.filter_by(pet_id=pet.pet_id)
            .order_by(PetPhoto.sort_order, PetPhoto.photo_id)
            .first()
        )
        if replacement:
            replacement.is_cover = True
    db.session.commit()
    delete_uploaded_file(relative_path)
    return jsonify({"data": None, "message": "照片已删除"})
