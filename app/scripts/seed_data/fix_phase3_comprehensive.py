#!/usr/bin/env python3
"""
Fix Phase 3 Comprehensive - Ensure ALL students have health records and scale properly
This script addresses the root cause: missing student_health records for most students
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

def get_all_student_ids(session: Session) -> list:
    """Get ALL student IDs from students table"""
    result = session.execute(text("SELECT id FROM students ORDER BY id"))
    return [row[0] for row in result.fetchall()]

def ensure_all_students_have_health_records(session: Session, student_ids: list):
    """Ensure ALL students have health records - this is the root cause fix"""
    print("🔧 ENSURING ALL STUDENTS HAVE HEALTH RECORDS...")
    
    # Check current student_health count
    current_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
    print(f"  📊 Current student_health records: {current_count:,}")
    print(f"  📊 Total students: {len(student_ids):,}")
    
    if current_count >= len(student_ids):
        print("  ✅ All students already have health records")
        return
    
    # Find students missing health records
    missing_students = session.execute(text("""
        SELECT s.id FROM students s 
        LEFT JOIN student_health sh ON s.id = sh.student_id 
        WHERE sh.student_id IS NULL
        ORDER BY s.id
    """)).fetchall()
    
    missing_count = len(missing_students)
    print(f"  📊 Students missing health records: {missing_count:,}")
    
    if missing_count == 0:
        print("  ✅ No students missing health records")
        return
    
    # Create health records for missing students
    print(f"  📝 Creating health records for {missing_count:,} students...")
    
    batch_size = 1000
    for i in range(0, missing_count, batch_size):
        batch_end = min(i + batch_size, missing_count)
        batch_records = []
        
        for j in range(i, batch_end):
            student_id = missing_students[j][0]
            health_record = {
                'student_id': student_id,
                'first_name': f'Student{student_id}',
                'last_name': f'LastName{student_id}',
                'date_of_birth': datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                'gender': random.choice(['Male', 'Female', 'Other']),
                'grade_level': random.choice(['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']),
                'student_metadata': json.dumps({'source': 'system', 'type': 'health_record'}),
                'health_status': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                'health_notes': f'Health notes for student {student_id}',
                'health_metadata': json.dumps({'source': 'system', 'type': 'health_metadata'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            batch_records.append(health_record)
        
        try:
            session.execute(text("""
                INSERT INTO student_health (student_id, first_name, last_name, date_of_birth, gender, 
                                          grade_level, student_metadata, health_status, health_notes, 
                                          health_metadata, created_at, updated_at, last_accessed_at, 
                                          archived_at, deleted_at, scheduled_deletion_at, retention_period)
                VALUES (:student_id, :first_name, :last_name, :date_of_birth, :gender, 
                       :grade_level, :student_metadata, :health_status, :health_notes, 
                       :health_metadata, :created_at, :updated_at, :last_accessed_at, 
                       :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
            """), batch_records)
            session.commit()
            print(f"  ✅ Created health records for batch {i+1}-{batch_end} ({len(batch_records)} records)")
        except Exception as e:
            print(f"  ❌ Error creating health records for batch {i+1}-{batch_end}: {e}")
            session.rollback()
    
    # Verify all students now have health records
    final_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
    print(f"  ✅ Final student_health count: {final_count:,}")

def scale_fitness_assessments(session: Session, student_count: int):
    """Scale fitness_assessments to match student count"""
    print("🔧 SCALING fitness_assessments...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed:,} fitness_assessments records...")
        
        # Get all student IDs that have health records
        student_health_ids = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id")).fetchall()
        student_health_ids = [row[0] for row in student_health_ids]
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping fitness_assessments")
            return
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
                fitness_assessment = {
                    'student_id': student_id,
                    'assessment_type': random.choice(['Initial', 'Progress', 'Final', 'Quarterly', 'Annual']),
                    'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'score': round(random.uniform(60, 100), 2),
                    'assessment_notes': f'Assessment notes for student {student_id}',
                    'assessment_metadata': json.dumps({'source': 'system', 'type': 'fitness'}),
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
                print(f"  ✅ Added fitness_assessments batch {batch_start+1}-{batch_end}")
            except Exception as e:
                print(f"  ❌ Error in fitness_assessments batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ fitness_assessments already has {current_count:,} records")

def scale_student_health_fitness_goals(session: Session, student_count: int):
    """Scale student_health_fitness_goals to match student count"""
    print("🔧 SCALING student_health_fitness_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed:,} student_health_fitness_goals records...")
        
        # Get all student IDs that have health records
        student_health_ids = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id")).fetchall()
        student_health_ids = [row[0] for row in student_health_ids]
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping student_health_fitness_goals")
            return
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
                student_hf_goal = {
                    'student_id': student_id,
                    'goal_type': random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']),
                    'category': random.choice(['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION', 'SPEED', 'AGILITY', 'POWER', 'SPORTS_SPECIFIC', 'GENERAL_FITNESS', 'WEIGHT_MANAGEMENT']),
                    'timeframe': random.choice(['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'ACADEMIC_YEAR', 'CUSTOM']),
                    'description': f'Fitness goal description for student {student_id}',
                    'target_value': round(random.uniform(10, 100), 2),
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'completion_date': None,
                    'status': random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD']),
                    'priority': random.randint(1, 5),
                    'notes': f'Goal notes for student {student_id}',
                    'goal_metadata': json.dumps({'source': 'system', 'type': 'fitness_goal'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(student_hf_goal)
            
            try:
                session.execute(text("""
                    INSERT INTO student_health_fitness_goals (student_id, goal_type, category, timeframe, description, 
                                                            target_value, target_date, completion_date, status, priority, 
                                                            notes, goal_metadata, created_at, updated_at)
                    VALUES (:student_id, :goal_type, :category, :timeframe, :description, 
                           :target_value, :target_date, :completion_date, :status, :priority, 
                           :notes, :goal_metadata, :created_at, :updated_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added student_health_fitness_goals batch {batch_start+1}-{batch_end}")
            except Exception as e:
                print(f"  ❌ Error in student_health_fitness_goals batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ student_health_fitness_goals already has {current_count:,} records")

def scale_health_alerts(session: Session, student_count: int):
    """Scale health_alerts - 1 per 10 students"""
    print("🔧 SCALING health_alerts...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_alerts")).scalar()
    target_count = student_count // 10  # 1 alert per 10 students
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed:,} health_alerts records...")
        
        # Get all student IDs that have health records
        student_health_ids = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id")).fetchall()
        student_health_ids = [row[0] for row in student_health_ids]
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping health_alerts")
            return
        
        batch_records = []
        for i in range(needed):
            student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
            health_alert = {
                'student_id': student_id,
                'condition_id': None,  # Can be null
                'alert_type': random.choice(['RISK_THRESHOLD', 'EMERGENCY', 'PROTOCOL', 'MAINTENANCE', 'WEATHER']),
                'message': f'Health alert message for student {student_id}',
                'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'is_active': random.choice([True, False]),
                'resolved_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                'notes': f'Alert notes for student {student_id}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            batch_records.append(health_alert)
        
        try:
            session.execute(text("""
                INSERT INTO health_alerts (student_id, condition_id, alert_type, message, severity, is_active, 
                                         resolved_at, notes, created_at, updated_at, last_accessed_at, 
                                         archived_at, deleted_at, scheduled_deletion_at, retention_period)
                VALUES (:student_id, :condition_id, :alert_type, :message, :severity, :is_active, 
                       :resolved_at, :notes, :created_at, :updated_at, :last_accessed_at, 
                       :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
            """), batch_records)
            session.commit()
            print(f"  ✅ Added {len(batch_records):,} health_alerts records")
        except Exception as e:
            print(f"  ❌ Error adding health_alerts: {e}")
            session.rollback()
    else:
        print(f"  ✅ health_alerts already has {current_count:,} records")

def scale_physical_education_nutrition_logs(session: Session, student_count: int):
    """Scale physical_education_nutrition_logs - 3 per student"""
    print("🔧 SCALING physical_education_nutrition_logs...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_logs")).scalar()
    target_count = student_count * 3
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed:,} physical_education_nutrition_logs records...")
        
        # Get all student IDs that have health records
        student_health_ids = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id")).fetchall()
        student_health_ids = [row[0] for row in student_health_ids]
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping physical_education_nutrition_logs")
            return
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
                pe_nutrition_log = {
                    'student_id': student_id,
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                    'log_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'calories': random.randint(200, 800),
                    'protein': round(random.uniform(10, 50), 2),
                    'carbohydrates': round(random.uniform(20, 100), 2),
                    'fats': round(random.uniform(5, 30), 2),
                    'hydration': round(random.uniform(200, 1000), 2),
                    'notes': f'PE nutrition log notes for student {student_id}',
                    'log_metadata': json.dumps({'source': 'system', 'type': 'pe_nutrition'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                batch_records.append(pe_nutrition_log)
            
            try:
                session.execute(text("""
                    INSERT INTO physical_education_nutrition_logs (student_id, meal_type, log_date, calories, protein, 
                                                                 carbohydrates, fats, hydration, notes, log_metadata, 
                                                                 created_at, updated_at, last_accessed_at, archived_at, 
                                                                 deleted_at, scheduled_deletion_at, retention_period)
                    VALUES (:student_id, :meal_type, :log_date, :calories, :protein, 
                           :carbohydrates, :fats, :hydration, :notes, :log_metadata, 
                           :created_at, :updated_at, :last_accessed_at, :archived_at, 
                           :deleted_at, :scheduled_deletion_at, :retention_period)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added physical_education_nutrition_logs batch {batch_start+1}-{batch_end}")
            except Exception as e:
                print(f"  ❌ Error in physical_education_nutrition_logs batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ physical_education_nutrition_logs already has {current_count:,} records")

def main():
    """Main function to fix Phase 3 comprehensively"""
    print("="*70)
    print("🔧 FIXING PHASE 3 COMPREHENSIVELY - ROOT CAUSE SOLUTION")
    print("="*70)
    print("📊 Ensuring ALL students have health records first")
    print("📊 Then scaling all health tables to full student population")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_ids = get_all_student_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Student IDs available: {len(student_ids):,}")
        
        if not student_ids:
            print("❌ No students found, cannot proceed with scaling")
            return
        
        # STEP 1: Ensure ALL students have health records (root cause fix)
        ensure_all_students_have_health_records(session, student_ids)
        
        # STEP 2: Scale all health tables to full student population
        scale_fitness_assessments(session, student_count)
        scale_student_health_fitness_goals(session, student_count)
        scale_health_alerts(session, student_count)
        scale_physical_education_nutrition_logs(session, student_count)
        
        # Final verification
        print("\n📊 FINAL VERIFICATION")
        print("-" * 50)
        student_health_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        fitness_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
        goals_count = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals")).scalar()
        alerts_count = session.execute(text("SELECT COUNT(*) FROM health_alerts")).scalar()
        nutrition_logs_count = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_logs")).scalar()
        
        print(f"✅ student_health: {student_health_count:,} records")
        print(f"✅ fitness_assessments: {fitness_count:,} records")
        print(f"✅ student_health_fitness_goals: {goals_count:,} records")
        print(f"✅ health_alerts: {alerts_count:,} records")
        print(f"✅ physical_education_nutrition_logs: {nutrition_logs_count:,} records")
        
        print("\n🎉 Phase 3 comprehensive fix completed!")
        
    except Exception as e:
        print(f"❌ Error during Phase 3 fix: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
