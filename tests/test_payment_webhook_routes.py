from decimal import Decimal

from app.config import settings
from app.core.signatures import build_payment_signature
from app.main import create_app
from app.routes import webhooks as webhooks_module
from app.services.payment_webhooks import PaymentWebhookResult


def signed_payload(**overrides):
    payload = {
        "transaction_id": "external-transaction-id",
        "user_id": 1,
        "account_id": 1,
        "amount": 100,
    }
    payload.update(overrides)
    payload["signature"] = build_payment_signature(
        payload,
        settings.webhook_secret_key,
    )
    return payload


def test_payment_webhook_returns_processed_result(monkeypatch):
    async def fake_process_payment_webhook(session, webhook):
        assert webhook.transaction_id == "external-transaction-id"
        assert webhook.amount == Decimal("100")
        return PaymentWebhookResult(
            status="processed",
            transaction_id=webhook.transaction_id,
            account_id=webhook.account_id,
            balance=Decimal("100.00"),
        )

    monkeypatch.setattr(
        webhooks_module,
        "process_payment_webhook",
        fake_process_payment_webhook,
    )

    app = create_app("payment-webhook-test")
    _, response = app.test_client.post("/webhooks/payments", json=signed_payload())

    assert response.status == 200
    assert response.json == {
        "status": "processed",
        "transaction_id": "external-transaction-id",
        "account_id": 1,
        "balance": "100.00",
    }


def test_payment_webhook_rejects_invalid_signature():
    payload = signed_payload()
    payload["signature"] = "wrong-signature"

    app = create_app("payment-webhook-invalid-signature-test")
    _, response = app.test_client.post("/webhooks/payments", json=payload)

    assert response.status == 401
    assert response.json == {"error": "Invalid signature"}


def test_payment_webhook_validates_payload():
    app = create_app("payment-webhook-validation-test")
    _, response = app.test_client.post(
        "/webhooks/payments",
        json={"transaction_id": "external-transaction-id"},
    )

    assert response.status == 400
    assert response.json == {"error": "signature is required"}
