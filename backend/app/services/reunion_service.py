from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import current_app
from sqlalchemy import select

from ..api.errors import APIError
from ..extensions import db
from ..models.lost_case import LostCase
from ..models.reunion import ReunionRecord
from ..models.search import SearchArea, SearchTask
from ..models.user import User


def _validate_confirmation(lost_case: LostCase, confirmed_by: int) -> None:
    if lost_case.status != "SEARCHING":
        raise APIError("CASE_NOT_SEARCHING", "只有寻找中的事件可以确认寻回", 409)
    if confirmed_by not in {lost_case.pet.owner_id, lost_case.publisher_id}:
        raise APIError("REUNION_ACCESS_DENIED", "只有宠物主人或事件发布者可以确认寻回", 403)


def _confirm_with_orm(case_id: int, confirmed_by: int, payload: dict[str, Any]) -> ReunionRecord:
    try:
        lost_case = db.session.execute(
            select(LostCase).where(LostCase.case_id == case_id).with_for_update()
        ).scalar_one_or_none()
        if lost_case is None:
            raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
        _validate_confirmation(lost_case, confirmed_by)
        if payload.get("finder_id") and db.session.get(User, payload["finder_id"]) is None:
            raise APIError("FINDER_NOT_FOUND", "发现者账号不存在", 422)

        record = ReunionRecord(
            case_id=case_id,
            confirmed_by=confirmed_by,
            **payload,
        )
        db.session.add(record)
        lost_case.status = "REUNITED"
        lost_case.closed_at = datetime.now()

        areas = SearchArea.query.filter_by(case_id=case_id).all()
        for area in areas:
            area.status = "CLOSED"
            if area.task and area.task.status != "COMPLETED":
                area.task.status = "CANCELLED"
        db.session.commit()
        return record
    except APIError:
        db.session.rollback()
        raise
    except Exception:
        db.session.rollback()
        raise


def _confirm_with_procedure(
    case_id: int,
    confirmed_by: int,
    payload: dict[str, Any],
) -> ReunionRecord:
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None:
        raise APIError("CASE_NOT_FOUND", "走失事件不存在", 404)
    _validate_confirmation(lost_case, confirmed_by)
    if payload.get("finder_id") and db.session.get(User, payload["finder_id"]) is None:
        raise APIError("FINDER_NOT_FOUND", "发现者账号不存在", 422)
    db.session.remove()

    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    parameters = (
        case_id,
        payload.get("finder_id"),
        confirmed_by,
        payload["reunion_time"],
        payload.get("latitude"),
        payload.get("longitude"),
        payload["address"],
        payload.get("method"),
        payload.get("note"),
    )
    try:
        cursor.callproc("sp_confirm_reunion", parameters)
        while cursor.nextset():
            pass
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

    record = ReunionRecord.query.filter_by(case_id=case_id).first()
    if record is None:
        raise RuntimeError("Reunion procedure completed without a reunion record")
    return record


def confirm_reunion(
    case_id: int,
    confirmed_by: int,
    payload: dict[str, Any],
) -> ReunionRecord:
    if current_app.config.get("USE_REUNION_PROCEDURE", True):
        return _confirm_with_procedure(case_id, confirmed_by, payload)
    return _confirm_with_orm(case_id, confirmed_by, payload)
