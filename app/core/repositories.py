"""
Repository Module

This module provides comprehensive repository functionality for the Faraday AI application.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from app.db.base_class import Base
from app.core.database import (
    ServiceDB, ServiceHealthDB,
    DeploymentDB, DeploymentConfigDB,
    FeatureFlagDB, FeatureFlagRuleDB,
    ABTestDB, ABTestResultDB,
    AnalyticsEventDB, AnalyticsMetricDB,
    AlertDB, AlertRuleDB,
    CircuitBreakerDB, CircuitBreakerStatsDB
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
from datetime import datetime
import logging
from uuid import UUID

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class with CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """Get a single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    async def get_async(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Get a single record by ID asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()

    async def get_multi_async(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination asynchronously."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def create_async(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record asynchronously."""
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def update_async(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record asynchronously."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: str) -> ModelType:
        """Remove a record."""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    async def remove_async(self, db: AsyncSession, *, id: str) -> ModelType:
        """Remove a record asynchronously."""
        obj = await db.get(self.model, id)
        await db.delete(obj)
        await db.commit()
        return obj

# Service Repositories
class ServiceRepository(BaseRepository[ServiceDB, ServiceModel, ServiceModel]):
    """Repository for service operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[ServiceDB]:
        """Get service by name."""
        return db.query(self.model).filter(self.model.name == name).first()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[ServiceDB]:
        """Get service by name asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()

    def get_by_status(self, db: Session, status: ServiceStatus) -> List[ServiceDB]:
        """Get services by status."""
        return db.query(self.model).filter(self.model.status == status).all()

    async def get_by_status_async(self, db: AsyncSession, status: ServiceStatus) -> List[ServiceDB]:
        """Get services by status asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.status == status))
        return result.scalars().all()

class ServiceHealthRepository(BaseRepository[ServiceHealthDB, ServiceModel, ServiceModel]):
    """Repository for service health operations."""
    
    def get_latest_health(self, db: Session, service_id: str) -> Optional[ServiceHealthDB]:
        """Get latest health check for a service."""
        return db.query(self.model)\
            .filter(self.model.service_id == service_id)\
            .order_by(self.model.created_at.desc())\
            .first()

    async def get_latest_health_async(self, db: AsyncSession, service_id: str) -> Optional[ServiceHealthDB]:
        """Get latest health check for a service asynchronously."""
        result = await db.execute(
            select(self.model)
            .filter(self.model.service_id == service_id)
            .order_by(self.model.created_at.desc())
        )
        return result.scalar_one_or_none()

# Deployment Repositories
class DeploymentRepository(BaseRepository[DeploymentDB, DeploymentModel, DeploymentModel]):
    """Repository for deployment operations."""
    
    def get_by_service(self, db: Session, service_id: str) -> List[DeploymentDB]:
        """Get deployments for a service."""
        return db.query(self.model).filter(self.model.service_id == service_id).all()

    async def get_by_service_async(self, db: AsyncSession, service_id: str) -> List[DeploymentDB]:
        """Get deployments for a service asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.service_id == service_id))
        return result.scalars().all()

    def get_by_status(self, db: Session, status: DeploymentStatus) -> List[DeploymentDB]:
        """Get deployments by status."""
        return db.query(self.model).filter(self.model.status == status).all()

    async def get_by_status_async(self, db: AsyncSession, status: DeploymentStatus) -> List[DeploymentDB]:
        """Get deployments by status asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.status == status))
        return result.scalars().all()

class DeploymentConfigRepository(BaseRepository[DeploymentConfigDB, DeploymentModel, DeploymentModel]):
    """Repository for deployment configuration operations."""
    
    def get_latest_config(self, db: Session, service_id: str) -> Optional[DeploymentConfigDB]:
        """Get latest configuration for a service."""
        return db.query(self.model)\
            .filter(self.model.service_id == service_id)\
            .order_by(self.model.created_at.desc())\
            .first()

    async def get_latest_config_async(self, db: AsyncSession, service_id: str) -> Optional[DeploymentConfigDB]:
        """Get latest configuration for a service asynchronously."""
        result = await db.execute(
            select(self.model)
            .filter(self.model.service_id == service_id)
            .order_by(self.model.created_at.desc())
        )
        return result.scalar_one_or_none()

# Feature Flag Repositories
class FeatureFlagRepository(BaseRepository[FeatureFlagDB, FeatureFlagModel, FeatureFlagModel]):
    """Repository for feature flag operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[FeatureFlagDB]:
        """Get feature flag by name."""
        return db.query(self.model).filter(self.model.name == name).first()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[FeatureFlagDB]:
        """Get feature flag by name asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()

    def get_by_type(self, db: Session, type: FeatureFlagType) -> List[FeatureFlagDB]:
        """Get feature flags by type."""
        return db.query(self.model).filter(self.model.type == type).all()

    async def get_by_type_async(self, db: AsyncSession, type: FeatureFlagType) -> List[FeatureFlagDB]:
        """Get feature flags by type asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.type == type))
        return result.scalars().all()

class FeatureFlagRuleRepository(BaseRepository[FeatureFlagRuleDB, FeatureFlagModel, FeatureFlagModel]):
    """Repository for feature flag rule operations."""
    
    def get_by_flag(self, db: Session, flag_id: str) -> List[FeatureFlagRuleDB]:
        """Get rules for a feature flag."""
        return db.query(self.model).filter(self.model.flag_id == flag_id).all()

    async def get_by_flag_async(self, db: AsyncSession, flag_id: str) -> List[FeatureFlagRuleDB]:
        """Get rules for a feature flag asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.flag_id == flag_id))
        return result.scalars().all()

# A/B Testing Repositories
class ABTestRepository(BaseRepository[ABTestDB, ABTestModel, ABTestModel]):
    """Repository for A/B test operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[ABTestDB]:
        """Get A/B test by name."""
        return db.query(self.model).filter(self.model.name == name).first()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[ABTestDB]:
        """Get A/B test by name asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()

    def get_by_status(self, db: Session, status: ABTestStatus) -> List[ABTestDB]:
        """Get A/B tests by status."""
        return db.query(self.model).filter(self.model.status == status).all()

    async def get_by_status_async(self, db: AsyncSession, status: ABTestStatus) -> List[ABTestDB]:
        """Get A/B tests by status asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.status == status))
        return result.scalars().all()

