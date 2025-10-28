"""
Teacher Lesson Plan Service for Beta Version

Handles creation, management, and AI enhancement of lesson plans
for individual teachers without student data integration.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

logger = logging.getLogger(__name__)

class TeacherLessonPlanService:
    """Service for managing teacher lesson plans."""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_lesson_plan(
        self,
        teacher_id: str,
        title: str,
        description: str = None,
        grade_level: str = None,
        duration_minutes: int = None,
        subject_area: str = "PE",
        learning_objectives: List[str] = None,
        materials_needed: List[str] = None,
        equipment_needed: List[str] = None,
        space_requirements: str = None,
        warm_up_activities: List[str] = None,
        main_activities: List[str] = None,
        cool_down_activities: List[str] = None,
        assessment_methods: List[str] = None,
        modifications: str = None,
        safety_considerations: str = None,
        standards_alignment: List[str] = None,
        tags: List[str] = None,
        is_template: bool = False,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new lesson plan.
        
        Args:
            teacher_id: ID of the teacher creating the lesson plan
            title: Title of the lesson plan
            description: Description of the lesson plan
            grade_level: Grade level for the lesson
            duration_minutes: Duration in minutes
            subject_area: Subject area (PE, Health, etc.)
            learning_objectives: List of learning objectives
            materials_needed: List of materials needed
            equipment_needed: List of equipment needed
            space_requirements: Space requirements
            warm_up_activities: List of warm-up activities
            main_activities: List of main activities
            cool_down_activities: List of cool-down activities
            assessment_methods: List of assessment methods
            modifications: Modifications for different abilities
            safety_considerations: Safety considerations
            standards_alignment: List of standards aligned to
            tags: List of tags for categorization
            is_template: Whether this is a template
            is_public: Whether the lesson plan is public
            
        Returns:
            Dict containing the created lesson plan data
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate input data
            self._validate_lesson_plan_data(title, learning_objectives, main_activities)
            
            # Generate lesson plan ID
            lesson_plan_id = str(uuid.uuid4())
            
            # Insert lesson plan
            insert_query = text("""
                INSERT INTO teacher_lesson_plans (
                    id, teacher_id, title, description, grade_level, duration_minutes,
                    subject_area, learning_objectives, materials_needed, equipment_needed,
                    space_requirements, warm_up_activities, main_activities, cool_down_activities,
                    assessment_methods, modifications, safety_considerations, standards_alignment,
                    tags, is_template, is_public
                ) VALUES (
                    :id, :teacher_id, :title, :description, :grade_level, :duration_minutes,
                    :subject_area, :learning_objectives, :materials_needed, :equipment_needed,
                    :space_requirements, :warm_up_activities, :main_activities, :cool_down_activities,
                    :assessment_methods, :modifications, :safety_considerations, :standards_alignment,
                    :tags, :is_template, :is_public
                )
            """)
            
            self.db.execute(insert_query, {
                'id': lesson_plan_id,
                'teacher_id': teacher_id,
                'title': title.strip(),
                'description': description.strip() if description else None,
                'grade_level': grade_level.strip() if grade_level else None,
                'duration_minutes': duration_minutes,
                'subject_area': subject_area.strip(),
                'learning_objectives': learning_objectives or [],
                'materials_needed': materials_needed or [],
                'equipment_needed': equipment_needed or [],
                'space_requirements': space_requirements.strip() if space_requirements else None,
                'warm_up_activities': warm_up_activities or [],
                'main_activities': main_activities or [],
                'cool_down_activities': cool_down_activities or [],
                'assessment_methods': assessment_methods or [],
                'modifications': modifications.strip() if modifications else None,
                'safety_considerations': safety_considerations.strip() if safety_considerations else None,
                'standards_alignment': standards_alignment or [],
                'tags': tags or [],
                'is_template': is_template,
                'is_public': is_public
            })
            
            self.db.commit()
            
            self.logger.info(f"Lesson plan created: {lesson_plan_id} by teacher {teacher_id}")
            
            return {
                "success": True,
                "lesson_plan_id": lesson_plan_id,
                "message": "Lesson plan created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating lesson plan: {str(e)}")
            raise
    
    async def get_my_lesson_plans(
        self,
        teacher_id: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get lesson plans created by a specific teacher.
        
        Args:
            teacher_id: ID of the teacher
            filters: Optional filters (grade_level, subject_area, etc.)
            
        Returns:
            List of lesson plan data
        """
        try:
            # Build query with filters
            where_conditions = ["teacher_id = :teacher_id"]
            params = {"teacher_id": teacher_id}
            
            if filters:
                if filters.get("grade_level"):
                    where_conditions.append("grade_level = :grade_level")
                    params["grade_level"] = filters["grade_level"]
                
                if filters.get("subject_area"):
                    where_conditions.append("subject_area = :subject_area")
                    params["subject_area"] = filters["subject_area"]
                
                if filters.get("is_template") is not None:
                    where_conditions.append("is_template = :is_template")
                    params["is_template"] = filters["is_template"]
                
                if filters.get("is_public") is not None:
                    where_conditions.append("is_public = :is_public")
                    params["is_public"] = filters["is_public"]
            
            query = text(f"""
                SELECT 
                    id, title, description, grade_level, duration_minutes, subject_area,
                    learning_objectives, materials_needed, equipment_needed, space_requirements,
                    warm_up_activities, main_activities, cool_down_activities, assessment_methods,
                    modifications, safety_considerations, standards_alignment, tags,
                    is_template, is_public, usage_count, rating_average, rating_count,
                    created_at, updated_at
                FROM teacher_lesson_plans
                WHERE {' AND '.join(where_conditions)}
                ORDER BY created_at DESC
            """)
            
            results = self.db.execute(query, params).fetchall()
            
            lesson_plans = []
            for row in results:
                lesson_plans.append({
                    "id": str(row.id),
                    "title": row.title,
                    "description": row.description,
                    "grade_level": row.grade_level,
                    "duration_minutes": row.duration_minutes,
                    "subject_area": row.subject_area,
                    "learning_objectives": row.learning_objectives,
                    "materials_needed": row.materials_needed,
                    "equipment_needed": row.equipment_needed,
                    "space_requirements": row.space_requirements,
                    "warm_up_activities": row.warm_up_activities,
                    "main_activities": row.main_activities,
                    "cool_down_activities": row.cool_down_activities,
                    "assessment_methods": row.assessment_methods,
                    "modifications": row.modifications,
                    "safety_considerations": row.safety_considerations,
                    "standards_alignment": row.standards_alignment,
                    "tags": row.tags,
                    "is_template": row.is_template,
                    "is_public": row.is_public,
                    "usage_count": row.usage_count,
                    "rating_average": float(row.rating_average) if row.rating_average else 0.0,
                    "rating_count": row.rating_count,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                })
            
            return lesson_plans
            
        except Exception as e:
            self.logger.error(f"Error getting teacher lesson plans: {str(e)}")
            raise
    
    async def get_lesson_plan_by_id(
        self,
        lesson_plan_id: str,
        teacher_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific lesson plan by ID.
        
        Args:
            lesson_plan_id: ID of the lesson plan
            teacher_id: Optional teacher ID for authorization
            
        Returns:
            Lesson plan data if found, None otherwise
        """
        try:
            # Build query
            where_conditions = ["id = :lesson_plan_id"]
            params = {"lesson_plan_id": lesson_plan_id}
            
            if teacher_id:
                where_conditions.append("teacher_id = :teacher_id")
                params["teacher_id"] = teacher_id
            
            query = text(f"""
                SELECT 
                    id, title, description, grade_level, duration_minutes, subject_area,
                    learning_objectives, materials_needed, equipment_needed, space_requirements,
                    warm_up_activities, main_activities, cool_down_activities, assessment_methods,
                    modifications, safety_considerations, standards_alignment, tags,
                    is_template, is_public, usage_count, rating_average, rating_count,
                    created_at, updated_at
                FROM teacher_lesson_plans
                WHERE {' AND '.join(where_conditions)}
            """)
            
            result = self.db.execute(query, params).fetchone()
            
            if not result:
                return None
            
            return {
                "id": str(result.id),
                "title": result.title,
                "description": result.description,
                "grade_level": result.grade_level,
                "duration_minutes": result.duration_minutes,
                "subject_area": result.subject_area,
                "learning_objectives": result.learning_objectives,
                "materials_needed": result.materials_needed,
                "equipment_needed": result.equipment_needed,
                "space_requirements": result.space_requirements,
                "warm_up_activities": result.warm_up_activities,
                "main_activities": result.main_activities,
                "cool_down_activities": result.cool_down_activities,
                "assessment_methods": result.assessment_methods,
                "modifications": result.modifications,
                "safety_considerations": result.safety_considerations,
                "standards_alignment": result.standards_alignment,
                "tags": result.tags,
                "is_template": result.is_template,
                "is_public": result.is_public,
                "usage_count": result.usage_count,
                "rating_average": float(result.rating_average) if result.rating_average else 0.0,
                "rating_count": result.rating_count,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting lesson plan {lesson_plan_id}: {str(e)}")
            raise
    
    async def update_lesson_plan(
        self,
        lesson_plan_id: str,
        teacher_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing lesson plan.
        
        Args:
            lesson_plan_id: ID of the lesson plan to update
            teacher_id: ID of the teacher (for authorization)
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing update result
            
        Raises:
            ValueError: If lesson plan not found or unauthorized
        """
        try:
            # Check if lesson plan exists and belongs to teacher
            check_query = text("""
                SELECT id FROM teacher_lesson_plans 
                WHERE id = :lesson_plan_id AND teacher_id = :teacher_id
            """)
            
            result = self.db.execute(check_query, {
                'lesson_plan_id': lesson_plan_id,
                'teacher_id': teacher_id
            }).fetchone()
            
            if not result:
                raise ValueError("Lesson plan not found or unauthorized")
            
            # Build update query
            update_fields = []
            params = {'lesson_plan_id': lesson_plan_id, 'teacher_id': teacher_id}
            
            for field, value in updates.items():
                if field in ['title', 'description', 'grade_level', 'subject_area', 
                           'space_requirements', 'modifications', 'safety_considerations']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value.strip() if isinstance(value, str) else value
                elif field in ['learning_objectives', 'materials_needed', 'equipment_needed',
                              'warm_up_activities', 'main_activities', 'cool_down_activities',
                              'assessment_methods', 'standards_alignment', 'tags']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value or []
                elif field in ['duration_minutes', 'usage_count', 'rating_count']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
                elif field in ['is_template', 'is_public']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = bool(value)
                elif field == 'rating_average':
                    update_fields.append(f"{field} = :{field}")
                    params[field] = float(value) if value else 0.0
            
            if not update_fields:
                return {"success": True, "message": "No updates provided"}
            
            update_fields.append("updated_at = NOW()")
            
            update_query = text(f"""
                UPDATE teacher_lesson_plans 
                SET {', '.join(update_fields)}
                WHERE id = :lesson_plan_id AND teacher_id = :teacher_id
            """)
            
            self.db.execute(update_query, params)
            self.db.commit()
            
            self.logger.info(f"Lesson plan updated: {lesson_plan_id}")
            
            return {
                "success": True,
                "message": "Lesson plan updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating lesson plan {lesson_plan_id}: {str(e)}")
            raise
    
    async def delete_lesson_plan(
        self,
        lesson_plan_id: str,
        teacher_id: str
    ) -> bool:
        """
        Delete a lesson plan.
        
        Args:
            lesson_plan_id: ID of the lesson plan to delete
            teacher_id: ID of the teacher (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Check if lesson plan exists and belongs to teacher
            check_query = text("""
                SELECT id FROM teacher_lesson_plans 
                WHERE id = :lesson_plan_id AND teacher_id = :teacher_id
            """)
            
            result = self.db.execute(check_query, {
                'lesson_plan_id': lesson_plan_id,
                'teacher_id': teacher_id
            }).fetchone()
            
            if not result:
                return False
            
            # Delete lesson plan (cascade will handle related records)
            delete_query = text("""
                DELETE FROM teacher_lesson_plans 
                WHERE id = :lesson_plan_id AND teacher_id = :teacher_id
            """)
            
            self.db.execute(delete_query, {
                'lesson_plan_id': lesson_plan_id,
                'teacher_id': teacher_id
            })
            self.db.commit()
            
            self.logger.info(f"Lesson plan deleted: {lesson_plan_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting lesson plan {lesson_plan_id}: {str(e)}")
            return False
    
    async def duplicate_lesson_plan(
        self,
        lesson_plan_id: str,
        teacher_id: str,
        new_title: str = None
    ) -> Dict[str, Any]:
        """
        Duplicate an existing lesson plan.
        
        Args:
            lesson_plan_id: ID of the lesson plan to duplicate
            teacher_id: ID of the teacher creating the duplicate
            new_title: Optional new title for the duplicate
            
        Returns:
            Dict containing the new lesson plan data
        """
        try:
            # Get original lesson plan
            original = await self.get_lesson_plan_by_id(lesson_plan_id)
            
            if not original:
                raise ValueError("Lesson plan not found")
            
            # Create duplicate
            duplicate_title = new_title or f"{original['title']} (Copy)"
            
            # Create new lesson plan with same data
            result = await self.create_lesson_plan(
                teacher_id=teacher_id,
                title=duplicate_title,
                description=original['description'],
                grade_level=original['grade_level'],
                duration_minutes=original['duration_minutes'],
                subject_area=original['subject_area'],
                learning_objectives=original['learning_objectives'],
                materials_needed=original['materials_needed'],
                equipment_needed=original['equipment_needed'],
                space_requirements=original['space_requirements'],
                warm_up_activities=original['warm_up_activities'],
                main_activities=original['main_activities'],
                cool_down_activities=original['cool_down_activities'],
                assessment_methods=original['assessment_methods'],
                modifications=original['modifications'],
                safety_considerations=original['safety_considerations'],
                standards_alignment=original['standards_alignment'],
                tags=original['tags'],
                is_template=False,  # Duplicates are not templates by default
                is_public=False     # Duplicates are private by default
            )
            
            # Track usage
            await self._track_lesson_plan_usage(lesson_plan_id, teacher_id, "duplicated")
            
            self.logger.info(f"Lesson plan duplicated: {lesson_plan_id} -> {result['lesson_plan_id']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error duplicating lesson plan {lesson_plan_id}: {str(e)}")
            raise
    
    async def generate_ai_lesson_plan(
        self,
        teacher_id: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a lesson plan using AI assistance.
        
        Args:
            teacher_id: ID of the teacher
            requirements: Lesson plan requirements
            
        Returns:
            Dict containing the generated lesson plan data
        """
        try:
            # This would integrate with your AI service
            # For now, return a placeholder response
            return {
                "success": True,
                "message": "AI lesson plan generation not yet implemented",
                "lesson_plan_id": None
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI lesson plan: {str(e)}")
            raise
    
    async def _track_lesson_plan_usage(
        self,
        lesson_plan_id: str,
        teacher_id: str,
        usage_type: str,
        notes: str = None
    ):
        """Track lesson plan usage for analytics."""
        try:
            insert_query = text("""
                INSERT INTO teacher_lesson_plan_usage (lesson_plan_id, teacher_id, usage_type, notes)
                VALUES (:lesson_plan_id, :teacher_id, :usage_type, :notes)
            """)
            
            self.db.execute(insert_query, {
                'lesson_plan_id': lesson_plan_id,
                'teacher_id': teacher_id,
                'usage_type': usage_type,
                'notes': notes
            })
            
        except Exception as e:
            self.logger.warning(f"Error tracking lesson plan usage: {str(e)}")
    
    def _validate_lesson_plan_data(self, title: str, learning_objectives: List[str], main_activities: List[str]):
        """Validate lesson plan input data."""
        if not title or len(title.strip()) < 3:
            raise ValueError("Lesson plan title must be at least 3 characters long")
        
        if not learning_objectives or len(learning_objectives) == 0:
            raise ValueError("At least one learning objective is required")
        
        if not main_activities or len(main_activities) == 0:
            raise ValueError("At least one main activity is required")
