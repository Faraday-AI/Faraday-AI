#!/usr/bin/env python3
"""
Fix Missing Dependencies Script
Creates missing tables that other tables depend on
"""

import os
import sys
sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta
import random
import json

def create_missing_dependencies():
    """Create missing dependency tables"""
    session = SessionLocal()
    try:
        print('🔧 FIXING MISSING DEPENDENCIES')
        print('=' * 50)
        
        # 1. Create workout_exercises if missing
        result = session.execute(text('SELECT COUNT(*) FROM workout_exercises'))
        workout_exercises_count = result.scalar()
        print(f'workout_exercises: {workout_exercises_count} records')
        
        if workout_exercises_count == 0:
            print('🔧 Creating workout_exercises...')
            
            # Get workout and exercise IDs
            workout_result = session.execute(text('SELECT id FROM workouts LIMIT 20'))
            workout_ids = [row[0] for row in workout_result.fetchall()]
            
            exercise_result = session.execute(text('SELECT id FROM exercises LIMIT 20'))
            exercise_ids = [row[0] for row in exercise_result.fetchall()]
            
            if workout_ids and exercise_ids:
                workout_exercises = []
                for i in range(100):
                    workout_exercises.append({
                    'workout_id': random.choice(workout_ids),
                    'exercise_id': random.choice(exercise_ids),
                    'sets': random.randint(1, 5),
                    'reps': random.randint(5, 20),
                    'duration_minutes': round(random.uniform(5.0, 60.0), 1),
                    'order': i + 1,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': 365
                })
                
                # Insert workout exercises
                columns = list(workout_exercises[0].keys())
                # Quote column names that are SQL reserved keywords
                quoted_columns = [f'"{col}"' if col in ['order'] else col for col in columns]
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO workout_exercises ({', '.join(quoted_columns)}) VALUES ({placeholders})"
                
                session.execute(text(query), workout_exercises)
                session.commit()
                print(f'  ✅ Created {len(workout_exercises)} workout_exercises records')
            else:
                print('  ⚠️ No workouts or exercises found')
        
        # 2. Create health_fitness_workout_exercises if missing
        result = session.execute(text('SELECT COUNT(*) FROM health_fitness_workout_exercises'))
        health_workout_exercises_count = result.scalar()
        print(f'health_fitness_workout_exercises: {health_workout_exercises_count} records')
        
        if health_workout_exercises_count == 0:
            print('🔧 Creating health_fitness_workout_exercises...')
            
            # Get health fitness workout and exercise IDs
            workout_result = session.execute(text('SELECT id FROM health_fitness_workouts LIMIT 20'))
            workout_ids = [row[0] for row in workout_result.fetchall()]
            
            exercise_result = session.execute(text('SELECT id FROM health_fitness_exercises LIMIT 20'))
            exercise_ids = [row[0] for row in exercise_result.fetchall()]
            
            if workout_ids and exercise_ids:
                health_workout_exercises = []
                for i in range(50):
                    health_workout_exercises.append({
                    'workout_id': random.choice(workout_ids),
                    'exercise_id': random.choice(exercise_ids),
                    'sets': random.randint(1, 5),
                    'reps': random.randint(5, 20),
                    'duration_minutes': round(random.uniform(5.0, 60.0), 1),
                    'order': i + 1,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now()
                })
                
                # Insert health fitness workout exercises
                columns = list(health_workout_exercises[0].keys())
                # Quote column names that are SQL reserved keywords
                quoted_columns = [f'"{col}"' if col in ['order'] else col for col in columns]
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO health_fitness_workout_exercises ({', '.join(quoted_columns)}) VALUES ({placeholders})"
                
                session.execute(text(query), health_workout_exercises)
                session.commit()
                print(f'  ✅ Created {len(health_workout_exercises)} health_fitness_workout_exercises records')
            else:
                print('  ⚠️ No health_fitness_workouts or health_fitness_exercises found')
        
        # 3. Create activity_tracking if missing
        result = session.execute(text('SELECT COUNT(*) FROM activity_tracking'))
        activity_tracking_count = result.scalar()
        print(f'activity_tracking: {activity_tracking_count} records')
        
        if activity_tracking_count == 0:
            print('🔧 Creating activity_tracking...')
            
            # Get student and activity IDs
            student_result = session.execute(text('SELECT id FROM students LIMIT 100'))
            student_ids = [row[0] for row in student_result.fetchall()]
            
            activity_result = session.execute(text('SELECT id FROM activities LIMIT 50'))
            activity_ids = [row[0] for row in activity_result.fetchall()]
            
            if student_ids and activity_ids:
                activity_tracking = []
                for i in range(2000):  # Create 2000 activity tracking records
                    activity_tracking.append({
                        'student_id': random.choice(student_ids),
                        'activity_id': random.choice(activity_ids),
                        'tracking_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                        'duration_minutes': random.randint(15, 120),
                        'intensity_level': random.choice(['LOW', 'MODERATE', 'HIGH']),
                        'notes': f'Activity tracking {i+1}',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                # Insert in batches
                batch_size = 500
                for i in range(0, len(activity_tracking), batch_size):
                    batch = activity_tracking[i:i+batch_size]
                    columns = list(batch[0].keys())
                    placeholders = ', '.join([f':{col}' for col in columns])
                    query = f"INSERT INTO activity_tracking ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    session.execute(text(query), batch)
                    session.commit()
                    print(f'    📊 Created batch {i//batch_size + 1}: {len(batch)} records')
                
                print(f'  ✅ Created {len(activity_tracking)} activity_tracking records')
            else:
                print('  ⚠️ No students or activities found')
        
        print('\\n🎉 Missing dependencies fixed!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_missing_dependencies()
