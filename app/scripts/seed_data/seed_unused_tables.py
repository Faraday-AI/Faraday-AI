#!/usr/bin/env python3
"""
Seed script for populating unused tables that are showing 0 records.
This script copies data from active tables to populate unused table definitions.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import random
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_unused_tables(session: Session) -> Dict[str, int]:
    """
    Seed unused tables by copying data from active tables.
    Each table is handled independently to prevent cascading rollbacks.
    """
    print("🌱 Seeding unused tables with data from active tables...")
    
    total_records = 0
    results = {}
    
    # Get student IDs first to avoid variable scope issues
    try:
        student_ids = session.execute(text("SELECT id FROM students")).fetchall()
        if student_ids:
            student_ids = [s[0] for s in student_ids]
        else:
            student_ids = [1]  # Default fallback
    except Exception as e:
        print(f"  ⚠️  Could not get student IDs: {e}")
        student_ids = [1]  # Default fallback
    
    # 0. First, populate student_health table if it's empty
    print("  📊 Populating student_health table...")
    try:
        student_health_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        if student_health_count == 0:
            print("    📝 Creating basic student health records...")
            
            # Get student details for health records
            student_details = session.execute(text("""
                SELECT id, first_name, last_name, date_of_birth, grade_level 
                FROM students 
                LIMIT 100
            """)).fetchall()
            
            if student_details:
                health_records_created = 0
                for student in student_details:
                    try:
                        insert_query = text("""
                            INSERT INTO student_health 
                            (first_name, last_name, date_of_birth, gender, grade_level, student_metadata, 
                             created_at, updated_at, student_id, health_status, health_notes, health_metadata)
                            VALUES (:first_name, :last_name, :date_of_birth, :gender, :grade_level, :student_metadata,
                                   :created_at, :updated_at, :student_id, :health_status, :health_notes, :health_metadata)
                        """)
                        
                        # Generate random health data
                        gender = random.choice(['Male', 'Female', 'Other'])
                        health_status = random.choice(['Healthy', 'Good', 'Fair', 'Excellent'])
                        health_notes = random.choice([
                            'Student shows good physical development',
                            'Regular health check completed',
                            'No health concerns noted',
                            'Active and healthy student',
                            'Good fitness level maintained'
                        ])
                        
                        session.execute(insert_query, {
                            'first_name': student[1],
                            'last_name': student[2],
                            'date_of_birth': student[3] or datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                            'gender': gender,
                            'grade_level': student[4] or 'UNKNOWN',
                            'student_metadata': json.dumps({'source': 'seeding_script', 'health_created': True}),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now(),
                            'student_id': student[0],
                            'health_status': health_status,
                            'health_notes': health_notes,
                            'health_metadata': json.dumps({'health_score': random.randint(70, 100), 'fitness_level': random.choice(['Beginner', 'Intermediate', 'Advanced'])})
                        })
                        health_records_created += 1
                        
                    except Exception as e:
                        print(f"      ⚠️  Could not create health record for student {student[0]}: {e}")
                        continue
                
                session.flush()
                session.commit()  # Commit student_health data
                print(f"    ✅ Created {health_records_created} student health records")
                results['student_health'] = health_records_created
                total_records += health_records_created
            else:
                print("    ⚠️  No student details found")
                results['student_health'] = 0
        else:
            print(f"    ✅ student_health table already has {student_health_count} records")
            results['student_health'] = student_health_count
            
    except Exception as e:
        print(f"    ❌ Error populating student_health: {e}")
        results['student_health'] = 0
        session.rollback()  # Rollback on error
    
    # 1. Now populate activity_performances table (copy from student_activity_performances)
    print("  📊 Populating activity_performances table...")
    try:
        # Check if student_health table now has data
        student_health_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        if student_health_count == 0:
            print("    ⚠️  student_health table is still empty - cannot populate activity_performances")
            results['activity_performances'] = 0
        else:
            # Get existing data from student_activity_performances
            # We need to map student_id from students to student_health.id
            existing_performances = session.execute(text("""
                SELECT sap.student_id, sap.activity_id, sap.performance_level, sap.score, 
                       sap.completion_time, sap.notes, sap.feedback, sap.performance_metadata, sap.recorded_at,
                       sh.id as student_health_id
                FROM student_activity_performances sap
                JOIN student_health sh ON sap.student_id = sh.student_id
                LIMIT 1000
            """)).fetchall()
            
            if existing_performances:
                activity_performances_created = 0
                # Insert into activity_performances table
                for perf in existing_performances:
                    try:
                        insert_query = text("""
                            INSERT INTO activity_performances 
                            (student_id, activity_id, performance_date, performance_score, performance_notes, performance_metadata, created_at, updated_at)
                            VALUES (:student_id, :activity_id, :performance_date, :performance_score, :performance_notes, :performance_metadata, :created_at, :updated_at)
                        """)
                        
                        # Convert empty dict to JSON string for PostgreSQL
                        metadata = perf[7] if perf[7] else '{}'
                        if isinstance(metadata, dict):
                            metadata = json.dumps(metadata)
                        
                        # Ensure performance_date is a proper datetime
                        performance_date = perf[8] if perf[8] else datetime.now()
                        if isinstance(performance_date, dict):
                            performance_date = datetime.now()
                        
                        session.execute(insert_query, {
                            'student_id': perf[9],  # Use student_health_id
                            'activity_id': perf[1],
                            'performance_date': performance_date,  # Ensure it's a datetime
                            'performance_score': perf[3],  # score
                            'performance_notes': perf[5],  # notes
                            'performance_metadata': metadata,  # performance_metadata or empty JSON
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        })
                        activity_performances_created += 1
                        
                    except Exception as e:
                        print(f"      ⚠️  Could not create performance record: {e}")
                        continue
                
                session.flush()
                session.commit()  # Commit activity_performances data
                print(f"    ✅ Created {activity_performances_created} activity_performances records")
                results['activity_performances'] = activity_performances_created
                total_records += activity_performances_created
            else:
                print("    ⚠️  No existing student_activity_performances data found or no matching student_health records")
                results['activity_performances'] = 0
                
    except Exception as e:
        print(f"    ❌ Error populating activity_performances: {e}")
        results['activity_performances'] = 0
        session.rollback()  # Rollback on error
    
    # 2. Populate activity_preferences table (copy from pe_activity_preferences)
    print("  📊 Populating activity_preferences table...")
    try:
        # Check if student_health table has data
        student_health_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        if student_health_count == 0:
            print("    ⚠️  student_health table is empty - cannot populate activity_preferences")
            results['activity_preferences'] = 0
        else:
            # Check if activity_preferences table exists
            table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'activity_preferences')")).scalar()
            if not table_exists:
                print("    ⚠️  activity_preferences table does not exist")
                results['activity_preferences'] = 0
            else:
                # Get existing data from pe_activity_preferences
                # Use student_id directly (not student_health.id)
                existing_preferences = session.execute(text("""
                    SELECT sap.student_id, sap.activity_id, sap.preference_score, sap.preference_level, 
                           sap.notes, sap.preference_metadata, sap.last_updated
                    FROM pe_activity_preferences sap
                    LIMIT 1000
                """)).fetchall()
                
                if existing_preferences:
                    activity_preferences_created = 0
                    # Insert into activity_preferences table - using correct column names
                    for pref in existing_preferences:
                        try:
                            insert_query = text("""
                                INSERT INTO activity_preferences 
                                (student_id, activity_id, preference_level, preference_notes, preference_metadata, created_at, updated_at)
                                VALUES (:student_id, :activity_id, :preference_level, :preference_notes, :preference_metadata, :created_at, :updated_at)
                            """)
                            
                            # Convert empty dict to JSON string for PostgreSQL
                            metadata = pref[5] if pref[5] else '{}'
                            if isinstance(metadata, dict):
                                metadata = json.dumps(metadata)
                            
                            session.execute(insert_query, {
                                'student_id': pref[0], # Use student_id directly
                                'activity_id': pref[1],
                                'preference_level': pref[3],  # preference_level
                                'preference_notes': pref[4],  # notes -> preference_notes
                                'preference_metadata': metadata,  # preference_metadata or empty JSON
                                'created_at': datetime.now(),
                                'updated_at': datetime.now()
                            })
                            activity_preferences_created += 1
                            
                        except Exception as e:
                            print(f"      ⚠️  Could not create preference record: {e}")
                            continue
                    
                    session.flush()
                    session.commit()  # Commit activity_preferences data
                    print(f"    ✅ Created {activity_preferences_created} activity_preferences records")
                    results['activity_preferences'] = activity_preferences_created
                    total_records += activity_preferences_created
                else:
                    print("    ⚠️  No existing pe_activity_preferences data found or no matching student_health records")
                    results['activity_preferences'] = 0
                
    except Exception as e:
        print(f"    ❌ Error populating activity_preferences: {e}")
        results['activity_preferences'] = 0
        session.rollback()  # Rollback on error
    
    # 3. Populate student_health_goal_recommendations table
    print("  📊 Populating student_health_goal_recommendations table...")
    try:
        # Check if table exists
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'student_health_goal_recommendations')")).scalar()
        if not table_exists:
            print("    ⚠️  student_health_goal_recommendations table does not exist")
            results['student_health_goal_recommendations'] = 0
        else:
            # Get student health fitness goals to create recommendations
            # First check what columns exist in the table
            columns_result = session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'student_health_fitness_goals' 
                ORDER BY ordinal_position
            """)).fetchall()
            available_columns = [col[0] for col in columns_result]
            print(f"    📋 Available columns in student_health_fitness_goals: {available_columns}")
            
            # Build query based on available columns
            if 'current_value' in available_columns:
                goal_data = session.execute(text("""
                    SELECT shfg.id, shfg.student_id, shfg.goal_type, shfg.target_value, shfg.current_value
                    FROM student_health_fitness_goals shfg
                    LIMIT 100
                """)).fetchall()
            else:
                # Use available columns without current_value
                goal_data = session.execute(text("""
                    SELECT shfg.id, shfg.student_id, shfg.goal_type, shfg.target_value
                    FROM student_health_fitness_goals shfg
                    LIMIT 100
                """)).fetchall()
            
            if goal_data:
                recommendations_created = 0
                recommendation_types = ['NUTRITION', 'EXERCISE', 'SLEEP', 'HYDRATION', 'STRESS_MANAGEMENT']
                recommendation_levels = ['LOW', 'MEDIUM', 'HIGH']
                
                for goal in goal_data:
                    try:
                        insert_query = text("""
                            INSERT INTO student_health_goal_recommendations 
                            (goal_id, student_id, recommendation_type, description, priority, 
                             is_implemented, created_at, updated_at)
                            VALUES (:goal_id, :student_id, :recommendation_type, :description, 
                                    :priority, :is_implemented, :created_at, :updated_at)
                        """)
                        
                        # Handle both cases: with and without current_value
                        if len(goal) >= 5:  # Has current_value
                            description = f"Focus on {goal[2].lower()} activities to reach your target of {goal[3]}"
                        else:  # No current_value
                            description = f"Focus on {goal[2].lower()} activities to reach your target of {goal[3]}"
                        
                        session.execute(insert_query, {
                            'goal_id': goal[0],
                            'student_id': goal[1],
                            'recommendation_type': random.choice(recommendation_types),
                            'description': description,
                            'priority': random.randint(1, 5),  # Use integer priority instead of string
                            'is_implemented': random.choice([True, False]),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        })
                        recommendations_created += 1
                        
                    except Exception as e:
                        print(f"      ⚠️  Could not create recommendation record: {e}")
                        continue
                
                session.flush()
                print(f"    ✅ Created {recommendations_created} student_health_goal_recommendations records")
                results['student_health_goal_recommendations'] = recommendations_created
                total_records += recommendations_created
            else:
                print("    ⚠️  No student_health_fitness_goals data found")
                results['student_health_goal_recommendations'] = 0
                
    except Exception as e:
        print(f"    ❌ Error populating student_health_goal_recommendations: {e}")
        results['student_health_goal_recommendations'] = 0
        session.rollback()
    
    # 4. Populate feedback table (copy from dashboard_feedback)
    print("  📊 Populating feedback table...")
    try:
        # Check if feedback table exists
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'feedback')")).scalar()
        if not table_exists:
            print("    ⚠️  feedback table does not exist")
            results['feedback'] = 0
        else:
            # Get existing data from dashboard_feedback
            existing_feedback = session.execute(text("SELECT user_id, feedback_type, content, rating, created_at, status, priority FROM dashboard_feedback LIMIT 500")).fetchall()
            
            if existing_feedback:
                # Insert into feedback table - check what columns exist first
                try:
                    # Try to get table structure
                    columns_result = session.execute(text("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'feedback' 
                        ORDER BY ordinal_position
                    """)).fetchall()
                    
                    if columns_result:
                        available_columns = [col[0] for col in columns_result]
                        print(f"    📋 Available columns in feedback table: {available_columns}")
                        
                        # Check valid status values for the enum
                        try:
                            status_values_result = session.execute(text("""
                                SELECT unnest(enum_range(NULL::base_status_enum))
                            """)).fetchall()
                            valid_statuses = [row[0] for row in status_values_result] if status_values_result else ['ACTIVE']
                            print(f"    📋 Valid status values: {valid_statuses}")
                        except:
                            valid_statuses = ['ACTIVE', 'INACTIVE', 'PENDING']
                            print(f"    ⚠️  Could not determine valid status values, using defaults: {valid_statuses}")
                        
                        feedback_created = 0
                        # Build dynamic insert query based on available columns
                        for fb in existing_feedback:
                            try:
                                # Convert content to string if it's JSON
                                content_str = fb[2] if isinstance(fb[2], str) else json.dumps(fb[2])
                                
                                # Build dynamic column list and values
                                columns = []
                                values = {}
                                
                                if 'user_id' in available_columns:
                                    columns.append('user_id')
                                    values['user_id'] = fb[0]
                                
                                if 'feedback_type' in available_columns:
                                    columns.append('feedback_type')
                                    values['feedback_type'] = fb[1]
                                
                                if 'content' in available_columns:
                                    columns.append('content')
                                    values['content'] = content_str
                                
                                if 'rating' in available_columns:
                                    columns.append('rating')
                                    values['rating'] = fb[3]
                                
                                if 'status' in available_columns:
                                    columns.append('status')
                                    # Use a valid status value
                                    values['status'] = random.choice(valid_statuses)
                                
                                if 'priority' in available_columns:
                                    columns.append('priority')
                                    values['priority'] = fb[6] or 'medium'
                                
                                if columns:
                                    placeholders = ', '.join([f':{col}' for col in columns])
                                    insert_query = text(f"""
                                        INSERT INTO feedback 
                                        ({', '.join(columns)})
                                        VALUES ({placeholders})
                                    """)
                                
                                    session.execute(insert_query, values)
                                    feedback_created += 1
                                    
                            except Exception as e:
                                print(f"      ⚠️  Could not create feedback record: {e}")
                                continue
                        
                        session.flush()
                        session.commit()  # Commit feedback data
                        print(f"    ✅ Created {feedback_created} feedback records")
                        results['feedback'] = feedback_created
                        total_records += feedback_created
                    else:
                        print("    ⚠️  Could not determine feedback table structure")
                        results['feedback'] = 0
                        
                except Exception as e:
                    print(f"    ❌ Error determining feedback table structure: {e}")
                    results['feedback'] = 0
            else:
                print("    ⚠️  No existing dashboard_feedback data found")
                results['feedback'] = 0
    except Exception as e:
        print(f"    ❌ Error populating feedback: {e}")
        results['feedback'] = 0
        session.rollback()  # Rollback on error
    
    # 4. Populate health_fitness tables
    print("  📊 Populating health_fitness tables...")
    try:
        # Check if fitness_health_metrics table exists (the actual table name)
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'fitness_health_metrics')")).scalar()
        if not table_exists:
            print("    ⚠️  fitness_health_metrics table does not exist")
            results['fitness_health_metrics'] = 0
        else:
            # Create some basic health metrics records
            health_metrics_created = 0
            for i in range(50):
                try:
                    insert_query = text("""
                        INSERT INTO fitness_health_metrics 
                        (student_id, metric_type, value, unit, timestamp, notes, metric_metadata, created_at, updated_at)
                        VALUES (:student_id, :metric_type, :value, :unit, :timestamp, :notes, :metric_metadata, :created_at, :updated_at)
                    """)
                    
                    session.execute(insert_query, {
                        'student_id': random.choice(student_ids),
                        'metric_type': random.choice(['HEART_RATE', 'BLOOD_PRESSURE', 'TEMPERATURE', 'WEIGHT', 'HEIGHT']),
                        'value': random.uniform(60, 200),
                        'unit': random.choice(['BPM', 'MMHG', 'FAHRENHEIT', 'POUNDS', 'INCHES']),
                        'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
                        'notes': f"Health metric recording for {random.choice(['routine check', 'fitness assessment', 'health monitoring'])}",
                        'metric_metadata': json.dumps({'source': 'seeding_script', 'quality': 'good'}),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    health_metrics_created += 1
                    
                except Exception as e:
                    print(f"      ⚠️  Could not create health metric record: {e}")
                    continue
            
            session.flush()
            session.commit()  # Commit health_fitness data
            print(f"    ✅ Created {health_metrics_created} fitness_health_metrics records")
            results['fitness_health_metrics'] = health_metrics_created
            total_records += health_metrics_created
            
    except Exception as e:
        print(f"    ❌ Error populating health_fitness tables: {e}")
        results['fitness_health_metrics'] = 0
        session.rollback()  # Rollback on error
    
    # 5. Populate nutrition tables
    print("  📊 Populating nutrition tables...")
    try:
        # Check if nutrition_plans table exists
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'nutrition_plans')")).scalar()
        if not table_exists:
            print("    ⚠️  nutrition_plans table does not exist")
            results['nutrition_plans'] = 0
        else:
            # Create some basic nutrition plan records
            nutrition_plans_created = 0
            for i in range(30):
                try:
                    insert_query = text("""
                        INSERT INTO nutrition_plans 
                        (student_id, title, description, start_date, end_date, dietary_restrictions, calorie_target, macronutrient_targets, hydration_target, special_instructions, created_at, updated_at)
                        VALUES (:student_id, :title, :description, :start_date, :end_date, :dietary_restrictions, :calorie_target, :macronutrient_targets, :hydration_target, :special_instructions, :created_at, :updated_at)
                    """)
                    
                    session.execute(insert_query, {
                        'student_id': random.choice(student_ids),
                        'title': f"Nutrition Plan {i+1}",
                        'description': f"Comprehensive nutrition plan for student development and health",
                        'start_date': datetime.now(),
                        'end_date': datetime.now() + timedelta(days=30),
                        'dietary_restrictions': json.dumps({'restrictions': random.choice(['NONE', 'VEGETARIAN', 'GLUTEN_FREE', 'DAIRY_FREE'])}),
                        'calorie_target': random.randint(1500, 2500),
                        'macronutrient_targets': json.dumps({'protein': random.randint(60, 120), 'carbs': random.randint(150, 300), 'fat': random.randint(50, 100)}),
                        'hydration_target': random.uniform(2.0, 4.0),
                        'special_instructions': random.choice(['Focus on protein', 'Increase hydration', 'Limit processed foods', 'Eat more vegetables']),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    nutrition_plans_created += 1
                    
                except Exception as e:
                    print(f"      ⚠️  Could not create nutrition plan record: {e}")
                    continue
            
            session.flush()
            session.commit()  # Commit nutrition data
            print(f"    ✅ Created {nutrition_plans_created} nutrition_plans records")
            results['nutrition_plans'] = nutrition_plans_created
            total_records += nutrition_plans_created
            
    except Exception as e:
        print(f"    ❌ Error populating nutrition tables: {e}")
        results['nutrition_plans'] = 0
        session.rollback()  # Rollback on error
    
    # 6. Populate workout tables
    print("  📊 Populating workout tables...")
    try:
        # Check if workouts table exists
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'workouts')")).scalar()
        if not table_exists:
            print("    ⚠️  workouts table does not exist")
            results['workouts'] = 0
        else:
            # Create some basic workout records
            workouts_created = 0
            for i in range(40):
                try:
                    insert_query = text("""
                        INSERT INTO workouts 
                        (name, description, duration_minutes, difficulty, target_audience, created_at, updated_at)
                        VALUES (:name, :description, :duration_minutes, :difficulty, :target_audience, :created_at, :updated_at)
                    """)
                    
                    session.execute(insert_query, {
                        'name': f"Workout {i+1}",
                        'description': f"Comprehensive workout session for physical education and fitness development",
                        'duration_minutes': random.randint(20, 60),
                        'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                        'target_audience': random.choice(['ELEMENTARY', 'MIDDLE_SCHOOL', 'HIGH_SCHOOL', 'ALL_AGES']),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    workouts_created += 1
                    
                except Exception as e:
                    print(f"      ⚠️  Could not create workout record: {e}")
                    continue
            
            session.flush()
            session.commit()  # Commit workout data
            print(f"    ✅ Created {workouts_created} workouts records")
            results['workouts'] = workouts_created
            total_records += workouts_created
            
    except Exception as e:
        print(f"    ❌ Error populating workout tables: {e}")
        results['workouts'] = 0
        session.rollback()  # Rollback on error
    
    # 7. Populate equipment tables
    print("  📊 Populating equipment tables...")
    try:
        # Check if equipment_base table exists (the actual table with columns)
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'equipment_base')")).scalar()
        if not table_exists:
            print("    ⚠️  equipment_base table does not exist")
            results['equipment'] = 0
        else:
            # Create some basic equipment records
            equipment_created = 0
            for i in range(25):
                try:
                    insert_query = text("""
                        INSERT INTO equipment_base 
                        (name, type, status, last_maintenance, next_maintenance, maintenance_notes)
                        VALUES (:name, :type, :status, :last_maintenance, :next_maintenance, :maintenance_notes)
                    """)
                    
                    session.execute(insert_query, {
                        'name': f"Equipment {i+1}",
                        'type': random.choice(['BALLS', 'MATS', 'WEIGHTS', 'MACHINES', 'NETS', 'TOOLS']),
                        'status': random.choice(['AVAILABLE', 'IN_USE', 'MAINTENANCE', 'REPAIR', 'RETIRED', 'LOST', 'DAMAGED']),
                        'last_maintenance': datetime.now() - timedelta(days=random.randint(1, 90)),
                        'next_maintenance': datetime.now() + timedelta(days=random.randint(30, 180)),
                        'maintenance_notes': random.choice(['Regular maintenance completed', 'Minor repairs needed', 'Good condition', 'Requires inspection'])
                    })
                    equipment_created += 1
                    
                except Exception as e:
                    print(f"      ⚠️  Could not create equipment record: {e}")
                    continue
            
            session.flush()
            session.commit()  # Commit equipment data
            print(f"    ✅ Created {equipment_created} equipment records")
            results['equipment'] = equipment_created
            total_records += equipment_created
            
    except Exception as e:
        print(f"    ❌ Error populating equipment tables: {e}")
        results['equipment'] = 0
        session.rollback()  # Rollback on error
    
    print(f"\n✅ Unused tables seeding complete! Created {total_records} total records")
    print("📊 Results summary:")
    for table, count in results.items():
        print(f"  - {table}: {count} records")
    
    print(f"\n🎉 Successfully seeded unused tables with {total_records} records!")
    
    return results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        results = seed_unused_tables(session)
        print(f"\nFinal results: {results}")
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        session.rollback()
    finally:
        session.close() 