class ABTestResultRepository(BaseRepository[ABTestResultDB, ABTestModel, ABTestModel]):
    """Repository for A/B test result operations."""
    
    def get_by_test(self, db: Session, test_id: str) -> List[ABTestResultDB]:
        """Get results for an A/B test."""
        return db.query(self.model).filter(self.model.test_id == test_id).all()

    async def get_by_test_async(self, db: AsyncSession, test_id: str) -> List[ABTestResultDB]:
        """Get results for an A/B test asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.test_id == test_id))
        return result.scalars().all()

# Analytics Repositories
class AnalyticsEventRepository(BaseRepository[AnalyticsEventDB, AnalyticsEventDB, AnalyticsEventDB]):
    """Repository for analytics event operations."""
    
    def get_by_type(self, db: Session, type: str) -> List[AnalyticsEventDB]:
        """Get events by type."""
        return db.query(self.model).filter(self.model.type == type).all()

    async def get_by_type_async(self, db: AsyncSession, type: str) -> List[AnalyticsEventDB]:
        """Get events by type asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.type == type))
        return result.scalars().all()

    def get_by_user(self, db: Session, user_id: str) -> List[AnalyticsEventDB]:
        """Get events by user."""
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    async def get_by_user_async(self, db: AsyncSession, user_id: str) -> List[AnalyticsEventDB]:
        """Get events by user asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id))
        return result.scalars().all()

class AnalyticsMetricRepository(BaseRepository[AnalyticsMetricDB, AnalyticsMetricDB, AnalyticsMetricDB]):
    """Repository for analytics metric operations."""
    
    def get_by_name(self, db: Session, name: str) -> List[AnalyticsMetricDB]:
        """Get metrics by name."""
        return db.query(self.model).filter(self.model.name == name).all()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> List[AnalyticsMetricDB]:
        """Get metrics by name asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().all()

# Alert Repositories
class AlertRepository(BaseRepository[AlertDB, AlertModel, AlertModel]):
    """Repository for alert operations."""
    
    def get_by_severity(self, db: Session, severity: AlertSeverity) -> List[AlertDB]:
        """Get alerts by severity."""
        return db.query(self.model).filter(self.model.severity == severity).all()

    async def get_by_severity_async(self, db: AsyncSession, severity: AlertSeverity) -> List[AlertDB]:
        """Get alerts by severity asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.severity == severity))
        return result.scalars().all()

    def get_by_status(self, db: Session, status: AlertStatus) -> List[AlertDB]:
        """Get alerts by status."""
        return db.query(self.model).filter(self.model.status == status).all()

    async def get_by_status_async(self, db: AsyncSession, status: AlertStatus) -> List[AlertDB]:
        """Get alerts by status asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.status == status))
        return result.scalars().all()

class AlertRuleRepository(BaseRepository[AlertRuleDB, AlertModel, AlertModel]):
    """Repository for alert rule operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[AlertRuleDB]:
        """Get alert rule by name."""
        return db.query(self.model).filter(self.model.name == name).first()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[AlertRuleDB]:
        """Get alert rule by name asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()

    def get_by_severity(self, db: Session, severity: AlertSeverity) -> List[AlertRuleDB]:
        """Get alert rules by severity."""
        return db.query(self.model).filter(self.model.severity == severity).all()

    async def get_by_severity_async(self, db: AsyncSession, severity: AlertSeverity) -> List[AlertRuleDB]:
        """Get alert rules by severity asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.severity == severity))
        return result.scalars().all()

# Circuit Breaker Repositories
class CircuitBreakerRepository(BaseRepository[CircuitBreakerDB, CircuitBreakerModel, CircuitBreakerModel]):
    """Repository for circuit breaker operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[CircuitBreakerDB]:
        """Get circuit breaker by name."""
        return db.query(self.model).filter(self.model.name == name).first()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[CircuitBreakerDB]:
        """Get circuit breaker by name asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()

    def get_by_state(self, db: Session, state: CircuitBreakerState) -> List[CircuitBreakerDB]:
        """Get circuit breakers by state."""
        return db.query(self.model).filter(self.model.state == state).all()

    async def get_by_state_async(self, db: AsyncSession, state: CircuitBreakerState) -> List[CircuitBreakerDB]:
        """Get circuit breakers by state asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.state == state))
        return result.scalars().all()

class CircuitBreakerStatsRepository(BaseRepository[CircuitBreakerStatsDB, CircuitBreakerModel, CircuitBreakerModel]):
    """Repository for circuit breaker statistics operations."""
    
    def get_by_breaker(self, db: Session, breaker_id: str) -> Optional[CircuitBreakerStatsDB]:
        """Get statistics for a circuit breaker."""
        return db.query(self.model).filter(self.model.breaker_id == breaker_id).first()

    async def get_by_breaker_async(self, db: AsyncSession, breaker_id: str) -> Optional[CircuitBreakerStatsDB]:
        """Get statistics for a circuit breaker asynchronously."""
        result = await db.execute(select(self.model).filter(self.model.breaker_id == breaker_id))
        return result.scalar_one_or_none() 