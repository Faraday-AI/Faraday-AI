from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from app.models.core.core_models import (
    Gender, GoalType, GoalStatus,
    GoalCategory, GoalTimeframe
)
from app.models.physical_education.pe_enums.pe_types import (
    GradeLevel, StudentLevel, StudentStatus, StudentCategory
)
from app.models.physical_education.student.models import Student

def seed_students(session):
    """Seed the students table with initial data."""
    students = [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild asthma, peanut allergy"
        },
        {
            "first_name": "Emily",
            "last_name": "Johnson",
            "email": "emily.johnson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "michael.brown@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Moderate asthma"
        },
        {
            "first_name": "Sarah",
            "last_name": "Davis",
            "email": "sarah.davis@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None
        },
        {
            "first_name": "David",
            "last_name": "Wilson",
            "email": "david.wilson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Type 1 diabetes"
        },
        {
            "first_name": "Jessica",
            "last_name": "Taylor",
            "email": "jessica.taylor@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None
        },
        {
            "first_name": "Robert",
            "last_name": "Anderson",
            "email": "robert.anderson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None
        },
        {
            "first_name": "Jennifer",
            "last_name": "Martinez",
            "email": "jennifer.martinez@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild asthma"
        }
    ]

    for student_data in students:
        student = Student(**student_data)
        session.add(student)

    session.flush()
    print("Students seeded successfully!") 