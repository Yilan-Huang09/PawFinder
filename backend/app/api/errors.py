from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from flask import Flask, g, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


@dataclass
class APIError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] = field(default_factory=dict)


def _error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
):
    response = jsonify(
        {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": getattr(g, "request_id", None),
        }
    )
    response.status_code = status_code
    return response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        return _error_response(
            error.code,
            error.message,
            error.status_code,
            error.details,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return _error_response(
            "VALIDATION_ERROR",
            "提交的数据不符合要求",
            422,
            {"errors": error.errors(include_url=False)},
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        if error.code == 404:
            return _error_response(
                "RESOURCE_NOT_FOUND",
                "请求的资源不存在",
                404,
            )
        return _error_response(
            f"HTTP_{error.code}",
            error.description,
            error.code or 500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        if app.config.get("TESTING"):
            raise error
        app.logger.exception(
            "Unhandled request error",
            extra={"request_id": getattr(g, "request_id", None)},
        )
        return _error_response(
            "INTERNAL_ERROR",
            "服务器暂时无法处理请求",
            500,
        )
