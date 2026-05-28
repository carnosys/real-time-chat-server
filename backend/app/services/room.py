from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import room_repository as repo


# -------------------------
# CREATE ROOM
# -------------------------
async def create_room(
    db: AsyncSession,
    name: str,
    created_by: int,
    is_private: bool = False,
):
    return await repo.create_room(
        db=db,
        name=name,
        created_by=created_by,
        is_private=is_private,
    )


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