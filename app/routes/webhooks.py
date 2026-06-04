from sanic import Blueprint, Request
from sanic.response import HTTPResponse, json

from app.config import settings
from app.core.signatures import verify_payment_signature
from app.db import SessionLocal
from app.schemas.webhooks import parse_payment_webhook_request
from app.services.payment_webhooks import (
    PaymentWebhookError,
    process_payment_webhook,
)

webhooks_bp = Blueprint("webhooks", url_prefix="/webhooks")


@webhooks_bp.post("/payments")
async def payment_webhook(request: Request) -> HTTPResponse:
    webhook, parse_error = parse_payment_webhook_request(request.json)

    if parse_error is not None or webhook is None:
        return json({"error": parse_error}, status=400)

    if not verify_payment_signature(
        webhook.raw_payload,
        webhook.signature,
        settings.webhook_secret_key,
    ):
        return json({"error": "Invalid signature"}, status=401)

    async with SessionLocal() as session:
        try:
            result = await process_payment_webhook(session, webhook)
            await session.commit()
        except PaymentWebhookError as error:
            await session.rollback()
            return json({"error": error.message}, status=error.status_code)

    return json(
        {
            "status": result.status,
            "transaction_id": result.transaction_id,
            "account_id": result.account_id,
            "balance": str(result.balance) if result.balance is not None else None,
        }
    )
