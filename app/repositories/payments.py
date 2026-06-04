from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment


async def list_payments_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> list[Payment]:
    result = await session.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.id)
    )
    return list(result.scalars())
