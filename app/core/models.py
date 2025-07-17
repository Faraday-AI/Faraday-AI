"""
Core Models Module

This module provides core models used across the application.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Set
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, root_validator, constr, model_serializer
from enum import Enum
import re

from app.models.core.core_models import (
    Region,
    ServiceStatus,
    DeploymentStatus,
    FeatureFlagType,
    FeatureFlagStatus,
    ABTestType,
    ABTestStatus,
    AnalyticsEventType,
    MetricsType,
    AlertSeverity,
    AlertStatus,
    CircuitBreakerState
)

# Base Models
class BaseModel(BaseModel):
    """Base model with common fields."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = Field(default=1)
    is_active: bool = Field(default=True)
    tags: Set[str] = Field(default_factory=set)

    model_config = {
        "arbitrary_types_allowed": True
    }

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Custom serializer for the model."""
        data = self.model_dump()
        # Convert datetime to ISO format
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data.get('updated_at'), datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        # Convert UUID to string
        if isinstance(data.get('id'), UUID):
            data['id'] = str(data['id'])
        return data

    @field_validator('updated_at')
    @classmethod
    def validate_updated_at(cls, v, values):
        """Validate updated_at is after created_at."""
        if 'created_at' in values and v < values['created_at']:
            raise ValueError('updated_at must be after created_at')
        return v

class TimestampModel(BaseModel):
    """Model with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    @field_validator('deleted_at')
    @classmethod
    def validate_deleted_at(cls, v, values):
        """Validate deleted_at is after created_at."""
        if v and 'created_at' in values and v < values['created_at']:
            raise ValueError('deleted_at must be after created_at')
        return v

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, v, values):
        """Validate expires_at is after created_at."""
        if v and 'created_at' in values and v < values['created_at']:
            raise ValueError('expires_at must be after created_at')
        return v

class AuditModel(BaseModel):
    """Model with audit fields."""
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_from: Optional[str] = None
    updated_from: Optional[str] = None
    deleted_from: Optional[str] = None
    created_reason: Optional[str] = None
    updated_reason: Optional[str] = None
    deleted_reason: Optional[str] = None

class VersionModel(BaseModel):
    """Model with version fields."""
    version: int = Field(default=1)
    previous_version: Optional[int] = None
    version_notes: Optional[str] = None
    version_changes: Dict[str, Any] = Field(default_factory=dict)
    version_author: Optional[UUID] = None
    version_timestamp: datetime = Field(default_factory=datetime.utcnow)
    version_tags: List[str] = Field(default_factory=list)

