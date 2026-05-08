from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import RoomMembership
from app.models.room import Room


async def create_room(
    db: AsyncSession,
    name: str,
    created_by: int,
    is_private: bool = False,
) -> Room:
    room = Room(name=name, created_by=created_by, is_private=is_private)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def get_room(db: AsyncSession, room_id: int) -> Room | None:
    return await db.get(Room, room_id)


async def get_rooms(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Room]:
    result = await db.execute(select(Room).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_rooms_by_creator(
    db: AsyncSession,
    created_by: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Room]:
    result = await db.execute(
        select(Room)
        .where(Room.created_by == created_by)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_rooms_by_user(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Room]:
    result = await db.execute(
        select(Room)
        .join(RoomMembership, Room.id == RoomMembership.room_id)
        .where(RoomMembership.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_room(
    db: AsyncSession,
    room_id: int,
    name: str | None = None,
    is_private: bool | None = None,
) -> Room | None:
    room = await get_room(db, room_id)
    if room is None:
        return None

    if name is not None:
        room.name = name
    if is_private is not None:
        room.is_private = is_private

    await db.commit()
    await db.refresh(room)
    return room


async def delete_room(db: AsyncSession, room_id: int) -> bool:
    room = await get_room(db, room_id)
    if room is None:
        return False

    await db.delete(room)
    await db.commit()
    return True
