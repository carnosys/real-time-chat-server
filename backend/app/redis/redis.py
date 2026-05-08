from core.config import Settings
import redis

redis_client = redis.Redis(
    host = Settings.REDIS_HOST,
    port = Settings.REDIS_PORT,
    db = Settings.REDIS_DB,
    decode_response = True
)