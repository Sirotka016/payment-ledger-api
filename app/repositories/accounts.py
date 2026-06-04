from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account


async def list_accounts_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> list[Account]:
    result = await session.execute(
        select(Account)
        .where(Account.user_id == user_id)
        .order_by(Account.id)
    )
    return list(result.scalars())


async def get_account_by_id(
    session: AsyncSession,
    account_id: int,
) -> Account | None:
    result = await session.execute(select(Account).where(Account.id == account_id))
    return result.scalar_one_or_none()


async def create_account(
    session: AsyncSession,
    account_id: int,
    user_id: int,
) -> Account:
    account = Account(
        id=account_id,
        user_id=user_id,
        balance=Decimal("0.00"),
    )
    session.add(account)
    await session.flush()
    return account
