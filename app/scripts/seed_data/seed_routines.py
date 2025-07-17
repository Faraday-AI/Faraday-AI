from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.routine import Routine, RoutineActivity
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    RoutineType,
    DifficultyLevel,
    RoutineStatus,
    RoutineLevel,
    RoutineTrigger
)

async def seed_routines(session):
    """Seed the routines table with initial data."""
    # First delete all routine activities
    await session.execute(RoutineActivity.__table__.delete())
    
    # Then delete all routines
    await session.execute(Routine.__table__.delete())
    
    # Create sample routines
    routines = [
        {
            "name": "Morning Warm-up",
            "description": "A gentle warm-up routine to start the day",
            "routine_type": RoutineType.WARM_UP,
            "status": RoutineStatus.ACTIVE,
            "duration_minutes": 15,
            "difficulty_level": RoutineLevel.BEGINNER,
            "equipment_needed": {"equipment": ["yoga mat"]},
            "instructions": "Follow each exercise in sequence",
            "target_muscle_groups": ["core", "legs", "arms"],
            "prerequisites": {"fitness_level": "any"},
            "safety_notes": "Maintain proper form throughout"
        },
        {
            "name": "Cardio Circuit",
            "description": "High-intensity cardio workout",
            "routine_type": RoutineType.CARDIO,
            "status": RoutineStatus.ACTIVE,
            "duration_minutes": 30,
            "difficulty_level": RoutineLevel.INTERMEDIATE,
            "equipment_needed": {"equipment": ["jump rope", "cones"]},
            "instructions": "Perform each exercise for 1 minute",
            "target_muscle_groups": ["legs", "core", "cardiovascular"],
            "prerequisites": {"fitness_level": "intermediate"},
            "safety_notes": "Take breaks as needed"
        },
        {
            "name": "Strength Training",
            "description": "Full body strength workout",
            "routine_type": RoutineType.STRENGTH,
            "status": RoutineStatus.ACTIVE,
            "duration_minutes": 45,
            "difficulty_level": RoutineLevel.ADVANCED,
            "equipment_needed": {"equipment": ["dumbbells", "resistance bands"]},
            "instructions": "Complete 3 sets of each exercise",
            "target_muscle_groups": ["chest", "back", "legs", "arms"],
            "prerequisites": {"fitness_level": "advanced"},
            "safety_notes": "Use proper lifting technique"
        }
    ]

    created_routines = []
    for routine_data in routines:
        routine = Routine(**routine_data)
        session.add(routine)
        created_routines.append(routine)
    
    await session.commit()

    # Get all activities to associate with routines
    result = await session.execute(select(Activity))
    activities = result.scalars().all()

    # Create routine-activity associations
    for routine in created_routines:
        # Randomly select 3-5 activities for each routine
        num_activities = random.randint(3, 5)
        selected_activities = random.sample(activities, num_activities)
        
        for i, activity in enumerate(selected_activities, 1):
            routine_activity = RoutineActivity(
                routine_id=routine.id,
                activity_id=activity.id,
                order=i,
                duration_minutes=random.randint(5, 15),
                sets=random.randint(2, 4),
                reps=random.randint(8, 15),
                rest_time_seconds=random.randint(30, 90),
                intensity_level="medium",
                notes=f"Activity {i} in routine",
                modifications={"optional": "reduce reps if needed"}
            )
            session.add(routine_activity)
    
    await session.commit() 