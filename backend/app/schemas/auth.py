from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,50}$")
PHONE_PATTERN = re.compile(r"^1\d{10}$")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class RequestModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


def _validate_username(value: str) -> str:
    normalized = value.lower()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError("用户名只能包含3至50位字母、数字或下划线")
    return normalized


def _validate_password(value: str) -> str:
    if len(value) < 8 or len(value) > 128:
        raise ValueError("密码长度必须为8至128位")
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("密码必须同时包含字母和数字")
    return value


def _validate_phone(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    if not PHONE_PATTERN.fullmatch(value):
        raise ValueError("手机号格式不正确")
    return value


def _validate_email(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    normalized = value.lower()
    if len(normalized) > 120 or not EMAIL_PATTERN.fullmatch(normalized):
        raise ValueError("邮箱格式不正确")
    return normalized


class RegisterRequest(RequestModel):
    username: str
    password: str
    phone: str | None = None
    email: str | None = None

    _username_validator = field_validator("username")(_validate_username)
    _password_validator = field_validator("password")(_validate_password)
    _phone_validator = field_validator("phone")(_validate_phone)
    _email_validator = field_validator("email")(_validate_email)


class LoginRequest(RequestModel):
    username: str
    password: str = Field(min_length=1, max_length=128)

    _username_validator = field_validator("username")(_validate_username)


class ChangePasswordRequest(RequestModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str

    _new_password_validator = field_validator("new_password")(_validate_password)

    @model_validator(mode="after")
    def passwords_must_differ(self):
        if self.current_password == self.new_password:
            raise ValueError("新密码不能与当前密码相同")
        return self


class UpdateProfileRequest(RequestModel):
    phone: str | None = None
    email: str | None = None
    avatar_url: str | None = Field(default=None, max_length=500)

    _phone_validator = field_validator("phone")(_validate_phone)
    _email_validator = field_validator("email")(_validate_email)


class UpdateUserStatusRequest(RequestModel):
    status: Literal["ACTIVE", "DISABLED"]
