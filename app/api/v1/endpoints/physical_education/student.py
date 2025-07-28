from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
import asyncio
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, oauth2_scheme
from app.core.rate_limit import rate_limit
from app.core.cache import cache_manager
from app.core.database import get_db
from app.services.physical_education.student_manager import StudentManager
from app.services.physical_education.assessment_system import AssessmentSystem
from app.models.physical_education.student import (
    Student,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation
)
from app.models.health_fitness.metrics.health import HealthMetric
from app.models.physical_education.progress import (
    Progress,
    ProgressGoal,
    PhysicalEducationProgressNote as ProgressNote
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/student",
    tags=["student"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# Initialize managers
student_manager = StudentManager()
assessment_system = AssessmentSystem()

# Rate limiting configuration
RATE_LIMIT = {
    "student_profiles": {"requests": 30, "period": 60},
    "class_management": {"requests": 20, "period": 60},
    "attendance": {"requests": 50, "period": 60},
    "progress": {"requests": 40, "period": 60},
    "reports": {"requests": 10, "period": 60},
    "recommendations": {"requests": 10, "period": 60}
}

# Response Models
class StudentProfileResponse(BaseModel):
    """Response model for student profiles."""
    student_id: str
    first_name: str
    last_name: str
    grade_level: str
    date_of_birth: datetime
    medical_conditions: List[str]
    emergency_contact: Dict[str, str]
    skill_level: str
    attendance_rate: float
    current_classes: List[str]
    progress_history: List[Dict[str, Any]]
    assessments: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-001",
                "first_name": "John",
                "last_name": "Doe",
                "grade_level": "5",
                "date_of_birth": "2010-01-15T00:00:00Z",
                "medical_conditions": ["Asthma"],
                "emergency_contact": {
                    "name": "Jane Doe",
                    "phone": "555-123-4567",
                    "relationship": "Parent"
                },
                "skill_level": "Intermediate",
                "attendance_rate": 0.95,
                "current_classes": ["PE-2024-001"],
                "progress_history": [
                    {
                        "date": "2024-03-01T00:00:00Z",
                        "skill": "Running",
                        "level": "Improved"
                    }
                ],
                "assessments": [
                    {
                        "date": "2024-03-15T00:00:00Z",
                        "type": "Fitness Test",
                        "score": 85
                    }
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "last_updated": "2024-03-15T00:00:00Z"
            }
        }
    )

