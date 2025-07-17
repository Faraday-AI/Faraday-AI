from datetime import datetime, time, timedelta
from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent
from app.models.core.core_models import (
    ClassType,
    StudentType
)
from app.models.physical_education.pe_enums.pe_types import ClassStatus, ClassType
from app.models.app_models import GradeLevel
from sqlalchemy import select, update
import random
from typing import List
from sqlalchemy.orm import Session

def seed_classes(session):
    """Seed the classes table with initial data."""
    # First delete all class_students records
    session.execute(ClassStudent.__table__.delete())
    
    # Then delete all classes
    session.execute(PhysicalEducationClass.__table__.delete())
    
    # Set up dates for the school year
    current_year = datetime.now().year
    start_date = datetime(current_year, 9, 1)  # September 1st
    end_date = datetime(current_year + 1, 6, 15)  # June 15th next year

    classes = [
        {
            "id": 501,
            "name": "Grade 5 Physical Education",
            "description": "Physical education class for 5th grade students",
            "class_type": ClassType.REGULAR,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 30,
            "schedule": str({
                "monday": {"start": "09:00", "end": "10:00"},
                "wednesday": {"start": "09:00", "end": "10:00"},
                "friday": {"start": "09:00", "end": "10:00"}
            }),
            "location": "Gymnasium A",
            "start_date": start_date,
            "end_date": end_date,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 601,
            "name": "Grade 6 Physical Education",
            "description": "Physical education class for 6th grade students",
            "class_type": ClassType.REGULAR,
            "teacher_id": 1,
            "grade_level": GradeLevel.SIXTH,
            "max_students": 30,
            "schedule": str({
                "tuesday": {"start": "10:00", "end": "11:00"},
                "thursday": {"start": "10:00", "end": "11:00"}
            }),
            "location": "Gymnasium B",
            "start_date": start_date,
            "end_date": end_date,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 502,
            "name": "Grade 5 Advanced PE",
            "description": "Advanced physical education for 5th grade students",
            "class_type": ClassType.ADVANCED,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 20,
            "schedule": str({
                "monday": {"start": "14:00", "end": "15:00"},
                "wednesday": {"start": "14:00", "end": "15:00"}
            }),
            "location": "Gymnasium A",
            "start_date": start_date,
            "end_date": end_date,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 602,
            "name": "Grade 6 Advanced PE",
            "description": "Advanced physical education for 6th grade students",
            "class_type": ClassType.ADVANCED,
            "teacher_id": 1,
            "grade_level": GradeLevel.SIXTH,
            "max_students": 20,
            "schedule": str({
                "tuesday": {"start": "14:00", "end": "15:00"},
                "thursday": {"start": "14:00", "end": "15:00"}
            }),
            "location": "Gymnasium B",
            "start_date": start_date,
            "end_date": end_date,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Then insert all classes
    for class_data in classes:
        new_class = PhysicalEducationClass(**class_data)
        session.add(new_class)
    
    session.flush()
    print("Classes seeded successfully!") 