from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.accounts import create_account, get_account_by_id
from app.repositories.payments import (
    create_payment,
    get_payment_by_transaction_id,
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
    existing_payment = await get_payment_by_transaction_id(
        session,
        webhook.transaction_id,
    )

    if existing_payment is not None:
        account = await get_account_by_id(session, existing_payment.account_id)
        return PaymentWebhookResult(
            status="already_processed",
            transaction_id=existing_payment.transaction_id,
            account_id=existing_payment.account_id,
            balance=account.balance if account is not None else None,
        )

    user = await get_user_by_id(session, webhook.user_id)

    if user is None:
        raise PaymentWebhookError("User not found", status_code=404)

    account = await get_account_by_id(session, webhook.account_id)

    if account is None:
        account = await create_account(
            session,
            account_id=webhook.account_id,
            user_id=webhook.user_id,
        )
    elif account.user_id != webhook.user_id:
        raise PaymentWebhookError(
            "Account belongs to another user",
            status_code=409,
        )

    account.balance += webhook.amount
    await create_payment(
        session,
        transaction_id=webhook.transaction_id,
        user_id=webhook.user_id,
        account_id=webhook.account_id,
        amount=webhook.amount,
    )
    await session.flush()

    return PaymentWebhookResult(
        status="processed",
        transaction_id=webhook.transaction_id,
        account_id=account.id,
        balance=account.balance,
    )
