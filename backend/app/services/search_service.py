from __future__ import annotations

from datetime import datetime

from sqlalchemy import update

from ..api.errors import APIError
from ..extensions import db
from ..models.search import SearchTask


def claim_task(task_id: int, volunteer_id: int) -> SearchTask:
    task = db.session.get(SearchTask, task_id)
    if task is None:
        raise APIError("TASK_NOT_FOUND", "搜寻任务不存在", 404)
    if task.area.status != "OPEN" or task.area.lost_case.status != "SEARCHING":
        raise APIError("TASK_NOT_AVAILABLE", "该搜寻任务已关闭", 409)

    result = db.session.execute(
        update(SearchTask)
        .where(
            SearchTask.task_id == task_id,
            SearchTask.status == "AVAILABLE",
            SearchTask.volunteer_id.is_(None),
        )
        .values(
            volunteer_id=volunteer_id,
            status="CLAIMED",
            accepted_at=datetime.now(),
            started_at=None,
            completed_at=None,
            report=None,
        )
    )
    if result.rowcount != 1:
        db.session.rollback()
        raise APIError("TASK_ALREADY_CLAIMED", "该搜寻区域已被其他志愿者认领", 409)
    db.session.commit()
    return db.session.get(SearchTask, task_id)


def update_task_progress(
    task_id: int,
    volunteer_id: int,
    status: str,
    report: str | None,
) -> SearchTask:
    task = db.session.get(SearchTask, task_id)
    if task is None:
        raise APIError("TASK_NOT_FOUND", "搜寻任务不存在", 404)
    if task.volunteer_id != volunteer_id:
        raise APIError("TASK_ACCESS_DENIED", "只能更新自己认领的任务", 403)
    if task.status not in {"CLAIMED", "IN_PROGRESS"}:
        raise APIError("TASK_NOT_EDITABLE", "当前任务状态不能更新进度", 409)

    now = datetime.now()
    if status == "IN_PROGRESS":
        task.status = "IN_PROGRESS"
        task.started_at = task.started_at or now
    elif status == "COMPLETED":
        task.status = "COMPLETED"
        task.started_at = task.started_at or now
        task.completed_at = now
    task.report = report
    db.session.commit()
    return task


def release_task(task_id: int, volunteer_id: int) -> SearchTask:
    task = db.session.get(SearchTask, task_id)
    if task is None:
        raise APIError("TASK_NOT_FOUND", "搜寻任务不存在", 404)
    if task.volunteer_id != volunteer_id:
        raise APIError("TASK_ACCESS_DENIED", "只能释放自己认领的任务", 403)
    if task.status not in {"CLAIMED", "IN_PROGRESS"}:
        raise APIError("TASK_NOT_RELEASABLE", "当前任务状态不能释放", 409)
    task.volunteer_id = None
    task.status = "AVAILABLE"
    task.accepted_at = None
    task.started_at = None
    task.completed_at = None
    task.report = None
    db.session.commit()
    return task
