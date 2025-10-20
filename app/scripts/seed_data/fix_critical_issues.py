#!/usr/bin/env python3
"""
Fix Critical Seeding Issues
Addresses all the critical issues identified in the seeding process:
1. Student count discrepancy (4,868 → 3,754)
2. School-teacher ratio mismatch (8 schools vs 32 teachers)
3. School distribution imbalance (one school with only 85 students)
4. Phase 3 dependency sufficiency
"""

import sys
import os
sys.path.insert(0, '/app')

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
import random
from datetime import datetime, timedelta
import json

def get_current_counts(session: Session) -> dict:
    """Get current counts of all critical tables"""
    counts = {}
    
    # Students
    counts['students'] = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    
    # Schools
    counts['schools'] = session.execute(text("SELECT COUNT(*) FROM schools")).scalar()
    
    # Teachers
    counts['teachers'] = session.execute(text("SELECT COUNT(*) FROM teachers")).scalar()
    
    # PE Teachers
    counts['pe_teachers'] = session.execute(text("SELECT COUNT(*) FROM physical_education_teachers")).scalar()
    
    # Students per school
    school_distribution = session.execute(text("""
        SELECT s.name, s.school_type, COUNT(st.id) as student_count
        FROM schools s
        LEFT JOIN students st ON s.id = st.school_id
        GROUP BY s.id, s.name, s.school_type
        ORDER BY s.name
    """)).fetchall()
    
    counts['school_distribution'] = school_distribution
    
    # Phase 3 dependencies
    phase3_tables = [
        'goals', 'nutrition_plans', 'meals', 'student_health', 
        'fitness_goals', 'student_health_fitness_goals', 
        'physical_education_nutrition_plans', 'progress'
    ]
    
    counts['phase3_dependencies'] = {}
    for table in phase3_tables:
        try:
            counts['phase3_dependencies'][table] = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        except:
            counts['phase3_dependencies'][table] = 0
    
    return counts

def fix_student_count_discrepancy(session: Session) -> dict:
    """Fix the student count discrepancy issue"""
    print("🔧 FIXING STUDENT COUNT DISCREPANCY")
    print("-" * 50)
    
    # Get current student count
    current_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    print(f"📊 Current student count: {current_count:,}")
    
    if current_count >= 4000:
        print("✅ Student count is sufficient")
        return {'students_added': 0}
    
    # Calculate how many students we need to add
    target_count = 4500  # Target for 8 schools
    students_needed = target_count - current_count
    
    print(f"📊 Target student count: {target_count:,}")
    print(f"📊 Students needed: {students_needed:,}")
    
    if students_needed <= 0:
        print("✅ No students need to be added")
        return {'students_added': 0}
    
    # Get school IDs for distribution
    schools = session.execute(text("SELECT id, name, school_type FROM schools ORDER BY name")).fetchall()
    if not schools:
        print("❌ No schools found, cannot add students")
        return {'students_added': 0}
    
    print(f"📊 Found {len(schools)} schools for student distribution")
    
    # Add students with proper school distribution
    students_added = 0
    batch_size = 500
    
    for i in range(0, students_needed, batch_size):
        batch_count = min(batch_size, students_needed - i)
        batch_students = []
        
        for j in range(batch_count):
            # Select school based on type and current distribution
            school = random.choice(schools)
            
            # Generate student data
            student_data = {
                'first_name': f'Student{i + j + 1}',
                'last_name': f'Added{i + j + 1}',
                'email': f'student{i + j + 1}@example.com',
                'date_of_birth': datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                'gender': random.choice(['MALE', 'FEMALE']),
                'grade_level': random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'SIXTH', 'SEVENTH', 'EIGHTH', 'NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']),
                'level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'status': 'ACTIVE',
                'category': random.choice(['REGULAR', 'SPECIAL_NEEDS', 'GIFTED']),
                'medical_conditions': None,
                'emergency_contact': f'Parent{i + j + 1}',
                'parent_name': f'Parent{i + j + 1}',
                'parent_phone': f'973-555-{random.randint(1000, 9999)}',
                'school_id': school.id
            }
            
            batch_students.append(student_data)
        
        # Insert batch
        if batch_students:
            session.execute(text("""
                INSERT INTO students (first_name, last_name, email, date_of_birth, gender, 
                                   grade_level, level, status, category, medical_conditions, 
                                   emergency_contact, parent_name, parent_phone, school_id)
                VALUES (:first_name, :last_name, :email, :date_of_birth, :gender, 
                        :grade_level, :level, :status, :category, :medical_conditions, 
                        :emergency_contact, :parent_name, :parent_phone, :school_id)
            """), batch_students)
            
            students_added += len(batch_students)
            print(f"  ✅ Added batch {i//batch_size + 1}: {len(batch_students)} students")
    
    print(f"✅ Total students added: {students_added:,}")
    return {'students_added': students_added}

