from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import RoomMembership


async def create_membership(
    db: AsyncSession,
    room_id: int,
    user_id: int,
) -> RoomMembership:
    membership = RoomMembership(room_id=room_id, user_id=user_id)
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def get_membership(
    db: AsyncSession,
    room_id: int,
    user_id: int,
) -> RoomMembership | None:
    return await db.get(RoomMembership, (room_id, user_id))


async def get_room_memberships(
    db: AsyncSession,
    room_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[RoomMembership]:
    result = await db.execute(
        select(RoomMembership)
        .where(RoomMembership.room_id == room_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_memberships(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[RoomMembership]:
    result = await db.execute(
        select(RoomMembership)
        .where(RoomMembership.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete_membership(
    db: AsyncSession,
    room_id: int,
    user_id: int,
) -> bool:
    membership = await get_membership(db, room_id, user_id)
    if membership is None:
        return False

    await db.delete(membership)
    await db.commit()
    return True
