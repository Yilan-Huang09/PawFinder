from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Gender = Literal["MALE", "FEMALE", "UNKNOWN"]
PetSize = Literal["SMALL", "MEDIUM", "LARGE", "UNKNOWN"]


class PetRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


def _uppercase(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    return value.upper()


def _validate_birth_date(value: date | None) -> date | None:
    if value and value > date.today():
        raise ValueError("出生日期不能晚于今天")
    return value


class PetCreateRequest(PetRequest):
    name: str = Field(min_length=1, max_length=80)
    species: str = Field(min_length=1, max_length=30)
    breed: str | None = Field(default=None, max_length=80)
    primary_color: str = Field(min_length=1, max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    gender: Gender = "UNKNOWN"
    size: PetSize = "UNKNOWN"
    birth_date: date | None = None
    distinctive_features: str | None = Field(default=None, max_length=2000)

    _species_upper = field_validator("species")(_uppercase)
    _primary_color_upper = field_validator("primary_color")(_uppercase)
    _secondary_color_upper = field_validator("secondary_color")(_uppercase)
    _birth_date_validator = field_validator("birth_date")(_validate_birth_date)


class PetUpdateRequest(PetRequest):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    species: str | None = Field(default=None, min_length=1, max_length=30)
    breed: str | None = Field(default=None, max_length=80)
    primary_color: str | None = Field(default=None, min_length=1, max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    gender: Gender | None = None
    size: PetSize | None = None
    birth_date: date | None = None
    distinctive_features: str | None = Field(default=None, max_length=2000)

    _species_upper = field_validator("species")(_uppercase)
    _primary_color_upper = field_validator("primary_color")(_uppercase)
    _secondary_color_upper = field_validator("secondary_color")(_uppercase)
    _birth_date_validator = field_validator("birth_date")(_validate_birth_date)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("至少需要提交一个要修改的字段")
        return self
