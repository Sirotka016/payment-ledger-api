from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Admin


async def get_admin_by_email(session: AsyncSession, email: str) -> Admin | None:
    result = await session.execute(select(Admin).where(Admin.email == email))
    return result.scalar_one_or_none()


async def get_admin_by_id(session: AsyncSession, admin_id: int) -> Admin | None:
    result = await session.execute(select(Admin).where(Admin.id == admin_id))
    return result.scalar_one_or_none()
