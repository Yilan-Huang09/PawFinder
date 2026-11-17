from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _upload_folder() -> str:
    configured = os.getenv("UPLOAD_FOLDER", "backend/uploads")
    path = Path(configured)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return str(path.resolve())


class BaseConfig:
    APP_VERSION = "1.0.0"
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "connect_args": {"init_command": "SET time_zone = '+08:00'"},
    }
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "development-only-change-this-secret-before-deployment",
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
    MAX_PHOTO_BYTES = int(os.getenv("MAX_PHOTO_BYTES", str(5 * 1024 * 1024)))
    MAX_PET_PHOTOS = int(os.getenv("MAX_PET_PHOTOS", "6"))
    MAX_SIGHTING_PHOTOS = int(os.getenv("MAX_SIGHTING_PHOTOS", "4"))
    UPLOAD_FOLDER = _upload_folder()
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
    USE_REUNION_PROCEDURE = True
    AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "")
    AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "8"))


class DevelopmentConfig(BaseConfig):
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://pawfinder:change_me@127.0.0.1:3306/pawfinder?charset=utf8mb4",
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite+pysqlite:///:memory:",
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    USE_REUNION_PROCEDURE = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
