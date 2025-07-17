from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator

from app.db.session import get_db
from app.api.v1.models.activity import (
    ActivityRecommendationRequest,
    ActivityRecommendationResponse,
    ActivityType,
    DifficultyLevel
)
from app.services.physical_education.activity_recommendation_service import ActivityRecommendationService

router = APIRouter()

class ActivityRecommendationRequestExample(BaseModel):
    student_id: int = Field(..., example=1, description="ID of the student")
    class_id: int = Field(..., example=1, description="ID of the class")
    preferences: dict = Field(
        ...,
        example={
            "difficulty_level": "intermediate",
            "activity_types": ["strength", "cardio"],
            "duration_minutes": 30
        },
        description="Student's activity preferences"
    )

class ActivityRecommendationResponseExample(BaseModel):
    id: int = Field(..., example=1, description="Recommendation ID")
    student_id: int = Field(..., example=1, description="ID of the student")
    class_id: int = Field(..., example=1, description="ID of the class")
    activity_id: int = Field(..., example=1, description="ID of the recommended activity")
    recommendation_score: float = Field(..., example=0.85, description="Recommendation score (0.0 to 1.0)")
    score_breakdown: dict = Field(
        ...,
        example={
            "skill_match": 0.9,
            "fitness_match": 0.8,
            "preference_match": 0.85
        },
        description="Detailed breakdown of the recommendation score"
    )
    created_at: datetime = Field(..., example="2024-04-01T12:00:00Z", description="Timestamp of recommendation")

@router.post(
    "/recommendations",
    response_model=List[ActivityRecommendationResponse],
    summary="Get personalized activity recommendations",
    description="""
    Get personalized activity recommendations for a student based on their preferences and class requirements.
    
    Additional filtering options:
    - min_score: Minimum recommendation score (0.0 to 1.0)
    - max_duration: Maximum activity duration in minutes
    - exclude_recent: Exclude activities that were recently recommended
    
    Example Request:
    ```json
    {
        "student_id": 1,
        "class_id": 1,
        "preferences": {
            "difficulty_level": "intermediate",
            "activity_types": ["strength", "cardio"],
            "duration_minutes": 30
        }
    }
    ```
    
    Example Response:
    ```json
    [
        {
            "id": 1,
            "student_id": 1,
            "class_id": 1,
            "activity_id": 1,
            "recommendation_score": 0.85,
            "score_breakdown": {
                "skill_match": 0.9,
                "fitness_match": 0.8,
                "preference_match": 0.85
            },
            "created_at": "2024-04-01T12:00:00Z"
        }
    ]
    ```
    """,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "student_id": 1,
                            "class_id": 1,
                            "activity_id": 1,
                            "recommendation_score": 0.85,
                            "score_breakdown": {
                                "skill_match": 0.9,
                                "fitness_match": 0.8,
                                "preference_match": 0.85
                            },
                            "created_at": "2024-04-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Student or class not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Student or class not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "An error occurred while getting recommendations"}
                }
            }
        }
    }
)
async def get_activity_recommendations(
    request: ActivityRecommendationRequest = Body(..., example={
        "student_id": 1,
        "class_id": 1,
        "preferences": {
            "difficulty_level": "intermediate",
            "activity_types": ["strength", "cardio"],
            "duration_minutes": 30
        }
    }),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum recommendation score (0.0 to 1.0)"),
    max_duration: Optional[int] = Query(None, gt=0, description="Maximum activity duration in minutes"),
    exclude_recent: bool = Query(False, description="Exclude activities that were recently recommended"),
    db: Session = Depends(get_db)
):
    """
    Get personalized activity recommendations for a student.
    
    Args:
        request: ActivityRecommendationRequest containing student_id, class_id, and preferences
        min_score: Optional minimum recommendation score (0.0 to 1.0)
        max_duration: Optional maximum activity duration in minutes
        exclude_recent: Whether to exclude recently recommended activities
        
    Returns:
        List of ActivityRecommendationResponse objects sorted by recommendation score
    """
    service = ActivityRecommendationService(db)
    return await service.get_recommendations(
        request.student_id,
        request.class_id,
        request.preferences,
        min_score=min_score,
        max_duration=max_duration,
        exclude_recent=exclude_recent
    )

