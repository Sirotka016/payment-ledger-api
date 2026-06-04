import asyncio
from dataclasses import dataclass
from decimal import Decimal

import pytest

from app.schemas.webhooks import PaymentWebhookRequest
from app.services import payment_webhooks as payment_service
from app.services.payment_webhooks import PaymentWebhookError


@dataclass
class FakeUser:
    id: int


@dataclass
class FakeAccount:
    id: int
    user_id: int
    balance: Decimal


@dataclass
class FakePayment:
    transaction_id: str
    account_id: int


class FakeSession:
    async def flush(self):
        return None


def webhook_request(
    transaction_id: str = "external-transaction-id",
    user_id: int = 1,
    account_id: int = 1,
    amount: Decimal = Decimal("100.00"),
) -> PaymentWebhookRequest:
    return PaymentWebhookRequest(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature="signature",
        raw_payload={},
    )


def test_process_payment_webhook_increases_balance(monkeypatch):
    account = FakeAccount(id=1, user_id=1, balance=Decimal("0.00"))
    created_payments = []

    async def fake_get_payment_by_transaction_id(session, transaction_id):
        return None

    async def fake_get_user_by_id(session, user_id):
        return FakeUser(id=user_id)

    async def fake_get_account_by_id(session, account_id):
        return account

    async def fake_create_payment(session, transaction_id, user_id, account_id, amount):
        created_payments.append(transaction_id)

    monkeypatch.setattr(
        payment_service,
        "get_payment_by_transaction_id",
        fake_get_payment_by_transaction_id,
    )
    monkeypatch.setattr(payment_service, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(payment_service, "get_account_by_id", fake_get_account_by_id)
    monkeypatch.setattr(payment_service, "create_payment", fake_create_payment)

    result = asyncio.run(
        payment_service.process_payment_webhook(
            session=FakeSession(),
            webhook=webhook_request(),
        )
    )

    assert result.status == "processed"
    assert result.balance == Decimal("100.00")
    assert account.balance == Decimal("100.00")
    assert created_payments == ["external-transaction-id"]


def test_process_payment_webhook_is_idempotent(monkeypatch):
    account = FakeAccount(id=1, user_id=1, balance=Decimal("100.00"))

    async def fake_get_payment_by_transaction_id(session, transaction_id):
        return FakePayment(transaction_id=transaction_id, account_id=1)

    async def fake_get_account_by_id(session, account_id):
        return account

    monkeypatch.setattr(
        payment_service,
        "get_payment_by_transaction_id",
        fake_get_payment_by_transaction_id,
    )
    monkeypatch.setattr(payment_service, "get_account_by_id", fake_get_account_by_id)

    result = asyncio.run(
        payment_service.process_payment_webhook(
            session=object(),
            webhook=webhook_request(),
        )
    )

    assert result.status == "already_processed"
    assert result.balance == Decimal("100.00")
    assert account.balance == Decimal("100.00")


def test_process_payment_webhook_rejects_missing_user(monkeypatch):
    async def fake_get_payment_by_transaction_id(session, transaction_id):
        return None

    async def fake_get_user_by_id(session, user_id):
        return None

    monkeypatch.setattr(
        payment_service,
        "get_payment_by_transaction_id",
        fake_get_payment_by_transaction_id,
    )
    monkeypatch.setattr(payment_service, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(PaymentWebhookError) as error:
        asyncio.run(
            payment_service.process_payment_webhook(
                session=object(),
                webhook=webhook_request(),
            )
        )

    assert error.value.status_code == 404
    assert error.value.message == "User not found"
