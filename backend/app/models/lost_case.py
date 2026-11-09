from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .types import ID_TYPE


def mask_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    if len(phone) >= 7:
        return f"{phone[:3]}****{phone[-4:]}"
    return "****"


class LostCase(db.Model):
    __tablename__ = "lost_cases"

    case_id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("pets.pet_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    publisher_id: Mapped[int] = mapped_column(
        ID_TYPE,
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    lost_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SEARCHING", index=True)
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
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    pet: Mapped["Pet"] = relationship()

    def to_dict(self, reveal_contact: bool = False) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "pet_id": self.pet_id,
            "publisher_id": self.publisher_id,
            "lost_time": self.lost_time.isoformat() if self.lost_time else None,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "address": self.address,
            "description": self.description,
            "contact_phone": self.contact_phone if reveal_contact else mask_phone(self.contact_phone),
            "status": self.status,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "pet": self.pet.to_dict(include_photos=False),
        }


from .pet import Pet  # noqa: E402
