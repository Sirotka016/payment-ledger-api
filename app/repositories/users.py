from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def list_users_with_accounts(session: AsyncSession) -> list[User]:
    result = await session.execute(
        select(User).options(selectinload(User.accounts)).order_by(User.id)
    )
    return list(result.scalars().unique())


async def create_user(
    session: AsyncSession,
    email: str,
    password_hash: str,
    full_name: str,
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
    )
    session.add(user)
    await session.flush()
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