class StudentProfileRequest(BaseModel):
    """Request model for creating/updating student profiles."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    grade_level: str = Field(..., min_length=1, max_length=10)
    date_of_birth: datetime
    medical_conditions: Optional[List[str]] = Field(default_factory=list)
    emergency_contact: Optional[Dict[str, str]] = Field(default_factory=dict)

    @validator('medical_conditions')
    def validate_medical_conditions(cls, v):
        if not all(isinstance(condition, str) for condition in v):
            raise ValueError("All medical conditions must be strings")
        return v

    @validator('emergency_contact')
    def validate_emergency_contact(cls, v):
        required_fields = ['name', 'phone', 'relationship']
        if not all(field in v for field in required_fields):
            raise ValueError("Emergency contact must include name, phone, and relationship")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "grade_level": "5",
                "date_of_birth": "2010-01-15T00:00:00Z",
                "medical_conditions": ["Asthma"],
                "emergency_contact": {
                    "name": "Jane Doe",
                    "phone": "555-123-4567",
                    "relationship": "Parent"
                }
            }
        }
    )

# Class Management Models
class ClassResponse(BaseModel):
    """Response model for classes."""
    class_id: str
    name: str
    grade_level: str
    max_size: int
    current_size: int
    schedule: Dict[str, Any]
    enrolled_students: List[str]
    created_at: datetime
    last_updated: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "class_id": "PE-2024-001",
                "name": "Grade 5 Physical Education",
                "grade_level": "5",
                "max_size": 30,
                "current_size": 25,
                "schedule": {
                    "monday": "9:00-10:00",
                    "wednesday": "9:00-10:00",
                    "friday": "9:00-10:00"
                },
                "enrolled_students": ["STU-001", "STU-002"],
                "created_at": "2024-01-01T00:00:00Z",
                "last_updated": "2024-03-15T00:00:00Z"
            }
        }
    )

class ClassRequest(BaseModel):
    """Request model for creating/updating classes."""
    name: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=10)
    max_size: int = Field(..., gt=0, le=50)
    schedule: Dict[str, Any]

    @validator('schedule')
    def validate_schedule(cls, v):
        if not all(day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'] for day in v.keys()):
            raise ValueError("Schedule must only include weekdays")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Grade 5 Physical Education",
                "grade_level": "5",
                "max_size": 30,
                "schedule": {
                    "monday": "9:00-10:00",
                    "wednesday": "9:00-10:00",
                    "friday": "9:00-10:00"
                }
            }
        }
    )

# Student Profile Endpoints
@router.post(
    "/profiles",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student profile",
    description="Creates a new student profile with basic information and medical details",
    response_description="The created student profile",
    responses={
        201: {"description": "Student profile created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["student_profiles"]["requests"], period=RATE_LIMIT["student_profiles"]["period"])
async def create_student_profile(
    request: StudentProfileRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new student profile.
    
    This endpoint creates a new student profile with basic information and medical details.
    
    Args:
        request: Student profile request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        StudentProfileResponse: Created student profile
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info("Creating new student profile")
        
        # Check user permissions
        if not current_user.get("can_manage_students", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to manage students",
                    "required_permissions": ["can_manage_students"]
                }
            )
        
        # Generate student ID
        student_id = f"STU-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create student profile
        result = await student_manager.create_student_profile(
            student_id=student_id,
            first_name=request.first_name,
            last_name=request.last_name,
            grade_level=request.grade_level,
            date_of_birth=request.date_of_birth,
            medical_conditions=request.medical_conditions,
            emergency_contact=request.emergency_contact
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        logger.error(f"Validation error in student profile creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in student profile creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/profiles/{student_id}",
    response_model=StudentProfileResponse,
    summary="Get student profile",
    description="Retrieves a student profile by ID",
    response_description="The student profile",
    responses={
        200: {"description": "Successfully retrieved student profile"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student profile not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["student_profiles"]["requests"], period=RATE_LIMIT["student_profiles"]["period"])
async def get_student_profile(
    student_id: str,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a student profile by ID.
    
    This endpoint retrieves a student profile with all associated information.
    
    Args:
        student_id: The ID of the student to retrieve
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        StudentProfileResponse: The student profile
    
    Raises:
        HTTPException: If student not found or server error occurs
    """
    try:
        logger.info(f"Retrieving student profile for {student_id}")
        
        # Check user permissions
        if not current_user.get("can_view_students", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to view students",
                    "required_permissions": ["can_view_students"]
                }
            )
        
        # Generate cache key
        cache_key = f"student_profile:{student_id}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached student profile")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get student profile if not in cache
        result = await student_manager.get_student_profile(student_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Student profile with ID {student_id} not found"
                }
            )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in student profile retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Class Management Endpoints
