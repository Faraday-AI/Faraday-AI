"""
PE Activity Template API Endpoints for Beta Version

Handles creation, management, and sharing of PE activity templates
for individual teachers without student data integration.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.pe.activity_template_service import ActivityTemplateService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/activities/templates",
    tags=["activity-templates"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input data"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Insufficient permissions"},
        status.HTTP_404_NOT_FOUND: {"description": "Template not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# Pydantic models
class ActivityTemplateCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255, description="Activity name")
    description: Optional[str] = Field(None, max_length=1000, description="Activity description")
    category: str = Field(..., min_length=2, max_length=100, description="Activity category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Activity subcategory")
    grade_levels: Optional[List[str]] = Field(default=[], description="Grade levels")
    duration_minutes: Optional[int] = Field(None, ge=1, le=180, description="Duration in minutes")
    equipment_needed: Optional[List[str]] = Field(default=[], description="Required equipment")
    space_requirements: Optional[str] = Field(None, max_length=100, description="Space requirements")
    skill_level: Optional[str] = Field(None, description="Required skill level")
    learning_objectives: Optional[List[str]] = Field(default=[], description="Learning objectives")
    instructions: str = Field(..., min_length=10, description="Activity instructions")
    safety_considerations: Optional[str] = Field(None, description="Safety considerations")
    modifications: Optional[str] = Field(None, description="Activity modifications")
    assessment_criteria: Optional[str] = Field(None, description="Assessment criteria")
    tags: Optional[List[str]] = Field(default=[], description="Activity tags")
    is_public: bool = Field(default=False, description="Make template public")
    
    @validator('skill_level')
    def validate_skill_level(cls, v):
        if v and v not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError('Skill level must be beginner, intermediate, or advanced')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'cardiovascular', 'strength', 'flexibility', 'coordination',
            'balance', 'agility', 'sports', 'games', 'dance', 'yoga',
            'martial_arts', 'outdoor', 'water_activities', 'other'
        ]
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

class ActivityTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    grade_levels: Optional[List[str]] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=180)
    equipment_needed: Optional[List[str]] = None
    space_requirements: Optional[str] = Field(None, max_length=100)
    skill_level: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    instructions: Optional[str] = Field(None, min_length=10)
    safety_considerations: Optional[str] = None
    modifications: Optional[str] = None
    assessment_criteria: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class ActivityTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    subcategory: Optional[str]
    grade_levels: List[str]
    duration_minutes: Optional[int]
    equipment_needed: List[str]
    space_requirements: Optional[str]
    skill_level: Optional[str]
    learning_objectives: List[str]
    instructions: str
    safety_considerations: Optional[str]
    modifications: Optional[str]
    assessment_criteria: Optional[str]
    tags: List[str]
    is_public: bool
    is_featured: bool
    usage_count: int
    rating_average: float
    rating_count: int
    created_at: Optional[str]
    updated_at: Optional[str]

class TemplateDuplicateRequest(BaseModel):
    new_name: Optional[str] = Field(None, min_length=3, max_length=255)

# Dependency to get activity template service
def get_activity_template_service(db: Session = Depends(get_db)) -> ActivityTemplateService:
    return ActivityTemplateService(db)

@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity template",
    description="Create a new PE activity template for personal use or sharing",
    response_description="Template creation result"
)
async def create_activity_template(
    template_data: ActivityTemplateCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Create a new PE activity template."""
    try:
        logger.info(f"Creating activity template: {template_data.name}")
        
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Create template
        result = await template_service.create_template(
            teacher_id=teacher_id,
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            subcategory=template_data.subcategory,
            grade_levels=template_data.grade_levels,
            duration_minutes=template_data.duration_minutes,
            equipment_needed=template_data.equipment_needed,
            space_requirements=template_data.space_requirements,
            skill_level=template_data.skill_level,
            learning_objectives=template_data.learning_objectives,
            instructions=template_data.instructions,
            safety_considerations=template_data.safety_considerations,
            modifications=template_data.modifications,
            assessment_criteria=template_data.assessment_criteria,
            tags=template_data.tags,
            is_public=template_data.is_public
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result
        )
        
    except ValueError as e:
        logger.warning(f"Validation error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the template"
        )

