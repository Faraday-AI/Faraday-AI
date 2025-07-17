from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.activity import (
    Activity,
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.core.core_models import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    StudentType,
    MetricType
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

async def seed_student_activity_data(session):
    """Seed the student activity performances and preferences tables with initial data."""
    # First, get the actual student IDs from the database
    result = await session.execute(select(Student.id))
    student_ids = [row[0] for row in result.fetchall()]
    
    if not student_ids:
        print("No students found in the database. Please seed students first.")
        return

    # Get the actual activity IDs from the database
    result = await session.execute(select(Activity.id))
    activity_ids = [row[0] for row in result.fetchall()]
    
    if not activity_ids:
        print("No activities found in the database. Please seed activities first.")
        return

    # Seed student activity performances
    activity_performances = [
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[0],  # First activity
            "date": datetime.now() - timedelta(days=1),
            "score": 0.85,
            "notes": "Good performance with room for improvement in technique"
        },
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[1],  # Second activity
            "date": datetime.now() - timedelta(days=2),
            "score": 0.90,
            "notes": "Excellent performance, showing good progress"
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[0],  # First activity
            "date": datetime.now() - timedelta(days=1),
            "score": 0.75,
            "notes": "Needs more practice with basic movements"
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[1],  # Second activity
            "date": datetime.now() - timedelta(days=2),
            "score": 0.80,
            "notes": "Showing improvement in coordination"
        }
    ]

    for performance_data in activity_performances:
        performance = StudentActivityPerformance(**performance_data)
        session.add(performance)

    # Seed student activity preferences
    activity_preferences = [
        {
            "student_id": student_ids[0],  # First student
            "activity_type": "SKILL_DEVELOPMENT",  # Use string value directly
            "preference_score": 0.85,
            "last_updated": datetime.now() - timedelta(days=1)
        },
        {
            "student_id": student_ids[0],  # First student
            "activity_type": "GAME",  # Use string value directly
            "preference_score": 0.90,
            "last_updated": datetime.now() - timedelta(days=1)
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_type": "FITNESS_TRAINING",  # Use string value directly
            "preference_score": 0.75,
            "last_updated": datetime.now() - timedelta(days=2)
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_type": "WARM_UP",  # Use string value directly
            "preference_score": 0.80,
            "last_updated": datetime.now() - timedelta(days=2)
        }
    ]

    for preference_data in activity_preferences:
        preference = StudentActivityPreference(**preference_data)
        session.add(preference)

    await session.flush()
    print("Student activity performances and preferences seeded successfully!") 