from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, g, request

from .api import api_v1
from .api.errors import register_error_handlers
from .config import CONFIGS
from .extensions import cors, db, jwt


def create_app(
    config_name: str = "development",
    overrides: dict[str, Any] | None = None,
) -> Flask:
    if config_name not in CONFIGS:
        raise ValueError(f"Unknown configuration: {config_name}")

    app = Flask("pawfinder")
    app.config.from_object(CONFIGS[config_name])
    if overrides:
        app.config.update(overrides)

    if config_name == "production" and not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL is required in production")

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )

    app.register_blueprint(api_v1)
    register_error_handlers(app)

    @app.before_request
    def assign_request_id() -> None:
        supplied_request_id = request.headers.get("X-Request-ID", "").strip()
        g.request_id = supplied_request_id[:128] if supplied_request_id else uuid4().hex

    @app.after_request
    def attach_request_id(response):
        response.headers["X-Request-ID"] = getattr(g, "request_id", uuid4().hex)
        return response

    return app