@router.get(
    "/my-templates",
    response_model=List[ActivityTemplateResponse],
    summary="Get my activity templates",
    description="Retrieve all activity templates created by the current teacher",
    response_description="List of teacher's activity templates"
)
async def get_my_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    grade_level: Optional[str] = Query(None, description="Filter by grade level"),
    skill_level: Optional[str] = Query(None, description="Filter by skill level"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Get all templates created by the current teacher."""
    try:
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Build filters
        filters = {}
        if category:
            filters["category"] = category
        if grade_level:
            filters["grade_level"] = grade_level
        if skill_level:
            filters["skill_level"] = skill_level
        if is_public is not None:
            filters["is_public"] = is_public
        
        # Get templates
        templates = await template_service.get_my_templates(teacher_id, filters)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting teacher templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving templates"
        )

@router.get(
    "/shared-templates",
    response_model=List[ActivityTemplateResponse],
    summary="Get shared activity templates",
    description="Retrieve activity templates shared with the current teacher",
    response_description="List of shared activity templates"
)
async def get_shared_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Get templates shared with the current teacher."""
    try:
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Build filters
        filters = {}
        if category:
            filters["category"] = category
        
        # Get shared templates
        templates = await template_service.get_shared_templates(teacher_id, filters)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting shared templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving shared templates"
        )

@router.get(
    "/{template_id}",
    response_model=ActivityTemplateResponse,
    summary="Get activity template",
    description="Retrieve a specific activity template by ID",
    response_description="Activity template data"
)
async def get_activity_template(
    template_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Get a specific activity template."""
    try:
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Get template (this would need to be implemented in the service)
        # For now, return a placeholder response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Get single template endpoint not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the template"
        )

@router.put(
    "/{template_id}",
    response_model=Dict[str, Any],
    summary="Update activity template",
    description="Update an existing activity template",
    response_description="Update result"
)
async def update_activity_template(
    template_id: str,
    template_data: ActivityTemplateUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Update an existing activity template."""
    try:
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Convert Pydantic model to dict, excluding None values
        updates = {k: v for k, v in template_data.dict().items() if v is not None}
        
        if not updates:
            return {"success": True, "message": "No updates provided"}
        
        # Update template
        result = await template_service.update_template(template_id, teacher_id, updates)
        
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the template"
        )

@router.delete(
    "/{template_id}",
    response_model=Dict[str, Any],
    summary="Delete activity template",
    description="Delete an activity template",
    response_description="Deletion result"
)
async def delete_activity_template(
    template_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Delete an activity template."""
    try:
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Delete template
        success = await template_service.delete_template(template_id, teacher_id)
        
        if success:
            return {"success": True, "message": "Template deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found or unauthorized"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the template"
        )

@router.post(
    "/{template_id}/duplicate",
    response_model=Dict[str, Any],
    summary="Duplicate activity template",
    description="Create a copy of an existing activity template",
    response_description="Duplication result"
)
async def duplicate_activity_template(
    template_id: str,
    duplicate_request: TemplateDuplicateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ActivityTemplateService = Depends(get_activity_template_service)
):
    """Duplicate an existing activity template."""
    try:
        # Extract teacher ID from current user
        teacher_id = current_user.get("teacher_id") or current_user.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Teacher authentication required"
            )
        
        # Duplicate template
        result = await template_service.duplicate_template(
            template_id=template_id,
            teacher_id=teacher_id,
            new_name=duplicate_request.new_name
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result
        )
        
    except ValueError as e:
        logger.warning(f"Validation error duplicating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error duplicating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while duplicating the template"
        )

@router.get(
    "/categories/list",
    response_model=List[str],
    summary="Get activity categories",
    description="Get list of available activity categories",
    response_description="List of activity categories"
)
async def get_activity_categories():
    """Get list of available activity categories."""
    categories = [
        "cardiovascular",
        "strength", 
        "flexibility",
        "coordination",
        "balance",
        "agility",
        "sports",
        "games",
        "dance",
        "yoga",
        "martial_arts",
        "outdoor",
        "water_activities",
        "other"
    ]
    return categories

@router.get(
    "/skill-levels/list",
    response_model=List[str],
    summary="Get skill levels",
    description="Get list of available skill levels",
    response_description="List of skill levels"
)
async def get_skill_levels():
    """Get list of available skill levels."""
    return ["beginner", "intermediate", "advanced"]
