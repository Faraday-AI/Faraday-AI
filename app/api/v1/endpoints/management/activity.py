from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import os
from app.api.v1.models.activity import (
    ActivityData,
    ActivityResponse,
    ActivityStatusUpdate,
    BatchActivityRequest,
    ProgressResponse,
    ScheduleResponse,
    ActivityListResponse
)
from app.api.v1.middleware.auth import oauth2_scheme, get_current_active_user
from app.api.v1.middleware.rate_limiter import rate_limiter
from app.services.physical_education.activity_manager import ActivityManager
from app.services.physical_education.activity_analysis_manager import ActivityAnalysisManager
from app.services.physical_education.activity_visualization_manager import ActivityVisualizationManager
from app.services.physical_education.activity_export_manager import ActivityExportManager
from app.services.physical_education.activity_collaboration_manager import ActivityCollaborationManager
from app.services.physical_education.activity_adaptation_manager import ActivityAdaptationManager
from app.services.physical_education.activity_assessment_manager import ActivityAssessmentManager
from app.services.physical_education.activity_security_manager import ActivitySecurityManager
from app.services.physical_education.activity_cache_manager import ActivityCacheManager
from app.services.physical_education.activity_rate_limit_manager import ActivityRateLimitManager
from app.services.physical_education.activity_circuit_breaker_manager import ActivityCircuitBreakerManager

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/activity",
    tags=["activity"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# Initialize managers
activity_manager = ActivityManager()
analysis_manager = ActivityAnalysisManager()
visualization_manager = ActivityVisualizationManager()
export_manager = ActivityExportManager()
adaptation_manager = ActivityAdaptationManager()
assessment_manager = ActivityAssessmentManager()
collaboration_manager = ActivityCollaborationManager()
security_manager = ActivitySecurityManager()
cache_manager = ActivityCacheManager()
rate_limit_manager = ActivityRateLimitManager()
circuit_breaker_manager = ActivityCircuitBreakerManager()

# Rate limiting configuration
RATE_LIMITS = {
    "create_activity": {"max_requests": 10, "time_window": 60},
    "get_activities": {"max_requests": 20, "time_window": 60},
    "batch_activities": {"max_requests": 5, "time_window": 60},
    "update_status": {"max_requests": 15, "time_window": 60},
    "get_progress": {"max_requests": 10, "time_window": 60},
    "get_schedule": {"max_requests": 10, "time_window": 60},
    "analyze_activity": {"max_requests": 5, "time_window": 60},
    "visualize_activity": {"max_requests": 5, "time_window": 60},
    "export_activity": {"max_requests": 3, "time_window": 60},
    "collaborate_activity": {"max_requests": 10, "time_window": 60}
}

# Cache configuration
CACHE_TTL = {
    "activity": 300,  # 5 minutes
    "progress": 600,  # 10 minutes
    "schedule": 300,  # 5 minutes
    "analysis": 900,  # 15 minutes
    "visualization": 900,  # 15 minutes
    "export": 1800,  # 30 minutes
    "collaboration": 300  # 5 minutes
}

@router.post(
    "/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity",
    description="Creates a new activity record with the provided data",
    response_description="The created activity record"
)
@rate_limiter(limit=RATE_LIMITS["create_activity"]["max_requests"], 
              window=RATE_LIMITS["create_activity"]["time_window"])
async def create_activity(
    activity: ActivityData,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity record."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("create_activity"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create activities"
            )

        # Create activity
        result = await activity_manager.create_activity(
            student_id=activity.student_id,
            date=activity.date,
            score=activity.score,
            category=activity.category,
            activity_type=activity.activity_type,
            duration=activity.duration,
            intensity=activity.intensity,
            notes=activity.notes,
            created_by=current_user.id
        )

        # Invalidate relevant caches
        await cache_manager.invalidate_pattern(f"activity:{activity.student_id}:*")
        await cache_manager.invalidate_pattern(f"progress:{activity.student_id}:*")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error creating activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the activity: {str(e)}"
        )

@router.get(
    "/activities/{student_id}",
    response_model=List[ActivityResponse],
    summary="Get activities for a student",
    description="Retrieves activities for a specific student with optional filters",
    response_description="List of activities matching the criteria"
)
@rate_limiter(limit=RATE_LIMITS["get_activities"]["max_requests"], 
              window=RATE_LIMITS["get_activities"]["time_window"])
