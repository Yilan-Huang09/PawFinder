from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


class Sighting(db.Model):
    __tablename__ = "sightings"

    sighting_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    species: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    breed_guess: Mapped[str | None] = mapped_column(String(80))
    primary_color: Mapped[str] = mapped_column(String(50), nullable=False)
    secondary_color: Mapped[str | None] = mapped_column(String(50))
    gender_guess: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    size_guess: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    seen_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    direction: Mapped[str | None] = mapped_column(String(80))
    confidence: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=3)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)
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

    photos: Mapped[list["SightingPhoto"]] = relationship(
        back_populates="sighting",
        cascade="all, delete-orphan",
        order_by="SightingPhoto.sort_order, SightingPhoto.photo_id",
    )

    def to_dict(self, include_photos: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "sighting_id": self.sighting_id,
            "reporter_id": self.reporter_id,
            "species": self.species,
            "breed_guess": self.breed_guess,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "gender_guess": self.gender_guess,
            "size_guess": self.size_guess,
            "seen_time": self.seen_time.isoformat() if self.seen_time else None,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "address": self.address,
            "direction": self.direction,
            "confidence": self.confidence,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_photos:
            payload["photos"] = [photo.to_dict() for photo in self.photos]
        return payload


from .sighting_photo import SightingPhoto  # noqa: E402
