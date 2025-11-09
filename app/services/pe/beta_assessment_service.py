"""
Beta Assessment Service
Provides assessment management for beta teachers (assessment templates, rubric building, etc.)
Independent from student-level assessment tracking.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.skill_assessment.assessment.assessment import (
    AssessmentCriteria
)
from app.models.teacher_registration import TeacherRegistration
from app.models.assessment_tools import (
    AssessmentTemplate,
    AssessmentCriteria as TemplateAssessmentCriteria,
    AssessmentRubric
)


class BetaAssessmentService:
    """Assessment service for beta teachers - focuses on templates and tools."""
    
    def __init__(self, db: Session, teacher_id: int):
        self.db = db
        self.teacher_id = teacher_id
        self.logger = __import__('logging').getLogger("beta_assessment_service")
    
    async def load_skill_benchmarks(self) -> Dict[str, Any]:
        """Load skill benchmarks for assessment template creation."""
        try:
            # Query assessment criteria from database
            criteria_list = self.db.query(AssessmentCriteria).all()
            
            # Organize criteria by skill and age group
            benchmarks = {}
            for criterion in criteria_list:
                skill_name = criterion.name.lower() if criterion.name else "unknown"
                criteria_type = criterion.criteria_type or "technical"
                
                if skill_name not in benchmarks:
                    benchmarks[skill_name] = {
                        "elementary": {},
                        "middle": {},
                        "high": {}
                    }
                
                # Parse rubric for benchmark values
                rubric = criterion.rubric if isinstance(criterion.rubric, dict) else {}
                
                age_groups = ["elementary", "middle", "high"]
                for age_group in age_groups:
                    if criteria_type not in benchmarks[skill_name][age_group]:
                        benchmarks[skill_name][age_group][criteria_type] = {
                            "min_score": criterion.min_score,
                            "max_score": criterion.max_score,
                            "weight": criterion.weight,
                            "rubric": rubric
                        }
            
            self.logger.info("Skill benchmarks loaded successfully for beta teacher")
            return benchmarks
            
        except Exception as e:
            self.logger.error(f"Error loading skill benchmarks: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading skill benchmarks: {str(e)}"
            )
    
    async def get_assessment_templates(self) -> List[Dict]:
        """Get assessment templates for this beta teacher."""
        try:
            # AssessmentTemplate uses teacher_id (UUID), not created_by
            templates = self.db.query(AssessmentTemplate).filter(
                AssessmentTemplate.teacher_id == self.teacher_id
            ).all()
            return [self._template_to_dict(t) for t in templates]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving assessment templates: {str(e)}"
            )
    
    def _template_to_dict(self, template: AssessmentTemplate) -> Dict:
        """Convert AssessmentTemplate to dictionary."""
        return {
            "id": str(template.id),
            "title": template.title,  # Field is 'title', not 'name'
            "description": template.description,
            "subject": template.subject,
            "grade_level": template.grade_level,  # Field is 'grade_level', not 'grade_levels'
            "assessment_type": template.assessment_type,
            "duration_minutes": template.duration_minutes,
            "total_points": template.total_points,
            "instructions": template.instructions,
            "materials_needed": template.materials_needed or [],
            "safety_considerations": template.safety_considerations or [],
            "ai_generated": template.ai_generated,
            "difficulty_level": template.difficulty_level,
            "equipment_required": template.equipment_required or [],
            "space_requirements": template.space_requirements,
            "weather_dependent": template.weather_dependent,
            "is_public": template.is_public,
            "usage_count": template.usage_count,
            "rating_average": float(template.rating_average) if template.rating_average else 0.0,
            "rating_count": template.rating_count,
            "teacher_id": str(template.teacher_id),  # Use teacher_id, not created_by
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        }

