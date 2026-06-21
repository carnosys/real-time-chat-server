from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.message import (
    create_message as repo_create_message,
    get_message as repo_get_message,
    update_message as repo_update_message,
    update_message_read_status as repo_update_message_read_status,
    delete_message as repo_delete_message,
    get_room_messages as repo_get_room_messages,
)
from app.models.message import Message


async def create_message_service(
    db: AsyncSession,
    room_id: int,
    sender_id: int,
    content: str,
    client_message_id: str,
) -> Message:
    # Business logic can go here later:
    # - validate room access
    # - check banned users
    # - filter profanity
    # - rate limiting

    return await repo_create_message(
        db=db,
        room_id=room_id,
        sender_id=sender_id,
        content=content,
        client_message_id=client_message_id,
    )


async def get_room_messages_service(
    db: AsyncSession,
    room_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Message]:
    # Future logic examples:
    # - verify user is participant of room
    # - enforce pagination limits
    # - filter deleted messages

    return await repo_get_room_messages(
        db=db,
        room_id=room_id,
        skip=skip,
        limit=limit,
    )


async def update_message_service(
    db: AsyncSession,
    message_id: int,
    new_content: str,
) -> Message | None:
    message = await repo_get_message(db, message_id)

    if message is None:
        return None

    # Business rules (important in real apps):
    # - only sender can edit message
    # - time limit for editing (e.g., 15 mins)
    # - moderation checks

    return await repo_update_message(
        db=db,
        message_id=message_id,
        content=new_content,
    )


async def delete_message_service(
    db: AsyncSession,
    message_id: int,
) -> bool:
    message = await repo_get_message(db, message_id)

    if message is None:
        return False

    # Business rules:
    # - only sender or admin can delete
    # - soft delete instead of hard delete (common in production)

    return await repo_delete_message(
        db=db,
        message_id=message_id,
    )


async def update_message_read_status_service(
    db: AsyncSession,
    message_id: int,
    is_read: bool,
) -> Message | None:
    message = await repo_get_message(db, message_id)

    if message is None:
        return None

    return await repo_update_message_read_status(
        db=db,
        message_id=message_id,
        is_read=is_read,
    )
