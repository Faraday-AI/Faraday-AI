from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import psutil
import time
import os
import logging
import asyncio
from app.core.monitoring import system_monitor, model_monitor
from app.core.config import get_settings, settings
from app.core.regional_failover import Region
from app.core.health_checks import check_redis, check_minio, check_database, check_environment

router = APIRouter()
logger = logging.getLogger(__name__)

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    details: Dict[str, Any]
    region: str

class RegionalHealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    regions: Dict[str, Dict[str, Any]]

async def check_region_health(region: Region, engines: Dict[str, Any]) -> Dict[str, Any]:
    """Check health of all services in a specific region."""
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
        
    health_checks["redis"] = await check_redis(os.getenv("REDIS_URL", ""), region.value)
    health_checks["minio"] = await check_minio(region.value)
    health_checks["database"] = await check_database(engines[region.value], region.value)
    health_checks["environment"] = await check_environment(region.value)
    
    # Determine region status
    region_status = "healthy"
    for check in health_checks.values():
        if check.get("status") == "unhealthy":
            region_status = "unhealthy"
            break
            
    return {
        "status": region_status,
        "timestamp": datetime.utcnow(),
        "region": region.value,
        "details": health_checks
    }

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(engines: Dict[str, Any] = Depends(lambda: {})) -> HealthCheckResponse:
    """Health check endpoint for the current region."""
    try:
        # Use North America as default region for health check
        current_region = Region.NORTH_AMERICA
        
        # Check health of current region
        health_checks = await check_region_health(current_region, engines)
        
        return HealthCheckResponse(
            status=health_checks["status"],
            timestamp=health_checks["timestamp"],
            details=health_checks["details"],
            region=current_region.value
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            details={"error": str(e)},
            region="unknown"
        )

@router.get("/health/regional", response_model=RegionalHealthCheckResponse)
async def regional_health_check(engines: Dict[str, Any] = Depends(lambda: {})) -> RegionalHealthCheckResponse:
    """Health check endpoint for all regions."""
    try:
        # Check health of all regions
        health_checks = {}
        for region in Region:
            health_checks[region.value] = await check_region_health(region, engines)
            
        # Determine overall status
        overall_status = "healthy"
        for region_health in health_checks.values():
            if region_health["status"] == "unhealthy":
                overall_status = "unhealthy"
                break
                
        return RegionalHealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            regions=health_checks
        )
    except Exception as e:
        return RegionalHealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            regions={"error": str(e)}
        ) 