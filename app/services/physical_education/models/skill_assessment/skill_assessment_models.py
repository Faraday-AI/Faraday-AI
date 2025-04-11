from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import logging

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