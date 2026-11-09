from __future__ import annotations

from flask import Blueprint, current_app, jsonify


api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_v1.get("/health")
def health_check():
    return jsonify(
        {
            "data": {
                "service": "pawfinder-api",
                "status": "ok",
                "version": current_app.config["APP_VERSION"],
            },
            "message": "PawFinder API is healthy",
        }
    )
