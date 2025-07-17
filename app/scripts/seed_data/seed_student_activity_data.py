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
from app.models.physical_education.student.models import Student
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

def seed_student_activity_data(session):
    """Seed the student activity performances and preferences tables with initial data."""
    # First, get the actual student IDs from the database
    result = session.execute(select(Student.id))
    student_ids = [row[0] for row in result.fetchall()]
    
    if not student_ids:
        print("No students found in the database. Please seed students first.")
        return

    # Get the actual activity IDs from the database
    result = session.execute(select(Activity.id))
    activity_ids = [row[0] for row in result.fetchall()]
    
    if not activity_ids:
        print("No activities found in the database. Please seed activities first.")
        return

    # Seed student activity performances
    activity_performances = [
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[0],  # First activity
            "performance_level": "EXCELLENT",
            "score": 0.85,
            "recorded_at": datetime.now() - timedelta(days=1),
            "notes": "Good performance with room for improvement in technique"
        },
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[1],  # Second activity
            "performance_level": "EXCELLENT",
            "score": 0.90,
            "recorded_at": datetime.now() - timedelta(days=2),
            "notes": "Excellent performance, showing good progress"
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[0],  # First activity
            "performance_level": "SATISFACTORY",
            "score": 0.75,
            "recorded_at": datetime.now() - timedelta(days=1),
            "notes": "Needs more practice with basic movements"
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[1],  # Second activity
            "performance_level": "GOOD",
            "score": 0.80,
            "recorded_at": datetime.now() - timedelta(days=2),
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
            "activity_id": activity_ids[0],  # First activity
            "preference_level": 4,
            "preference_score": 0.85,
            "last_updated": datetime.now() - timedelta(days=1)
        },
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[1],  # Second activity
            "preference_level": 5,
            "preference_score": 0.90,
            "last_updated": datetime.now() - timedelta(days=1)
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[0],  # First activity
            "preference_level": 3,
            "preference_score": 0.75,
            "last_updated": datetime.now() - timedelta(days=2)
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[1],  # Second activity
            "preference_level": 4,
            "preference_score": 0.80,
            "last_updated": datetime.now() - timedelta(days=2)
        }
    ]

    for preference_data in activity_preferences:
        preference = StudentActivityPreference(**preference_data)
        session.add(preference)

    session.flush()
    print("Student activity performances and preferences seeded successfully!") 