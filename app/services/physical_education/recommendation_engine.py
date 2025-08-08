from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.student import Student
from app.models.activity import Activity
from app.models.routine import Routine
from app.models.physical_education.assessment import Assessment
# Define ActivityRecommendation locally to avoid circular imports
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ActivityRecommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity: Any = Field(..., description="Activity object")
    recommendation_score: float = Field(..., description="Recommendation score (0.0 to 1.0)", ge=0.0, le=1.0)
    score_breakdown: Dict[str, float] = Field(..., description="Detailed breakdown of the recommendation score")
from app.schemas.physical_education.student import StudentPreferences
from app.core.config import settings
from app.core.logging import get_logger
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    SkillLevel,
    FitnessLevel
)

logger = get_logger(__name__)

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger

    def get_activity_recommendations(
        self,
        student_id: int,
        class_id: int,
        preferences: Optional[Dict] = None,
        limit: int = 5
    ) -> List[ActivityRecommendation]:
        """Generate personalized activity recommendations for a student."""
        # Get student and class information
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with ID {student_id} not found")

        class_ = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
        if not class_:
            raise ValueError(f"Class with ID {class_id} not found")

        # Get student's recent assessments
        recent_assessments = (
            self.db.query(Assessment)
            .filter(Assessment.student_id == student_id)
            .order_by(Assessment.created_at.desc())
            .limit(5)
            .all()
        )

        # Get all available activities
        activities = self.db.query(Activity).all()

        # Calculate recommendation scores for each activity
        recommendations = []
        for activity in activities:
            score = self._calculate_recommendation_score(
                activity=activity,
                student=student,
                class_=class_,
                recent_assessments=recent_assessments,
                preferences=preferences
            )
            
            recommendations.append(
                ActivityRecommendation(
                    activity=activity,
                    recommendation_score=score["overall"],
                    score_breakdown=score["breakdown"]
                )
            )

        # Sort by recommendation score and limit results
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
        return recommendations[:limit]

    def _calculate_recommendation_score(
        self,
        activity: Activity,
        student: Student,
        class_: PhysicalEducationClass,
        recent_assessments: List[Assessment],
        preferences: Optional[Dict] = None
    ) -> Dict:
        """Calculate recommendation score for an activity."""
        score_breakdown = {
            "skill_level_match": 0.0,
            "fitness_level_match": 0.0,
            "preference_match": 0.0,
            "class_requirements": 0.0,
            "recent_performance": 0.0
        }

        # Calculate skill level match
        if student.skill_level and activity.skill_level:
            score_breakdown["skill_level_match"] = 1.0 - abs(
                student.skill_level - activity.skill_level
            ) / 5.0

        # Calculate fitness level match
        if student.fitness_level and activity.fitness_level:
            score_breakdown["fitness_level_match"] = 1.0 - abs(
                student.fitness_level - activity.fitness_level
            ) / 5.0

        # Calculate preference match
        if preferences:
            if "activity_types" in preferences:
                if activity.type in preferences["activity_types"]:
                    score_breakdown["preference_match"] = 1.0
            if "difficulty" in preferences:
                score_breakdown["preference_match"] += 1.0 - abs(
                    activity.difficulty - preferences["difficulty"]
                ) / 5.0

        # Calculate class requirements match
        if class_.requirements:
            if activity.type in class_.requirements.get("activity_types", []):
                score_breakdown["class_requirements"] = 1.0

        # Calculate recent performance
        if recent_assessments:
            relevant_assessments = [
                a for a in recent_assessments
                if a.activity_id == activity.id
            ]
            if relevant_assessments:
                avg_score = sum(a.score for a in relevant_assessments) / len(relevant_assessments)
                score_breakdown["recent_performance"] = avg_score / 100.0

        # Calculate overall score
        weights = {
            "skill_level_match": 0.3,
            "fitness_level_match": 0.2,
            "preference_match": 0.2,
            "class_requirements": 0.2,
            "recent_performance": 0.1
        }

        overall_score = sum(
            score * weights[factor]
            for factor, score in score_breakdown.items()
        )

        return {
            "overall": overall_score,
            "breakdown": score_breakdown
        }

    def _get_student_info(self, student_id: int) -> Student:
        """Get student's current level and performance data."""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with ID {student_id} not found")
        return student

    def _get_class_info(self, class_id: int) -> PhysicalEducationClass:
        """Get class information and current focus areas."""
        class_info = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
        if not class_info:
            raise ValueError(f"Class with ID {class_id} not found")
        return class_info

    def _get_relevant_activities(
        self,
        student_id: int,
        class_id: int,
        preferences: Optional[StudentPreferences] = None
    ) -> List[Activity]:
        """Get activities relevant to student's level and class focus."""
        # Base query for activities
        query = self.db.query(Activity)
        
        # Filter by student's level
        student = self._get_student_info(student_id)
        query = query.filter(Activity.difficulty_level <= student.skill_level + 1)
        
        # Filter by class focus areas if specified
        class_info = self._get_class_info(class_id)
        if class_info.focus_areas:
            query = query.filter(Activity.category.in_(class_info.focus_areas))
        
        # Apply preferences if provided
        if preferences:
            if preferences.activity_types:
                query = query.filter(Activity.type.in_(preferences.activity_types))
            if preferences.equipment_preferences:
                query = query.filter(Activity.equipment_requirements.in_(preferences.equipment_preferences))
        
        return query.all()

    def _score_activities(
        self,
        activities: List[Activity],
        student: Student,
        class_info: PhysicalEducationClass,
        preferences: Optional[StudentPreferences] = None
    ) -> List[Dict]:
        """Score activities based on various factors."""
        scored_activities = []
        
        for activity in activities:
            score = 0.0
            
            # Base score from activity difficulty match
            difficulty_score = self._calculate_difficulty_score(activity, student)
            score += difficulty_score * 0.3
            
            # Score from class focus alignment
            focus_score = self._calculate_focus_score(activity, class_info)
            score += focus_score * 0.2
            
            # Score from student preferences
            if preferences:
                preference_score = self._calculate_preference_score(activity, preferences)
                score += preference_score * 0.2
            
            # Score from recent performance
            performance_score = self._calculate_performance_score(activity, student)
            score += performance_score * 0.3
            
            scored_activities.append({
                "activity": activity,
                "score": score,
                "scores": {
                    "difficulty": difficulty_score,
                    "focus": focus_score,
                    "preference": preference_score if preferences else 0,
                    "performance": performance_score
                }
            })
        
        return scored_activities

    def _calculate_difficulty_score(self, activity: Activity, student: Student) -> float:
        """Calculate score based on activity difficulty match with student level."""
        level_diff = abs(activity.difficulty_level - student.skill_level)
        return max(0, 1 - (level_diff * 0.2))

    def _calculate_focus_score(self, activity: Activity, class_info: PhysicalEducationClass) -> float:
        """Calculate score based on alignment with class focus areas."""
        if not class_info.focus_areas:
            return 0.5
        return 1.0 if activity.category in class_info.focus_areas else 0.0

    def _calculate_preference_score(self, activity: Activity, preferences: StudentPreferences) -> float:
        """Calculate score based on student preferences."""
        score = 0.0
        
        if preferences.activity_types and activity.type in preferences.activity_types:
            score += 0.5
        
        if preferences.equipment_preferences and activity.equipment_requirements in preferences.equipment_preferences:
            score += 0.5
        
        return score

    def _calculate_performance_score(self, activity: Activity, student: Student) -> float:
        """Calculate score based on student's recent performance in similar activities."""
        # TODO: Implement performance-based scoring
        return 0.5

    def _get_top_recommendations(
        self,
        scored_activities: List[Dict],
        limit: int
    ) -> List[ActivityRecommendation]:
        """Get top recommendations based on scores."""
        # Sort by score in descending order
        sorted_activities = sorted(
            scored_activities,
            key=lambda x: x["score"],
            reverse=True
        )
        
        # Convert to recommendation objects
        recommendations = []
        for item in sorted_activities[:limit]:
            recommendations.append(
                ActivityRecommendation(
                    activity=item["activity"],
                    score=item["score"],
                    scores=item["scores"]
                )
            )
        
        return recommendations 