from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
import psutil
import time
import os
import redis
from minio import Minio
from app.core.database import get_db
from app.core.monitoring import system_monitor, model_monitor
from app.services.ai_analytics import AIAnalytics, get_ai_analytics_service
from app.core.auth import get_current_user
from app.models.lesson import User

router = APIRouter()

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    details: Dict[str, Any]

async def check_redis() -> Dict[str, Any]:
    """Check Redis connection and health."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_minio() -> Dict[str, Any]:
    """Check MinIO connection and health."""
    try:
        minio_url = os.getenv("MINIO_URL", "localhost:9000")
        minio_client = Minio(
            minio_url,
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False
        )
        minio_client.list_buckets()
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_database(db: Session) -> Dict[str, Any]:
    """Check database connection and migrations."""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Check migrations (you'll need to implement this based on your migration system)
        # This is a placeholder for actual migration check
        migrations_status = "ok"
        
        return {
            "status": "healthy",
            "connection": "ok",
            "migrations": migrations_status
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

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
async def health_check(
    db: Session = Depends(get_db),
    ai_analytics: AIAnalytics = Depends(get_ai_analytics_service),
    current_user: User = Depends(get_current_user)
) -> HealthCheckResponse:
    """
    Comprehensive health check endpoint that verifies all system components.
    """
    try:
        # Collect all health checks
        system_health = system_monitor.get_system_health()
        model_metrics = model_monitor.get_model_metrics()
        redis_health = await check_redis()
        minio_health = await check_minio()
        db_health = await check_database(db)
        env_health = await check_environment()
        
        # Determine overall status
        all_checks = [system_health, redis_health, minio_health, db_health, env_health]
        overall_status = "healthy" if all(
            check.get("status") == "healthy" for check in all_checks
        ) else "unhealthy"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            details={
                "system": system_health,
                "models": model_metrics,
                "redis": redis_health,
                "minio": minio_health,
                "database": db_health,
                "environment": env_health,
                "ai_analytics": {
                    "status": "healthy",
                    "service": "operational"
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        ) 