@router.get(
    "/recommendations/history/{student_id}",
    response_model=List[ActivityRecommendationResponse],
    summary="Get recommendation history",
    description="""
    Get historical activity recommendations for a student.
    
    Additional filtering options:
    - start_date: Filter recommendations after this date
    - end_date: Filter recommendations before this date
    - min_score: Minimum recommendation score (0.0 to 1.0)
    - activity_type: Filter by specific activity type
    - difficulty_level: Filter by difficulty level
    
    Example Response:
    ```json
    [
        {
            "id": 1,
            "student_id": 1,
            "class_id": 1,
            "activity_id": 1,
            "recommendation_score": 0.85,
            "score_breakdown": {
                "skill_match": 0.9,
                "fitness_match": 0.8,
                "preference_match": 0.85
            },
            "created_at": "2024-04-01T12:00:00Z"
        }
    ]
    ```
    """,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "student_id": 1,
                            "class_id": 1,
                            "activity_id": 1,
                            "recommendation_score": 0.85,
                            "score_breakdown": {
                                "skill_match": 0.9,
                                "fitness_match": 0.8,
                                "preference_match": 0.85
                            },
                            "created_at": "2024-04-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Student not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Student not found"}
                }
            }
        }
    }
)
async def get_recommendation_history(
    student_id: int,
    class_id: Optional[int] = Query(None, description="Optional class ID to filter by", example=1),
    start_date: Optional[datetime] = Query(None, description="Filter recommendations after this date", example="2024-04-01T00:00:00Z"),
    end_date: Optional[datetime] = Query(None, description="Filter recommendations before this date", example="2024-04-30T23:59:59Z"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum recommendation score (0.0 to 1.0)", example=0.8),
    activity_type: Optional[ActivityType] = Query(None, description="Filter by specific activity type", example=ActivityType.STRENGTH),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level", example=DifficultyLevel.INTERMEDIATE),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """
    Get historical activity recommendations for a student.
    
    Args:
        student_id: ID of the student
        class_id: Optional class ID to filter by
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        min_score: Optional minimum recommendation score
        activity_type: Optional activity type to filter by
        difficulty_level: Optional difficulty level to filter by
        limit: Maximum number of recommendations to return
        
    Returns:
        List of historical ActivityRecommendationResponse objects
    """
    service = ActivityRecommendationService(db)
    return await service.get_recommendation_history(
        student_id,
        class_id=class_id,
        start_date=start_date,
        end_date=end_date,
        min_score=min_score,
        activity_type=activity_type,
        difficulty_level=difficulty_level,
        limit=limit
    )

@router.delete(
    "/recommendations/{student_id}",
    summary="Clear recommendations",
    description="""
    Clear stored recommendations for a student.
    
    Additional filtering options:
    - class_id: Clear recommendations for a specific class
    - before_date: Clear recommendations before this date
    
    Example Response:
    ```json
    {
        "message": "Recommendations cleared successfully"
    }
    ```
    """,
    responses={
        200: {
            "description": "Recommendations cleared successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Recommendations cleared successfully"}
                }
            }
        },
        404: {
            "description": "Student not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Student not found"}
                }
            }
        }
    }
)
async def clear_recommendations(
    student_id: int,
    class_id: Optional[int] = Query(None, description="Optional class ID to filter by", example=1),
    before_date: Optional[datetime] = Query(None, description="Clear recommendations before this date", example="2024-04-01T00:00:00Z"),
    db: Session = Depends(get_db)
):
    """
    Clear stored recommendations for a student.
    
    Args:
        student_id: ID of the student
        class_id: Optional class ID to filter by
        before_date: Optional date to clear recommendations before
        
    Returns:
        Success message
    """
    service = ActivityRecommendationService(db)
    success = await service.clear_recommendations(
        student_id,
        class_id=class_id,
        before_date=before_date
    )
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to clear recommendations"
        )
    return {"message": "Recommendations cleared successfully"}

@router.get(
    "/recommendations/category/{student_id}/{class_id}/{category_id}",
    response_model=List[ActivityRecommendationResponse],
    summary="Get category recommendations",
    description="""
    Get activity recommendations based on a specific category.
    
    Additional filtering options:
    - activity_type: Filter by specific activity type
    - difficulty_level: Filter by difficulty level
    - min_score: Minimum recommendation score (0.0 to 1.0)
    - max_duration: Maximum activity duration in minutes
    - exclude_recent: Exclude activities that were recently recommended
    
    Example Response:
    ```json
    [
        {
            "id": 1,
            "student_id": 1,
            "class_id": 1,
            "activity_id": 1,
            "recommendation_score": 0.85,
            "score_breakdown": {
                "skill_match": 0.9,
                "fitness_match": 0.8,
                "preference_match": 0.85
            },
            "created_at": "2024-04-01T12:00:00Z"
        }
    ]
    ```
    """,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "student_id": 1,
                            "class_id": 1,
                            "activity_id": 1,
                            "recommendation_score": 0.85,
                            "score_breakdown": {
                                "skill_match": 0.9,
                                "fitness_match": 0.8,
                                "preference_match": 0.85
                            },
                            "created_at": "2024-04-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Student, class, or category not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Student, class, or category not found"}
                }
            }
        }
    }
)
async def get_category_recommendations(
    student_id: int,
    class_id: int,
    category_id: int,
    activity_type: Optional[ActivityType] = Query(None, description="Filter by specific activity type", example=ActivityType.STRENGTH),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level", example=DifficultyLevel.INTERMEDIATE),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum recommendation score (0.0 to 1.0)", example=0.8),
    max_duration: Optional[int] = Query(None, gt=0, description="Maximum activity duration in minutes", example=30),
    exclude_recent: bool = Query(False, description="Exclude activities that were recently recommended"),
    db: Session = Depends(get_db)
):
    """
    Get activity recommendations for a specific category.
    
    Args:
        student_id: ID of the student
        class_id: ID of the class
        category_id: ID of the activity category
        activity_type: Optional activity type to filter by
        difficulty_level: Optional difficulty level to filter by
        min_score: Optional minimum recommendation score
        max_duration: Optional maximum activity duration
        exclude_recent: Whether to exclude recently recommended activities
        
    Returns:
        List of ActivityRecommendationResponse objects for the specified category
    """
    service = ActivityRecommendationService(db)
    return await service.get_category_recommendations(
        student_id,
        class_id,
        category_id,
        activity_type=activity_type,
        difficulty_level=difficulty_level,
        min_score=min_score,
        max_duration=max_duration,
        exclude_recent=exclude_recent
    )

@router.get(
    "/recommendations/balanced/{student_id}/{class_id}",
    response_model=List[ActivityRecommendationResponse],
    summary="Get balanced recommendations",
    description="""
    Get a balanced set of recommendations across different categories.
    
    Additional filtering options:
    - min_score: Minimum recommendation score (0.0 to 1.0)
    - max_duration: Maximum activity duration in minutes
    - exclude_recent: Exclude activities that were recently recommended
    - activity_types: Filter by specific activity types
    - difficulty_levels: Filter by specific difficulty levels
    
    Example Response:
    ```json
    [
        {
            "id": 1,
            "student_id": 1,
            "class_id": 1,
            "activity_id": 1,
            "recommendation_score": 0.85,
            "score_breakdown": {
                "skill_match": 0.9,
                "fitness_match": 0.8,
                "preference_match": 0.85
            },
            "created_at": "2024-04-01T12:00:00Z"
        }
    ]
    ```
    """,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "student_id": 1,
                            "class_id": 1,
                            "activity_id": 1,
                            "recommendation_score": 0.85,
                            "score_breakdown": {
                                "skill_match": 0.9,
                                "fitness_match": 0.8,
                                "preference_match": 0.85
                            },
                            "created_at": "2024-04-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Student or class not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Student or class not found"}
                }
            }
        }
    }
)
async def get_balanced_recommendations(
    student_id: int,
    class_id: int,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum recommendation score (0.0 to 1.0)", example=0.8),
    max_duration: Optional[int] = Query(None, gt=0, description="Maximum activity duration in minutes", example=30),
    exclude_recent: bool = Query(False, description="Exclude activities that were recently recommended"),
    activity_types: Optional[List[ActivityType]] = Query(None, description="Filter by specific activity types", example=[ActivityType.STRENGTH, ActivityType.CARDIO]),
    difficulty_levels: Optional[List[DifficultyLevel]] = Query(None, description="Filter by specific difficulty levels", example=[DifficultyLevel.INTERMEDIATE]),
    db: Session = Depends(get_db)
):
    """
    Get a balanced set of recommendations across different categories.
    
    Args:
        student_id: ID of the student
        class_id: ID of the class
        min_score: Optional minimum recommendation score
        max_duration: Optional maximum activity duration
        exclude_recent: Whether to exclude recently recommended activities
        activity_types: Optional list of activity types to include
        difficulty_levels: Optional list of difficulty levels to include
        
    Returns:
        List of ActivityRecommendationResponse objects balanced across categories
    """
    service = ActivityRecommendationService(db)
    return await service.get_balanced_recommendations(
        student_id,
        class_id,
        min_score=min_score,
        max_duration=max_duration,
        exclude_recent=exclude_recent,
        activity_types=activity_types,
        difficulty_levels=difficulty_levels
    ) 