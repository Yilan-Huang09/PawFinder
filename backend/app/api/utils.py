from __future__ import annotations

from typing import TypeVar

from flask import request
from pydantic import BaseModel

from .errors import APIError


SchemaT = TypeVar("SchemaT", bound=BaseModel)


def parse_json(schema: type[SchemaT]) -> SchemaT:
    if not request.is_json:
        raise APIError(
            "JSON_BODY_REQUIRED",
            "请求体必须使用 JSON 格式",
            415,
        )
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise APIError(
            "INVALID_JSON_BODY",
            "请求体必须是 JSON 对象",
            422,
        )
    return schema.model_validate(payload)
