from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class Pet(db.Model):
    __tablename__ = "pets"

    pet_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    species: Mapped[str] = mapped_column(String(30), nullable=False)
    breed: Mapped[str | None] = mapped_column(String(80))
    primary_color: Mapped[str] = mapped_column(String(50), nullable=False)
    secondary_color: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    size: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    birth_date: Mapped[date | None] = mapped_column(Date)
    distinctive_features: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
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

    photos: Mapped[list["PetPhoto"]] = relationship(
        back_populates="pet",
        cascade="all, delete-orphan",
        order_by="PetPhoto.sort_order, PetPhoto.photo_id",
    )

    def to_dict(self, include_photos: bool = True) -> dict[str, Any]:
        cover = next((photo for photo in self.photos if photo.is_cover), None)
        payload: dict[str, Any] = {
            "pet_id": self.pet_id,
            "owner_id": self.owner_id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "gender": self.gender,
            "size": self.size,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "distinctive_features": self.distinctive_features,
            "status": self.status,
            "cover_photo_url": cover.photo_url if cover else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_photos:
            payload["photos"] = [photo.to_dict() for photo in self.photos]
        return payload


from .pet_photo import PetPhoto  # noqa: E402
