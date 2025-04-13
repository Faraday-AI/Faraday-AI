from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator, confloat, conint, ConfigDict
import logging
from functools import lru_cache
from ...middleware.auth import oauth2_scheme, get_current_active_user
from ...middleware.rate_limit import rate_limit
from ....services.physical_education.services.safety_manager import SafetyManager
from ....services.physical_education.services.equipment_manager import EquipmentManager
from ....services.physical_education.services.safety_incident_manager import SafetyIncidentManager
from ....services.physical_education.services.risk_assessment_manager import RiskAssessmentManager
from ....core.cache import cache_manager
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/safety",
    tags=["safety"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)

# Rate limiting configuration
RATE_LIMIT = {
    "risk_assessment": {"requests": 10, "period": 60},  # 10 requests per minute
    "incidents": {"requests": 20, "period": 60},
    "safety_checks": {"requests": 30, "period": 60},
    "equipment_checks": {"requests": 20, "period": 60},
    "environmental_checks": {"requests": 15, "period": 60},
    "bulk_operations": {"requests": 100, "period": 60},
    "metrics": {"requests": 1, "period": 60}
}

# Initialize managers with caching
safety_manager = SafetyManager(cache_manager=cache_manager)
equipment_manager = EquipmentManager(cache_manager=cache_manager)
incident_manager = SafetyIncidentManager(cache_manager=cache_manager)
risk_manager = RiskAssessmentManager(cache_manager=cache_manager)

# Enhanced Pydantic models with stricter validation
class RiskAssessmentRequest(BaseModel):
    """Request model for conducting a risk assessment."""
    class_id: str = Field(..., min_length=1, max_length=50, description="ID of the class")
    activity_type: str = Field(..., description="Type of activity being assessed")
    environment: str = Field(..., description="Environment where activity will take place")
    additional_notes: Optional[str] = Field(None, max_length=500)
    weather_conditions: Optional[Dict[str, Any]] = Field(None)
    student_count: Optional[conint(gt=0)] = Field(None)

    @validator('activity_type')
    def validate_activity_type(cls, v):
        valid_types = ['indoor', 'outdoor', 'water', 'gym', 'field']
        if v.lower() not in valid_types:
            raise ValueError(f"Activity type must be one of: {', '.join(valid_types)}")
        return v.lower()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "class_id": "PE-2024-001",
                "activity_type": "outdoor",
                "environment": "soccer_field",
                "additional_notes": "Field slightly wet from morning rain",
                "weather_conditions": {
                    "temperature": 22,
                    "humidity": 65,
                    "wind_speed": 10
                },
                "student_count": 25
            }
        }
    )

class SafetyIncidentRequest(BaseModel):
    """Request model for recording a safety incident."""
    class_id: str = Field(..., min_length=1, max_length=50)
    incident_type: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=10, max_length=1000)
    severity: str = Field(..., description="Severity level of the incident")
    affected_students: List[str] = Field(..., min_items=1)
    actions_taken: List[str] = Field(..., min_items=1)
    location: Optional[str] = Field(None, max_length=100)
    time_of_incident: Optional[datetime] = Field(None)
    witnesses: Optional[List[str]] = Field(None)
    follow_up_required: bool = Field(False)

    @validator('severity')
    def validate_severity(cls, v):
        valid_levels = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_levels:
            raise ValueError(f"Severity must be one of: {', '.join(valid_levels)}")
        return v.lower()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "class_id": "PE-2024-001",
                "incident_type": "slip_and_fall",
                "description": "Student slipped on wet surface during warm-up",
                "severity": "medium",
                "affected_students": ["STU-001"],
                "actions_taken": ["First aid applied", "Parent notified"],
                "location": "Main gym floor",
                "time_of_incident": "2024-03-15T10:30:00Z",
                "witnesses": ["STU-002", "STU-003"],
                "follow_up_required": True
            }
        }
    )