# Service Models
class ServiceModel(BaseModel):
    """Service model."""
    name: constr(min_length=1, max_length=100)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    version: str
    host: str
    port: int = Field(gt=0, lt=65536)
    health_check_url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    environment: str
    region: str
    replicas: int = Field(default=1, ge=1)
    resources: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    secrets: Dict[str, Any] = Field(default_factory=dict)
    endpoints: List[str] = Field(default_factory=list)
    health_check_interval: int = Field(default=30, ge=5)
    health_check_timeout: int = Field(default=5, ge=1)
    health_check_retries: int = Field(default=3, ge=1)
    startup_timeout: int = Field(default=300, ge=30)
    shutdown_timeout: int = Field(default=30, ge=5)

    @field_validator('health_check_url')
    @classmethod
    def validate_health_check_url(cls, v):
        """Validate health check URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('health_check_url must start with http:// or https://')
        return v

class ServiceHealthModel(BaseModel):
    """Service health model."""
    service_id: UUID
    status: ServiceStatus
    last_check: datetime
    response_time: float = Field(ge=0)
    error_count: int = Field(default=0, ge=0)
    warning_count: int = Field(default=0, ge=0)
    details: Dict[str, Any] = Field(default_factory=dict)
    cpu_usage: float = Field(default=0, ge=0, le=100)
    memory_usage: float = Field(default=0, ge=0, le=100)
    disk_usage: float = Field(default=0, ge=0, le=100)
    network_io: Dict[str, float] = Field(default_factory=dict)
    uptime: float = Field(default=0, ge=0)
    last_error: Optional[str] = None
    last_warning: Optional[str] = None
    health_score: float = Field(default=100, ge=0, le=100)

# Deployment Models
class DeploymentModel(BaseModel):
    """Deployment model."""
    service_id: UUID
    version: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    rollback_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    environment: str
    region: str
    strategy: str = "rolling"
    replicas: int = Field(default=1, ge=1)
    timeout: int = Field(default=300, ge=30)
    health_check: Dict[str, Any] = Field(default_factory=dict)
    rollback_enabled: bool = True
    rollback_threshold: int = Field(default=3, ge=1)
    verification_steps: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    config_changes: Dict[str, Any] = Field(default_factory=dict)
    secrets_changes: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('completed_at')
    @classmethod
    def validate_completed_at(cls, v, values):
        """Validate completed_at is after started_at."""
        if v and 'started_at' in values and v < values['started_at']:
            raise ValueError('completed_at must be after started_at')
        return v

    @field_validator('rollback_at')
    @classmethod
    def validate_rollback_at(cls, v, values):
        """Validate rollback_at is after started_at."""
        if v and 'started_at' in values and v < values['started_at']:
            raise ValueError('rollback_at must be after started_at')
        return v

class DeploymentConfigModel(BaseModel):
    """Deployment configuration model."""
    service_id: UUID
    version: str
    config: Dict[str, Any]
    environment: str
    region: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    secrets: Dict[str, Any] = Field(default_factory=dict)
    resources: Dict[str, Any] = Field(default_factory=dict)
    scaling: Dict[str, Any] = Field(default_factory=dict)
    networking: Dict[str, Any] = Field(default_factory=dict)
    monitoring: Dict[str, Any] = Field(default_factory=dict)
    security: Dict[str, Any] = Field(default_factory=dict)

# Feature Flag Models
class FeatureFlagModel(BaseModel):
    """Feature flag model."""
    name: constr(min_length=1, max_length=100)
    type: FeatureFlagType
    status: FeatureFlagStatus = FeatureFlagStatus.DISABLED
    value: Any
    description: Optional[str] = None
    created_by: UUID
    updated_by: Optional[UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    default_value: Any
    rollout_percentage: float = Field(default=0, ge=0, le=100)
    target_users: List[str] = Field(default_factory=list)
    target_environments: List[str] = Field(default_factory=list)
    schedule: Optional[Dict[str, datetime]] = None
    dependencies: List[str] = Field(default_factory=list)
    analytics_enabled: bool = True
    evaluation_count: int = Field(default=0, ge=0)
    last_evaluated: Optional[datetime] = None

    @field_validator('rollout_percentage')
    @classmethod
    def validate_rollout_percentage(cls, v, values):
        """Validate rollout percentage based on status."""
        if values.get('status') == FeatureFlagStatus.ROLLING_OUT and v == 0:
            raise ValueError('rollout_percentage must be greater than 0 for rolling out status')
        return v

class FeatureFlagRuleModel(BaseModel):
    """Feature flag rule model."""
    flag_id: UUID
    condition: str
    value: Any
    priority: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    target_users: List[str] = Field(default_factory=list)
    target_environments: List[str] = Field(default_factory=list)
    schedule: Optional[Dict[str, datetime]] = None
    weight: float = Field(default=1.0, ge=0, le=1.0)
    evaluation_count: int = Field(default=0, ge=0)
    last_evaluated: Optional[datetime] = None

# A/B Testing Models
class ABTestModel(BaseModel):
    """A/B test model."""
    name: constr(min_length=1, max_length=100)
    type: ABTestType
    status: ABTestStatus = ABTestStatus.DRAFT
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    variants: Dict[str, Any]
    metrics: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    sample_size: int = Field(default=1000, ge=100)
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99)
    minimum_duration: int = Field(default=7, ge=1)  # days
    maximum_duration: int = Field(default=30, ge=1)  # days
    success_criteria: Dict[str, Any] = Field(default_factory=dict)
    analysis_frequency: str = "daily"
    notifications: List[Dict[str, Any]] = Field(default_factory=list)
    owner: UUID
    stakeholders: List[UUID] = Field(default_factory=list)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, values):
        """Validate end_date is after start_date."""
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @field_validator('maximum_duration')
    @classmethod
    def validate_maximum_duration(cls, v, values):
        """Validate maximum_duration is greater than minimum_duration."""
        if 'minimum_duration' in values and v < values['minimum_duration']:
            raise ValueError('maximum_duration must be greater than minimum_duration')
        return v

class ABTestResultModel(BaseModel):
    """A/B test result model."""
    test_id: UUID
    variant: str
    sample_size: int = Field(ge=0)
    conversion_rate: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    p_value: float = Field(ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    segment_results: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    statistical_significance: bool = False
    practical_significance: bool = False
    recommendation: Optional[str] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_method: str
    confidence_intervals: Dict[str, Dict[str, float]] = Field(default_factory=dict)

# Analytics Models
class AnalyticsEventModel(BaseModel):
    """Analytics event model."""
    type: AnalyticsEventType
    user_id: Optional[UUID] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str
    environment: str
    version: str
    correlation_id: Optional[str] = None
    parent_event_id: Optional[UUID] = None
    duration: Optional[float] = None
    status: str = "success"
    error: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        """Validate duration is positive."""
        if v is not None and v < 0:
            raise ValueError('duration must be positive')
        return v

class AnalyticsMetricModel(BaseModel):
    """Analytics metric model."""
    name: constr(min_length=1, max_length=100)
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    type: str = "gauge"
    unit: Optional[str] = None
    description: Optional[str] = None
    aggregation: str = "last"
    retention: int = Field(default=30, ge=1)  # days
    alert_thresholds: Optional[Dict[str, float]] = None
    trend: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    sum_value: Optional[float] = None
    count: int = Field(default=1, ge=1)

    @field_validator('value')
    @classmethod
    def validate_value(cls, v, values):
        """Validate value is within min/max bounds if specified."""
        if 'min_value' in values and values['min_value'] is not None and v < values['min_value']:
            raise ValueError(f'value must be greater than or equal to {values["min_value"]}')
        if 'max_value' in values and values['max_value'] is not None and v > values['max_value']:
            raise ValueError(f'value must be less than or equal to {values["max_value"]}')
        return v

# Metrics Models
class MetricsModel(BaseModel):
    """Metrics model."""
    name: str
    type: MetricsType
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MetricsQueryModel(BaseModel):
    """Metrics query model."""
    name: str
    start_time: datetime
    end_time: datetime
    interval: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    aggregations: List[str] = Field(default_factory=list)

# Alert Models
class AlertModel(BaseModel):
    """Alert model."""
    name: constr(min_length=1, max_length=100)
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    description: str
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    category: str
    tags: List[str] = Field(default_factory=list)
    assigned_to: Optional[UUID] = None
    priority: int = Field(default=0, ge=0)
    impact: str
    urgency: str
    resolution: Optional[str] = None
    resolution_notes: Optional[str] = None
    related_alerts: List[UUID] = Field(default_factory=list)
    affected_services: List[str] = Field(default_factory=list)
    affected_users: Optional[int] = None
    detection_time: datetime = Field(default_factory=datetime.utcnow)
    first_occurrence: datetime = Field(default_factory=datetime.utcnow)
    last_occurrence: datetime = Field(default_factory=datetime.utcnow)
    occurrence_count: int = Field(default=1, ge=1)
    suppression_until: Optional[datetime] = None
    escalation_level: int = Field(default=0, ge=0)
    notification_channels: List[str] = Field(default_factory=list)

    @field_validator('resolved_at')
    @classmethod
    def validate_resolved_at(cls, v, values):
        """Validate resolved_at is after timestamp."""
        if v and 'timestamp' in values and v < values['timestamp']:
            raise ValueError('resolved_at must be after timestamp')
        return v

    @field_validator('acknowledged_at')
    @classmethod
    def validate_acknowledged_at(cls, v, values):
        """Validate acknowledged_at is after timestamp."""
        if v and 'timestamp' in values and v < values['timestamp']:
            raise ValueError('acknowledged_at must be after timestamp')
        return v

class AlertRuleModel(BaseModel):
    """Alert rule model."""
    name: constr(min_length=1, max_length=100)
    condition: str
    severity: AlertSeverity
    description: str
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    actions: List[str] = Field(default_factory=list)
    category: str
    tags: List[str] = Field(default_factory=list)
    threshold: Optional[float] = None
    threshold_duration: Optional[int] = None  # seconds
    evaluation_window: int = Field(default=300, ge=60)  # seconds
    cooldown_period: int = Field(default=300, ge=0)  # seconds
    group_by: List[str] = Field(default_factory=list)
    aggregation: str = "count"
    notification_channels: List[str] = Field(default_factory=list)
    escalation_policy: Optional[Dict[str, Any]] = None
    suppression_rules: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    created_by: UUID
    updated_by: Optional[UUID] = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = Field(default=0, ge=0)

# Circuit Breaker Models
class CircuitBreakerModel(BaseModel):
    """Circuit breaker model."""
    name: constr(min_length=1, max_length=100)
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_threshold: int = Field(ge=1)
    recovery_timeout: int = Field(ge=1)  # seconds
    half_open_max_calls: int = Field(ge=1)
    last_state_change: datetime = Field(default_factory=datetime.utcnow)
    failure_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    service: str
    endpoint: str
    method: str
    timeout: int = Field(default=30, ge=1)  # seconds
    retry_count: int = Field(default=3, ge=0)
    retry_delay: int = Field(default=1, ge=0)  # seconds
    error_threshold: float = Field(default=0.5, ge=0, le=1)
    success_threshold: float = Field(default=0.8, ge=0, le=1)
    window_size: int = Field(default=100, ge=10)
    rolling_window: bool = True
    ignore_errors: List[str] = Field(default_factory=list)
    fallback_response: Optional[Dict[str, Any]] = None
    monitoring_enabled: bool = True
    alert_on_state_change: bool = True
    tags: List[str] = Field(default_factory=list)

    @field_validator('error_threshold')
    @classmethod
    def validate_error_threshold(cls, v, values):
        """Validate error_threshold is less than success_threshold."""
        if 'success_threshold' in values and v >= values['success_threshold']:
            raise ValueError('error_threshold must be less than success_threshold')
        return v

class CircuitBreakerStatsModel(BaseModel):
    """Circuit breaker statistics model."""
    breaker_id: UUID
    total_calls: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    average_response_time: float = Field(ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_rate: float = Field(ge=0, le=1)
    success_rate: float = Field(ge=0, le=1)
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    p95_response_time: Optional[float] = None
    p99_response_time: Optional[float] = None
    state_changes: List[Dict[str, Any]] = Field(default_factory=list)
    current_window: Dict[str, Any] = Field(default_factory=dict)
    historical_windows: List[Dict[str, Any]] = Field(default_factory=list)
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    reset_count: int = Field(default=0, ge=0)
    alert_count: int = Field(default=0, ge=0)
    maintenance_count: int = Field(default=0, ge=0)

    @field_validator('error_rate', 'success_rate')
    @classmethod
    def validate_rates(cls, v):
        """Validate rates are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError('rates must be between 0 and 1')
        return v 