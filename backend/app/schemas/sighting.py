from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .case import _validate_not_future


Gender = Literal["MALE", "FEMALE", "UNKNOWN"]
PetSize = Literal["SMALL", "MEDIUM", "LARGE", "UNKNOWN"]


def _uppercase(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    return value.upper()


class SightingRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class SightingCreateRequest(SightingRequest):
    species: str = Field(min_length=1, max_length=30)
    breed_guess: str | None = Field(default=None, max_length=80)
    primary_color: str = Field(min_length=1, max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    gender_guess: Gender = "UNKNOWN"
    size_guess: PetSize = "UNKNOWN"
    seen_time: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str = Field(min_length=2, max_length=255)
    direction: str | None = Field(default=None, max_length=80)
    confidence: int = Field(default=3, ge=1, le=5)
    description: str | None = Field(default=None, max_length=5000)

    _species_upper = field_validator("species")(_uppercase)
    _primary_color_upper = field_validator("primary_color")(_uppercase)
    _secondary_color_upper = field_validator("secondary_color")(_uppercase)
    _time_validator = field_validator("seen_time")(_validate_not_future)


class SightingUpdateRequest(SightingRequest):
    species: str | None = Field(default=None, min_length=1, max_length=30)
    breed_guess: str | None = Field(default=None, max_length=80)
    primary_color: str | None = Field(default=None, min_length=1, max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    gender_guess: Gender | None = None
    size_guess: PetSize | None = None
    seen_time: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, min_length=2, max_length=255)
    direction: str | None = Field(default=None, max_length=80)
    confidence: int | None = Field(default=None, ge=1, le=5)
    description: str | None = Field(default=None, max_length=5000)

    _species_upper = field_validator("species")(_uppercase)
    _primary_color_upper = field_validator("primary_color")(_uppercase)
    _secondary_color_upper = field_validator("secondary_color")(_uppercase)
    _time_validator = field_validator("seen_time")(
        lambda value: _validate_not_future(value) if value else value
    )

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("至少需要提交一个要修改的字段")
        return self
