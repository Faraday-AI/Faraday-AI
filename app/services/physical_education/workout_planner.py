from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories 
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.monitoring import track_metrics
from app.core.database import get_db
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.workout import (
    Workout,
    WorkoutSession,
    WorkoutPlan,
    WorkoutPlanWorkout,
    PhysicalEducationWorkoutExercise
)
from app.models.physical_education.pe_enums.pe_types import (
    WorkoutType,
    DifficultyLevel,
    ExerciseType
)

class WorkoutPlanner:
    """Manager for handling workout plans and exercise routines."""

    def __init__(self):
        self.logger = logging.getLogger("workout_planner")
        
        # Exercise templates for different workout types
        self.exercise_templates = {
            WorkoutType.CARDIO: {
                DifficultyLevel.BEGINNER: [
                    {
                        "name": "Walking",
                        "type": ExerciseType.CARDIO,
                        "duration": 20,
                        "intensity": "moderate"
                    },
                    {
                        "name": "Light Jogging",
                        "type": ExerciseType.CARDIO,
                        "duration": 15,
                        "intensity": "moderate"
                    }
                ],
                DifficultyLevel.INTERMEDIATE: [
                    {
                        "name": "Running",
                        "type": ExerciseType.CARDIO,
                        "duration": 25,
                        "intensity": "high"
                    },
                    {
                        "name": "Jump Rope",
                        "type": ExerciseType.CARDIO,
                        "duration": 10,
                        "intensity": "high"
                    }
                ]
            },
            WorkoutType.STRENGTH: {
                DifficultyLevel.BEGINNER: [
                    {
                        "name": "Push-ups",
                        "type": ExerciseType.BODYWEIGHT,
                        "sets": 3,
                        "reps": 10
                    },
                    {
                        "name": "Squats",
                        "type": ExerciseType.BODYWEIGHT,
                        "sets": 3,
                        "reps": 15
                    }
                ]
            }
            # Add more templates for other workout types...
        }

    @track_metrics
    async def create_workout(
        self,
        db: Session,
        name: str,
        description: str,
        workout_type: WorkoutType,
        difficulty: DifficultyLevel,
        duration: int,
        exercises: List[Dict],
        equipment_needed: Optional[List[str]] = None,
        target_heart_rate: Optional[Dict] = None,
        safety_requirements: Optional[Dict] = None,
        indoor_outdoor: str = "both",
        space_required: str = "medium",
        max_participants: int = 30,
        metadata: Optional[Dict] = None
    ) -> Workout:
        """Create a new workout."""
        try:
            workout = Workout(
                name=name,
                description=description,
                workout_type=workout_type,
                difficulty=difficulty,
                duration=duration,
                equipment_needed=equipment_needed or [],
                target_heart_rate=target_heart_rate,
                safety_requirements=safety_requirements or {},
                indoor_outdoor=indoor_outdoor,
                space_required=space_required,
                max_participants=max_participants,
                metadata=metadata or {}
            )
            
            db.add(workout)
            db.commit()
            db.refresh(workout)
            
            # Add exercises to workout
            for exercise_data in exercises:
                exercise = await self.get_or_create_exercise(db, exercise_data)
                workout.exercises.append(exercise)
            
            db.commit()
            return workout
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating workout: {str(e)}")
            raise

    @track_metrics
    async def create_workout_plan(
        self,
        db: Session,
        student_id: int,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        frequency: int,
        workouts: List[Dict],
        goals: Optional[Dict] = None,
        progress_metrics: Optional[Dict] = None,
        schedule: Optional[Dict] = None,
        adaptations_needed: Optional[Dict] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> WorkoutPlan:
        """Create a workout plan for a student."""
        try:
            plan = WorkoutPlan(
                student_id=student_id,
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                goals=goals or {},
                progress_metrics=progress_metrics or {},
                schedule=schedule or {},
                adaptations_needed=adaptations_needed,
                notes=notes,
                metadata=metadata or {}
            )
            
            db.add(plan)
            db.commit()
            db.refresh(plan)
            
            # Add workouts to plan
            for workout_data in workouts:
                workout_id = workout_data["workout_id"]
                day_of_week = workout_data["day_of_week"]
                order = workout_data.get("order", 1)
                
                plan_workout = WorkoutPlanWorkout(
                    plan_id=plan.id,
                    workout_id=workout_id,
                    day_of_week=day_of_week,
                    order=order,
                    notes=workout_data.get("notes")
                )
                db.add(plan_workout)
            
            db.commit()
            return plan
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating workout plan: {str(e)}")
            raise

    @track_metrics
    async def record_workout_session(
        self,
        db: Session,
        workout_id: int,
        student_id: int,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        completed: bool = False,
        performance_data: Optional[Dict] = None,
        difficulty_rating: Optional[int] = None,
        enjoyment_rating: Optional[int] = None,
        notes: Optional[str] = None,
        modifications_used: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> WorkoutSession:
        """Record a workout session for a student."""
        try:
            session = WorkoutSession(
                workout_id=workout_id,
                student_id=student_id,
                start_time=start_time,
                end_time=end_time,
                completed=completed,
                performance_data=performance_data or {},
                difficulty_rating=difficulty_rating,
                enjoyment_rating=enjoyment_rating,
                notes=notes,
                modifications_used=modifications_used,
                metadata=metadata or {}
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return session
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error recording workout session: {str(e)}")
            raise

    @track_metrics
    async def get_student_workouts(
        self,
        db: Session,
        student_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WorkoutSession]:
        """Get workout history for a student."""
        try:
            query = db.query(WorkoutSession).filter(
                WorkoutSession.student_id == student_id
            )
            
            if start_date:
                query = query.filter(WorkoutSession.start_time >= start_date)
            if end_date:
                query = query.filter(WorkoutSession.start_time <= end_date)
                
            return query.order_by(WorkoutSession.start_time.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving student workouts: {str(e)}")
            raise

    @track_metrics
    async def get_workout_plan(
        self,
        db: Session,
        plan_id: int
    ) -> Optional[Dict]:
        """Get detailed workout plan information."""
        try:
            plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
            if not plan:
                return None
                
            # Get all workouts in the plan
            plan_workouts = db.query(WorkoutPlanWorkout).filter(
                WorkoutPlanWorkout.plan_id == plan_id
            ).order_by(
                WorkoutPlanWorkout.day_of_week,
                WorkoutPlanWorkout.order
            ).all()
            
            # Organize workouts by day
            workouts_by_day = {}
            for pw in plan_workouts:
                if pw.day_of_week not in workouts_by_day:
                    workouts_by_day[pw.day_of_week] = []
                workouts_by_day[pw.day_of_week].append({
                    "workout": pw.workout,
                    "order": pw.order,
                    "notes": pw.notes
                })
            
            return {
                "plan": plan,
                "workouts_by_day": workouts_by_day
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving workout plan: {str(e)}")
            raise

    async def get_or_create_exercise(
        self,
        db: Session,
        exercise_data: Dict
    ) -> Exercise:
        """Get existing exercise or create new one."""
        try:
            # Check if exercise exists
            exercise = db.query(Exercise).filter(
                Exercise.name == exercise_data["name"],
                Exercise.exercise_type == exercise_data["type"]
            ).first()
            
            if exercise:
                return exercise
                
            # Create new exercise
            exercise = Exercise(
                name=exercise_data["name"],
                description=exercise_data.get("description", ""),
                exercise_type=exercise_data["type"],
                difficulty=exercise_data.get("difficulty", DifficultyLevel.BEGINNER),
                equipment_needed=exercise_data.get("equipment_needed", []),
                instructions=exercise_data.get("instructions", {}),
                muscles_targeted=exercise_data.get("muscles_targeted", {}),
                safety_tips=exercise_data.get("safety_tips", {}),
                modifications=exercise_data.get("modifications", {}),
                video_url=exercise_data.get("video_url"),
                image_url=exercise_data.get("image_url"),
                metadata=exercise_data.get("metadata", {})
            )
            
            db.add(exercise)
            db.commit()
            db.refresh(exercise)
            
            return exercise
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error getting/creating exercise: {str(e)}")
            raise

    @track_metrics
    async def generate_workout_plan(
        self,
        db: Session,
        student_id: int,
        fitness_level: DifficultyLevel,
        preferred_types: List[WorkoutType],
        frequency: int = 3,
        duration_weeks: int = 4
    ) -> WorkoutPlan:
        """Generate a personalized workout plan based on student preferences."""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(weeks=duration_weeks)
            
            # Create workouts for each type
            workouts = []
            for workout_type in preferred_types:
                if workout_type in self.exercise_templates:
                    templates = self.exercise_templates[workout_type][fitness_level]
                    workout = await self.create_workout(
                        db,
                        name=f"{workout_type.value.title()} Workout",
                        description=f"Generated {workout_type.value} workout for {fitness_level.value} level",
                        workout_type=workout_type,
                        difficulty=fitness_level,
                        duration=45,  # Default duration
                        exercises=templates
                    )
                    workouts.append({
                        "workout_id": workout.id,
                        "day_of_week": len(workouts) % 7,  # Distribute across week
                        "order": 1
                    })
            
            # Create the plan
            return await self.create_workout_plan(
                db,
                student_id=student_id,
                name=f"Generated {duration_weeks}-Week Plan",
                description=f"Personalized workout plan for {fitness_level.value} level",
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                workouts=workouts,
                goals={
                    "improve_fitness": True,
                    "target_types": [t.value for t in preferred_types]
                },
                progress_metrics={
                    "completion_rate": 0,
                    "difficulty_ratings": [],
                    "enjoyment_ratings": []
                },
                schedule={
                    "weekly_distribution": True,
                    "rest_days": [6]  # Sunday
                }
            )
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error generating workout plan: {str(e)}")
            raise

# Initialize global workout planner
workout_planner = WorkoutPlanner() 