"""
Health models for tracking student health metrics and conditions.

This module contains models for tracking student health metrics, conditions,
and monitoring capabilities.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from app.models.base import Base

class HealthMetric(Base, TimestampedMixin, MetadataMixin):
    """Model for tracking general health metrics."""
    
    __tablename__ = "general_health_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    metric_type = Column(String, nullable=False, index=True)  # e.g., "heart_rate", "blood_pressure"
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # e.g., "bpm", "mmHg"
    notes = Column(String, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="health_metrics", overlaps="student,health_metrics")
    history = relationship("HealthMetricHistory", back_populates="metric", cascade="all, delete-orphan", overlaps="metric,history")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "student_id": self.student_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "notes": self.notes
        }

class HealthMetricHistory(Base, TimestampedMixin):
    """Model for tracking general health metric history."""
    __tablename__ = 'general_health_metric_history'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("fitness_health_metrics.id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    # Relationships
    metric = relationship("HealthMetric", back_populates="history", overlaps="metric,history")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "metric_id": self.metric_id,
            "value": self.value,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "notes": self.notes
        }

class HealthCondition(Base, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for tracking student health conditions."""
    
    __tablename__ = "health_fitness_health_conditions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    severity = Column(String, nullable=False)  # e.g., "mild", "moderate", "severe"
    diagnosis_date = Column(DateTime, nullable=False)
    treatment_plan = Column(String, nullable=True)
    restrictions = Column(JSON, nullable=True)  # e.g., {"activities": ["running"], "duration": "30min"}
    notes = Column(String, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="health_conditions", overlaps="student,health_conditions")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "student_id": self.student_id,
            "severity": self.severity,
            "diagnosis_date": self.diagnosis_date.isoformat() if self.diagnosis_date else None,
            "treatment_plan": self.treatment_plan,
            "restrictions": self.restrictions,
            "notes": self.notes
        }

class HealthAlert(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for tracking health-related alerts."""
    
    __tablename__ = "health_fitness_health_alerts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    alert_type = Column(String, nullable=False, index=True)  # e.g., "allergy", "injury", "condition"
    severity = Column(String, nullable=False)  # e.g., "low", "medium", "high"
    description = Column(String, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    action_taken = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="health_alerts", overlaps="student,health_alerts")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "student_id": self.student_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "description": self.description,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "action_taken": self.action_taken,
            "notes": self.notes
        }

class HealthCheck(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for tracking routine health checks."""
    
    __tablename__ = "health_fitness_health_checks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    check_type = Column(String, nullable=False, index=True)  # e.g., "pre_activity", "post_activity", "routine"
    performed_by = Column(String, nullable=False)  # e.g., "teacher", "nurse", "system"
    findings = Column(JSON, nullable=True)
    recommendations = Column(String, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="health_checks", overlaps="student,health_checks")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "student_id": self.student_id,
            "check_type": self.check_type,
            "performed_by": self.performed_by,
            "findings": self.findings,
            "recommendations": self.recommendations
        } 