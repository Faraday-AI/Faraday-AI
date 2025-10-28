"""
PE Activity Template Service for Beta Version

Handles creation, management, and sharing of PE activity templates
without requiring student data integration.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

logger = logging.getLogger(__name__)

class ActivityTemplateService:
    """Service for managing PE activity templates."""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_template(
        self,
        teacher_id: str,
        name: str,
        description: str,
        category: str,
        subcategory: str = None,
        grade_levels: List[str] = None,
        duration_minutes: int = None,
        equipment_needed: List[str] = None,
        space_requirements: str = None,
        skill_level: str = None,
        learning_objectives: List[str] = None,
        instructions: str = "",
        safety_considerations: str = None,
        modifications: str = None,
        assessment_criteria: str = None,
        tags: List[str] = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new PE activity template.
        
        Args:
            teacher_id: ID of the teacher creating the template
            name: Name of the activity
            description: Description of the activity
            category: Activity category (cardiovascular, strength, etc.)
            subcategory: Activity subcategory (running, weightlifting, etc.)
            grade_levels: List of grade levels this activity is suitable for
            duration_minutes: Duration of the activity in minutes
            equipment_needed: List of equipment required
            space_requirements: Space requirements (gym, outdoor, classroom)
            skill_level: Skill level required (beginner, intermediate, advanced)
            learning_objectives: List of learning objectives
            instructions: Detailed instructions for the activity
            safety_considerations: Safety considerations and precautions
            modifications: Modifications for different abilities
            assessment_criteria: How to assess student performance
            tags: List of tags for categorization
            is_public: Whether the template is public
            
        Returns:
            Dict containing the created template data
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate input data
            self._validate_template_data(name, description, category, instructions)
            
            # Generate template ID
            template_id = str(uuid.uuid4())
            
            # Insert template
            insert_query = text("""
                INSERT INTO activity_templates (
                    id, teacher_id, name, description, category, subcategory,
                    grade_levels, duration_minutes, equipment_needed, space_requirements,
                    skill_level, learning_objectives, instructions, safety_considerations,
                    modifications, assessment_criteria, tags, is_public
                ) VALUES (
                    :id, :teacher_id, :name, :description, :category, :subcategory,
                    :grade_levels, :duration_minutes, :equipment_needed, :space_requirements,
                    :skill_level, :learning_objectives, :instructions, :safety_considerations,
                    :modifications, :assessment_criteria, :tags, :is_public
                )
            """)
            
            self.db.execute(insert_query, {
                'id': template_id,
                'teacher_id': teacher_id,
                'name': name.strip(),
                'description': description.strip() if description else None,
                'category': category.strip(),
                'subcategory': subcategory.strip() if subcategory else None,
                'grade_levels': grade_levels or [],
                'duration_minutes': duration_minutes,
                'equipment_needed': equipment_needed or [],
                'space_requirements': space_requirements.strip() if space_requirements else None,
                'skill_level': skill_level.strip() if skill_level else None,
                'learning_objectives': learning_objectives or [],
                'instructions': instructions.strip(),
                'safety_considerations': safety_considerations.strip() if safety_considerations else None,
                'modifications': modifications.strip() if modifications else None,
                'assessment_criteria': assessment_criteria.strip() if assessment_criteria else None,
                'tags': tags or [],
                'is_public': is_public
            })
            
            self.db.commit()
            
            self.logger.info(f"Activity template created: {template_id} by teacher {teacher_id}")
            
            return {
                "success": True,
                "template_id": template_id,
                "message": "Activity template created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating activity template: {str(e)}")
            raise
    
    async def get_my_templates(
        self,
        teacher_id: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get templates created by a specific teacher.
        
        Args:
            teacher_id: ID of the teacher
            filters: Optional filters (category, grade_level, etc.)
            
        Returns:
            List of template data
        """
        try:
            # Build query with filters
            where_conditions = ["teacher_id = :teacher_id"]
            params = {"teacher_id": teacher_id}
            
            if filters:
                if filters.get("category"):
                    where_conditions.append("category = :category")
                    params["category"] = filters["category"]
                
                if filters.get("grade_level"):
                    where_conditions.append(":grade_level = ANY(grade_levels)")
                    params["grade_level"] = filters["grade_level"]
                
                if filters.get("skill_level"):
                    where_conditions.append("skill_level = :skill_level")
                    params["skill_level"] = filters["skill_level"]
                
                if filters.get("is_public") is not None:
                    where_conditions.append("is_public = :is_public")
                    params["is_public"] = filters["is_public"]
            
            query = text(f"""
                SELECT 
                    id, name, description, category, subcategory,
                    grade_levels, duration_minutes, equipment_needed, space_requirements,
                    skill_level, learning_objectives, instructions, safety_considerations,
                    modifications, assessment_criteria, tags, is_public, is_featured,
                    usage_count, rating_average, rating_count, created_at, updated_at
                FROM activity_templates
                WHERE {' AND '.join(where_conditions)}
                ORDER BY created_at DESC
            """)
            
            results = self.db.execute(query, params).fetchall()
            
            templates = []
            for row in results:
                templates.append({
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description,
                    "category": row.category,
                    "subcategory": row.subcategory,
                    "grade_levels": row.grade_levels,
                    "duration_minutes": row.duration_minutes,
                    "equipment_needed": row.equipment_needed,
                    "space_requirements": row.space_requirements,
                    "skill_level": row.skill_level,
                    "learning_objectives": row.learning_objectives,
                    "instructions": row.instructions,
                    "safety_considerations": row.safety_considerations,
                    "modifications": row.modifications,
                    "assessment_criteria": row.assessment_criteria,
                    "tags": row.tags,
                    "is_public": row.is_public,
                    "is_featured": row.is_featured,
                    "usage_count": row.usage_count,
                    "rating_average": float(row.rating_average) if row.rating_average else 0.0,
                    "rating_count": row.rating_count,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                })
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Error getting teacher templates: {str(e)}")
            raise
    
    async def get_shared_templates(
        self,
        teacher_id: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get templates shared with a specific teacher.
        
        Args:
            teacher_id: ID of the teacher
            filters: Optional filters
            
        Returns:
            List of shared template data
        """
        try:
            # Build query for shared templates
            where_conditions = [
                "ats.shared_with_teacher_id = :teacher_id",
                "ats.expires_at > NOW() OR ats.expires_at IS NULL"
            ]
            params = {"teacher_id": teacher_id}
            
            if filters:
                if filters.get("category"):
                    where_conditions.append("at.category = :category")
                    params["category"] = filters["category"]
            
            query = text(f"""
                SELECT 
                    at.id, at.name, at.description, at.category, at.subcategory,
                    at.grade_levels, at.duration_minutes, at.equipment_needed, at.space_requirements,
                    at.skill_level, at.learning_objectives, at.instructions, at.safety_considerations,
                    at.modifications, at.assessment_criteria, at.tags, at.is_public, at.is_featured,
                    at.usage_count, at.rating_average, at.rating_count, at.created_at, at.updated_at,
                    ats.permission_level, ats.shared_at
                FROM activity_templates at
                JOIN activity_template_sharing ats ON at.id = ats.template_id
                WHERE {' AND '.join(where_conditions)}
                ORDER BY ats.shared_at DESC
            """)
            
            results = self.db.execute(query, params).fetchall()
            
            templates = []
            for row in results:
                templates.append({
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description,
                    "category": row.category,
                    "subcategory": row.subcategory,
                    "grade_levels": row.grade_levels,
                    "duration_minutes": row.duration_minutes,
                    "equipment_needed": row.equipment_needed,
                    "space_requirements": row.space_requirements,
                    "skill_level": row.skill_level,
                    "learning_objectives": row.learning_objectives,
                    "instructions": row.instructions,
                    "safety_considerations": row.safety_considerations,
                    "modifications": row.modifications,
                    "assessment_criteria": row.assessment_criteria,
                    "tags": row.tags,
                    "is_public": row.is_public,
                    "is_featured": row.is_featured,
                    "usage_count": row.usage_count,
                    "rating_average": float(row.rating_average) if row.rating_average else 0.0,
                    "rating_count": row.rating_count,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "permission_level": row.permission_level,
                    "shared_at": row.shared_at.isoformat() if row.shared_at else None
                })
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Error getting shared templates: {str(e)}")
            raise
    
    async def update_template(
        self,
        template_id: str,
        teacher_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing activity template.
        
        Args:
            template_id: ID of the template to update
            teacher_id: ID of the teacher (for authorization)
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing update result
            
        Raises:
            ValueError: If template not found or unauthorized
        """
        try:
            # Check if template exists and belongs to teacher
            check_query = text("""
                SELECT id FROM activity_templates 
                WHERE id = :template_id AND teacher_id = :teacher_id
            """)
            
            result = self.db.execute(check_query, {
                'template_id': template_id,
                'teacher_id': teacher_id
            }).fetchone()
            
            if not result:
                raise ValueError("Template not found or unauthorized")
            
            # Build update query
            update_fields = []
            params = {'template_id': template_id, 'teacher_id': teacher_id}
            
            for field, value in updates.items():
                if field in ['name', 'description', 'category', 'subcategory', 
                           'space_requirements', 'skill_level', 'instructions',
                           'safety_considerations', 'modifications', 'assessment_criteria']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value.strip() if isinstance(value, str) else value
                elif field in ['grade_levels', 'equipment_needed', 'learning_objectives', 'tags']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value or []
                elif field in ['duration_minutes', 'usage_count', 'rating_count']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
                elif field in ['is_public', 'is_featured']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = bool(value)
                elif field == 'rating_average':
                    update_fields.append(f"{field} = :{field}")
                    params[field] = float(value) if value else 0.0
            
            if not update_fields:
                return {"success": True, "message": "No updates provided"}
            
            update_fields.append("updated_at = NOW()")
            
            update_query = text(f"""
                UPDATE activity_templates 
                SET {', '.join(update_fields)}
                WHERE id = :template_id AND teacher_id = :teacher_id
            """)
            
            self.db.execute(update_query, params)
            self.db.commit()
            
            self.logger.info(f"Activity template updated: {template_id}")
            
            return {
                "success": True,
                "message": "Template updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating template {template_id}: {str(e)}")
            raise
    
    async def delete_template(
        self,
        template_id: str,
        teacher_id: str
    ) -> bool:
        """
        Delete an activity template.
        
        Args:
            template_id: ID of the template to delete
            teacher_id: ID of the teacher (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Check if template exists and belongs to teacher
            check_query = text("""
                SELECT id FROM activity_templates 
                WHERE id = :template_id AND teacher_id = :teacher_id
            """)
            
            result = self.db.execute(check_query, {
                'template_id': template_id,
                'teacher_id': teacher_id
            }).fetchone()
            
            if not result:
                return False
            
            # Delete template (cascade will handle related records)
            delete_query = text("""
                DELETE FROM activity_templates 
                WHERE id = :template_id AND teacher_id = :teacher_id
            """)
            
            self.db.execute(delete_query, {
                'template_id': template_id,
                'teacher_id': teacher_id
            })
            self.db.commit()
            
            self.logger.info(f"Activity template deleted: {template_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting template {template_id}: {str(e)}")
            return False
    
    async def duplicate_template(
        self,
        template_id: str,
        teacher_id: str,
        new_name: str = None
    ) -> Dict[str, Any]:
        """
        Duplicate an existing template.
        
        Args:
            template_id: ID of the template to duplicate
            teacher_id: ID of the teacher creating the duplicate
            new_name: Optional new name for the duplicate
            
        Returns:
            Dict containing the new template data
        """
        try:
            # Get original template
            get_query = text("""
                SELECT * FROM activity_templates WHERE id = :template_id
            """)
            
            result = self.db.execute(get_query, {'template_id': template_id}).fetchone()
            
            if not result:
                raise ValueError("Template not found")
            
            # Create duplicate
            new_template_id = str(uuid.uuid4())
            duplicate_name = new_name or f"{result.name} (Copy)"
            
            insert_query = text("""
                INSERT INTO activity_templates (
                    id, teacher_id, name, description, category, subcategory,
                    grade_levels, duration_minutes, equipment_needed, space_requirements,
                    skill_level, learning_objectives, instructions, safety_considerations,
                    modifications, assessment_criteria, tags, is_public
                ) VALUES (
                    :id, :teacher_id, :name, :description, :category, :subcategory,
                    :grade_levels, :duration_minutes, :equipment_needed, :space_requirements,
                    :skill_level, :learning_objectives, :instructions, :safety_considerations,
                    :modifications, :assessment_criteria, :tags, FALSE
                )
            """)
            
            self.db.execute(insert_query, {
                'id': new_template_id,
                'teacher_id': teacher_id,
                'name': duplicate_name,
                'description': result.description,
                'category': result.category,
                'subcategory': result.subcategory,
                'grade_levels': result.grade_levels,
                'duration_minutes': result.duration_minutes,
                'equipment_needed': result.equipment_needed,
                'space_requirements': result.space_requirements,
                'skill_level': result.skill_level,
                'learning_objectives': result.learning_objectives,
                'instructions': result.instructions,
                'safety_considerations': result.safety_considerations,
                'modifications': result.modifications,
                'assessment_criteria': result.assessment_criteria,
                'tags': result.tags
            })
            
            # Track usage
            await self._track_template_usage(template_id, teacher_id, "duplicated")
            
            self.db.commit()
            
            self.logger.info(f"Template duplicated: {template_id} -> {new_template_id}")
            
            return {
                "success": True,
                "template_id": new_template_id,
                "message": "Template duplicated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error duplicating template {template_id}: {str(e)}")
            raise
    
    async def _track_template_usage(
        self,
        template_id: str,
        teacher_id: str,
        usage_type: str,
        notes: str = None
    ):
        """Track template usage for analytics."""
        try:
            insert_query = text("""
                INSERT INTO activity_template_usage (template_id, teacher_id, usage_type, notes)
                VALUES (:template_id, :teacher_id, :usage_type, :notes)
            """)
            
            self.db.execute(insert_query, {
                'template_id': template_id,
                'teacher_id': teacher_id,
                'usage_type': usage_type,
                'notes': notes
            })
            
        except Exception as e:
            self.logger.warning(f"Error tracking template usage: {str(e)}")
    
    def _validate_template_data(self, name: str, description: str, category: str, instructions: str):
        """Validate template input data."""
        if not name or len(name.strip()) < 3:
            raise ValueError("Activity name must be at least 3 characters long")
        
        if not category or len(category.strip()) < 2:
            raise ValueError("Activity category is required")
        
        if not instructions or len(instructions.strip()) < 10:
            raise ValueError("Instructions must be at least 10 characters long")
        
        if description and len(description.strip()) < 5:
            raise ValueError("Description must be at least 5 characters long")
