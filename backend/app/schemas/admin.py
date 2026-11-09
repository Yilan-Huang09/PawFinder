from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class SightingStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ACTIVE", "HIDDEN", "INVALID"]


class CaseStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SEARCHING", "CLOSED"]