def fix_school_distribution(session: Session) -> dict:
    """Fix uneven school distribution"""
    print("\n🔧 FIXING SCHOOL DISTRIBUTION")
    print("-" * 50)
    
    # Get current distribution
    distribution = session.execute(text("""
        SELECT s.id, s.name, s.school_type, COUNT(st.id) as student_count
        FROM schools s
        LEFT JOIN students st ON s.id = st.school_id
        GROUP BY s.id, s.name, s.school_type
        ORDER BY s.name
    """)).fetchall()
    
    print("📊 Current school distribution:")
    for school in distribution:
        print(f"  {school.name} ({school.school_type}): {school.student_count} students")
    
    # Target distribution
    targets = {
        'ELEMENTARY': 450,  # 450 students per elementary school
        'MIDDLE': 350,      # 350 students per middle school  
        'HIGH': 300         # 300 students per high school
    }
    
    # Find schools that need more students
    schools_to_fix = []
    for school in distribution:
        target = targets.get(school.school_type, 300)
        if school.student_count < target:
            needed = target - school.student_count
            schools_to_fix.append({
                'id': school.id,
                'name': school.name,
                'type': school.school_type,
                'current': school.student_count,
                'target': target,
                'needed': needed
            })
    
    if not schools_to_fix:
        print("✅ All schools have adequate student distribution")
        return {'students_moved': 0}
    
    print(f"📊 Schools needing more students: {len(schools_to_fix)}")
    
    # Move students from overpopulated schools to underpopulated ones
    students_moved = 0
    
    for school_info in schools_to_fix:
        print(f"  🔄 Fixing {school_info['name']}: need {school_info['needed']} more students")
        
        # Find students from overpopulated schools
        overpopulated_schools = [s for s in distribution if s.student_count > targets.get(s.school_type, 300)]
        
        if not overpopulated_schools:
            print(f"    ⚠️  No overpopulated schools to move students from")
            continue
        
        # Move students
        students_to_move = min(school_info['needed'], 100)  # Move up to 100 at a time
        
        for overpop_school in overpopulated_schools:
            if students_to_move <= 0:
                break
                
            # Get students from overpopulated school
            students = session.execute(text("""
                SELECT id FROM students 
                WHERE school_id = :school_id 
                ORDER BY RANDOM() 
                LIMIT :limit
            """), {'school_id': overpop_school.id, 'limit': students_to_move}).fetchall()
            
            if students:
                student_ids = [s.id for s in students]
                
                # Move them to the underpopulated school
                session.execute(text("""
                    UPDATE students 
                    SET school_id = :new_school_id 
                    WHERE id = ANY(:student_ids)
                """), {'new_school_id': school_info['id'], 'student_ids': student_ids})
                
                moved_count = len(student_ids)
                students_moved += moved_count
                students_to_move -= moved_count
                
                print(f"    ✅ Moved {moved_count} students from {overpop_school.name}")
    
    print(f"✅ Total students moved: {students_moved:,}")
    return {'students_moved': students_moved}