# Add response models for better API documentation
class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment results."""
    assessment_id: str = Field(..., min_length=1, max_length=50)
    class_id: str = Field(..., min_length=1, max_length=50)
    activity_type: str = Field(..., min_length=1, max_length=50)
    risk_level: str = Field(..., description="Overall risk level")
    risk_factors: List[str] = Field(..., min_items=1)
    mitigation_measures: List[str] = Field(..., min_items=1)
    assessment_date: datetime = Field(...)
    assessed_by: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., description="Current status of the assessment")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assessment_id": "RA-2024-001",
                "class_id": "PE-2024-001",
                "activity_type": "basketball",
                "risk_level": "medium",
                "risk_factors": ["Wet floor", "Crowded space"],
                "mitigation_measures": ["Dry floor", "Reduce class size"],
                "assessment_date": "2024-03-15T09:00:00Z",
                "assessed_by": "John Smith",
                "status": "active"
            }
        }
    )

# Enhanced error handling with specific error types
class SafetyError(Exception):
    """Base exception for safety-related errors."""
    def __init__(self, message: str, code: str = "SAFETY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationError(SafetyError):
    """Exception for validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field

class DatabaseError(SafetyError):
    """Exception for database-related errors."""
    def __init__(self, message: str, operation: str):
        super().__init__(message, "DATABASE_ERROR")
        self.operation = operation

class AuthorizationError(SafetyError):
    """Exception for authorization errors."""
    def __init__(self, message: str, required_permissions: List[str]):
        super().__init__(message, "AUTHORIZATION_ERROR")
        self.required_permissions = required_permissions

