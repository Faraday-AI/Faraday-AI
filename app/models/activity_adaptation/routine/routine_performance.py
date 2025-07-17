"""Routine performance models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel
from app.models.activity_adaptation.routine.routine import Routine
from app.models.physical_education.student.student import StudentHealthProfile

class AdaptedRoutinePerformanceBackup(BaseModel):
    """Model for tracking performance of adapted routines."""
    __tablename__ = 'adapted_routine_performances_backup'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey('adapted_routines.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('student_health.id', ondelete='CASCADE'), nullable=False)
    date_performed = Column(DateTime, default=datetime.utcnow)
    completion_time = Column(Float, nullable=True)  # in minutes
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    engagement_level = Column(Integer, nullable=True)  # 1-10 scale
    accuracy_score = Column(Float, nullable=False)  # Added from service-specific version
    effort_score = Column(Float, nullable=False)  # Added from service-specific version
    is_completed = Column(Boolean, default=False)  # Added from service-specific version
    notes = Column(Text, nullable=True)  # Changed from String to Text
    performance_metrics = Column(JSON, nullable=True)  # Additional performance metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    adapted_routine = relationship("AdaptedRoutine", back_populates="performance_backups", overlaps="adapted_routine,performances")
    student = relationship("app.models.physical_education.student.student.StudentHealthProfile", back_populates="adapted_routine_performances", overlaps="student,adapted_routine_performances")
    performance_metrics_records = relationship("AdaptedPerformanceMetrics", back_populates="performance")

    def __repr__(self):
        return f"<AdaptedRoutinePerformance {self.id}>"

class AdaptedPerformanceMetrics(BaseModel):
    """Model for adapted routine performance metrics."""
    __tablename__ = "adapted_performance_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("adapted_routine_performances_backup.id", ondelete='CASCADE'), nullable=False)
    metric_type = Column(String(50), nullable=False)  # heart_rate, speed, form_quality, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # bpm, mph, score, etc.
    timestamp = Column(DateTime, nullable=False)
    metric_metadata = Column(JSON, nullable=True)  # Additional metric data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    performance = relationship("AdaptedRoutinePerformanceBackup", back_populates="performance_metrics_records")

    def __repr__(self):
        return f"<AdaptedPerformanceMetrics {self.performance_id} - {self.metric_type}>" 