# app/services/presence.py

from datetime import datetime, timezone

from redis.asyncio import Redis


PRESENCE_TTL_SECONDS = 90


def online_key(user_id: int) -> str:
    return f"presence:online:{user_id}"


def last_seen_key(user_id: int) -> str:
    return f"presence:last_seen:{user_id}"


async def mark_user_online(
    redis: Redis,
    user_id: int,
) -> None:
    now = datetime.now(timezone.utc).isoformat()

    async with redis.pipeline(transaction=True) as pipeline:
        pipeline.set(
            online_key(user_id),
            now,
            ex=PRESENCE_TTL_SECONDS,
        )
        pipeline.set(
            last_seen_key(user_id),
            now,
        )
        await pipeline.execute()


async def refresh_user_presence(
    redis: Redis,
    user_id: int,
) -> None:
    now = datetime.now(timezone.utc).isoformat()

    async with redis.pipeline(transaction=True) as pipeline:
        pipeline.set(
            online_key(user_id),
            now,
            ex=PRESENCE_TTL_SECONDS,
        )
        pipeline.set(
            last_seen_key(user_id),
            now,
        )
        await pipeline.execute()


async def mark_user_offline(
    redis: Redis,
    user_id: int,
) -> None:
    now = datetime.now(timezone.utc).isoformat()

    async with redis.pipeline(transaction=True) as pipeline:
        pipeline.delete(online_key(user_id))
        pipeline.set(
            last_seen_key(user_id),
            now,
        )
        await pipeline.execute()


async def get_user_presence(
    redis: Redis,
    user_id: int,
) -> dict:
    is_online = bool(
        await redis.exists(online_key(user_id))
    )

    last_seen = await redis.get(
        last_seen_key(user_id)
    )

    return {
        "user_id": user_id,
        "is_online": is_online,
        "last_seen": last_seen,
    }