from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .types import ID_TYPE


class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(
        ID_TYPE,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    related_case_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey("lost_cases.case_id", ondelete="SET NULL", onupdate="RESTRICT"),
    )
    related_match_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey(
            "case_sighting_matches.match_id",
            ondelete="SET NULL",
            onupdate="RESTRICT",
        ),
    )
    related_task_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey("search_tasks.task_id", ondelete="SET NULL", onupdate="RESTRICT"),
    )
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime)

    def to_dict(self) -> dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "related_case_id": self.related_case_id,
            "related_match_id": self.related_match_id,
            "related_task_id": self.related_task_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }
