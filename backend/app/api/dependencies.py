from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.database.session import get_db_session
from app.database.redis import get_redis_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_redis() -> redis.Redis:
    return await get_redis_client()
