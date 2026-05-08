from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(
    db: AsyncSession,
    display_name: str,
    username: str,
    password: str,
    email: str,
) -> User:
    user = User(
        display_name=display_name,
        username=username,
        password=password,
        email=email,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession,
    user_id: int,
    display_name: str | None = None,
    username: str | None = None,
    password: str | None = None,
    email: str | None = None,
) -> User | None:
    user = await get_user(db, user_id)
    if user is None:
        return None

    if display_name is not None:
        user.display_name = display_name
    if username is not None:
        user.username = username
    if password is not None:
        user.password = password
    if email is not None:
        user.email = email

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user(db, user_id)
    if user is None:
        return False

    await db.delete(user)
    await db.commit()
    return True
