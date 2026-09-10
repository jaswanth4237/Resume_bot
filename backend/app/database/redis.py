import redis.asyncio as redis
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5.0,
        )
    return redis_client


async def check_redis_health() -> bool:
    try:
        client = await get_redis_client()
        pong = await client.ping()
        return pong is True
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


async def close_redis_connection():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
