#!/usr/bin/env python3
"""
Fix Remaining Health Tables - Simple Targeted Approach
Fix the remaining health tables that didn't get scaled properly
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

def get_student_count(session: Session) -> int:
    """Get total student count from database"""
    result = session.execute(text("SELECT COUNT(*) FROM students"))
    return result.scalar()

def get_student_ids(session: Session) -> list:
    """Get all student IDs from database"""
    result = session.execute(text("SELECT id FROM students ORDER BY id"))
    return [row[0] for row in result.fetchall()]

def get_user_ids(session: Session) -> list:
    """Get all user IDs from database"""
    result = session.execute(text("SELECT id FROM users ORDER BY id"))
    return [row[0] for row in result.fetchall()]

def fix_health_checks(session: Session, student_ids: list, user_ids: list, student_count: int):
    """Fix health_checks table - add missing records"""
    print("🔧 FIXING health_checks...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_checks")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} health_checks records...")
        
        # Add records in smaller batches to avoid issues
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                health_check = {
                    'student_id': random.choice(student_ids),
                    'check_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY']),
                    'status': random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'NEEDS_IMPROVEMENT', 'ON_HOLD', 'CANCELLED']),
                    'performed_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'performed_by': random.choice(user_ids),
                    'notes': f'Health check notes for check {i + 1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(health_check)
            
            try:
                session.execute(text("""
                    INSERT INTO health_checks (student_id, check_type, status, performed_at, performed_by, notes, created_at, updated_at)
                    VALUES (:student_id, :check_type, :status, :performed_at, :performed_by, :notes, :created_at, :updated_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of health_checks")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ health_checks already has {current_count} records")

def fix_student_health(session: Session, student_ids: list, student_count: int):
    """Fix student_health table - add missing records"""
    print("🔧 FIXING student_health...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} student_health records...")
        
        # Add records in smaller batches
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                student_health_record = {
                    'student_id': random.choice(student_ids),
                    'first_name': f'Student{i + 1}',
                    'last_name': f'Health{i + 1}',
                    'date_of_birth': datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                    'gender': random.choice(['Male', 'Female', 'Other']),
                    'grade_level': random.choice(['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']),
                    'student_metadata': '{"source": "system", "type": "health_record"}',
                    'health_status': random.choice(['Healthy', 'Under Observation', 'Needs Attention', 'Critical']),
                    'health_notes': f'Health notes for student {i + 1}',
                    'health_metadata': '{"conditions": "None", "priority": "normal"}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                batch_records.append(student_health_record)
            
            try:
                session.execute(text("""
                    INSERT INTO student_health (student_id, first_name, last_name, date_of_birth, gender, grade_level,
                                             student_metadata, health_status, health_notes, health_metadata,
                                             created_at, updated_at, last_accessed_at, archived_at, deleted_at,
                                             scheduled_deletion_at, retention_period)
                    VALUES (:student_id, :first_name, :last_name, :date_of_birth, :gender, :grade_level,
                           :student_metadata, :health_status, :health_notes, :health_metadata,
                           :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                           :scheduled_deletion_at, :retention_period)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of student_health")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ student_health already has {current_count} records")

def fix_fitness_assessments(session: Session, student_ids: list, student_count: int):
    """Fix fitness_assessments table - add missing records"""
    print("🔧 FIXING fitness_assessments...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} fitness_assessments records...")
        
        # Add records in smaller batches
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                fitness_assessment = {
                    'student_id': random.choice(student_ids),
                    'assessment_type': random.choice(['Initial', 'Progress', 'Final', 'Quarterly', 'Annual']),
                    'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'score': round(random.uniform(60, 100), 2),
                    'assessment_notes': f'Assessment notes for student {i + 1}',
                    'assessment_metadata': '{"source": "system", "type": "fitness"}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(fitness_assessment)
            
            try:
                session.execute(text("""
                    INSERT INTO fitness_assessments (student_id, assessment_type, assessment_date, score, 
                                                   assessment_notes, assessment_metadata, created_at, updated_at)
                    VALUES (:student_id, :assessment_type, :assessment_date, :score, 
                           :assessment_notes, :assessment_metadata, :created_at, :updated_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of fitness_assessments")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ fitness_assessments already has {current_count} records")

def main():
    """Main function to fix remaining health tables"""
    print("="*70)
    print("🔧 FIXING REMAINING HEALTH TABLES")
    print("="*70)
    print("📊 Fixing health tables that didn't get scaled properly")
    print("🎯 Target: 3,877 students across all health tables")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_ids = get_student_ids(session)
        user_ids = get_user_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Student IDs available: {len(student_ids):,}")
        print(f"📊 User IDs available: {len(user_ids):,}")
        
        if not student_ids:
            print("❌ No students found, cannot proceed with scaling")
            return
        
        # Fix each table individually
        fix_health_checks(session, student_ids, user_ids, student_count)
        fix_student_health(session, student_ids, student_count)
        fix_fitness_assessments(session, student_ids, student_count)
        
        print("\n🎉 Health table fixes completed!")
        
    except Exception as e:
        print(f"❌ Error during fixing: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
