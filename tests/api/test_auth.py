from unittest.mock import patch

import pytest

from auth import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("secret123")
        assert not verify_password("wrong", hashed)

    def test_hash_not_plaintext(self):
        hashed = hash_password("secret123")
        assert hashed != "secret123"


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token("admin")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "admin"

    def test_invalid_token_returns_none(self):
        assert decode_access_token("not-a-valid-token") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token("admin")
        tampered = token + "x"
        assert decode_access_token(tampered) is None

    def test_token_includes_password_changed_at(self):
        from datetime import datetime
        pwd_changed = datetime.utcnow()
        token = create_access_token("admin", pwd_changed)
        payload = decode_access_token(token)
        assert payload is not None
        assert "pwd_changed" in payload
        assert payload["pwd_changed"] == pwd_changed.isoformat()
