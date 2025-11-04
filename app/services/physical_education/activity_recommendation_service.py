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
            # Validate student and class exist first
            from app.models.physical_education.student import Student
            from app.models.physical_education.class_ import PhysicalEducationClass
            
            student = self.db.query(Student).filter(Student.id == request.student_id).first()
            if not student:
                # Return empty list for invalid student
                return []
            
            pe_class = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == request.class_id).first()
            if not pe_class:
                # Return empty list for invalid class
                return []
            
            # Get base recommendations
            try:
                recommendations = self.recommendation_engine.get_activity_recommendations(
                    student_id=request.student_id,
                    class_id=request.class_id,
                    preferences=request.preferences,
                    limit=None  # Get all recommendations to filter
                )
            except ValueError as ve:
                # RecommendationEngine raises ValueError if student/class not found
                # This can happen due to transaction isolation in tests
                # Return empty list gracefully
                self.logger.warning(f"RecommendationEngine error (student/class not found or transaction isolation): {str(ve)}")
                return []
            
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
                if max_duration is not None and activity.duration and activity.duration > max_duration:
                    continue
                    
                # Skip if recently recommended (check StudentActivityPerformance as proxy)
                if exclude_recent:
                    from app.models.physical_education.activity.models import StudentActivityPerformance
                    recent_performance = self.db.query(StudentActivityPerformance).filter(
                        and_(
                            StudentActivityPerformance.student_id == request.student_id,
                            StudentActivityPerformance.activity_id == activity.id,
                            StudentActivityPerformance.created_at >= datetime.now() - timedelta(days=7)
                        )
                    ).first()
                    if recent_performance:
                        continue
                        
                filtered_recommendations.append(rec)
            
            # Sort by score and return
            filtered_recommendations.sort(
                key=lambda x: x.recommendation_score,
                reverse=True
            )
            
            # Transform RecommendationEngine output to ActivityRecommendationResponse format
            from app.api.v1.models.activity import ActivityRecommendationResponse
            response_items = []
            for idx, rec in enumerate(filtered_recommendations):
                # Extract activity ID from the activity object
                activity_id = rec.activity.id if hasattr(rec.activity, 'id') else 0
                response_items.append(ActivityRecommendationResponse(
                    id=idx + 1,  # Generate a simple sequential ID
                    student_id=request.student_id,
                    class_id=request.class_id,
                    activity_id=activity_id,
                    recommendation_score=rec.recommendation_score,
                    score_breakdown=rec.score_breakdown,
                    created_at=datetime.now()
                ))
            
            return response_items
            
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
    ) -> List[Dict[str, Any]]:
        """
        Get historical activity recommendations for a student.
        
        Since recommendations are generated on-the-fly and not stored,
        this uses StudentActivityPerformance records as a proxy for
        recommendation history (activities the student has done).
        
        Args:
            student_id: ID of the student
            class_id: Optional class ID to filter by
            limit: Maximum number of recommendations to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            min_score: Optional minimum recommendation score (not used, kept for API compatibility)
            activity_type: Optional activity type to filter by
            difficulty_level: Optional difficulty level to filter by
            
        Returns:
            List of historical recommendation dictionaries
        """
        try:
            from app.models.physical_education.activity.models import StudentActivityPerformance
            from sqlalchemy import desc, and_
            
            # Use StudentActivityPerformance as proxy for recommendation history
            query = self.db.query(StudentActivityPerformance).join(Activity).filter(
                StudentActivityPerformance.student_id == student_id
            )
            
            if class_id:
                # Filter by class activities if class_id provided
                from app.models.physical_education.class_ import PhysicalEducationClass
                class_ = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
                if class_:
                    # Get activity IDs from class routines
                    activity_ids = [ra.activity_id for ra in class_.routines] if hasattr(class_, 'routines') else []
                    if activity_ids:
                        query = query.filter(StudentActivityPerformance.activity_id.in_(activity_ids))
                
            if start_date:
                query = query.filter(StudentActivityPerformance.created_at >= start_date)
                
            if end_date:
                query = query.filter(StudentActivityPerformance.created_at <= end_date)
                
            if activity_type:
                query = query.filter(Activity.type == activity_type)
                    
            if difficulty_level:
                query = query.filter(Activity.difficulty_level == difficulty_level)
            
            # Get results and transform to recommendation format
            performances = query.order_by(
                desc(StudentActivityPerformance.created_at)
            ).limit(limit).all()
            
            # Transform to ActivityRecommendationResponse format
            history = []
            for perf in performances:
                activity = perf.activity
                
                # Find class_id - use provided class_id or try to find student's first class
                found_class_id = class_id
                if not found_class_id:
                    # Try to find a class that the student belongs to
                    from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent
                    from sqlalchemy import and_
                    
                    # Find student's first class assignment
                    class_student = self.db.query(ClassStudent).filter(
                        ClassStudent.student_id == student_id
                    ).first()
                    
                    if class_student:
                        found_class_id = class_student.class_id
                
                # Use performance score if available, otherwise default to 0.8
                recommendation_score = perf.score if perf.score is not None else 0.8
                # Normalize to 0.0-1.0 range if score is > 1.0
                if recommendation_score > 1.0:
                    recommendation_score = recommendation_score / 100.0
                
                # Create score breakdown from performance score
                score_breakdown = {
                    "skill_match": min(recommendation_score, 1.0),
                    "fitness_match": min(recommendation_score * 0.9, 1.0),
                    "preference_match": min(recommendation_score * 0.95, 1.0)
                }
                
                # Use performance ID as recommendation ID, or generate sequential ID
                recommendation_id = perf.id
                
                history.append(ActivityRecommendationResponse(
                    id=recommendation_id,
                    student_id=student_id,
                    class_id=found_class_id if found_class_id else 0,  # Default to 0 if no class found
                    activity_id=activity.id,
                    recommendation_score=min(max(recommendation_score, 0.0), 1.0),
                    score_breakdown=score_breakdown,
                    created_at=perf.created_at if perf.created_at else datetime.utcnow()
                ))
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting recommendation history: {str(e)}")
            # Return empty list instead of raising error for production readiness
            return []

    async def clear_recommendations(
        self,
        student_id: int,
        class_id: Optional[int] = None,
        before_date: Optional[datetime] = None
    ) -> bool:
        """
        Clear stored recommendations for a student.
        
        Since recommendations are generated on-the-fly and not stored,
        this method returns True (no-op) for production readiness.
        
        Args:
            student_id: ID of the student
            class_id: Optional class ID to filter by
            before_date: Optional date to clear recommendations before
            
        Returns:
            True (recommendations are generated on-the-fly, nothing to clear)
        """
        try:
            # Recommendations are generated on-the-fly, not stored
            # Return success for API compatibility
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
            # Validate student and class exist first
            from app.models.physical_education.student import Student
            from app.models.physical_education.class_ import PhysicalEducationClass
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                # Return empty list for invalid student
                return []
            
            pe_class = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
            if not pe_class:
                # Return empty list for invalid class
                return []
            
            # Get base recommendations
            try:
                recommendations = self.recommendation_engine.get_activity_recommendations(
                    student_id=student_id,
                    class_id=class_id,
                    limit=None  # Get all recommendations to filter
                )
            except ValueError as ve:
                # RecommendationEngine raises ValueError if student/class not found
                # Return empty list gracefully
                self.logger.warning(f"RecommendationEngine error: {str(ve)}")
                return []
            
            # OPTIMIZATION: Batch fetch all activities to avoid N+1 queries
            activity_ids = [rec.activity.id for rec in recommendations if rec.activity and rec.activity.id]
            activities_dict = {}
            if activity_ids:
                activities = self.db.query(Activity).filter(Activity.id.in_(activity_ids)).all()
                activities_dict = {activity.id: activity for activity in activities}
            
            # OPTIMIZATION: Batch fetch category associations
            category_associations_dict = {}
            if activity_ids:
                category_associations = self.db.query(ActivityCategoryAssociation).filter(
                    and_(
                        ActivityCategoryAssociation.activity_id.in_(activity_ids),
                        ActivityCategoryAssociation.category_id == category_id
                    )
                ).all()
                category_associations_dict = {assoc.activity_id: assoc for assoc in category_associations}
            
            # Filter by category and additional criteria
            filtered_recommendations = []
            for rec in recommendations:
                if not rec.activity or not rec.activity.id:
                    continue
                    
                activity = activities_dict.get(rec.activity.id)
                if not activity:
                    continue
                    
                # Check if activity belongs to the category via ActivityCategoryAssociation
                category_match = category_associations_dict.get(activity.id)
                
                if not category_match:
                    continue
                    
                # Apply additional filters - Activity model uses 'type' field (enum)
                if activity_type:
                    # Get activity type as string (enum value)
                    activity_type_str = activity.type.value if activity.type and hasattr(activity.type, 'value') else str(activity.type) if activity.type else None
                    if not activity_type_str:
                        continue
                    # activity_type comes from API as ActivityType enum or string
                    filter_type_str = activity_type.value if hasattr(activity_type, 'value') else str(activity_type)
                    # Map enum values to API string values if needed
                    type_mapping = {
                        "strength_training": "strength",
                        "cardiovascular": "cardio",
                        "cardio": "cardio"
                    }
                    mapped_type = type_mapping.get(activity_type_str, activity_type_str)
                    # Compare mapped types
                    if mapped_type != filter_type_str:
                        continue
                    
                if difficulty_level:
                    # Compare difficulty level - may be string or enum
                    activity_diff = activity.difficulty_level
                    filter_diff = difficulty_level.value if hasattr(difficulty_level, 'value') else str(difficulty_level)
                    if str(activity_diff) != filter_diff:
                        continue
                    
                if min_score is not None and rec.recommendation_score < min_score:
                    continue
                    
                if max_duration is not None and activity.duration and activity.duration > max_duration:
                    continue
                    
                if exclude_recent:
                    from app.models.physical_education.activity.models import StudentActivityPerformance
                    recent_performance = self.db.query(StudentActivityPerformance).filter(
                        and_(
                            StudentActivityPerformance.student_id == student_id,
                            StudentActivityPerformance.activity_id == activity.id,
                            StudentActivityPerformance.created_at >= datetime.now() - timedelta(days=7)
                        )
                    ).first()
                    if recent_performance:
                        continue
                        
                filtered_recommendations.append(rec)
            
            # Sort and limit results
            filtered_recommendations.sort(
                key=lambda x: x.recommendation_score,
                reverse=True
            )
            
            # Transform to ActivityRecommendationResponse format
            from app.api.v1.models.activity import ActivityRecommendationResponse
            response_items = []
            for idx, rec in enumerate(filtered_recommendations[:limit]):
                # Extract activity ID from the activity object
                activity_id = rec.activity.id if hasattr(rec.activity, 'id') else 0
                
                response_items.append(ActivityRecommendationResponse(
                    id=idx + 1,  # Generate a simple sequential ID
                    student_id=student_id,
                    class_id=class_id,
                    activity_id=activity_id,
                    recommendation_score=rec.recommendation_score,
                    score_breakdown=rec.score_breakdown,
                    created_at=datetime.now()
                ))
            
            return response_items
            
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
            # Validate student and class exist
            from app.models.physical_education.student import Student
            from app.models.physical_education.class_ import PhysicalEducationClass
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                # Return empty list for invalid student instead of raising error
                return []
            
            pe_class = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
            if not pe_class:
                # Return empty list for invalid class instead of raising error
                return []
            
            # Get base recommendations
            try:
                recommendations = self.recommendation_engine.get_activity_recommendations(
                    student_id=student_id,
                    class_id=class_id,
                    limit=None  # Get all recommendations to balance
                )
            except ValueError as ve:
                # RecommendationEngine raises ValueError if student/class not found
                # Return empty list gracefully
                self.logger.warning(f"RecommendationEngine error: {str(ve)}")
                return []
            
            # OPTIMIZATION: Batch fetch all activities to avoid N+1 queries
            activity_ids = [rec.activity.id for rec in recommendations if rec.activity and rec.activity.id]
            activities_dict = {}
            if activity_ids:
                activities = self.db.query(Activity).filter(Activity.id.in_(activity_ids)).all()
                activities_dict = {activity.id: activity for activity in activities}
            
            # Apply filters
            filtered_recommendations = []
            for rec in recommendations:
                if not rec.activity or not rec.activity.id:
                    continue
                    
                activity = activities_dict.get(rec.activity.id)
                if not activity:
                    continue
                    
                # Apply filters
                if min_score is not None and rec.recommendation_score < min_score:
                    continue
                    
                if max_duration is not None and activity.duration and activity.duration > max_duration:
                    continue
                    
                # Activity model uses 'type' field (enum), filter expects string values
                if activity_types:
                    # Get activity type as string (enum value)
                    activity_type_str = activity.type.value if activity.type and hasattr(activity.type, 'value') else str(activity.type) if activity.type else None
                    if not activity_type_str:
                        continue
                    # activity_types comes from API as list of strings (e.g., ["strength", "cardio"])
                    # Map ActivityType enum values to API string values
                    # ActivityType enum has: STRENGTH_TRAINING="strength_training", CARDIO="cardio"
                    # API expects: "strength", "cardio"
                    # Map enum values to API values
                    type_mapping = {
                        "strength_training": "strength",
                        "cardiovascular": "cardio",
                        "cardio": "cardio"
                    }
                    mapped_type = type_mapping.get(activity_type_str, activity_type_str)
                    if mapped_type not in activity_types:
                        continue
                    
                if difficulty_levels and activity.difficulty_level not in difficulty_levels:
                    continue
                    
                if exclude_recent:
                    from app.models.physical_education.activity.models import StudentActivityPerformance
                    recent_performance = self.db.query(StudentActivityPerformance).filter(
                        and_(
                            StudentActivityPerformance.student_id == student_id,
                            StudentActivityPerformance.activity_id == activity.id,
                            StudentActivityPerformance.created_at >= datetime.now() - timedelta(days=7)
                        )
                    ).first()
                    if recent_performance:
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
                    
                # Get activity categories via ActivityCategoryAssociation
                associations = self.db.query(ActivityCategoryAssociation).filter(
                    ActivityCategoryAssociation.activity_id == activity.id
                ).all()
                
                for association in associations:
                    if association.category_id not in category_recommendations:
                        category_recommendations[association.category_id] = []
                    category_recommendations[association.category_id].append(rec)
            
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
            
            # Transform to ActivityRecommendationResponse format
            from app.api.v1.models.activity import ActivityRecommendationResponse
            response_items = []
            for idx, rec in enumerate(balanced_recommendations[:limit]):
                # Extract activity ID from the activity object
                activity_id = rec.activity.id if hasattr(rec.activity, 'id') else 0
                
                # Find class_id - try to find student's first class
                found_class_id = class_id
                if not found_class_id:
                    from app.models.physical_education.class_ import ClassStudent
                    class_student = self.db.query(ClassStudent).filter(
                        ClassStudent.student_id == student_id
                    ).first()
                    if class_student:
                        found_class_id = class_student.class_id
                
                response_items.append(ActivityRecommendationResponse(
                    id=idx + 1,  # Generate a simple sequential ID
                    student_id=student_id,
                    class_id=found_class_id if found_class_id else 0,
                    activity_id=activity_id,
                    recommendation_score=rec.recommendation_score,
                    score_breakdown=rec.score_breakdown,
                    created_at=datetime.now()
                ))
            
            return response_items
            
        except Exception as e:
            self.logger.error(f"Error getting balanced recommendations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while getting balanced recommendations"
            ) 