async def get_activities(
    student_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activities for a student with optional filters."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("view_activities"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view activities"
            )

        # Generate cache key
        cache_key = f"activity:{student_id}:{start_date}:{end_date}:{category}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Get activities
        result = await activity_manager.get_activities(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            category=category
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["activity"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error getting activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving activities: {str(e)}"
        )

@router.post(
    "/activities/batch",
    response_model=List[ActivityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple activities",
    description="Creates multiple activity records in a single request",
    response_description="List of created activity records"
)
@rate_limiter(limit=RATE_LIMITS["batch_activities"]["max_requests"], 
              window=RATE_LIMITS["batch_activities"]["time_window"])
async def create_batch_activities(
    request: BatchActivityRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create multiple activity records."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("create_activity"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create activities"
            )

        # Process activities in batches to prevent overload
        batch_size = 10
        results = []
        student_ids = set()

        for i in range(0, len(request.activities), batch_size):
            batch = request.activities[i:i + batch_size]
            for activity in batch:
                result = await activity_manager.create_activity(
                    student_id=activity.student_id,
                    date=activity.date,
                    score=activity.score,
                    category=activity.category,
                    activity_type=activity.activity_type,
                    duration=activity.duration,
                    intensity=activity.intensity,
                    notes=activity.notes,
                    created_by=current_user.id
                )
                results.append(result)
                student_ids.add(activity.student_id)

        # Invalidate caches for all affected students
        for student_id in student_ids:
            await cache_manager.invalidate_pattern(f"activity:{student_id}:*")
            await cache_manager.invalidate_pattern(f"progress:{student_id}:*")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(results)
        )

    except ValueError as e:
        logger.error(f"Validation error creating batch activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating batch activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating activities: {str(e)}"
        )

@router.patch(
    "/activities/{activity_id}/status",
    response_model=ActivityResponse,
    summary="Update activity status",
    description="Updates the status of an existing activity",
    response_description="The updated activity record"
)
@rate_limiter(limit=RATE_LIMITS["update_status"]["max_requests"], 
              window=RATE_LIMITS["update_status"]["time_window"])
async def update_activity_status(
    activity_id: str,
    status_update: ActivityStatusUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update the status of an activity."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("update_activity"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update activities"
            )

        # Get current activity to check ownership
        current_activity = await activity_manager.get_activity(activity_id)
        if not current_activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )

        # Check if user has permission to update this activity
        if not current_user.has_permission("update_any_activity") and current_activity.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update activities you created"
            )

        # Update activity status
        result = await activity_manager.update_activity_status(
            activity_id=activity_id,
            status=status_update.status,
            notes=status_update.notes,
            updated_by=current_user.id
        )

        # Invalidate relevant caches
        await cache_manager.invalidate_pattern(f"activity:{result.student_id}:*")
        await cache_manager.invalidate_pattern(f"progress:{result.student_id}:*")
        await cache_manager.invalidate(f"activity:{activity_id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error updating activity status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating activity status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the activity status: {str(e)}"
        )

@router.get(
    "/activities/{student_id}/progress",
    response_model=ProgressResponse,
    summary="Get activity progress",
    description="Retrieves progress information for a student's activities",
    response_description="Progress information and recommendations"
)
@rate_limiter(limit=RATE_LIMITS["get_progress"]["max_requests"], 
              window=RATE_LIMITS["get_progress"]["time_window"])
