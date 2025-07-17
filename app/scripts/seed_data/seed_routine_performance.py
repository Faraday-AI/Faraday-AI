from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.physical_education.student.models import Student
from app.models.physical_education.routine.models import RoutinePerformance, Routine
from app.models.core.core_models import (
    RoutineType,
    StudentType,
    MetricType
)
from app.models.physical_education.class_ import PhysicalEducationClass

def seed_routine_performance(session):
    """Seed the routine_performances table with initial data."""
    # Get all routines
    result = session.execute(select(Routine))
    routines = result.scalars().unique().all()
    
    # Get all students
    result = session.execute(select(Student))
    students = result.scalars().unique().all()
    
    # Get all classes
    result = session.execute(select(PhysicalEducationClass))
    classes = result.scalars().unique().all()
    
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
                completion_time=random.randint(20, 60),
                energy_level=random.randint(1, 10),
                difficulty_rating=random.randint(1, 10),
                notes="Sample performance record"
            )
            session.add(performance)
    
    session.commit() 