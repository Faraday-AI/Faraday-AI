#!/usr/bin/env python3
"""
Seed minimal test student data for beta system testing

This seeds test data for:
- beta_students: Test data for beta teacher student management API tests
- drivers_ed_student_progress: Sample progress for Drivers Ed curriculum testing
- health_student_progress: Sample progress for Health curriculum testing

Only seeds if TEST_MODE environment variable is set or explicitly requested.
"""

import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import random

def seed_test_beta_students(session: Session, count: int = 10) -> None:
    """Seed test beta students for API testing"""
    print(f"🔄 Seeding {count} test beta students...")
    
    # Get a beta teacher to associate students with
    teacher_result = session.execute(text("""
        SELECT id FROM teacher_registrations LIMIT 1
    """)).first()
    
    if not teacher_result:
        print("⚠️  No beta teachers found, skipping beta_students seeding")
        return
    
    teacher_id = teacher_result[0]
    
    # Create test students
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Sage", "River"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    grade_levels = ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"]
    genders = ["MALE", "FEMALE", "OTHER"]
    
    created = 0
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"test.student.{i+1}@beta.test"
        
        # Ensure unique email
        existing = session.execute(text("""
            SELECT COUNT(*) FROM beta_students WHERE email = :email
        """), {"email": email}).scalar()
        
        if existing > 0:
            email = f"test.student.{uuid.uuid4().hex[:8]}@beta.test"
        
        session.execute(text("""
            INSERT INTO beta_students (
                id, created_by_teacher_id, first_name, last_name, email,
                date_of_birth, gender, grade_level, status, level, category,
                height_cm, weight_kg, medical_conditions, emergency_contact,
                parent_name, parent_phone, created_at, updated_at
            ) VALUES (
                :id, :teacher_id, :first_name, :last_name, :email,
                :dob, :gender, :grade_level, :status, :level, :category,
                :height, :weight, :medical, :emergency, :parent_name, :parent_phone,
                :created_at, :updated_at
            ) ON CONFLICT (email) DO NOTHING
        """), {
            "id": str(uuid.uuid4()),
            "teacher_id": teacher_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "dob": datetime.now() - timedelta(days=random.randint(2190, 5475)),  # 6-15 years old
            "gender": random.choice(genders),
            "grade_level": random.choice(grade_levels),
            "status": "ACTIVE",
            "level": "BEGINNER",
            "category": "REGULAR",
            "height": random.uniform(100, 180),
            "weight": random.uniform(20, 80),
            "medical": None if random.random() > 0.2 else "No known conditions",
            "emergency": f"+1-555-{random.randint(1000, 9999)}",
            "parent_name": f"{first_name} Parent",
            "parent_phone": f"+1-555-{random.randint(1000, 9999)}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        created += 1
    
    print(f"   ✅ Created {created} test beta students")
    session.flush()

def seed_test_drivers_ed_progress(session: Session, count: int = 5) -> None:
    """Seed test Drivers Ed student progress"""
    print(f"🔄 Seeding {count} test Drivers Ed progress records...")
    
    # Get main students (drivers_ed_student_progress uses integer student_id from main students table)
    student_result = session.execute(text("""
        SELECT id FROM students LIMIT :count
    """), {"count": count}).fetchall()
    
    if not student_result:
        print("   ⚠️  No students found in main students table, skipping Drivers Ed progress seeding")
        return
    
    # Get Drivers Ed curriculum units (UUID)
    units_result = session.execute(text("""
        SELECT id FROM drivers_ed_curriculum_units LIMIT 5
    """)).fetchall()
    
    if not units_result:
        print("   ⚠️  No Drivers Ed curriculum units found, skipping progress seeding")
        return
    
    # Get Drivers Ed lesson plans (optional - UUID)
    lesson_plans_result = session.execute(text("""
        SELECT id FROM drivers_ed_lesson_plans LIMIT 5
    """)).fetchall()
    
    completion_statuses = ["not_started", "in_progress", "completed", "needs_remediation"]
    
    created = 0
    for student_id_tuple in student_result:
        student_id = student_id_tuple[0]  # integer
        unit_id = random.choice(units_result)[0] if units_result else None
        lesson_plan_id = random.choice(lesson_plans_result)[0] if lesson_plans_result else None
        
        status = random.choice(completion_statuses)
        score = random.randint(60, 100) if status in ["completed", "in_progress"] else None
        max_score = 100 if score else None
        completion_date = datetime.utcnow() - timedelta(days=random.randint(1, 30)) if status == "completed" else None
        
        session.execute(text("""
            INSERT INTO drivers_ed_student_progress (
                id, student_id, lesson_plan_id, curriculum_unit_id, completion_status,
                completion_date, score, max_score, instructor_notes, student_reflection,
                remediation_required, remediation_notes, created_at, updated_at
            ) VALUES (
                :id, :student_id, :lesson_plan_id, :unit_id, :status, :completion_date,
                :score, :max_score, :instructor_notes, :student_reflection,
                :remediation_required, :remediation_notes, :created_at, :updated_at
            ) ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "lesson_plan_id": str(lesson_plan_id) if lesson_plan_id else None,
            "unit_id": str(unit_id) if unit_id else None,
            "status": status,
            "completion_date": completion_date,
            "score": score,
            "max_score": max_score,
            "instructor_notes": f"Test progress for student {student_id}",
            "student_reflection": None if status == "not_started" else f"Reflection on unit progress",
            "remediation_required": status == "needs_remediation",
            "remediation_notes": f"Remediation notes" if status == "needs_remediation" else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        created += 1
    
    print(f"   ✅ Created {created} Drivers Ed progress records")
    session.flush()

def seed_test_health_progress(session: Session, count: int = 5) -> None:
    """Seed test Health curriculum student progress"""
    print(f"🔄 Seeding {count} test Health progress records...")
    
    # Get beta students (health_student_progress uses UUID student_id, can be from beta_students)
    beta_student_result = session.execute(text(f"""
        SELECT id FROM beta_students LIMIT {count}
    """)).fetchall()
    
    # Fallback to main students if no beta students (though schema expects UUID)
    if not beta_student_result:
        print("   ⚠️  No beta_students found, skipping Health progress seeding (requires UUID student_id)")
        return
    
    # Get Health curriculum units (UUID)
    units_result = session.execute(text("""
        SELECT id FROM health_curriculum_units LIMIT 5
    """)).fetchall()
    
    if not units_result:
        print("   ⚠️  No Health curriculum units found, skipping progress seeding")
        return
    
    # Get Health lesson plans (optional - UUID)
    lesson_plans_result = session.execute(text("""
        SELECT id FROM health_lesson_plans LIMIT 5
    """)).fetchall()
    
    completion_statuses = ["not_started", "in_progress", "completed", "needs_remediation"]
    
    created = 0
    for student_id_tuple in beta_student_result:
        student_id = student_id_tuple[0]  # UUID
        unit_id = random.choice(units_result)[0] if units_result else None
        lesson_plan_id = random.choice(lesson_plans_result)[0] if lesson_plans_result else None
        
        status = random.choice(completion_statuses)
        score = random.randint(60, 100) if status in ["completed", "in_progress"] else None
        max_score = 100 if score else None
        completion_date = datetime.utcnow() - timedelta(days=random.randint(1, 30)) if status == "completed" else None
        
        session.execute(text("""
            INSERT INTO health_student_progress (
                id, student_id, lesson_plan_id, curriculum_unit_id, completion_status,
                completion_date, score, max_score, instructor_notes, student_reflection,
                remediation_required, remediation_notes, created_at, updated_at
            ) VALUES (
                :id, :student_id, :lesson_plan_id, :unit_id, :status, :completion_date,
                :score, :max_score, :instructor_notes, :student_reflection,
                :remediation_required, :remediation_notes, :created_at, :updated_at
            ) ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid.uuid4()),
            "student_id": str(student_id),  # Convert UUID to string
            "lesson_plan_id": str(lesson_plan_id) if lesson_plan_id else None,
            "unit_id": str(unit_id) if unit_id else None,
            "status": status,
            "completion_date": completion_date,
            "score": score,
            "max_score": max_score,
            "instructor_notes": f"Test progress for student {student_id}",
            "student_reflection": None if status == "not_started" else f"Reflection on unit progress",
            "remediation_required": status == "needs_remediation",
            "remediation_notes": f"Remediation notes" if status == "needs_remediation" else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        created += 1
    
    print(f"   ✅ Created {created} Health progress records")
    session.flush()

def seed_test_student_data(session: Session, for_tests: bool = False) -> None:
    """
    Seed minimal test student data for testing purposes
    
    Args:
        session: Database session
        for_tests: If True, always seed. If False, only seed if TEST_MODE env var is set
    """
    test_mode = os.getenv("TEST_MODE", "").lower() == "true"
    seed_for_tests = os.getenv("SEED_TEST_STUDENT_DATA", "").lower() == "true"
    
    if not (for_tests or test_mode or seed_for_tests):
        print("ℹ️  Skipping test student data seeding (set SEED_TEST_STUDENT_DATA=true to enable)")
        return
    
    print("\n📚 Seeding test student data for testing purposes...")
    print("-" * 80)
    
    try:
        seed_test_beta_students(session, count=10)
        seed_test_drivers_ed_progress(session, count=5)
        seed_test_health_progress(session, count=5)
        
        print("\n✅ Test student data seeded successfully!")
        
    except Exception as e:
        print(f"⚠️  Error seeding test student data: {e}")
        # Don't raise - this is optional test data

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        seed_test_student_data(session, for_tests=True)
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

