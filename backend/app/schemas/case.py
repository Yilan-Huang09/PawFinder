from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .auth import _validate_phone


LOCAL_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")


def _validate_not_future(value: datetime) -> datetime:
    comparable = (
        value.astimezone(LOCAL_TIMEZONE).replace(tzinfo=None)
        if value.tzinfo
        else value
    )
    local_now = datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)
    if comparable > local_now:
        raise ValueError("时间不能晚于当前时间")
    return comparable


class CaseRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class CaseCreateRequest(CaseRequest):
    pet_id: int = Field(gt=0)
    lost_time: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    contact_phone: str | None = None

    _time_validator = field_validator("lost_time")(_validate_not_future)
    _phone_validator = field_validator("contact_phone")(_validate_phone)


class CaseUpdateRequest(CaseRequest):
    lost_time: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    contact_phone: str | None = None
    status: Literal["CLOSED"] | None = None

    _time_validator = field_validator("lost_time")(
        lambda value: _validate_not_future(value) if value else value
    )
    _phone_validator = field_validator("contact_phone")(_validate_phone)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("至少需要提交一个要修改的字段")
        return self
