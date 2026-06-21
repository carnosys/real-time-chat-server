from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import membership as repo


# -------------------------
# ADD USER TO ROOM (JOIN)
# -------------------------
async def add_user(
    db: AsyncSession,
    room_id: int,
    user_id: int,
):
    # Optional future improvement:
    # - check if room exists
    # - check if already a member before inserting

    existing = await repo.get_membership(db, room_id, user_id)
    if existing:
        return existing  # idempotent behavior (safe join)

    return await repo.create_membership(
        db=db,
        room_id=room_id,
        user_id=user_id,
    )


# -------------------------
# REMOVE USER FROM ROOM (LEAVE)
# -------------------------
async def delete_user(
    db: AsyncSession,
    room_id: int,
    user_id: int,
) -> bool:
    # Optional future improvement:
    # - check if user is owner (prevent leaving or transfer ownership)

    return await repo.delete_membership(
        db=db,
        room_id=room_id,
        user_id=user_id,
    )


async def is_user_member(
    db: AsyncSession,user_id: int,
    room_id: int) -> bool:
    membership = await repo.get_membership(db, room_id, user_id)
    return membership is not None

# -------------------------
# LIST ROOM MEMBERS
# -------------------------
async def get_room_members(
    db: AsyncSession,
    room_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return await repo.get_room_memberships(
        db=db,
        room_id=room_id,
        skip=skip,
        limit=limit,
    )

