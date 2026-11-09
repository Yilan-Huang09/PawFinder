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


from .auth import auth_bp  # noqa: E402
from .cases import cases_bp  # noqa: E402
from .matches import matches_bp  # noqa: E402
from .pets import pets_bp  # noqa: E402
from .sightings import sightings_bp  # noqa: E402
from .users import users_bp  # noqa: E402

api_v1.register_blueprint(auth_bp)
api_v1.register_blueprint(cases_bp)
api_v1.register_blueprint(matches_bp)
api_v1.register_blueprint(pets_bp)
api_v1.register_blueprint(sightings_bp)
api_v1.register_blueprint(users_bp)
