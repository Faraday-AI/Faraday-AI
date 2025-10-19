#!/usr/bin/env python
"""
Phase 8: Advanced Physical Education & Adaptations - Minimal Test
Tests just a few tables to avoid hanging issues
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

def get_dependency_ids(session: Session) -> Dict[str, List[int]]:
    """Get IDs from existing populated tables for foreign key references"""
    ids = {}
    
    try:
        result = session.execute(text('SELECT id FROM users '))
        ids['user_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM students 0'))
        ids['student_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM activities LIMIT 50'))
        ids['activity_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM educational_classes LIMIT 20'))
        ids['class_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM exercises LIMIT 20'))
        ids['exercise_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM workouts LIMIT 20'))
        ids['workout_ids'] = [row[0] for row in result.fetchall()]
        
        print(f"✅ Retrieved dependency IDs: {len(ids['user_ids'])} users, {len(ids['student_ids'])} students, {len(ids['class_ids'])} classes")
        
    except Exception as e:
        print(f"⚠️ Error getting dependency IDs: {e}")
        ids = {
            'user_ids': list(range(1, 11)),
            'student_ids': list(range(1, 101)),
            'activity_ids': list(range(1, 51)),
            'class_ids': list(range(1, 21)),
            'exercise_ids': list(range(1, 21)),
            'workout_ids': list(range(1, 21))
        }
    
    return ids

def seed_phase8_minimal(session: Session) -> Dict[str, int]:
    """Seed Phase 8: Advanced Physical Education & Adaptations - Minimal test"""
    print("🚀 PHASE 8: ADVANCED PHYSICAL EDUCATION & ADAPTATIONS - MINIMAL TEST")
    print("=" * 70)
    print("📊 Testing just a few tables to avoid hanging issues")
    print("🎯 Small scale test")
    print("=" * 70)
    
    results = {}
    
    # Get dependency IDs
    ids = get_dependency_ids(session)
    
    print()
    print("🏃 TESTING CORE TABLES (5 tables)")
    print("-" * 50)
    
    # 1. adapted_activity_categories (simple table)
    try:
        additional_categories = []
        for i in range(10):  # Just 10 categories
            additional_categories.append({
                'category_type': random.choice(['COMPETITIVE', 'GROUP', 'INDIVIDUAL', 'NON_COMPETITIVE', 'PAIR', 'TEAM']),
                'name': f'Adapted Category {i+1}',
                'description': f'Category for adapted activities {i+1}',
                'metadata': json.dumps({'source': 'phase8_minimal_test'})
            })
        
        columns = list(additional_categories[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO adapted_activity_categories ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_categories)
        session.commit()
        results['adapted_activity_categories'] = len(additional_categories)
        print(f"  ✅ adapted_activity_categories: +{len(additional_categories)} records")
    except Exception as e:
        print(f"  ❌ adapted_activity_categories: {e}")
        session.rollback()
        results['adapted_activity_categories'] = 0

    # 2. adapted_exercises (simple table)
    try:
        additional_exercises = []
        for i in range(20):  # Just 20 exercises
            additional_exercises.append({
                'name': f'Adapted Exercise {i+1}',
                'description': f'Description for adapted exercise {i+1}',
                'exercise_type': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'BALANCE', 'COORDINATION']),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'duration_minutes': random.randint(5, 30),
                'equipment_needed': json.dumps(['Mats', 'Weights', 'Balls']),
                'instructions': f'Instructions for adapted exercise {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(additional_exercises[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO adapted_exercises ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_exercises)
        session.commit()
        results['adapted_exercises'] = len(additional_exercises)
        print(f"  ✅ adapted_exercises: +{len(additional_exercises)} records")
    except Exception as e:
        print(f"  ❌ adapted_exercises: {e}")
        session.rollback()
        results['adapted_exercises'] = 0

    # 3. adapted_workouts (simple table)
    try:
        additional_workouts = []
        for i in range(15):  # Just 15 workouts
            student_id = random.choice(ids['student_ids'])
            workout_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_workouts.append({
                'student_id': student_id,
                'date': workout_date,
                'duration_minutes': random.randint(15, 60),
                'intensity': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'notes': f'Workout notes {i+1}',
                'created_at': workout_date,
                'updated_at': workout_date
            })
        
        columns = list(additional_workouts[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO adapted_workouts ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_workouts)
        session.commit()
        results['adapted_workouts'] = len(additional_workouts)
        print(f"  ✅ adapted_workouts: +{len(additional_workouts)} records")
    except Exception as e:
        print(f"  ❌ adapted_workouts: {e}")
        session.rollback()
        results['adapted_workouts'] = 0

    # 4. student_health_skill_assessments (simple table)
    try:
        additional_assessments = []
        for i in range(25):  # Just 25 assessments
            student_id = random.choice(ids['student_ids'])
            assessment_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_assessments.append({
                'student_id': student_id,
                'assessment_date': assessment_date,
                'skill_type': random.choice(['COORDINATION', 'BALANCE', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE']),
                'skill_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'score': random.randint(1, 100),
                'notes': f'Assessment notes {i+1}',
                'created_at': assessment_date,
                'updated_at': assessment_date
            })
        
        columns = list(additional_assessments[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO student_health_skill_assessments ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_assessments)
        session.commit()
        results['student_health_skill_assessments'] = len(additional_assessments)
        print(f"  ✅ student_health_skill_assessments: +{len(additional_assessments)} records")
    except Exception as e:
        print(f"  ❌ student_health_skill_assessments: {e}")
        session.rollback()
        results['student_health_skill_assessments'] = 0

    # 5. workout_sessions (simple table)
    try:
        additional_sessions = []
        for i in range(30):  # Just 30 sessions
            student_id = random.choice(ids['student_ids'])
            teacher_id = random.choice(ids['user_ids'])
            workout_id = random.choice(ids['workout_ids'])
            start_time = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_sessions.append({
                'workout_id': workout_id,
                'student_id': student_id,
                'teacher_id': teacher_id,
                'start_time': start_time,
                'end_time': start_time + timedelta(minutes=random.randint(30, 90)),
                'duration_minutes': random.randint(30, 90),
                'calories_burned': random.randint(100, 500),
                'performance_rating': random.randint(1, 10),
                'notes': f'Session notes {i+1}',
                'created_at': start_time,
                'updated_at': start_time
            })
        
        columns = list(additional_sessions[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO workout_sessions ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_sessions)
        session.commit()
        results['workout_sessions'] = len(additional_sessions)
        print(f"  ✅ workout_sessions: +{len(additional_sessions)} records")
    except Exception as e:
        print(f"  ❌ workout_sessions: {e}")
        session.rollback()
        results['workout_sessions'] = 0

    print()
    print("🎉 Phase 8 Minimal Test: {} records created".format(sum(results.values())))
    print("📊 Total tables processed: {}".format(len([k for k, v in results.items() if v > 0])))
    
    return results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    print('🚀 TESTING PHASE 8 - MINIMAL TEST')
    print('=' * 50)
    
    session = SessionLocal()
    try:
        results = seed_phase8_minimal(session)
        print(f'\n🎉 Phase 8 completed! Created {sum(results.values())} records')
        print(f'📊 Tables processed: {len(results)}')
        for table, count in results.items():
            if count > 0:
                print(f'  ✅ {table}: {count} records')
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()
