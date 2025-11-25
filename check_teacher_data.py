#!/usr/bin/env python3
"""Quick script to check teacher data relationships in the database."""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from app.models.physical_education.class_ import PhysicalEducationClass
from sqlalchemy import func

db = SessionLocal()

print("="*80)
print("TEACHER DATA RELATIONSHIP CHECK")
print("="*80)

# Get all TeacherRegistrations ordered by created_at
print("\n1. TEACHER REGISTRATIONS (by created_at order):")
print("-" * 80)
teachers = db.query(TeacherRegistration).order_by(TeacherRegistration.created_at).limit(10).all()
for i, teacher in enumerate(teachers, 1):
    # Check if User exists
    user = db.query(User).filter(func.lower(User.email) == func.lower(teacher.email)).first()
    user_id = user.id if user else None
    
    # Count classes for this user
    class_count = 0
    if user_id:
        class_count = db.query(PhysicalEducationClass).filter(
            PhysicalEducationClass.teacher_id == user_id
        ).count()
    
    print(f"Teacher {i}: {teacher.first_name} {teacher.last_name}")
    print(f"  Email: {teacher.email}")
    print(f"  TeacherRegistration.id: {teacher.id}")
    print(f"  User.id: {user_id if user_id else '❌ NO USER RECORD'}")
    print(f"  Classes: {class_count}")
    print()

# Get all Users with springfield.edu emails
print("\n2. USERS WITH SPRINGFIELD.EDU EMAILS (seed users):")
print("-" * 80)
seed_users = db.query(User).filter(User.email.ilike("%@springfield.edu")).limit(10).all()
for user in seed_users:
    # Check if TeacherRegistration exists
    teacher_reg = db.query(TeacherRegistration).filter(
        func.lower(TeacherRegistration.email) == func.lower(user.email)
    ).first()
    
    # Count classes
    class_count = db.query(PhysicalEducationClass).filter(
        PhysicalEducationClass.teacher_id == user.id
    ).count()
    
    print(f"User.id={user.id}: {user.first_name} {user.last_name}")
    print(f"  Email: {user.email}")
    print(f"  TeacherRegistration: {'✅ EXISTS' if teacher_reg else '❌ MISSING'}")
    print(f"  Classes: {class_count}")
    print()

# Check classes for period 3
print("\n3. CLASSES WITH 'PERIOD 3' IN SCHEDULE OR NAME:")
print("-" * 80)
period3_classes = db.query(PhysicalEducationClass).filter(
    (PhysicalEducationClass.schedule.ilike("%Period 3%")) |
    (PhysicalEducationClass.schedule.ilike("%3%")) |
    (PhysicalEducationClass.name.ilike("%Period 3%")) |
    (PhysicalEducationClass.name.ilike("%3%"))
).limit(10).all()

for pe_class in period3_classes:
    teacher_user = db.query(User).filter(User.id == pe_class.teacher_id).first()
    print(f"Class: {pe_class.name}")
    print(f"  teacher_id: {pe_class.teacher_id}")
    print(f"  Teacher: {teacher_user.first_name if teacher_user else 'UNKNOWN'} {teacher_user.last_name if teacher_user else ''} ({teacher_user.email if teacher_user else 'NO USER'})")
    print(f"  Schedule: {pe_class.schedule[:100] if pe_class.schedule else 'None'}")
    print()

db.close()

