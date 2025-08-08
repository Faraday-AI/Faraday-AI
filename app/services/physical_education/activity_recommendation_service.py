from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from app.models.activity import (
    Activity,
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
# Define models locally to avoid circular imports
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ActivityRecommendationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: int = Field(..., description="ID of the student")
    class_id: int = Field(..., description="ID of the class")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Student preferences")
    limit: Optional[int] = Field(5, description="Maximum number of recommendations to return")

class ActivityRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Recommendation ID")
    student_id: int = Field(..., description="ID of the student")
    class_id: int = Field(..., description="ID of the class")
    activity_id: int = Field(..., description="ID of the recommended activity")
    recommendation_score: float = Field(..., description="Recommendation score (0.0 to 1.0)", ge=0.0, le=1.0)
    score_breakdown: Dict[str, float] = Field(..., description="Detailed breakdown of the recommendation score")
    created_at: datetime = Field(..., description="Timestamp of recommendation")

class ActivityRecommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_type: str = Field(..., description="Type of activity recommended")
    category: str = Field(..., description="Category of the activity")
    duration: int = Field(..., description="Recommended duration in minutes", gt=0)
    intensity: str = Field(..., description="Recommended intensity level")
    priority: str = Field(..., description="Priority of the recommendation")
    reason: str = Field(..., description="Reason for the recommendation")
    expected_improvement: float = Field(..., description="Expected improvement percentage", ge=0, le=100)
from app.services.physical_education.recommendation_engine import RecommendationEngine
from app.core.logging import get_logger
from app.models.physical_education.pe_enums.pe_types import (
    ActivityCategoryType
)

logger = get_logger(__name__)

class ActivityRecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.recommendation_engine = RecommendationEngine(db)
        self.logger = logger

    async def get_recommendations(
        self,
        request: ActivityRecommendationRequest,
        min_score: Optional[float] = None,
        max_duration: Optional[int] = None,
        exclude_recent: bool = False
    ) -> List[ActivityRecommendation]:
        """
        Get personalized activity recommendations for a student.
        
        Args:
            request: ActivityRecommendationRequest containing student_id, class_id, and preferences
            min_score: Optional minimum recommendation score (0.0 to 1.0)
            max_duration: Optional maximum activity duration in minutes
            exclude_recent: Whether to exclude recently recommended activities
            
        Returns:
            List of ActivityRecommendation objects sorted by recommendation score
        """
        try:
            # Get base recommendations
            recommendations = self.recommendation_engine.get_activity_recommendations(
                student_id=request.student_id,
                class_id=request.class_id,
                preferences=request.preferences,
                limit=None  # Get all recommendations to filter
            )
            
            # Apply filters
            filtered_recommendations = []
            for rec in recommendations:
                # Skip if below minimum score
                if min_score is not None and rec.recommendation_score < min_score:
                    continue
                    
                # Get activity details
                activity = self.db.query(Activity).filter(
                    Activity.id == rec.activity.id
                ).first()
                
                if not activity:
                    continue
                    
                # Skip if duration exceeds maximum
                if max_duration is not None and activity.duration_minutes > max_duration:
                    continue
                    
                # Skip if recently recommended
                if exclude_recent:
                    recent_recommendation = self.db.query(ActivityRecommendation).filter(
                        and_(
                            ActivityRecommendation.student_id == request.student_id,
                            ActivityRecommendation.activity_id == activity.id,
                            ActivityRecommendation.created_at >= datetime.now() - timedelta(days=7)
                        )
                    ).first()
                    if recent_recommendation:
                        continue
                        
                filtered_recommendations.append(rec)
            
            # Sort by score and return
            filtered_recommendations.sort(
                key=lambda x: x.recommendation_score,
                reverse=True
            )
            
            return filtered_recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while getting recommendations"
            )

    async def get_recommendation_history(
        self,
        student_id: int,
        class_id: Optional[int] = None,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_score: Optional[float] = None,
        activity_type: Optional[ActivityType] = None,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> List[ActivityRecommendation]:
        """
        Get historical activity recommendations for a student.
        
        Args:
            student_id: ID of the student
            class_id: Optional class ID to filter by
            limit: Maximum number of recommendations to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            min_score: Optional minimum recommendation score
            activity_type: Optional activity type to filter by
            difficulty_level: Optional difficulty level to filter by
            
        Returns:
            List of historical ActivityRecommendation objects
        """
        try:
            query = self.db.query(ActivityRecommendation).filter(
                ActivityRecommendation.student_id == student_id
            )
            
            if class_id:
                query = query.filter(ActivityRecommendation.class_id == class_id)
                
            if start_date:
                query = query.filter(ActivityRecommendation.created_at >= start_date)
                
            if end_date:
                query = query.filter(ActivityRecommendation.created_at <= end_date)
                
            if min_score is not None:
                query = query.filter(ActivityRecommendation.recommendation_score >= min_score)
                
            if activity_type or difficulty_level:
                query = query.join(Activity)
                
                if activity_type:
                    query = query.filter(Activity.activity_type == activity_type)
                    
                if difficulty_level:
                    query = query.filter(Activity.difficulty_level == difficulty_level)
            
            return query.order_by(
                desc(ActivityRecommendation.created_at)
            ).limit(limit).all()
            
        except Exception as e:
            self.logger.error(f"Error getting recommendation history: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while getting recommendation history"
            )

    async def clear_recommendations(
        self,
        student_id: int,
        class_id: Optional[int] = None,
        before_date: Optional[datetime] = None
    ) -> bool:
        """
        Clear stored recommendations for a student.
        
        Args:
            student_id: ID of the student
            class_id: Optional class ID to filter by
            before_date: Optional date to clear recommendations before
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = self.db.query(ActivityRecommendation).filter(
                ActivityRecommendation.student_id == student_id
            )
            
            if class_id:
                query = query.filter(ActivityRecommendation.class_id == class_id)
                
            if before_date:
                query = query.filter(ActivityRecommendation.created_at <= before_date)
                
            query.delete()
            self.db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing recommendations: {str(e)}")
            self.db.rollback()
            return False

    async def get_category_recommendations(
        self,
        student_id: int,
        class_id: int,
        category_id: int,
        activity_type: Optional[ActivityType] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        min_score: Optional[float] = None,
        max_duration: Optional[int] = None,
        exclude_recent: bool = False,
        limit: int = 5
    ) -> List[ActivityRecommendation]:
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
            limit: Maximum number of recommendations to return
            
        Returns:
            List of ActivityRecommendation objects for the specified category
        """
        try:
            # Get base recommendations
            recommendations = self.recommendation_engine.get_activity_recommendations(
                student_id=student_id,
                class_id=class_id,
                limit=None  # Get all recommendations to filter
            )
            
            # Filter by category and additional criteria
            filtered_recommendations = []
            for rec in recommendations:
                activity = self.db.query(Activity).filter(
                    Activity.id == rec.activity.id
                ).first()
                
                if not activity:
                    continue
                    
                # Check if activity belongs to the category
                category_match = self.db.query(ActivityCategory).filter(
                    and_(
                        ActivityCategory.activity_id == activity.id,
                        ActivityCategory.category_id == category_id
                    )
                ).first()
                
                if not category_match:
                    continue
                    
                # Apply additional filters
                if activity_type and activity.activity_type != activity_type:
                    continue
                    
                if difficulty_level and activity.difficulty_level != difficulty_level:
                    continue
                    
                if min_score is not None and rec.recommendation_score < min_score:
                    continue
                    
                if max_duration is not None and activity.duration_minutes > max_duration:
                    continue
                    
                if exclude_recent:
                    recent_recommendation = self.db.query(ActivityRecommendation).filter(
                        and_(
                            ActivityRecommendation.student_id == student_id,
                            ActivityRecommendation.activity_id == activity.id,
                            ActivityRecommendation.created_at >= datetime.now() - timedelta(days=7)
                        )
                    ).first()
                    if recent_recommendation:
                        continue
                        
                filtered_recommendations.append(rec)
            
            # Sort and limit results
            filtered_recommendations.sort(
                key=lambda x: x.recommendation_score,
                reverse=True
            )
            
            return filtered_recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting category recommendations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while getting category recommendations"
            )

    async def get_balanced_recommendations(
        self,
        student_id: int,
        class_id: int,
        min_score: Optional[float] = None,
        max_duration: Optional[int] = None,
        exclude_recent: bool = False,
        activity_types: Optional[List[ActivityType]] = None,
        difficulty_levels: Optional[List[DifficultyLevel]] = None,
        limit: int = 5
    ) -> List[ActivityRecommendation]:
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
            limit: Maximum number of recommendations to return
            
        Returns:
            List of ActivityRecommendation objects balanced across categories
        """
        try:
            # Get base recommendations
            recommendations = self.recommendation_engine.get_activity_recommendations(
                student_id=student_id,
                class_id=class_id,
                limit=None  # Get all recommendations to balance
            )
            
            # Apply filters
            filtered_recommendations = []
            for rec in recommendations:
                activity = self.db.query(Activity).filter(
                    Activity.id == rec.activity.id
                ).first()
                
                if not activity:
                    continue
                    
                # Apply filters
                if min_score is not None and rec.recommendation_score < min_score:
                    continue
                    
                if max_duration is not None and activity.duration_minutes > max_duration:
                    continue
                    
                if activity_types and activity.activity_type not in activity_types:
                    continue
                    
                if difficulty_levels and activity.difficulty_level not in difficulty_levels:
                    continue
                    
                if exclude_recent:
                    recent_recommendation = self.db.query(ActivityRecommendation).filter(
                        and_(
                            ActivityRecommendation.student_id == student_id,
                            ActivityRecommendation.activity_id == activity.id,
                            ActivityRecommendation.created_at >= datetime.now() - timedelta(days=7)
                        )
                    ).first()
                    if recent_recommendation:
                        continue
                        
                filtered_recommendations.append(rec)
            
            # Group recommendations by category
            category_recommendations = {}
            for rec in filtered_recommendations:
                activity = self.db.query(Activity).filter(
                    Activity.id == rec.activity.id
                ).first()
                
                if not activity:
                    continue
                    
                # Get activity categories
                categories = self.db.query(ActivityCategory).filter(
                    ActivityCategory.activity_id == activity.id
                ).all()
                
                for category in categories:
                    if category.category_id not in category_recommendations:
                        category_recommendations[category.category_id] = []
                    category_recommendations[category.category_id].append(rec)
            
            # Select top recommendations from each category
            balanced_recommendations = []
            for category_id, recs in category_recommendations.items():
                # Sort recommendations by score
                recs.sort(key=lambda x: x.recommendation_score, reverse=True)
                # Take top recommendation from each category
                if recs:
                    balanced_recommendations.append(recs[0])
            
            # Sort all recommendations by score and limit
            balanced_recommendations.sort(
                key=lambda x: x.recommendation_score,
                reverse=True
            )
            
            return balanced_recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting balanced recommendations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while getting balanced recommendations"
            ) 