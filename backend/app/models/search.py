from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class SearchArea(db.Model):
    __tablename__ = "search_areas"

    area_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("lost_cases.case_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )
    area_name: Mapped[str] = mapped_column(String(100), nullable=False)
    center_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    center_longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    radius_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    lost_case: Mapped["LostCase"] = relationship()
    task: Mapped["SearchTask | None"] = relationship(
        back_populates="area",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def to_dict(self, include_task: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "area_id": self.area_id,
            "case_id": self.case_id,
            "created_by": self.created_by,
            "area_name": self.area_name,
            "center_latitude": float(self.center_latitude),
            "center_longitude": float(self.center_longitude),
            "radius_meters": self.radius_meters,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_task:
            payload["task"] = self.task.to_dict() if self.task else None
        return payload


class SearchTask(db.Model):
    __tablename__ = "search_tasks"
    __table_args__ = (UniqueConstraint("area_id", name="uq_search_tasks_area"),)

    task_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    area_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("search_areas.area_id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    volunteer_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="SET NULL", onupdate="RESTRICT"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="AVAILABLE", index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    report: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    area: Mapped[SearchArea] = relationship(back_populates="task")

    def to_dict(self, include_area: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "task_id": self.task_id,
            "area_id": self.area_id,
            "volunteer_id": self.volunteer_id,
            "status": self.status,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "report": self.report,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_area:
            payload["area"] = self.area.to_dict(include_task=False)
        return payload


from .lost_case import LostCase  # noqa: E402
