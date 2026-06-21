# app/websockets/routes.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis import redis_client
from app.api.deps import get_db, get_user_from_token
from app.services.presence import (
    mark_user_offline,
    mark_user_online,
)
from app.websocket.events import handle_event
from app.websocket.manager import manager


router = APIRouter()


async def get_current_user_for_websocket(
    websocket: WebSocket,
    db: AsyncSession,
):
    token = websocket.query_params.get("token")

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing authentication token",
        )

    try:
        return await get_user_from_token(
            db=db,
            token=token,
        )
    except HTTPException as exc:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=str(exc.detail),
        ) from exc


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user_for_websocket(
        websocket=websocket,
        db=db,
    )
    user_id = current_user.id

    await manager.connect(
        user_id=user_id,
        websocket=websocket,
    )

    await mark_user_online(
        redis=redis_client,
        user_id=user_id,
    )

    try:
        while True:
            data = await websocket.receive_json()

            await handle_event(
                current_user_id=user_id,
                data=data,
                db=db,
            )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

        await mark_user_offline(
            redis=redis_client,
            user_id=user_id,
        )
