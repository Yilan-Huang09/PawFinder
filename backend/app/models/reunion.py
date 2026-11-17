from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class ReunionRecord(db.Model):
    __tablename__ = "reunion_records"
    __table_args__ = (UniqueConstraint("case_id", name="uq_reunion_records_case"),)

    reunion_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("lost_cases.case_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )
    finder_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="SET NULL", onupdate="RESTRICT"),
    )
    confirmed_by: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )
    reunion_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str | None] = mapped_column(String(100))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    lost_case: Mapped["LostCase"] = relationship()

    def to_dict(self) -> dict[str, Any]:
        return {
            "reunion_id": self.reunion_id,
            "case_id": self.case_id,
            "finder_id": self.finder_id,
            "confirmed_by": self.confirmed_by,
            "reunion_time": self.reunion_time.isoformat() if self.reunion_time else None,
            "latitude": float(self.latitude) if self.latitude is not None else None,
            "longitude": float(self.longitude) if self.longitude is not None else None,
            "address": self.address,
            "method": self.method,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


from .lost_case import LostCase  # noqa: E402
