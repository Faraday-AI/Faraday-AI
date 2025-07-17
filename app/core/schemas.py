"""
Core Schemas Module

This module provides core Pydantic schemas used across the application.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID
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

# Base Schemas
class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

# Service Schemas
class ServiceBase(BaseSchema):
    """Base schema for service."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    version: str = Field(..., min_length=1, max_length=50)
    status: ServiceStatus = Field(default=ServiceStatus.ACTIVE)
    health_check_url: str = Field(..., min_length=1, max_length=500)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ServiceCreate(ServiceBase):
    """Schema for creating a service."""
    pass

class ServiceUpdate(ServiceBase):
    """Schema for updating a service."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[ServiceStatus] = None
    health_check_url: Optional[str] = Field(None, min_length=1, max_length=500)

class ServiceInDB(ServiceBase):
    """Schema for service in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class ServiceHealthBase(BaseSchema):
    """Base schema for service health."""
    
    service_id: UUID
    status: ServiceStatus
    last_check: datetime
    response_time: float = Field(..., ge=0)
    error_count: int = Field(..., ge=0)
    warning_count: int = Field(..., ge=0)
    details: Dict[str, Any] = Field(default_factory=dict)

class ServiceHealthCreate(ServiceHealthBase):
    """Schema for creating service health."""
    pass

class ServiceHealthUpdate(ServiceHealthBase):
    """Schema for updating service health."""
    
    status: Optional[ServiceStatus] = None
    response_time: Optional[float] = Field(None, ge=0)
    error_count: Optional[int] = Field(None, ge=0)
    warning_count: Optional[int] = Field(None, ge=0)

class ServiceHealthInDB(ServiceHealthBase):
    """Schema for service health in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

# Deployment Schemas
class DeploymentBase(BaseSchema):
    """Base schema for deployment."""
    
    service_id: UUID
    version: str = Field(..., min_length=1, max_length=50)
    status: DeploymentStatus = Field(default=DeploymentStatus.PENDING)
    started_at: datetime
    completed_at: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment."""
    pass

class DeploymentUpdate(DeploymentBase):
    """Schema for updating a deployment."""
    
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[DeploymentStatus] = None
    completed_at: Optional[datetime] = None

class DeploymentInDB(DeploymentBase):
    """Schema for deployment in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class DeploymentConfigBase(BaseSchema):
    """Base schema for deployment configuration."""
    
    service_id: UUID
    version: str = Field(..., min_length=1, max_length=50)
    config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)

class DeploymentConfigCreate(DeploymentConfigBase):
    """Schema for creating deployment configuration."""
    pass

class DeploymentConfigUpdate(DeploymentConfigBase):
    """Schema for updating deployment configuration."""
    
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None

class DeploymentConfigInDB(DeploymentConfigBase):
    """Schema for deployment configuration in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

# Feature Flag Schemas
class FeatureFlagBase(BaseSchema):
    """Base schema for feature flag."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: FeatureFlagType
    status: FeatureFlagStatus = Field(default=FeatureFlagStatus.DISABLED)
    default_value: bool = Field(default=False)
    rules: Optional[Dict[str, Any]] = Field(default_factory=dict)

class FeatureFlagCreate(FeatureFlagBase):
    """Schema for creating a feature flag."""
    pass

class FeatureFlagUpdate(FeatureFlagBase):
    """Schema for updating a feature flag."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[FeatureFlagType] = None
    status: Optional[FeatureFlagStatus] = None
    default_value: Optional[bool] = None

class FeatureFlagInDB(FeatureFlagBase):
    """Schema for feature flag in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class FeatureFlagRuleBase(BaseSchema):
    """Base schema for feature flag rule."""
    
    flag_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    value: bool = Field(default=True)
    is_active: bool = Field(default=True)

class FeatureFlagRuleCreate(FeatureFlagRuleBase):
    """Schema for creating a feature flag rule."""
    pass

class FeatureFlagRuleUpdate(FeatureFlagRuleBase):
    """Schema for updating a feature flag rule."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[bool] = None
    is_active: Optional[bool] = None

class FeatureFlagRuleInDB(FeatureFlagRuleBase):
    """Schema for feature flag rule in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

# A/B Testing Schemas
class ABTestBase(BaseSchema):
    """Base schema for A/B test."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ABTestType
    status: ABTestStatus = Field(default=ABTestStatus.DRAFT)
    variants: Dict[str, float] = Field(default_factory=dict)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sample_size: Optional[int] = Field(None, ge=0)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)

class ABTestCreate(ABTestBase):
    """Schema for creating an A/B test."""
    pass

