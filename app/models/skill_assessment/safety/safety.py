"""Safety models for physical education."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.physical_education.base.sqlalchemy_base import BaseModelMixin
from app.db.mixins import TimestampMixin, StatusMixin
from app.models.physical_education.base.base_class import PEBase

class IncidentSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(enum.Enum):
    INJURY = "injury"
    EQUIPMENT_FAILURE = "equipment_failure"
    ENVIRONMENTAL = "environmental"
    MEDICAL = "medical"
    OTHER = "other"

class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AlertType(enum.Enum):
    RISK_THRESHOLD = "risk_threshold"
    EMERGENCY = "emergency"
    PROTOCOL = "protocol"
    MAINTENANCE = "maintenance"
    WEATHER = "weather"

class CheckType(enum.Enum):
    EQUIPMENT = "equipment"
    ENVIRONMENT = "environment"
    STUDENT = "student"
    ACTIVITY = "activity"

class SkillAssessmentSafetyIncident(BaseModelMixin, TimestampMixin):
    """Model for tracking safety incidents in skill assessment context."""
    
    __tablename__ = "skill_assessment_safety_incidents"
    __table_args__ = {'extend_existing': True}
    
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    incident_type = Column(SQLEnum(IncidentType, name='incident_type_enum'), nullable=False)
    severity = Column(SQLEnum(IncidentSeverity, name='incident_severity_enum'), nullable=False)
    description = Column(String(1000), nullable=False)
    response_taken = Column(String(1000), nullable=False)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String(255), nullable=True)
    equipment_involved = Column(JSON, nullable=True)
    witnesses = Column(JSON, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SafetyIncident {self.incident_type} - {self.severity}>"

class RiskAssessment(BaseModelMixin, TimestampMixin):
    """Model for storing risk assessments."""
    
    __tablename__ = "skill_assessment_risk_assessments"
    __table_args__ = {'extend_existing': True}
    
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    risk_level = Column(SQLEnum(RiskLevel, name='risk_level_enum'), nullable=False)
    factors = Column(JSON, nullable=False)  # List of risk factors
    mitigation_measures = Column(JSON, nullable=False)  # List of mitigation measures
    environmental_conditions = Column(JSON, nullable=True)
    equipment_status = Column(JSON, nullable=True)
    student_health_considerations = Column(JSON, nullable=True)
    weather_conditions = Column(JSON, nullable=True)
    assessed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="risk_assessments", overlaps="activity,risk_assessments")
    assessor = relationship("User", back_populates="conducted_assessments", overlaps="user,conducted_assessments")

class SafetyAlert(BaseModelMixin, TimestampMixin):
    """Model for safety alerts and notifications."""
    
    __tablename__ = "skill_assessment_safety_alerts"
    __table_args__ = {'extend_existing': True}
    
    alert_type = Column(SQLEnum(AlertType, name='alert_type_enum'), nullable=False)
    severity = Column(SQLEnum(IncidentSeverity, name='alert_incident_severity_enum'), nullable=False)
    message = Column(String(1000), nullable=False)
    recipients = Column(JSON, nullable=False)  # List of user IDs
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety_alerts", overlaps="activity,safety_alerts")
    equipment = relationship("Equipment", back_populates="safety_alerts", overlaps="equipment,safety_alerts")
    creator = relationship("User", back_populates="created_alerts", overlaps="user,created_alerts")

class SafetyProtocol(BaseModelMixin, TimestampMixin):
    """Model for storing safety protocols."""
    
    __tablename__ = "skill_assessment_safety_protocols"
    __table_args__ = {'extend_existing': True}
    
    description = Column(String(1000), nullable=False)
    activity_type = Column(String(100), nullable=True)
    protocol_type = Column(String(100), nullable=False)  # e.g., "pre_activity", "emergency", "equipment"
    steps = Column(JSON, nullable=False)  # List of protocol steps
    required_equipment = Column(JSON, nullable=True)
    emergency_contacts = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_protocols", overlaps="user,created_protocols")
    safety = relationship("Safety", back_populates="protocols", overlaps="safety,protocols")

class SafetyCheck(BaseModelMixin, TimestampMixin):
    """Base model for safety checks."""
    
    __tablename__ = "skill_assessment_safety_checks"
    __table_args__ = {'extend_existing': True}
    
    check_type = Column(SQLEnum(CheckType, name='check_type_enum'), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False)  # passed, failed, needs_attention
    notes = Column(String(1000))
    issues_found = Column(JSON)  # List of issues found
    actions_taken = Column(JSON)  # List of actions taken
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(String(1000))
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety_checks", overlaps="activity,safety_checks")
    performer = relationship("User", back_populates="performed_checks", overlaps="user,performed_checks")
    safety = relationship("Safety", back_populates="checks", overlaps="safety,checks")
    environmental_details = relationship("EnvironmentalCheck", back_populates="safety_check", cascade="all, delete-orphan", overlaps="safety_check,environmental_details")
    equipment_details = relationship("EquipmentCheck", back_populates="safety_check", cascade="all, delete-orphan", overlaps="safety_check,equipment_details")

class EnvironmentalCheck(BaseModelMixin, TimestampMixin):
    """Model for environmental safety checks."""
    
    __tablename__ = "skill_assessment_environmental_checks"
    __table_args__ = {'extend_existing': True}
    
    safety_check_id = Column(Integer, ForeignKey("safety_checks.id"), nullable=False)
    temperature = Column(Integer)  # in Celsius
    humidity = Column(Integer)  # percentage
    lighting_level = Column(String(50))  # adequate, inadequate
    ventilation_status = Column(String(50))  # good, poor
    surface_condition = Column(String(50))  # dry, wet, damaged
    hazards_present = Column(JSON)  # List of hazards found
    weather_conditions = Column(JSON)  # Current weather conditions
    
    # Relationships
    safety_check = relationship("SafetyCheck", back_populates="environmental_details", overlaps="safety_check,environmental_details")

class EquipmentCheck(BaseModelMixin, TimestampMixin):
    """Model for equipment safety checks."""
    
    __tablename__ = "equipment_checks"
    __table_args__ = {'extend_existing': True}
    
    safety_check_id = Column(Integer, ForeignKey("safety_checks.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    condition = Column(String(50))  # good, fair, poor, damaged
    maintenance_needed = Column(Boolean, default=False)
    maintenance_type = Column(String(100))
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    inspection_points = Column(JSON)  # List of points checked
    damage_description = Column(String(1000))
    replacement_needed = Column(Boolean, default=False)
    
    # Relationships
    safety_check = relationship("SafetyCheck", back_populates="equipment_details", overlaps="safety_check,equipment_details")
    equipment = relationship("Equipment", back_populates="safety_checks", overlaps="equipment,safety_checks")

class Safety(BaseModelMixin, TimestampMixin, StatusMixin):
    """Base model for safety management."""
    
    __tablename__ = "safety"
    __table_args__ = {'extend_existing': True}
    
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    risk_level = Column(SQLEnum(RiskLevel, name='risk_level_enum'), nullable=False)
    safety_notes = Column(String(1000))
    safety_metadata = Column(JSON)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety", overlaps="activity,safety")
    incidents = relationship("SafetyIncident", back_populates="safety", overlaps="safety,incidents")
    protocols = relationship("SafetyProtocol", back_populates="safety", overlaps="safety,protocols")
    checks = relationship("SafetyCheck", back_populates="safety", overlaps="safety,checks")

    def __repr__(self):
        return f"<Safety {self.id} - {self.safety_status}>"

class SafetyReport(BaseModelMixin, TimestampMixin):
    """Model for safety reports, particularly for equipment."""
    
    __tablename__ = "safety_reports"
    __table_args__ = {'extend_existing': True}
    
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # maintenance, damage, inspection
    severity = Column(SQLEnum(IncidentSeverity, name='final_incident_severity_enum'), nullable=False)
    description = Column(Text, nullable=False)
    action_needed = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)  # URLs to any attached images
    report_metadata = Column(JSON, nullable=True)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="safety_reports", overlaps="equipment,safety_reports")
    reporter = relationship("User", back_populates="safety_reports", overlaps="user,safety_reports")

    def __repr__(self):
        return f"<SafetyReport {self.report_type} - {self.severity}>" 