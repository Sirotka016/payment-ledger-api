from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class PaymentWebhookRequest:
    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal
    signature: str
    raw_payload: dict[str, object]


def _parse_positive_int(value: object, field_name: str) -> tuple[int | None, str | None]:
    if type(value) is not int or value <= 0:
        return None, f"{field_name} must be a positive integer"

    return value, None


def _parse_positive_decimal(
    value: object,
    field_name: str,
) -> tuple[Decimal | None, str | None]:
    if isinstance(value, bool):
        return None, f"{field_name} must be a positive number"

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, f"{field_name} must be a positive number"

    if amount <= 0:
        return None, f"{field_name} must be a positive number"

    return amount, None


def parse_payment_webhook_request(
    data: object,
) -> tuple[PaymentWebhookRequest | None, str | None]:
    if not isinstance(data, dict):
        return None, "JSON body is required"

    transaction_id = data.get("transaction_id")
    signature = data.get("signature")

    if not isinstance(transaction_id, str) or not transaction_id.strip():
        return None, "transaction_id is required"

    if not isinstance(signature, str) or not signature.strip():
        return None, "signature is required"

    user_id, user_id_error = _parse_positive_int(data.get("user_id"), "user_id")

    if user_id_error is not None or user_id is None:
        return None, user_id_error

    account_id, account_id_error = _parse_positive_int(
        data.get("account_id"),
        "account_id",
    )

    if account_id_error is not None or account_id is None:
        return None, account_id_error

    amount, amount_error = _parse_positive_decimal(data.get("amount"), "amount")

    if amount_error is not None or amount is None:
        return None, amount_error

    return (
        PaymentWebhookRequest(
            transaction_id=transaction_id.strip(),
            user_id=user_id,
            account_id=account_id,
            amount=amount,
            signature=signature.strip(),
            raw_payload=data,
        ),
        None,
    )
