"""Service for managing health and fitness-related operations."""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.monitoring import track_metrics
from app.core.database import get_db
from app.models.student import (
    Student,
    HealthMetricThreshold,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation,
    MetricType,
    MeasurementUnit,
    GoalType,
    GoalStatus
)
from app.models.health_fitness.metrics.health import HealthMetric, HealthMetricHistory

class HealthFitnessService:
    """Service for managing health and fitness operations."""

    def __init__(self):
        self.logger = logging.getLogger("health_fitness_service")

    @track_metrics
    async def get_student_health_metrics(
        self,
        db: Session,
        student_id: int,
        metric_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HealthMetric]:
        """Get health metrics for a student."""
        try:
            query = db.query(HealthMetric).filter(HealthMetric.student_id == student_id)
            
            if metric_type:
                query = query.filter(HealthMetric.metric_type == metric_type)
            if start_date:
                query = query.filter(HealthMetric.measured_at >= start_date)
            if end_date:
                query = query.filter(HealthMetric.measured_at <= end_date)
                
            return query.order_by(HealthMetric.measured_at.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving health metrics: {str(e)}")
            raise

    @track_metrics
    async def get_metric_history(
        self,
        db: Session,
        student_id: int,
        metric_type: str,
        timeframe: str
    ) -> List[Dict[str, Any]]:
        """Get historical health metric data."""
        try:
            # Calculate start date based on timeframe
            end_date = datetime.utcnow()
            if timeframe == "1D":
                start_date = end_date - timedelta(days=1)
            elif timeframe == "1W":
                start_date = end_date - timedelta(weeks=1)
            elif timeframe == "1M":
                start_date = end_date - timedelta(days=30)
            elif timeframe == "3M":
                start_date = end_date - timedelta(days=90)
            elif timeframe == "6M":
                start_date = end_date - timedelta(days=180)
            elif timeframe == "1Y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)  # Default to 1 month
            
            history = db.query(HealthMetricHistory).filter(
                HealthMetricHistory.student_id == student_id,
                HealthMetricHistory.metric_type == metric_type,
                HealthMetricHistory.recorded_at.between(start_date, end_date)
            ).order_by(HealthMetricHistory.recorded_at.asc()).all()
            
            return [
                {
                    "value": h.value,
                    "unit": h.unit,
                    "recorded_at": h.recorded_at,
                    "is_abnormal": h.is_abnormal,
                    "notes": h.notes
                }
                for h in history
            ]
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving metric history: {str(e)}")
            raise

    @track_metrics
    async def get_fitness_goals(
        self,
        db: Session,
        student_id: int,
        status: Optional[str] = None,
        category: Optional[str] = None,
        timeframe: Optional[str] = None
    ) -> List[StudentHealthFitnessGoal]:
        """Get fitness goals for a student."""
        try:
            query = db.query(StudentHealthFitnessGoal).filter(StudentHealthFitnessGoal.student_id == student_id)
            
            if status:
                query = query.filter(StudentHealthFitnessGoal.status == status)
            if category:
                query = query.filter(StudentHealthFitnessGoal.category == category)
            if timeframe:
                query = query.filter(StudentHealthFitnessGoal.timeframe == timeframe)
                
            return query.order_by(StudentHealthFitnessGoal.priority, StudentHealthFitnessGoal.target_date).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving fitness goals: {str(e)}")
            raise

    @track_metrics
    async def get_goal_progress(
        self,
        db: Session,
        goal_id: int
    ) -> List[StudentHealthGoalProgress]:
        """Get progress history for a specific goal."""
        try:
            return db.query(StudentHealthGoalProgress).filter(
                StudentHealthGoalProgress.goal_id == goal_id
            ).order_by(StudentHealthGoalProgress.date.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving goal progress: {str(e)}")
            raise

    @track_metrics
    async def get_recommendations(
        self,
        db: Session,
        student_id: int,
        category: Optional[str] = None
    ) -> List[StudentHealthGoalRecommendation]:
        """Get goal recommendations for a student."""
        try:
            query = db.query(StudentHealthGoalRecommendation).filter(
                StudentHealthGoalRecommendation.student_id == student_id
            )
            
            if category:
                query = query.filter(StudentHealthGoalRecommendation.category == category)
                
            return query.order_by(StudentHealthGoalRecommendation.priority.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving goal recommendations: {str(e)}")
            raise

# Initialize global service instance
health_fitness_service = HealthFitnessService() 