from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Float, Integer, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, Field, validator

class SafetyIncident(Base):
    """Model for safety incidents."""
    __tablename__ = "safety_incidents"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    incident_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(String, nullable=False)
    action_taken = Column(String, nullable=False)
    incident_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="safety_incidents")
    activity = relationship("Activity", back_populates="safety_incidents")

    def __repr__(self):
        return f"<SafetyIncident {self.incident_type} - {self.student_id}>"

class RiskAssessment(Base):
    """Model for risk assessments."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    environment = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    risk_level = Column(String, nullable=False)
    environmental_risks = Column(JSON, default=list)
    student_risks = Column(JSON, default=list)
    activity_risks = Column(JSON, default=list)
    mitigation_strategies = Column(JSON, default=list)
    assessment_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RiskAssessment {self.id} - {self.risk_level}>"

class SafetyCheck(Base):
    """Model for safety checks."""
    __tablename__ = "safety_checks"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    check_type = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    results = Column(JSON, nullable=False)
    status = Column(String, nullable=False)
    check_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SafetyCheck {self.check_type} - {self.class_id}>"

class EquipmentCheck(Base):
    """Model for equipment safety checks."""
    __tablename__ = "equipment_checks"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    equipment_id = Column(String, nullable=False)
    check_date = Column(DateTime, default=datetime.utcnow)
    maintenance_status = Column(Boolean, nullable=False)
    damage_status = Column(Boolean, nullable=False)
    age_status = Column(Boolean, nullable=False)
    last_maintenance = Column(DateTime)
    purchase_date = Column(DateTime)
    max_age_years = Column(Float)
    equipment_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<EquipmentCheck {self.equipment_id} - {self.class_id}>"

class EnvironmentalCheck(Base):
    """Model for environmental safety checks."""
    __tablename__ = "environmental_checks"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    check_date = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    humidity = Column(Float)
    air_quality = Column(Float)
    surface_conditions = Column(JSON)
    lighting = Column(Float)
    equipment_condition = Column(JSON)
    environmental_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<EnvironmentalCheck {self.class_id} - {self.check_date}>" 