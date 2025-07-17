from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.physical_education.base.base_class import Base
import enum

class MetricType(str, enum.Enum):
    """Types of health metrics that can be tracked."""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BODY_TEMPERATURE = "body_temperature"
    WEIGHT = "weight"
    HEIGHT = "height"
    BMI = "bmi"
    BODY_FAT = "body_fat"
    OXYGEN_SATURATION = "oxygen_saturation"
    RESPIRATORY_RATE = "respiratory_rate"
    FLEXIBILITY = "flexibility"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    BALANCE = "balance"
    COORDINATION = "coordination"

class MeasurementUnit(str, enum.Enum):
    """Available measurement units."""
    # Weight
    KG = "kg"
    LBS = "lbs"
    # Height
    CM = "cm"
    INCHES = "inches"
    # Temperature
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    # Heart Rate
    BPM = "bpm"
    # Blood Pressure
    MMHG = "mmHg"
    # Percentage
    PERCENT = "percent"
    # Time
    SECONDS = "seconds"
    MINUTES = "minutes"
    # Distance
    METERS = "meters"
    KILOMETERS = "kilometers"
    MILES = "miles"
    # Generic
    SCORE = "score"
    LEVEL = "level"

class HealthMetric(Base):
    """Model for tracking fitness health metrics."""
    __tablename__ = 'fitness_health_metrics'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # e.g., "heart_rate", "blood_pressure", "weight"
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # e.g., "bpm", "mmHg", "kg"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text)
    metric_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="health_metrics", overlaps="student,health_metrics")
    history = relationship("HealthMetricHistory", back_populates="metric", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HealthMetric {self.metric_type} - {self.value} {self.unit}>"

class GeneralHealthMetricThreshold(Base):
    """Model for storing acceptable ranges for health metrics."""
    __tablename__ = "health_metric_thresholds"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(Enum(MetricType), nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    unit = Column(Enum(MeasurementUnit), nullable=False)
    age_group = Column(String, nullable=False)  # e.g., "5-7", "8-10", etc.
    gender = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HealthMetricHistory(Base):
    """Model for tracking fitness health metric history."""
    __tablename__ = 'fitness_health_metric_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, ForeignKey("fitness_health_metrics.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    change_reason = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    metric = relationship("HealthMetric", back_populates="history")
    student = relationship("Student", back_populates="health_metric_history", overlaps="student,health_metric_history")

    def __repr__(self):
        return f"<HealthMetricHistory {self.metric_id} - {self.old_value} -> {self.new_value}>"

class FitnessMetric(Base):
    """Model for tracking fitness-specific metrics."""
    __tablename__ = 'fitness_metrics'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # e.g., "strength", "endurance", "flexibility"
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # e.g., "reps", "minutes", "score"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text)
    metric_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="fitness_metrics", overlaps="student,fitness_metrics")
    history = relationship("FitnessMetricHistory", back_populates="metric", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FitnessMetric {self.metric_type} - {self.value} {self.unit}>"

class FitnessMetricHistory(Base):
    """Model for tracking fitness metric history."""
    __tablename__ = 'fitness_metric_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, ForeignKey("fitness_metrics.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    change_reason = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    metric = relationship("FitnessMetric", back_populates="history")
    student = relationship("Student", back_populates="fitness_metric_history", overlaps="student,fitness_metric_history")

    def __repr__(self):
        return f"<FitnessMetricHistory {self.metric_id} - {self.old_value} -> {self.new_value}>" 