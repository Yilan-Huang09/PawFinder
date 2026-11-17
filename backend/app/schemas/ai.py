from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DescriptionOptimizeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(min_length=1, max_length=2000)


class CaseSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: int = Field(gt=0)
