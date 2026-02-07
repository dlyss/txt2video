from __future__ import annotations

import base64
import hashlib
from cryptography.fernet import Fernet

from ..settings import settings


def _derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _fernet() -> Fernet:
    secret = settings.settings_secret_key or "dev-secret"
    key = _derive_key(secret)
    return Fernet(key)


def encrypt(value: str) -> str:
    if not value:
        return ""
    token = _fernet().encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(token: str) -> str:
    if not token:
        return ""
    value = _fernet().decrypt(token.encode("utf-8"))
    return value.decode("utf-8")


def mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return "****" + value[-4:]

