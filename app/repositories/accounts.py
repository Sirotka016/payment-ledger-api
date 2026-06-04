from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account


async def list_accounts_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> list[Account]:
    result = await session.execute(
        select(Account).where(Account.user_id == user_id).order_by(Account.id)
    )
    return list(result.scalars())


async def get_account_by_id(
    session: AsyncSession,
    account_id: int,
) -> Account | None:
    result = await session.execute(select(Account).where(Account.id == account_id))
    return result.scalar_one_or_none()


async def get_or_create_account(
    session: AsyncSession,
    account_id: int,
    user_id: int,
) -> Account:
    statement = (
        insert(Account)
        .values(id=account_id, user_id=user_id, balance=Decimal("0.00"))
        .on_conflict_do_nothing(index_elements=[Account.id])
    )
    await session.execute(statement)

    account = await get_account_by_id(session, account_id)

    if account is None:
        raise RuntimeError("Account was not created")

    return account


async def increase_account_balance(
    session: AsyncSession,
    account_id: int,
    amount: Decimal,
) -> Decimal:
    statement = (
        update(Account)
        .where(Account.id == account_id)
        .values(balance=Account.balance + amount)
        .returning(Account.balance)
    )
    result = await session.execute(statement)
    return result.scalar_one()
