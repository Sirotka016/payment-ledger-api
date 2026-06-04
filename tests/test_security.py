from datetime import timedelta

from app.core.security import create_access_token, decode_access_token
from app.core.security import hash_password, verify_password


def test_password_hash_can_be_verified():
    password_hash = hash_password("secret-password", salt="test-salt")

    assert verify_password("secret-password", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_seeded_user_password_hash_can_be_verified():
    password_hash = (
        "pbkdf2_sha256$600000$default-user-salt$"
        "f3488d07413f42a7e2f4184f8fcccf0bb51505d37cbf327cb06706e4259d2a79"
    )

    assert verify_password("user12345", password_hash) is True
    assert verify_password("admin12345", password_hash) is False


def test_access_token_contains_subject_and_role():
    token = create_access_token(
        subject="10",
        role="admin",
        expires_delta=timedelta(minutes=5),
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "10"
    assert payload["role"] == "admin"
