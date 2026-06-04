from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment


async def list_payments_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> list[Payment]:
    result = await session.execute(
        select(Payment).where(Payment.user_id == user_id).order_by(Payment.id)
    )
    return list(result.scalars())


async def get_payment_by_transaction_id(
    session: AsyncSession,
    transaction_id: str,
) -> Payment | None:
    result = await session.execute(
        select(Payment).where(Payment.transaction_id == transaction_id)
    )
    return result.scalar_one_or_none()


async def insert_payment_if_not_exists(
    session: AsyncSession,
    transaction_id: str,
    user_id: int,
    account_id: int,
    amount: Decimal,
) -> bool:
    statement = (
        insert(Payment)
        .values(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
        )
        .on_conflict_do_nothing(index_elements=[Payment.transaction_id])
        .returning(Payment.id)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none() is not None
