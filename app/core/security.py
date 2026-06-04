from datetime import UTC, datetime, timedelta
from typing import Any
import hashlib
import secrets

import jwt

from app.config import settings

HASH_ALGORITHM = "pbkdf2_sha256"
DEFAULT_HASH_ITERATIONS = 600_000


def hash_password(
    password: str,
    salt: str | None = None,
    iterations: int = DEFAULT_HASH_ITERATIONS,
) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()

    return f"{HASH_ALGORITHM}${iterations}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected_digest = password_hash.split("$", 3)
        iterations = int(iterations_raw)
    except ValueError:
        return False

    if algorithm != HASH_ALGORITHM:
        return False

    actual_hash = hash_password(password, salt=salt, iterations=iterations)
    actual_digest = actual_hash.rsplit("$", 1)[1]

    return secrets.compare_digest(actual_digest, expected_digest)


def create_access_token(
    subject: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload = {
        "sub": subject,
        "role": role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
