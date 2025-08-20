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
    
    # Create realistic activity progressions for multiple students
    progressions = []
    
    # Get a sample of students and activities for variety
    student_ids = list(students.values())
    activity_names = list(activities.keys())
    
    # Create progressions for a subset of students (about 100-200 progressions)
    num_progressions = min(150, len(student_ids) * len(activity_names) // 10)
    
    for _ in range(num_progressions):
        # Randomly select student and activity
        student_id = random.choice(student_ids)
        activity_name = random.choice(activity_names)
        activity_id = activities[activity_name]
        
        # Randomly determine progression level
        level = random.choice(list(ProgressionLevel))
        current_level = random.choice(list(ProgressionLevel))
        
        # Generate realistic requirements based on level
        if level == ProgressionLevel.NOVICE:
            requirements = f"Learn basic {activity_name.lower()} skills"
        elif level == ProgressionLevel.DEVELOPING:
            requirements = f"Master intermediate {activity_name.lower()} techniques"
        elif level == ProgressionLevel.ADVANCED:
            requirements = f"Perfect advanced {activity_name.lower()} skills"
        else:
            requirements = f"Excel in {activity_name.lower()} mastery"
        
        # Random dates within last 90 days
        start_date = datetime.now() - timedelta(days=random.randint(1, 90))
        last_updated = start_date + timedelta(days=random.randint(1, 30))
        
        # Realistic metadata
        attempts = random.randint(3, 20)
        success_rate = round(random.uniform(0.4, 0.95), 2)
        
        progression_data = {
            "student_id": student_id,
            "activity_id": activity_id,
            "level": level,
            "current_level": current_level,
            "requirements": requirements,
            "start_date": start_date,
            "last_updated": last_updated,
            "progression_metadata": {"attempts": attempts, "success_rate": success_rate}
        }
        
        progressions.append(progression_data)
    
    for progression_data in progressions:
        progression = ActivityProgression(**progression_data)
        session.add(progression)
    
    session.flush()
    print("Activity progressions seeded successfully!") 