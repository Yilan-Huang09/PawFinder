from __future__ import annotations

from ..extensions import db
from ..models.notification import Notification
from ..models.search import SearchTask


TASK_STATUS_COPY = {
    "CLAIMED": ("搜寻任务已被认领", "有志愿者认领了搜寻区域“{area_name}”。"),
    "IN_PROGRESS": ("搜寻任务正在进行", "搜寻区域“{area_name}”已开始执行。"),
    "COMPLETED": ("搜寻任务已完成", "搜寻区域“{area_name}”已提交搜寻反馈。"),
    "AVAILABLE": ("搜寻任务已释放", "搜寻区域“{area_name}”已重新开放认领。"),
}


def add_notification(
    *,
    user_id: int,
    type: str,
    title: str,
    content: str,
    related_case_id: int | None = None,
    related_match_id: int | None = None,
    related_task_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        content=content,
        related_case_id=related_case_id,
        related_match_id=related_match_id,
        related_task_id=related_task_id,
        is_read=False,
    )
    db.session.add(notification)
    return notification


def add_task_status_notification(task: SearchTask) -> Notification:
    title, content_template = TASK_STATUS_COPY[task.status]
    lost_case = task.area.lost_case
    return add_notification(
        user_id=lost_case.pet.owner_id,
        type="TASK_STATUS",
        title=title,
        content=content_template.format(area_name=task.area.area_name),
        related_case_id=lost_case.case_id,
        related_task_id=task.task_id,
    )
