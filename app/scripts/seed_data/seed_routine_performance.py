from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.student import Student
from app.models.routine import RoutinePerformance, Routine
from app.models.core.core_models import (
    RoutineType,
    StudentType,
    MetricType
)
from app.models.physical_education.class_ import PhysicalEducationClass

async def seed_routine_performance(session):
    """Seed the routine_performances table with initial data."""
    # Get all routines
    result = await session.execute(select(Routine))
    routines = result.scalars().all()
    
    # Get all students
    result = await session.execute(select(Student))
    students = result.scalars().all()
    
    # Get all classes
    result = await session.execute(select(PhysicalEducationClass))
    classes = result.scalars().all()
    
    # Create performance records
    for routine in routines:
        # Create 5-10 performance records per routine
        num_records = random.randint(5, 10)
        
        for _ in range(num_records):
            student = random.choice(students)
            class_ = random.choice(classes)
            
            performance = RoutinePerformance(
                routine_id=routine.id,
                student_id=student.id,
                class_id=class_.id,
                date=datetime.now(),
                completion_time=random.randint(20, 60),
                difficulty_rating=random.randint(1, 5),
                energy_level=random.randint(1, 5),
                perceived_exertion=random.randint(1, 10),
                heart_rate_avg=random.randint(120, 160),
                heart_rate_max=random.randint(160, 200),
                calories_burned=random.randint(100, 500),
                notes="Sample performance record",
                performance_data={
                    "form_rating": random.randint(1, 5),
                    "technique_notes": "Good form maintained throughout",
                    "areas_for_improvement": ["pacing", "breathing technique"]
                }
            )
            session.add(performance)
    
    await session.commit() 