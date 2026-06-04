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