async def get_activity_progress(
    student_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get progress information for a student's activities."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("view_progress"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view progress"
            )

        # Generate cache key
        cache_key = f"progress:{student_id}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Get progress information
        result = await activity_manager.get_activity_progress(
            student_id=student_id
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["progress"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error getting progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving progress: {str(e)}"
        )

@router.get(
    "/activities/{student_id}/schedule",
    response_model=List[ScheduleResponse],
    summary="Get activity schedule",
    description="Retrieves scheduled activities for a student",
    response_description="List of scheduled activities"
)
@rate_limiter(limit=RATE_LIMITS["get_schedule"]["max_requests"], 
              window=RATE_LIMITS["get_schedule"]["time_window"])
async def get_activity_schedule(
    student_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get scheduled activities for a student."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("view_schedule"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view schedule"
            )

        # Generate cache key
        cache_key = f"schedule:{student_id}:{start_date}:{end_date}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Get schedule
        result = await activity_manager.get_activity_schedule(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["schedule"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error getting schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving schedule: {str(e)}"
        )

@router.get(
    "/activities/{student_id}/analysis",
    response_model=Dict[str, Any],
    summary="Analyze activity data",
    description="Performs detailed analysis of a student's activity data",
    response_description="Analysis results including trends, patterns, and insights"
)
@rate_limiter(limit=RATE_LIMITS["analyze_activity"]["max_requests"], 
              window=RATE_LIMITS["analyze_activity"]["time_window"])
async def analyze_activity(
    student_id: str,
    analysis_type: str = Query(..., description="Type of analysis to perform"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Analyze a student's activity data."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("analyze_activities"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to analyze activities"
            )

        # Generate cache key
        cache_key = f"analysis:{student_id}:{analysis_type}:{start_date}:{end_date}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Perform analysis
        result = await analysis_manager.analyze_activities(
            student_id=student_id,
            analysis_type=analysis_type,
            start_date=start_date,
            end_date=end_date
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["analysis"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error analyzing activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error analyzing activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing activities: {str(e)}"
        )

@router.get(
    "/activities/{student_id}/visualization",
    response_model=Dict[str, Any],
    summary="Visualize activity data",
    description="Generates visualizations of a student's activity data",
    response_description="Visualization data in various formats"
)
@rate_limiter(limit=RATE_LIMITS["visualize_activity"]["max_requests"], 
              window=RATE_LIMITS["visualize_activity"]["time_window"])
async def visualize_activity(
    student_id: str,
    visualization_type: str = Query(..., description="Type of visualization to generate"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query("json", description="Output format (json, png, svg)"),
    token: str = Depends(oauth2_scheme)
):
    """Generate visualizations of a student's activity data."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("visualize_activities"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to visualize activities"
            )

        # Generate cache key
        cache_key = f"visualization:{student_id}:{visualization_type}:{start_date}:{end_date}:{format}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Generate visualization
        result = await visualization_manager.generate_visualization(
            student_id=student_id,
            visualization_type=visualization_type,
            start_date=start_date,
            end_date=end_date,
            format=format
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["visualization"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error generating visualization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating visualization: {str(e)}"
        )

@router.get(
    "/activities/{student_id}/export",
    response_model=Dict[str, Any],
    summary="Export activity data",
    description="Exports a student's activity data in various formats",
    response_description="Exported data in the requested format"
)
@rate_limiter(limit=RATE_LIMITS["export_activity"]["max_requests"], 
              window=RATE_LIMITS["export_activity"]["time_window"])
async def export_activity(
    student_id: str,
    export_type: str = Query(..., description="Type of export to generate"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query("json", description="Output format (json, csv, pdf)"),
    token: str = Depends(oauth2_scheme)
):
    """Export a student's activity data."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("export_activities"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to export activities"
            )

        # Generate cache key
        cache_key = f"export:{student_id}:{export_type}:{start_date}:{end_date}:{format}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Generate export
        result = await export_manager.generate_export(
            student_id=student_id,
            export_type=export_type,
            start_date=start_date,
            end_date=end_date,
            format=format
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["export"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error generating export: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating export: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating export: {str(e)}"
        )

@router.post(
    "/activities/{student_id}/collaborate",
    response_model=Dict[str, Any],
    summary="Collaborate on activity data",
    description="Enables collaboration features for a student's activity data",
    response_description="Collaboration status and results"
)
@rate_limiter(limit=RATE_LIMITS["collaborate_activity"]["max_requests"], 
              window=RATE_LIMITS["collaborate_activity"]["time_window"])
async def collaborate_activity(
    student_id: str,
    collaboration_type: str = Query(..., description="Type of collaboration to perform"),
    collaborators: List[str] = Query(..., description="List of collaborator IDs"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Enable collaboration on a student's activity data."""
    try:
        # Get current user
        current_user = await get_current_active_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Check permissions
        if not current_user.has_permission("collaborate_activities"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to collaborate on activities"
            )

        # Generate cache key
        cache_key = f"collaboration:{student_id}:{collaboration_type}:{start_date}:{end_date}"

        # Try to get from cache
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(cached_result)
            )

        # Enable collaboration
        result = await collaboration_manager.enable_collaboration(
            student_id=student_id,
            collaboration_type=collaboration_type,
            collaborators=collaborators,
            start_date=start_date,
            end_date=end_date,
            initiated_by=current_user.id
        )

        # Cache the result
        await cache_manager.set(cache_key, result, ttl=CACHE_TTL["collaboration"])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )

    except ValueError as e:
        logger.error(f"Validation error enabling collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error enabling collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while enabling collaboration: {str(e)}"
        ) 