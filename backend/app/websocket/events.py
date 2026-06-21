# app/websockets/events.py

from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.membership import is_user_member
from app.services.message import create_message_service
from app.websocket.manager import manager
from app.redis import redis_client
from app.services.presence import refresh_user_presence
from app.redis import redis_client
from app.services.presence import get_user_presence



# Every event handler must accept:
# current_user_id, event data, and database session.
EventHandler = Callable[
    [int, dict[str, Any], AsyncSession],
    Awaitable[None],
]


async def send_error(
    current_user_id: int,
    message: str,
    event_type: str | None = None,
) -> None:
    """
    Send an error only to the user who produced the invalid event.
    """

    payload: dict[str, Any] = {
        "type": "error",
        "message": message,
    }

    if event_type is not None:
        payload["event"] = event_type

    await manager.send_to_user(
        recipient_id=current_user_id,
        payload=payload,
    )


def serialize_message(message: Any) -> dict[str, Any]:
    """
    Convert a SQLAlchemy Message object into JSON-compatible data.
    """

    return {
        "id": message.id,
        "room_id": message.room_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
        "is_read": message.is_read,
        "client_message_id": message.client_message_id,
    }


async def handle_event(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    """
    Find and execute the handler associated with the received event type.

    current_user_id is the user who owns the current WebSocket connection.
    """

    event_type = data.get("type")

    if not isinstance(event_type, str):
        await send_error(
            current_user_id=current_user_id,
            message="A valid event type is required",
        )
        return

    handler = EVENT_HANDLERS.get(event_type)

    if handler is None:
        await send_error(
            current_user_id=current_user_id,
            event_type=event_type,
            message="Unknown event type",
        )
        return

    await handler(current_user_id, data, db)


async def handle_join_room(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    room_id = data.get("room_id")

    if not isinstance(room_id, int):
        await send_error(
            current_user_id=current_user_id,
            event_type="join_room",
            message="A valid room_id is required",
        )
        return

    member = await is_user_member(
        db=db,
        user_id=current_user_id,
        room_id=room_id,
    )

    if not member:
        await send_error(
            current_user_id=current_user_id,
            event_type="join_room",
            message="You are not a member of this room",
        )
        return

    manager.join_room(
        user_id=current_user_id,
        room_id=room_id,
    )

    await manager.send_to_user(
        recipient_id=current_user_id,
        payload={
            "type": "join_room_ack",
            "room_id": room_id,
        },
    )


async def handle_leave_room(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    room_id = data.get("room_id")

    if not isinstance(room_id, int):
        await send_error(
            current_user_id=current_user_id,
            event_type="leave_room",
            message="A valid room_id is required",
        )
        return

    manager.leave_room(
        user_id=current_user_id,
        room_id=room_id,
    )

    await manager.send_to_user(
        recipient_id=current_user_id,
        payload={
            "type": "leave_room_ack",
            "room_id": room_id,
        },
    )


async def handle_room_message(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    """
    Handle both private and group messages.

    A private conversation is simply a room with is_private=True.
    A group conversation is a room with is_private=False.

    WebSocket delivery is the same for both:
        save message -> send message to the room
    """

    room_id = data.get("room_id")
    content = data.get("content")
    client_message_id = data.get("client_message_id")

    if not isinstance(room_id, int):
        await send_error(
            current_user_id=current_user_id,
            event_type="room_message",
            message="A valid room_id is required",
        )
        return

    if not isinstance(content, str) or not content.strip():
        await send_error(
            current_user_id=current_user_id,
            event_type="room_message",
            message="Message content is required",
        )
        return

    if (
        not isinstance(client_message_id, str)
        or not client_message_id.strip()
    ):
        await send_error(
            current_user_id=current_user_id,
            event_type="room_message",
            message="client_message_id is required",
        )
        return

    member = await is_user_member(
        db=db,
        user_id=current_user_id,
        room_id=room_id,
    )

    if not member:
        await send_error(
            current_user_id=current_user_id,
            event_type="room_message",
            message="You are not a member of this room",
        )
        return

    message = await create_message_service(
        db=db,
        room_id=room_id,
        sender_id=current_user_id,
        content=content.strip(),
        client_message_id=client_message_id,
    )

    await manager.send_to_room(
        room_id=room_id,
        payload={
            "type": "room_message",
            "message": serialize_message(message),
        },
    )


async def handle_typing(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    """
    Inform the other currently connected room members that this user
    started or stopped typing.
    """

    room_id = data.get("room_id")
    is_typing = data.get("is_typing")

    if not isinstance(room_id, int):
        await send_error(
            current_user_id=current_user_id,
            event_type="typing",
            message="A valid room_id is required",
        )
        return

    if not isinstance(is_typing, bool):
        await send_error(
            current_user_id=current_user_id,
            event_type="typing",
            message="is_typing must be true or false",
        )
        return

    member = await is_user_member(
        db=db,
        user_id=current_user_id,
        room_id=room_id,
    )

    if not member:
        await send_error(
            current_user_id=current_user_id,
            event_type="typing",
            message="You are not a member of this room",
        )
        return

    await manager.send_to_room(
        room_id=room_id,
        payload={
            "type": "typing",
            "room_id": room_id,
            "user_id": current_user_id,
            "is_typing": is_typing,
        },
        exclude_user_id=current_user_id,
    )


async def handle_broadcast_message(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    """
    Send an application-wide message to every connected user.

    In a real application, this should normally be restricted to admins
    or internal server events.
    """

    content = data.get("content")

    if not isinstance(content, str) or not content.strip():
        await send_error(
            current_user_id=current_user_id,
            event_type="broadcast_message",
            message="Message content is required",
        )
        return

    # TODO:
    # Check whether current_user_id has permission to broadcast globally.

    await manager.broadcast(
        payload={
            "type": "broadcast_message",
            "sender_id": current_user_id,
            "content": content.strip(),
        },
    )


async def handle_status(
    current_user_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> None:
    """
    Return another user's current online status.

    last_seen should later come from your user/presence service or database.
    """

    target_user_id = data.get("user_id")

    if not isinstance(target_user_id, int):
        await send_error(
            current_user_id=current_user_id,
            event_type="status",
            message="A valid user_id is required",
        )
        return

    is_online = manager.is_user_online(target_user_id)

    await manager.send_to_user(
        recipient_id=current_user_id,
        payload={
            "type": "status",
            "user_id": target_user_id,
            "is_online": is_online,
            "last_seen": None,
        },
    )


async def handle_heartbeat(
    current_user_id: int,
    data: dict,
    db: AsyncSession,
) -> None:
    await refresh_user_presence(
        redis=redis_client,
        user_id=current_user_id,
    )

    await manager.send_to_user(
        recipient_id=current_user_id,
        payload={
            "type": "heartbeat_ack",
        },
    )




async def handle_status(
    current_user_id: int,
    data: dict,
    db: AsyncSession,
) -> None:
    target_user_id = data.get("user_id")

    if not isinstance(target_user_id, int):
        await send_error(
            current_user_id=current_user_id,
            event_type="status",
            message="A valid user_id is required",
        )
        return

    presence = await get_user_presence(
        redis=redis_client,
        user_id=target_user_id,
    )

    await manager.send_to_user(
        recipient_id=current_user_id,
        payload={
            "type": "status",
            **presence,
        },
    )


EVENT_HANDLERS: dict[str, EventHandler] = {
    "join_room": handle_join_room,
    "leave_room": handle_leave_room,
    "room_message": handle_room_message,
    "typing": handle_typing,
    "broadcast_message": handle_broadcast_message,
    "status": handle_status,
    "heartbeat": handle_heartbeat,
}
