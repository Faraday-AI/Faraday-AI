#!/usr/bin/env python3
"""
Fix Final 3 Tables - Foreign Key Constraint Resolution
Fix fitness_assessments, student_health_fitness_goals, and health_alerts using only valid student_health IDs
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

def get_student_health_ids(session: Session) -> list:
    """Get all student IDs that have health records - these are the only valid IDs"""
    result = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id"))
    return [row[0] for row in result.fetchall()]

def fix_fitness_assessments(session: Session, student_health_ids: list, student_count: int):
    """Fix fitness_assessments - use only students with health records"""
    print("🔧 FIXING fitness_assessments...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} fitness_assessments records...")
        
        # Use only students that have health records
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping fitness_assessments")
            return
        
        # Create one fitness assessment per student with health record
        batch_records = []
        for i, student_id in enumerate(student_health_ids[:needed]):
            fitness_assessment = {
                'student_id': student_id,  # Use actual student_health IDs in order
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
            print(f"  ✅ Added {len(batch_records)} fitness_assessments records")
        except Exception as e:
            print(f"  ❌ Error adding fitness_assessments: {e}")
            session.rollback()
    else:
        print(f"  ✅ fitness_assessments already has {current_count} records")

def fix_student_health_fitness_goals(session: Session, student_health_ids: list, student_count: int):
    """Fix student_health_fitness_goals - use only students with health records"""
    print("🔧 FIXING student_health_fitness_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} student_health_fitness_goals records...")
        
        # Use only students that have health records
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping student_health_fitness_goals")
            return
        
        # Create one fitness goal per student with health record
        batch_records = []
        for i, student_id in enumerate(student_health_ids[:needed]):
            student_hf_goal = {
                'student_id': student_id,  # Use actual student_health IDs in order
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
            print(f"  ✅ Added {len(batch_records)} student_health_fitness_goals records")
        except Exception as e:
            print(f"  ❌ Error adding student_health_fitness_goals: {e}")
            session.rollback()
    else:
        print(f"  ✅ student_health_fitness_goals already has {current_count} records")

def fix_health_alerts(session: Session, student_health_ids: list, student_count: int):
    """Fix health_alerts - 1 per 10 students (realistic for alerts) using only students with health records"""
    print("🔧 FIXING health_alerts...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_alerts")).scalar()
    target_count = student_count // 10  # 1 alert per 10 students
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} health_alerts records...")
        
        # Use only students that have health records
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping health_alerts")
            return
        
        # Create alerts using actual student_health IDs
        batch_records = []
        for i in range(needed):
            student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
            health_alert = {
                'student_id': student_id,  # Use actual student_health IDs
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
            print(f"  ✅ Added {len(batch_records)} health_alerts records")
        except Exception as e:
            print(f"  ❌ Error adding health_alerts: {e}")
            session.rollback()
    else:
        print(f"  ✅ health_alerts already has {current_count} records")

def main():
    """Main function to fix the final 3 tables"""
    print("="*70)
    print("🔧 FIXING FINAL 3 TABLES - FOREIGN KEY CONSTRAINT RESOLUTION")
    print("="*70)
    print("📊 Fixing fitness_assessments, student_health_fitness_goals, health_alerts")
    print("🎯 Using only student IDs that exist in student_health table")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_health_ids = get_student_health_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Students with health records: {len(student_health_ids):,}")
        
        if not student_health_ids:
            print("❌ No students with health records found, cannot proceed with scaling")
            return
        
        # Fix each table individually
        fix_fitness_assessments(session, student_health_ids, student_count)
        fix_student_health_fitness_goals(session, student_health_ids, student_count)
        fix_health_alerts(session, student_health_ids, student_count)
        
        print("\n🎉 All final 3 table fixes completed!")
        
    except Exception as e:
        print(f"❌ Error during fixing: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
