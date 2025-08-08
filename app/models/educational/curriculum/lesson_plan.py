"""Lesson plan models for physical education."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date, time, datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from app.models.physical_education.base.base_class import Base

from app.models.core.base import BaseModel as SQLAlchemyBaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin

class GradeLevel(str, Enum):
    K = "K"
    GRADE_1 = "1"
    GRADE_2 = "2"
    GRADE_3 = "3"
    GRADE_4 = "4"
    GRADE_5 = "5"
    GRADE_6 = "6"
    GRADE_7 = "7"
    GRADE_8 = "8"
    GRADE_9 = "9"
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"

class GradeLevelModel(SQLAlchemyBaseModel):
    """Model for grade levels."""
    __tablename__ = "grade_levels"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lesson_plans = relationship("app.models.educational.curriculum.lesson_plan.LessonPlan", back_populates="grade_level")

    def __repr__(self):
        return f"<GradeLevel {self.name}>"

class Subject(str, Enum):
    PHYSICAL_EDUCATION = "Physical Education"
    HEALTH = "Health"
    DRIVERS_ED = "Driver's Education"

class SubjectModel(SQLAlchemyBaseModel):
    """Model for subjects."""
    __tablename__ = "subjects"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lesson_plans = relationship("app.models.educational.curriculum.lesson_plan.LessonPlan", back_populates="subject")

    def __repr__(self):
        return f"<Subject {self.name}>"

class Standard(BaseModel):
    code: str = Field(..., description="Standard code (e.g., 2.1.12.PGD.1)")
    description: str = Field(..., description="Standard description")
    type: str = Field("CCCS", description="Type of standard (e.g., CCCS, SLS)")

class SmartGoal(BaseModel):
    specific: str = Field(..., description="What specifically will be accomplished?")
    measurable: str = Field(..., description="How will progress be measured?")
    achievable: str = Field(..., description="Is this realistic with available resources?")
    relevant: str = Field(..., description="How does this align with broader goals?")
    time_bound: str = Field(..., description="What is the timeframe for achievement?")
    
class Objective(BaseModel):
    smart_goal: SmartGoal
    description: str = Field(..., description="Learning objective")
    assessment_criteria: str = Field(..., description="How the objective will be assessed")
    language_objective: Optional[str] = Field(None, description="Specific objective for ELL students")

class Activity(BaseModel):
    name: str
    description: str
    duration: int = Field(..., description="Duration in minutes")
    materials: List[str] = []
    grouping: Optional[str] = None
    modifications: Optional[Dict[str, str]] = Field(
        None,
        description="Specific modifications for different student groups"
    )
    teaching_phase: str = Field(
        ..., 
        description="Phase of instruction (e.g., Direct Instruction, Guided Practice)"
    )

class Assessment(BaseModel):
    type: str
    description: str
    criteria: List[str]
    tools: Optional[List[str]] = None
    modifications: Optional[Dict[str, str]] = None

class DifferentiationPlan(BaseModel):
    ell_strategies: Dict[str, str] = Field(
        ...,
        description={
            "language_domains": "Reading, Writing, Speaking, Listening focus areas",
            "proficiency_level": "Student language development level",
            "strategies": "Specific ELL teaching strategies",
            "accommodations": "Language accommodations"
        }
    )
    iep_accommodations: Dict[str, str] = Field(
        ...,
        description="Specific accommodations for IEP students"
    )
    section_504_accommodations: Dict[str, str] = Field(
        ...,
        description="Accommodations for 504 students"
    )
    gifted_talented_enrichment: Dict[str, str] = Field(
        ...,
        description="Enrichment activities for gifted students"
    )

class LessonPlan(SQLAlchemyBaseModel):
    """Model for lesson plans."""
    __tablename__ = "lesson_plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("educational_teachers.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade_level_id = Column(Integer, ForeignKey("grade_levels.id"), nullable=False)
    unit_title = Column(String, nullable=False)
    lesson_title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    period = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    essential_question = Column(String, nullable=False)
    do_now = Column(String, nullable=False)
    objectives = Column(JSON, nullable=False)  # List of learning objectives
    anticipatory_set = Column(String, nullable=False)
    direct_instruction = Column(String, nullable=False)
    guided_practice = Column(JSON, nullable=True)  # List of guided practice activities
    independent_practice = Column(JSON, nullable=True)  # List of independent practice activities
    closure = Column(String, nullable=False)
    assessment = Column(JSON, nullable=True)  # Assessment methods and criteria
    materials = Column(JSON, nullable=True)  # List of required materials
    homework = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    reflection = Column(String, nullable=True)
    next_steps = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("app.models.educational.staff.teacher.Teacher", back_populates="lesson_plans")
    subject = relationship("SubjectModel", back_populates="lesson_plans")
    grade_level = relationship("GradeLevelModel")

    def __repr__(self):
        return f"<LessonPlan {self.lesson_title}>"

    class Config:
        json_schema_extra = {
            "example": {
                "teacher_name": "John Doe",
                "subject": "Physical Education",
                "grade_level": "9",
                "unit_title": "Basketball Fundamentals",
                "lesson_title": "Dribbling Techniques",
                "week_of": "2024-03-11",
                "date": "2024-03-15",
                "period": "3",
                "duration": 45,
                "standards": [{
                    "code": "2.1.12.PGD.1",
                    "description": "Develop a health care plan...",
                    "type": "CCCS"
                }],
                "objectives": [{
                    "smart_goal": {
                        "specific": "Master basic basketball dribbling techniques",
                        "measurable": "Complete dribbling course with 80% accuracy",
                        "achievable": "Progressive skill building with modifications",
                        "relevant": "Foundation for advanced basketball skills",
                        "time_bound": "By end of class period"
                    },
                    "description": "Students will demonstrate proper dribbling technique",
                    "assessment_criteria": "Successfully complete dribbling drill with 80% accuracy",
                    "language_objective": "Demonstrate understanding of dribbling terminology"
                }],
                "essential_question": "How does proper dribbling technique improve basketball performance?",
                "do_now": "Quick partner passing warm-up",
                "materials_needed": ["Basketballs", "Cones", "Whistle"],
                "anticipatory_set": "Quick dribbling demonstration and discussion",
                "direct_instruction": "Demonstration of proper dribbling technique with key points",
                "guided_practice": [{
                    "name": "Partner Dribbling Practice",
                    "description": "Students practice in pairs, giving feedback",
                    "duration": 15,
                    "materials": ["Basketballs"],
                    "grouping": "Pairs",
                    "teaching_phase": "Guided Practice",
                    "modifications": {
                        "ell": "Visual demonstrations",
                        "iep": "Modified equipment",
                        "gifted": "Complex patterns"
                    }
                }],
                "independent_practice": [{
                    "name": "Dribbling Course Challenge",
                    "description": "Individual completion of dribbling obstacle course",
                    "duration": 15,
                    "materials": ["Basketballs", "Cones"],
                    "teaching_phase": "Independent Practice"
                }],
                "closure": "Class demonstration and skill review"
            }
        } 