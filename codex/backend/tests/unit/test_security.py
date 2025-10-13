from ddms.core.security import create_jwt, decode_jwt, hash_password, verify_password


def test_hash_verify_password() -> None:
    pw = "s3cret"
    h = hash_password(pw)
    assert verify_password(pw, h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip() -> None:
    token = create_jwt({"sub": 123, "role": "admin"}, expires_in_seconds=60)
    payload = decode_jwt(token)
    assert payload["sub"] == 123
    assert payload["role"] == "admin"
    assert "iat" in payload and "exp" in payload

