"""Seed data for activity progressions."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.activity_adaptation.activity.activity_adaptation import ActivityAdaptation
from app.models.physical_education.activity.models import ActivityProgression
from app.models.core.core_models import AdaptationType
from app.models.student import Student
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    ProgressionLevel
)

async def seed_activity_progressions(session: AsyncSession) -> None:
    """Seed activity progressions data."""
    print("Seeding activity progressions...")
    
    # Delete existing records
    await session.execute(text("DELETE FROM activity_progressions"))
    await session.commit()
    
    # Get all students and activities
    result = await session.execute(select(Student.id, Student.first_name, Student.last_name))
    students = {f"{row.first_name} {row.last_name}": row.id for row in result.fetchall()}
    
    result = await session.execute(select(Activity.id, Activity.name))
    activities = {row.name: row.id for row in result.fetchall()}
    
    if not students or not activities:
        print("Missing required data. Please seed students and activities first.")
        return
    
    # Create activity progressions
    progressions = [
        {
            "student_id": students["John Smith"],
            "activity_id": activities["Jump Rope Basics"],
            "current_level": ProgressionLevel.BEGINNER,
            "improvement_rate": 0.75,
            "last_assessment_date": datetime.now() - timedelta(days=7)
        },
        {
            "student_id": students["Emily Johnson"],
            "activity_id": activities["Basketball Dribbling"],
            "current_level": ProgressionLevel.INTERMEDIATE,
            "improvement_rate": 0.85,
            "last_assessment_date": datetime.now() - timedelta(days=5)
        },
        {
            "student_id": students["Michael Brown"],
            "activity_id": activities["Soccer Passing"],
            "current_level": ProgressionLevel.BEGINNER,
            "improvement_rate": 0.65,
            "last_assessment_date": datetime.now() - timedelta(days=3)
        },
        {
            "student_id": students["Sarah Davis"],
            "activity_id": activities["Advanced Jump Rope"],
            "current_level": ProgressionLevel.ADVANCED,
            "improvement_rate": 0.90,
            "last_assessment_date": datetime.now() - timedelta(days=2)
        }
    ]
    
    for progression_data in progressions:
        progression = ActivityProgression(**progression_data)
        session.add(progression)
    
    await session.flush()
    print("Activity progressions seeded successfully!") 