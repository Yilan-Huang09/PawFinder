from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchAreaCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    area_name: str = Field(min_length=2, max_length=100)
    center_latitude: float = Field(ge=-90, le=90)
    center_longitude: float = Field(ge=-180, le=180)
    radius_meters: int = Field(ge=1, le=20000)
    description: str | None = Field(default=None, max_length=500)


class TaskProgressRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    status: Literal["IN_PROGRESS", "COMPLETED"]
    report: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def completed_task_requires_report(self):
        if self.status == "COMPLETED" and not self.report:
            raise ValueError("完成任务时必须填写搜寻反馈")
        return self
