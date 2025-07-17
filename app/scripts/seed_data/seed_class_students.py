from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.core.core_models import (
    StudentType,
    ClassType
)
from app.models.physical_education.pe_enums.pe_types import ClassStatus
from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent

async def seed_class_students(session):
    """Seed the class_students table with initial data."""
    # Get all students
    students = await session.execute(text("SELECT id, first_name, last_name FROM students"))
    student_map = {f"{row.first_name} {row.last_name}": row.id for row in students}
    
    # Define class-student mappings using student names
    class_student_mappings = [
        # Grade 5 Regular PE (PE501)
        {"class_id": 501, "student_name": "John Smith", "status": "active"},
        {"class_id": 501, "student_name": "Michael Brown", "status": "active"},
        {"class_id": 501, "student_name": "David Wilson", "status": "active"},
        {"class_id": 501, "student_name": "Jessica Taylor", "status": "active"},
        
        # Grade 6 Regular PE (PE601)
        {"class_id": 601, "student_name": "Emily Johnson", "status": "active"},
        {"class_id": 601, "student_name": "Sarah Davis", "status": "active"},
        {"class_id": 601, "student_name": "Robert Anderson", "status": "active"},
        {"class_id": 601, "student_name": "Jennifer Martinez", "status": "active"},
        
        # Grade 5 Advanced PE (PE502)
        {"class_id": 502, "student_name": "John Smith", "status": "active"},
        {"class_id": 502, "student_name": "David Wilson", "status": "active"},
        
        # Grade 6 Advanced PE (PE602)
        {"class_id": 602, "student_name": "Emily Johnson", "status": "active"},
        {"class_id": 602, "student_name": "Robert Anderson", "status": "active"}
    ]

    # Create class_student entries using actual student IDs
    for mapping in class_student_mappings:
        student_id = student_map.get(mapping["student_name"])
        if student_id is None:
            print(f"Warning: Student {mapping['student_name']} not found in database")
            continue
            
        class_student = ClassStudent(
            class_id=mapping["class_id"],
            student_id=student_id,
            enrollment_date=datetime.now(),
            status=mapping["status"]
        )
        session.add(class_student)

    await session.flush()
    print("Class students seeded successfully!") 