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

def seed_class_students(session):
    """Seed the class_students table with realistic enrollment data."""
    print("Seeding class enrollments...")
    
    # Get all classes and students
    classes = session.execute(text("SELECT id, name, max_students, grade_level FROM physical_education_classes ORDER BY id"))
    students = session.execute(text("SELECT id, first_name, last_name, grade_level FROM students ORDER BY id"))
    
    # Create a map of students by grade level
    students_by_grade = {}
    for student in students:
        grade = student.grade_level
        if grade not in students_by_grade:
            students_by_grade[grade] = []
        students_by_grade[grade].append(student.id)
    
    # Create realistic enrollments for each class
    total_enrollments = 0
    for class_row in classes:
        class_id = class_row.id
        class_name = class_row.name
        max_students = class_row.max_students
        grade_level = class_row.grade_level
        
        # Get students in the same grade level
        available_students = students_by_grade.get(grade_level, [])
        
        if not available_students:
            print(f"Warning: No students found for grade level {grade_level} in class {class_name}")
            continue
        
        # Determine how many students to enroll (random between 60-90% of max capacity)
        target_enrollment = min(
            max_students,
            int(max_students * random.uniform(0.6, 0.9))
        )
        
        # Randomly select students for this class
        selected_students = random.sample(
            available_students, 
            min(target_enrollment, len(available_students))
        )
        
        # Create enrollments
        for student_id in selected_students:
            class_student = ClassStudent(
                class_id=class_id,
                student_id=student_id,
                enrollment_date=datetime.now(),
                status="ACTIVE"
            )
            session.add(class_student)
            total_enrollments += 1
    
    session.flush()
    print(f"Class enrollments seeded successfully! Total enrollments: {total_enrollments}") 