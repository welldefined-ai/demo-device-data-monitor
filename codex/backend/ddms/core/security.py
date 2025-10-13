from typing import Any, Optional

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from jose import jwt

from ddms.core.config import Settings, get_settings


_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return _hasher.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    """Verify a plaintext password against an Argon2 hash."""
    try:
        _hasher.verify(hash_, password)
        return True
    except Exception:  # pragma: no cover - thin wrapper
        return False


def create_jwt(payload: dict[str, Any], *, expires_in_seconds: int | None = None, settings: Optional[Settings] = None) -> str:
    """Create a signed JWT with issued-at and expiration claims."""
    st = settings or get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=expires_in_seconds or 60 * 60 * 8)  # default 8h
    # Ensure subject is a string to satisfy JWT claim validation
    subj = payload.get("sub")
    normalized = {**payload}
    if subj is not None and not isinstance(subj, str):
        normalized["sub"] = str(subj)
    to_encode = {**normalized, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(to_encode, st.secret_key, algorithm=st.jwt_algorithm)


def decode_jwt(token: str, settings: Optional[Settings] = None) -> dict[str, Any]:
    """Decode and validate a JWT, returning its payload."""
    st = settings or get_settings()
    return jwt.decode(token, st.secret_key, algorithms=[st.jwt_algorithm])


AUTH_COOKIE_NAME = "ddms_auth"


def set_auth_cookie(token: str, *, settings: Optional[Settings] = None) -> dict[str, Any]:
    """Return kwargs for Response.set_cookie for the auth token."""
    st = settings or get_settings()
    # Secure only in non-development envs
    secure = st.env.lower() in {"staging", "production", "prod"}
    return {
        "key": AUTH_COOKIE_NAME,
        "value": token,
        "httponly": True,
        "samesite": "strict",
        "secure": secure,
        "path": "/",
        # Max-Age set to 8h to match token lifetime
        "max_age": 60 * 60 * 8,
    }


def clear_auth_cookie(*, settings: Optional[Settings] = None) -> dict[str, Any]:
    """Return kwargs to clear the auth cookie."""
    st = settings or get_settings()
    secure = st.env.lower() in {"staging", "production", "prod"}
    return {
        "key": AUTH_COOKIE_NAME,
        "value": "",
        "httponly": True,
        "samesite": "strict",
        "secure": secure,
        "path": "/",
        "max_age": 0,
    }
