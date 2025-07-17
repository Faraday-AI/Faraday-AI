from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.routine.models import Routine, RoutineActivity
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    RoutineType,
    DifficultyLevel,
    RoutineStatus,
    RoutineLevel,
    RoutineTrigger
)

def seed_routines(session):
    """Seed the routines table with initial data."""
    # First delete all routine activities
    session.execute(RoutineActivity.__table__.delete())
    
    # Then delete all routines
    session.execute(Routine.__table__.delete())
    
    # Get a teacher and class for the routines
    teacher_result = session.execute(text("SELECT id FROM users LIMIT 1"))
    teacher_id = teacher_result.fetchone()[0]
    
    class_result = session.execute(text("SELECT id FROM physical_education_classes LIMIT 1"))
    class_id = class_result.fetchone()[0]
    
    # Create sample routines
    routines = [
        {
            "name": "Morning Warm-up",
            "description": "A gentle warm-up routine to start the day",
            "equipment_needed": {"equipment": ["yoga mat"]},
            "target_skills": ["core", "legs", "arms"],
            "instructions": "Follow each exercise in sequence",
            "duration": 15,
            "difficulty": DifficultyLevel.BEGINNER,
            "created_by": teacher_id,
            "class_id": class_id
        },
        {
            "name": "Cardio Circuit",
            "description": "High-intensity cardio workout",
            "equipment_needed": {"equipment": ["jump rope", "cones"]},
            "target_skills": ["legs", "core", "cardiovascular"],
            "instructions": "Perform each exercise for 1 minute",
            "duration": 30,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "created_by": teacher_id,
            "class_id": class_id
        },
        {
            "name": "Strength Training",
            "description": "Full body strength workout",
            "equipment_needed": {"equipment": ["dumbbells", "resistance bands"]},
            "target_skills": ["chest", "back", "legs", "arms"],
            "instructions": "Complete 3 sets of each exercise",
            "duration": 45,
            "difficulty": DifficultyLevel.ADVANCED,
            "created_by": teacher_id,
            "class_id": class_id
        }
    ]

    created_routines = []
    for routine_data in routines:
        routine = Routine(**routine_data)
        session.add(routine)
        created_routines.append(routine)
    
    session.commit()

    # Get all activities to associate with routines
    result = session.execute(select(Activity))
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
                sequence_order=i,
                duration_minutes=random.randint(5, 15),
                notes=f"Activity {i} in routine"
            )
            session.add(routine_activity)
    
    session.commit() 