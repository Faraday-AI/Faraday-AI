#!/usr/bin/env python
"""
Phase 7: Specialized Features - Properly Scaled for 3,915+ Students
Uses existing tables and scales record counts appropriately
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
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
        # Get user IDs (32 users)
        result = session.execute(text('SELECT id FROM users'))
        ids['user_ids'] = [row[0] for row in result.fetchall()]
        
        # Get student IDs (4,166 students)
        result = session.execute(text('SELECT id FROM students'))
        ids['student_ids'] = [row[0] for row in result.fetchall()]
        
        # Get school IDs (6 schools)
        result = session.execute(text('SELECT id FROM schools'))
        ids['school_ids'] = [row[0] for row in result.fetchall()]
        
        # Get activity IDs (1,024 activities)
        result = session.execute(text('SELECT id FROM activities'))
        ids['activity_ids'] = [row[0] for row in result.fetchall()]
        
        # Get class IDs (256 classes)
        result = session.execute(text('SELECT id FROM educational_classes'))
        ids['class_ids'] = [row[0] for row in result.fetchall()]
        
        # Get dashboard IDs (3 dashboards)
        result = session.execute(text('SELECT id FROM dashboards'))
        ids['dashboard_ids'] = [row[0] for row in result.fetchall()]
        
        # Get organization IDs (1 organization)
        result = session.execute(text('SELECT id FROM organizations'))
        ids['organization_ids'] = [row[0] for row in result.fetchall()]
        
        # Get role IDs (migrate from existing data)
        result = session.execute(text('SELECT id FROM roles'))
        ids['role_ids'] = [row[0] for row in result.fetchall()]
        if not ids['role_ids']:
            print("⚠️ No existing roles found, creating basic roles...")
            # Create basic roles if none exist
            basic_roles = [
                {'name': 'admin', 'description': 'Administrator role'},
                {'name': 'teacher', 'description': 'Teacher role'},
                {'name': 'student', 'description': 'Student role'},
                {'name': 'parent', 'description': 'Parent role'},
                {'name': 'staff', 'description': 'Staff role'},
                {'name': 'guest', 'description': 'Guest role'}
            ]
            for role in basic_roles:
                session.execute(text("""
                    INSERT INTO roles (name, description, status, is_active)
                    VALUES (:name, :description, :status, :is_active)
                """), {
                    'name': role['name'],
                    'description': role['description'],
                    'status': 'ACTIVE',
                    'is_active': True
                })
            session.commit()
            # Get the newly created role IDs
            result = session.execute(text('SELECT id FROM roles'))
            ids['role_ids'] = [row[0] for row in result.fetchall()]
            print(f"✅ Created {len(ids['role_ids'])} basic roles")
        
        # Get workout exercise IDs (migrate from existing data)
        result = session.execute(text('SELECT id FROM physical_education_workout_exercises LIMIT 100'))
        ids['workout_exercise_ids'] = [row[0] for row in result.fetchall()]
        if not ids['workout_exercise_ids']:
            # Try to get existing workout and exercise IDs from earlier phases
            result = session.execute(text('SELECT id FROM health_fitness_workouts ORDER BY id LIMIT 5'))
            existing_workout_ids = [row[0] for row in result.fetchall()]
            
            result = session.execute(text('SELECT id FROM health_fitness_exercises ORDER BY id LIMIT 10'))
            existing_exercise_ids = [row[0] for row in result.fetchall()]
            
            if existing_workout_ids and existing_exercise_ids:
                # Create workout exercises using existing data
                workout_exercises_data = []
                for i in range(1, 21):  # Create 20 workout exercises
                    workout_exercises_data.append({
                        'exercise_id': existing_exercise_ids[i % len(existing_exercise_ids)],
                        'workout_id': existing_workout_ids[i % len(existing_workout_ids)],
                        'order': i % 10,
                        'sets': random.randint(1, 5),
                        'reps': random.randint(5, 20),
                        'duration_minutes': round(random.uniform(5.0, 30.0), 1),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                        'updated_at': datetime.now()
                    })
                
                for we in workout_exercises_data:
                    session.execute(text('''
                        INSERT INTO health_fitness_workout_exercises 
                        (exercise_id, workout_id, "order", sets, reps, duration_minutes, created_at, updated_at)
                        VALUES (:exercise_id, :workout_id, :order, :sets, :reps, :duration_minutes, :created_at, :updated_at)
                    '''), we)
                session.commit()
                print("✅ Created 20 workout exercises from existing data")
                
                # Get the newly created workout exercise IDs
                result = session.execute(text('SELECT id FROM health_fitness_workout_exercises'))
                ids['workout_exercise_ids'] = [row[0] for row in result.fetchall()]
            else:
                print("⚠️ No existing workouts or exercises found to migrate from")
                ids['workout_exercise_ids'] = []
        
        print(f"✅ Retrieved dependency IDs: {len(ids['user_ids'])} users, {len(ids['student_ids'])} students, {len(ids['school_ids'])} schools")
        
    except Exception as e:
        print(f"⚠️ Error getting dependency IDs: {e}")
        # Fallback values
        ids = {
            'user_ids': list(range(1, 33)),
            'student_ids': list(range(1, 4167)),
            'school_ids': list(range(1, 7)),
            'activity_ids': list(range(1, 1025)),
            'class_ids': list(range(1, 257)),
            'dashboard_ids': list(range(1, 4)),
            'organization_ids': [1],
            'role_ids': list(range(1, 6))
        }
    
    return ids

def safe_insert(session: Session, table_name: str, data: List[Dict], batch_size: int = 100) -> int:
    """Safely insert data in batches with error handling"""
    if not data:
        return 0
    
    try:
        total_inserted = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            if batch:
                # Use raw SQL for better control
                columns = list(batch[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                session.execute(text(query), batch)
                total_inserted += len(batch)
        
        return total_inserted
    except Exception as e:
        print(f"⚠️ Error inserting into {table_name}: {e}")
        return 0

def seed_phase7_specialized_features(session: Session) -> Dict[str, int]:
    """Seed Phase 7: Specialized Features - 20 tables properly scaled for 3,915+ students"""
    print("🚀 PHASE 7: SPECIALIZED FEATURES")
    print("=" * 60)
    print("📊 Seeding 20 tables for advanced specialized features")
    print("🎯 Properly scaled for 3,915+ student district")
    print("=" * 60)
    
    results = {}
    
    # Get dependency IDs
    ids = get_dependency_ids(session)
    
    # Scale factors for 3,915+ students
    student_scale = len(ids['student_ids'])  # 4,166 students
    user_scale = len(ids['user_ids'])        # 32 users
    school_scale = len(ids['school_ids'])    # 6 schools
    
    print(f"📊 Scaling factors: {student_scale} students, {user_scale} users, {school_scale} schools")
    
    # 1. User Management Tables (10 tables)
    print("\n👤 USER MANAGEMENT TABLES")
    print("-" * 40)
    
    # user_profiles (migrate from existing users)
    try:
        # Always migrate from all users, regardless of existing profiles
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_profiles = []
            for user_id in all_users:
                additional_profiles.append({
                    'user_id': user_id,
                    'bio': f'User profile for teacher {user_id}',
                    'timezone': random.choice(['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']),
                    'language': random.choice(['en', 'es', 'fr']),
                    'notification_preferences': json.dumps({'email': True, 'push': True, 'sms': False}),
                    'custom_settings': json.dumps({'theme': 'light', 'layout': 'default'}),
                    'metadata': json.dumps({'source': 'phase7_seeding', 'version': '1.0'})
                })
            
            inserted = safe_insert(session, 'user_profiles', additional_profiles)
            results['user_profiles'] = inserted
            print(f"  ✅ user_profiles: +{inserted} records (migrated from all users)")
        else:
            results['user_profiles'] = 0
            print(f"  ⚠️ user_profiles: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ user_profiles: {e}")
        results['user_profiles'] = 0
    
    # user_sessions (migrate from existing users)
    try:
        # Always migrate from all users, regardless of existing sessions
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_sessions = []
            for user_id in all_users:
                # Create 2 sessions per user
                for session_num in range(2):
                    additional_sessions.append({
                        'user_id': user_id,
                        'session_token': f'session_{user_id}_{session_num+1}_{random.randint(1000, 9999)}',
                        'ip_address': f'192.168.1.{random.randint(1, 254)}',
                        'user_agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'last_activity': datetime.now() - timedelta(hours=random.randint(1, 24)),
                        'expires_at': datetime.now() + timedelta(hours=random.randint(1, 8)),
                        'is_active': True,
                        'status': 'ACTIVE'
                    })
            
            inserted = safe_insert(session, 'user_sessions', additional_sessions)
            results['user_sessions'] = inserted
            print(f"  ✅ user_sessions: +{inserted} records (migrated from all users)")
        else:
            results['user_sessions'] = 0
            print(f"  ⚠️ user_sessions: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ user_sessions: {e}")
        results['user_sessions'] = 0
    
    # 2. Feedback & Communication Tables (15 tables)
    print("\n💬 FEEDBACK & COMMUNICATION TABLES")
    print("-" * 40)
    
    # messages (migrate from existing users)
    try:
        # Always create messages from all users
        additional_messages = []
        for i in range(1000):  # Create 1000 messages
            sender_id = random.choice(ids['user_ids'])
            receiver_id = random.choice(ids['user_ids'])
            additional_messages.append({
                'sender_id': sender_id,
                'recipient_id': receiver_id,
                'subject': f'Message {i+1} Subject',
                'content': f'Message {i+1}: Important communication about student progress',
                'status': random.choice(['SENT', 'DELIVERED', 'READ']),
                'sent_at': datetime.now() - timedelta(hours=random.randint(1, 168))
            })
        
        inserted = safe_insert(session, 'messages', additional_messages)
        results['messages'] = inserted
        print(f"  ✅ messages: +{inserted} records (migrated from all users)")
    except Exception as e:
        print(f"  ❌ messages: {e}")
        results['messages'] = 0
    
    # feedback (migrate from existing users)
    try:
        # Always create feedback from all users
        additional_feedback = []
        for i in range(1000):  # Create 1000 feedback records
            user_id = random.choice(ids['user_ids'])
            additional_feedback.append({
                'feedback_type': random.choice(['PERFORMANCE', 'BEHAVIOR', 'ACADEMIC', 'SOCIAL']),
                'content': json.dumps({'message': f'Feedback {i+1}: Student performance review and recommendations'}),
                'rating': random.randint(1, 5),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'user_id': user_id,
                'status': 'ACTIVE',
                'is_active': True,
                'metadata': json.dumps({'source': 'phase7_seeding', 'category': 'student_review'})
            })
        
        inserted = safe_insert(session, 'feedback', additional_feedback)
        results['feedback'] = inserted
        print(f"  ✅ feedback: +{inserted} records (migrated from all users)")
    except Exception as e:
        print(f"  ❌ feedback: {e}")
        results['feedback'] = 0
    
    # 3. Dashboard & Analytics Tables (20 tables)
    print("\n📊 DASHBOARD & ANALYTICS TABLES")
    print("-" * 40)
    
    # dashboard_widgets (migrate from existing users)
    try:
        # Always create widgets from all users
        additional_widgets = []
        for i in range(320):  # Create 320 widgets (10 per user)
            user_id = random.choice(ids['user_ids'])
            dashboard_id = random.choice(ids['dashboard_ids'])
            additional_widgets.append({
                'user_id': user_id,
                'dashboard_id': dashboard_id,
                'name': f'Widget {i+1}',
                'description': f'Dashboard widget {i+1} for analytics',
                'widget_type': 'CHART',  # Use valid enum value
                'layout_position': 'TOP_LEFT',  # Use valid enum value
                'size': json.dumps({'width': 300, 'height': 200}),
                'configuration': json.dumps({'chart_type': 'bar', 'data_source': 'student_performance'}),
                'is_active': True,
                'is_visible': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 90))
            })
        
        inserted = safe_insert(session, 'dashboard_widgets', additional_widgets)
        results['dashboard_widgets'] = inserted
        print(f"  ✅ dashboard_widgets: +{inserted} records (migrated from all users)")
    except Exception as e:
        print(f"  ❌ dashboard_widgets: {e}")
        results['dashboard_widgets'] = 0
    
    # 4. Physical Education Advanced Tables (15 tables)
    print("\n🏃 PHYSICAL EDUCATION ADVANCED TABLES")
    print("-" * 40)
    
    # workout_plans (migrate from existing students)
    try:
        # Always create workout plans from all students
        additional_plans = []
        for i in range(len(ids['student_ids'])):  # Create one plan per student
            student_id = ids['student_ids'][i % len(ids['student_ids'])]
            teacher_id = ids['user_ids'][i % len(ids['user_ids'])]
            
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            additional_plans.append({
                'student_id': student_id,
                'teacher_id': teacher_id,
                'name': f'Workout Plan {i+1}',
                'description': f'Customized workout plan for student {student_id}',
                'start_date': start_date,
                'end_date': start_date + timedelta(weeks=random.randint(4, 12)),
                'frequency': random.choice(['DAILY', 'WEEKLY', 'BIWEEKLY']),
                'goals': f'Improve fitness and health for student {student_id}',
                'notes': f'Personalized workout plan created by teacher {teacher_id}',
                'created_at': start_date
            })
        
        inserted = safe_insert(session, 'workout_plans', additional_plans)
        results['workout_plans'] = inserted
        print(f"  ✅ workout_plans: +{inserted} records (migrated from all students)")
    except Exception as e:
        print(f"  ❌ workout_plans: {e}")
        results['workout_plans'] = 0
    
        # exercise_sets (migrate from workout_exercises)
        try:
            existing_count = session.execute(text('SELECT COUNT(*) FROM exercise_sets')).scalar()
            if existing_count > 0:
                print(f"  📊 exercise_sets already has {existing_count} records, migrating additional data...")
            
            # Get workout_exercises IDs
            workout_exercise_result = session.execute(text('SELECT id FROM workout_exercises LIMIT 100'))
            workout_exercise_ids = [row[0] for row in workout_exercise_result.fetchall()]
            
            if workout_exercise_ids:
                additional_exercise_sets = []
                for i in range(100):  # Create 100 additional exercise sets
                    workout_exercise_id = random.choice(workout_exercise_ids)
                    additional_exercise_sets.append({
                        'workout_exercise_id': workout_exercise_id,
                        'set_number': random.randint(1, 5),
                        'reps_completed': random.randint(5, 20),
                        'weight_used': round(random.uniform(10.0, 100.0), 1),
                        'duration_seconds': random.randint(30, 300),
                        'distance_meters': round(random.uniform(0.0, 1000.0), 1),
                        'rest_time_seconds': random.randint(30, 120),
                        'notes': f'Exercise set {i+1} notes',
                        'performance_rating': random.randint(1, 10),
                        'additional_data': json.dumps({'intensity': 'moderate', 'form_quality': 'good'}),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                inserted = safe_insert(session, 'exercise_sets', additional_exercise_sets)
                results['exercise_sets'] = existing_count + inserted
                print(f"  ✅ exercise_sets: +{inserted} additional records (migrated from workout_exercises)")
            else:
                results['exercise_sets'] = existing_count
                print(f"  ⚠️ exercise_sets: {existing_count} records (no workout_exercises available for migration)")
        except Exception as e:
            print(f"  ❌ exercise_sets: {e}")
            results['exercise_sets'] = 0
    
    # exercise_progress (migrate from existing data) - using correct schema
    try:
        # Always create exercise progress from existing data
        student_data = session.execute(text('SELECT id FROM students LIMIT 50')).fetchall()
        exercise_data = session.execute(text('SELECT id FROM exercises LIMIT 20')).fetchall()
        
        if student_data and exercise_data:
            additional_progress = []
            for i in range(100):  # Create 100 progress records
                student = random.choice(student_data)
                exercise = random.choice(exercise_data)
                additional_progress.append({
                    'student_id': student[0],
                    'exercise_id': exercise[0],  # Use actual exercise ID
                    'progress_date': datetime.now() - timedelta(days=random.randint(1, 60)),
                    'progress_metadata': json.dumps({
                        'progress_value': round(random.uniform(0, 100), 2),
                        'notes': f'Progress for exercise {exercise[0]} - Student {student[0]}',
                        'improvement': round(random.uniform(-10, 20), 2)
                    }),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            inserted = safe_insert(session, 'exercise_progress', additional_progress)
            results['exercise_progress'] = inserted
            print(f"  ✅ exercise_progress: +{inserted} records (migrated from students & exercises)")
        else:
            results['exercise_progress'] = 0
            print(f"  ⚠️ exercise_progress: no student/exercise data to migrate")
    except Exception as e:
        print(f"  ❌ exercise_progress: {e}")
        results['exercise_progress'] = 0
    
    # 5. Security & Access Tables (10 tables)
    print("\n🔒 SECURITY & ACCESS TABLES")
    print("-" * 40)
    
    # security_policies (migrate from existing schools)
    try:
        # Always create security policies from all schools
        additional_policies = []
        for i in range(120):  # Create 120 policies (20 per school)
            additional_policies.append({
                'name': f'Security Policy {i+1}',
                'description': f'Comprehensive security policy for school district',
                'policy_type': random.choice(['ACCESS_CONTROL', 'DATA_PROTECTION', 'AUDIT']),
                'rules': json.dumps({
                    'access_level': 'standard',
                    'permissions': ['read', 'write'],
                    'restrictions': ['no_external_sharing'],
                    'compliance': 'FERPA'
                }),
                'priority': random.randint(1, 10),
                'is_active': True,
                'policy_metadata': json.dumps({
                    'version': '1.0',
                    'review_date': (datetime.now() + timedelta(days=90)).isoformat(),
                    'approver': 'IT_Department'
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'status': 'ACTIVE'
            })
        
        inserted = safe_insert(session, 'security_policies', additional_policies)
        results['security_policies'] = inserted
        print(f"  ✅ security_policies: +{inserted} records (migrated from all schools)")
    except Exception as e:
        print(f"  ❌ security_policies: {e}")
        results['security_policies'] = 0
    
    # user_roles (create basic roles and assign to users)
    try:
        # First create some basic roles if they don't exist
        existing_roles = session.execute(text('SELECT COUNT(*) FROM roles')).scalar()
        if existing_roles == 0:
            basic_roles = [
                {'name': 'admin', 'description': 'Administrator role', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'teacher', 'description': 'Teacher role', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'student', 'description': 'Student role', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'parent', 'description': 'Parent role', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'coach', 'description': 'Physical Education Coach', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'principal', 'description': 'School Principal', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True}
            ]
            safe_insert(session, 'roles', basic_roles)
            print(f"  ✅ Created {len(basic_roles)} basic roles")
        
        # Now assign roles to users - always create new assignments
        users = session.execute(text('SELECT id FROM users')).fetchall()
        roles = session.execute(text('SELECT id FROM roles')).fetchall()
        
        if users and roles:
            additional_roles = []
            for user in users:
                # Assign a random role to each user
                role = random.choice(roles)
                additional_roles.append({
                    'user_id': user[0],
                    'role_id': role[0]
                })
            
            inserted = safe_insert(session, 'user_roles', additional_roles)
            results['user_roles'] = inserted
            print(f"  ✅ user_roles: +{inserted} records (assigned roles to users)")
        else:
            results['user_roles'] = 0
            print(f"  ⚠️ user_roles: no users or roles found")
    except Exception as e:
        print(f"  ❌ user_roles: {e}")
        results['user_roles'] = 0
    
    # 6. Assessment & Progress Tables (15 tables)
    print("\n📈 ASSESSMENT & PROGRESS TABLES")
    print("-" * 40)
    
    # progress_metrics (migrate from existing data) - using correct schema
    try:
        # Always create progress metrics from existing data
        progress_data = session.execute(text('SELECT id FROM exercise_progress LIMIT 50')).fetchall()
        
        if progress_data:
            additional_metrics = []
            for i in range(100):  # Create 100 progress metrics
                progress_id = random.choice(progress_data)[0]
                additional_metrics.append({
                    'progress_id': progress_id,  # Reference to exercise_progress
                    'metric_type': random.choice(['PERFORMANCE', 'ATTENDANCE', 'ENGAGEMENT', 'SKILL_LEVEL', 'ENDURANCE']),
                    'metric_value': round(random.uniform(0, 100), 2),
                    'unit': random.choice(['percentage', 'score', 'minutes', 'reps', 'points']),
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 90)),
                    'context_data': json.dumps({
                        'category': 'fitness',
                        'subcategory': random.choice(['strength', 'cardio', 'flexibility']),
                        'notes': f'Metric for progress {progress_id}'
                    }),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 90))
                })
            
            inserted = safe_insert(session, 'progress_metrics', additional_metrics)
            results['progress_metrics'] = inserted
            print(f"  ✅ progress_metrics: +{inserted} records (migrated from exercise_progress)")
        else:
            results['progress_metrics'] = 0
            print(f"  ⚠️ progress_metrics: no progress data to migrate from")
    except Exception as e:
        print(f"  ❌ progress_metrics: {e}")
        results['progress_metrics'] = 0
    
    # 7. Additional User Management Tables (15 tables)
    print("\n👥 ADDITIONAL USER MANAGEMENT TABLES")
    print("-" * 40)
    
    # user_activities (migrate from existing users)
    try:
        # Always create activities from all users
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_activities = []
            for user_id in all_users:
                # Create 5 activities per user
                for activity_num in range(5):
                    additional_activities.append({
                        'user_id': user_id,
                        'activity_type': random.choice(['LOGIN', 'LOGOUT', 'PAGE_VIEW', 'DATA_UPDATE', 'REPORT_GENERATE']),
                        'activity_data': json.dumps({
                            'description': f'User activity {activity_num + 1} for user {user_id}',
                            'session_duration': random.randint(300, 3600),
                            'page_views': random.randint(1, 10)
                        }),
                        'session_id': f'session_{user_id}_{activity_num + 1}',
                        'timestamp': datetime.now() - timedelta(hours=random.randint(1, 168)),
                        'ip_address': f'192.168.1.{random.randint(1, 254)}',
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'location_data': json.dumps({
                            'country': 'US',
                            'city': 'New York',
                            'timezone': 'America/New_York'
                        })
                    })
            
            inserted = safe_insert(session, 'user_activities', additional_activities)
            results['user_activities'] = inserted
            print(f"  ✅ user_activities: +{inserted} records (migrated from all users)")
        else:
            results['user_activities'] = 0
            print(f"  ⚠️ user_activities: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ user_activities: {e}")
        results['user_activities'] = 0
    
    # user_behaviors (migrate from existing users)
    try:
        # Always create behaviors from all users
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_behaviors = []
            for user_id in all_users:
                additional_behaviors.append({
                    'user_id': user_id,
                    'behavior_type': random.choice(['FREQUENT_USER', 'CASUAL_USER', 'POWER_USER', 'ADMIN_USER']),
                    'behavior_data': json.dumps({
                        'frequency_score': round(random.uniform(0.1, 1.0), 2),
                        'engagement_level': random.choice(['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']),
                        'preferences': {
                            'theme': random.choice(['light', 'dark']),
                            'notifications': random.choice([True, False]),
                            'auto_save': random.choice([True, False])
                        }
                    }),
                    'confidence_score': round(random.uniform(0.5, 1.0), 2),
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'analysis_period': random.choice(['DAILY', 'WEEKLY', 'MONTHLY'])
                })
            
            inserted = safe_insert(session, 'user_behaviors', additional_behaviors)
            results['user_behaviors'] = inserted
            print(f"  ✅ user_behaviors: +{inserted} records (migrated from all users)")
        else:
            results['user_behaviors'] = 0
            print(f"  ⚠️ user_behaviors: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ user_behaviors: {e}")
        results['user_behaviors'] = 0
    
    # user_engagements (migrate from existing users)
    try:
        # Always create engagements from all users
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_engagements = []
            for user_id in all_users:
                additional_engagements.append({
                    'user_id': user_id,
                    'engagement_score': round(random.uniform(0.0, 100.0), 2),
                    'session_count': random.randint(1, 100),
                    'avg_session_duration': round(random.uniform(300.0, 3600.0), 2),
                    'feature_usage': json.dumps({
                        'dashboard_views': random.randint(10, 100),
                        'reports_generated': random.randint(1, 20),
                        'settings_changed': random.randint(0, 10)
                    }),
                    'retention_metrics': json.dumps({
                        'days_since_last_login': random.randint(1, 30),
                        'consecutive_days': random.randint(1, 7),
                        'total_logins': random.randint(10, 200)
                    }),
                    'churn_risk': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'period': random.choice(['DAILY', 'WEEKLY', 'MONTHLY'])
                })
            
            inserted = safe_insert(session, 'user_engagements', additional_engagements)
            results['user_engagements'] = inserted
            print(f"  ✅ user_engagements: +{inserted} records (migrated from all users)")
        else:
            results['user_engagements'] = 0
            print(f"  ⚠️ user_engagements: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ user_engagements: {e}")
        results['user_engagements'] = 0

    # 8. Additional Communication Tables (10 tables)
    print("\n📢 ADDITIONAL COMMUNICATION TABLES")
    print("-" * 40)
    
    # dashboard_notification_preferences (migrate from existing users)
    try:
        # Always create notification preferences from all users
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_notification_prefs = []
            for user_id in all_users:
                additional_notification_prefs.append({
                    'user_id': user_id,
                    'channel': random.choice(['EMAIL', 'PUSH', 'SMS', 'IN_APP']),
                    'type': random.choice(['SYSTEM', 'ALERT', 'UPDATE', 'REMINDER', 'ACHIEVEMENT']),
                    'enabled': random.choice([True, False]),
                    'priority_threshold': random.choice(['LOW', 'NORMAL', 'HIGH', 'URGENT']),
                    'quiet_hours_start': '22:00',
                    'quiet_hours_end': '08:00',
                    'timezone': 'America/New_York',
                    'batching_enabled': random.choice([True, False]),
                    'batching_interval': random.randint(5, 60),
                    'status': 'ACTIVE',
                    'is_active': True,
                    'metadata': json.dumps({
                        'frequency': random.choice(['IMMEDIATE', 'DAILY', 'WEEKLY']),
                        'preferences': {
                            'email': random.choice([True, False]),
                            'push': random.choice([True, False]),
                            'sms': random.choice([True, False])
                        }
                    })
                })
            
            inserted = safe_insert(session, 'dashboard_notification_preferences', additional_notification_prefs)
            results['dashboard_notification_preferences'] = inserted
            print(f"  ✅ dashboard_notification_preferences: +{inserted} records (migrated from all users)")
        else:
            results['dashboard_notification_preferences'] = 0
            print(f"  ⚠️ dashboard_notification_preferences: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ dashboard_notification_preferences: {e}")
        results['dashboard_notification_preferences'] = 0

    # 9. Analytics & Reporting Tables (15 tables)
    print("\n📊 ANALYTICS & REPORTING TABLES")
    print("-" * 40)
    
    # analytics_events (migrate from existing users)
    try:
        # Always create analytics events from all users
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_analytics = []
            for user_id in all_users:
                # Create 10 analytics events per user
                for event_num in range(10):
                    additional_analytics.append({
                        'user_id': user_id,
                        'event_type': random.choice(['PAGE_VIEW', 'CLICK', 'SEARCH', 'DOWNLOAD', 'UPLOAD']),
                        'event_data': json.dumps({
                            'event_name': f'Event {event_num + 1}',
                            'page': f'/page/{event_num + 1}',
                            'duration': random.randint(10, 300)
                        }),
                        'session_id': f'session_{user_id}_{event_num + 1}',
                        'timestamp': datetime.now() - timedelta(hours=random.randint(1, 168)),
                        'source': 'web',
                        'version': '1.0.0',
                        'event_metadata': json.dumps({
                            'browser': 'Chrome',
                            'os': 'Windows',
                            'device': 'desktop'
                        })
                    })
            
            inserted = safe_insert(session, 'analytics_events', additional_analytics)
            results['analytics_events'] = inserted
            print(f"  ✅ analytics_events: +{inserted} records (migrated from all users)")
        else:
            results['analytics_events'] = 0
            print(f"  ⚠️ analytics_events: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ analytics_events: {e}")
        results['analytics_events'] = 0
    
    # user_performances (migrate from existing users)
    try:
        # Always create performance data from all users
        result = session.execute(text('SELECT id FROM users'))
        all_users = [row[0] for row in result.fetchall()]
        
        if all_users:
            additional_performance = []
            for user_id in all_users:
                additional_performance.append({
                    'user_id': user_id,
                    'accuracy': round(random.uniform(0.8, 1.0), 2),
                    'speed': round(random.uniform(0.5, 1.0), 2),
                    'completion_rate': round(random.uniform(0.7, 1.0), 2),
                    'efficiency': round(random.uniform(0.7, 1.0), 2),
                    'skill_levels': json.dumps({
                        'technical': random.randint(1, 10),
                        'communication': random.randint(1, 10),
                        'problem_solving': random.randint(1, 10)
                    }),
                    'performance_data': json.dumps({
                        'response_time': random.randint(100, 2000),
                        'tasks_completed': random.randint(5, 50),
                        'errors_made': random.randint(0, 5)
                    }),
                    'timestamp': datetime.now() - timedelta(hours=random.randint(1, 72)),
                    'context': random.choice(['LOGIN', 'DATA_ENTRY', 'REPORT_GENERATION', 'SYSTEM_USE'])
                })
            
            inserted = safe_insert(session, 'user_performances', additional_performance)
            results['user_performances'] = inserted
            print(f"  ✅ user_performances: +{inserted} records (migrated from all users)")
        else:
            results['user_performances'] = 0
            print(f"  ⚠️ user_performances: no users found to migrate from")
    except Exception as e:
        print(f"  ❌ user_performances: {e}")
        results['user_performances'] = 0

    # 10. Assessment & Learning Tables (20 tables)
    print("\n🎓 ASSESSMENT & LEARNING TABLES")
    print("-" * 40)
    
    # general_assessments (migrate from existing students)
    try:
        # Always create assessments from all students
        result = session.execute(text('SELECT id FROM students LIMIT 100'))
        all_students = [row[0] for row in result.fetchall()]
        
        if all_students:
            additional_assessments = []
            for student_id in all_students:
                # Create 3 assessments per student
                for assess_num in range(3):
                    # Get a random activity_id from existing activities
                    activity_result = session.execute(text('SELECT id FROM activities LIMIT 1')).fetchone()
                    activity_id = activity_result[0] if activity_result else 1
                
                additional_assessments.append({
                    'activity_id': activity_id,
                    'student_id': student_id,
                    'type': random.choice(['SKILL', 'FITNESS', 'BEHAVIOR', 'PROGRESS', 'SAFETY', 'MOVEMENT']),
                    'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED']),
                    'level': random.choice(['EXCELLENT', 'GOOD', 'AVERAGE', 'NEEDS_IMPROVEMENT', 'POOR']),
                    'trigger': random.choice(['MANUAL', 'SCHEDULED', 'PERFORMANCE', 'PROGRESS', 'SAFETY', 'ADAPTATION', 'SYSTEM']),
                    'result': random.choice(['PASS', 'FAIL', 'PENDING', 'NEEDS_REVIEW']),
                    'score': round(random.uniform(0.0, 100.0), 2),
                    'feedback': f'Assessment feedback for student {student_id}',
                    'criteria': json.dumps({
                        'rubric': 'Standard assessment rubric',
                        'weighting': {'accuracy': 0.4, 'completeness': 0.3, 'timeliness': 0.3}
                    }),
                    'meta_data': json.dumps({
                        'subject': random.choice(['MATH', 'SCIENCE', 'ENGLISH', 'HISTORY']),
                        'difficulty': random.choice(['EASY', 'MEDIUM', 'HARD'])
                    }),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'completed_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            inserted = safe_insert(session, 'general_assessments', additional_assessments)
            results['general_assessments'] = inserted
            print(f"  ✅ general_assessments: +{inserted} records (migrated from all students)")
        else:
            results['general_assessments'] = 0
            print(f"  ⚠️ general_assessments: no students found to migrate from")
    except Exception as e:
        print(f"  ❌ general_assessments: {e}")
        results['general_assessments'] = 0
    
    # general_skill_assessments (migrate from existing assessments)
    try:
        # Always create skill assessments from existing assessments
        assessment_result = session.execute(text('SELECT id FROM general_assessments LIMIT 50')).fetchall()
        assessment_ids = [row[0] for row in assessment_result]
        
        if assessment_ids:
            additional_skill_assessments = []
            for assessment_id in assessment_ids:
                additional_skill_assessments.append({
                    'assessment_id': assessment_id,
                    'skill_name': f'Skill Assessment {assessment_id}',
                    'skill_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                    'performance_level': random.choice(['EXCELLENT', 'GOOD', 'SATISFACTORY', 'NEEDS_IMPROVEMENT', 'POOR']),
                    'confidence_level': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                    'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                    'analysis_type': random.choice(['MOVEMENT', 'PERFORMANCE', 'PROGRESS', 'SAFETY', 'TECHNIQUE', 'ENGAGEMENT', 'ADAPTATION', 'ASSESSMENT']),
                    'analysis_level': random.choice(['BASIC', 'STANDARD', 'DETAILED', 'COMPREHENSIVE', 'EXPERT']),
                    'analysis_status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED']),
                    'analysis_trigger': random.choice(['MANUAL', 'SCHEDULED', 'PERFORMANCE', 'PROGRESS', 'SAFETY', 'ADAPTATION', 'SYSTEM']),
                    'score': round(random.uniform(0.0, 100.0), 2),
                    'feedback': f'Skill assessment feedback for assessment {assessment_id}',
                    'criteria': json.dumps({
                        'rubric': 'Skill assessment rubric',
                        'weighting': {'technical': 0.4, 'social': 0.3, 'physical': 0.3}
                    }),
                    'meta_data': json.dumps({
                        'category': random.choice(['ACADEMIC', 'SOCIAL', 'PHYSICAL', 'COGNITIVE']),
                        'difficulty': random.choice(['EASY', 'MEDIUM', 'HARD'])
                    }),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'completed_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            inserted = safe_insert(session, 'general_skill_assessments', additional_skill_assessments)
            results['general_skill_assessments'] = inserted
            print(f"  ✅ general_skill_assessments: +{inserted} records (migrated from assessments)")
        else:
            results['general_skill_assessments'] = 0
            print(f"  ⚠️ general_skill_assessments: no assessments available to migrate from")
    except Exception as e:
        print(f"  ❌ general_skill_assessments: {e}")
        results['general_skill_assessments'] = 0

    # 11. System & Configuration Tables (15 tables)
    print("\n⚙️ SYSTEM & CONFIGURATION TABLES")
    print("-" * 40)
    
    # dashboard_theme_configs (create with correct schema)
    try:
        # Always create theme configurations
        additional_themes = []
        for i in range(10):  # Create 10 theme configurations
            additional_themes.append({
                'name': f'Theme {i+1}',
                'description': f'Custom theme configuration {i+1}',
                'colors': json.dumps({
                    'primary': f'#{random.randint(0, 0xFFFFFF):06x}',
                    'secondary': f'#{random.randint(0, 0xFFFFFF):06x}',
                    'background': f'#{random.randint(0, 0xFFFFFF):06x}',
                    'text': f'#{random.randint(0, 0xFFFFFF):06x}'
                }),
                'typography': json.dumps({
                    'font_family': random.choice(['Arial', 'Helvetica', 'Times New Roman', 'Georgia']),
                    'font_size': random.choice(['small', 'medium', 'large']),
                    'font_weight': random.choice(['normal', 'bold'])
                }),
                'spacing': json.dumps({
                    'padding': random.choice(['small', 'medium', 'large']),
                    'margin': random.choice(['small', 'medium', 'large'])
                }),
                'user_id': random.choice(ids['user_ids']),
                'status': 'ACTIVE',
                'is_active': True,
                'metadata': json.dumps({'created_by': 'phase7_seeding'})
            })
        
        inserted = safe_insert(session, 'dashboard_theme_configs', additional_themes)
        results['dashboard_theme_configs'] = inserted
        print(f"  ✅ dashboard_theme_configs: +{inserted} records (migrated from all users)")
    except Exception as e:
        print(f"  ❌ dashboard_theme_configs: {e}")
        results['dashboard_theme_configs'] = 0
    
    # dashboard_filter_configs (create with correct schema)
    try:
        existing_count = session.execute(text('SELECT COUNT(*) FROM dashboard_filter_configs')).scalar()
        if existing_count > 0:
            print(f"  📊 dashboard_filter_configs already has {existing_count} records, migrating additional data...")
        
        # Create dashboard filter configurations
        additional_filter_configs = []
        for i in range(50):  # Create 50 filter configurations
            additional_filter_configs.append({
                'filter_type': random.choice(['DATE_RANGE', 'CATEGORY', 'STATUS', 'PRIORITY', 'ASSIGNEE']),
                'name': f'Filter Config {i+1}',
                'configuration': json.dumps({
                    'date_range': {'start': '2024-01-01', 'end': '2024-12-31'},
                    'categories': ['urgent', 'important'],
                    'sort_by': 'created_at'
                }),
                'applied_to': json.dumps(['dashboard', 'reports', 'analytics']),
                'user_id': random.choice(ids['user_ids']),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'created_by': 'system', 'version': '1.0'})
            })
        
        inserted = safe_insert(session, 'dashboard_filter_configs', additional_filter_configs)
        results['dashboard_filter_configs'] = existing_count + inserted
        print(f"  ✅ dashboard_filter_configs: +{inserted} additional records")
    except Exception as e:
        print(f"  ❌ dashboard_filter_configs: {e}")
        results['dashboard_filter_configs'] = 0

    # 12. Miscellaneous Tables (20 tables)
    print("\n🔧 MISCELLANEOUS TABLES")
    print("-" * 40)
    
    # api_keys (create with correct schema)
    try:
        # Always create API keys for all users
        additional_keys = []
        for i in range(len(ids['user_ids'])):  # Create one key per user
            user_id = random.choice(ids['user_ids'])
            additional_keys.append({
                'key': f'api_key_{i+1}_{random.randint(1000, 9999)}',
                'name': f'API Key {i+1}',
                'description': f'API key for user {user_id}',
                'user_id': user_id,
                'permissions': json.dumps(['read', 'write']),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'expires_at': datetime.now() + timedelta(days=random.randint(30, 365)),
                'last_used_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'created_by': user_id,
                'source': 'DATABASE',  # Use valid enum value
                'environment': 'development',
                'service_name': 'faraday_ai'
            })
        
        inserted = safe_insert(session, 'api_keys', additional_keys)
        results['api_keys'] = inserted
        print(f"  ✅ api_keys: +{inserted} records (migrated from all users)")
    except Exception as e:
        print(f"  ❌ api_keys: {e}")
        results['api_keys'] = 0
    
    print(f"\n🎉 Phase 7 Specialized Features: {sum(results.values())} records created")
    print(f"📊 Total tables processed: {len(results)}")
    
    return results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase7_specialized_features(session)
        session.commit()
        print(f"\n🎉 Phase 7 completed! Created {sum(results.values())} records")
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()