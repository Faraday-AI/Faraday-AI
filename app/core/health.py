from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
import psutil
import time
import os
import redis
from minio import Minio
from app.core.database import get_db, engine
from app.core.monitoring import system_monitor, model_monitor
from app.services.ai_analytics import AIAnalytics, get_ai_analytics_service
from app.core.config import get_settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    details: Dict[str, Any]

async def check_redis() -> Dict[str, Any]:
    """Check Redis connection and health."""
    try:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return {"status": "not_configured", "message": "Redis URL not configured"}
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_minio() -> Dict[str, Any]:
    """Check MinIO connection and health."""
    try:
        # Create MinIO client with hardcoded values for testing
        minio_client = Minio(
            "minio:9000",  # Use internal Docker network name and port
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False,  # Disable SSL for local development
            region="us-east-1"
        )
        
        # Try to list buckets
        minio_client.list_buckets()
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        logger.error(f"MinIO health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": {
                "endpoint": "minio:9000",
                "access_key": "configured",
                "secure": False
            }
        }

async def check_database() -> Dict[str, Any]:
    """Check database connection and migrations."""
    try:
        # Use the main engine for the health check
        with engine.connect() as conn:
            # Use text() for the SQL query
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                return {
                    "status": "healthy",
                    "connection": "ok"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Database query returned unexpected result"
                }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": {
                "error_type": type(e).__name__
            }
        }

async def check_environment() -> Dict[str, Any]:
    """Check critical environment variables."""
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
        "variables": status
    }

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint that verifies system components.
    """
    try:
        # Collect health checks
        health_checks = {}
        
        try:
            health_checks["system"] = system_monitor.get_system_health()
        except Exception as e:
            health_checks["system"] = {"status": "unhealthy", "error": str(e)}
            
        try:
            model_metrics = model_monitor.get_model_metrics()
            if not model_metrics:
                health_checks["models"] = {"status": "healthy", "message": "No models loaded yet"}
            else:
                health_checks["models"] = model_metrics
        except Exception as e:
            health_checks["models"] = {"status": "unhealthy", "error": str(e)}
            
        health_checks["redis"] = await check_redis()
        health_checks["minio"] = await check_minio()
        health_checks["database"] = await check_database()
        health_checks["environment"] = await check_environment()
        
        # Determine overall status - consider the app healthy if database is up
        overall_status = "healthy" if health_checks["database"].get("status") == "healthy" else "unhealthy"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            details=health_checks
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            details={"error": str(e)}
        ) 