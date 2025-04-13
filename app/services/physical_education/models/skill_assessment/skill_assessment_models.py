from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, Optional

class SkillAssessment(Base):
    """Model for storing skill assessments."""
    __tablename__ = "skill_assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    skill_type = Column(String, nullable=False)
    assessment_data = Column(JSON, nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="skill_assessments")
    activity = relationship("Activity", back_populates="skill_assessments")

class AssessmentCriteria(Base):
    """Model for storing assessment criteria."""
    __tablename__ = "assessment_criteria"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, nullable=False)
    parent_id = Column(Integer, ForeignKey("assessment_criteria.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship for hierarchical criteria
    sub_criteria = relationship("AssessmentCriteria", backref="parent", remote_side=[id])

class AssessmentResult(Base):
    """Model for storing assessment results."""
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("skill_assessments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    score = Column(Float, nullable=False)
    criteria_scores = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("SkillAssessment", backref="results")

class AssessmentHistory(Base):
    """Model for tracking assessment history."""
    __tablename__ = "assessment_history"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("skill_assessments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    previous_score = Column(Float, nullable=True)
    new_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("SkillAssessment", backref="history")

class SkillAssessmentModel:
    """Model for predicting and calculating assessment scores."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.model_path = Path('models/skill_assessment.joblib')
        self._load_model()

    def _load_model(self):
        """Load the trained model if available."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(str(self.model_path))
            else:
                self.logger.warning(f"Model file not found at {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            self.model = None

    def calculate_score(
        self,
        assessment_data: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> float:
        """Calculate overall assessment score based on criteria."""
        try:
            overall_score = 0.0
            for criterion, config in criteria.items():
                if criterion in assessment_data:
                    criterion_score = 0.0
                    for sub_criterion, weight in config['sub_criteria'].items():
                        if sub_criterion in assessment_data[criterion]:
                            criterion_score += assessment_data[criterion][sub_criterion] * weight
                    overall_score += criterion_score * config['weight']
            return min(max(overall_score, 0.0), 1.0)
        except Exception as e:
            self.logger.error(f"Error calculating score: {str(e)}")
            return 0.0

# Add relationships to SkillAssessment
SkillAssessment.results = relationship("AssessmentResult", back_populates="assessment")
SkillAssessment.history = relationship("AssessmentHistory", back_populates="assessment")

class SkillProgress(Base):
    """Model for tracking skill progress over time."""
    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("skill_assessments.id"), nullable=False)
    previous_score = Column(Float, nullable=False)
    current_score = Column(Float, nullable=False)
    progress_metrics = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("SkillAssessment", back_populates="progress_history")

# Add relationship to SkillAssessment
SkillAssessment.progress_history = relationship("SkillProgress", back_populates="assessment")

class SkillModels:
    """Service for managing skill assessment models and operations."""
    
    def __init__(self):
        self.logger = logging.getLogger("skill_models")
        self.assessment_history = []
        self.progress_tracking = {}
        self.skill_benchmarks = {}
        
    async def initialize(self):
        """Initialize skill assessment resources."""
        try:
            await self.load_skill_benchmarks()
            self.logger.info("Skill models initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing skill models: {str(e)}")
            raise
            
    async def cleanup(self):
        """Cleanup skill assessment resources."""
        try:
            self.assessment_history.clear()
            self.progress_tracking.clear()
            self.skill_benchmarks.clear()
            self.logger.info("Skill models cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up skill models: {str(e)}")
            raise
            
    async def load_skill_benchmarks(self):
        """Load skill benchmarks for different activities."""
        try:
            self.skill_benchmarks = {
                "throwing": {
                    "velocity": {"excellent": 30.0, "good": 25.0, "average": 20.0},
                    "accuracy": {"excellent": 0.9, "good": 0.8, "average": 0.7},
                    "form_score": {"excellent": 0.9, "good": 0.8, "average": 0.7}
                },
                "jumping": {
                    "height": {"excellent": 0.6, "good": 0.5, "average": 0.4},
                    "power": {"excellent": 2000, "good": 1800, "average": 1600},
                    "form_score": {"excellent": 0.9, "good": 0.8, "average": 0.7}
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading skill benchmarks: {str(e)}")
            raise 