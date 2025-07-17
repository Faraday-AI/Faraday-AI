from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories 

import logging
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.monitoring import track_metrics
from app.core.database import get_db
from app.models.student import (
    Student,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation
)
from app.models.physical_education.pe_enums.pe_types import (
    GoalType,
    GoalStatus,
    GoalLevel,
    GoalTrigger,
    Gender,
    FitnessLevel,
    GoalCategory,
    GoalTimeframe,
    GoalAdjustment
)

class FitnessGoalManager:
    """Manager for handling fitness goals and progress tracking."""

    def __init__(self):
        self.logger = logging.getLogger("fitness_goal_manager")
        
        # Goal recommendation templates
        self.goal_templates = {
            GoalCategory.CARDIOVASCULAR: {
                "beginner": {
                    "description": "Complete {duration} minutes of continuous aerobic activity",
                    "initial_duration": 15,
                    "progression_rate": 5,  # minutes per week
                    "target_duration": 30
                },
                "intermediate": {
                    "description": "Maintain target heart rate for {duration} minutes",
                    "initial_duration": 20,
                    "progression_rate": 7,
                    "target_duration": 45
                },
                "advanced": {
                    "description": "Complete high-intensity interval training for {duration} minutes",
                    "initial_duration": 25,
                    "progression_rate": 10,
                    "target_duration": 60
                }
            },
            # Add templates for other categories...
        }

    @track_metrics
    async def create_goal(
        self,
        db: Session,
        student_id: int,
        category: GoalCategory,
        description: str,
        target_value: Optional[float] = None,
        timeframe: GoalTimeframe = GoalTimeframe.SHORT_TERM,
        start_date: Optional[datetime] = None,
        target_date: Optional[datetime] = None,
        priority: int = 1,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> StudentHealthFitnessGoal:
        """Create a new fitness goal."""
        try:
            # Set default dates if not provided
            if not start_date:
                start_date = datetime.utcnow()
            if not target_date:
                # Set default target date based on timeframe
                if timeframe == GoalTimeframe.SHORT_TERM:
                    target_date = start_date + timedelta(weeks=4)
                elif timeframe == GoalTimeframe.MEDIUM_TERM:
                    target_date = start_date + timedelta(weeks=12)
                elif timeframe == GoalTimeframe.LONG_TERM:
                    target_date = start_date + timedelta(weeks=24)
                elif timeframe == GoalTimeframe.ACADEMIC_YEAR:
                    target_date = datetime(start_date.year + 1, 6, 30)
                else:
                    target_date = start_date + timedelta(weeks=12)

            goal = StudentHealthFitnessGoal(
                student_id=student_id,
                category=category,
                description=description,
                target_value=target_value,
                current_value=None,
                start_date=start_date,
                target_date=target_date,
                status=GoalStatus.NOT_STARTED,
                timeframe=timeframe,
                priority=priority,
                notes=notes,
                metadata=metadata or {}
            )
            
            db.add(goal)
            db.commit()
            db.refresh(goal)
            
            return goal
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating fitness goal: {str(e)}")
            raise

    @track_metrics
    async def update_progress(
        self,
        db: Session,
        goal_id: int,
        value: float,
        notes: Optional[str] = None,
        is_milestone: bool = False,
        metadata: Optional[Dict] = None
    ) -> StudentHealthGoalProgress:
        """Record progress towards a fitness goal."""
        try:
            # Get the goal
            goal = db.query(StudentHealthFitnessGoal).filter(StudentHealthFitnessGoal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal {goal_id} not found")
                
            # Create progress record
            progress = StudentHealthGoalProgress(
                goal_id=goal_id,
                value=value,
                notes=notes,
                is_milestone=is_milestone,
                metadata=metadata or {}
            )
            
            # Update goal current value and status
            goal.current_value = value
            if value >= goal.target_value:
                goal.status = GoalStatus.COMPLETED
            elif goal.status == GoalStatus.NOT_STARTED:
                goal.status = GoalStatus.IN_PROGRESS
                
            db.add(progress)
            db.commit()
            db.refresh(progress)
            
            return progress
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error updating goal progress: {str(e)}")
            raise

    @track_metrics
    async def adjust_goal(
        self,
        db: Session,
        goal_id: int,
        new_target: Optional[float] = None,
        new_date: Optional[datetime] = None,
        reason: str = "",
        adjusted_by: str = "system"
    ) -> GoalAdjustment:
        """Adjust a fitness goal's target or date."""
        try:
            goal = db.query(StudentHealthFitnessGoal).filter(StudentHealthFitnessGoal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal {goal_id} not found")
                
            # Create adjustment record
            adjustment = GoalAdjustment(
                goal_id=goal_id,
                previous_target=goal.target_value,
                new_target=new_target,
                previous_date=goal.target_date,
                new_date=new_date,
                reason=reason,
                adjusted_by=adjusted_by
            )
            
            # Update goal
            if new_target is not None:
                goal.target_value = new_target
            if new_date is not None:
                goal.target_date = new_date
            goal.status = GoalStatus.ADJUSTED
            
            db.add(adjustment)
            db.commit()
            db.refresh(adjustment)
            
            return adjustment
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error adjusting goal: {str(e)}")
            raise

    @track_metrics
    async def get_student_goals(
        self,
        db: Session,
        student_id: int,
        status: Optional[GoalStatus] = None,
        category: Optional[GoalCategory] = None,
        timeframe: Optional[GoalTimeframe] = None
    ) -> List[StudentHealthFitnessGoal]:
        """Get all fitness goals for a student."""
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
            self.logger.error(f"Error retrieving student goals: {str(e)}")
            raise

    @track_metrics
    async def generate_recommendations(
        self,
        db: Session,
        student_id: int,
        fitness_level: str = "beginner"
    ) -> List[StudentHealthGoalRecommendation]:
        """Generate goal recommendations based on student's fitness level."""
        try:
            recommendations = []
            
            for category in GoalCategory:
                if category in self.goal_templates:
                    template = self.goal_templates[category][fitness_level]
                    
                    recommendation = StudentHealthGoalRecommendation(
                        student_id=student_id,
                        category=category,
                        description=template["description"].format(
                            duration=template["initial_duration"]
                        ),
                        suggested_target=template["target_duration"],
                        suggested_timeframe=GoalTimeframe.SHORT_TERM,
                        reasoning=f"Based on {fitness_level} fitness level",
                        priority=2,
                        metadata={
                            "initial_duration": template["initial_duration"],
                            "progression_rate": template["progression_rate"],
                            "target_duration": template["target_duration"]
                        }
                    )
                    
                    recommendations.append(recommendation)
            
            db.add_all(recommendations)
            db.commit()
            for rec in recommendations:
                db.refresh(rec)
            
            return recommendations
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error generating goal recommendations: {str(e)}")
            raise

    @track_metrics
    async def get_progress_history(
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
            self.logger.error(f"Error retrieving goal progress history: {str(e)}")
            raise

    @track_metrics
    async def get_adjustment_history(
        self,
        db: Session,
        goal_id: int
    ) -> List[GoalAdjustment]:
        """Get adjustment history for a specific goal."""
        try:
            return db.query(GoalAdjustment).filter(
                GoalAdjustment.goal_id == goal_id
            ).order_by(GoalAdjustment.adjustment_date.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving goal adjustment history: {str(e)}")
            raise

# Initialize global fitness goal manager
fitness_goal_manager = FitnessGoalManager() 