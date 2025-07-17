from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.pe_enums.pe_types import (
    ExerciseType,
    ExerciseDifficulty
)

def seed_exercises(session):
    """Seed the exercises table with initial data."""
    # Get all activities
    activities = session.execute(text("SELECT id, name FROM activities"))
    activity_map = {row.name: row.id for row in activities}
    
    exercises = [
        {
            "name": "Basic Jump Rope",
            "description": "Basic jump rope technique with two feet",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "cardio",
            "equipment_needed": ["Jump rope"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Keep knees slightly bent, land softly on balls of feet. Focus on maintaining a steady rhythm.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 4,
                "reps": 20,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Basketball Dribble Drills",
            "description": "Basic basketball dribbling techniques",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "skill_development",
            "equipment_needed": ["Basketball"],
            "target_muscle_groups": ["arms", "shoulders", "core"],
            "instructions": "Keep eyes up, use fingertips, maintain low stance. Practice with both hands.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 4,
                "reps": 30,
                "rest_time_seconds": 45,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Soccer Passing Drills",
            "description": "Basic soccer passing techniques",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "skill_development",
            "equipment_needed": ["Soccer ball"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Plant foot next to ball, strike with inside of foot. Practice with both feet.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 4,
                "reps": 25,
                "rest_time_seconds": 45,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Dynamic Warm-up Circuit",
            "description": "Full-body dynamic warm-up exercises",
            "exercise_type": ExerciseType.WARM_UP.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "warm_up",
            "equipment_needed": [],
            "target_muscle_groups": ["full_body"],
            "instructions": "Move through full range of motion, maintain control. Focus on proper form.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 3,
                "reps": 15,
                "rest_time_seconds": 30,
                "intensity": "LOW"
            }
        },
        {
            "name": "Static Stretching Routine",
            "description": "Post-activity static stretching",
            "exercise_type": ExerciseType.COOL_DOWN.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "cool_down",
            "equipment_needed": ["Yoga mat"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Hold each stretch for 20-30 seconds, breathe deeply. Don't bounce while stretching.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 3,
                "reps": 1,
                "rest_time_seconds": 30,
                "intensity": "LOW"
            }
        },
        {
            "name": "Circuit Training Workout",
            "description": "Full-body circuit training exercises",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "strength_training",
            "equipment_needed": ["Various fitness equipment"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Maintain proper form, control movement speed. Adjust weights as needed.",
            "exercise_metadata": {
                "duration_minutes": 30,
                "sets": 5,
                "reps": 15,
                "rest_time_seconds": 60,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Basketball Game Drills",
            "description": "5v5 basketball game preparation",
            "exercise_type": ExerciseType.SPORTS.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "team_sports",
            "equipment_needed": ["Basketball", "court"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Focus on team play, communication, and strategy. Rotate positions regularly.",
            "exercise_metadata": {
                "duration_minutes": 40,
                "sets": 5,
                "reps": 1,
                "rest_time_seconds": 120,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Advanced Jump Rope Techniques",
            "description": "Advanced jump rope combinations",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.ADVANCED.value,
            "category": "cardio",
            "equipment_needed": ["Jump rope"],
            "target_muscle_groups": ["legs", "core", "arms"],
            "instructions": "Master basic jumps before attempting advanced moves. Progress gradually to more complex moves.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 5,
                "reps": 30,
                "rest_time_seconds": 60,
                "intensity": "HIGH"
            }
        }
    ]

    for exercise_data in exercises:
        exercise = Exercise(**exercise_data)
        session.add(exercise)

    session.flush()
    print("Exercises seeded successfully!") 