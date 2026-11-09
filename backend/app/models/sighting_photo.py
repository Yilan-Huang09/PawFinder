from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class SightingPhoto(db.Model):
    __tablename__ = "sighting_photos"

    photo_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    sighting_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("sightings.sighting_id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    sighting: Mapped["Sighting"] = relationship(back_populates="photos")

    def to_dict(self) -> dict[str, Any]:
        return {
            "photo_id": self.photo_id,
            "sighting_id": self.sighting_id,
            "photo_url": self.photo_url,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


from .sighting import Sighting  # noqa: E402
