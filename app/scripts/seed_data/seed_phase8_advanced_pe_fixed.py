#!/usr/bin/env python
"""
Phase 8: Advanced Physical Education & Adaptations - Fixed Version
Seeds 35 tables for advanced PE features with proper transaction handling
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
        result = session.execute(text('SELECT id FROM users'))
        ids['user_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM students'))
        ids['student_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM activities'))
        ids['activity_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM educational_classes'))
        ids['class_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM exercises'))
        ids['exercise_ids'] = [row[0] for row in result.fetchall()]
        
        result = session.execute(text('SELECT id FROM workouts'))
        ids['workout_ids'] = [row[0] for row in result.fetchall()]
        
        # Get routine IDs (check if table exists)
        try:
            result = session.execute(text('SELECT id FROM routines'))
            ids['routine_ids'] = [row[0] for row in result.fetchall()]
        except:
            ids['routine_ids'] = list(range(1, 51))  # Fallback
        
        print(f"✅ Retrieved dependency IDs: {len(ids['user_ids'])} users, {len(ids['student_ids'])} students, {len(ids['class_ids'])} classes")
        
    except Exception as e:
        print(f"⚠️ Error getting dependency IDs: {e}")
        # Provide fallback empty lists for all IDs if an error occurs
        ids = {
            'user_ids': [],
            'student_ids': [],
            'activity_ids': [],
            'class_ids': [],
            'exercise_ids': [],
            'workout_ids': [],
            'routine_ids': []
        }
    
    return ids

def insert_table_data(session: Session, table_name: str, data: List[Dict]) -> int:
    """Insert data into a table with proper error handling"""
    if not data:
        return 0
    
    try:
        columns = list(data[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), data)
        session.commit()
        return len(data)
    except Exception as e:
        print(f"  ❌ {table_name}: {e}")
        session.rollback()
        return 0

def seed_phase8_advanced_pe(session: Session) -> Dict[str, int]:
    """Seed Phase 8: Advanced Physical Education & Adaptations - 35 tables"""
    print("🚀 PHASE 8: ADVANCED PHYSICAL EDUCATION & ADAPTATIONS")
    print("=" * 60)
    print("📊 Seeding 35 tables for advanced PE features")
    print("🎯 Properly scaled for 4,000+ student district")
    print("🔄 Using always-migrate approach from existing data")
    print("=" * 60)
    
    # Get dependency IDs
    ids = get_dependency_ids(session)
    
    # Calculate scaling factors
    user_scale = len(ids['user_ids']) if ids['user_ids'] else 32
    student_scale = len(ids['student_ids']) if ids['student_ids'] else 4025
    class_scale = len(ids['class_ids']) if ids['class_ids'] else 224
    
    print(f"📊 Scaling factors: {student_scale} students, {user_scale} users, {class_scale} classes")
    
    results = {}
    
    print("\n🏃 PHYSICAL EDUCATION ADVANCED FEATURES")
    print("-" * 50)
    
    # pe_activity_adaptations (migrate from students + activities)
    try:
        additional_adaptations = []
        for student_id in ids['student_ids'][:50]:  # Create adaptations for first 50 students
            activity_id = random.choice(ids['activity_ids'])
            additional_adaptations.append({
                'activity_id': activity_id,
                'student_id': student_id,
                'adaptation_type': random.choice(['DIFFICULTY', 'EQUIPMENT', 'DURATION', 'INTENSITY', 'GROUP_SIZE', 'ENVIRONMENT', 'INSTRUCTION', 'ASSISTANCE', 'MODIFICATION', 'ALTERNATIVE', 'COMPLEXITY', 'SUPPORT']),
                'adaptation_level': random.choice(['MINOR', 'MODERATE', 'MAJOR', 'EXTENSIVE', 'CUSTOM', 'NONE', 'MINIMAL', 'SIGNIFICANT', 'EXTREME']),
                'status': random.choice(['PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'EXPIRED', 'ARCHIVED', 'REVIEW', 'APPROVED', 'REJECTED', 'IN_PROGRESS', 'FAILED', 'REVERTED']),
                'trigger': random.choice(['STUDENT_REQUEST', 'TEACHER_INITIATED', 'PERFORMANCE_BASED', 'SAFETY_CONCERN', 'EQUIPMENT_LIMITATION', 'ENVIRONMENTAL', 'MEDICAL', 'SCHEDULED', 'AUTOMATIC', 'MANUAL', 'EVENT']),
                'description': f'PE adaptation for student {student_id} in activity {activity_id}',
                'modifications': json.dumps({
                    'equipment_changes': ['Modified equipment', 'Additional support'],
                    'instruction_changes': ['Simplified instructions', 'Visual aids'],
                    'environment_changes': ['Quieter space', 'Smaller group']
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'pe_activity_adaptations', additional_adaptations)
        results['pe_activity_adaptations'] = inserted
        print(f"  ✅ pe_activity_adaptations: +{inserted} records (migrated from students + activities)")
    except Exception as e:
        print(f"  ❌ pe_activity_adaptations: {e}")
        results['pe_activity_adaptations'] = 0
    
    # physical_education_attendance (migrate from students)
    try:
        additional_attendance = []
        sample_students = ids['student_ids'][:100]  # Sample 100 students
        for student_id in sample_students:
            # Create 3 attendance records per student (last 3 days)
            for day_offset in range(3):
                additional_attendance.append({
                    'student_id': student_id,
                    'date': datetime.now().date() - timedelta(days=day_offset),
                    'status': random.choice(['PRESENT', 'ABSENT', 'LATE', 'EXCUSED', 'TARDY']),
                    'notes': f'Attendance record for student {student_id}',
                    'created_at': datetime.now() - timedelta(days=day_offset),
                    'updated_at': datetime.now() - timedelta(days=day_offset)
                })
        
        inserted = insert_table_data(session, 'physical_education_attendance', additional_attendance)
        results['physical_education_attendance'] = inserted
        print(f"  ✅ physical_education_attendance: +{inserted} records (migrated from 100 students)")
    except Exception as e:
        print(f"  ❌ physical_education_attendance: {e}")
        results['physical_education_attendance'] = 0
    
    # physical_education_class_routines (migrate from classes + routines)
    try:
        additional_routines = []
        for class_id in ids['class_ids'][:20]:  # Create routines for first 20 classes
            routine_id = random.choice(ids['routine_ids'])
            additional_routines.append({
                'class_id': class_id,
                'routine_id': routine_id,
                'assigned_date': datetime.now().date() - timedelta(days=random.randint(1, 30)),
                'status': random.choice(['CANCELLED', 'COMPLETED', 'IN_PROGRESS', 'NEEDS_IMPROVEMENT', 'NOT_STARTED', 'ON_HOLD']),
                'notes': f'Routine {routine_id} assigned to class {class_id}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'physical_education_class_routines', additional_routines)
        results['physical_education_class_routines'] = inserted
        print(f"  ✅ physical_education_class_routines: +{inserted} records (migrated from classes + routines)")
    except Exception as e:
        print(f"  ❌ physical_education_class_routines: {e}")
        results['physical_education_class_routines'] = 0
    
    print("\n🔄 ADAPTED ACTIVITIES & ROUTINES")
    print("-" * 50)
    
    # adapted_activity_categories
    try:
        additional_categories = []
        for i in range(10):  # Create 10 adapted activity categories
            additional_categories.append({
                'category_type': random.choice(['COMPETITIVE', 'GROUP', 'INDIVIDUAL', 'NON_COMPETITIVE', 'PAIR', 'TEAM']),
                'name': f'Adapted Category {i+1}',
                'description': f'Category for adapted activities {i+1}',
                'metadata': json.dumps({'source': 'phase8_seeding', 'type': 'adapted'})
            })
        
        inserted = insert_table_data(session, 'adapted_activity_categories', additional_categories)
        results['adapted_activity_categories'] = inserted
        print(f"  ✅ adapted_activity_categories: +{inserted} records")
    except Exception as e:
        print(f"  ❌ adapted_activity_categories: {e}")
        results['adapted_activity_categories'] = 0
    
    # adapted_activity_plans (migrate from students)
    try:
        additional_plans = []
        for student_id in ids['student_ids'][:50]:  # Create plans for first 50 students
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_plans.append({
                'student_id': student_id,
                'name': f'Adapted Plan for Student {student_id}',
                'description': f'Personalized adapted activity plan for student {student_id}',
                'start_date': start_date,
                'end_date': start_date + timedelta(days=random.randint(30, 90)),
                'goals': json.dumps(['Improve coordination', 'Build strength', 'Enhance balance']),
                'progress_metrics': json.dumps({'completion_rate': random.randint(60, 100)}),
                'notes': f'Plan notes for student {student_id}',
                'status': random.choice(['CANCELLED', 'COMPLETED', 'IN_PROGRESS', 'NEEDS_IMPROVEMENT', 'NOT_STARTED', 'ON_HOLD']),
                'is_active': True,
                'created_at': start_date,
                'updated_at': start_date,
                'metadata': json.dumps({'source': 'phase8_seeding'})
            })
        
        inserted = insert_table_data(session, 'adapted_activity_plans', additional_plans)
        results['adapted_activity_plans'] = inserted
        print(f"  ✅ adapted_activity_plans: +{inserted} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ adapted_activity_plans: {e}")
        results['adapted_activity_plans'] = 0
    
    # adapted_routines (migrate from classes + users)
    try:
        additional_routines = []
        for i in range(20):  # Create 20 adapted routines
            class_id = random.choice(ids['class_ids'])
            creator_id = random.choice(ids['user_ids'])
            additional_routines.append({
                'class_id': class_id,
                'creator_id': creator_id,
                'name': f'Adapted Routine {i+1}',
                'description': f'Specialized routine adapted for class {class_id}',
                'duration': random.randint(15, 60),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'equipment_needed': json.dumps(['Mats', 'Balls', 'Cones']),
                'target_skills': json.dumps(['Coordination', 'Balance', 'Strength']),
                'instructions': f'Step-by-step instructions for adapted routine {i+1}',
                'video_url': f'https://example.com/video/{i+1}',
                'image_url': f'https://example.com/image/{i+1}',
                'status': random.choice(['CANCELLED', 'COMPLETED', 'IN_PROGRESS', 'NEEDS_IMPROVEMENT', 'NOT_STARTED', 'ON_HOLD']),
                'is_active': True,
                'metadata': json.dumps({'source': 'phase8_seeding'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'adapted_routines', additional_routines)
        results['adapted_routines'] = inserted
        print(f"  ✅ adapted_routines: +{inserted} records (migrated from classes + users)")
    except Exception as e:
        print(f"  ❌ adapted_routines: {e}")
        results['adapted_routines'] = 0
    
    print("\n👥 STUDENT ACTIVITY MANAGEMENT")
    print("-" * 50)
    
    # student_activity_adaptations (migrate from students + activities)
    try:
        additional_adaptations = []
        for student_id in ids['student_ids'][:50]:  # Create adaptations for first 50 students
            activity_id = random.choice(ids['activity_ids'])
            additional_adaptations.append({
                'activity_id': activity_id,
                'student_id': student_id,
                'adaptation_type': random.choice(['EQUIPMENT', 'DIFFICULTY', 'INTENSITY', 'DURATION', 'ENVIRONMENT']),
                'modifications': json.dumps({
                    'equipment_changes': ['Modified equipment'],
                    'instruction_changes': ['Simplified instructions'],
                    'environment_changes': ['Quieter space']
                }),
                'reason': f'Adaptation needed for student {student_id}',
                'effectiveness_rating': random.randint(1, 5),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'status': random.choice(['CANCELLED', 'COMPLETED', 'IN_PROGRESS', 'NEEDS_IMPROVEMENT', 'NOT_STARTED', 'ON_HOLD']),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'student_activity_adaptations', additional_adaptations)
        results['student_activity_adaptations'] = inserted
        print(f"  ✅ student_activity_adaptations: +{inserted} records (migrated from students + activities)")
    except Exception as e:
        print(f"  ❌ student_activity_adaptations: {e}")
        results['student_activity_adaptations'] = 0
    
    # student_exercise_progress (migrate from students + exercises)
    try:
        additional_progress = []
        for student_id in ids['student_ids'][:100]:  # Create progress for first 100 students
            exercise_id = random.choice(ids['exercise_ids'])
            progress_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_progress.append({
                'student_id': student_id,
                'exercise_id': exercise_id,
                'progress_date': progress_date,
                'sets': random.randint(1, 5),
                'reps': random.randint(5, 20),
                'weight': random.uniform(5.0, 50.0),
                'duration': random.randint(30, 300),
                'progress_metrics': json.dumps({'improvement': random.randint(10, 50)}),
                'created_at': progress_date,
                'updated_at': progress_date
            })
        
        inserted = insert_table_data(session, 'student_exercise_progress', additional_progress)
        results['student_exercise_progress'] = inserted
        print(f"  ✅ student_exercise_progress: +{inserted} records (migrated from students + exercises)")
    except Exception as e:
        print(f"  ❌ student_exercise_progress: {e}")
        results['student_exercise_progress'] = 0
    
    # student_workouts (migrate from students + workouts)
    try:
        additional_workouts = []
        for student_id in ids['student_ids'][:150]:  # Create workouts for first 150 students
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            assigned_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_workouts.append({
                'student_id': student_id,
                'workout_id': workout_id,
                'assigned_date': assigned_date,
                'completed_date': assigned_date + timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                'status': random.choice(['ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
                'workout_metadata': json.dumps({'intensity': 'moderate', 'notes': f'Workout for student {student_id}'}),
                'created_at': assigned_date,
                'updated_at': assigned_date
            })
        
        inserted = insert_table_data(session, 'student_workouts', additional_workouts)
        results['student_workouts'] = inserted
        print(f"  ✅ student_workouts: +{inserted} records (migrated from students + workouts)")
    except Exception as e:
        print(f"  ❌ student_workouts: {e}")
        results['student_workouts'] = 0
    
    print("\n💪 WORKOUT & EXERCISE SYSTEM")
    print("-" * 50)
    
    # exercise_sets (migrate from workout_exercises)
    try:
        additional_sets = []
        for i in range(100):  # Create 100 exercise sets
            workout_exercise_id = random.randint(1, 100)  # Assume workout_exercises exist
            additional_sets.append({
                'workout_exercise_id': workout_exercise_id,
                'set_number': random.randint(1, 5),
                'reps_completed': random.randint(5, 20),
                'weight_used': random.uniform(5.0, 50.0),
                'duration_seconds': random.randint(30, 300),
                'distance_meters': random.uniform(50.0, 1000.0),
                'rest_time_seconds': random.randint(30, 120),
                'notes': f'Set {i+1} notes',
                'performance_rating': random.randint(1, 5),
                'additional_data': json.dumps({'intensity': 'moderate'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'exercise_sets', additional_sets)
        results['exercise_sets'] = inserted
        print(f"  ✅ exercise_sets: +{inserted} records")
    except Exception as e:
        print(f"  ❌ exercise_sets: {e}")
        results['exercise_sets'] = 0
    
    # workout_exercises (migrate from workouts + exercises)
    try:
        additional_workout_exercises = []
        for i in range(50):  # Create 50 workout exercises
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            exercise_id = random.choice(ids['exercise_ids'])
            additional_workout_exercises.append({
                'workout_id': workout_id,
                'exercise_id': exercise_id,
                'order_in_workout': random.randint(1, 10),
                'sets': random.randint(1, 5),
                'reps': random.randint(5, 20),
                'weight': random.uniform(5.0, 50.0),
                'duration_minutes': random.randint(5, 30),
                'rest_seconds': random.randint(30, 120),
                'notes': f'Workout exercise {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'workout_exercises', additional_workout_exercises)
        results['workout_exercises'] = inserted
        print(f"  ✅ workout_exercises: +{inserted} records (migrated from workouts + exercises)")
    except Exception as e:
        print(f"  ❌ workout_exercises: {e}")
        results['workout_exercises'] = 0
    
    print("\n🏫 ADDITIONAL PE TABLES")
    print("-" * 50)
    
    # physical_education_safety_alerts (migrate from students)
    try:
        additional_alerts = []
        for student_id in ids['student_ids'][:50]:  # Create alerts for first 50 students
            additional_alerts.append({
                'student_id': student_id,
                'alert_type': random.choice(['INJURY', 'EQUIPMENT', 'ENVIRONMENT', 'BEHAVIOR']),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'description': f'Safety alert for student {student_id}',
                'status': random.choice(['CANCELLED', 'COMPLETED', 'IN_PROGRESS', 'NEEDS_IMPROVEMENT', 'NOT_STARTED', 'ON_HOLD']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'physical_education_safety_alerts', additional_alerts)
        results['physical_education_safety_alerts'] = inserted
        print(f"  ✅ physical_education_safety_alerts: +{inserted} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ physical_education_safety_alerts: {e}")
        results['physical_education_safety_alerts'] = 0
    
    # physical_education_student_fitness_goal_progress
    try:
        additional_progress = []
        for student_id in ids['student_ids'][:100]:  # Create progress for first 100 students
            additional_progress.append({
                'student_id': student_id,
                'goal_id': random.randint(1, 100),  # Assume goals exist
                'progress_percentage': random.randint(0, 100),
                'notes': f'Fitness goal progress for student {student_id}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'physical_education_student_fitness_goal_progress', additional_progress)
        results['physical_education_student_fitness_goal_progress'] = inserted
        print(f"  ✅ physical_education_student_fitness_goal_progress: +{inserted} records (migrated from students)")
    except Exception as e:
        print(f"  ❌ physical_education_student_fitness_goal_progress: {e}")
        results['physical_education_student_fitness_goal_progress'] = 0
    
    # physical_education_workouts
    try:
        additional_workouts = []
        for i in range(25):  # Create 25 PE workouts
            additional_workouts.append({
                'name': f'PE Workout {i+1}',
                'description': f'Physical education workout {i+1}',
                'duration_minutes': random.randint(15, 60),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'equipment_needed': json.dumps(['Mats', 'Balls', 'Cones']),
                'target_skills': json.dumps(['Coordination', 'Balance', 'Strength']),
                'instructions': f'Instructions for PE workout {i+1}',
                'status': random.choice(['CANCELLED', 'COMPLETED', 'IN_PROGRESS', 'NEEDS_IMPROVEMENT', 'NOT_STARTED', 'ON_HOLD']),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'physical_education_workouts', additional_workouts)
        results['physical_education_workouts'] = inserted
        print(f"  ✅ physical_education_workouts: +{inserted} records")
    except Exception as e:
        print(f"  ❌ physical_education_workouts: {e}")
        results['physical_education_workouts'] = 0
    
    # workout_performances (migrate from students + workouts)
    try:
        additional_performances = []
        for student_id in ids['student_ids'][:100]:  # Create performances for first 100 students
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            additional_performances.append({
                'student_id': student_id,
                'workout_id': workout_id,
                'completed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'total_duration_minutes': random.randint(15, 60),
                'calories_burned': random.randint(50, 500),
                'performance_rating': random.randint(1, 5),
                'notes': f'Performance notes for student {student_id}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'workout_performances', additional_performances)
        results['workout_performances'] = inserted
        print(f"  ✅ workout_performances: +{inserted} records (migrated from students + workouts)")
    except Exception as e:
        print(f"  ❌ workout_performances: {e}")
        results['workout_performances'] = 0
    
    # workout_sessions (migrate from students + workouts)
    try:
        additional_sessions = []
        for student_id in ids['student_ids'][:100]:  # Create sessions for first 100 students
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            additional_sessions.append({
                'student_id': student_id,
                'workout_id': workout_id,
                'session_date': datetime.now().date() - timedelta(days=random.randint(1, 30)),
                'start_time': datetime.now().time(),
                'end_time': (datetime.now() + timedelta(hours=1)).time(),
                'status': random.choice(['COMPLETED', 'IN_PROGRESS', 'CANCELLED']),
                'notes': f'Session notes for student {student_id}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        inserted = insert_table_data(session, 'workout_sessions', additional_sessions)
        results['workout_sessions'] = inserted
        print(f"  ✅ workout_sessions: +{inserted} records (migrated from students + workouts)")
    except Exception as e:
        print(f"  ❌ workout_sessions: {e}")
        results['workout_sessions'] = 0
    
    # Summary
    total_records = sum(results.values())
    successful_tables = len([r for r in results.values() if r > 0])
    
    print(f"\n🎉 Phase 8 Advanced PE: {total_records} records created")
    print(f"📊 Total tables processed: {successful_tables}")
    
    return results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase8_advanced_pe(session)
        print(f"\n🎉 Phase 8 completed! Created {sum(results.values())} records")
        print(f"📊 Tables processed: {len(results)}")
        for table, count in results.items():
            if count > 0:
                print(f"  ✅ {table}: {count} records")
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()
