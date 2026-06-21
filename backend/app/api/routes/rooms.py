from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.membership import MembershipRead
from app.schemas.room import RoomCreate, RoomRead
from app.services import membership as membership_service
from app.services import room as room_service


router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await room_service.create_room(
        db=db,
        name=room_data.name,
        created_by=current_user.id,
        is_private=room_data.is_private,
    )


@router.get("", response_model=list[RoomRead])
async def list_rooms(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await room_service.get_all_rooms(db=db, skip=skip, limit=limit)


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = await room_service.get_room(db=db, room_id=room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    return room


@router.post(
    "/{room_id}/members",
    response_model=MembershipRead,
    status_code=status.HTTP_201_CREATED,
)
async def join_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = await room_service.get_room(db=db, room_id=room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return await membership_service.add_user(
        db=db,
        room_id=room_id,
        user_id=current_user.id,
    )


@router.delete("/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    room_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = await room_service.get_room(db=db, room_id=room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    deleted = await membership_service.delete_user(
        db=db,
        room_id=room_id,
        user_id=user_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room member not found",
        )


@router.get("/{room_id}/members", response_model=list[MembershipRead])
async def list_members(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = await room_service.get_room(db=db, room_id=room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return await membership_service.get_room_members(
        db=db,
        room_id=room_id,
        skip=skip,
        limit=limit,
    )
