"""
Health Models

This module defines health-related models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, Float, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    AlertType,
    CheckType
)

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampMixin = TimestampedMixin

class HealthMetric(BaseModelMixin, TimestampMixin):
    """Model for tracking health metrics."""
    __tablename__ = 'health_metrics'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships using simple class names since they are already imported
    student = relationship('Student', back_populates='pe_health_metrics')
    history = relationship('app.models.physical_education.health.models.HealthMetricHistory', back_populates='metric')

class HealthMetricCreate(BaseModel):
    """Pydantic model for creating health metrics."""
    
    student_id: int
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime
    notes: Optional[str] = None

class HealthMetricUpdate(BaseModel):
    """Pydantic model for updating health metrics."""
    
    student_id: Optional[int] = None
    metric_type: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None

class HealthMetricResponse(BaseModel):
    """Pydantic model for health metric responses."""
    
    id: int
    student_id: int
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthCondition(BaseModelMixin, TimestampMixin):
    """Model for tracking health conditions."""
    __tablename__ = 'health_conditions'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    condition_name = Column(String(100), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)
    diagnosis_date = Column(DateTime)
    treatment = Column(Text)
    restrictions = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship('Student', back_populates='pe_health_conditions')
    alerts = relationship('app.models.physical_education.health.models.HealthAlert', back_populates='condition')

class HealthConditionCreate(BaseModel):
    """Pydantic model for creating health conditions."""
    
    student_id: int
    condition_name: str
    description: Optional[str] = None
    severity: str
    diagnosis_date: Optional[datetime] = None
    treatment: Optional[str] = None
    restrictions: Optional[str] = None
    notes: Optional[str] = None

class HealthConditionUpdate(BaseModel):
    """Pydantic model for updating health conditions."""
    
    student_id: Optional[int] = None
    condition_name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    diagnosis_date: Optional[datetime] = None
    treatment: Optional[str] = None
    restrictions: Optional[str] = None
    notes: Optional[str] = None

class HealthConditionResponse(BaseModel):
    """Pydantic model for health condition responses."""
    
    id: int
    student_id: int
    condition_name: str
    description: Optional[str] = None
    severity: str
    diagnosis_date: Optional[datetime] = None
    treatment: Optional[str] = None
    restrictions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthAlert(BaseModelMixin, TimestampMixin):
    """Model for tracking health alerts."""
    __tablename__ = 'health_alerts'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    condition_id = Column(Integer, ForeignKey('health_conditions.id'))
    alert_type = Column(Enum(AlertType, name='alert_type_enum'), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship('app.models.physical_education.student.models.Student', back_populates='health_alerts')
    condition = relationship('app.models.physical_education.health.models.HealthCondition', back_populates='alerts')

class HealthAlertCreate(BaseModel):
    """Pydantic model for creating health alerts."""
    
    student_id: int
    condition_id: Optional[int] = None
    alert_type: AlertType
    message: str
    severity: str
    is_active: bool = True
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None

class HealthAlertUpdate(BaseModel):
    """Pydantic model for updating health alerts."""
    
    student_id: Optional[int] = None
    condition_id: Optional[int] = None
    alert_type: Optional[AlertType] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None

class HealthAlertResponse(BaseModel):
    """Pydantic model for health alert responses."""
    
    id: int
    student_id: int
    condition_id: Optional[int] = None
    alert_type: AlertType
    message: str
    severity: str
    is_active: bool
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthCheck(BaseModelMixin, TimestampMixin):
    """Model for tracking health checks."""
    __tablename__ = 'health_checks'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    check_type = Column(Enum(CheckType, name='check_type_enum'), nullable=False)
    status = Column(String(20), nullable=False)
    performed_at = Column(DateTime, nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship('app.models.physical_education.student.models.Student', back_populates='health_checks')
    teacher = relationship('app.models.core.user.User', back_populates='health_checks')

class HealthCheckCreate(BaseModel):
    """Pydantic model for creating health checks."""
    
    student_id: int
    check_type: CheckType
    status: str
    performed_at: datetime
    performed_by: int
    notes: Optional[str] = None

class HealthCheckUpdate(BaseModel):
    """Pydantic model for updating health checks."""
    
    student_id: Optional[int] = None
    check_type: Optional[CheckType] = None
    status: Optional[str] = None
    performed_at: Optional[datetime] = None
    performed_by: Optional[int] = None
    notes: Optional[str] = None

class HealthCheckResponse(BaseModel):
    """Pydantic model for health check responses."""
    
    id: int
    student_id: int
    check_type: CheckType
    status: str
    performed_at: datetime
    performed_by: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthMetricHistory(BaseModelMixin, TimestampMixin):
    """Model for tracking health metric history."""
    __tablename__ = 'health_metric_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('health_metrics.id'), nullable=False)
    value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships using full module path to avoid circular imports
    metric = relationship('app.models.physical_education.health.models.HealthMetric', back_populates='history')

class HealthMetricHistoryCreate(BaseModel):
    """Pydantic model for creating health metric history entries."""
    
    metric_id: int
    value: float
    recorded_at: datetime
    notes: Optional[str] = None

class HealthMetricHistoryUpdate(BaseModel):
    """Pydantic model for updating health metric history entries."""
    
    metric_id: Optional[int] = None
    value: Optional[float] = None
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None

class HealthMetricHistoryResponse(BaseModel):
    """Pydantic model for health metric history responses."""
    
    id: int
    metric_id: int
    value: float
    recorded_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 