# Enhanced risk assessment endpoint with rate limiting and caching
@router.post(
    "/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Conduct a risk assessment",
    description="Conducts a risk assessment for a specific class and activity",
    response_description="The created risk assessment record",
    responses={
        201: {"description": "Risk assessment created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["risk_assessment"]["requests"], period=RATE_LIMIT["risk_assessment"]["period"])
async def conduct_risk_assessment(
    request: RiskAssessmentRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Conduct a risk assessment for a class activity.
    
    This endpoint performs a comprehensive risk assessment for a physical education activity,
    considering environmental factors, student conditions, and activity-specific risks.
    
    Args:
        request: Risk assessment request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        RiskAssessmentResponse: Created risk assessment record
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info(f"Conducting risk assessment for class {request.class_id}")
        
        # Check user permissions
        if not current_user.get("can_conduct_risk_assessment", False):
            raise AuthorizationError(
                "User not authorized to conduct risk assessments",
                ["can_conduct_risk_assessment"]
            )
        
        # Generate cache key
        cache_key = f"risk_assessment:{request.class_id}:{request.activity_type}:{request.environment}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached risk assessment")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Conduct assessment if not in cache
        result = await safety_manager.conduct_risk_assessment(
            class_id=request.class_id,
            activity_type=request.activity_type,
            environment=request.environment,
            additional_notes=request.additional_notes,
            weather_conditions=request.weather_conditions,
            student_count=request.student_count
        )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in risk assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in risk assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except DatabaseError as e:
        logger.error(f"Database error in risk assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database Error",
                "message": "Error saving risk assessment",
                "operation": e.operation
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in risk assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Add health check endpoint
@router.get(
    "/health",
    summary="Check safety system health",
    description="Checks the health status of the safety system components"
)
async def health_check():
    """Check the health status of the safety system."""
    try:
        health_status = {
            "status": "healthy",
            "components": {
                "database": await safety_manager.check_database_health(),
                "cache": await cache_manager.check_health(),
                "services": {
                    "safety_manager": await safety_manager.check_health(),
                    "equipment_manager": await equipment_manager.check_health(),
                    "incident_manager": await incident_manager.check_health(),
                    "risk_manager": await risk_manager.check_health()
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        return JSONResponse(content=health_status)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Add metrics endpoint
@router.get(
    "/metrics",
    summary="Get safety system metrics",
    description="Retrieves metrics about the safety system's performance"
)
async def get_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get safety system metrics."""
    try:
        metrics = await safety_manager.get_metrics(
            start_date=start_date,
            end_date=end_date
        )
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Add new endpoints for updating and deleting risk assessments
@router.put(
    "/risk-assessment/{assessment_id}",
    summary="Update a risk assessment",
    description="Updates an existing risk assessment record"
)
async def update_risk_assessment(
    assessment_id: int,
    request: RiskAssessmentRequest,
    token: str = Depends(oauth2_scheme)
):
    """Update an existing risk assessment."""
    try:
        result = await safety_manager.update_risk_assessment(
            assessment_id=assessment_id,
            update_data=request.dict()
        )
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error updating risk assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/risk-assessment/{assessment_id}",
    summary="Delete a risk assessment",
    description="Deletes an existing risk assessment record"
)
async def delete_risk_assessment(
    assessment_id: int,
    token: str = Depends(oauth2_scheme)
):
    """Delete an existing risk assessment."""
    try:
        result = await safety_manager.delete_risk_assessment(assessment_id)
        return JSONResponse(content={"success": result})
    except Exception as e:
        logger.error(f"Error deleting risk assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Add new endpoints for emergency procedures
@router.post(
    "/emergency-procedures",
    status_code=status.HTTP_201_CREATED,
    summary="Create emergency procedure",
    description="Creates a new emergency procedure record"
)
async def create_emergency_procedure(
    request: EmergencyProcedureRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create a new emergency procedure."""
    try:
        result = await safety_manager.create_emergency_procedure(
            class_id=request.class_id,
            procedure_type=request.procedure_type,
            description=request.description,
            steps=request.steps,
            contact_info=request.contact_info
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except Exception as e:
        logger.error(f"Error creating emergency procedure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/emergency-procedures",
    summary="Get emergency procedures",
    description="Retrieves emergency procedures with optional filters"
)
async def get_emergency_procedures(
    class_id: Optional[str] = None,
    procedure_type: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get emergency procedures with optional filters."""
    try:
        result = await safety_manager.get_emergency_procedures(
            class_id=class_id,
            procedure_type=procedure_type
        )
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error getting emergency procedures: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Add new endpoint for safety statistics
@router.get(
    "/statistics",
    summary="Get safety statistics",
    description="Retrieves safety statistics with optional filters"
)
async def get_safety_statistics(
    class_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get safety statistics with optional filters."""
    try:
        result = await safety_manager.get_safety_statistics(
            class_id=class_id,
            start_date=start_date,
            end_date=end_date
        )
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error getting safety statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Add new endpoint for safety reports
@router.get(
    "/reports",
    summary="Generate safety report",
    description="Generates a safety report with optional filters"
)
async def generate_safety_report(
    class_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query("pdf", regex="^(pdf|json|csv)$"),
    token: str = Depends(oauth2_scheme)
):
    """Generate a safety report with optional filters."""
    try:
        result = await safety_manager.generate_safety_report(
            class_id=class_id,
            start_date=start_date,
            end_date=end_date,
            format=format
        )
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error generating safety report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Add new endpoint for bulk operations
@router.post(
    "/bulk",
    summary="Perform bulk safety operations",
    description="Performs bulk operations on safety records"
)
async def bulk_safety_operations(
    operations: List[Dict[str, Any]],
    token: str = Depends(oauth2_scheme)
):
    """Perform bulk operations on safety records."""
    try:
        result = await safety_manager.bulk_operations(operations)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error performing bulk operations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Safety Incident Endpoints
class SafetyIncidentResponse(BaseModel):
    """Response model for safety incidents."""
    id: int
    class_id: str
    incident_type: str
    description: str
    severity: str
    affected_students: List[str]
    actions_taken: List[str]
    location: Optional[str]
    time_of_incident: Optional[datetime]
    witnesses: Optional[List[str]]
    follow_up_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "class_id": "PE-2024-001",
                "incident_type": "slip_and_fall",
                "description": "Student slipped on wet surface during warm-up",
                "severity": "medium",
                "affected_students": ["STU-001"],
                "actions_taken": ["First aid applied", "Parent notified"],
                "location": "Main gym floor",
                "time_of_incident": "2024-03-15T10:30:00Z",
                "witnesses": ["STU-002", "STU-003"],
                "follow_up_required": True,
                "created_at": "2024-03-15T10:35:00Z",
                "updated_at": "2024-03-15T10:35:00Z"
            }
        }
    )

@router.post(
    "/incidents",
    response_model=SafetyIncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a safety incident",
    description="Records a new safety incident with detailed information",
    response_description="The created safety incident record",
    responses={
        201: {"description": "Incident recorded successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["incidents"]["requests"], period=RATE_LIMIT["incidents"]["period"])
async def record_incident(
    request: SafetyIncidentRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record a new safety incident.
    
    This endpoint records a safety incident with detailed information about the event,
    affected students, actions taken, and follow-up requirements.
    
    Args:
        request: Safety incident request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        SafetyIncidentResponse: Created safety incident record
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info(f"Recording safety incident for class {request.class_id}")
        
        # Check user permissions
        if not current_user.get("can_record_incidents", False):
            raise AuthorizationError(
                "User not authorized to record incidents",
                ["can_record_incidents"]
            )
        
        # Generate cache key
        cache_key = f"incident:{request.class_id}:{request.incident_type}:{request.severity}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached incident record")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Record incident if not in cache
        result = await incident_manager.record_incident(
            class_id=request.class_id,
            incident_type=request.incident_type,
            description=request.description,
            severity=request.severity,
            affected_students=request.affected_students,
            actions_taken=request.actions_taken,
            location=request.location,
            time_of_incident=request.time_of_incident,
            witnesses=request.witnesses,
            follow_up_required=request.follow_up_required
        )
        
        # Cache the result for 30 minutes
        await cache_manager.set(cache_key, result, expire=1800)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in incident recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in incident recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except DatabaseError as e:
        logger.error(f"Database error in incident recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database Error",
                "message": "Error saving incident record",
                "operation": e.operation
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in incident recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/incidents",
    response_model=List[SafetyIncidentResponse],
    summary="Get safety incidents",
    description="Retrieves safety incidents with optional filters",
    response_description="List of safety incident records",
    responses={
        200: {"description": "Successfully retrieved incidents"},
        400: {"description": "Invalid filter parameters"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["incidents"]["requests"], period=RATE_LIMIT["incidents"]["period"])
async def get_incidents(
    class_id: Optional[str] = Query(None, description="Filter by class ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get safety incidents with optional filters.
    
    This endpoint retrieves safety incidents based on various filter criteria.
    
    Args:
        class_id: Optional class ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        severity: Optional severity level filter
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        List[SafetyIncidentResponse]: List of safety incident records
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info("Retrieving safety incidents")
        
        # Check user permissions
        if not current_user.get("can_view_incidents", False):
            raise AuthorizationError(
                "User not authorized to view incidents",
                ["can_view_incidents"]
            )
        
        # Generate cache key based on filters
        cache_key = f"incidents:{class_id}:{start_date}:{end_date}:{severity}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached incidents")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get incidents if not in cache
        result = await incident_manager.get_incidents(
            class_id=class_id,
            start_date=start_date,
            end_date=end_date,
            severity=severity
        )
        
        # Cache the result for 15 minutes
        await cache_manager.set(cache_key, result, expire=900)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in incident retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in incident retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in incident retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Safety Check Endpoints
class SafetyCheckResponse(BaseModel):
    """Response model for safety checks."""
    id: int
    class_id: str
    check_type: str
    status: str
    findings: List[str]
    recommendations: List[str]
    checked_by: str
    checked_at: datetime
    next_check_due: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "class_id": "PE-2024-001",
                "check_type": "pre-class",
                "status": "completed",
                "findings": [
                    "Floor slightly wet near entrance",
                    "Emergency exit path clear"
                ],
                "recommendations": [
                    "Place wet floor sign",
                    "Monitor floor condition"
                ],
                "checked_by": "TEACHER-001",
                "checked_at": "2024-03-15T08:30:00Z",
                "next_check_due": "2024-03-15T09:30:00Z",
                "created_at": "2024-03-15T08:35:00Z",
                "updated_at": "2024-03-15T08:35:00Z"
            }
        }
    )

class SafetyCheckRequest(BaseModel):
    """Request model for conducting a safety check."""
    class_id: str = Field(..., min_length=1, max_length=50)
    check_type: str = Field(..., description="Type of safety check")
    findings: List[str] = Field(..., min_items=1)
    recommendations: List[str] = Field(..., min_items=1)
    next_check_due: Optional[datetime] = Field(None)
    additional_notes: Optional[str] = Field(None, max_length=500)

    @validator('check_type')
    def validate_check_type(cls, v):
        valid_types = ['pre-class', 'during-class', 'post-class', 'emergency']
        if v.lower() not in valid_types:
            raise ValueError(f"Check type must be one of: {', '.join(valid_types)}")
        return v.lower()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "class_id": "PE-2024-001",
                "check_type": "pre-class",
                "findings": [
                    "Floor slightly wet near entrance",
                    "Emergency exit path clear"
                ],
                "recommendations": [
                    "Place wet floor sign",
                    "Monitor floor condition"
                ],
                "next_check_due": "2024-03-15T09:30:00Z",
                "additional_notes": "Check floor condition every 30 minutes"
            }
        }
    )

@router.post(
    "/safety-checks",
    response_model=SafetyCheckResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Conduct a safety check",
    description="Conducts a safety check for a class with detailed findings and recommendations",
    response_description="The created safety check record",
    responses={
        201: {"description": "Safety check recorded successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["safety_checks"]["requests"], period=RATE_LIMIT["safety_checks"]["period"])
async def conduct_safety_check(
    request: SafetyCheckRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Conduct a safety check for a class.
    
    This endpoint records a safety check with detailed findings and recommendations
    for maintaining a safe environment.
    
    Args:
        request: Safety check request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        SafetyCheckResponse: Created safety check record
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info(f"Conducting safety check for class {request.class_id}")
        
        # Check user permissions
        if not current_user.get("can_conduct_safety_checks", False):
            raise AuthorizationError(
                "User not authorized to conduct safety checks",
                ["can_conduct_safety_checks"]
            )
        
        # Generate cache key
        cache_key = f"safety_check:{request.class_id}:{request.check_type}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached safety check")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Conduct check if not in cache
        result = await safety_manager.conduct_safety_check(
            class_id=request.class_id,
            check_type=request.check_type,
            findings=request.findings,
            recommendations=request.recommendations,
            next_check_due=request.next_check_due,
            additional_notes=request.additional_notes,
            checked_by=current_user["id"]
        )
        
        # Cache the result for 15 minutes
        await cache_manager.set(cache_key, result, expire=900)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in safety check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in safety check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except DatabaseError as e:
        logger.error(f"Database error in safety check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database Error",
                "message": "Error saving safety check",
                "operation": e.operation
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in safety check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/safety-checks",
    response_model=List[SafetyCheckResponse],
    summary="Get safety checks",
    description="Retrieves safety checks with optional filters",
    response_description="List of safety check records",
    responses={
        200: {"description": "Successfully retrieved safety checks"},
        400: {"description": "Invalid filter parameters"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["safety_checks"]["requests"], period=RATE_LIMIT["safety_checks"]["period"])
async def get_safety_checks(
    class_id: Optional[str] = Query(None, description="Filter by class ID"),
    check_type: Optional[str] = Query(None, description="Filter by check type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get safety checks with optional filters.
    
    This endpoint retrieves safety checks based on various filter criteria.
    
    Args:
        class_id: Optional class ID filter
        check_type: Optional check type filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        List[SafetyCheckResponse]: List of safety check records
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info("Retrieving safety checks")
        
        # Check user permissions
        if not current_user.get("can_view_safety_checks", False):
            raise AuthorizationError(
                "User not authorized to view safety checks",
                ["can_view_safety_checks"]
            )
        
        # Generate cache key based on filters
        cache_key = f"safety_checks:{class_id}:{check_type}:{start_date}:{end_date}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached safety checks")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get safety checks if not in cache
        result = await safety_manager.get_safety_checks(
            class_id=class_id,
            check_type=check_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Cache the result for 15 minutes
        await cache_manager.set(cache_key, result, expire=900)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in safety check retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in safety check retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in safety check retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Equipment Check Endpoints
class EquipmentCheckResponse(BaseModel):
    """Response model for equipment checks."""
    id: int
    class_id: str
    equipment_id: str
    maintenance_status: bool
    damage_status: bool
    age_status: bool
    last_maintenance: Optional[datetime]
    purchase_date: Optional[datetime]
    max_age_years: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "class_id": "PE-2024-001",
                "equipment_id": "EQ-001",
                "maintenance_status": True,
                "damage_status": False,
                "age_status": True,
                "last_maintenance": "2024-02-15T10:00:00Z",
                "purchase_date": "2023-01-15T00:00:00Z",
                "max_age_years": 5.0,
                "created_at": "2024-03-15T08:30:00Z",
                "updated_at": "2024-03-15T08:30:00Z"
            }
        }
    )

class EquipmentCheckRequest(BaseModel):
    """Request model for recording an equipment check."""
    class_id: str = Field(..., min_length=1, max_length=50)
    equipment_id: str = Field(..., min_length=1, max_length=50)
    maintenance_status: bool
    damage_status: bool
    age_status: bool
    last_maintenance: Optional[datetime] = Field(None)
    purchase_date: Optional[datetime] = Field(None)
    max_age_years: Optional[float] = Field(None)

    @validator('class_id')
    def validate_class_id(cls, v):
        if not v.isalnum():
            raise ValueError("Class ID must be alphanumeric")
        return v

    @validator('equipment_id')
    def validate_equipment_id(cls, v):
        if not v.isalnum():
            raise ValueError("Equipment ID must be alphanumeric")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "class_id": "PE-2024-001",
                "equipment_id": "EQ-001",
                "maintenance_status": True,
                "damage_status": False,
                "age_status": True,
                "last_maintenance": "2024-02-15T10:00:00Z",
                "purchase_date": "2023-01-15T00:00:00Z",
                "max_age_years": 5.0
            }
        }
    )

class BulkEquipmentCheckRequest(BaseModel):
    """Request model for bulk equipment checks."""
    checks: List[EquipmentCheckRequest] = Field(..., min_items=1, max_items=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "checks": [
                    {
                        "class_id": "PE-2024-001",
                        "equipment_id": "EQ-001",
                        "maintenance_status": True,
                        "damage_status": False,
                        "age_status": True,
                        "last_maintenance": "2024-02-15T10:00:00Z",
                        "purchase_date": "2023-01-15T00:00:00Z",
                        "max_age_years": 5.0
                    }
                ]
            }
        }
    )

class EnhancedMetricsResponse(BaseModel):
    """Response model for enhanced safety metrics."""
    total_checks: int
    active_equipment: int
    maintenance_needed: int
    damaged_equipment: int
    aging_equipment: int
    last_check_date: Optional[datetime]
    next_maintenance_due: Optional[datetime]
    equipment_status_summary: Dict[str, int]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_checks": 150,
                "active_equipment": 45,
                "maintenance_needed": 5,
                "damaged_equipment": 2,
                "aging_equipment": 3,
                "last_check_date": "2024-03-15T08:30:00Z",
                "next_maintenance_due": "2024-04-15T00:00:00Z",
                "equipment_status_summary": {
                    "good": 35,
                    "needs_maintenance": 5,
                    "damaged": 2,
                    "aging": 3
                }
            }
        }
    )

@router.post(
    "/equipment-checks",
    response_model=EquipmentCheckResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record an equipment check",
    description="Records a new equipment safety check",
    response_description="The created equipment check record",
    responses={
        201: {"description": "Equipment check recorded successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["equipment_checks"]["requests"], period=RATE_LIMIT["equipment_checks"]["period"])
async def record_equipment_check(
    request: EquipmentCheckRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record a new equipment safety check.
    
    This endpoint records an equipment safety check with maintenance and condition details.
    
    Args:
        request: Equipment check request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        EquipmentCheckResponse: Created equipment check record
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info(f"Recording equipment check for class {request.class_id}")
        
        # Check user permissions
        if not current_user.get("can_conduct_equipment_checks", False):
            raise AuthorizationError(
                "User not authorized to conduct equipment checks",
                ["can_conduct_equipment_checks"]
            )
        
        # Generate cache key
        cache_key = f"equipment_check:{request.class_id}:{request.equipment_id}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached equipment check")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Record check if not in cache
        result = await equipment_manager.record_equipment_check(
            class_id=request.class_id,
            equipment_id=request.equipment_id,
            maintenance_status=request.maintenance_status,
            damage_status=request.damage_status,
            age_status=request.age_status,
            last_maintenance=request.last_maintenance,
            purchase_date=request.purchase_date,
            max_age_years=request.max_age_years
        )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in equipment check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in equipment check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except DatabaseError as e:
        logger.error(f"Database error in equipment check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database Error",
                "message": "Error saving equipment check",
                "operation": e.operation
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in equipment check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/equipment-checks",
    response_model=List[EquipmentCheckResponse],
    summary="Get equipment checks",
    description="Retrieves equipment checks with optional filters",
    response_description="List of equipment check records",
    responses={
        200: {"description": "Successfully retrieved equipment checks"},
        400: {"description": "Invalid filter parameters"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["equipment_checks"]["requests"], period=RATE_LIMIT["equipment_checks"]["period"])
async def get_equipment_checks(
    class_id: Optional[str] = Query(None, description="Filter by class ID"),
    equipment_id: Optional[str] = Query(None, description="Filter by equipment ID"),
    maintenance_status: Optional[bool] = Query(None, description="Filter by maintenance status"),
    damage_status: Optional[bool] = Query(None, description="Filter by damage status"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get equipment checks with optional filters.
    
    This endpoint retrieves equipment checks based on various filter criteria.
    
    Args:
        class_id: Optional class ID filter
        equipment_id: Optional equipment ID filter
        maintenance_status: Optional maintenance status filter
        damage_status: Optional damage status filter
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        List[EquipmentCheckResponse]: List of equipment check records
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info("Retrieving equipment checks")
        
        # Check user permissions
        if not current_user.get("can_view_equipment_checks", False):
            raise AuthorizationError(
                "User not authorized to view equipment checks",
                ["can_view_equipment_checks"]
            )
        
        # Generate cache key based on filters
        cache_key = f"equipment_checks:{class_id}:{equipment_id}:{maintenance_status}:{damage_status}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached equipment checks")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get equipment checks if not in cache
        result = await equipment_manager.get_equipment_checks(
            class_id=class_id,
            equipment_id=equipment_id,
            maintenance_status=maintenance_status,
            damage_status=damage_status
        )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValidationError as e:
        logger.error(f"Validation error in equipment check retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in equipment check retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in equipment check retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.post(
    "/equipment-checks/bulk",
    response_model=List[EquipmentCheckResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record bulk equipment checks",
    description="Records multiple equipment checks in a single operation",
    response_description="List of created equipment check records",
    responses={
        201: {"description": "Bulk equipment checks recorded successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["bulk_operations"]["requests"], period=RATE_LIMIT["bulk_operations"]["period"])
async def record_bulk_equipment_checks(
    request: BulkEquipmentCheckRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record multiple equipment checks in a single operation.
    
    This endpoint records multiple equipment checks efficiently in a single database transaction.
    
    Args:
        request: Bulk equipment check request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        List[EquipmentCheckResponse]: List of created equipment check records
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info(f"Recording {len(request.checks)} equipment checks")
        
        # Check user permissions
        if not current_user.get("can_conduct_equipment_checks", False):
            raise AuthorizationError(
                "User not authorized to conduct equipment checks",
                ["can_conduct_equipment_checks"]
            )
        
        # Process checks in batches to prevent overload
        batch_size = 10
        results = []
        
        for i in range(0, len(request.checks), batch_size):
            batch = request.checks[i:i + batch_size]
            batch_results = await equipment_manager.record_bulk_equipment_checks(batch)
            results.extend(batch_results)
            
            # Small delay between batches to prevent system overload
            if i + batch_size < len(request.checks):
                await asyncio.sleep(0.1)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(results)
        )
    except ValidationError as e:
        logger.error(f"Validation error in bulk equipment checks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "field": e.field
            }
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in bulk equipment checks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except DatabaseError as e:
        logger.error(f"Database error in bulk equipment checks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database Error",
                "message": "Error saving bulk equipment checks",
                "operation": e.operation
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in bulk equipment checks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/metrics/enhanced",
    response_model=EnhancedMetricsResponse,
    summary="Get enhanced safety metrics",
    description="Retrieves detailed safety metrics and equipment status",
    response_description="Enhanced safety metrics",
    responses={
        200: {"description": "Successfully retrieved enhanced metrics"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["metrics"]["requests"], period=RATE_LIMIT["metrics"]["period"])
async def get_enhanced_metrics(
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get enhanced safety metrics and equipment status.
    
    This endpoint provides detailed metrics about equipment status and safety checks.
    
    Args:
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        EnhancedMetricsResponse: Detailed safety metrics
    
    Raises:
        HTTPException: If server error occurs
    """
    try:
        logger.info("Retrieving enhanced safety metrics")
        
        # Check user permissions
        if not current_user.get("can_view_metrics", False):
            raise AuthorizationError(
                "User not authorized to view metrics",
                ["can_view_metrics"]
            )
        
        # Generate cache key
        cache_key = "enhanced_metrics"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached enhanced metrics")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get metrics if not in cache
        result = await equipment_manager.get_enhanced_metrics()
        
        # Cache the result for 5 minutes (metrics can be slightly stale)
        await cache_manager.set(cache_key, result, expire=300)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except AuthorizationError as e:
        logger.error(f"Authorization error in enhanced metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": str(e),
                "required_permissions": e.required_permissions
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in enhanced metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Environmental Check Endpoints
@router.post(
    "/environmental-checks",
    status_code=status.HTTP_201_CREATED,
    summary="Record an environmental check",
    description="Records a new environmental safety check"
)
async def record_environmental_check(
    request: EnvironmentalCheckRequest,
    token: str = Depends(oauth2_scheme)
):
    """Record a new environmental safety check."""
    try:
        result = await safety_manager.get_environmental_checks(
            class_id=request.class_id,
            temperature=request.temperature,
            humidity=request.humidity,
            air_quality=request.air_quality,
            surface_conditions=request.surface_conditions,
            lighting=request.lighting,
            equipment_condition=request.equipment_condition
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/environmental-checks",
    summary="Get environmental checks",
    description="Retrieves environmental checks with optional filters"
)
async def get_environmental_checks(
    class_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get environmental checks with optional filters."""
    try:
        result = await safety_manager.get_environmental_checks(
            class_id=class_id,
            start_date=start_date,
            end_date=end_date
        )
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 