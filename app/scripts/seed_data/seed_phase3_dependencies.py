"""
Phase 3 Dependency Tables Seeding

This module seeds the core dependency tables that Phase 3 health & fitness system needs.
These tables must be seeded in Phase 1 to ensure they exist when Phase 3 runs.
"""

import random
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text


def seed_phase3_dependencies(session: Session) -> None:
    """
    Seed the core dependency tables for Phase 3 health & fitness system.
    
    This function creates and seeds:
    - goals
    - nutrition_plans  
    - meals
    - student_health
    - fitness_goals
    - student_health_fitness_goals
    - physical_education_nutrition_plans
    """
    
    print("  🔄 Seeding Phase 3 dependency tables...")
    
    # Get student IDs for foreign key references - use ALL students
    try:
        student_result = session.execute(text("SELECT id FROM students"))
        student_ids = [row[0] for row in student_result.fetchall()]
        print(f"  📊 Found {len(student_ids)} students for foreign key references")
    except Exception as e:
        print(f"  ⚠️  Could not get student IDs: {e}")
        student_ids = list(range(1, 101))  # Fallback range
    
    # Get user IDs for foreign key references
    try:
        user_result = session.execute(text("SELECT id FROM users LIMIT 50"))
        user_ids = [row[0] for row in user_result.fetchall()]
        print(f"  📊 Found {len(user_ids)} users for foreign key references")
    except Exception as e:
        print(f"  ⚠️  Could not get user IDs: {e}")
        user_ids = list(range(1, 51))  # Fallback range
    
    # 1. Seed goals table
    try:
        goal_count = session.execute(text("SELECT COUNT(*) FROM goals")).scalar()
        if goal_count == 0:
            goals_data = []
            for i in range(50):  # Create 50 goals
                goals_data.append({
                    'student_id': random.choice(student_ids) if student_ids else random.randint(1, 100),
                    'goal_type': random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']),
                    'description': f'Goal description {i + 1}',
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'priority': random.randint(1, 10),
                    'target_metrics': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'current_progress': json.dumps({"progress": round(random.uniform(0, 100), 2), "unit": "percentage"}),
                    'completion_percentage': round(random.uniform(0, 100), 2),
                    'difficulty_level': random.choice(['EASY', 'MEDIUM', 'HARD', 'EXPERT']),
                    'expected_duration': random.randint(30, 365),
                    'required_resources': json.dumps({"equipment": ["dumbbells", "mat"], "time": "30min"}),
                    'success_criteria': json.dumps({"criteria": f"Complete goal {i + 1}"}),
                    'risk_factors': json.dumps({"risks": ["injury", "motivation"]}),
                    'support_needed': json.dumps({"support": ["coach", "family"]}),
                    'last_progress_update': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'progress_history': json.dumps({"history": [{"date": "2024-01-01", "progress": 25}]}),
                    'blockers': json.dumps({"blockers": []}),
                    'achievements': json.dumps({"achievements": []}),
                    'motivation_level': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                    'engagement_metrics': json.dumps({"engagement": random.randint(1, 10)}),
                    'reward_system': json.dumps({"rewards": ["badge", "points"]}),
                    'parent_goal_id': None,
                    'is_template': False,
                    'is_recurring': False,
                    'recurrence_pattern': None,
                    'name': f'Goal {i + 1}',
                    'status': random.choice(['ACTIVE', 'PENDING', 'COMPLETED', 'CANCELLED']),
                    'is_active': True
                })
            
            session.execute(text("""
                INSERT INTO goals (student_id, goal_type, description, target_date, start_date, priority, 
                                 target_metrics, current_progress, completion_percentage, difficulty_level, 
                                 expected_duration, required_resources, success_criteria, risk_factors, 
                                 support_needed, last_progress_update, progress_history, blockers, achievements, 
                                 motivation_level, engagement_metrics, reward_system, parent_goal_id, 
                                 is_template, is_recurring, recurrence_pattern, name, status, is_active)
                VALUES (:student_id, :goal_type, :description, :target_date, :start_date, :priority, 
                        :target_metrics, :current_progress, :completion_percentage, :difficulty_level, 
                        :expected_duration, :required_resources, :success_criteria, :risk_factors, 
                        :support_needed, :last_progress_update, :progress_history, :blockers, :achievements, 
                        :motivation_level, :engagement_metrics, :reward_system, :parent_goal_id, 
                        :is_template, :is_recurring, :recurrence_pattern, :name, :status, :is_active)
            """), goals_data)
            session.commit()
            print(f"  ✅ Seeded goals table: {len(goals_data)} records")
        else:
            print(f"  ⚠️  Goals table already has {goal_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding goals: {e}")
    
    # 2. Seed nutrition_plans table
    try:
        plan_count = session.execute(text("SELECT COUNT(*) FROM nutrition_plans")).scalar()
        if plan_count == 0:
            plans_data = []
            for i in range(60):  # Create 60 nutrition plans to include IDs 35, 39
                plans_data.append({
                'student_id': random.choice(student_ids) if student_ids else random.randint(1, 100),
                'title': f'Nutrition Plan {i + 1}',
                'description': f'Description for nutrition plan {i + 1}',
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                'dietary_restrictions': json.dumps({"restrictions": []}),
                'calorie_target': random.randint(1500, 3000),
                'macronutrient_targets': json.dumps({"protein": random.randint(50, 150), "carbs": random.randint(100, 300), "fat": random.randint(30, 100)}),
                'hydration_target': round(random.uniform(1.5, 3.0), 2),
                'special_instructions': f'Special instructions for plan {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
            
            session.execute(text("""
                INSERT INTO nutrition_plans (student_id, title, description, start_date, end_date,
                                           dietary_restrictions, calorie_target, macronutrient_targets,
                                           hydration_target, special_instructions, created_at, updated_at)
                VALUES (:student_id, :title, :description, :start_date, :end_date,
                        :dietary_restrictions, :calorie_target, :macronutrient_targets,
                        :hydration_target, :special_instructions, :created_at, :updated_at)
            """), plans_data)
            session.commit()
            print(f"  ✅ Seeded nutrition_plans table: {len(plans_data)} records")
        else:
            print(f"  ⚠️  Nutrition_plans table already has {plan_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding nutrition_plans: {e}")
    
    # 3. Seed meals table
    try:
        meal_count = session.execute(text("SELECT COUNT(*) FROM meals")).scalar()
        if meal_count == 0:
            meals_data = []
            for i in range(100):  # Create 100 meals
                meals_data.append({
                    'student_id': random.randint(1, 100),
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT']),
                    'name': f'Meal {i + 1}',
                    'description': f'Description for meal {i + 1}',
                    'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'time': datetime.now() - timedelta(hours=random.randint(1, 12)),
                    'total_calories': random.randint(200, 800),
                    'total_protein': round(random.uniform(10, 50), 2),
                    'total_carbohydrates': round(random.uniform(20, 80), 2),
                    'total_fats': round(random.uniform(5, 30), 2),
                    'total_fiber': round(random.uniform(2, 15), 2),
                    'total_sugar': round(random.uniform(5, 40), 2),
                    'total_sodium': round(random.uniform(100, 1000), 2),
                    'preparation_time': random.randint(10, 60),
                    'cooking_method': random.choice(['BAKED', 'FRIED', 'GRILLED', 'STEAMED', 'RAW']),
                    'serving_size': random.choice(['SMALL', 'MEDIUM', 'LARGE']),
                    'temperature': random.choice(['HOT', 'COLD', 'ROOM_TEMPERATURE']),
                    'was_consumed': random.choice([True, False]),
                    'consumption_notes': f'Consumption notes for meal {i + 1}',
                    'satisfaction_rating': random.randint(1, 5),
                    'hunger_level_before': random.randint(1, 10),
                    'hunger_level_after': random.randint(1, 10),
                    'additional_data': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO meals (student_id, meal_type, name, description, date, time, total_calories,
                                 total_protein, total_carbohydrates, total_fats, total_fiber, total_sugar, 
                                 total_sodium, preparation_time, cooking_method, serving_size, temperature,
                                 was_consumed, consumption_notes, satisfaction_rating, hunger_level_before,
                                 hunger_level_after, additional_data, created_at, updated_at)
                VALUES (:student_id, :meal_type, :name, :description, :date, :time, :total_calories,
                        :total_protein, :total_carbohydrates, :total_fats, :total_fiber, :total_sugar,
                        :total_sodium, :preparation_time, :cooking_method, :serving_size, :temperature,
                        :was_consumed, :consumption_notes, :satisfaction_rating, :hunger_level_before,
                        :hunger_level_after, :additional_data, :created_at, :updated_at)
            """), meals_data)
            session.commit()
            print(f"  ✅ Seeded meals table: {len(meals_data)} records")
        else:
            print(f"  ⚠️  Meals table already has {meal_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding meals: {e}")
    
    # 4. Seed student_health table
    try:
        health_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        if health_count == 0:
            health_data = []
            for i in range(100):  # Create 100 student health records
                health_data.append({
                    'student_id': random.choice(student_ids) if student_ids else random.randint(1, 100),
                    'first_name': f'Student{i + 1}',
                    'last_name': f'Health{i + 1}',
                    'date_of_birth': datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                    'gender': random.choice(['MALE', 'FEMALE', 'OTHER']),
                    'grade_level': random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'SIXTH', 'SEVENTH', 'EIGHTH', 'NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']),
                    'student_metadata': json.dumps({"student_id": i + 1, "health_score": random.randint(1, 100)}),
                    'health_status': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR']),
                    'health_notes': f'Health notes for student {i + 1}',
                    'health_metadata': json.dumps({"bmi": round(random.uniform(15.0, 35.0), 2), "fitness_level": random.choice(['LOW', 'MEDIUM', 'HIGH'])}),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(1, 7),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO student_health (student_id, first_name, last_name, date_of_birth, gender,
                                          grade_level, student_metadata, health_status, health_notes,
                                          health_metadata, last_accessed_at, archived_at, deleted_at,
                                          scheduled_deletion_at, retention_period, created_at, updated_at)
                VALUES (:student_id, :first_name, :last_name, :date_of_birth, :gender,
                        :grade_level, :student_metadata, :health_status, :health_notes,
                        :health_metadata, :last_accessed_at, :archived_at, :deleted_at,
                        :scheduled_deletion_at, :retention_period, :created_at, :updated_at)
            """), health_data)
            session.commit()
            print(f"  ✅ Seeded student_health table: {len(health_data)} records")
        else:
            print(f"  ⚠️  Student_health table already has {health_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding student_health: {e}")
    
    # 5. Seed fitness_goals table
    try:
        # Check if table exists first
        table_exists = session.execute(text("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'fitness_goals')")).scalar()
        if not table_exists:
            # Skip silently - table doesn't exist
            pass
        else:
            fitness_goal_count = session.execute(text("SELECT COUNT(*) FROM fitness_goals")).scalar()
            if fitness_goal_count == 0:
                fitness_goals_data = []
                for i in range(200):  # Create 200 fitness goals
                    fitness_goals_data.append({
                        'student_id': random.choice(student_ids) if student_ids else random.randint(1, 100),
                        'goal_type': random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']),
                        'description': f'Fitness goal {i + 1}',
                        'target_value': round(random.uniform(1, 100), 2),
                        'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                        'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
                        'priority': random.randint(1, 10)
                    })
                
                session.execute(text("""
                    INSERT INTO fitness_goals (student_id, goal_type, description, target_value, target_date, status, priority)
                    VALUES (:student_id, :goal_type, :description, :target_value, :target_date, :status, :priority)
                """), fitness_goals_data)
                session.commit()
                print(f"  ✅ Seeded fitness_goals table: {len(fitness_goals_data)} records")
            else:
                print(f"  ⚠️  Fitness_goals table already has {fitness_goal_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding fitness_goals: {e}")
    
    # 6. Seed student_health_fitness_goals table
    try:
        shf_goal_count = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals")).scalar()
        if shf_goal_count == 0:
            # Get student_health IDs for foreign key references
            try:
                student_health_result = session.execute(text("SELECT id FROM student_health"))
                student_health_ids = [row[0] for row in student_health_result.fetchall()]
                print(f"  📊 Found {len(student_health_ids)} student_health records for foreign key references")
            except Exception as e:
                print(f"  ⚠️  Could not get student_health IDs: {e}")
                student_health_ids = list(range(1, 101))  # Fallback range
            
            shf_goals_data = []
            for i in range(200):  # Create 200 student health fitness goals
                shf_goals_data.append({
                    'student_id': random.choice(student_health_ids) if student_health_ids else random.randint(1, 100),
                    'goal_type': random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']),
                    'category': random.choice(['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION', 'SPEED', 'AGILITY', 'POWER', 'SPORTS_SPECIFIC', 'GENERAL_FITNESS', 'WEIGHT_MANAGEMENT']),
                    'timeframe': random.choice(['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'ACADEMIC_YEAR', 'CUSTOM']),
                    'description': f'Student health fitness goal description {i + 1}',
                    'target_value': round(random.uniform(1.0, 100.0), 2),
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'completion_date': datetime.now() + timedelta(days=random.randint(30, 365)) if random.random() < 0.3 else None,
                    'status': random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD']),
                    'priority': random.randint(1, 1000),
                    'notes': f'Notes for student health fitness goal {i + 1}',
                    'goal_metadata': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO student_health_fitness_goals (student_id, goal_type, category, timeframe, description, target_value, 
                                                        target_date, completion_date, status, priority, notes, goal_metadata, 
                                                        created_at, updated_at)
                VALUES (:student_id, :goal_type, :category, :timeframe, :description, :target_value, 
                        :target_date, :completion_date, :status, :priority, :notes, :goal_metadata, 
                        :created_at, :updated_at)
            """), shf_goals_data)
            session.commit()
            print(f"  ✅ Seeded student_health_fitness_goals table: {len(shf_goals_data)} records")
        else:
            print(f"  ⚠️  Student_health_fitness_goals table already has {shf_goal_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding student_health_fitness_goals: {e}")
    
    # 7. Seed physical_education_nutrition_plans table
    try:
        pe_nutrition_plan_count = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_plans")).scalar()
        if pe_nutrition_plan_count == 0:
            pe_nutrition_plans_data = []
            for i in range(50):  # Create 50 physical education nutrition plans
                pe_nutrition_plans_data.append({
                    'student_id': random.choice(student_ids),
                    'plan_name': f'PE Nutrition Plan {i + 1}',
                    'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'end_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                    'plan_notes': f'Notes for PE nutrition plan {i + 1}',
                    'daily_calories': random.randint(1500, 3000),
                    'protein_goal': round(random.uniform(50, 150), 2),
                    'carbs_goal': round(random.uniform(100, 300), 2),
                    'fat_goal': round(random.uniform(30, 100), 2),
                    'plan_metadata': json.dumps({"plan_type": "PE", "difficulty": random.choice(["BEGINNER", "INTERMEDIATE", "ADVANCED"])}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO physical_education_nutrition_plans (student_id, plan_name, start_date, end_date, plan_notes, daily_calories, protein_goal, 
                                                              carbs_goal, fat_goal, plan_metadata, created_at, updated_at)
                VALUES (:student_id, :plan_name, :start_date, :end_date, :plan_notes, :daily_calories, :protein_goal, 
                        :carbs_goal, :fat_goal, :plan_metadata, :created_at, :updated_at)
            """), pe_nutrition_plans_data)
            session.commit()
            print(f"  ✅ Seeded physical_education_nutrition_plans table: {len(pe_nutrition_plans_data)} records")
        else:
            print(f"  ⚠️  Physical_education_nutrition_plans table already has {pe_nutrition_plan_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding physical_education_nutrition_plans: {e}")
    
    # Create and seed fitness_health_metrics table
    try:
        # Create fitness_health_metrics table if it doesn't exist
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS fitness_health_metrics (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                metric_type VARCHAR(100) NOT NULL,
                value DECIMAL(10,2),
                unit VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                metric_metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        session.commit()
        print("  ✅ Created fitness_health_metrics table")
        
        # Check if fitness_health_metrics table has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_health_metrics"))
        fitness_count = result.scalar()
        
        if fitness_count == 0:
            # Generate fitness_health_metrics data
            fitness_data = []
            for i in range(50):  # Create 50 fitness health metrics (includes ID 11)
                fitness_data.append({
                    'student_id': random.randint(1, 100),
                    'metric_type': random.choice(['HEART_RATE', 'BLOOD_PRESSURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'MUSCLE_MASS', 'FLEXIBILITY', 'STRENGTH', 'ENDURANCE']),
                    'value': round(random.uniform(50.0, 200.0), 2),
                    'unit': random.choice(['bpm', 'mmHg', 'kg', 'cm', '%', 'seconds', 'reps']),
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'notes': f'Fitness health metric {i + 1}',
                    'metric_metadata': json.dumps({"metric_id": i + 1, "difficulty": random.choice(['EASY', 'MEDIUM', 'HARD'])}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO fitness_health_metrics (student_id, metric_type, value, unit, timestamp, notes, metric_metadata, created_at, updated_at)
                VALUES (:student_id, :metric_type, :value, :unit, :timestamp, :notes, :metric_metadata, :created_at, :updated_at)
            """), fitness_data)
            session.commit()
            print(f"  ✅ Seeded fitness_health_metrics table: {len(fitness_data)} records")
        else:
            print(f"  ⚠️  Fitness_health_metrics table already has {fitness_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding fitness_health_metrics: {e}")
    
    # Create and seed progress table
    try:
        # Create progress table if it doesn't exist
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS progress (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                tracking_period VARCHAR(255),
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                progress_metrics JSON,
                baseline_data JSON,
                current_data JSON,
                improvement_rate DECIMAL(10,2),
                fitness_metrics JSON,
                skill_assessments JSON,
                attendance_record JSON,
                goals_progress JSON,
                challenges_faced JSON,
                support_provided JSON,
                next_evaluation_date TIMESTAMP,
                is_on_track BOOLEAN,
                strength_score DECIMAL(10,2),
                endurance_score DECIMAL(10,2),
                flexibility_score DECIMAL(10,2),
                coordination_score DECIMAL(10,2),
                created_by VARCHAR(255),
                updated_by VARCHAR(255),
                audit_trail JSON,
                last_audit_at TIMESTAMP,
                audit_status VARCHAR(50),
                is_valid BOOLEAN,
                validation_errors JSON,
                last_validated_at TIMESTAMP,
                validation_score DECIMAL(10,2),
                validation_history JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed_at TIMESTAMP,
                archived_at TIMESTAMP,
                deleted_at TIMESTAMP,
                scheduled_deletion_at TIMESTAMP,
                retention_period INTEGER,
                metadata JSON,
                status VARCHAR(50),
                is_active BOOLEAN
            )
        """))
        session.commit()
        print("  ✅ Created progress table")
        
        # Check if progress table has data
        result = session.execute(text("SELECT COUNT(*) FROM progress"))
        progress_count = result.scalar()
        
        if progress_count == 0:
            # Generate progress data
            progress_data = []
            for i in range(100):  # Create 100 progress records (includes ID 38)
                progress_data.append({
                    'student_id': random.randint(1, 100),  # Match student_health range
                    'tracking_period': f"Period {i+1}",
                    'start_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                    'end_date': datetime.now() - timedelta(days=random.randint(1, 29)),
                    'progress_metrics': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'baseline_data': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'current_data': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'improvement_rate': round(random.uniform(0.1, 2.0), 2),
                    'fitness_metrics': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'skill_assessments': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'attendance_record': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'goals_progress': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'challenges_faced': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'support_provided': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'next_evaluation_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                    'is_on_track': random.choice([True, False]),
                    'strength_score': round(random.uniform(1.0, 10.0), 2),
                    'endurance_score': round(random.uniform(1.0, 10.0), 2),
                    'flexibility_score': round(random.uniform(1.0, 10.0), 2),
                    'coordination_score': round(random.uniform(1.0, 10.0), 2),
                    'created_by': f"User {i+1}",
                    'updated_by': f"User {i+1}",
                    'audit_trail': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'last_audit_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'audit_status': random.choice(['active', 'inactive', 'pending', 'completed']),
                    'is_valid': random.choice([True, False]),
                    'validation_errors': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'last_validated_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'validation_score': round(random.uniform(1.0, 100.0), 2),
                    'validation_history': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'archived_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                    'deleted_at': datetime.now() - timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                    'scheduled_deletion_at': datetime.now() + timedelta(days=random.randint(30, 90)) if random.choice([True, False]) else None,
                    'retention_period': random.randint(30, 365),
                    'metadata': json.dumps({"key": f"value_{i}", "data": random.randint(1, 100)}),
                    'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED']),
                    'is_active': random.choice([True, False])
                })
            
            session.execute(text("""
                INSERT INTO progress (student_id, tracking_period, start_date, end_date, progress_metrics, 
                                   baseline_data, current_data, improvement_rate, fitness_metrics, skill_assessments,
                                   attendance_record, goals_progress, challenges_faced, support_provided, 
                                   next_evaluation_date, is_on_track, strength_score, endurance_score, 
                                   flexibility_score, coordination_score, created_by, updated_by, audit_trail,
                                   last_audit_at, audit_status, is_valid, validation_errors, last_validated_at,
                                   validation_score, validation_history, created_at, updated_at, last_accessed_at,
                                   archived_at, deleted_at, scheduled_deletion_at, retention_period, metadata,
                                   status, is_active)
                VALUES (:student_id, :tracking_period, :start_date, :end_date, :progress_metrics,
                        :baseline_data, :current_data, :improvement_rate, :fitness_metrics, :skill_assessments,
                        :attendance_record, :goals_progress, :challenges_faced, :support_provided,
                        :next_evaluation_date, :is_on_track, :strength_score, :endurance_score,
                        :flexibility_score, :coordination_score, :created_by, :updated_by, :audit_trail,
                        :last_audit_at, :audit_status, :is_valid, :validation_errors, :last_validated_at,
                        :validation_score, :validation_history, :created_at, :updated_at, :last_accessed_at,
                        :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period, :metadata,
                        :status, :is_active)
            """), progress_data)
            session.commit()
            print(f"  ✅ Seeded progress table: {len(progress_data)} records")
        else:
            print(f"  ⚠️  Progress table already has {progress_count} records")
    except Exception as e:
        print(f"  ❌ Error seeding progress: {e}")
    
    print("  ✅ Phase 3 dependency tables seeding completed!")


def seed_progress_table(session):
    """
    Seed just the progress table - used for re-seeding after it gets cleared.
    """
    try:
        # Check if table already has data
        result = session.execute(text("SELECT COUNT(*) FROM progress"))
        count = result.scalar()
        
        if count > 0:
            print(f"  ℹ️  progress table already has {count} records")
            return count
        
        # Generate progress data matching the actual schema
        progress_data = []
        for i in range(100):
            progress_data.append({
                'student_id': random.randint(1, 100),
                'tracking_period': f'Period {i + 1}',
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'progress_metrics': json.dumps({"score": random.randint(1, 100), "time": random.randint(30, 300)}),
                'baseline_data': json.dumps({"baseline_score": random.randint(1, 50)}),
                'current_data': json.dumps({"current_score": random.randint(51, 100)}),
                'improvement_rate': round(random.uniform(0.1, 2.0), 2),
                'fitness_metrics': json.dumps({"strength": random.randint(1, 100), "endurance": random.randint(1, 100)}),
                'skill_assessments': json.dumps({"assessment": f"Assessment {i + 1}"}),
                'attendance_record': json.dumps({"attendance": random.randint(80, 100)}),
                'goals_progress': json.dumps({"goal_progress": random.randint(1, 100)}),
                'challenges_faced': json.dumps({"challenges": f"Challenge {i + 1}"}),
                'support_provided': json.dumps({"support": f"Support {i + 1}"}),
                'next_evaluation_date': datetime.now() + timedelta(days=random.randint(7, 30)),
                'is_on_track': random.choice([True, False]),
                'strength_score': round(random.uniform(1.0, 10.0), 2),
                'endurance_score': round(random.uniform(1.0, 10.0), 2),
                'flexibility_score': round(random.uniform(1.0, 10.0), 2),
                'coordination_score': round(random.uniform(1.0, 10.0), 2),
                'created_by': f'User {random.randint(1, 10)}',
                'updated_by': f'User {random.randint(1, 10)}',
                'audit_trail': json.dumps({"audit": f"Audit {i + 1}"}),
                'last_audit_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'audit_status': random.choice(['completed', 'pending', 'in_progress']),
                'is_valid': random.choice([True, False]),
                'validation_errors': json.dumps({"errors": []}),
                'last_validated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'validation_score': round(random.uniform(0.0, 100.0), 2),
                'validation_history': json.dumps({"history": f"History {i + 1}"}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'archived_at': None if random.choice([True, False]) else datetime.now() - timedelta(days=random.randint(1, 7)),
                'deleted_at': None if random.choice([True, False]) else datetime.now() - timedelta(days=random.randint(1, 7)),
                'scheduled_deletion_at': None if random.choice([True, False]) else datetime.now() + timedelta(days=random.randint(30, 365)),
                'retention_period': random.randint(30, 365),
                'metadata': json.dumps({"metadata": f"Metadata {i + 1}"}),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED']),
                'is_active': random.choice([True, False])
            })
        
        # Insert progress data using the correct schema
        session.execute(text("""
            INSERT INTO progress (student_id, tracking_period, start_date, end_date, progress_metrics,
                                baseline_data, current_data, improvement_rate, fitness_metrics, skill_assessments,
                                attendance_record, goals_progress, challenges_faced, support_provided,
                                next_evaluation_date, is_on_track, strength_score, endurance_score, flexibility_score,
                                coordination_score, created_by, updated_by, audit_trail, last_audit_at, audit_status,
                                is_valid, validation_errors, last_validated_at, validation_score, validation_history,
                                created_at, updated_at, last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                retention_period, metadata, status, is_active)
            VALUES (:student_id, :tracking_period, :start_date, :end_date, :progress_metrics,
                    :baseline_data, :current_data, :improvement_rate, :fitness_metrics, :skill_assessments,
                    :attendance_record, :goals_progress, :challenges_faced, :support_provided,
                    :next_evaluation_date, :is_on_track, :strength_score, :endurance_score, :flexibility_score,
                    :coordination_score, :created_by, :updated_by, :audit_trail, :last_audit_at, :audit_status,
                    :is_valid, :validation_errors, :last_validated_at, :validation_score, :validation_history,
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                    :retention_period, :metadata, :status, :is_active)
        """), progress_data)
        
        print(f"  ✅ Seeded progress table with {len(progress_data)} records")
        return len(progress_data)
        
    except Exception as e:
        print(f"  ❌ Error seeding progress table: {e}")
        raise


def seed_additional_phase3_dependencies(session):
    """
    Seed additional Phase 3 dependency tables that need to be seeded early in the main script.
    This includes health_fitness_goals, physical_education_nutrition_plans, physical_education_meals.
    """
    try:
        # Seed health_fitness_goals table
        print("  Seeding health_fitness_goals...")
        
        # Check if already seeded
        result = session.execute(text("SELECT COUNT(*) FROM health_fitness_goals"))
        count = result.scalar()
        
        if count == 0:
            health_fitness_goals_data = []
            for i in range(100):
                health_fitness_goals_data.append({
                    'student_id': random.randint(1, 100),
                    'goal_type': random.choice(['STRENGTH', 'ENDURANCE', 'FLEXIBILITY', 'COORDINATION']),
                    'description': f'Health fitness goal {i + 1}',
                    'target_value': round(random.uniform(50.0, 100.0), 2),
                    'current_value': round(random.uniform(10.0, 80.0), 2),
                    'unit': random.choice(['reps', 'minutes', 'seconds', 'score']),
                    'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                    'status': random.choice(['ACTIVE', 'COMPLETED', 'PAUSED']),
                    'progress': round(random.uniform(0.0, 100.0), 2),
                    'is_achieved': random.choice([True, False]),
                    'goal_data': json.dumps({"goal_id": i + 1, "difficulty": random.choice(['EASY', 'MEDIUM', 'HARD'])}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO health_fitness_goals (student_id, goal_type, description, target_value,
                                                current_value, unit, start_date, target_date, status, 
                                                progress, is_achieved, goal_data, created_at, updated_at)
                VALUES (:student_id, :goal_type, :description, :target_value, :current_value, :unit,
                        :start_date, :target_date, :status, :progress, :is_achieved, :goal_data, 
                        :created_at, :updated_at)
            """), health_fitness_goals_data)
            print(f"    ✅ Seeded health_fitness_goals: {len(health_fitness_goals_data)} records")
        else:
            print(f"    ℹ️  health_fitness_goals already has {count} records")
        
        # Seed physical_education_nutrition_plans table
        print("  Seeding physical_education_nutrition_plans...")
        
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_plans"))
        count = result.scalar()
        
        if count == 0:
            nutrition_plans_data = []
            for i in range(50):
                nutrition_plans_data.append({
                    'student_id': random.randint(1, 100),
                    'plan_name': f'PE Nutrition Plan {i + 1}',
                    'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'end_date': datetime.now() + timedelta(days=random.randint(30, 90)),
                    'daily_calories': random.randint(1500, 3000),
                    'protein_goal': round(random.uniform(50.0, 150.0), 2),
                    'carbs_goal': round(random.uniform(100.0, 300.0), 2),
                    'fat_goal': round(random.uniform(30.0, 100.0), 2),
                    'plan_notes': f'Plan notes for PE nutrition plan {i + 1}',
                    'plan_metadata': json.dumps({"plan_id": i + 1, "difficulty": random.choice(['EASY', 'MEDIUM', 'HARD'])}),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(1, 7),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO physical_education_nutrition_plans (student_id, plan_name, start_date, end_date,
                                                              daily_calories, protein_goal, carbs_goal, fat_goal,
                                                              plan_notes, plan_metadata, last_accessed_at, archived_at,
                                                              deleted_at, scheduled_deletion_at, retention_period,
                                                              created_at, updated_at)
                VALUES (:student_id, :plan_name, :start_date, :end_date, :daily_calories, :protein_goal,
                        :carbs_goal, :fat_goal, :plan_notes, :plan_metadata, :last_accessed_at, :archived_at,
                        :deleted_at, :scheduled_deletion_at, :retention_period, :created_at, :updated_at)
            """), nutrition_plans_data)
            print(f"    ✅ Seeded physical_education_nutrition_plans: {len(nutrition_plans_data)} records")
        else:
            print(f"    ℹ️  physical_education_nutrition_plans already has {count} records")
        
        # Seed physical_education_meals table
        print("  Seeding physical_education_meals...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS physical_education_meals (
                id SERIAL PRIMARY KEY,
                nutrition_plan_id INTEGER NOT NULL,
                meal_type VARCHAR(50) NOT NULL,
                meal_time TIMESTAMP,
                calories INTEGER,
                protein DECIMAL(5,2),
                carbs DECIMAL(5,2),
                fat DECIMAL(5,2),
                meal_notes TEXT,
                meal_metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_meals"))
        count = result.scalar()
        
        if count == 0:
            meals_data = []
            for i in range(100):
                meals_data.append({
                    'nutrition_plan_id': random.randint(1, 50),  # Reference physical_education_nutrition_plans
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                    'meal_time': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'calories': random.randint(200, 800),
                    'protein': round(random.uniform(10.0, 50.0), 2),
                    'carbs': round(random.uniform(20.0, 80.0), 2),
                    'fat': round(random.uniform(5.0, 30.0), 2),
                    'meal_notes': f'Meal notes for record {i + 1}',
                    'meal_metadata': json.dumps({"meal_id": i + 1, "nutrition_score": random.randint(1, 100)}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            session.execute(text("""
                INSERT INTO physical_education_meals (nutrition_plan_id, meal_type, meal_time, calories,
                                                    protein, carbs, fat, meal_notes, meal_metadata, created_at, updated_at)
                VALUES (:nutrition_plan_id, :meal_type, :meal_time, :calories, :protein, :carbs, :fat,
                        :meal_notes, :meal_metadata, :created_at, :updated_at)
            """), meals_data)
            print(f"    ✅ Seeded physical_education_meals: {len(meals_data)} records")
        else:
            print(f"    ℹ️  physical_education_meals already has {count} records")
        
        print("  ✅ Additional Phase 3 dependency tables seeded successfully!")
        
    except Exception as e:
        print(f"  ❌ Error seeding additional Phase 3 dependencies: {e}")
        raise
