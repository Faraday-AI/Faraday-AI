#!/usr/bin/env python3
"""
Phase 9: Health & Fitness System
Seeds health and fitness tracking system with 25 tables
Based on REMAINING_PHASES_MAPPING.md
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def get_dependency_ids(session: Session) -> Dict[str, List[int]]:
    """Get dependency IDs for seeding"""
    try:
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id "))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        # Get user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id "))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        # Get exercise IDs
        exercise_result = session.execute(text("SELECT id FROM exercises ORDER BY id LIMIT 500"))
        exercise_ids = [row[0] for row in exercise_result.fetchall()]
        
        # Get workout IDs
        workout_result = session.execute(text("SELECT id FROM workouts ORDER BY id LIMIT 200"))
        workout_ids = [row[0] for row in workout_result.fetchall()]
        
        return {
            'student_ids': student_ids,
            'user_ids': user_ids,
            'exercise_ids': exercise_ids,
            'workout_ids': workout_ids
        }
    except Exception as e:
        print(f"⚠️ Error getting dependency IDs: {e}")
        return {
            'student_ids': list(range(1, 1001)),
            'user_ids': list(range(1, 101)),
            'exercise_ids': list(range(1, 501)),
            'workout_ids': list(range(1, 201))
        }


def seed_phase9_health_fitness(session: Session) -> Dict[str, int]:
    """
    Phase 9: Health & Fitness System
    Seeds health and fitness tracking system with 25 tables
    """
    print("="*80)
    print("🚀 PHASE 9: HEALTH & FITNESS SYSTEM")
    print("="*80)
    print("📊 Seeding health and fitness tracking system")
    print("💪 Exercise tracking, workout management, and health metrics")
    print("🎯 Properly scaled for 3,819+ student district")
    print("="*80)
    
    results = {}
    
    # Get dependency IDs
    ids = get_dependency_ids(session)
    
    print("\n💪 HEALTH & FITNESS CORE")
    print("-" * 70)
    
    # 1. health_fitness_exercises (migrate from exercises)
    try:
        # Get existing exercises to migrate
        existing_exercises = session.execute(text("SELECT id, name, description FROM exercises ")).fetchall()
        
        health_fitness_exercises = []
        for i, (exercise_id, name, description) in enumerate(existing_exercises):
            health_fitness_exercises.append({
                'name': f'Health Fitness {name}',
                'description': f'Health and fitness focused: {description}',
                'category': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'BALANCE', 'ENDURANCE']),
                'difficulty_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'muscle_groups': json.dumps(random.sample(['chest', 'back', 'legs', 'arms', 'core'], random.randint(1, 3))),
                'equipment_needed': json.dumps(random.sample(['dumbbells', 'mat', 'resistance_band', 'kettlebell'], random.randint(0, 3))),
                'instructions': f'Detailed instructions for health fitness exercise {i+1}',
                'safety_notes': f'Safety considerations for exercise {i+1}',
                'modifications': json.dumps({'variations': ['beginner', 'advanced'], 'equipment_alternatives': ['bodyweight']}),
                'video_url': f'https://example.com/videos/exercise_{i+1}.mp4',
                'image_url': f'https://example.com/images/exercise_{i+1}.jpg',
                'additional_data': json.dumps({'calories_burned': random.randint(50, 500), 'duration_minutes': random.randint(10, 60)}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(health_fitness_exercises[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO health_fitness_exercises ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), health_fitness_exercises)
        session.commit()
        results['health_fitness_exercises'] = len(health_fitness_exercises)
        print(f"  ✅ health_fitness_exercises: +{len(health_fitness_exercises)} records")
    except Exception as e:
        print(f"  ❌ health_fitness_exercises: {e}")
        session.rollback()
        results['health_fitness_exercises'] = 0

    # 2. health_fitness_workouts (migrate from workouts)
    try:
        # Get existing workouts to migrate
        existing_workouts = session.execute(text("SELECT id, name, description FROM workouts LIMIT 200")).fetchall()
        
        health_fitness_workouts = []
        for i, (workout_id, name, description) in enumerate(existing_workouts):
            health_fitness_workouts.append({
                'name': f'Health Fitness {name}',
                'description': f'Health and fitness focused: {description}',
                'workout_type': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'HIIT', 'CIRCUIT']),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'duration': random.randint(20, 90),
                'equipment_needed': json.dumps(random.sample(['dumbbells', 'mat', 'resistance_band'], random.randint(0, 2))),
                'target_heart_rate': json.dumps({'min': random.randint(120, 140), 'max': random.randint(160, 180)}),
                'safety_requirements': json.dumps(['warm_up', 'cool_down', 'proper_form']),
                'modifications_available': random.choice([True, False]),
                'indoor_outdoor': random.choice(['INDOOR', 'OUTDOOR', 'BOTH']),
                'space_required': random.choice(['SMALL', 'MEDIUM', 'LARGE']),
                'max_participants': random.randint(1, 20),
                'additional_data': json.dumps({'intensity': 'moderate', 'focus': 'overall_fitness'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(health_fitness_workouts[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO health_fitness_workouts ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), health_fitness_workouts)
        session.commit()
        results['health_fitness_workouts'] = len(health_fitness_workouts)
        print(f"  ✅ health_fitness_workouts: +{len(health_fitness_workouts)} records")
    except Exception as e:
        print(f"  ❌ health_fitness_workouts: {e}")
        session.rollback()
        results['health_fitness_workouts'] = 0

    # 3. health_fitness_workout_exercises (migrate from workout_exercises)
    try:
        health_fitness_workout_exercises = []
        for i in range(2000):  # 2000 workout exercise assignments for district scale
            workout_id = random.randint(1, 40)  # Reference health_fitness_workouts
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            health_fitness_workout_exercises.append({
                'workout_id': workout_id,
                'exercise_id': exercise_id,
                'sets': random.randint(1, 5),
                'reps': random.randint(5, 20),
                'duration_minutes': round(random.uniform(5, 30), 1),
                'order': random.randint(1, 10),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(health_fitness_workout_exercises[0].keys())
        # Quote the 'order' column since it's a reserved keyword
        quoted_columns = [f'"{col}"' if col == 'order' else col for col in columns]
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO health_fitness_workout_exercises ({', '.join(quoted_columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), health_fitness_workout_exercises)
        session.commit()
        results['health_fitness_workout_exercises'] = len(health_fitness_workout_exercises)
        print(f"  ✅ health_fitness_workout_exercises: +{len(health_fitness_workout_exercises)} records")
    except Exception as e:
        print(f"  ❌ health_fitness_workout_exercises: {e}")
        session.rollback()
        results['health_fitness_workout_exercises'] = 0

    # 4. health_fitness_workout_plans (migrate from workout_plans)
    try:
        health_fitness_workout_plans = []
        for i in range(1000):  # 1000 workout plans for district scale
            student_id = random.choice(ids['student_ids'])
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(28, 84))
            health_fitness_workout_plans.append({
                'student_id': student_id,
                'name': f'Health Fitness Plan {i+1}',
                'description': f'Comprehensive health fitness plan {i+1}',
                'start_date': start_date,
                'end_date': end_date,
                'frequency': random.randint(2, 6),
                'goals': json.dumps(['improve_fitness', 'lose_weight', 'gain_strength']),
                'progress_metrics': json.dumps({'weight_tracking': True, 'strength_measurements': True}),
                'schedule': json.dumps({'monday': 'cardio', 'wednesday': 'strength', 'friday': 'flexibility'}),
                'adaptations_needed': json.dumps(['knee_friendly', 'low_impact']),
                'notes': f'Workout plan notes {i+1}',
                'additional_data': json.dumps({'difficulty': 'intermediate', 'focus': 'overall_fitness'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(health_fitness_workout_plans[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO health_fitness_workout_plans ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), health_fitness_workout_plans)
        session.commit()
        results['health_fitness_workout_plans'] = len(health_fitness_workout_plans)
        print(f"  ✅ health_fitness_workout_plans: +{len(health_fitness_workout_plans)} records")
    except Exception as e:
        print(f"  ❌ health_fitness_workout_plans: {e}")
        session.rollback()
        results['health_fitness_workout_plans'] = 0

    # 5. health_fitness_workout_plan_workouts (migrate from existing plan_workouts)
    try:
        # Get existing plan_workouts to migrate
        existing_plan_workouts = session.execute(text("SELECT plan_id, workout_id, day_of_week, \"order\", created_at FROM workout_plan_workouts LIMIT 300")).fetchall()
        
        if not existing_plan_workouts:
            print("  ⚠️ No existing plan_workouts found, creating minimal data")
            health_fitness_workout_plan_workouts = []
            for i in range(1000):  # 1000 plan workout assignments for district scale
                plan_id = random.randint(1, 150)  # Reference health_fitness_workout_plans
                workout_id = random.randint(1, 40)  # Reference health_fitness_workouts
                health_fitness_workout_plan_workouts.append({
                    'plan_id': plan_id,
                    'workout_id': workout_id,
                    'day_of_week': random.randint(1, 7),
                    'order': random.randint(1, 10),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
        else:
            health_fitness_workout_plan_workouts = []
            # Map day names to integers
            day_mapping = {
                'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 'THURSDAY': 4,
                'FRIDAY': 5, 'SATURDAY': 6, 'SUNDAY': 7
            }
            for plan_id, workout_id, day_of_week, order, created_at in existing_plan_workouts:
                # Convert day name to integer
                day_int = day_mapping.get(day_of_week, random.randint(1, 7))
                health_fitness_workout_plan_workouts.append({
                    'plan_id': plan_id,
                    'workout_id': workout_id,
                    'day_of_week': day_int,
                    'order': order,
                    'created_at': created_at
                })
        
        columns = list(health_fitness_workout_plan_workouts[0].keys())
        # Quote the 'order' column since it's a reserved keyword
        quoted_columns = [f'"{col}"' if col == 'order' else col for col in columns]
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO health_fitness_workout_plan_workouts ({', '.join(quoted_columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), health_fitness_workout_plan_workouts)
        session.commit()
        results['health_fitness_workout_plan_workouts'] = len(health_fitness_workout_plan_workouts)
        print(f"  ✅ health_fitness_workout_plan_workouts: +{len(health_fitness_workout_plan_workouts)} records")
    except Exception as e:
        print(f"  ❌ health_fitness_workout_plan_workouts: {e}")
        session.rollback()
        results['health_fitness_workout_plan_workouts'] = 0

    # 6. health_fitness_workout_sessions (migrate from workout_sessions)
    try:
        health_fitness_workout_sessions = []
        for i in range(3000):  # 3000 workout sessions for district scale
            student_id = random.choice(ids['student_ids'])
            workout_id = random.randint(1, 40)  # Reference health_fitness_workouts
            start_time = datetime.now() - timedelta(hours=random.randint(1, 24))
            end_time = start_time + timedelta(minutes=random.randint(20, 90))
            health_fitness_workout_sessions.append({
                'workout_id': workout_id,
                'student_id': student_id,
                'start_time': start_time,
                'end_time': end_time,
                'completed': random.choice([True, False]),
                'performance_data': json.dumps({'heart_rate_avg': random.randint(120, 180), 'calories_burned': random.randint(100, 800)}),
                'difficulty_rating': random.randint(1, 5),
                'enjoyment_rating': random.randint(1, 5),
                'notes': f'Workout session notes {i+1}',
                'modifications_used': json.dumps(['knee_friendly', 'low_impact']),
                'additional_data': json.dumps({'intensity': 'moderate', 'focus': 'cardio'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            })
        
        columns = list(health_fitness_workout_sessions[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO health_fitness_workout_sessions ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), health_fitness_workout_sessions)
        session.commit()
        results['health_fitness_workout_sessions'] = len(health_fitness_workout_sessions)
        print(f"  ✅ health_fitness_workout_sessions: +{len(health_fitness_workout_sessions)} records")
    except Exception as e:
        print(f"  ❌ health_fitness_workout_sessions: {e}")
        session.rollback()
        results['health_fitness_workout_sessions'] = 0

    print("\n🏃 EXERCISE & PERFORMANCE TRACKING")
    print("-" * 70)
    
    # 7. exercise_base (migrate from exercises)
    try:
        exercise_base = []
        for i in range(500):  # 500 base exercises for district scale
            exercise_base.append({
                'name': f'Base Exercise {i+1}',
                'description': f'Fundamental exercise {i+1}',
                'type': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'BALANCE']),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'target_muscle_groups': ', '.join(random.sample(['chest', 'back', 'legs', 'arms', 'core'], random.randint(1, 3))),
                'equipment_needed': random.choice(['None', 'Dumbbells', 'Barbell', 'Machine', 'Bodyweight']),
                'instructions': f'Detailed instructions for exercise {i+1}',
                'safety_precautions': f'Safety precautions for exercise {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            })
        
        columns = list(exercise_base[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_base ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_base)
        session.commit()
        results['exercise_base'] = len(exercise_base)
        print(f"  ✅ exercise_base: +{len(exercise_base)} records")
    except Exception as e:
        print(f"  ❌ exercise_base: {e}")
        session.rollback()
        results['exercise_base'] = 0

    # 8. exercise_performances (migrate from performances)
    try:
        exercise_performances = []
        for i in range(5000):  # 5000 exercise performances for district scale
            student_id = random.choice(ids['student_ids'])
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            exercise_performances.append({
                'exercise_id': exercise_id,
                'student_id': student_id,
                'performance_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'duration_minutes': round(random.uniform(5, 60), 1),
                'repetitions': random.randint(1, 50),
                'sets': random.randint(1, 10),
                'weight': round(random.uniform(0, 100), 1),
                'notes': f'Performance notes {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(exercise_performances[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_performances ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_performances)
        session.commit()
        results['exercise_performances'] = len(exercise_performances)
        print(f"  ✅ exercise_performances: +{len(exercise_performances)} records")
    except Exception as e:
        print(f"  ❌ exercise_performances: {e}")
        session.rollback()
        results['exercise_performances'] = 0

    # 9. exercise_routines (migrate from routines)
    try:
        exercise_routines = []
        for i in range(1000):  # 1000 exercise routines for district scale
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            routine_id = random.randint(1, 50)  # Reference routines
            exercise_routines.append({
                'exercise_id': exercise_id,
                'routine_id': routine_id,
                'sets': random.randint(1, 5),
                'reps': random.randint(5, 25),
                'duration_minutes': random.randint(10, 60),
                'routine_metadata': json.dumps({
                    'name': f'Exercise Routine {i+1}',
                    'description': f'Structured exercise routine {i+1}',
                    'routine_type': random.choice(['WARMUP', 'MAIN', 'COOLDOWN', 'STRETCH']),
                    'difficulty_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                    'target_goals': ['strength', 'endurance', 'flexibility'],
                    'equipment_needed': random.sample(['dumbbells', 'mat', 'resistance_band'], random.randint(0, 2))
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(exercise_routines[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_routines ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_routines)
        session.commit()
        results['exercise_routines'] = len(exercise_routines)
        print(f"  ✅ exercise_routines: +{len(exercise_routines)} records")
    except Exception as e:
        print(f"  ❌ exercise_routines: {e}")
        session.rollback()
        results['exercise_routines'] = 0

    # 10. exercise_sets (migrate from sets)
    try:
        exercise_sets = []
        for i in range(1500):  # 1500 exercise sets for district scale
            workout_exercise_id = random.randint(1, 100)  # Reference workout_exercises
            exercise_sets.append({
                'workout_exercise_id': workout_exercise_id,
                'set_number': random.randint(1, 10),
                'reps_completed': random.randint(1, 20),
                'weight_used': round(random.uniform(0, 100), 1),
                'duration_seconds': random.randint(30, 300),
                'distance_meters': round(random.uniform(0, 1000), 1),
                'rest_time_seconds': random.randint(30, 180),
                'notes': f'Set notes {i+1}',
                'performance_rating': random.randint(1, 5),
                'additional_data': json.dumps({'is_completed': random.choice([True, False])}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            })
        
        columns = list(exercise_sets[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_sets ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_sets)
        session.commit()
        results['exercise_sets'] = len(exercise_sets)
        print(f"  ✅ exercise_sets: +{len(exercise_sets)} records")
    except Exception as e:
        print(f"  ❌ exercise_sets: {e}")
        session.rollback()
        results['exercise_sets'] = 0

    # 11. exercise_techniques (migrate from techniques)
    try:
        exercise_techniques = []
        for i in range(800):  # 800 exercise techniques for district scale
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            exercise_techniques.append({
                'exercise_id': exercise_id,
                'name': f'Technique {i+1}',
                'description': f'Proper technique for exercise {i+1}',
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                'technique_metadata': json.dumps({'key_points': ['form', 'breathing', 'tempo'], 'common_mistakes': ['poor_form', 'too_fast', 'wrong_breathing']}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(exercise_techniques[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_techniques ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_techniques)
        session.commit()
        results['exercise_techniques'] = len(exercise_techniques)
        print(f"  ✅ exercise_techniques: +{len(exercise_techniques)} records")
    except Exception as e:
        print(f"  ❌ exercise_techniques: {e}")
        session.rollback()
        results['exercise_techniques'] = 0

    # 12. exercise_variations (migrate from variations)
    try:
        exercise_variations = []
        for i in range(1000):  # 1000 exercise variations for district scale
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            exercise_variations.append({
                'exercise_id': exercise_id,
                'name': f'Variation {i+1}',
                'description': f'Exercise variation {i+1}',
                'difficulty': random.choice(['EASIER', 'SAME', 'HARDER']),
                'instructions': f'Instructions for variation {i+1}',
                'video_url': f'https://example.com/variation/{i+1}',
                'image_url': f'https://example.com/images/variation/{i+1}.jpg',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(exercise_variations[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_variations ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_variations)
        session.commit()
        results['exercise_variations'] = len(exercise_variations)
        print(f"  ✅ exercise_variations: +{len(exercise_variations)} records")
    except Exception as e:
        print(f"  ❌ exercise_variations: {e}")
        session.rollback()
        results['exercise_variations'] = 0

    # 13. exercise_videos (migrate from videos)
    try:
        exercise_videos = []
        for i in range(1000):  # 1000 exercise videos for district scale
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            exercise_videos.append({
                'exercise_id': exercise_id,
                'video_url': f'https://example.com/video/{i+1}',
                'video_type': random.choice(['DEMONSTRATION', 'TUTORIAL', 'WARMUP', 'COOLDOWN']),
                'duration': random.randint(60, 600),
                'video_notes': f'Video notes for exercise {i+1}',
                'video_metadata': json.dumps({'quality': random.choice(['HD', 'FULL_HD', '4K']), 'language': random.choice(['EN', 'ES', 'FR'])}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(exercise_videos[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO exercise_videos ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), exercise_videos)
        session.commit()
        results['exercise_videos'] = len(exercise_videos)
        print(f"  ✅ exercise_videos: +{len(exercise_videos)} records")
    except Exception as e:
        print(f"  ❌ exercise_videos: {e}")
        session.rollback()
        results['exercise_videos'] = 0

    print("\n💪 WORKOUT MANAGEMENT")
    print("-" * 70)
    
    # 14. workout_exercises (migrate from existing)
    try:
        workout_exercises = []
        for i in range(2000):  # 2000 workout exercises for district scale
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            exercise_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            workout_exercises.append({
                'workout_id': workout_id,
                'exercise_id': exercise_id,
                'sets': random.randint(1, 5),
                'reps': random.randint(5, 25),
                'duration_minutes': round(random.uniform(1, 30), 1),
                'order': random.randint(1, 20),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(workout_exercises[0].keys())
        # Quote the 'order' column since it's a reserved keyword
        quoted_columns = [f'"{col}"' if col == 'order' else col for col in columns]
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO workout_exercises ({', '.join(quoted_columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), workout_exercises)
        session.commit()
        results['workout_exercises'] = len(workout_exercises)
        print(f"  ✅ workout_exercises: +{len(workout_exercises)} records")
    except Exception as e:
        print(f"  ❌ workout_exercises: {e}")
        session.rollback()
        results['workout_exercises'] = 0

    # 15. workout_performances (migrate from performances)
    try:
        workout_performances = []
        for i in range(4000):  # 4000 workout performances for district scale
            student_id = random.choice(ids['student_ids'])
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            workout_performances.append({
                'workout_id': workout_id,
                'student_id': student_id,
                'performance_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'duration_minutes': round(random.uniform(20, 90), 1),
                'calories_burned': round(random.uniform(100, 800), 1),
                'completed_exercises': random.randint(5, 20),
                'performance_metadata': json.dumps({'heart_rate_avg': random.randint(120, 180), 'heart_rate_max': random.randint(150, 200), 'total_sets': random.randint(10, 50)}),
                'notes': f'Workout performance notes {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(workout_performances[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO workout_performances ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), workout_performances)
        session.commit()
        results['workout_performances'] = len(workout_performances)
        print(f"  ✅ workout_performances: +{len(workout_performances)} records")
    except Exception as e:
        print(f"  ❌ workout_performances: {e}")
        session.rollback()
        results['workout_performances'] = 0

    # 16. workout_plan_workouts (migrate from plan_workouts)
    try:
        workout_plan_workouts = []
        for i in range(1000):  # 1000 plan workout assignments for district scale
            plan_id = random.randint(1, 100)  # Reference workout_plans
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            workout_plan_workouts.append({
                'plan_id': plan_id,
                'workout_id': workout_id,
                'day_of_week': random.choice(['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']),
                'order': random.randint(1, 10),
                'notes': f'Plan workout notes {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(workout_plan_workouts[0].keys())
        # Quote the 'order' column since it's a reserved keyword
        quoted_columns = [f'"{col}"' if col == 'order' else col for col in columns]
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO workout_plan_workouts ({', '.join(quoted_columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), workout_plan_workouts)
        session.commit()
        results['workout_plan_workouts'] = len(workout_plan_workouts)
        print(f"  ✅ workout_plan_workouts: +{len(workout_plan_workouts)} records")
    except Exception as e:
        print(f"  ❌ workout_plan_workouts: {e}")
        session.rollback()
        results['workout_plan_workouts'] = 0

    # 17. workout_sessions (migrate from sessions)
    try:
        workout_sessions = []
        for i in range(3000):  # 3000 workout sessions for district scale
            student_id = random.choice(ids['student_ids'])
            workout_id = random.choice(ids['workout_ids']) if ids['workout_ids'] else random.randint(1, 40)
            teacher_id = random.choice(ids['user_ids'])
            start_time = datetime.now() - timedelta(hours=random.randint(1, 24))
            end_time = start_time + timedelta(minutes=random.randint(20, 90))
            workout_sessions.append({
                'workout_id': workout_id,
                'student_id': student_id,
                'teacher_id': teacher_id,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': random.randint(20, 90),
                'calories_burned': random.randint(100, 800),
                'notes': f'Workout session notes {i+1}',
                'performance_rating': random.randint(1, 5),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(workout_sessions[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO workout_sessions ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), workout_sessions)
        session.commit()
        results['workout_sessions'] = len(workout_sessions)
        print(f"  ✅ workout_sessions: +{len(workout_sessions)} records")
    except Exception as e:
        print(f"  ❌ workout_sessions: {e}")
        session.rollback()
        results['workout_sessions'] = 0

    # 18. workoutbase (migrate from workouts)
    try:
        workoutbase = []
        for i in range(1000):  # 1000 base workouts for district scale
            workoutbase.append({
                'name': f'Base Workout {i+1}',
                'description': f'Fundamental workout {i+1}',
                'duration_minutes': random.randint(20, 90),
                'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                'target_audience': random.choice(['STUDENTS', 'TEACHERS', 'ADULTS', 'SENIORS', 'ATHLETES']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            })
        
        columns = list(workoutbase[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO workoutbase ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), workoutbase)
        session.commit()
        results['workoutbase'] = len(workoutbase)
        print(f"  ✅ workoutbase: +{len(workoutbase)} records")
    except Exception as e:
        print(f"  ❌ workoutbase: {e}")
        session.rollback()
        results['workoutbase'] = 0

    print("\n📊 HEALTH METRICS & GOALS")
    print("-" * 70)
    
    # 19. general_health_metrics (migrate from current metrics) - MOVED FIRST
    try:
        general_health_metrics = []
        for i in range(1000):  # 1000 current health metrics
            student_id = random.choice(ids['student_ids'])
            general_health_metrics.append({
                'student_id': student_id,
                'metric_type': random.choice(['weight', 'height', 'bmi', 'body_fat_percentage', 'muscle_mass']),
                'value': round(random.uniform(50, 200), 1),
                'unit': random.choice(['kg', 'cm', 'bmi', '%', 'lbs']),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'metadata': json.dumps({'source': 'manual', 'device': 'scale'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            })
        
        columns = list(general_health_metrics[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO general_health_metrics ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), general_health_metrics)
        session.commit()
        results['general_health_metrics'] = len(general_health_metrics)
        print(f"  ✅ general_health_metrics: +{len(general_health_metrics)} records")
    except Exception as e:
        print(f"  ❌ general_health_metrics: {e}")
        session.rollback()
        results['general_health_metrics'] = 0

    # 20. general_health_metric_history (migrate from health_metrics) - MOVED AFTER
    try:
        # First ensure general_health_metrics exist
        existing_metrics = session.execute(text("SELECT id FROM general_health_metrics ")).fetchall()
        if not existing_metrics:
            print("  ⚠️ No general_health_metrics found, skipping general_health_metric_history")
            results['general_health_metric_history'] = 0
        else:
            metric_ids = [row[0] for row in existing_metrics]
            general_health_metric_history = []
            for i in range(2000):  # 2000 health metric history records
                metric_id = random.choice(metric_ids)  # Use existing metric IDs
                general_health_metric_history.append({
                    'metric_id': metric_id,
                    'value': round(random.uniform(50, 200), 1),
                    'recorded_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'notes': f'Health metric history {i+1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                })
            
            columns = list(general_health_metric_history[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            query = f"INSERT INTO general_health_metric_history ({', '.join(columns)}) VALUES ({placeholders})"
            
            session.execute(text(query), general_health_metric_history)
            session.commit()
            results['general_health_metric_history'] = len(general_health_metric_history)
            print(f"  ✅ general_health_metric_history: +{len(general_health_metric_history)} records")
    except Exception as e:
        print(f"  ❌ general_health_metric_history: {e}")
        session.rollback()
        results['general_health_metric_history'] = 0

    # 21. general_skill_progress (create skill progress data)
    try:
        print("  📊 Creating general skill progress data...")
        general_skill_progress = []
        for i in range(2000):  # 2000 skill progress records for district scale
            student_id = random.choice(ids['student_ids'])
            general_skill_progress.append({
                'student_id': student_id,
                'skill_name': random.choice(['running', 'swimming', 'cycling', 'strength_training', 'flexibility', 'basketball', 'soccer', 'tennis']),
                'type': random.choice(['SKILL', 'FITNESS', 'BEHAVIOR', 'PERFORMANCE', 'PARTICIPATION', 'ATTENDANCE', 'ACHIEVEMENT', 'DEVELOPMENT']),
                'status': random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'NEEDS_IMPROVEMENT', 'ON_HOLD', 'CANCELLED']),
                'current_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                'target_level': random.choice(['INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                'confidence_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'performance_level': random.choice(['EXCELLENT', 'GOOD', 'SATISFACTORY', 'NEEDS_IMPROVEMENT', 'POOR']),
                'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'progress_percentage': round(random.uniform(0, 100), 1),
                'assessment_count': random.randint(1, 20),
                'last_assessment_id': random.randint(1, 100),
                'last_assessment_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'next_assessment_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'meta_data': json.dumps({'notes': f'Skill progress notes {i+1}', 'goals': f'Improve {random.choice(["endurance", "strength", "flexibility", "coordination"])}'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(general_skill_progress[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO general_skill_progress ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), general_skill_progress)
        session.commit()
        results['general_skill_progress'] = len(general_skill_progress)
        print(f"  ✅ general_skill_progress: +{len(general_skill_progress)} records")
    except Exception as e:
        print(f"  ❌ general_skill_progress: {e}")
        session.rollback()
        results['general_skill_progress'] = 0

    # 22. goal_activities (migrate from goals + activities)
    try:
        goal_activities = []
        for i in range(1500):  # 1500 goal activities for district scale
            goal_id = random.randint(1, 50)  # Reference goals
            activity_id = random.choice(ids['exercise_ids']) if ids['exercise_ids'] else random.randint(1, 500)
            goal_activities.append({
                'goal_id': goal_id,
                'activity_id': activity_id,
                'frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'AS_NEEDED']),
                'duration': random.randint(15, 120),
                'intensity': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'notes': f'Goal activity notes {i+1}',
                'schedule': json.dumps({'days': ['MONDAY', 'WEDNESDAY', 'FRIDAY'], 'time': '09:00'}),
                'progress_metrics': json.dumps({'completion_rate': random.uniform(0, 1), 'satisfaction': random.randint(1, 5)}),
                'adaptations': json.dumps({'modifications': ['easier', 'harder'], 'equipment': ['dumbbells']}),
                'equipment_needed': json.dumps(['dumbbells', 'mat', 'resistance_band']),
                'space_requirements': json.dumps({'min_area': '10x10', 'indoor': True}),
                'safety_considerations': json.dumps(['warm_up', 'proper_form', 'spotter']),
                'performance_history': json.dumps({'last_performance': 'good', 'trend': 'improving'}),
                'difficulty_adjustments': json.dumps({'last_adjustment': 'increased_weight', 'reason': 'too_easy'}),
                'feedback_history': json.dumps({'last_feedback': 'excellent_form', 'instructor': 'John_Doe'}),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'COMPLETED', 'CANCELLED']),
                'is_active': random.choice([True, False])
            })
        
        columns = list(goal_activities[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO goal_activities ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), goal_activities)
        session.commit()
        results['goal_activities'] = len(goal_activities)
        print(f"  ✅ goal_activities: +{len(goal_activities)} records")
    except Exception as e:
        print(f"  ❌ goal_activities: {e}")
        session.rollback()
        results['goal_activities'] = 0

    # 23. goal_adjustments (migrate from goal adjustments)
    try:
        goal_adjustments = []
        for i in range(1000):  # 1000 goal adjustments for district scale
            goal_id = random.randint(1, 100)  # Reference health_fitness_goals
            goal_adjustments.append({
                'goal_id': goal_id,
                'previous_target': round(random.uniform(50, 200), 1),
                'new_target': round(random.uniform(50, 200), 1),
                'previous_date': datetime.now() - timedelta(days=random.randint(30, 90)),
                'new_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'reason': f'Adjustment reason {i+1}',
                'adjusted_by': f'User_{random.choice(ids["user_ids"])}',
                'adjustment_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'additional_data': json.dumps({'adjustment_type': 'TARGET_CHANGE', 'notes': f'Adjustment notes {i+1}'})
            })
        
        columns = list(goal_adjustments[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO goal_adjustments ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), goal_adjustments)
        session.commit()
        results['goal_adjustments'] = len(goal_adjustments)
        print(f"  ✅ goal_adjustments: +{len(goal_adjustments)} records")
    except Exception as e:
        print(f"  ❌ goal_adjustments: {e}")
        session.rollback()
        results['goal_adjustments'] = 0

    # 24. goal_dependencies (migrate from goal relationships)
    try:
        goal_dependencies = []
        for i in range(1000):  # 1000 goal dependencies for district scale
            goal_id = random.randint(1, 50)  # Reference goals
            depends_on_goal_id = random.randint(1, 50)  # Reference goals
            goal_dependencies.append({
                'dependent_goal_id': goal_id,
                'prerequisite_goal_id': depends_on_goal_id
            })
        
        columns = list(goal_dependencies[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO goal_dependencies ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        session.execute(text(query), goal_dependencies)
        session.commit()
        results['goal_dependencies'] = len(goal_dependencies)
        print(f"  ✅ goal_dependencies: +{len(goal_dependencies)} records")
    except Exception as e:
        print(f"  ❌ goal_dependencies: {e}")
        session.rollback()
        results['goal_dependencies'] = 0

    # 25. goal_milestones (migrate from goal milestones)
    try:
        goal_milestones = []
        for i in range(1000):  # 1000 goal milestones for district scale
            goal_id = random.randint(1, 50)  # Reference goals
            is_completed = random.choice([True, False])
            goal_milestones.append({
                'goal_id': goal_id,
                'name': f'Milestone {i+1}',
                'description': f'Goal milestone {i+1}',
                'target_date': datetime.now() + timedelta(days=random.randint(1, 365)),
                'achieved_date': datetime.now() - timedelta(days=random.randint(1, 90)) if is_completed else None,
                'metrics': json.dumps({'completion_percentage': random.randint(0, 100), 'progress': 'on_track'}),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'difficulty_level': random.choice(['EASY', 'MEDIUM', 'HARD']),
                'effort_required': random.randint(1, 10),
                'prerequisites': json.dumps(['previous_milestone', 'training_completed']),
                'validation_criteria': json.dumps(['form_check', 'time_requirement', 'quality_standard']),
                'completion_evidence': json.dumps(['video_submission', 'instructor_signoff']),
                'feedback': f'Milestone feedback {i+1}',
                'status': random.choice(['PENDING', 'COMPLETED', 'CANCELLED']),
                'is_active': random.choice([True, False])
            })
        
        columns = list(goal_milestones[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO goal_milestones ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), goal_milestones)
        session.commit()
        results['goal_milestones'] = len(goal_milestones)
        print(f"  ✅ goal_milestones: +{len(goal_milestones)} records")
    except Exception as e:
        print(f"  ❌ goal_milestones: {e}")
        session.rollback()
        results['goal_milestones'] = 0

    # 26. goal_recommendations (migrate from recommendations)
    try:
        goal_recommendations = []
        for i in range(800):  # 800 goal recommendations for district scale
            student_id = random.choice(ids['student_ids'])
            goal_id = random.randint(1, 100)  # Reference health_fitness_goals
            goal_recommendations.append({
                'student_id': student_id,
                'goal_id': goal_id,
                'recommendation_type': random.choice(['EXERCISE', 'NUTRITION', 'LIFESTYLE', 'TRAINING']),
                'description': f'Goal recommendation {i+1}',
                'priority': random.randint(1, 5),
                'recommendation_metadata': json.dumps({'title': f'Recommendation {i+1}', 'category': 'fitness'}),
                'is_implemented': random.choice([True, False]),
                'recommendation_data': json.dumps({'implementation_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat() if random.choice([True, False]) else None}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        columns = list(goal_recommendations[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO goal_recommendations ({', '.join(columns)}) VALUES ({placeholders})"
        
        session.execute(text(query), goal_recommendations)
        session.commit()
        results['goal_recommendations'] = len(goal_recommendations)
        print(f"  ✅ goal_recommendations: +{len(goal_recommendations)} records")
    except Exception as e:
        print(f"  ❌ goal_recommendations: {e}")
        session.rollback()
        results['goal_recommendations'] = 0
    
    print(f"\n🎉 Phase 9 Health & Fitness: {sum(results.values())} records created")
    print(f"📊 Total tables processed: {len(results)}")
    print(f"✅ Successfully populated {len([r for r in results.values() if r > 0])} working tables")
    print("✅ Phase 9 health & fitness system completed successfully!")
    
    return results