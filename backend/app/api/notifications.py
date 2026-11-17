from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models.notification import Notification
from ..security import active_user_required, get_current_user
from .errors import APIError


notifications_bp = Blueprint("notifications", __name__)


def _owned_notification(notification_id: int) -> Notification:
    notification = Notification.query.filter_by(
        notification_id=notification_id,
        user_id=get_current_user().user_id,
    ).first()
    if notification is None:
        raise APIError("NOTIFICATION_NOT_FOUND", "通知不存在", 404)
    return notification


@notifications_bp.get("/notifications")
@active_user_required
def list_notifications():
    user_id = get_current_user().user_id
    unread_only = request.args.get("unread_only", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    notifications = query.order_by(
        Notification.created_at.desc(),
        Notification.notification_id.desc(),
    ).all()
    unread_count = Notification.query.filter_by(
        user_id=user_id,
        is_read=False,
    ).count()
    return jsonify(
        {
            "data": [item.to_dict() for item in notifications],
            "meta": {"unread_count": unread_count},
            "message": "获取成功",
        }
    )


@notifications_bp.patch("/notifications/<int:notification_id>/read")
@active_user_required
def mark_notification_read(notification_id: int):
    notification = _owned_notification(notification_id)
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now()
        db.session.commit()
    return jsonify({"data": notification.to_dict(), "message": "通知已标记为已读"})


@notifications_bp.patch("/notifications/read-all")
@active_user_required
def mark_all_notifications_read():
    user_id = get_current_user().user_id
    unread = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    read_at = datetime.now()
    for notification in unread:
        notification.is_read = True
        notification.read_at = read_at
    db.session.commit()
    return jsonify(
        {
            "data": {"updated_count": len(unread)},
            "message": "全部通知已标记为已读",
        }
    )
