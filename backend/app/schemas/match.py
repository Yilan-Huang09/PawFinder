from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class MatchReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_status: Literal["CONFIRMED", "REJECTED"]
