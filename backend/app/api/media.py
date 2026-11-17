from __future__ import annotations

from flask import Blueprint, current_app, send_from_directory


media_bp = Blueprint("media", __name__)


@media_bp.get("/uploads/<path:filename>")
def uploaded_media(filename: str):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename,
        conditional=True,
        max_age=3600,
    )