class ABTestUpdate(ABTestBase):
    """Schema for updating an A/B test."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[ABTestType] = None
    status: Optional[ABTestStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ABTestInDB(ABTestBase):
    """Schema for A/B test in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class ABTestResultBase(BaseSchema):
    """Base schema for A/B test result."""
    
    test_id: UUID
    variant: str = Field(..., min_length=1, max_length=100)
    user_id: Optional[UUID] = None
    session_id: Optional[str] = None
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ABTestResultCreate(ABTestResultBase):
    """Schema for creating an A/B test result."""
    pass

class ABTestResultUpdate(ABTestResultBase):
    """Schema for updating an A/B test result."""
    
    value: Optional[float] = None

class ABTestResultInDB(ABTestResultBase):
    """Schema for A/B test result in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

# Analytics Schemas
class AnalyticsEventBase(BaseSchema):
    """Base schema for analytics event."""
    
    type: str = Field(..., min_length=1, max_length=100)
    user_id: Optional[UUID] = None
    session_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime

class AnalyticsEventCreate(AnalyticsEventBase):
    """Schema for creating an analytics event."""
    pass

class AnalyticsEventUpdate(AnalyticsEventBase):
    """Schema for updating an analytics event."""
    
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    timestamp: Optional[datetime] = None

class AnalyticsEventInDB(AnalyticsEventBase):
    """Schema for analytics event in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class AnalyticsMetricBase(BaseSchema):
    """Base schema for analytics metric."""
    
    name: str = Field(..., min_length=1, max_length=100)
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime

class AnalyticsMetricCreate(AnalyticsMetricBase):
    """Schema for creating an analytics metric."""
    pass

class AnalyticsMetricUpdate(AnalyticsMetricBase):
    """Schema for updating an analytics metric."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[float] = None
    timestamp: Optional[datetime] = None

class AnalyticsMetricInDB(AnalyticsMetricBase):
    """Schema for analytics metric in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

# Alert Schemas
class AlertBase(BaseSchema):
    """Base schema for alert."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    severity: AlertSeverity
    status: AlertStatus = Field(default=AlertStatus.ACTIVE)
    source: str = Field(..., min_length=1, max_length=100)
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    pass

class AlertUpdate(AlertBase):
    """Schema for updating an alert."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    timestamp: Optional[datetime] = None

class AlertInDB(AlertBase):
    """Schema for alert in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class AlertRuleBase(BaseSchema):
    """Base schema for alert rule."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    severity: AlertSeverity
    conditions: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)
    cooldown: Optional[int] = Field(None, ge=0)  # in seconds

class AlertRuleCreate(AlertRuleBase):
    """Schema for creating an alert rule."""
    pass

class AlertRuleUpdate(AlertRuleBase):
    """Schema for updating an alert rule."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    severity: Optional[AlertSeverity] = None
    is_active: Optional[bool] = None
    cooldown: Optional[int] = Field(None, ge=0)

class AlertRuleInDB(AlertRuleBase):
    """Schema for alert rule in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

# Circuit Breaker Schemas
class CircuitBreakerBase(BaseSchema):
    """Base schema for circuit breaker."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    state: CircuitBreakerState = Field(default=CircuitBreakerState.CLOSED)
    failure_threshold: int = Field(default=5, ge=1)
    recovery_timeout: int = Field(default=60, ge=1)  # in seconds
    half_open_max_calls: int = Field(default=3, ge=1)
    success_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    last_state_change: Optional[datetime] = None

class CircuitBreakerCreate(CircuitBreakerBase):
    """Schema for creating a circuit breaker."""
    pass

class CircuitBreakerUpdate(CircuitBreakerBase):
    """Schema for updating a circuit breaker."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[CircuitBreakerState] = None
    failure_threshold: Optional[int] = Field(None, ge=1)
    recovery_timeout: Optional[int] = Field(None, ge=1)
    half_open_max_calls: Optional[int] = Field(None, ge=1)

class CircuitBreakerInDB(CircuitBreakerBase):
    """Schema for circuit breaker in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime

class CircuitBreakerStatsBase(BaseSchema):
    """Base schema for circuit breaker statistics."""
    
    breaker_id: UUID
    total_calls: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    average_response_time: float = Field(default=0.0, ge=0)
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

class CircuitBreakerStatsCreate(CircuitBreakerStatsBase):
    """Schema for creating circuit breaker statistics."""
    pass

class CircuitBreakerStatsUpdate(CircuitBreakerStatsBase):
    """Schema for updating circuit breaker statistics."""
    
    total_calls: Optional[int] = Field(None, ge=0)
    failure_count: Optional[int] = Field(None, ge=0)
    success_count: Optional[int] = Field(None, ge=0)
    average_response_time: Optional[float] = Field(None, ge=0)

class CircuitBreakerStatsInDB(CircuitBreakerStatsBase):
    """Schema for circuit breaker statistics in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime 