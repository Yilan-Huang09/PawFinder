from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage

from ..api.errors import APIError


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _detected_extension(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    return None


def save_uploaded_image(upload: FileStorage, folder: str = "pets") -> str:
    original_name = upload.filename or ""
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise APIError(
            "UNSUPPORTED_IMAGE_TYPE",
            "仅支持 JPG、PNG 和 WebP 图片",
            422,
        )
    if upload.mimetype and upload.mimetype not in ALLOWED_MIME_TYPES:
        raise APIError(
            "UNSUPPORTED_IMAGE_TYPE",
            "图片 MIME 类型不受支持",
            422,
        )

    max_bytes = int(current_app.config["MAX_PHOTO_BYTES"])
    data = upload.stream.read(max_bytes + 1)
    if not data:
        raise APIError("EMPTY_IMAGE", "上传的图片为空", 422)
    if len(data) > max_bytes:
        raise APIError("IMAGE_TOO_LARGE", "单张图片大小超过限制", 413)

    detected = _detected_extension(data)
    expected = "jpg" if extension == "jpeg" else extension
    if detected is None or detected != expected:
        raise APIError(
            "INVALID_IMAGE_CONTENT",
            "文件内容与图片格式不匹配",
            422,
        )

    relative_path = Path(folder) / f"{uuid4().hex}.{detected}"
    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    target = (upload_root / relative_path).resolve()
    if not target.is_relative_to(upload_root):
        raise APIError("UNSAFE_UPLOAD_PATH", "上传路径无效", 400)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return relative_path.as_posix()


def delete_uploaded_file(relative_path: str) -> None:
    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    target = (upload_root / relative_path).resolve()
    if not target.is_relative_to(upload_root):
        raise APIError("UNSAFE_UPLOAD_PATH", "文件路径无效", 400)
    if target.is_file():
        target.unlink()
