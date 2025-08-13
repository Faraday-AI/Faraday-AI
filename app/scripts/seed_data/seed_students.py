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
from sqlalchemy import text

def seed_students(session):
    """Seed the students table with comprehensive and diverse initial data."""
    
    # First delete existing students
    session.execute(Student.__table__.delete())
    
    # Generate more diverse student data
    students = [
        # Grade 5 Students
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild asthma, peanut allergy",
            "emergency_contact": "555-0101"
        },
        {
            "first_name": "Emily",
            "last_name": "Johnson",
            "email": "emily.johnson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0103",
            "parent_name": "Jennifer Johnson",
            "parent_phone": "555-0104"
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "michael.brown@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Moderate asthma",
            "emergency_contact": "555-0105",
            "parent_name": "David Brown",
            "parent_phone": "555-0106"
        },
        {
            "first_name": "Sarah",
            "last_name": "Davis",
            "email": "sarah.davis@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0107",
            "parent_name": "Lisa Davis",
            "parent_phone": "555-0108"
        },
        {
            "first_name": "David",
            "last_name": "Wilson",
            "email": "david.wilson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Type 1 diabetes",
            "emergency_contact": "555-0109",
            "parent_name": "Mark Wilson",
            "parent_phone": "555-0110"
        },
        {
            "first_name": "Jessica",
            "last_name": "Taylor",
            "email": "jessica.taylor@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0111",
            "parent_name": "Amanda Taylor",
            "parent_phone": "555-0112"
        },
        {
            "first_name": "Robert",
            "last_name": "Anderson",
            "email": "robert.anderson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0113",
            "parent_name": "Thomas Anderson",
            "parent_phone": "555-0114"
        },
        {
            "first_name": "Amanda",
            "last_name": "Martinez",
            "email": "amanda.martinez@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild hearing impairment",
            "emergency_contact": "555-0115",
            "parent_name": "Carlos Martinez",
            "parent_phone": "555-0116"
        },
        {
            "first_name": "Christopher",
            "last_name": "Garcia",
            "email": "christopher.garcia@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0117",
            "parent_name": "Maria Garcia",
            "parent_phone": "555-0118"
        },
        {
            "first_name": "Sophia",
            "last_name": "Rodriguez",
            "email": "sophia.rodriguez@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Eczema",
            "emergency_contact": "555-0119",
            "parent_name": "Jose Rodriguez",
            "parent_phone": "555-0120"
        },
        
        # Grade 6 Students
        {
            "first_name": "Daniel",
            "last_name": "Lee",
            "email": "daniel.lee@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0121",
            "parent_name": "James Lee",
            "parent_phone": "555-0122"
        },
        {
            "first_name": "Isabella",
            "last_name": "White",
            "email": "isabella.white@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild scoliosis",
            "emergency_contact": "555-0123",
            "parent_name": "Patricia White",
            "parent_phone": "555-0124"
        },
        {
            "first_name": "Matthew",
            "last_name": "Harris",
            "email": "matthew.harris@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0125",
            "parent_name": "Richard Harris",
            "parent_phone": "555-0126"
        },
        {
            "first_name": "Emma",
            "last_name": "Clark",
            "email": "emma.clark@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Seasonal allergies",
            "emergency_contact": "555-0127",
            "parent_name": "William Clark",
            "parent_phone": "555-0128"
        },
        {
            "first_name": "Andrew",
            "last_name": "Lewis",
            "email": "andrew.lewis@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0129",
            "parent_name": "Robert Lewis",
            "parent_phone": "555-0130"
        },
        {
            "first_name": "Olivia",
            "last_name": "Robinson",
            "email": "olivia.robinson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild ADHD",
            "emergency_contact": "555-0131",
            "parent_name": "Michael Robinson",
            "parent_phone": "555-0132"
        },
        {
            "first_name": "Joshua",
            "last_name": "Walker",
            "email": "joshua.walker@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.BEGINNER,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0133",
            "parent_name": "Christopher Walker",
            "parent_phone": "555-0134"
        },
        {
            "first_name": "Ava",
            "last_name": "Perez",
            "email": "ava.perez@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.ADVANCED,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Asthma",
            "emergency_contact": "555-0135",
            "parent_name": "Anthony Perez",
            "parent_phone": "555-0136"
        },
        
        # Additional diverse students
        {
            "first_name": "Ethan",
            "last_name": "Thompson",
            "email": "ethan.thompson@example.com",
            "date_of_birth": datetime.now() - timedelta(days=11*365 + random.randint(0, 365)),
            "gender": Gender.MALE,
            "grade_level": GradeLevel.FIFTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": None,
            "emergency_contact": "555-0137",
            "parent_name": "Kevin Thompson",
            "parent_phone": "555-0138"
        },
        {
            "first_name": "Mia",
            "last_name": "Moore",
            "email": "mia.moore@example.com",
            "date_of_birth": datetime.now() - timedelta(days=12*365 + random.randint(0, 365)),
            "gender": Gender.FEMALE,
            "grade_level": GradeLevel.SIXTH,
            "level": StudentLevel.INTERMEDIATE,
            "status": StudentStatus.ACTIVE,
            "category": StudentCategory.REGULAR,
            "medical_conditions": "Mild anxiety",
            "emergency_contact": "555-0139",
            "parent_name": "Steven Moore",
            "parent_phone": "555-0140"
        }
    ]

    # Create and add students
    for student_data in students:
        student = Student(**student_data)
        session.add(student)

    session.commit()
    
    # Verify students were created
    result = session.execute(text("SELECT COUNT(*) FROM students"))
    count = result.scalar()
    print(f"Students seeded successfully! Total students in database: {count}")
    
    # Print sample of students for verification
    result = session.execute(text("SELECT id, first_name, last_name, grade_level, level FROM students LIMIT 5"))
    sample_students = result.fetchall()
    print("Sample students:")
    for student in sample_students:
        print(f"  {student.first_name} {student.last_name} - Grade {student.grade_level} - Level: {student.level}") 