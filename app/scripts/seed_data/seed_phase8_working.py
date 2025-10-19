#!/usr/bin/env python
"""
Phase 8: Advanced Physical Education & Adaptations - Working Implementation
Seeds working tables only, skips problematic foreign key dependencies
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
        result = session.execute(text('SELECT id FROM users LIMIT 50'))
        ids['user_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM students '))
        ids['student_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM activities '))
        ids['activity_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM educational_classes '))
        ids['class_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM exercises '))
        ids['exercise_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM workouts '))
        ids['workout_ids'] = [row[0] for row in result.fetchall()]
        
        print(f"✅ Retrieved dependency IDs: {len(ids['user_ids'])} users, {len(ids['student_ids'])} students, {len(ids['class_ids'])} classes")
        
    except Exception as e:
        print(f"⚠️ Error getting dependency IDs: {e}")
        ids = {
            'user_ids': list(range(1, 51)),
            'student_ids': list(range(1, 1001)),
            'activity_ids': list(range(1, 101)),
            'class_ids': list(range(1, 101)),
            'exercise_ids': list(range(1, 101)),
            'workout_ids': list(range(1, 101))
        }
    
    return ids

def seed_phase8_working(session: Session) -> Dict[str, int]:
    """Seed Phase 8: Advanced Physical Education & Adaptations - Working tables only"""
    print("🚀 PHASE 8: ADVANCED PHYSICAL EDUCATION & ADAPTATIONS - WORKING")
    print("=" * 80)
    print("📊 Seeding working tables only, skipping problematic foreign key dependencies")
    print("🎯 Properly scaled for 4,000+ student district")
    print("🔄 Using comprehensive data migration approach")
    print("=" * 80)
    
    results = {}
    
    # Get dependency IDs
    ids = get_dependency_ids(session)
    
    print()
    print("🏃 WORKING PHYSICAL EDUCATION TABLES (15 tables)")
    print("-" * 70)
    
    # 1. pe_activity_adaptations (migrate from students + activities) - WORKING
    try:
        additional_adaptations = []
        for student_id in ids['student_ids'][:200]:  # 200 adaptations
            activity_id = random.choice(ids['activity_ids'])
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_adaptations.append({
                'activity_id': activity_id,
                'student_id': student_id,
                'adaptation_type': random.choice(['DIFFICULTY', 'EQUIPMENT', 'DURATION', 'INTENSITY', 'GROUP_SIZE', 'ENVIRONMENT', 'INSTRUCTION', 'ASSISTANCE', 'MODIFICATION', 'ALTERNATIVE', 'COMPLEXITY', 'SUPPORT']),
                'adaptation_level': random.choice(['MINOR', 'MODERATE', 'MAJOR', 'EXTENSIVE', 'CUSTOM', 'NONE', 'MINIMAL', 'SIGNIFICANT', 'EXTREME']),
                'status': random.choice(['PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'EXPIRED', 'ARCHIVED', 'REVIEW', 'APPROVED', 'REJECTED', 'IN_PROGRESS', 'FAILED', 'REVERTED']),
                'trigger': random.choice(['AUTOMATIC', 'ENVIRONMENTAL', 'EQUIPMENT_LIMITATION', 'EVENT', 'MANUAL', 'MEDICAL', 'PERFORMANCE_BASED', 'SAFETY_CONCERN', 'SCHEDULED', 'STUDENT_REQUEST', 'TEACHER_INITIATED']),
                'description': f'PE adaptation for student {student_id} in activity {activity_id}',
                'modifications': json.dumps({
                    'equipment_changes': ['Modified equipment', 'Additional support'],
                    'instruction_changes': ['Simplified instructions', 'Visual aids'],
                    'environment_changes': ['Quieter space', 'Smaller group']
                }),
                'created_at': start_date,
                'updated_at': start_date + timedelta(days=random.randint(1, 30))
            })
        
        columns = list(additional_adaptations[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO pe_activity_adaptations ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_adaptations)
        session.commit()
        results['pe_activity_adaptations'] = len(additional_adaptations)
        print(f"  ✅ pe_activity_adaptations: +{len(additional_adaptations)} records (migrated from students + activities)")
    except Exception as e:
        print(f"  ❌ pe_activity_adaptations: {e}")
        session.rollback()
        results['pe_activity_adaptations'] = 0

    # 2. pe_adaptation_history (migrate from pe_activity_adaptations) - WORKING
    try:
        # First get existing adaptations
        existing_adaptations = session.execute(text('SELECT id FROM pe_activity_adaptations')).fetchall()
        
        additional_history = []
        for i, (adaptation_id,) in enumerate(existing_adaptations[:300]):
            history_date = datetime.now() - timedelta(days=random.randint(1, 60))
            additional_history.append({
                'adaptation_id': adaptation_id,
                'previous_type': random.choice(['DIFFICULTY', 'EQUIPMENT', 'DURATION', 'INTENSITY', 'GROUP_SIZE', 'ENVIRONMENT', 'INSTRUCTION', 'ASSISTANCE', 'MODIFICATION', 'ALTERNATIVE', 'COMPLEXITY', 'SUPPORT']),
                'previous_level': random.choice(['MINOR', 'MODERATE', 'MAJOR', 'EXTENSIVE', 'CUSTOM', 'NONE', 'MINIMAL', 'SIGNIFICANT', 'EXTREME']),
                'previous_status': random.choice(['PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'EXPIRED', 'ARCHIVED', 'REVIEW', 'APPROVED', 'REJECTED', 'IN_PROGRESS', 'FAILED', 'REVERTED']),
                'previous_modifications': json.dumps(['Previous mod 1', 'Previous mod 2']),
                'reason': f'Reason for change {i+1}',
                'created_at': history_date
            })
        
        if additional_history:
            columns = list(additional_history[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            query = f"INSERT INTO pe_adaptation_history ({', '.join(columns)}) VALUES ({placeholders})"
            
            session.execute(text(query), additional_history)
            session.commit()
            results['pe_adaptation_history'] = len(additional_history)
            print(f"  ✅ pe_adaptation_history: +{len(additional_history)} records (migrated from pe_activity_adaptations)")
        else:
            results['pe_adaptation_history'] = 0
            print(f"  ⚠️ pe_adaptation_history: no existing adaptations to create history from")
    except Exception as e:
        print(f"  ❌ pe_adaptation_history: {e}")
        session.rollback()
        results['pe_adaptation_history'] = 0

    # 3. physical_education_activity_adaptations (migrate from students + activities) - WORKING
    try:
        additional_pe_adaptations = []
        for i in range(150):  # 150 PE adaptations
            student_id = random.choice(ids['student_ids'])
            activity_id = random.choice(ids['activity_ids'])
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_pe_adaptations.append({
                'activity_id': activity_id,
                'student_id': student_id,
                'adaptation_type': random.choice(['DIFFICULTY', 'EQUIPMENT', 'DURATION', 'INTENSITY', 'GROUP_SIZE', 'ENVIRONMENT', 'INSTRUCTION', 'ASSISTANCE', 'MODIFICATION', 'ALTERNATIVE', 'COMPLEXITY', 'SUPPORT']),
                'description': f'PE activity adaptation {i+1} for student {student_id}',
                'reason': f'Reason for adaptation {i+1}',
                'equipment_needed': json.dumps(['Mats', 'Weights', 'Balls']),
                'instructions': f'Instructions for adaptation {i+1}',
                'safety_considerations': f'Safety notes for adaptation {i+1}',
                'created_by': random.choice(ids['user_ids']) if ids['user_ids'] else random.randint(1, 10),
                'active': True,
                'created_at': start_date,
                'updated_at': start_date + timedelta(days=random.randint(1, 30))
            })
        
        columns = list(additional_pe_adaptations[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO physical_education_activity_adaptations ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_pe_adaptations)
        session.commit()
        results['physical_education_activity_adaptations'] = len(additional_pe_adaptations)
        print(f"  ✅ physical_education_activity_adaptations: +{len(additional_pe_adaptations)} records (migrated from students + activities)")
    except Exception as e:
        print(f"  ❌ physical_education_activity_adaptations: {e}")
        session.rollback()
        results['physical_education_activity_adaptations'] = 0

    # 4. physical_education_attendance (migrate from students) - WORKING
    try:
        additional_attendance = []
        for student_id in ids['student_ids'][:1000]:  # 1000 attendance records
            for day in range(3):  # 3 days of attendance per student
                attendance_date = datetime.now() - timedelta(days=day)
                additional_attendance.append({
                    'student_id': student_id,
                    'date': attendance_date.date(),  # Use date() for date column
                    'status': random.choice(['PRESENT', 'ABSENT', 'LATE', 'EXCUSED', 'TARDY']),
                    'notes': f'Attendance notes for student {student_id} on {attendance_date.strftime("%Y-%m-%d")}',
                    'created_at': attendance_date,
                    'updated_at': attendance_date
                })
        
        columns = list(additional_attendance[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO physical_education_attendance ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_attendance)
        session.commit()
        results['physical_education_attendance'] = len(additional_attendance)
        print(f"  ✅ physical_education_attendance: +{len(additional_attendance)} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ physical_education_attendance: {e}")
        session.rollback()
        results['physical_education_attendance'] = 0

    # 5. physical_education_safety_alerts (migrate from activities + users) - WORKING
    try:
        additional_alerts = []
        for i in range(100):  # 100 safety alerts
            activity_id = random.choice(ids['activity_ids']) if ids['activity_ids'] else random.randint(1, 50)
            created_by = random.choice(ids['user_ids']) if ids['user_ids'] else random.randint(1, 10)
            additional_alerts.append({
                'alert_type': random.choice(['SAFETY', 'MAINTENANCE', 'INJURY', 'EQUIPMENT', 'ENVIRONMENT']),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'message': f'Safety alert {i+1} for activity {activity_id}',
                'recipients': json.dumps(['teachers', 'students', 'administrators']),
                'created_by': created_by,
                'resolved_at': datetime.now() - timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                'resolution_notes': f'Resolution notes for alert {i+1}' if random.choice([True, False]) else None
            })
        
        columns = list(additional_alerts[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO physical_education_safety_alerts ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_alerts)
        session.commit()
        results['physical_education_safety_alerts'] = len(additional_alerts)
        print(f"  ✅ physical_education_safety_alerts: +{len(additional_alerts)} records (migrated from activities + users)")
    except Exception as e:
        print(f"  ❌ physical_education_safety_alerts: {e}")
        session.rollback()
        results['physical_education_safety_alerts'] = 0

    # 6. adapted_activity_categories (simple table) - WORKING
    try:
        additional_categories = []
        for i in range(50):  # 50 categories
            additional_categories.append({
                'category_type': random.choice(['COMPETITIVE', 'GROUP', 'INDIVIDUAL', 'NON_COMPETITIVE', 'PAIR', 'TEAM']),
                'name': f'Adapted Category {i+1}',
                'description': f'Category for adapted activities {i+1}',
                'metadata': json.dumps({'source': 'phase8_working'})
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

    # 7. adapted_exercises (simple table) - WORKING
    try:
        additional_exercises = []
        for i in range(100):  # 100 exercises
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

    # 8. adapted_workouts (migrate from students) - WORKING
    try:
        additional_workouts = []
        for i in range(200):  # 200 adapted workouts
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
        print(f"  ✅ adapted_workouts: +{len(additional_workouts)} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ adapted_workouts: {e}")
        session.rollback()
        results['adapted_workouts'] = 0

    # 9. student_health_skill_assessments (migrate from students) - WORKING
    try:
        additional_assessments = []
        for i in range(500):  # 500 assessments
            student_id = random.choice(ids['student_ids'])
            assessment_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_assessments.append({
                'student_id': student_id,
                'assessment_date': assessment_date,
                'skill_type': random.choice(['COORDINATION', 'BALANCE', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE']),
                'skill_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
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
        print(f"  ✅ student_health_skill_assessments: +{len(additional_assessments)} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ student_health_skill_assessments: {e}")
        session.rollback()
        results['student_health_skill_assessments'] = 0

    # 10. workout_sessions (migrate from students + workouts) - WORKING
    try:
        additional_sessions = []
        for i in range(300):  # 300 workout sessions
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
        print(f"  ✅ workout_sessions: +{len(additional_sessions)} records (migrated from students + workouts)")
    except Exception as e:
        print(f"  ❌ workout_sessions: {e}")
        session.rollback()
        results['workout_sessions'] = 0

    # 11. physical_education_workouts (simple table) - WORKING
    try:
        additional_pe_workouts = []
        for i in range(100):  # 100 PE workouts
            additional_pe_workouts.append({
                'workout_name': f'PE Workout {i+1}',
                'workout_type': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'BALANCE', 'COORDINATION']),
                'description': f'Physical education workout {i+1}',
                'duration': random.randint(15, 60),
                'difficulty_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'workout_metadata': json.dumps({'intensity': 'moderate', 'focus': 'general fitness'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(additional_pe_workouts[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO physical_education_workouts ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_pe_workouts)
        session.commit()
        results['physical_education_workouts'] = len(additional_pe_workouts)
        print(f"  ✅ physical_education_workouts: +{len(additional_pe_workouts)} records")
    except Exception as e:
        print(f"  ❌ physical_education_workouts: {e}")
        session.rollback()
        results['physical_education_workouts'] = 0

    # 12. physical_education_workout_exercises (migrate from workouts + exercises) - WORKING
    try:
        additional_pe_workout_exercises = []
        for i in range(400):  # 400 PE workout exercises
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 50)
            additional_pe_workout_exercises.append({
                'workout_id': workout_id,
                'exercise_id': exercise_id,
                'sets': random.randint(1, 5),
                'reps': random.randint(5, 20),
                'weight': random.uniform(5.0, 50.0),
                'duration_seconds': random.randint(30, 300),
                'rest_seconds': random.randint(30, 120),
                'notes': f'Exercise notes {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(additional_pe_workout_exercises[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO physical_education_workout_exercises ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_pe_workout_exercises)
        session.commit()
        results['physical_education_workout_exercises'] = len(additional_pe_workout_exercises)
        print(f"  ✅ physical_education_workout_exercises: +{len(additional_pe_workout_exercises)} records (migrated from workouts + exercises)")
    except Exception as e:
        print(f"  ❌ physical_education_workout_exercises: {e}")
        session.rollback()
        results['physical_education_workout_exercises'] = 0

    # 13. adapted_activity_plans (migrate from students) - WORKING
    try:
        additional_plans = []
        for i in range(100):  # 100 plans
            student_id = random.choice(ids['student_ids'])
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_plans.append({
                'start_date': start_date,
                'end_date': start_date + timedelta(days=random.randint(30, 90)),
                'goals': json.dumps(['Improve coordination', 'Build strength', 'Enhance balance']),
                'progress_metrics': json.dumps({'completion_rate': random.randint(60, 100)}),
                'notes': f'Plan notes {i+1}',
                'created_at': start_date,
                'updated_at': start_date
            })
        
        columns = list(additional_plans[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO adapted_activity_plans ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_plans)
        session.commit()
        results['adapted_activity_plans'] = len(additional_plans)
        print(f"  ✅ adapted_activity_plans: +{len(additional_plans)} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ adapted_activity_plans: {e}")
        session.rollback()
        results['adapted_activity_plans'] = 0

    # 14. adapted_activity_plan_activities (migrate from activities) - WORKING
    try:
        additional_plan_activities = []
        for i in range(200):  # 200 plan activities
            plan_id = random.randint(1, 100)  # Assume plans exist
            activity_id = random.choice(ids['activity_ids'])
            additional_plan_activities.append({
                'plan_id': plan_id,
                'activity_id': activity_id,
                'order': i + 1,
                'duration_minutes': random.randint(10, 60),
                'intensity': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'notes': f'Plan activity notes {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(additional_plan_activities[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO adapted_activity_plan_activities ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_plan_activities)
        session.commit()
        results['adapted_activity_plan_activities'] = len(additional_plan_activities)
        print(f"  ✅ adapted_activity_plan_activities: +{len(additional_plan_activities)} records (migrated from activities)")
    except Exception as e:
        print(f"  ❌ adapted_activity_plan_activities: {e}")
        session.rollback()
        results['adapted_activity_plan_activities'] = 0

    # 15. adapted_routines (migrate from students) - WORKING
    try:
        additional_routines = []
        for i in range(150):  # 150 adapted routines
            student_id = random.choice(ids['student_ids'])
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_routines.append({
                'student_id': student_id,
                'name': f'Adapted Routine {i+1}',
                'description': f'Adapted routine for student {student_id}',
                'routine_type': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'CUSTOM']),
                'duration_minutes': random.randint(20, 60),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'equipment_needed': json.dumps(['Mats', 'Weights', 'Balls']),
                'instructions': f'Instructions for routine {i+1}',
                'created_at': start_date,
                'updated_at': start_date
            })
        
        columns = list(additional_routines[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO adapted_routines ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), additional_routines)
        session.commit()
        results['adapted_routines'] = len(additional_routines)
        print(f"  ✅ adapted_routines: +{len(additional_routines)} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ adapted_routines: {e}")
        session.rollback()
        results['adapted_routines'] = 0

    print()
    print("🎉 Phase 8 Working: {} records created".format(sum(results.values())))
    print("📊 Total tables processed: {}".format(len([k for k, v in results.items() if v > 0])))
    print("✅ Successfully populated {} working tables".format(len([k for k, v in results.items() if v > 0])))
    
    return results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    print('🚀 TESTING PHASE 8 - WORKING IMPLEMENTATION')
    print('=' * 60)
    
    session = SessionLocal()
    try:
        results = seed_phase8_working(session)
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
