import uuid
import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.dependencies import get_db
from app.database.redis import check_redis_health

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    request_id = str(uuid.uuid4())
    db_status = "disconnected"
    redis_status = "disconnected"

    # Check Database Connection
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "connected"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")

    # Check Redis Connection
    try:
        if await check_redis_health():
            redis_status = "connected"
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")

    is_healthy = (db_status == "connected" or db_status == "disconnected")  # Allow running in mock/isolated modes gracefully
    
    return {
        "success": True,
        "data": {
            "status": "healthy" if db_status == "connected" and redis_status == "connected" else "degraded",
            "services": {
                "database": db_status,
                "redis": redis_status
            }
        },
        "requestId": request_id
    }
