from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import membership as membership_repo
from app.repositories import room as repo


# -------------------------
# CREATE ROOM
# -------------------------
async def create_room(
    db: AsyncSession,
    name: str,
    created_by: int,
    is_private: bool = False,
):
    room = await repo.create_room(
        db=db,
        name=name,
        created_by=created_by,
        is_private=is_private,
    )

    existing_membership = await membership_repo.get_membership(
        db=db,
        room_id=room.id,
        user_id=created_by,
    )

    if existing_membership is None:
        await membership_repo.create_membership(
            db=db,
            room_id=room.id,
            user_id=created_by,
        )

    return room


# -------------------------
# DELETE ROOM
# -------------------------
async def delete_room(db: AsyncSession, room_id: int) -> bool:
    # here you can later add permission checks
    return await repo.delete_room(db, room_id)


# -------------------------
# UPDATE ROOM
# -------------------------
async def update_room(
    db: AsyncSession,
    room_id: int,
    name: str | None = None,
    is_private: bool | None = None,
):
    # future: check if user is owner/admin
    return await repo.update_room(
        db=db,
        room_id=room_id,
        name=name,
        is_private=is_private,
    )


# -------------------------
# GET ROOMS FOR USER (JOINED ROOMS)
# -------------------------
async def get_my_rooms(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return await repo.get_rooms_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


# -------------------------
# GET ROOMS CREATED BY USER
# -------------------------
async def get_created_rooms(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return await repo.get_rooms_by_creator(
        db=db,
        created_by=user_id,
        skip=skip,
        limit=limit,
    )


# -------------------------
# OPTIONAL: GET SINGLE ROOM
# -------------------------
async def get_room(db: AsyncSession, room_id: int):
    return await repo.get_room(db, room_id)


# -------------------------
# OPTIONAL: GET ALL ROOMS
# -------------------------
async def get_all_rooms(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await repo.get_rooms(db, skip=skip, limit=limit)
