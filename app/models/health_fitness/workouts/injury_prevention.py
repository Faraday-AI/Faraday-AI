"""
Injury prevention models for tracking risk factors and prevention strategies.

This module contains models for monitoring injury risks, implementing
prevention strategies, and tracking their effectiveness.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.shared_base import SharedBase
from app.models.mixins import NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from app.models.activity import Activity

# Association table for many-to-many relationship between InjuryRiskFactor and SafetyGuideline
injury_risk_factor_safety_guidelines = Table('injury_risk_factor_safety_guidelines', SharedBase.metadata,
    Column('risk_factor_id', Integer, ForeignKey('injury_risk_factors.id'), primary_key=True),
    Column('safety_guideline_id', Integer, ForeignKey('safety_guidelines.id'), primary_key=True),
    extend_existing=True
)

class InjuryPreventionBaseModel(SharedBase, TimestampedMixin, MetadataMixin):
    """Base model for injury prevention with metadata, audit, and validation support."""
    
    __abstract__ = True
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return super().dict()

class InjuryRiskFactor(InjuryPreventionBaseModel, NamedMixin, StatusMixin):
    """Model for tracking injury risk factors."""
    
    __tablename__ = "injury_risk_factors"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    category = Column(String, nullable=False)
    affected_activities = Column(JSON, nullable=True)
    prevention_strategies = Column(JSON, nullable=True)
    monitoring_frequency = Column(String, nullable=False)
    prevention_program_id = Column(Integer, ForeignKey("injury_preventions.id"), nullable=True, index=True)
    
    # Risk details
    risk_indicators = Column(JSON, nullable=True)
    contributing_factors = Column(JSON, nullable=True)
    early_warning_signs = Column(JSON, nullable=True)
    impact_severity = Column(String, nullable=True)
    occurrence_likelihood = Column(String, nullable=True)
    
    # Prevention planning
    prevention_priority = Column(String, nullable=False, default="medium")
    required_resources = Column(JSON, nullable=True)
    implementation_timeline = Column(JSON, nullable=True)
    success_metrics = Column(JSON, nullable=True)
    validation_criteria = Column(JSON, nullable=True)
    
    # Monitoring
    next_assessment = Column(DateTime, nullable=True)
    monitoring_history = Column(JSON, nullable=True)
    incident_history = Column(JSON, nullable=True)
    effectiveness_metrics = Column(JSON, nullable=True)
    
    # Education and awareness
    training_requirements = Column(JSON, nullable=True)
    awareness_materials = Column(JSON, nullable=True)
    communication_plan = Column(JSON, nullable=True)
    
    # Relationships
    assessments = relationship("InjuryRiskAssessment", back_populates="risk_factor", cascade="all, delete-orphan")
    prevention_measures = relationship("PreventionMeasure", back_populates="risk_factor", cascade="all, delete-orphan")
    prevention_program = relationship("InjuryPrevention", back_populates="risk_factors")
    safety_guidelines = relationship("SafetyGuideline", secondary=injury_risk_factor_safety_guidelines, back_populates="risk_factors")

class PreventionMeasure(InjuryPreventionBaseModel, NamedMixin, StatusMixin):
    """Model for tracking injury prevention measures."""
    
    __tablename__ = "prevention_measures"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    risk_factor_id = Column(Integer, ForeignKey("injury_risk_factors.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    implementation_steps = Column(JSON, nullable=False)
    effectiveness_rating = Column(Float, nullable=True)
    next_scheduled = Column(DateTime, nullable=True)
    
    # Implementation details
    target_population = Column(JSON, nullable=True)
    required_equipment = Column(JSON, nullable=True)
    training_needed = Column(JSON, nullable=True)
    cost_estimates = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    
    # Monitoring and evaluation
    success_criteria = Column(JSON, nullable=True)
    monitoring_metrics = Column(JSON, nullable=True)
    evaluation_frequency = Column(String, nullable=True)
    compliance_metrics = Column(JSON, nullable=True)
    feedback_mechanism = Column(JSON, nullable=True)
    
    # Adaptation and improvement
    modification_history = Column(JSON, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)
    lessons_learned = Column(JSON, nullable=True)
    
    # Documentation
    documentation_required = Column(JSON, nullable=True)
    reporting_requirements = Column(JSON, nullable=True)
    review_schedule = Column(JSON, nullable=True)
    
    # Relationships
    risk_factor = relationship("InjuryRiskFactor", back_populates="prevention_measures")
    assessments = relationship("PreventionAssessment", back_populates="measure", cascade="all, delete-orphan")

class PreventionAssessment(InjuryPreventionBaseModel, StatusMixin):
    """Model for assessing prevention measure effectiveness."""
    
    __tablename__ = "prevention_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    measure_id = Column(Integer, ForeignKey("prevention_measures.id"), nullable=False, index=True)
    effectiveness_score = Column(Float, nullable=False)
    compliance_rate = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    next_assessment_date = Column(DateTime, nullable=True)
    
    # Assessment details
    assessment_type = Column(String, nullable=False)
    assessment_method = Column(String, nullable=False)
    data_collected = Column(JSON, nullable=True)
    analysis_results = Column(JSON, nullable=True)
    key_findings = Column(JSON, nullable=True)
    
    # Impact analysis
    impact_metrics = Column(JSON, nullable=True)
    cost_benefit_analysis = Column(JSON, nullable=True)
    resource_utilization = Column(JSON, nullable=True)
    implementation_quality = Column(Float, nullable=True)
    
    # Follow-up
    action_items = Column(JSON, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    responsible_parties = Column(JSON, nullable=True)
    
    # Documentation
    supporting_evidence = Column(JSON, nullable=True)
    assessment_notes = Column(String, nullable=True)
    limitations = Column(JSON, nullable=True)
    
    # Relationships
    measure = relationship("PreventionMeasure", back_populates="assessments")

class InjuryRiskAssessment(InjuryPreventionBaseModel, StatusMixin):
    """Model for conducting risk assessments."""
    
    __tablename__ = "injury_risk_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    risk_factor_id = Column(Integer, ForeignKey("injury_risk_factors.id"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    factors_considered = Column(JSON, nullable=False)
    mitigation_plan = Column(JSON, nullable=True)
    
    # Assessment details
    assessment_method = Column(String, nullable=False)
    data_sources = Column(JSON, nullable=True)
    assessment_scope = Column(JSON, nullable=True)
    limitations = Column(JSON, nullable=True)
    
    # Risk analysis
    probability_score = Column(Float, nullable=True)
    impact_score = Column(Float, nullable=True)
    risk_matrix = Column(JSON, nullable=True)
    risk_trends = Column(JSON, nullable=True)
    
    # Controls and mitigation
    existing_controls = Column(JSON, nullable=True)
    proposed_controls = Column(JSON, nullable=True)
    control_effectiveness = Column(JSON, nullable=True)
    residual_risk = Column(Float, nullable=True)
    
    # Action planning
    action_items = Column(JSON, nullable=True)
    responsible_parties = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    resource_requirements = Column(JSON, nullable=True)
    
    # Monitoring
    monitoring_requirements = Column(JSON, nullable=True)
    review_frequency = Column(String, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    
    # Relationships
    risk_factor = relationship("InjuryRiskFactor", back_populates="assessments")
    activity = relationship("app.models.physical_education.activity.models.Activity")

class InjuryPrevention(InjuryPreventionBaseModel, NamedMixin, StatusMixin):
    """Model for injury prevention programs and strategies."""
    
    __tablename__ = "injury_preventions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    target_population = Column(JSON, nullable=True)
    implementation_plan = Column(JSON, nullable=False)
    effectiveness_metrics = Column(JSON, nullable=True)
    cost_estimates = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    
    # Program details
    program_type = Column(String, nullable=False)
    risk_factors_addressed = Column(JSON, nullable=True)
    prevention_strategies = Column(JSON, nullable=False)
    training_requirements = Column(JSON, nullable=True)
    equipment_needed = Column(JSON, nullable=True)
    
    # Monitoring and evaluation
    success_criteria = Column(JSON, nullable=True)
    monitoring_frequency = Column(String, nullable=True)
    evaluation_methods = Column(JSON, nullable=True)
    reporting_requirements = Column(JSON, nullable=True)
    
    # Relationships
    risk_factors = relationship("InjuryRiskFactor", back_populates="prevention_program")
    assessments = relationship("InjuryPreventionRiskAssessment", back_populates="prevention_program")

    def __repr__(self):
        return f"<InjuryPrevention {self.name} - {self.program_type}>"

class InjuryPreventionRiskAssessment(InjuryPreventionBaseModel, StatusMixin):
    """Model for comprehensive injury risk assessments."""
    
    __tablename__ = "injury_prevention_risk_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prevention_program_id = Column(Integer, ForeignKey("injury_preventions.id"), nullable=False, index=True)
    assessment_date = Column(DateTime, nullable=False)
    overall_risk_score = Column(Float, nullable=False)
    risk_factors_evaluated = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=True)
    
    # Assessment details
    assessment_method = Column(String, nullable=False)
    assessor = Column(String, nullable=False)
    data_sources = Column(JSON, nullable=True)
    limitations = Column(JSON, nullable=True)
    
    # Risk analysis
    high_risk_areas = Column(JSON, nullable=True)
    medium_risk_areas = Column(JSON, nullable=True)
    low_risk_areas = Column(JSON, nullable=True)
    risk_trends = Column(JSON, nullable=True)
    
    # Action planning
    immediate_actions = Column(JSON, nullable=True)
    short_term_actions = Column(JSON, nullable=True)
    long_term_actions = Column(JSON, nullable=True)
    responsible_parties = Column(JSON, nullable=True)
    
    # Follow-up
    next_assessment_date = Column(DateTime, nullable=True)
    monitoring_plan = Column(JSON, nullable=True)
    
    # Relationships
    prevention_program = relationship("InjuryPrevention", back_populates="assessments")

    def __repr__(self):
        return f"<InjuryPreventionRiskAssessment {self.id} - Score: {self.overall_risk_score}>"

class SafetyGuideline(InjuryPreventionBaseModel, NamedMixin, StatusMixin):
    """Model for safety guidelines and protocols."""
    
    __tablename__ = "safety_guidelines"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    guidelines = Column(JSON, nullable=False)
    compliance_requirements = Column(JSON, nullable=True)
    
    # Implementation
    target_activities = Column(JSON, nullable=True)
    equipment_requirements = Column(JSON, nullable=True)
    training_requirements = Column(JSON, nullable=True)
    supervision_requirements = Column(JSON, nullable=True)
    
    # Monitoring
    compliance_metrics = Column(JSON, nullable=True)
    review_frequency = Column(String, nullable=True)
    last_review_date = Column(DateTime, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    
    # Documentation
    reference_materials = Column(JSON, nullable=True)
    emergency_procedures = Column(JSON, nullable=True)
    contact_information = Column(JSON, nullable=True)
    
    # Relationships
    risk_factors = relationship("InjuryRiskFactor", secondary=injury_risk_factor_safety_guidelines, back_populates="safety_guidelines")

    def __repr__(self):
        return f"<SafetyGuideline {self.name} - {self.category}>" 