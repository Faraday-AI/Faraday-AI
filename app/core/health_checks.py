from typing import Dict, Any, Optional
import os
from urllib.parse import urlparse
from redis import asyncio as aioredis
from minio import Minio
from sqlalchemy import text
import logging
from datetime import datetime
from app.core.database import engine
from app.core.config import settings

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
        # Parse MinIO endpoint from MINIO_URL or MINIO_ENDPOINT
        minio_endpoint = None
        minio_secure = False
        
        # If MINIO_URL is set (e.g., http://minio.example.com:9000 or https://minio.onrender.com), parse it
        if settings.MINIO_URL:
            parsed_url = urlparse(settings.MINIO_URL)
            # For Render web services, the port is handled by the load balancer (443 for HTTPS, 80 for HTTP)
            # Extract just the hostname (netloc includes port if specified, but we'll use it as-is)
            minio_endpoint = parsed_url.netloc or parsed_url.path
            # Remove port if it's the default HTTPS (443), HTTP (80), or MinIO API (9000) port for Render
            # Render web services don't expose internal ports like 9000 directly
            if minio_endpoint and ':' in minio_endpoint:
                host, port = minio_endpoint.rsplit(':', 1)
                # Remove default ports for Render web services (443, 80) and MinIO API port (9000)
                if port in ('443', '80', '9000'):
                    minio_endpoint = host
            minio_secure = parsed_url.scheme == "https"
            logger.info(f"MinIO health check using MINIO_URL: {settings.MINIO_URL} (endpoint: {minio_endpoint}, secure: {minio_secure})")
        else:
            # Use MINIO_ENDPOINT directly (e.g., minio.example.com:9000)
            minio_endpoint = settings.MINIO_ENDPOINT
            minio_secure = settings.MINIO_SECURE
            logger.info(f"MinIO health check using MINIO_ENDPOINT: {minio_endpoint} (secure: {minio_secure})")
        
        if not minio_endpoint:
            return {
                "status": "not_configured",
                "message": "MinIO endpoint not configured",
                "region": region_value if region_value else "default"
            }
        
        # Create MinIO client using settings
        minio_client = Minio(
            minio_endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=minio_secure
        )
        
        # Test connection by listing buckets with timeout
        # Use asyncio to add timeout to the synchronous list_buckets call
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        try:
            # Get the running event loop (more reliable than get_event_loop)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            
            # Run the synchronous call in a thread with a timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                try:
                    buckets = await asyncio.wait_for(
                        loop.run_in_executor(executor, minio_client.list_buckets),
                        timeout=2.0  # 2 second timeout to fail faster and not block startup
                    )
                    logger.info(f"MinIO health check succeeded for region {region_value if region_value else 'default'}")
                except asyncio.TimeoutError:
                    logger.warning(f"MinIO connection timed out after 2 seconds to {minio_endpoint}")
                    raise Exception(f"MinIO connection timed out after 2 seconds to {minio_endpoint}")
        except Exception as timeout_error:
            # Re-raise timeout errors to be caught by outer exception handler
            if "timed out" in str(timeout_error):
                raise
            # For other errors, let them bubble up
            raise
        return {"status": "healthy", "connection": "ok", "region": region_value if region_value else "default"}
    except Exception as e:
        # Log error but don't fail the application - MinIO may not be available in all environments
        logger.warning(f"MinIO health check failed for region {region_value if region_value else 'default'}: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "region": region_value if region_value else "default",
            "details": {
                "endpoint": minio_endpoint if 'minio_endpoint' in locals() else "not_configured",
                "access_key": "configured" if settings.MINIO_ACCESS_KEY else "not_configured",
                "secure": minio_secure if 'minio_secure' in locals() else False
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