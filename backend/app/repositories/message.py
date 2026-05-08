from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


async def create_message(
    db: AsyncSession,
    room_id: int,
    sender_id: int,
    content: str,
    client_message_id: str,
) -> Message:
    message = Message(
        room_id=room_id,
        sender_id=sender_id,
        content=content,
        client_message_id=client_message_id,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_message(db: AsyncSession, message_id: int) -> Message | None:
    return await db.get(Message, message_id)


async def get_messages(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Message]:
    result = await db.execute(select(Message).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_room_messages(
    db: AsyncSession,
    room_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_sender_messages(
    db: AsyncSession,
    sender_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.sender_id == sender_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_message(
    db: AsyncSession,
    message_id: int,
    content: str,
) -> Message | None:
    message = await get_message(db, message_id)
    if message is None:
        return None

    message.content = content
    await db.commit()
    await db.refresh(message)
    return message


async def delete_message(db: AsyncSession, message_id: int) -> bool:
    message = await get_message(db, message_id)
    if message is None:
        return False

    await db.delete(message)
    await db.commit()
    return True