@router.post(
    "/classes",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new class",
    description="Creates a new physical education class",
    response_description="The created class",
    responses={
        201: {"description": "Class created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["class_management"]["requests"], period=RATE_LIMIT["class_management"]["period"])
async def create_class(
    request: ClassRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new physical education class.
    
    This endpoint creates a new class with schedule and capacity information.
    
    Args:
        request: Class request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        ClassResponse: Created class
    
    Raises:
        HTTPException: If validation fails or server error occurs
    """
    try:
        logger.info("Creating new class")
        
        # Check user permissions
        if not current_user.get("can_manage_classes", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to manage classes",
                    "required_permissions": ["can_manage_classes"]
                }
            )
        
        # Generate class ID
        class_id = f"PE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create class
        result = await student_manager.create_class(
            class_id=class_id,
            name=request.name,
            grade_level=request.grade_level,
            max_size=request.max_size,
            schedule=request.schedule
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        logger.error(f"Validation error in class creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in class creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/classes/{class_id}",
    response_model=ClassResponse,
    summary="Get class",
    description="Retrieves a class by ID",
    response_description="The class",
    responses={
        200: {"description": "Successfully retrieved class"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["class_management"]["requests"], period=RATE_LIMIT["class_management"]["period"])
async def get_class(
    class_id: str,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a class by ID.
    
    This endpoint retrieves a class with all associated information.
    
    Args:
        class_id: The ID of the class to retrieve
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        ClassResponse: The class
    
    Raises:
        HTTPException: If class not found or server error occurs
    """
    try:
        logger.info(f"Retrieving class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_view_classes", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to view classes",
                    "required_permissions": ["can_view_classes"]
                }
            )
        
        # Generate cache key
        cache_key = f"class:{class_id}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached class")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get class if not in cache
        result = await student_manager.get_class(class_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Class with ID {class_id} not found"
                }
            )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in class retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.post(
    "/classes/{class_id}/enroll/{student_id}",
    response_model=ClassResponse,
    summary="Enroll student in class",
    description="Enrolls a student in a physical education class",
    response_description="The updated class",
    responses={
        200: {"description": "Student enrolled successfully"},
        400: {"description": "Invalid enrollment request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["class_management"]["requests"], period=RATE_LIMIT["class_management"]["period"])
async def enroll_student(
    class_id: str,
    student_id: str,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Enroll a student in a class.
    
    This endpoint enrolls a student in a physical education class.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student to enroll
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        ClassResponse: The updated class
    
    Raises:
        HTTPException: If enrollment fails or server error occurs
    """
    try:
        logger.info(f"Enrolling student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_manage_enrollments", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to manage enrollments",
                    "required_permissions": ["can_manage_enrollments"]
                }
            )
        
        # Enroll student
        result = await student_manager.enroll_student(student_id, class_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Enrollment Error",
                    "message": "Failed to enroll student in class"
                }
            )
        
        # Invalidate cache
        await cache_manager.delete(f"class:{class_id}")
        await cache_manager.delete(f"student_profile:{student_id}")
        
        # Get updated class
        updated_class = await student_manager.get_class(class_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(updated_class)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in student enrollment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Attendance Models
class AttendanceRecordResponse(BaseModel):
    """Response model for attendance records."""
    class_id: str
    student_id: str
    date: datetime
    present: bool
    notes: Optional[str]
    recorded_by: str
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "class_id": "PE-2024-001",
                "student_id": "STU-001",
                "date": "2024-03-15T09:00:00Z",
                "present": True,
                "notes": "Participated in all activities",
                "recorded_by": "TEACHER-001",
                "created_at": "2024-03-15T09:05:00Z"
            }
        }
    )

class AttendanceRecordRequest(BaseModel):
    """Request model for recording attendance."""
    present: bool
    notes: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "present": True,
                "notes": "Participated in all activities",
                "date": "2024-03-15T09:00:00Z"
            }
        }
    )

class AttendanceSummaryResponse(BaseModel):
    """Response model for attendance summaries."""
    student_id: str
    class_id: str
    total_classes: int
    present_count: int
    absent_count: int
    attendance_rate: float
    recent_records: List[Dict[str, Any]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-001",
                "class_id": "PE-2024-001",
                "total_classes": 30,
                "present_count": 28,
                "absent_count": 2,
                "attendance_rate": 0.93,
                "recent_records": [
                    {
                        "date": "2024-03-15T09:00:00Z",
                        "present": True,
                        "notes": "Participated in all activities"
                    }
                ]
            }
        }
    )

# Attendance Endpoints
@router.post(
    "/classes/{class_id}/attendance/{student_id}",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record attendance",
    description="Records attendance for a student in a class",
    response_description="The created attendance record",
    responses={
        201: {"description": "Attendance recorded successfully"},
        400: {"description": "Invalid attendance data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["attendance"]["requests"], period=RATE_LIMIT["attendance"]["period"])
async def record_attendance(
    class_id: str,
    student_id: str,
    request: AttendanceRecordRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record attendance for a student in a class.
    
    This endpoint records attendance for a student in a physical education class.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student
        request: Attendance record data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        AttendanceRecordResponse: Created attendance record
    
    Raises:
        HTTPException: If recording fails or server error occurs
    """
    try:
        logger.info(f"Recording attendance for student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_record_attendance", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to record attendance",
                    "required_permissions": ["can_record_attendance"]
                }
            )
        
        # Record attendance
        result = await student_manager.record_attendance(
            class_id=class_id,
            student_id=student_id,
            date=request.date or datetime.now(),
            present=request.present,
            notes=request.notes
        )
        
        # Invalidate cache
        await cache_manager.delete(f"attendance_summary:{student_id}:{class_id}")
        await cache_manager.delete(f"student_profile:{student_id}")
        await cache_manager.delete(f"class:{class_id}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        logger.error(f"Validation error in attendance recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in attendance recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/classes/{class_id}/attendance/{student_id}/summary",
    response_model=AttendanceSummaryResponse,
    summary="Get attendance summary",
    description="Retrieves attendance summary for a student in a class",
    response_description="The attendance summary",
    responses={
        200: {"description": "Successfully retrieved attendance summary"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["attendance"]["requests"], period=RATE_LIMIT["attendance"]["period"])
async def get_attendance_summary(
    class_id: str,
    student_id: str,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get attendance summary for a student in a class.
    
    This endpoint retrieves attendance summary and recent records for a student.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        AttendanceSummaryResponse: The attendance summary
    
    Raises:
        HTTPException: If retrieval fails or server error occurs
    """
    try:
        logger.info(f"Retrieving attendance summary for student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_view_attendance", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to view attendance",
                    "required_permissions": ["can_view_attendance"]
                }
            )
        
        # Generate cache key
        cache_key = f"attendance_summary:{student_id}:{class_id}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached attendance summary")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get attendance summary if not in cache
        result = await student_manager.get_attendance_summary(student_id, class_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Attendance records not found for student {student_id} in class {class_id}"
                }
            )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in attendance summary retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Progress Tracking Models
class ProgressRecordResponse(BaseModel):
    """Response model for progress records."""
    student_id: str
    class_id: str
    assessment_type: str
    assessment_date: datetime
    metrics: Dict[str, float]
    notes: Optional[str]
    recorded_by: str
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-001",
                "class_id": "PE-2024-001",
                "assessment_type": "Fitness Test",
                "assessment_date": "2024-03-15T09:00:00Z",
                "metrics": {
                    "push_ups": 25,
                    "sit_ups": 30,
                    "mile_run": 8.5
                },
                "notes": "Showing improvement in endurance",
                "recorded_by": "TEACHER-001",
                "created_at": "2024-03-15T09:30:00Z"
            }
        }
    )

class ProgressRecordRequest(BaseModel):
    """Request model for recording progress."""
    assessment_type: str = Field(..., min_length=1, max_length=50)
    assessment_date: Optional[datetime] = None
    metrics: Dict[str, float]
    notes: Optional[str] = Field(None, max_length=500)

    @validator('assessment_type')
    def validate_assessment_type(cls, v):
        valid_types = ['Fitness Test', 'Skill Assessment', 'Performance Test']
        if v not in valid_types:
            raise ValueError(f"Assessment type must be one of: {', '.join(valid_types)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assessment_type": "Fitness Test",
                "assessment_date": "2024-03-15T09:00:00Z",
                "metrics": {
                    "push_ups": 25,
                    "sit_ups": 30,
                    "mile_run": 8.5
                },
                "notes": "Showing improvement in endurance"
            }
        }
    )

class ProgressSummaryResponse(BaseModel):
    """Response model for progress summaries."""
    student_id: str
    class_id: str
    assessment_type: str
    total_assessments: int
    average_metrics: Dict[str, float]
    improvement_rate: Dict[str, float]
    recent_records: List[Dict[str, Any]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-001",
                "class_id": "PE-2024-001",
                "assessment_type": "Fitness Test",
                "total_assessments": 5,
                "average_metrics": {
                    "push_ups": 23,
                    "sit_ups": 28,
                    "mile_run": 9.0
                },
                "improvement_rate": {
                    "push_ups": 0.15,
                    "sit_ups": 0.12,
                    "mile_run": -0.05
                },
                "recent_records": [
                    {
                        "date": "2024-03-15T09:00:00Z",
                        "metrics": {
                            "push_ups": 25,
                            "sit_ups": 30,
                            "mile_run": 8.5
                        }
                    }
                ]
            }
        }
    )

# Progress Tracking Endpoints
@router.post(
    "/classes/{class_id}/progress/{student_id}",
    response_model=ProgressRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record progress",
    description="Records progress for a student in a class",
    response_description="The created progress record",
    responses={
        201: {"description": "Progress recorded successfully"},
        400: {"description": "Invalid progress data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["progress"]["requests"], period=RATE_LIMIT["progress"]["period"])
async def record_progress(
    class_id: str,
    student_id: str,
    request: ProgressRecordRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record progress for a student in a class.
    
    This endpoint records progress for a student in a physical education class.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student
        request: Progress record data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        ProgressRecordResponse: Created progress record
    
    Raises:
        HTTPException: If recording fails or server error occurs
    """
    try:
        logger.info(f"Recording progress for student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_record_progress", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to record progress",
                    "required_permissions": ["can_record_progress"]
                }
            )
        
        # Record progress
        result = await student_manager.record_progress(
            class_id=class_id,
            student_id=student_id,
            assessment_type=request.assessment_type,
            assessment_date=request.assessment_date or datetime.now(),
            metrics=request.metrics,
            notes=request.notes
        )
        
        # Invalidate cache
        await cache_manager.delete(f"progress_summary:{student_id}:{class_id}:{request.assessment_type}")
        await cache_manager.delete(f"student_profile:{student_id}")
        await cache_manager.delete(f"class:{class_id}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        logger.error(f"Validation error in progress recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in progress recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

@router.get(
    "/classes/{class_id}/progress/{student_id}/summary",
    response_model=ProgressSummaryResponse,
    summary="Get progress summary",
    description="Retrieves progress summary for a student in a class",
    response_description="The progress summary",
    responses={
        200: {"description": "Successfully retrieved progress summary"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["progress"]["requests"], period=RATE_LIMIT["progress"]["period"])
async def get_progress_summary(
    class_id: str,
    student_id: str,
    assessment_type: str = Query(..., description="Type of assessment to summarize"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get progress summary for a student in a class.
    
    This endpoint retrieves progress summary and recent records for a student.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student
        assessment_type: Type of assessment to summarize
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        ProgressSummaryResponse: The progress summary
    
    Raises:
        HTTPException: If retrieval fails or server error occurs
    """
    try:
        logger.info(f"Retrieving progress summary for student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_view_progress", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to view progress",
                    "required_permissions": ["can_view_progress"]
                }
            )
        
        # Generate cache key
        cache_key = f"progress_summary:{student_id}:{class_id}:{assessment_type}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached progress summary")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Get progress summary if not in cache
        result = await student_manager.get_progress_summary(student_id, class_id, assessment_type)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Progress records not found for student {student_id} in class {class_id}"
                }
            )
        
        # Cache the result for 1 hour
        await cache_manager.set(cache_key, result, expire=3600)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in progress summary retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Progress Report Models
class ProgressReportResponse(BaseModel):
    """Response model for progress reports."""
    student_id: str
    class_id: str
    report_date: datetime
    assessment_type: str
    overall_progress: float
    attendance_rate: float
    skill_improvements: Dict[str, float]
    fitness_improvements: Dict[str, float]
    behavior_improvements: Dict[str, float]
    recommendations: List[str]
    next_steps: List[str]
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-001",
                "class_id": "PE-2024-001",
                "report_date": "2024-03-15T00:00:00Z",
                "assessment_type": "Fitness Test",
                "overall_progress": 0.85,
                "attendance_rate": 0.95,
                "skill_improvements": {
                    "running": 0.15,
                    "jumping": 0.10,
                    "throwing": 0.20
                },
                "fitness_improvements": {
                    "endurance": 0.25,
                    "strength": 0.15,
                    "flexibility": 0.10
                },
                "behavior_improvements": {
                    "participation": 0.30,
                    "teamwork": 0.20,
                    "sportsmanship": 0.25
                },
                "recommendations": [
                    "Continue focusing on endurance training",
                    "Practice throwing technique"
                ],
                "next_steps": [
                    "Increase running distance gradually",
                    "Work on throwing accuracy"
                ],
                "created_at": "2024-03-15T10:00:00Z"
            }
        }
    )

class ProgressReportRequest(BaseModel):
    """Request model for generating progress reports."""
    assessment_type: str = Field(..., min_length=1, max_length=50)
    report_date: Optional[datetime] = None
    include_recommendations: bool = True
    include_next_steps: bool = True

    @validator('assessment_type')
    def validate_assessment_type(cls, v):
        valid_types = ['Fitness Test', 'Skill Assessment', 'Performance Test']
        if v not in valid_types:
            raise ValueError(f"Assessment type must be one of: {', '.join(valid_types)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assessment_type": "Fitness Test",
                "report_date": "2024-03-15T00:00:00Z",
                "include_recommendations": True,
                "include_next_steps": True
            }
        }
    )

# Progress Report Endpoints
@router.post(
    "/classes/{class_id}/progress/{student_id}/report",
    response_model=ProgressReportResponse,
    summary="Generate progress report",
    description="Generates a comprehensive progress report for a student",
    response_description="The generated progress report",
    responses={
        200: {"description": "Progress report generated successfully"},
        400: {"description": "Invalid report request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["reports"]["requests"], period=RATE_LIMIT["reports"]["period"])
async def generate_progress_report(
    class_id: str,
    student_id: str,
    request: ProgressReportRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Generate a progress report for a student.
    
    This endpoint generates a comprehensive progress report including
    attendance, skill improvements, fitness improvements, and recommendations.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student
        request: Progress report request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        ProgressReportResponse: The generated progress report
    
    Raises:
        HTTPException: If report generation fails or server error occurs
    """
    try:
        logger.info(f"Generating progress report for student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_generate_reports", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to generate reports",
                    "required_permissions": ["can_generate_reports"]
                }
            )
        
        # Generate cache key
        cache_key = f"progress_report:{student_id}:{class_id}:{request.assessment_type}:{request.report_date}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached progress report")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Generate progress report
        result = await student_manager.generate_progress_report(
            class_id=class_id,
            student_id=student_id,
            assessment_type=request.assessment_type,
            report_date=request.report_date or datetime.now(),
            include_recommendations=request.include_recommendations,
            include_next_steps=request.include_next_steps
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Progress data not found for student {student_id} in class {class_id}"
                }
            )
        
        # Cache the result for 24 hours
        await cache_manager.set(cache_key, result, expire=86400)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        logger.error(f"Validation error in progress report generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in progress report generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Student Recommendations Models
class StudentRecommendationResponse(BaseModel):
    """Response model for student recommendations."""
    student_id: str
    class_id: str
    recommendation_type: str
    recommendation_date: datetime
    current_status: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    implementation_plan: List[Dict[str, Any]]
    expected_outcomes: List[str]
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-001",
                "class_id": "PE-2024-001",
                "recommendation_type": "Skill Development",
                "recommendation_date": "2024-03-15T00:00:00Z",
                "current_status": {
                    "skill_level": "Intermediate",
                    "strengths": ["Endurance", "Teamwork"],
                    "areas_for_improvement": ["Throwing accuracy", "Flexibility"]
                },
                "recommendations": [
                    {
                        "area": "Throwing",
                        "suggestion": "Practice throwing technique daily",
                        "resources": ["Throwing guide", "Video tutorials"]
                    }
                ],
                "implementation_plan": [
                    {
                        "action": "Daily throwing practice",
                        "duration": "15 minutes",
                        "frequency": "5 times per week"
                    }
                ],
                "expected_outcomes": [
                    "Improved throwing accuracy by 20%",
                    "Increased confidence in throwing activities"
                ],
                "created_at": "2024-03-15T10:00:00Z"
            }
        }
    )

class StudentRecommendationRequest(BaseModel):
    """Request model for generating student recommendations."""
    recommendation_type: str = Field(..., min_length=1, max_length=50)
    recommendation_date: Optional[datetime] = None
    include_implementation_plan: bool = True
    include_expected_outcomes: bool = True

    @validator('recommendation_type')
    def validate_recommendation_type(cls, v):
        valid_types = ['Skill Development', 'Fitness Improvement', 'Behavior Modification']
        if v not in valid_types:
            raise ValueError(f"Recommendation type must be one of: {', '.join(valid_types)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommendation_type": "Skill Development",
                "recommendation_date": "2024-03-15T00:00:00Z",
                "include_implementation_plan": True,
                "include_expected_outcomes": True
            }
        }
    )

# Student Recommendations Endpoints
@router.post(
    "/classes/{class_id}/recommendations/{student_id}",
    response_model=StudentRecommendationResponse,
    summary="Generate student recommendations",
    description="Generates personalized recommendations for a student",
    response_description="The generated student recommendations",
    responses={
        200: {"description": "Recommendations generated successfully"},
        400: {"description": "Invalid recommendation request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Class or student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["recommendations"]["requests"], period=RATE_LIMIT["recommendations"]["period"])
async def generate_student_recommendations(
    class_id: str,
    student_id: str,
    request: StudentRecommendationRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Generate personalized recommendations for a student.
    
    This endpoint generates personalized recommendations based on the student's
    current performance, progress, and goals.
    
    Args:
        class_id: The ID of the class
        student_id: The ID of the student
        request: Recommendation request data
        token: Authentication token
        current_user: Currently authenticated user
    
    Returns:
        StudentRecommendationResponse: The generated recommendations
    
    Raises:
        HTTPException: If recommendation generation fails or server error occurs
    """
    try:
        logger.info(f"Generating recommendations for student {student_id} in class {class_id}")
        
        # Check user permissions
        if not current_user.get("can_generate_recommendations", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Authorization Error",
                    "message": "User not authorized to generate recommendations",
                    "required_permissions": ["can_generate_recommendations"]
                }
            )
        
        # Generate cache key
        cache_key = f"student_recommendations:{student_id}:{class_id}:{request.recommendation_type}:{request.recommendation_date}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached student recommendations")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )
        
        # Generate recommendations
        result = await student_manager.generate_recommendations(
            class_id=class_id,
            student_id=student_id,
            recommendation_type=request.recommendation_type,
            recommendation_date=request.recommendation_date or datetime.now(),
            include_implementation_plan=request.include_implementation_plan,
            include_expected_outcomes=request.include_expected_outcomes
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Student data not found for student {student_id} in class {class_id}"
                }
            )
        
        # Cache the result for 24 hours
        await cache_manager.set(cache_key, result, expire=86400)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        logger.error(f"Validation error in recommendation generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in recommendation generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Progress Note Models
class ProgressNoteResponse(BaseModel):
    """Response model for progress notes."""
    id: int
    content: str
    progress_id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProgressNoteRequest(BaseModel):
    """Request model for progress notes."""
    content: str
    progress_id: int
    teacher_id: int

@router.post("/progress/notes", response_model=ProgressNoteResponse)
async def create_progress_note(
    request: ProgressNoteRequest,
    db: Session = Depends(get_db)
):
    """Create a new progress note."""
    note = ProgressNote(**request.dict())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

# ... More endpoints to be added ... 