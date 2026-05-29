import time
from redis.asyncio import Redis
from dataclasses import dataclass

@dataclass
class RateLimitResponse:
    allowed: bool
    tokens: int
    retry_after_seconds: float


class RedisTokenBucketRateLimiter():
    def __init__(self, redis: Redis):
        self.redis = redis

    async def allow(self, key: str, capacity: int, refill_rate:float, cost: int = 1):
        current_time = time.time()
        redis_key = f"rate_limit:{key}"
        bucket = await self.redis.hget(redis_key)

        if bucket:
            tokens = float(bucket.get("tokens", capacity))
            last_refill =  float(bucket.get("last_refill", current_time))
        else:
            tokens = float(capacity)
            last_refill = current_time

        elapsed_time = current_time - last_refill
        tokens_to_add = elapsed_time*refill_rate
        tokens = min(capacity, tokens_to_add+tokens)


        if tokens>cost:
            tokens-=cost
            allowed = True
            retry_after = 0

        
        elif tokens<cost:
            allowed = False
            tokens_missing = cost - tokens
            retry_after = tokens_missing/ refill_rate


        await self.redis.hset(
            redis_key,
            mapping={
                "tokens":tokens,
                "last_refill":current_time 
                }
        )
        
        await self.redis.expire(redis_key,3600)

        return RateLimitResponse(
            allowed = allowed,
            remaining_tokens = tokens,
            retry_after_in_seconds = retry_after
        )
                  