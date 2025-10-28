"""
Assessment Tools Service
Handles assessment template creation, management, and sharing for beta teachers
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
import uuid
import json

from app.models.assessment_tools import (
    AssessmentTemplate,
    AssessmentCriteria,
    AssessmentRubric,
    AssessmentQuestion,
    AssessmentChecklist,
    AssessmentTemplateSharing,
    AssessmentTemplateUsage,
    AssessmentCategory,
    AssessmentTemplateCategoryAssociation,
    AssessmentStandard
)
from app.schemas.assessment_tools import (
    AssessmentTemplateCreate,
    AssessmentTemplateUpdate,
    AssessmentTemplateResponse,
    AssessmentCriteriaCreate,
    AssessmentCriteriaResponse,
    AssessmentRubricCreate,
    AssessmentRubricResponse,
    AssessmentQuestionCreate,
    AssessmentQuestionResponse,
    AssessmentChecklistCreate,
    AssessmentChecklistResponse,
    AssessmentTemplateSharingCreate,
    AssessmentTemplateSharingResponse,
    AssessmentTemplateUsageCreate,
    AssessmentTemplateUsageResponse,
    AssessmentCategoryResponse,
    AssessmentStandardCreate,
    AssessmentStandardResponse
)


class AssessmentToolsService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== TEMPLATE MANAGEMENT ====================
    
    def create_assessment_template(
        self, 
        teacher_id: str, 
        template_data: AssessmentTemplateCreate
    ) -> AssessmentTemplateResponse:
        """Create a new assessment template"""
        try:
            # Create the template
            template = AssessmentTemplate(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                title=template_data.title,
                description=template_data.description,
                subject=template_data.subject,
                grade_level=template_data.grade_level,
                assessment_type=template_data.assessment_type,
                duration_minutes=template_data.duration_minutes,
                total_points=template_data.total_points,
                instructions=template_data.instructions,
                materials_needed=template_data.materials_needed,
                safety_considerations=template_data.safety_considerations,
                ai_generated=template_data.ai_generated,
                difficulty_level=template_data.difficulty_level,
                equipment_required=template_data.equipment_required,
                space_requirements=template_data.space_requirements,
                weather_dependent=template_data.weather_dependent,
                is_public=template_data.is_public
            )
            
            self.db.add(template)
            self.db.flush()  # Get the ID
            
            # Add criteria if provided
            if template_data.criteria:
                for i, criteria_data in enumerate(template_data.criteria):
                    criteria = AssessmentCriteria(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        criterion_name=criteria_data.criterion_name,
                        criterion_description=criteria_data.criterion_description,
                        max_points=criteria_data.max_points,
                        weight_percentage=criteria_data.weight_percentage,
                        assessment_method=criteria_data.assessment_method,
                        order_index=i + 1
                    )
                    self.db.add(criteria)
            
            # Add rubrics if provided
            if template_data.rubrics:
                for i, rubric_data in enumerate(template_data.rubrics):
                    rubric = AssessmentRubric(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        criterion_id=rubric_data.criterion_id,
                        rubric_name=rubric_data.rubric_name,
                        rubric_description=rubric_data.rubric_description,
                        performance_levels=rubric_data.performance_levels,
                        performance_descriptions=rubric_data.performance_descriptions,
                        point_values=rubric_data.point_values,
                        order_index=i + 1
                    )
                    self.db.add(rubric)
            
            # Add questions if provided
            if template_data.questions:
                for i, question_data in enumerate(template_data.questions):
                    question = AssessmentQuestion(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        question_text=question_data.question_text,
                        question_type=question_data.question_type,
                        correct_answer=question_data.correct_answer,
                        possible_answers=question_data.possible_answers,
                        points=question_data.points,
                        order_index=i + 1
                    )
                    self.db.add(question)
            
            # Add checklists if provided
            if template_data.checklists:
                for i, checklist_data in enumerate(template_data.checklists):
                    checklist = AssessmentChecklist(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        checklist_item=checklist_data.checklist_item,
                        item_description=checklist_data.item_description,
                        is_required=checklist_data.is_required,
                        points=checklist_data.points,
                        order_index=i + 1
                    )
                    self.db.add(checklist)
            
            # Add standards if provided
            if template_data.standards:
                for standard_data in template_data.standards:
                    standard = AssessmentStandard(
                        id=str(uuid.uuid4()),
                        template_id=template.id,
                        standard_code=standard_data.standard_code,
                        standard_description=standard_data.standard_description,
                        standard_framework=standard_data.standard_framework,
                        grade_level=standard_data.grade_level,
                        subject=standard_data.subject
                    )
                    self.db.add(standard)
            
            # Add category associations if provided
            if template_data.category_ids:
                for category_id in template_data.category_ids:
                    association = AssessmentTemplateCategoryAssociation(
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
            raise Exception(f"Failed to create assessment template: {str(e)}")

    def get_assessment_template(self, template_id: str, teacher_id: str) -> Optional[AssessmentTemplateResponse]:
        """Get a specific assessment template by ID"""
        template = self.db.query(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.id == template_id,
                or_(
                    AssessmentTemplate.teacher_id == teacher_id,
                    AssessmentTemplate.is_public == True
                )
            )
        ).first()
        
        if not template:
            return None
            
        return self._template_to_response(template)

    def get_teacher_assessment_templates(
        self, 
        teacher_id: str, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        assessment_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssessmentTemplateResponse]:
        """Get assessment templates created by a specific teacher"""
        query = self.db.query(AssessmentTemplate).filter(
            AssessmentTemplate.teacher_id == teacher_id
        )
        
        if subject:
            query = query.filter(AssessmentTemplate.subject == subject)
        if grade_level:
            query = query.filter(AssessmentTemplate.grade_level == grade_level)
        if assessment_type:
            query = query.filter(AssessmentTemplate.assessment_type == assessment_type)
        
        templates = query.order_by(desc(AssessmentTemplate.created_at)).offset(offset).limit(limit).all()
        
        return [self._template_to_response(template) for template in templates]

    def get_public_assessment_templates(
        self,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        assessment_type: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssessmentTemplateResponse]:
        """Get public assessment templates available to all teachers"""
        query = self.db.query(AssessmentTemplate).filter(
            AssessmentTemplate.is_public == True
        )
        
        if subject:
            query = query.filter(AssessmentTemplate.subject == subject)
        if grade_level:
            query = query.filter(AssessmentTemplate.grade_level == grade_level)
        if assessment_type:
            query = query.filter(AssessmentTemplate.assessment_type == assessment_type)
        if difficulty_level:
            query = query.filter(AssessmentTemplate.difficulty_level == difficulty_level)
        
        templates = query.order_by(desc(AssessmentTemplate.rating_average)).offset(offset).limit(limit).all()
        
        return [self._template_to_response(template) for template in templates]

    def update_assessment_template(
        self, 
        template_id: str, 
        teacher_id: str, 
        update_data: AssessmentTemplateUpdate
    ) -> Optional[AssessmentTemplateResponse]:
        """Update an existing assessment template"""
        template = self.db.query(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.id == template_id,
                AssessmentTemplate.teacher_id == teacher_id
            )
        ).first()
        
        if not template:
            return None
        
        # Update template fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field not in ["criteria", "rubrics", "questions", "checklists", "standards", "category_ids"]:
                setattr(template, field, value)
        
        # Update criteria if provided
        if update_data.criteria is not None:
            # Delete existing criteria
            self.db.query(AssessmentCriteria).filter(
                AssessmentCriteria.template_id == template_id
            ).delete()
            
            # Add new criteria
            for i, criteria_data in enumerate(update_data.criteria):
                criteria = AssessmentCriteria(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    criterion_name=criteria_data.criterion_name,
                    criterion_description=criteria_data.criterion_description,
                    max_points=criteria_data.max_points,
                    weight_percentage=criteria_data.weight_percentage,
                    assessment_method=criteria_data.assessment_method,
                    order_index=i + 1
                )
                self.db.add(criteria)
        
        # Update rubrics if provided
        if update_data.rubrics is not None:
            # Delete existing rubrics
            self.db.query(AssessmentRubric).filter(
                AssessmentRubric.template_id == template_id
            ).delete()
            
            # Add new rubrics
            for i, rubric_data in enumerate(update_data.rubrics):
                rubric = AssessmentRubric(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    criterion_id=rubric_data.criterion_id,
                    rubric_name=rubric_data.rubric_name,
                    rubric_description=rubric_data.rubric_description,
                    performance_levels=rubric_data.performance_levels,
                    performance_descriptions=rubric_data.performance_descriptions,
                    point_values=rubric_data.point_values,
                    order_index=i + 1
                )
                self.db.add(rubric)
        
        # Update questions if provided
        if update_data.questions is not None:
            # Delete existing questions
            self.db.query(AssessmentQuestion).filter(
                AssessmentQuestion.template_id == template_id
            ).delete()
            
            # Add new questions
            for i, question_data in enumerate(update_data.questions):
                question = AssessmentQuestion(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    question_text=question_data.question_text,
                    question_type=question_data.question_type,
                    correct_answer=question_data.correct_answer,
                    possible_answers=question_data.possible_answers,
                    points=question_data.points,
                    order_index=i + 1
                )
                self.db.add(question)
        
        # Update checklists if provided
        if update_data.checklists is not None:
            # Delete existing checklists
            self.db.query(AssessmentChecklist).filter(
                AssessmentChecklist.template_id == template_id
            ).delete()
            
            # Add new checklists
            for i, checklist_data in enumerate(update_data.checklists):
                checklist = AssessmentChecklist(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    checklist_item=checklist_data.checklist_item,
                    item_description=checklist_data.item_description,
                    is_required=checklist_data.is_required,
                    points=checklist_data.points,
                    order_index=i + 1
                )
                self.db.add(checklist)
        
        # Update standards if provided
        if update_data.standards is not None:
            # Delete existing standards
            self.db.query(AssessmentStandard).filter(
                AssessmentStandard.template_id == template_id
            ).delete()
            
            # Add new standards
            for standard_data in update_data.standards:
                standard = AssessmentStandard(
                    id=str(uuid.uuid4()),
                    template_id=template.id,
                    standard_code=standard_data.standard_code,
                    standard_description=standard_data.standard_description,
                    standard_framework=standard_data.standard_framework,
                    grade_level=standard_data.grade_level,
                    subject=standard_data.subject
                )
                self.db.add(standard)
        
        # Update category associations if provided
        if update_data.category_ids is not None:
            # Delete existing associations
            self.db.query(AssessmentTemplateCategoryAssociation).filter(
                AssessmentTemplateCategoryAssociation.template_id == template_id
            ).delete()
            
            # Add new associations
            for category_id in update_data.category_ids:
                association = AssessmentTemplateCategoryAssociation(
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

    def delete_assessment_template(self, template_id: str, teacher_id: str) -> bool:
        """Delete an assessment template"""
        template = self.db.query(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.id == template_id,
                AssessmentTemplate.teacher_id == teacher_id
            )
        ).first()
        
        if not template:
            return False
        
        self.db.delete(template)
        self.db.commit()
        
        return True

    def duplicate_assessment_template(self, template_id: str, teacher_id: str) -> Optional[AssessmentTemplateResponse]:
        """Duplicate an existing assessment template"""
        original_template = self.db.query(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.id == template_id,
                or_(
                    AssessmentTemplate.teacher_id == teacher_id,
                    AssessmentTemplate.is_public == True
                )
            )
        ).first()
        
        if not original_template:
            return None
        
        # Create new template
        new_template = AssessmentTemplate(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            title=f"{original_template.title} (Copy)",
            description=original_template.description,
            subject=original_template.subject,
            grade_level=original_template.grade_level,
            assessment_type=original_template.assessment_type,
            duration_minutes=original_template.duration_minutes,
            total_points=original_template.total_points,
            instructions=original_template.instructions,
            materials_needed=original_template.materials_needed,
            safety_considerations=original_template.safety_considerations,
            ai_generated=False,  # Mark as not AI-generated since it's a copy
            difficulty_level=original_template.difficulty_level,
            equipment_required=original_template.equipment_required,
            space_requirements=original_template.space_requirements,
            weather_dependent=original_template.weather_dependent,
            is_public=False  # Private by default
        )
        
        self.db.add(new_template)
        self.db.flush()
        
        # Copy criteria
        original_criteria = self.db.query(AssessmentCriteria).filter(
            AssessmentCriteria.template_id == template_id
        ).order_by(AssessmentCriteria.order_index).all()
        
        for criteria in original_criteria:
            new_criteria = AssessmentCriteria(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                criterion_name=criteria.criterion_name,
                criterion_description=criteria.criterion_description,
                max_points=criteria.max_points,
                weight_percentage=criteria.weight_percentage,
                assessment_method=criteria.assessment_method,
                order_index=criteria.order_index
            )
            self.db.add(new_criteria)
        
        # Copy rubrics
        original_rubrics = self.db.query(AssessmentRubric).filter(
            AssessmentRubric.template_id == template_id
        ).order_by(AssessmentRubric.order_index).all()
        
        for rubric in original_rubrics:
            new_rubric = AssessmentRubric(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                criterion_id=rubric.criterion_id,
                rubric_name=rubric.rubric_name,
                rubric_description=rubric.rubric_description,
                performance_levels=rubric.performance_levels,
                performance_descriptions=rubric.performance_descriptions,
                point_values=rubric.point_values,
                order_index=rubric.order_index
            )
            self.db.add(new_rubric)
        
        # Copy questions
        original_questions = self.db.query(AssessmentQuestion).filter(
            AssessmentQuestion.template_id == template_id
        ).order_by(AssessmentQuestion.order_index).all()
        
        for question in original_questions:
            new_question = AssessmentQuestion(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                question_text=question.question_text,
                question_type=question.question_type,
                correct_answer=question.correct_answer,
                possible_answers=question.possible_answers,
                points=question.points,
                order_index=question.order_index
            )
            self.db.add(new_question)
        
        # Copy checklists
        original_checklists = self.db.query(AssessmentChecklist).filter(
            AssessmentChecklist.template_id == template_id
        ).order_by(AssessmentChecklist.order_index).all()
        
        for checklist in original_checklists:
            new_checklist = AssessmentChecklist(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                checklist_item=checklist.checklist_item,
                item_description=checklist.item_description,
                is_required=checklist.is_required,
                points=checklist.points,
                order_index=checklist.order_index
            )
            self.db.add(new_checklist)
        
        # Copy standards
        original_standards = self.db.query(AssessmentStandard).filter(
            AssessmentStandard.template_id == template_id
        ).all()
        
        for standard in original_standards:
            new_standard = AssessmentStandard(
                id=str(uuid.uuid4()),
                template_id=new_template.id,
                standard_code=standard.standard_code,
                standard_description=standard.standard_description,
                standard_framework=standard.standard_framework,
                grade_level=standard.grade_level,
                subject=standard.subject
            )
            self.db.add(new_standard)
        
        # Copy category associations
        original_associations = self.db.query(AssessmentTemplateCategoryAssociation).filter(
            AssessmentTemplateCategoryAssociation.template_id == template_id
        ).all()
        
        for association in original_associations:
            new_association = AssessmentTemplateCategoryAssociation(
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

    # ==================== SHARING ====================
    
    def share_assessment_template(
        self, 
        template_id: str, 
        teacher_id: str, 
        sharing_data: AssessmentTemplateSharingCreate
    ) -> AssessmentTemplateSharingResponse:
        """Share an assessment template with other teachers"""
        # Verify template ownership
        template = self.db.query(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.id == template_id,
                AssessmentTemplate.teacher_id == teacher_id
            )
        ).first()
        
        if not template:
            raise Exception("Assessment template not found or access denied")
        
        sharing = AssessmentTemplateSharing(
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

    def get_shared_assessment_templates(
        self, 
        teacher_id: str, 
        sharing_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssessmentTemplateResponse]:
        """Get assessment templates shared with a teacher"""
        query = self.db.query(AssessmentTemplate).join(AssessmentTemplateSharing).filter(
            and_(
                AssessmentTemplateSharing.shared_with_teacher_id == teacher_id,
                AssessmentTemplateSharing.is_active == True,
                or_(
                    AssessmentTemplateSharing.expires_at.is_(None),
                    AssessmentTemplateSharing.expires_at > datetime.utcnow()
                )
            )
        )
        
        if sharing_type:
            query = query.filter(AssessmentTemplateSharing.sharing_type == sharing_type)
        
        templates = query.order_by(desc(AssessmentTemplateSharing.shared_at)).offset(offset).limit(limit).all()
        
        return [self._template_to_response(template) for template in templates]

    # ==================== CATEGORIES ====================
    
    def get_assessment_categories(
        self, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> List[AssessmentCategoryResponse]:
        """Get assessment categories"""
        query = self.db.query(AssessmentCategory).filter(
            AssessmentCategory.is_active == True
        )
        
        if subject:
            query = query.filter(AssessmentCategory.subject == subject)
        if grade_level:
            query = query.filter(AssessmentCategory.grade_level_range.contains(grade_level))
        
        categories = query.order_by(asc(AssessmentCategory.name)).all()
        
        return [self._category_to_response(category) for category in categories]

    # ==================== ANALYTICS ====================
    
    def get_assessment_template_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a teacher's assessment templates"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Template creation stats
        templates_created = self.db.query(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.teacher_id == teacher_id,
                AssessmentTemplate.created_at >= start_date
            )
        ).count()
        
        # Usage stats
        usage_stats = self.db.query(
            AssessmentTemplateUsage.usage_type,
            func.count(AssessmentTemplateUsage.id).label('count')
        ).join(AssessmentTemplate).filter(
            and_(
                AssessmentTemplate.teacher_id == teacher_id,
                AssessmentTemplateUsage.usage_date >= start_date
            )
        ).group_by(AssessmentTemplateUsage.usage_type).all()
        
        # Popular templates
        popular_templates = self.db.query(
            AssessmentTemplate.id,
            AssessmentTemplate.title,
            func.count(AssessmentTemplateUsage.id).label('usage_count')
        ).join(AssessmentTemplateUsage).filter(
            AssessmentTemplate.teacher_id == teacher_id
        ).group_by(
            AssessmentTemplate.id, 
            AssessmentTemplate.title
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
        usage = AssessmentTemplateUsage(
            id=str(uuid.uuid4()),
            template_id=template_id,
            teacher_id=teacher_id,
            usage_type=usage_type
        )
        self.db.add(usage)
        self.db.commit()

    def _template_to_response(self, template: AssessmentTemplate) -> AssessmentTemplateResponse:
        """Convert template model to response"""
        # Get criteria
        criteria = self.db.query(AssessmentCriteria).filter(
            AssessmentCriteria.template_id == template.id
        ).order_by(AssessmentCriteria.order_index).all()
        
        # Get rubrics
        rubrics = self.db.query(AssessmentRubric).filter(
            AssessmentRubric.template_id == template.id
        ).order_by(AssessmentRubric.order_index).all()
        
        # Get questions
        questions = self.db.query(AssessmentQuestion).filter(
            AssessmentQuestion.template_id == template.id
        ).order_by(AssessmentQuestion.order_index).all()
        
        # Get checklists
        checklists = self.db.query(AssessmentChecklist).filter(
            AssessmentChecklist.template_id == template.id
        ).order_by(AssessmentChecklist.order_index).all()
        
        # Get standards
        standards = self.db.query(AssessmentStandard).filter(
            AssessmentStandard.template_id == template.id
        ).all()
        
        # Get categories
        categories = self.db.query(AssessmentCategory).join(AssessmentTemplateCategoryAssociation).filter(
            AssessmentTemplateCategoryAssociation.template_id == template.id
        ).all()
        
        return AssessmentTemplateResponse(
            id=template.id,
            teacher_id=template.teacher_id,
            title=template.title,
            description=template.description,
            subject=template.subject,
            grade_level=template.grade_level,
            assessment_type=template.assessment_type,
            duration_minutes=template.duration_minutes,
            total_points=template.total_points,
            instructions=template.instructions,
            materials_needed=template.materials_needed,
            safety_considerations=template.safety_considerations,
            ai_generated=template.ai_generated,
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
            criteria=[self._criteria_to_response(criterion) for criterion in criteria],
            rubrics=[self._rubric_to_response(rubric) for rubric in rubrics],
            questions=[self._question_to_response(question) for question in questions],
            checklists=[self._checklist_to_response(checklist) for checklist in checklists],
            standards=[self._standard_to_response(standard) for standard in standards],
            categories=[self._category_to_response(category) for category in categories]
        )

    def _criteria_to_response(self, criteria: AssessmentCriteria) -> AssessmentCriteriaResponse:
        """Convert criteria model to response"""
        return AssessmentCriteriaResponse(
            id=criteria.id,
            template_id=criteria.template_id,
            criterion_name=criteria.criterion_name,
            criterion_description=criteria.criterion_description,
            max_points=criteria.max_points,
            weight_percentage=criteria.weight_percentage,
            assessment_method=criteria.assessment_method,
            order_index=criteria.order_index,
            created_at=criteria.created_at
        )

    def _rubric_to_response(self, rubric: AssessmentRubric) -> AssessmentRubricResponse:
        """Convert rubric model to response"""
        return AssessmentRubricResponse(
            id=rubric.id,
            template_id=rubric.template_id,
            criterion_id=rubric.criterion_id,
            rubric_name=rubric.rubric_name,
            rubric_description=rubric.rubric_description,
            performance_levels=rubric.performance_levels,
            performance_descriptions=rubric.performance_descriptions,
            point_values=rubric.point_values,
            order_index=rubric.order_index,
            created_at=rubric.created_at
        )

    def _question_to_response(self, question: AssessmentQuestion) -> AssessmentQuestionResponse:
        """Convert question model to response"""
        return AssessmentQuestionResponse(
            id=question.id,
            template_id=question.template_id,
            question_text=question.question_text,
            question_type=question.question_type,
            correct_answer=question.correct_answer,
            possible_answers=question.possible_answers,
            points=question.points,
            order_index=question.order_index,
            created_at=question.created_at
        )

    def _checklist_to_response(self, checklist: AssessmentChecklist) -> AssessmentChecklistResponse:
        """Convert checklist model to response"""
        return AssessmentChecklistResponse(
            id=checklist.id,
            template_id=checklist.template_id,
            checklist_item=checklist.checklist_item,
            item_description=checklist.item_description,
            is_required=checklist.is_required,
            points=checklist.points,
            order_index=checklist.order_index,
            created_at=checklist.created_at
        )

    def _standard_to_response(self, standard: AssessmentStandard) -> AssessmentStandardResponse:
        """Convert standard model to response"""
        return AssessmentStandardResponse(
            id=standard.id,
            template_id=standard.template_id,
            standard_code=standard.standard_code,
            standard_description=standard.standard_description,
            standard_framework=standard.standard_framework,
            grade_level=standard.grade_level,
            subject=standard.subject,
            created_at=standard.created_at
        )

    def _sharing_to_response(self, sharing: AssessmentTemplateSharing) -> AssessmentTemplateSharingResponse:
        """Convert sharing model to response"""
        return AssessmentTemplateSharingResponse(
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

    def _category_to_response(self, category: AssessmentCategory) -> AssessmentCategoryResponse:
        """Convert category model to response"""
        return AssessmentCategoryResponse(
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
