from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.accounts import (
    get_account_by_id,
    get_or_create_account,
    increase_account_balance,
)
from app.repositories.payments import (
    get_payment_by_transaction_id,
    insert_payment_if_not_exists,
)
from app.repositories.users import get_user_by_id
from app.schemas.webhooks import PaymentWebhookRequest


class PaymentWebhookError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class PaymentWebhookResult:
    status: str
    transaction_id: str
    account_id: int
    balance: Decimal | None


async def process_payment_webhook(
    session: AsyncSession,
    webhook: PaymentWebhookRequest,
) -> PaymentWebhookResult:
    existing_result = await get_existing_payment_result(
        session,
        webhook.transaction_id,
    )

    if existing_result is not None:
        return existing_result

    user = await get_user_by_id(session, webhook.user_id)

    if user is None:
        raise PaymentWebhookError("User not found", status_code=404)

    account = await get_or_create_account(
        session,
        account_id=webhook.account_id,
        user_id=webhook.user_id,
    )

    if account.user_id != webhook.user_id:
        raise PaymentWebhookError(
            "Account belongs to another user",
            status_code=409,
        )

    payment_created = await insert_payment_if_not_exists(
        session,
        transaction_id=webhook.transaction_id,
        user_id=webhook.user_id,
        account_id=webhook.account_id,
        amount=webhook.amount,
    )

    if not payment_created:
        existing_result = await get_existing_payment_result(
            session,
            webhook.transaction_id,
        )
        if existing_result is not None:
            return existing_result

        raise PaymentWebhookError("Payment transaction conflict", status_code=409)

    balance = await increase_account_balance(
        session,
        account_id=webhook.account_id,
        amount=webhook.amount,
    )

    return PaymentWebhookResult(
        status="processed",
        transaction_id=webhook.transaction_id,
        account_id=account.id,
        balance=balance,
    )


async def get_existing_payment_result(
    session: AsyncSession,
    transaction_id: str,
) -> PaymentWebhookResult | None:
    existing_payment = await get_payment_by_transaction_id(
        session,
        transaction_id,
    )

    if existing_payment is None:
        return None

    account = await get_account_by_id(session, existing_payment.account_id)
    return PaymentWebhookResult(
        status="already_processed",
        transaction_id=existing_payment.transaction_id,
        account_id=existing_payment.account_id,
        balance=account.balance if account is not None else None,
    )
