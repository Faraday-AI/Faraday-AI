"""Pydantic schemas for lesson plans."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class Subject(str, Enum):
    PHYSICAL_EDUCATION = "Physical Education"
    HEALTH = "Health"
    DRIVERS_ED = "Driver's Education"

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

class StandardSchema(BaseModel):
    code: str = Field(..., description="Standard code (e.g., 2.1.12.PGD.1)")
    description: str = Field(..., description="Standard description")
    type: str = Field("CCCS", description="Type of standard (e.g., CCCS, SLS)")

class ActivitySchema(BaseModel):
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

class AssessmentSchema(BaseModel):
    type: str
    description: str
    criteria: List[str]
    tools: Optional[List[str]] = None
    modifications: Optional[Dict[str, str]] = None

class DifferentiationPlanSchema(BaseModel):
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

class LessonPlanSchema(BaseModel):
    """Schema for lesson plan responses."""
    teacher_id: UUID
    curriculum_id: Optional[int] = None
    subject: Subject
    grade_level: GradeLevel
    unit_title: str
    lesson_title: str
    week_of: datetime
    date: datetime
    period: Optional[str] = None
    duration: int

    # Standards and Objectives
    standards: List[StandardSchema]
    objectives: List[Dict[str, Any]]

    # Lesson Components
    essential_question: str
    do_now: str
    materials_needed: List[str]
    
    # Instructional Plan
    anticipatory_set: str
    direct_instruction: str
    guided_practice: List[ActivitySchema]
    independent_practice: List[ActivitySchema]
    closure: str
    
    # Assessment and Differentiation
    assessments: List[AssessmentSchema]
    differentiation: DifferentiationPlanSchema
    
    # Additional Components
    homework: Optional[str] = None
    notes: Optional[str] = None
    reflection: Optional[str] = None
    next_steps: Optional[str] = None

    class Config:
        from_attributes = True 