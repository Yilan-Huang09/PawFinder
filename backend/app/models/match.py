from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class CaseSightingMatch(db.Model):
    __tablename__ = "case_sighting_matches"
    __table_args__ = (
        UniqueConstraint("case_id", "sighting_id", name="uq_matches_case_sighting"),
    )

    match_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("lost_cases.case_id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    sighting_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("sightings.sighting_id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    appearance_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    distance_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    time_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    total_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, index=True)
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    match_reason: Mapped[str] = mapped_column(Text, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(30), nullable=False, default="rule-v1")
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    reviewed_by: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="SET NULL", onupdate="RESTRICT"),
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    lost_case: Mapped["LostCase"] = relationship()
    sighting: Mapped["Sighting"] = relationship()

    def to_dict(self, include_sighting: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "match_id": self.match_id,
            "case_id": self.case_id,
            "sighting_id": self.sighting_id,
            "appearance_score": float(self.appearance_score),
            "distance_score": float(self.distance_score),
            "time_score": float(self.time_score),
            "total_score": float(self.total_score),
            "distance_km": float(self.distance_km),
            "match_reason": self.match_reason,
            "algorithm_version": self.algorithm_version,
            "review_status": self.review_status,
            "reviewed_by": self.reviewed_by,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
        if include_sighting:
            payload["sighting"] = self.sighting.to_dict()
        return payload


from .lost_case import LostCase  # noqa: E402
from .sighting import Sighting  # noqa: E402
