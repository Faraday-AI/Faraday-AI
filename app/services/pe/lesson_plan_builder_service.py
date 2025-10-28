"""
Lesson Plan Builder Service
Handles AI-assisted lesson plan creation, management, and sharing for beta teachers
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
import uuid
import json

from app.models.lesson_plan_builder import (
    LessonPlanTemplate,
    LessonPlanActivity,
    AILessonSuggestion,
    LessonPlanSharing,
    LessonPlanUsage,
    LessonPlanCategory,
    TemplateCategoryAssociation
)
from app.schemas.lesson_plan_builder import (
    LessonPlanTemplateCreate,
    LessonPlanTemplateUpdate,
    LessonPlanTemplateResponse,
    LessonPlanActivityCreate,
    LessonPlanActivityResponse,
    AISuggestionCreate,
    AISuggestionResponse,
    LessonPlanSharingCreate,
    LessonPlanSharingResponse,
    LessonPlanUsageCreate,
    LessonPlanUsageResponse,
    LessonPlanCategoryResponse
)


class LessonPlanBuilderService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== TEMPLATE MANAGEMENT ====================
    
    def create_template(
        self, 
        teacher_id: str, 
        template_data: LessonPlanTemplateCreate
    ) -> LessonPlanTemplateResponse:
        """Create a new lesson plan template"""
        try:
            # Create the template
            template = LessonPlanTemplate(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                title=template_data.title,
                description=template_data.description,
                subject=template_data.subject,
                grade_level=template_data.grade_level,
                duration_minutes=template_data.duration_minutes,
                learning_objectives=template_data.learning_objectives,
                materials_needed=template_data.materials_needed,
                safety_considerations=template_data.safety_considerations,
                assessment_methods=template_data.assessment_methods,
                ai_generated=template_data.ai_generated,
                template_type=template_data.template_type,
                difficulty_level=template_data.difficulty_level,
                equipment_required=template_data.equipment_required,
                space_requirements=template_data.space_requirements,
                weather_dependent=template_data.weather_dependent,
                is_public=template_data.is_public
            )
            
            self.db.add(template)
            self.db.flush()  # Get the ID
            
            # Add activities if provided
            if template_data.activities:
                for i, activity_data in enumerate(template_data.activities):
                    activity = LessonPlanActivity(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        activity_name=activity_data.activity_name,
                        activity_description=activity_data.activity_description,
                        duration_minutes=activity_data.duration_minutes,
                        activity_type=activity_data.activity_type,
                        equipment_needed=activity_data.equipment_needed,
                        space_required=activity_data.space_required,
                        safety_notes=activity_data.safety_notes,
                        instructions=activity_data.instructions,
                        modifications=activity_data.modifications,
                        success_criteria=activity_data.success_criteria,
                        order_index=i + 1
                    )
                    self.db.add(activity)
            
            # Add category associations if provided
            if template_data.category_ids:
                for category_id in template_data.category_ids:
                    association = TemplateCategoryAssociation(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        category_id=category_id
                    )
                    self.db.add(association)
            
            self.db.commit()
            
            # Log usage
            self._log_template_usage(
                template_id=template.id,
                teacher_id=teacher_id,
                usage_type="created"
            )
            
            return self._template_to_response(template)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create template: {str(e)}")

    def get_template(self, template_id: str, teacher_id: str) -> Optional[LessonPlanTemplateResponse]:
        """Get a specific template by ID"""
        template = self.db.query(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.id == template_id,
                or_(
                    LessonPlanTemplate.teacher_id == teacher_id,
                    LessonPlanTemplate.is_public == True
                )
            )
        ).first()
        
        if not template:
            return None
            
        return self._template_to_response(template)

    def get_teacher_templates(
        self, 
        teacher_id: str, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LessonPlanTemplateResponse]:
        """Get templates created by a specific teacher"""
        query = self.db.query(LessonPlanTemplate).filter(
            LessonPlanTemplate.teacher_id == teacher_id
        )
        
        if subject:
            query = query.filter(LessonPlanTemplate.subject == subject)
        if grade_level:
            query = query.filter(LessonPlanTemplate.grade_level == grade_level)
        if template_type:
            query = query.filter(LessonPlanTemplate.template_type == template_type)
        
        templates = query.order_by(desc(LessonPlanTemplate.created_at)).offset(offset).limit(limit).all()
        
        return [self._template_to_response(template) for template in templates]

    def get_public_templates(
        self,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        template_type: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LessonPlanTemplateResponse]:
        """Get public templates available to all teachers"""
        query = self.db.query(LessonPlanTemplate).filter(
            LessonPlanTemplate.is_public == True
        )
        
        if subject:
            query = query.filter(LessonPlanTemplate.subject == subject)
        if grade_level:
            query = query.filter(LessonPlanTemplate.grade_level == grade_level)
        if template_type:
            query = query.filter(LessonPlanTemplate.template_type == template_type)
        if difficulty_level:
            query = query.filter(LessonPlanTemplate.difficulty_level == difficulty_level)
        
        templates = query.order_by(desc(LessonPlanTemplate.rating_average)).offset(offset).limit(limit).all()
        
        return [self._template_to_response(template) for template in templates]

    def update_template(
        self, 
        template_id: str, 
        teacher_id: str, 
        update_data: LessonPlanTemplateUpdate
    ) -> Optional[LessonPlanTemplateResponse]:
        """Update an existing template"""
        template = self.db.query(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.id == template_id,
                LessonPlanTemplate.teacher_id == teacher_id
            )
        ).first()
        
        if not template:
            return None
        
        # Update template fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != "activities" and field != "category_ids":
                setattr(template, field, value)
        
        # Update activities if provided
        if update_data.activities is not None:
            # Delete existing activities
            self.db.query(LessonPlanActivity).filter(
                LessonPlanActivity.template_id == template_id
            ).delete()
            
            # Add new activities
            for i, activity_data in enumerate(update_data.activities):
                activity = LessonPlanActivity(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    activity_name=activity_data.activity_name,
                    activity_description=activity_data.activity_description,
                    duration_minutes=activity_data.duration_minutes,
                    activity_type=activity_data.activity_type,
                    equipment_needed=activity_data.equipment_needed,
                    space_required=activity_data.space_required,
                    safety_notes=activity_data.safety_notes,
                    instructions=activity_data.instructions,
                    modifications=activity_data.modifications,
                    success_criteria=activity_data.success_criteria,
                    order_index=i + 1
                )
                self.db.add(activity)
        
        # Update category associations if provided
        if update_data.category_ids is not None:
            # Delete existing associations
            self.db.query(TemplateCategoryAssociation).filter(
                TemplateCategoryAssociation.template_id == template_id
            ).delete()
            
            # Add new associations
            for category_id in update_data.category_ids:
                association = TemplateCategoryAssociation(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    category_id=category_id
                )
                self.db.add(association)
        
        template.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Log usage
        self._log_template_usage(
            template_id=template_id,
            teacher_id=teacher_id,
            usage_type="modified"
        )
        
        return self._template_to_response(template)

    def delete_template(self, template_id: str, teacher_id: str) -> bool:
        """Delete a template"""
        template = self.db.query(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.id == template_id,
                LessonPlanTemplate.teacher_id == teacher_id
            )
        ).first()
        
        if not template:
            return False
        
        self.db.delete(template)
        self.db.commit()
        
        return True

    def duplicate_template(self, template_id: str, teacher_id: str) -> Optional[LessonPlanTemplateResponse]:
        """Duplicate an existing template"""
        original_template = self.db.query(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.id == template_id,
                or_(
                    LessonPlanTemplate.teacher_id == teacher_id,
                    LessonPlanTemplate.is_public == True
                )
            )
        ).first()
        
        if not original_template:
            return None
        
        # Create new template
        new_template = LessonPlanTemplate(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            title=f"{original_template.title} (Copy)",
            description=original_template.description,
            subject=original_template.subject,
            grade_level=original_template.grade_level,
            duration_minutes=original_template.duration_minutes,
            learning_objectives=original_template.learning_objectives,
            materials_needed=original_template.materials_needed,
            safety_considerations=original_template.safety_considerations,
            assessment_methods=original_template.assessment_methods,
            ai_generated=False,  # Mark as not AI-generated since it's a copy
            template_type=original_template.template_type,
            difficulty_level=original_template.difficulty_level,
            equipment_required=original_template.equipment_required,
            space_requirements=original_template.space_requirements,
            weather_dependent=original_template.weather_dependent,
            is_public=False  # Private by default
        )
        
        self.db.add(new_template)
        self.db.flush()
        
        # Copy activities
        original_activities = self.db.query(LessonPlanActivity).filter(
            LessonPlanActivity.template_id == template_id
        ).order_by(LessonPlanActivity.order_index).all()
        
        for activity in original_activities:
            new_activity = LessonPlanActivity(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                activity_name=activity.activity_name,
                activity_description=activity.activity_description,
                duration_minutes=activity.duration_minutes,
                activity_type=activity.activity_type,
                equipment_needed=activity.equipment_needed,
                space_required=activity.space_required,
                safety_notes=activity.safety_notes,
                instructions=activity.instructions,
                modifications=activity.modifications,
                success_criteria=activity.success_criteria,
                order_index=activity.order_index
            )
            self.db.add(new_activity)
        
        # Copy category associations
        original_associations = self.db.query(TemplateCategoryAssociation).filter(
            TemplateCategoryAssociation.template_id == template_id
        ).all()
        
        for association in original_associations:
            new_association = TemplateCategoryAssociation(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                category_id=association.category_id
            )
            self.db.add(new_association)
        
        self.db.commit()
        
        # Log usage
        self._log_template_usage(
            template_id=new_template.id,
            teacher_id=teacher_id,
            usage_type="copied"
        )
        
        return self._template_to_response(new_template)

    # ==================== AI SUGGESTIONS ====================
    
    def create_ai_suggestion(
        self, 
        teacher_id: str, 
        suggestion_data: AISuggestionCreate
    ) -> AISuggestionResponse:
        """Create an AI-generated lesson plan suggestion"""
        suggestion = AILessonSuggestion(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            suggestion_type=suggestion_data.suggestion_type,
            subject=suggestion_data.subject,
            grade_level=suggestion_data.grade_level,
            context=suggestion_data.context,
            ai_suggestion=suggestion_data.ai_suggestion,
            confidence_score=suggestion_data.confidence_score,
            tags=suggestion_data.tags
        )
        
        self.db.add(suggestion)
        self.db.commit()
        
        return self._suggestion_to_response(suggestion)

    def get_ai_suggestions(
        self, 
        teacher_id: str, 
        suggestion_type: Optional[str] = None,
        subject: Optional[str] = None,
        applied_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[AISuggestionResponse]:
        """Get AI suggestions for a teacher"""
        query = self.db.query(AILessonSuggestion).filter(
            AILessonSuggestion.teacher_id == teacher_id
        )
        
        if suggestion_type:
            query = query.filter(AILessonSuggestion.suggestion_type == suggestion_type)
        if subject:
            query = query.filter(AILessonSuggestion.subject == subject)
        if applied_only:
            query = query.filter(AILessonSuggestion.is_applied == True)
        
        suggestions = query.order_by(desc(AILessonSuggestion.created_at)).offset(offset).limit(limit).all()
        
        return [self._suggestion_to_response(suggestion) for suggestion in suggestions]

    def apply_ai_suggestion(self, suggestion_id: str, teacher_id: str) -> bool:
        """Mark an AI suggestion as applied"""
        suggestion = self.db.query(AILessonSuggestion).filter(
            and_(
                AILessonSuggestion.id == suggestion_id,
                AILessonSuggestion.teacher_id == teacher_id
            )
        ).first()
        
        if not suggestion:
            return False
        
        suggestion.is_applied = True
        suggestion.applied_at = datetime.utcnow()
        self.db.commit()
        
        return True

    def rate_ai_suggestion(
        self, 
        suggestion_id: str, 
        teacher_id: str, 
        rating: int, 
        comment: Optional[str] = None
    ) -> bool:
        """Rate an AI suggestion"""
        suggestion = self.db.query(AILessonSuggestion).filter(
            and_(
                AILessonSuggestion.id == suggestion_id,
                AILessonSuggestion.teacher_id == teacher_id
            )
        ).first()
        
        if not suggestion or rating < 1 or rating > 5:
            return False
        
        suggestion.feedback_rating = rating
        suggestion.feedback_comment = comment
        self.db.commit()
        
        return True

    # ==================== SHARING ====================
    
    def share_template(
        self, 
        template_id: str, 
        teacher_id: str, 
        sharing_data: LessonPlanSharingCreate
    ) -> LessonPlanSharingResponse:
        """Share a template with other teachers"""
        # Verify template ownership
        template = self.db.query(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.id == template_id,
                LessonPlanTemplate.teacher_id == teacher_id
            )
        ).first()
        
        if not template:
            raise Exception("Template not found or access denied")
        
        sharing = LessonPlanSharing(
            id=str(uuid.uuid4()),
            template_id=template_id,
            shared_by_teacher_id=teacher_id,
            shared_with_teacher_id=sharing_data.shared_with_teacher_id,
            sharing_type=sharing_data.sharing_type,
            access_level=sharing_data.access_level,
            expires_at=sharing_data.expires_at
        )
        
        self.db.add(sharing)
        self.db.commit()
        
        return self._sharing_to_response(sharing)

    def get_shared_templates(
        self, 
        teacher_id: str, 
        sharing_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LessonPlanTemplateResponse]:
        """Get templates shared with a teacher"""
        query = self.db.query(LessonPlanTemplate).join(LessonPlanSharing).filter(
            and_(
                LessonPlanSharing.shared_with_teacher_id == teacher_id,
                LessonPlanSharing.is_active == True,
                or_(
                    LessonPlanSharing.expires_at.is_(None),
                    LessonPlanSharing.expires_at > datetime.utcnow()
                )
            )
        )
        
        if sharing_type:
            query = query.filter(LessonPlanSharing.sharing_type == sharing_type)
        
        templates = query.order_by(desc(LessonPlanSharing.shared_at)).offset(offset).limit(limit).all()
        
        return [self._template_to_response(template) for template in templates]

    # ==================== CATEGORIES ====================
    
    def get_categories(
        self, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> List[LessonPlanCategoryResponse]:
        """Get lesson plan categories"""
        query = self.db.query(LessonPlanCategory).filter(
            LessonPlanCategory.is_active == True
        )
        
        if subject:
            query = query.filter(LessonPlanCategory.subject == subject)
        if grade_level:
            query = query.filter(LessonPlanCategory.grade_level_range.contains(grade_level))
        
        categories = query.order_by(asc(LessonPlanCategory.name)).all()
        
        return [self._category_to_response(category) for category in categories]

    # ==================== ANALYTICS ====================
    
    def get_template_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a teacher's templates"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Template creation stats
        templates_created = self.db.query(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.teacher_id == teacher_id,
                LessonPlanTemplate.created_at >= start_date
            )
        ).count()
        
        # Usage stats
        usage_stats = self.db.query(
            LessonPlanUsage.usage_type,
            func.count(LessonPlanUsage.id).label('count')
        ).join(LessonPlanTemplate).filter(
            and_(
                LessonPlanTemplate.teacher_id == teacher_id,
                LessonPlanUsage.usage_date >= start_date
            )
        ).group_by(LessonPlanUsage.usage_type).all()
        
        # Popular templates
        popular_templates = self.db.query(
            LessonPlanTemplate.id,
            LessonPlanTemplate.title,
            func.count(LessonPlanUsage.id).label('usage_count')
        ).join(LessonPlanUsage).filter(
            LessonPlanTemplate.teacher_id == teacher_id
        ).group_by(
            LessonPlanTemplate.id, 
            LessonPlanTemplate.title
        ).order_by(desc('usage_count')).limit(5).all()
        
        return {
            "templates_created": templates_created,
            "usage_by_type": {stat.usage_type: stat.count for stat in usage_stats},
            "popular_templates": [
                {
                    "id": template.id,
                    "title": template.title,
                    "usage_count": template.usage_count
                }
                for template in popular_templates
            ]
        }

    # ==================== HELPER METHODS ====================
    
    def _log_template_usage(
        self, 
        template_id: str, 
        teacher_id: str, 
        usage_type: str
    ) -> None:
        """Log template usage for analytics"""
        usage = LessonPlanUsage(
            id=str(uuid.uuid4()),
            template_id=template_id,
            teacher_id=teacher_id,
            usage_type=usage_type
        )
        self.db.add(usage)
        self.db.commit()

    def _template_to_response(self, template: LessonPlanTemplate) -> LessonPlanTemplateResponse:
        """Convert template model to response"""
        # Get activities
        activities = self.db.query(LessonPlanActivity).filter(
            LessonPlanActivity.template_id == template.id
        ).order_by(LessonPlanActivity.order_index).all()
        
        # Get categories
        categories = self.db.query(LessonPlanCategory).join(TemplateCategoryAssociation).filter(
            TemplateCategoryAssociation.template_id == template.id
        ).all()
        
        return LessonPlanTemplateResponse(
            id=template.id,
            teacher_id=template.teacher_id,
            title=template.title,
            description=template.description,
            subject=template.subject,
            grade_level=template.grade_level,
            duration_minutes=template.duration_minutes,
            learning_objectives=template.learning_objectives,
            materials_needed=template.materials_needed,
            safety_considerations=template.safety_considerations,
            assessment_methods=template.assessment_methods,
            ai_generated=template.ai_generated,
            template_type=template.template_type,
            difficulty_level=template.difficulty_level,
            equipment_required=template.equipment_required,
            space_requirements=template.space_requirements,
            weather_dependent=template.weather_dependent,
            is_public=template.is_public,
            usage_count=template.usage_count,
            rating_average=template.rating_average,
            rating_count=template.rating_count,
            created_at=template.created_at,
            updated_at=template.updated_at,
            activities=[self._activity_to_response(activity) for activity in activities],
            categories=[self._category_to_response(category) for category in categories]
        )

    def _activity_to_response(self, activity: LessonPlanActivity) -> LessonPlanActivityResponse:
        """Convert activity model to response"""
        return LessonPlanActivityResponse(
            id=activity.id,
            template_id=activity.template_id,
            activity_name=activity.activity_name,
            activity_description=activity.activity_description,
            duration_minutes=activity.duration_minutes,
            activity_type=activity.activity_type,
            equipment_needed=activity.equipment_needed,
            space_required=activity.space_required,
            safety_notes=activity.safety_notes,
            instructions=activity.instructions,
            modifications=activity.modifications,
            success_criteria=activity.success_criteria,
            order_index=activity.order_index,
            created_at=activity.created_at
        )

    def _suggestion_to_response(self, suggestion: AILessonSuggestion) -> AISuggestionResponse:
        """Convert suggestion model to response"""
        return AISuggestionResponse(
            id=suggestion.id,
            teacher_id=suggestion.teacher_id,
            suggestion_type=suggestion.suggestion_type,
            subject=suggestion.subject,
            grade_level=suggestion.grade_level,
            context=suggestion.context,
            ai_suggestion=suggestion.ai_suggestion,
            confidence_score=suggestion.confidence_score,
            tags=suggestion.tags,
            is_applied=suggestion.is_applied,
            applied_at=suggestion.applied_at,
            feedback_rating=suggestion.feedback_rating,
            feedback_comment=suggestion.feedback_comment,
            created_at=suggestion.created_at
        )

    def _sharing_to_response(self, sharing: LessonPlanSharing) -> LessonPlanSharingResponse:
        """Convert sharing model to response"""
        return LessonPlanSharingResponse(
            id=sharing.id,
            template_id=sharing.template_id,
            shared_by_teacher_id=sharing.shared_by_teacher_id,
            shared_with_teacher_id=sharing.shared_with_teacher_id,
            sharing_type=sharing.sharing_type,
            access_level=sharing.access_level,
            shared_at=sharing.shared_at,
            expires_at=sharing.expires_at,
            is_active=sharing.is_active,
            usage_count=sharing.usage_count,
            feedback_rating=sharing.feedback_rating,
            feedback_comment=sharing.feedback_comment
        )

    def _category_to_response(self, category: LessonPlanCategory) -> LessonPlanCategoryResponse:
        """Convert category model to response"""
        return LessonPlanCategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_category_id=category.parent_category_id,
            subject=category.subject,
            grade_level_range=category.grade_level_range,
            icon_name=category.icon_name,
            color_code=category.color_code,
            is_active=category.is_active,
            created_at=category.created_at
        )
