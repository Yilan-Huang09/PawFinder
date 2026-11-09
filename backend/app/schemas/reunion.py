from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .case import _validate_not_future


class ReunionCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    finder_id: int | None = Field(default=None, gt=0)
    reunion_time: datetime
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address: str = Field(min_length=2, max_length=255)
    method: str | None = Field(default=None, max_length=100)
    note: str | None = Field(default=None, max_length=5000)

    _time_validator = field_validator("reunion_time")(_validate_not_future)

    @model_validator(mode="after")
    def coordinates_must_be_paired(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("寻回位置的经纬度必须同时填写")
        return self
