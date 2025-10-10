from typing import Any

from argon2 import PasswordHasher


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


def create_jwt(payload: dict[str, Any]) -> str:  # placeholder stub
    """Stub for JWT creation; implement later."""
    raise NotImplementedError

