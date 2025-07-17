"""
Regional Failover Module

This module handles regional failover functionality.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timedelta
import json
from redis import asyncio as aioredis
from app.core.config import get_settings
from app.core.health_checks import check_redis, check_minio, check_database
from sqlalchemy import create_engine
from app.core.enums import Region, ServiceStatus

logger = logging.getLogger(__name__)

class FailoverState(Enum):
    """Possible states of regional failover."""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILING_OVER = "failing_over"
    FAILED = "failed"
    RECOVERING = "recovering"

class RegionalFailoverManager:
    """Manages regional failover and high availability."""
    
    def __init__(self, engines: Optional[Dict[str, Any]] = None):
        self.settings = get_settings()
        self.redis = None
        self.current_region = Region.NORTH_AMERICA
        self.failover_state = FailoverState.ACTIVE
        self.engines = {}  # Initialize empty engines dict
        self.health_checks = {
            "database": lambda region: check_database(self.engines.get(region.value), region.value),
            "redis": lambda region: check_redis(self.settings.REDIS_URL, region.value),
            "minio": lambda region: check_minio(region.value)
        }
        self.health_status = {}
        self.failover_threshold = 3  # Number of failed health checks before failover
        self.failover_count = 0
        self.last_health_check = datetime.now()
        self.health_check_interval = 30  # seconds
        self.failover_lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize the failover manager."""
        try:
            # Initialize database engines first
            for region in Region:
                db_url = get_region_db_url(region)
                
                # Create sync engine
                self.engines[region.value] = create_engine(
                    db_url,
                    pool_pre_ping=True,
                    pool_size=3,
                    max_overflow=5,
                    pool_timeout=300,
                    pool_recycle=900,
                    connect_args={
                        "connect_timeout": 180,
                        "keepalives": 1,
                        "keepalives_idle": 120,
                        "keepalives_interval": 60,
                        "keepalives_count": 15,
                        "application_name": "faraday_ai",
                        "sslmode": "require"
                    }
                )
            
            # Initialize Redis connection
            self.redis = await aioredis.from_url(
                self.settings.REDIS_URL,
                encoding='utf-8',
                decode_responses=True
            )
            
            # Start health monitoring
            asyncio.create_task(self._monitor_health())
            logger.info("Regional failover manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize regional failover manager: {e}")
            raise

    async def _monitor_health(self):
        """Continuously monitor service health."""
        while True:
            try:
                await self._check_services_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def _check_services_health(self):
        """Check health of all services."""
        current_time = datetime.now()
        if (current_time - self.last_health_check).seconds < self.health_check_interval:
            return

        self.last_health_check = current_time
        health_results = {}
        
        for service, check_func in self.health_checks.items():
            try:
                result = await check_func(self.current_region)
                health_results[service] = result.get("status") == "healthy"
            except Exception as e:
                logger.error(f"Health check failed for {service}: {e}")
                health_results[service] = False

        self.health_status = health_results
        await self._evaluate_failover_need()

    async def _evaluate_failover_need(self):
        """Evaluate if failover is needed based on health status."""
        if self.failover_state == FailoverState.FAILING_OVER:
            return

        unhealthy_services = sum(1 for status in self.health_status.values() if not status)
        if unhealthy_services >= self.failover_threshold:
            self.failover_count += 1
            if self.failover_count >= 3:  # Require 3 consecutive failures
                await self._initiate_failover()
        else:
            self.failover_count = 0

    async def _initiate_failover(self):
        """Initiate regional failover process."""
        async with self.failover_lock:
            if self.failover_state != FailoverState.ACTIVE:
                return

            try:
                self.failover_state = FailoverState.FAILING_OVER
                logger.info(f"Initiating failover from {self.current_region.value}")
                
                # Select next available region
                next_region = await self._select_next_region()
                if not next_region:
                    logger.error("No available regions for failover")
                    self.failover_state = FailoverState.FAILED
                    return

                # Update region and state
                self.current_region = next_region
                self.failover_state = FailoverState.ACTIVE
                self.failover_count = 0
                
                # Notify services of region change
                await self._notify_region_change()
                
                logger.info(f"Successfully failed over to {self.current_region.value}")
                
            except Exception as e:
                logger.error(f"Failover failed: {e}")
                self.failover_state = FailoverState.FAILED

    async def _select_next_region(self) -> Optional[Region]:
        """Select the next available region for failover."""
        current_index = list(Region).index(self.current_region)
        regions = list(Region)
        
        for i in range(1, len(regions)):
            next_index = (current_index + i) % len(regions)
            next_region = regions[next_index]
            
            # Check if region is available
            if await self._check_region_availability(next_region):
                return next_region
                
        return None

    async def _check_region_availability(self, region: Region) -> bool:
        """Check if a region is available for failover."""
        try:
            # Check region-specific health endpoints
            # This would be implemented with actual region-specific checks
            return True
        except Exception as e:
            logger.error(f"Region availability check failed for {region.value}: {e}")
            return False

    async def _notify_region_change(self):
        """Notify all services of region change."""
        try:
            # Update Redis with new region
            await self.redis.set(
                "current_region",
                self.current_region.value,
                ex=3600  # 1 hour
            )
            
            # Broadcast region change event
            await self.redis.publish(
                "region_change",
                json.dumps({
                    "new_region": self.current_region.value,
                    "timestamp": datetime.now().isoformat()
                })
            )
        except Exception as e:
            logger.error(f"Failed to notify region change: {e}")

    async def get_current_region(self) -> Region:
        """Get the current active region."""
        return self.current_region

    async def get_failover_state(self) -> FailoverState:
        """Get the current failover state."""
        return self.failover_state

    async def get_health_status(self) -> Dict[str, bool]:
        """Get the current health status of all services."""
        return self.health_status

    async def close(self):
        """Clean up resources."""
        if self.redis:
            await self.redis.close()

    async def check_region_health(self, region: Region) -> Dict[str, Any]:
        """Check the health of a specific region.
        
        Args:
            region: The region to check
            
        Returns:
            Dict containing health status information:
            - status: 'healthy' or 'unhealthy'
            - latency: Average latency in seconds
            - errors: Number of errors in last check
            - services: Dict of service-specific health info
        """
        try:
            health_results = {}
            
            # Check each service in the region
            for service, check_func in self.health_checks.items():
                try:
                    result = await check_func(region)
                    health_results[service] = result.get("status") == "healthy"
                except Exception as e:
                    logger.error(f"Health check failed for {service} in {region}: {e}")
                    health_results[service] = False

            # Calculate overall health
            services_healthy = sum(1 for status in health_results.values() if status)
            total_services = len(health_results)
            health_score = services_healthy / total_services if total_services > 0 else 0

            return {
                "status": "healthy" if health_score >= 0.8 else "unhealthy",
                "latency": await self._check_region_latency(region),
                "errors": await self._get_region_errors(region),
                "services": health_results,
                "health_score": health_score
            }
        except Exception as e:
            logger.error(f"Failed to check region health for {region}: {e}")
            return {
                "status": "unhealthy",
                "latency": float('inf'),
                "errors": -1,
                "services": {},
                "health_score": 0
            }

    async def _check_region_latency(self, region: Region) -> float:
        """Check the latency to a region.
        
        Args:
            region: The region to check
            
        Returns:
            Average latency in seconds
        """
        try:
            # Implement actual latency check here
            # For now, return mock values
            return 0.1 if region == Region.NORTH_AMERICA else 0.2
        except Exception as e:
            logger.error(f"Failed to check latency for {region}: {e}")
            return float('inf')

    async def _get_region_errors(self, region: Region) -> int:
        """Get the number of errors in a region.
        
        Args:
            region: The region to check
            
        Returns:
            Number of errors in the last check interval
        """
        try:
            # Implement actual error counting here
            # For now, return mock values
            return 0
        except Exception as e:
            logger.error(f"Failed to get error count for {region}: {e}")
            return -1 