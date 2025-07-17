"""Seed data for activity progressions."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.models.activity import Activity
from app.models.activity_adaptation.activity.activity_adaptation import ActivityAdaptation
from app.models.physical_education.activity.models import ActivityProgression
from app.models.core.core_models import AdaptationType
from app.models.physical_education.student.models import Student
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    ProgressionLevel
)

def seed_activity_progressions(session: Session) -> None:
    """Seed activity progressions data."""
    print("Seeding activity progressions...")
    
    # Delete existing records
    session.execute(text("DELETE FROM activity_progressions"))
    session.commit()
    
    # Get all students and activities
    result = session.execute(select(Student.id, Student.first_name, Student.last_name))
    students = {f"{row.first_name} {row.last_name}": row.id for row in result.fetchall()}
    
    result = session.execute(select(Activity.id, Activity.name))
    activities = {row.name: row.id for row in result.fetchall()}
    
    if not students or not activities:
        print("Missing required data. Please seed students and activities first.")
        return
    
    # Create activity progressions
    progressions = [
        {
            "student_id": students["John Smith"],
            "activity_id": activities["Jump Rope Basics"],
            "level": ProgressionLevel.NOVICE,
            "current_level": ProgressionLevel.NOVICE,
            "requirements": "Complete basic jump rope skills",
            "start_date": datetime.now() - timedelta(days=30),
            "last_updated": datetime.now() - timedelta(days=7),
            "progression_metadata": {"attempts": 5, "success_rate": 0.75}
        },
        {
            "student_id": students["Emily Johnson"],
            "activity_id": activities["Basketball Dribbling"],
            "level": ProgressionLevel.DEVELOPING,
            "current_level": ProgressionLevel.DEVELOPING,
            "requirements": "Master basic dribbling techniques",
            "start_date": datetime.now() - timedelta(days=25),
            "last_updated": datetime.now() - timedelta(days=5),
            "progression_metadata": {"attempts": 8, "success_rate": 0.85}
        },
        {
            "student_id": students["Michael Brown"],
            "activity_id": activities["Soccer Passing"],
            "level": ProgressionLevel.NOVICE,
            "current_level": ProgressionLevel.NOVICE,
            "requirements": "Learn proper passing form",
            "start_date": datetime.now() - timedelta(days=20),
            "last_updated": datetime.now() - timedelta(days=3),
            "progression_metadata": {"attempts": 3, "success_rate": 0.65}
        },
        {
            "student_id": students["Sarah Davis"],
            "activity_id": activities["Advanced Jump Rope"],
            "level": ProgressionLevel.ADVANCED,
            "current_level": ProgressionLevel.ADVANCED,
            "requirements": "Master advanced jump rope techniques",
            "start_date": datetime.now() - timedelta(days=45),
            "last_updated": datetime.now() - timedelta(days=2),
            "progression_metadata": {"attempts": 12, "success_rate": 0.90}
        }
    ]
    
    for progression_data in progressions:
        progression = ActivityProgression(**progression_data)
        session.add(progression)
    
    session.flush()
    print("Activity progressions seeded successfully!") 