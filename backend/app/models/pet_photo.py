from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class PetPhoto(db.Model):
    __tablename__ = "pet_photos"

    photo_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("pets.pet_id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    pet: Mapped["Pet"] = relationship(back_populates="photos")

    def to_dict(self) -> dict[str, Any]:
        return {
            "photo_id": self.photo_id,
            "pet_id": self.pet_id,
            "photo_url": self.photo_url,
            "is_cover": self.is_cover,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


from .pet import Pet  # noqa: E402
