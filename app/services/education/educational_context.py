from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

class SubjectArea(str, Enum):
    MATH = "math"
    SCIENCE = "science"
    ENGLISH = "english"
    HISTORY = "history"
    COMPUTER_SCIENCE = "computer_science"
    GENERAL = "general"

class LearningLevel(str, Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    PROFESSIONAL = "professional"

class TeachingStyle(str, Enum):
    TRADITIONAL = "traditional"
    INQUIRY_BASED = "inquiry_based"
    PROJECT_BASED = "project_based"
    FLIPPED_CLASSROOM = "flipped_classroom"
    DIFFERENTIATED = "differentiated"
    BLENDED = "blended"

class EducationalContext(BaseModel):
    subject_area: SubjectArea
    learning_level: LearningLevel
    teaching_style: TeachingStyle
    specific_topic: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    
    def to_prompt_context(self) -> str:
        context = [
            f"Subject Area: {self.subject_area.value}",
            f"Learning Level: {self.learning_level.value}",
            f"Teaching Style: {self.teaching_style.value}"
        ]
        
        if self.specific_topic:
            context.append(f"Specific Topic: {self.specific_topic}")
            
        if self.learning_objectives:
            objectives = "\n- ".join(self.learning_objectives)
            context.append(f"Learning Objectives:\n- {objectives}")
            
        if self.prerequisites:
            prereqs = "\n- ".join(self.prerequisites)
            context.append(f"Prerequisites:\n- {prereqs}")
            
        return "\n".join(context)

class EducationalPromptService:
    def __init__(self):
        self.default_context = EducationalContext(
            subject_area=SubjectArea.GENERAL,
            learning_level=LearningLevel.UNDERGRADUATE,
            teaching_style=TeachingStyle.TRADITIONAL
        )
    
    def generate_lesson_prompt(self, context: Optional[EducationalContext] = None) -> str:
        ctx = context or self.default_context
        return f"""
Please generate a lesson plan with the following educational context:

{ctx.to_prompt_context()}

The lesson plan should include:
1. Introduction and motivation
2. Main concepts and definitions
3. Examples and exercises
4. Assessment strategies
5. Additional resources
"""

    def generate_exercise_prompt(self, context: Optional[EducationalContext] = None) -> str:
        ctx = context or self.default_context
        return f"""
Please generate practice exercises with the following educational context:

{ctx.to_prompt_context()}

Include:
1. A mix of difficulty levels
2. Clear instructions
3. Sample solutions
4. Explanations for common mistakes
"""

    def generate_assessment_prompt(self, context: Optional[EducationalContext] = None) -> str:
        ctx = context or self.default_context
        return f"""
Please generate an assessment with the following educational context:

{ctx.to_prompt_context()}

Include:
1. A variety of question types
2. Scoring rubric
3. Learning outcome alignment
4. Difficulty level indicators
""" 