def fix_teacher_distribution(session: Session) -> dict:
    """Fix teacher distribution for 8 schools"""
    print("\n🔧 FIXING TEACHER DISTRIBUTION")
    print("-" * 50)
    
    # Get current counts
    school_count = session.execute(text("SELECT COUNT(*) FROM schools")).scalar()
    teacher_count = session.execute(text("SELECT COUNT(*) FROM teachers")).scalar()
    pe_teacher_count = session.execute(text("SELECT COUNT(*) FROM physical_education_teachers")).scalar()
    
    print(f"📊 Schools: {school_count}")
    print(f"📊 Teachers: {teacher_count}")
    print(f"📊 PE Teachers: {pe_teacher_count}")
    
    # Calculate needed teachers
    target_teachers_per_school = 6  # 6 teachers per school
    target_total_teachers = school_count * target_teachers_per_school
    teachers_needed = target_total_teachers - teacher_count
    
    print(f"📊 Target total teachers: {target_total_teachers}")
    print(f"📊 Teachers needed: {teachers_needed}")
    
    if teachers_needed <= 0:
        print("✅ Teacher count is adequate")
        return {'teachers_added': 0}
    
    # Add teachers
    teachers_added = 0
    schools = session.execute(text("SELECT id FROM schools ORDER BY id")).fetchall()
    
    for i in range(teachers_needed):
        school_id = random.choice(schools).id
        
        teacher_data = {
            'first_name': f'Teacher{i + 1}',
            'last_name': f'Added{i + 1}',
            'email': f'teacher{i + 1}@example.com',
            'school_id': school_id,
            'subject': random.choice(['MATH', 'SCIENCE', 'ENGLISH', 'HISTORY', 'ART', 'MUSIC']),
            'grade_levels': json.dumps([random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH'])]),
            'is_active': True,
            'hire_date': datetime.now() - timedelta(days=random.randint(30, 365))
        }
        
        session.execute(text("""
            INSERT INTO teachers (first_name, last_name, email, school_id, subject, 
                               grade_levels, is_active, hire_date)
            VALUES (:first_name, :last_name, :email, :school_id, :subject, 
                    :grade_levels, :is_active, :hire_date)
        """), teacher_data)
        
        teachers_added += 1
    
    print(f"✅ Total teachers added: {teachers_added:,}")
    return {'teachers_added': teachers_added}

def fix_phase3_dependencies(session: Session) -> dict:
    """Ensure Phase 3 dependencies have sufficient records"""
    print("\n🔧 FIXING PHASE 3 DEPENDENCIES")
    print("-" * 50)
    
    student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    print(f"📊 Student count: {student_count:,}")
    
    # Target record counts
    targets = {
        'goals': student_count * 2,  # 2 goals per student
        'nutrition_plans': student_count,  # 1 plan per student
        'meals': student_count * 5,  # 5 meals per student
        'student_health': student_count,  # 1 health record per student
        'fitness_goals': student_count,  # 1 fitness goal per student
        'student_health_fitness_goals': student_count,  # 1 per student
        'physical_education_nutrition_plans': student_count // 2,  # 1 per 2 students
        'progress': student_count  # 1 progress record per student
    }
    
    results = {}
    
    for table, target in targets.items():
        current = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        needed = max(0, target - current)
        
        print(f"  📊 {table}: {current:,} current, {target:,} target, {needed:,} needed")
        
        if needed > 0:
            # Add records
            records_added = add_phase3_records(session, table, needed, student_count)
            results[table] = records_added
            print(f"    ✅ Added {records_added:,} records")
        else:
            results[table] = 0
            print(f"    ✅ Sufficient records")
    
    return results

def add_phase3_records(session: Session, table: str, count: int, student_count: int) -> int:
    """Add records to a Phase 3 dependency table"""
    student_ids = session.execute(text("SELECT id FROM students ORDER BY RANDOM() LIMIT 1000")).fetchall()
    student_ids = [s.id for s in student_ids]
    
    if not student_ids:
        return 0
    
    records = []
    for i in range(count):
        student_id = random.choice(student_ids)
        
        if table == 'goals':
            records.append({
                'student_id': student_id,
                'goal_type': random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE']),
                'description': f'Goal {i + 1}',
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'status': 'ACTIVE',
                'is_active': True
            })
        elif table == 'nutrition_plans':
            records.append({
                'student_id': student_id,
                'title': f'Nutrition Plan {i + 1}',
                'description': f'Plan description {i + 1}',
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                'calorie_target': random.randint(1500, 3000)
            })
        elif table == 'meals':
            records.append({
                'student_id': student_id,
                'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                'name': f'Meal {i + 1}',
                'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'total_calories': random.randint(200, 800)
            })
        elif table == 'student_health':
            records.append({
                'student_id': student_id,
                'first_name': f'Student{i + 1}',
                'last_name': f'Health{i + 1}',
                'date_of_birth': datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                'gender': random.choice(['MALE', 'FEMALE']),
                'grade_level': random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH']),
                'health_status': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        elif table == 'fitness_goals':
            records.append({
                'student_id': student_id,
                'goal_type': random.choice(['STRENGTH', 'ENDURANCE', 'FLEXIBILITY', 'COORDINATION']),
                'description': f'Fitness goal {i + 1}',
                'target_value': random.uniform(50, 100),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                'status': 'ACTIVE'
            })
        elif table == 'student_health_fitness_goals':
            records.append({
                'student_id': student_id,
                'goal_type': random.choice(['STRENGTH', 'ENDURANCE', 'FLEXIBILITY', 'COORDINATION']),
                'category': random.choice(['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY']),
                'description': f'Health fitness goal {i + 1}',
                'target_value': random.uniform(50, 100),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                'status': 'ACTIVE',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        elif table == 'physical_education_nutrition_plans':
            records.append({
                'student_id': student_id,
                'plan_name': f'PE Nutrition Plan {i + 1}',
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                'daily_calories': random.randint(1500, 3000),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        elif table == 'progress':
            records.append({
                'student_id': student_id,
                'tracking_period': f'Period {i + 1}',
                'start_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                'end_date': datetime.now() - timedelta(days=random.randint(1, 29)),
                'progress_metrics': json.dumps({"score": random.randint(1, 100)}),
                'is_on_track': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        # Insert in batches
        if len(records) >= 100:
            insert_batch(session, table, records)
            records = []
    
    # Insert remaining records
    if records:
        insert_batch(session, table, records)
    
    return count

def insert_batch(session: Session, table: str, records: list):
    """Insert a batch of records into a table"""
    if not records:
        return
    
    # Get column names from first record
    columns = list(records[0].keys())
    placeholders = ', '.join([f':{col}' for col in columns])
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    
    session.execute(text(query), records)

def main():
    """Main function to fix all critical issues"""
    print("="*70)
    print("🔧 FIXING CRITICAL SEEDING ISSUES")
    print("="*70)
    print("📊 Addressing all critical issues identified")
    print("🎯 Student count, school distribution, teacher ratio, Phase 3 deps")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get current state
        print("\n📊 CURRENT STATE ANALYSIS")
        print("-" * 50)
        counts = get_current_counts(session)
        
        print(f"Students: {counts['students']:,}")
        print(f"Schools: {counts['schools']:,}")
        print(f"Teachers: {counts['teachers']:,}")
        print(f"PE Teachers: {counts['pe_teachers']:,}")
        
        print("\nSchool Distribution:")
        for school in counts['school_distribution']:
            print(f"  {school.name} ({school.school_type}): {school.student_count} students")
        
        print("\nPhase 3 Dependencies:")
        for table, count in counts['phase3_dependencies'].items():
            print(f"  {table}: {count:,} records")
        
        # Fix issues
        print("\n🔧 APPLYING FIXES")
        print("="*70)
        
        # Fix 1: Student count discrepancy
        student_results = fix_student_count_discrepancy(session)
        session.commit()
        
        # Fix 2: School distribution
        distribution_results = fix_school_distribution(session)
        session.commit()
        
        # Fix 3: Teacher distribution
        teacher_results = fix_teacher_distribution(session)
        session.commit()
        
        # Fix 4: Phase 3 dependencies
        phase3_results = fix_phase3_dependencies(session)
        session.commit()
        
        # Final summary
        print("\n📊 FINAL RESULTS")
        print("="*70)
        
        final_counts = get_current_counts(session)
        
        print(f"✅ Students: {final_counts['students']:,} (was {counts['students']:,})")
        print(f"✅ Schools: {final_counts['schools']:,}")
        print(f"✅ Teachers: {final_counts['teachers']:,} (was {counts['teachers']:,})")
        print(f"✅ PE Teachers: {final_counts['pe_teachers']:,}")
        
        print("\nFinal School Distribution:")
        for school in final_counts['school_distribution']:
            print(f"  {school.name} ({school.school_type}): {school.student_count} students")
        
        print("\nFinal Phase 3 Dependencies:")
        for table, count in final_counts['phase3_dependencies'].items():
            print(f"  {table}: {count:,} records")
        
        print("\n🎉 All critical issues have been addressed!")
        
    except Exception as e:
        print(f"❌ Error during fixes: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
