"""Tests des primitives de sécurité : hashing bcrypt et JWT, sans DB ni réseau."""

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_is_not_plaintext():
    hashed = hash_password("mon-mot-de-passe")
    assert hashed != "mon-mot-de-passe"


def test_correct_password_verifies():
    hashed = hash_password("mon-mot-de-passe")
    assert verify_password("mon-mot-de-passe", hashed) is True


def test_wrong_password_fails_verification():
    hashed = hash_password("mon-mot-de-passe")
    assert verify_password("mauvais-mot-de-passe", hashed) is False


def test_token_roundtrip_preserves_claims():
    token = create_access_token({"sub": "user-123", "role": "doctor", "patient_id": None})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "doctor"


def test_tampered_token_is_rejected():
    token = create_access_token({"sub": "user-123", "role": "doctor"})
    tampered = token[:-3] + "xyz"
    with pytest.raises(Exception):
        decode_access_token(tampered)
