#!/usr/bin/env python3
"""
Quick Restore Script for Critical Test Tables

This script quickly restores only the critical tables needed for communication tests:
- students (with emails)
- physical_education_classes
- physical_education_class_students (enrollments)
- communication_records

This is MUCH faster than running the full seed script (minutes vs hours).
"""

import os
import sys
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.physical_education.student.models import Student
from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent
from app.models.communication.models import CommunicationRecord, CommunicationType, MessageType, CommunicationChannel, CommunicationStatus
from app.models.physical_education.pe_enums.pe_types import GradeLevel, ClassType, ClassStatus
from app.models.core.core_models import Gender

def quick_restore_critical_tables():
    """Quickly restore only critical tables for tests."""
    print("=" * 70)
    print("QUICK RESTORE: Critical Test Tables")
    print("=" * 70)
    print("Restoring: students, physical_education_classes, enrollments, communication_records")
    print()
    
    session = SessionLocal()
    try:
        # Check if data already exists
        student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
        if student_count > 0:
            print(f"⚠️  Students already exist ({student_count} records)")
            response = input("Do you want to delete and recreate? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
            print("Deleting existing data...")
            session.execute(text("DELETE FROM physical_education_class_students"))
            session.execute(text("DELETE FROM communication_records"))
            session.execute(text("DELETE FROM physical_education_classes"))
            session.execute(text("DELETE FROM students"))
            session.commit()
            print("✅ Existing data deleted")
        
        # Get required dependencies
        print("\n📋 Checking dependencies...")
        user_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if user_count == 0:
            print("❌ ERROR: No users found. Please run full seed script first to create users.")
            return
        
        school_count = session.execute(text("SELECT COUNT(*) FROM schools")).scalar()
        if school_count == 0:
            print("❌ ERROR: No schools found. Please run full seed script first to create schools.")
            return
        
        # Get user IDs that are teachers (teachers table has user_id column)
        teacher_ids = [row[0] for row in session.execute(text("SELECT user_id FROM teachers LIMIT 10")).fetchall()]
        if not teacher_ids:
            # Fallback: just use any user IDs
            teacher_ids = [row[0] for row in session.execute(text("SELECT id FROM users LIMIT 10")).fetchall()]
            if not teacher_ids:
                print("❌ ERROR: No users found. Please run full seed script first to create users.")
                return
            print(f"⚠️  No teachers found, using user IDs instead: {teacher_ids}")
        else:
            print(f"✅ Found {len(teacher_ids)} teachers")
        
        school_ids = [row[0] for row in session.execute(text("SELECT id FROM schools LIMIT 6")).fetchall()]
        print(f"✅ Found {user_count} users, {school_count} schools, {len(teacher_ids)} teachers")
        
        # 1. Create students (minimal set - 100 students for speed)
        print("\n👥 Creating 100 students...")
        students = []
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Sage", "River",
                      "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Christopher",
                      "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        grade_levels = list(GradeLevel)
        
        for i in range(100):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            grade = random.choice(grade_levels)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@springfield.edu"
            
            student = Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                date_of_birth=datetime.now() - timedelta(days=365 * (5 + i % 13)),
                grade_level=grade,
                gender=random.choice([Gender.MALE, Gender.FEMALE, Gender.OTHER]) if hasattr(Gender, 'MALE') else None,
                parent_name=f"Parent {last_name}",
                parent_phone=f"973-555-{1000 + i:04d}"
            )
            students.append(student)
            session.add(student)
        
        session.flush()
        print(f"✅ Created {len(students)} students")
        
        # Get student IDs
        student_ids = [s.id for s in students]
        
        # 2. Create physical education classes (minimal set - 10 classes)
        print("\n🏫 Creating 10 physical education classes...")
        classes = []
        current_year = datetime.now().year
        start_date = datetime(current_year, 9, 1)
        end_date = datetime(current_year + 1, 6, 15)
        
        for i in range(10):
            grade = random.choice(grade_levels)
            pe_class = PhysicalEducationClass(
                name=f"PE Class {i+1}",
                description=f"Physical Education Class {i+1}",
                class_type=ClassType.REGULAR,
                teacher_id=random.choice(teacher_ids),
                grade_level=grade,
                max_students=25,
                start_date=start_date,
                end_date=end_date
            )
            classes.append(pe_class)
            session.add(pe_class)
        
        session.flush()
        print(f"✅ Created {len(classes)} classes")
        
        # Get class IDs
        class_ids = [c.id for c in classes]
        
        # 3. Create enrollments (assign students to classes)
        print("\n📚 Creating enrollments...")
        enrollments = []
        for student_id in student_ids:
            # Each student enrolled in 1-2 classes
            num_classes = random.randint(1, 2)
            selected_classes = random.sample(class_ids, min(num_classes, len(class_ids)))
            for class_id in selected_classes:
                enrollment = ClassStudent(
                    student_id=student_id,
                    class_id=class_id,
                    enrollment_date=start_date,
                    status="active"
                )
                enrollments.append(enrollment)
                session.add(enrollment)
        
        session.flush()
        print(f"✅ Created {len(enrollments)} enrollments")
        
        # 4. Create communication records (minimal set - 50 records)
        print("\n📧 Creating 50 communication records...")
        for i in range(50):
            student_id = random.choice(student_ids)
            comm_record = CommunicationRecord(
                communication_type=CommunicationType.PARENT,
                message_type=MessageType.PROGRESS_UPDATE,
                channels=[CommunicationChannel.EMAIL],
                student_id=student_id,
                recipient_email=f"parent{student_id}@email.com",
                recipient_name=f"Parent of Student {student_id}",
                subject=f"Progress Update {i+1}",
                message=f"Test communication message {i+1}",
                status=CommunicationStatus.SENT,
                sent_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(comm_record)
        
        session.flush()
        print(f"✅ Created 50 communication records")
        
        # Commit everything
        session.commit()
        print("\n✅ All critical tables restored successfully!")
        
        # Verify
        print("\n📊 Verification:")
        student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
        class_count = session.execute(text("SELECT COUNT(*) FROM physical_education_classes")).scalar()
        enrollment_count = session.execute(text("SELECT COUNT(*) FROM physical_education_class_students")).scalar()
        comm_count = session.execute(text("SELECT COUNT(*) FROM communication_records")).scalar()
        
        print(f"  Students: {student_count}")
        print(f"  Classes: {class_count}")
        print(f"  Enrollments: {enrollment_count}")
        print(f"  Communication Records: {comm_count}")
        print("\n✅ Quick restore complete! You can now run tests.")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    quick_restore_critical_tables()

