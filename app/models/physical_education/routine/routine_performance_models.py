from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from datetime import datetime

class RoutinePerformanceMetrics(SharedBase):
    """Model for storing routine performance data."""
    __tablename__ = "physical_education_routine_performance"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("physical_education_routines.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    performance_data = Column(JSON, nullable=False)
    completion_time = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=False)
    effort_score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routine = relationship("Routine", back_populates="performance_metrics")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="routine_performance_metrics")

class RoutinePerformanceMetric(SharedBase):
    """Model for storing routine performance metric."""
    __tablename__ = "routine_performance_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("physical_education_routine_performance.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Remove relationship to avoid foreign key constraint issues
    # performance = relationship("RoutinePerformance", viewonly=True)

# Remove the problematic relationship
# RoutinePerformanceMetrics.metrics = relationship("PerformanceMetrics", back_populates="performance") 