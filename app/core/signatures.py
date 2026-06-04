from collections.abc import Mapping
import hashlib
import secrets

PAYMENT_SIGNATURE_FIELDS = ("account_id", "amount", "transaction_id", "user_id")


def build_payment_signature(payload: Mapping[str, object], secret_key: str) -> str:
    signature_base = "".join(str(payload[field]) for field in PAYMENT_SIGNATURE_FIELDS)
    return hashlib.sha256(f"{signature_base}{secret_key}".encode("utf-8")).hexdigest()


def verify_payment_signature(
    payload: Mapping[str, object],
    signature: str,
    secret_key: str,
) -> bool:
    expected_signature = build_payment_signature(payload, secret_key)
    return secrets.compare_digest(expected_signature, signature)
