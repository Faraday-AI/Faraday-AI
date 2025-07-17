"""
Services Module

This module provides comprehensive service functionality for the Faraday AI application.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repositories import (
    BaseRepository, ServiceRepository, ServiceHealthRepository,
    DeploymentRepository, DeploymentConfigRepository,
    FeatureFlagRepository, FeatureFlagRuleRepository,
    ABTestRepository, ABTestResultRepository,
    AnalyticsEventRepository, AnalyticsMetricRepository,
    AlertRepository, AlertRuleRepository,
    CircuitBreakerRepository, CircuitBreakerStatsRepository
)
from app.core.models import (
    ServiceModel, DeploymentModel,
    FeatureFlagModel, ABTestModel,
    AlertModel, CircuitBreakerModel
)
from app.models.core.core_models import (
    Region,
    ServiceStatus,
    DeploymentStatus,
    FeatureFlagType,
    FeatureFlagStatus,
    ABTestType,
    ABTestStatus,
    AlertSeverity,
    AlertStatus,
    CircuitBreakerState
)
from app.core.database import (
    ServiceDB, ServiceHealthDB,
    DeploymentDB, DeploymentConfigDB,
    FeatureFlagDB, FeatureFlagRuleDB,
    ABTestDB, ABTestResultDB,
    AnalyticsEventDB, AnalyticsMetricDB,
    AlertDB, AlertRuleDB,
    CircuitBreakerDB, CircuitBreakerStatsDB
)
from datetime import datetime
import logging
from uuid import UUID
import httpx
import asyncio
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for generic service
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with CRUD operations."""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.repository.get(db, id)

    async def get_async(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Get a single record by ID asynchronously."""
        return await self.repository.get_async(db, id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        return self.repository.get_multi(db, skip=skip, limit=limit)

    async def get_multi_async(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination asynchronously."""
        return await self.repository.get_multi_async(db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        return self.repository.create(db, obj_in=obj_in)

    async def create_async(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record asynchronously."""
        return await self.repository.create_async(db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record."""
        return self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

    async def update_async(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record asynchronously."""
        return await self.repository.update_async(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> ModelType:
        """Remove a record."""
        return self.repository.remove(db, id=id)

    async def remove_async(self, db: AsyncSession, *, id: str) -> ModelType:
        """Remove a record asynchronously."""
        return await self.repository.remove_async(db, id=id)

# Service Management Services
class ServiceService(BaseService[ServiceDB, ServiceModel, ServiceModel]):
    """Service for service management operations."""
    
    def __init__(self):
        super().__init__(ServiceRepository(ServiceDB))

    def get_by_name(self, db: Session, name: str) -> Optional[ServiceDB]:
        """Get service by name."""
        return self.repository.get_by_name(db, name)

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[ServiceDB]:
        """Get service by name asynchronously."""
        return await self.repository.get_by_name_async(db, name)

    def get_by_status(self, db: Session, status: ServiceStatus) -> List[ServiceDB]:
        """Get services by status."""
        return self.repository.get_by_status(db, status)

    async def get_by_status_async(self, db: AsyncSession, status: ServiceStatus) -> List[ServiceDB]:
        """Get services by status asynchronously."""
        return await self.repository.get_by_status_async(db, status)

    async def check_health(self, db: AsyncSession, service_id: str) -> ServiceHealthDB:
        """Check service health."""
        service = await self.get_async(db, service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        try:
            async with httpx.AsyncClient() as client:
                start_time = datetime.utcnow()
                response = await client.get(service.health_check_url, timeout=5.0)
                response_time = (datetime.utcnow() - start_time).total_seconds()

                health = ServiceHealthDB(
                    service_id=service_id,
                    status=ServiceStatus.HEALTHY if response.status_code == 200 else ServiceStatus.UNHEALTHY,
                    last_check=datetime.utcnow(),
                    response_time=response_time,
                    error_count=0 if response.status_code == 200 else 1,
                    warning_count=0,
                    details={"status_code": response.status_code}
                )

                db.add(health)
                await db.commit()
                await db.refresh(health)
                return health

        except Exception as e:
            health = ServiceHealthDB(
                service_id=service_id,
                status=ServiceStatus.UNHEALTHY,
                last_check=datetime.utcnow(),
                response_time=0.0,
                error_count=1,
                warning_count=0,
                details={"error": str(e)}
            )

            db.add(health)
            await db.commit()
            await db.refresh(health)
            return health

class ServiceHealthService(BaseService[ServiceHealthDB, ServiceModel, ServiceModel]):
    """Service for service health operations."""
    
    def __init__(self):
        super().__init__(ServiceHealthRepository(ServiceHealthDB))

    def get_latest_health(self, db: Session, service_id: str) -> Optional[ServiceHealthDB]:
        """Get latest health check for a service."""
        return self.repository.get_latest_health(db, service_id)

    async def get_latest_health_async(self, db: AsyncSession, service_id: str) -> Optional[ServiceHealthDB]:
        """Get latest health check for a service asynchronously."""
        return await self.repository.get_latest_health_async(db, service_id)

# Deployment Services
class DeploymentService(BaseService[DeploymentDB, DeploymentModel, DeploymentModel]):
    """Service for deployment operations."""
    
    def __init__(self):
        super().__init__(DeploymentRepository(DeploymentDB))

    def get_by_service(self, db: Session, service_id: str) -> List[DeploymentDB]:
        """Get deployments for a service."""
        return self.repository.get_by_service(db, service_id)

    async def get_by_service_async(self, db: AsyncSession, service_id: str) -> List[DeploymentDB]:
        """Get deployments for a service asynchronously."""
        return await self.repository.get_by_service_async(db, service_id)

    def get_by_status(self, db: Session, status: DeploymentStatus) -> List[DeploymentDB]:
        """Get deployments by status."""
        return self.repository.get_by_status(db, status)

    async def get_by_status_async(self, db: AsyncSession, status: DeploymentStatus) -> List[DeploymentDB]:
        """Get deployments by status asynchronously."""
        return await self.repository.get_by_status_async(db, status)

    async def deploy(self, db: AsyncSession, service_id: str, version: str) -> DeploymentDB:
        """Deploy a service version."""
        deployment = DeploymentDB(
            service_id=service_id,
            version=version,
            status=DeploymentStatus.PENDING,
            started_at=datetime.utcnow()
        )

        db.add(deployment)
        await db.commit()
        await db.refresh(deployment)

        try:
            # Simulate deployment process
            await asyncio.sleep(5)
            
            deployment.status = DeploymentStatus.COMPLETED
            deployment.completed_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(deployment)
            return deployment

        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.completed_at = datetime.utcnow()
            deployment.metadata = {"error": str(e)}
            
            await db.commit()
            await db.refresh(deployment)
            raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

class DeploymentConfigService(BaseService[DeploymentConfigDB, DeploymentModel, DeploymentModel]):
    """Service for deployment configuration operations."""
    
    def __init__(self):
        super().__init__(DeploymentConfigRepository(DeploymentConfigDB))

    def get_latest_config(self, db: Session, service_id: str) -> Optional[DeploymentConfigDB]:
        """Get latest configuration for a service."""
        return self.repository.get_latest_config(db, service_id)

    async def get_latest_config_async(self, db: AsyncSession, service_id: str) -> Optional[DeploymentConfigDB]:
        """Get latest configuration for a service asynchronously."""
        return await self.repository.get_latest_config_async(db, service_id)

# Feature Flag Services
class FeatureFlagService(BaseService[FeatureFlagDB, FeatureFlagModel, FeatureFlagModel]):
    """Service for feature flag operations."""
    
    def __init__(self):
        super().__init__(FeatureFlagRepository(FeatureFlagDB))

    def get_by_name(self, db: Session, name: str) -> Optional[FeatureFlagDB]:
        """Get feature flag by name."""
        return self.repository.get_by_name(db, name)

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[FeatureFlagDB]:
        """Get feature flag by name asynchronously."""
        return await self.repository.get_by_name_async(db, name)

    def get_by_type(self, db: Session, type: FeatureFlagType) -> List[FeatureFlagDB]:
        """Get feature flags by type."""
        return self.repository.get_by_type(db, type)

    async def get_by_type_async(self, db: AsyncSession, type: FeatureFlagType) -> List[FeatureFlagDB]:
        """Get feature flags by type asynchronously."""
        return await self.repository.get_by_type_async(db, type)

    def is_enabled(self, db: Session, name: str) -> bool:
        """Check if a feature flag is enabled."""
        flag = self.get_by_name(db, name)
        return flag is not None and flag.status == FeatureFlagStatus.ENABLED

    async def is_enabled_async(self, db: AsyncSession, name: str) -> bool:
        """Check if a feature flag is enabled asynchronously."""
        flag = await self.get_by_name_async(db, name)
        return flag is not None and flag.status == FeatureFlagStatus.ENABLED

class FeatureFlagRuleService(BaseService[FeatureFlagRuleDB, FeatureFlagModel, FeatureFlagModel]):
    """Service for feature flag rule operations."""
    
    def __init__(self):
        super().__init__(FeatureFlagRuleRepository(FeatureFlagRuleDB))

    def get_by_flag(self, db: Session, flag_id: str) -> List[FeatureFlagRuleDB]:
        """Get rules for a feature flag."""
        return self.repository.get_by_flag(db, flag_id)

    async def get_by_flag_async(self, db: AsyncSession, flag_id: str) -> List[FeatureFlagRuleDB]:
        """Get rules for a feature flag asynchronously."""
        return await self.repository.get_by_flag_async(db, flag_id)

# A/B Testing Services
class ABTestService(BaseService[ABTestDB, ABTestModel, ABTestModel]):
    """Service for A/B test operations."""
    
    def __init__(self):
        super().__init__(ABTestRepository(ABTestDB))

    def get_by_name(self, db: Session, name: str) -> Optional[ABTestDB]:
        """Get A/B test by name."""
        return self.repository.get_by_name(db, name)

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[ABTestDB]:
        """Get A/B test by name asynchronously."""
        return await self.repository.get_by_name_async(db, name)

    def get_by_status(self, db: Session, status: ABTestStatus) -> List[ABTestDB]:
        """Get A/B tests by status."""
        return self.repository.get_by_status(db, status)

    async def get_by_status_async(self, db: AsyncSession, status: ABTestStatus) -> List[ABTestDB]:
        """Get A/B tests by status asynchronously."""
        return await self.repository.get_by_status_async(db, status)

    def get_variant(self, db: Session, test_id: str, user_id: str) -> str:
        """Get variant for a user in an A/B test."""
        test = self.get(db, test_id)
        if not test or test.status != ABTestStatus.RUNNING:
            return "control"
        
        # Simple hash-based variant assignment
        hash_value = hash(f"{test_id}:{user_id}")
        variants = list(test.variants.keys())
        return variants[abs(hash_value) % len(variants)]

class ABTestResultService(BaseService[ABTestResultDB, ABTestModel, ABTestModel]):
    """Service for A/B test result operations."""
    
    def __init__(self):
        super().__init__(ABTestResultRepository(ABTestResultDB))

    def get_by_test(self, db: Session, test_id: str) -> List[ABTestResultDB]:
        """Get results for an A/B test."""
        return self.repository.get_by_test(db, test_id)

    async def get_by_test_async(self, db: AsyncSession, test_id: str) -> List[ABTestResultDB]:
        """Get results for an A/B test asynchronously."""
        return await self.repository.get_by_test_async(db, test_id)

# Analytics Services
class AnalyticsEventService(BaseService[AnalyticsEventDB, AnalyticsEventDB, AnalyticsEventDB]):
    """Service for analytics event operations."""
    
    def __init__(self):
        super().__init__(AnalyticsEventRepository(AnalyticsEventDB))

    def get_by_type(self, db: Session, type: str) -> List[AnalyticsEventDB]:
        """Get events by type."""
        return self.repository.get_by_type(db, type)

    async def get_by_type_async(self, db: AsyncSession, type: str) -> List[AnalyticsEventDB]:
        """Get events by type asynchronously."""
        return await self.repository.get_by_type_async(db, type)

    def get_by_user(self, db: Session, user_id: str) -> List[AnalyticsEventDB]:
        """Get events by user."""
        return self.repository.get_by_user(db, user_id)

    async def get_by_user_async(self, db: AsyncSession, user_id: str) -> List[AnalyticsEventDB]:
        """Get events by user asynchronously."""
        return await self.repository.get_by_user_async(db, user_id)

    def track_event(
        self, db: Session, type: str, user_id: Optional[str] = None,
        session_id: Optional[str] = None, properties: Dict[str, Any] = None
    ) -> AnalyticsEventDB:
        """Track an analytics event."""
        event = AnalyticsEventDB(
            type=type,
            user_id=user_id,
            session_id=session_id,
            properties=properties or {},
            timestamp=datetime.utcnow()
        )

        db.add(event)
        db.commit()
        db.refresh(event)
        return event

class AnalyticsMetricService(BaseService[AnalyticsMetricDB, AnalyticsMetricDB, AnalyticsMetricDB]):
    """Service for analytics metric operations."""
    
    def __init__(self):
        super().__init__(AnalyticsMetricRepository(AnalyticsMetricDB))

    def get_by_name(self, db: Session, name: str) -> List[AnalyticsMetricDB]:
        """Get metrics by name."""
        return self.repository.get_by_name(db, name)

    async def get_by_name_async(self, db: AsyncSession, name: str) -> List[AnalyticsMetricDB]:
        """Get metrics by name asynchronously."""
        return await self.repository.get_by_name_async(db, name)

    def track_metric(
        self, db: Session, name: str, value: float,
        labels: Dict[str, str] = None
    ) -> AnalyticsMetricDB:
        """Track an analytics metric."""
        metric = AnalyticsMetricDB(
            name=name,
            value=value,
            labels=labels or {},
            timestamp=datetime.utcnow()
        )

        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

# Alert Services
class AlertService(BaseService[AlertDB, AlertModel, AlertModel]):
    """Service for alert operations."""
    
    def __init__(self):
        super().__init__(AlertRepository(AlertDB))

    def get_by_severity(self, db: Session, severity: AlertSeverity) -> List[AlertDB]:
        """Get alerts by severity."""
        return self.repository.get_by_severity(db, severity)

    async def get_by_severity_async(self, db: AsyncSession, severity: AlertSeverity) -> List[AlertDB]:
        """Get alerts by severity asynchronously."""
        return await self.repository.get_by_severity_async(db, severity)

    def get_by_status(self, db: Session, status: AlertStatus) -> List[AlertDB]:
        """Get alerts by status."""
        return self.repository.get_by_status(db, status)

    async def get_by_status_async(self, db: AsyncSession, status: AlertStatus) -> List[AlertDB]:
        """Get alerts by status asynchronously."""
        return await self.repository.get_by_status_async(db, status)

    def create_alert(
        self, db: Session, name: str, severity: AlertSeverity,
        description: str, source: str
    ) -> AlertDB:
        """Create a new alert."""
        alert = AlertDB(
            name=name,
            severity=severity,
            status=AlertStatus.ACTIVE,
            description=description,
            source=source,
            timestamp=datetime.utcnow()
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

class AlertRuleService(BaseService[AlertRuleDB, AlertModel, AlertModel]):
    """Service for alert rule operations."""
    
    def __init__(self):
        super().__init__(AlertRuleRepository(AlertRuleDB))

    def get_by_name(self, db: Session, name: str) -> Optional[AlertRuleDB]:
        """Get alert rule by name."""
        return self.repository.get_by_name(db, name)

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[AlertRuleDB]:
        """Get alert rule by name asynchronously."""
        return await self.repository.get_by_name_async(db, name)

    def get_by_severity(self, db: Session, severity: AlertSeverity) -> List[AlertRuleDB]:
        """Get alert rules by severity."""
        return self.repository.get_by_severity(db, severity)

    async def get_by_severity_async(self, db: AsyncSession, severity: AlertSeverity) -> List[AlertRuleDB]:
        """Get alert rules by severity asynchronously."""
        return await self.repository.get_by_severity_async(db, severity)

# Circuit Breaker Services
class CircuitBreakerService(BaseService[CircuitBreakerDB, CircuitBreakerModel, CircuitBreakerModel]):
    """Service for circuit breaker operations."""
    
    def __init__(self):
        super().__init__(CircuitBreakerRepository(CircuitBreakerDB))

    def get_by_name(self, db: Session, name: str) -> Optional[CircuitBreakerDB]:
        """Get circuit breaker by name."""
        return self.repository.get_by_name(db, name)

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[CircuitBreakerDB]:
        """Get circuit breaker by name asynchronously."""
        return await self.repository.get_by_name_async(db, name)

    def get_by_state(self, db: Session, state: CircuitBreakerState) -> List[CircuitBreakerDB]:
        """Get circuit breakers by state."""
        return self.repository.get_by_state(db, state)

    async def get_by_state_async(self, db: AsyncSession, state: CircuitBreakerState) -> List[CircuitBreakerDB]:
        """Get circuit breakers by state asynchronously."""
        return await self.repository.get_by_state_async(db, state)

    def execute(
        self, db: Session, name: str, func: callable,
        *args, **kwargs
    ) -> Any:
        """Execute a function with circuit breaker protection."""
        breaker = self.get_by_name(db, name)
        if not breaker:
            raise HTTPException(status_code=404, detail="Circuit breaker not found")

        if breaker.state == CircuitBreakerState.OPEN:
            raise HTTPException(status_code=503, detail="Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            breaker.success_count += 1
            db.commit()
            return result

        except Exception as e:
            breaker.failure_count += 1
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitBreakerState.OPEN
                breaker.last_state_change = datetime.utcnow()
            db.commit()
            raise

class CircuitBreakerStatsService(BaseService[CircuitBreakerStatsDB, CircuitBreakerModel, CircuitBreakerModel]):
    """Service for circuit breaker statistics operations."""
    
    def __init__(self):
        super().__init__(CircuitBreakerStatsRepository(CircuitBreakerStatsDB))

    def get_by_breaker(self, db: Session, breaker_id: str) -> Optional[CircuitBreakerStatsDB]:
        """Get statistics for a circuit breaker."""
        return self.repository.get_by_breaker(db, breaker_id)

    async def get_by_breaker_async(self, db: AsyncSession, breaker_id: str) -> Optional[CircuitBreakerStatsDB]:
        """Get statistics for a circuit breaker asynchronously."""
        return await self.repository.get_by_breaker_async(db, breaker_id)

    def update_stats(
        self, db: Session, breaker_id: str,
        success: bool, response_time: float
    ) -> CircuitBreakerStatsDB:
        """Update circuit breaker statistics."""
        stats = self.get_by_breaker(db, breaker_id)
        if not stats:
            stats = CircuitBreakerStatsDB(
                breaker_id=breaker_id,
                total_calls=0,
                failure_count=0,
                success_count=0,
                average_response_time=0.0
            )

        stats.total_calls += 1
        if success:
            stats.success_count += 1
            stats.last_success = datetime.utcnow()
        else:
            stats.failure_count += 1
            stats.last_failure = datetime.utcnow()

        # Update average response time
        stats.average_response_time = (
            (stats.average_response_time * (stats.total_calls - 1) + response_time)
            / stats.total_calls
        )

        db.add(stats)
        db.commit()
        db.refresh(stats)
        return stats 