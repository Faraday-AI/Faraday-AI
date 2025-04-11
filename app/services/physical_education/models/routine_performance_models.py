from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class RoutinePerformance(Base):
    """Model for storing routine performance data."""
    __tablename__ = "routine_performance"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routines.id"), nullable=False)
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
    routine = relationship("Routine", back_populates="performances")
    student = relationship("Student", back_populates="routine_performances")

class PerformanceMetrics(Base):
    """Model for storing detailed performance metrics."""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("routine_performance.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    performance = relationship("RoutinePerformance", back_populates="metrics")

# Add relationship to RoutinePerformance
RoutinePerformance.metrics = relationship("PerformanceMetrics", back_populates="performance") 