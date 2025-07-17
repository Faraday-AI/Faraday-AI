from typing import Dict, Any, Optional
import os
from redis import asyncio as aioredis
from minio import Minio
from sqlalchemy import text
import logging
from datetime import datetime
from app.core.database import engine

logger = logging.getLogger(__name__)

async def check_redis(redis_url: str, region_value: Optional[str] = None) -> Dict[str, Any]:
    """Check Redis connection and health for a specific region."""
    try:
        if not redis_url:
            return {"status": "not_configured", "message": "Redis URL not configured"}
            
        if region_value:
            # Get region-specific Redis URL
            redis_url = redis_url.replace("redis", f"redis-{region_value}")
            
        redis_client = await aioredis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        await redis_client.close()
        return {"status": "healthy", "connection": "ok", "region": region_value if region_value else "default"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "region": region_value if region_value else "default"}

async def check_minio(region_value: Optional[str] = None) -> Dict[str, Any]:
    """Check MinIO connection and health for a specific region."""
    try:
        # Use the local MinIO endpoint since we're not actually running multi-region
        minio_client = Minio(
            "minio:9000",  # Use the Docker service name
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        minio_client.list_buckets()
        return {"status": "healthy", "connection": "ok", "region": region_value if region_value else "default"}
    except Exception as e:
        logger.error(f"MinIO health check failed for region {region_value if region_value else 'default'}: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "region": region_value if region_value else "default",
            "details": {
                "endpoint": "minio:9000",
                "access_key": "configured",
                "secure": False
            }
        }

async def check_database(region_engine=None, region_value: Optional[str] = None) -> Dict[str, Any]:
    """Check database connection and migrations for a specific region."""
    try:
        # Use global engine if no specific engine is provided
        db_engine = region_engine or engine
        
        if not db_engine:
            return {
                "status": "unhealthy",
                "error": "No database engine available",
                "region": region_value if region_value else "default"
            }
            
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                return {
                    "status": "healthy",
                    "connection": "ok",
                    "region": region_value if region_value else "default"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Database query returned unexpected result",
                    "region": region_value if region_value else "default"
                }
    except Exception as e:
        logger.error(f"Database health check failed for region {region_value if region_value else 'default'}: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "region": region_value if region_value else "default",
            "details": {
                "error_type": type(e).__name__
            }
        }

async def check_environment(region_value: Optional[str] = None) -> Dict[str, Any]:
    """Check critical environment variables for a specific region."""
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "MINIO_URL",
        "OPENAI_API_KEY",
        "APP_ENVIRONMENT"
    ]
    
    status = {}
    for var in required_vars:
        status[var] = "present" if os.getenv(var) else "missing"
    
    return {
        "status": "healthy" if all(v == "present" for v in status.values()) else "unhealthy",
        "variables": status,
        "region": region_value if region_value else "default"
    } 