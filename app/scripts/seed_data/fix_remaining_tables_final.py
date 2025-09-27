#!/usr/bin/env python3
"""
Fix Remaining Tables - Final Corrected Version
Fix all remaining health, nutrition, and medical tables with correct column names and enum values
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

def get_student_ids(session: Session) -> list:
    """Get all student IDs from database"""
    result = session.execute(text("SELECT id FROM students ORDER BY id"))
    return [row[0] for row in result.fetchall()]

def get_student_health_ids(session: Session) -> list:
    """Get all student IDs that have health records"""
    result = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id"))
    return [row[0] for row in result.fetchall()]

def get_nutrition_plan_ids(session: Session) -> list:
    """Get all nutrition plan IDs"""
    result = session.execute(text("SELECT id FROM physical_education_nutrition_plans ORDER BY id"))
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
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                fitness_assessment = {
                    'student_id': random.choice(student_health_ids),
                    'assessment_type': random.choice(['Initial', 'Progress', 'Final', 'Quarterly', 'Annual']),
                    'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'score': round(random.uniform(60, 100), 2),
                    'assessment_notes': f'Assessment notes for student {i + 1}',
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
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of fitness_assessments")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ fitness_assessments already has {current_count} records")

def fix_physical_education_nutrition_logs(session: Session, student_ids: list, student_count: int):
    """Fix physical_education_nutrition_logs - 3 per student"""
    print("🔧 FIXING physical_education_nutrition_logs...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_logs")).scalar()
    target_count = student_count * 3
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} physical_education_nutrition_logs records...")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                pe_nutrition_log = {
                    'student_id': random.choice(student_ids),
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                    'log_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'calories': random.randint(200, 800),
                    'protein': round(random.uniform(10, 50), 2),
                    'carbohydrates': round(random.uniform(20, 100), 2),
                    'fats': round(random.uniform(5, 30), 2),
                    'hydration': round(random.uniform(200, 1000), 2),
                    'notes': f'PE nutrition log notes {i + 1}',
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
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of physical_education_nutrition_logs")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ physical_education_nutrition_logs already has {current_count} records")

def fix_student_health_fitness_goals(session: Session, student_ids: list, student_count: int):
    """Fix student_health_fitness_goals"""
    print("🔧 FIXING student_health_fitness_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} student_health_fitness_goals records...")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                student_hf_goal = {
                    'student_id': random.choice(student_ids),
                    'goal_type': random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']),
                    'category': random.choice(['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION', 'SPEED', 'AGILITY', 'POWER', 'SPORTS_SPECIFIC', 'GENERAL_FITNESS', 'WEIGHT_MANAGEMENT']),
                    'timeframe': random.choice(['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'ACADEMIC_YEAR', 'CUSTOM']),
                    'description': f'Fitness goal description for student {i + 1}',
                    'target_value': round(random.uniform(10, 100), 2),
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'completion_date': None,
                    'status': random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD']),
                    'priority': random.randint(1, 5),
                    'notes': f'Goal notes for student {i + 1}',
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
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of student_health_fitness_goals")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ student_health_fitness_goals already has {current_count} records")

def fix_health_conditions(session: Session, student_ids: list, student_count: int):
    """Fix health_conditions"""
    print("🔧 FIXING health_conditions...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_conditions")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} health_conditions records...")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                health_condition = {
                    'student_id': random.choice(student_ids),
                    'condition_name': random.choice(['Asthma', 'Allergies', 'ADHD', 'Diabetes', 'None', 'Other']),
                    'description': f'Health condition description for student {i + 1}',
                    'severity': random.choice(['Low', 'Medium', 'High']),
                    'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 365*3)),
                    'treatment': f'Treatment plan for condition {i + 1}',
                    'restrictions': f'Activity restrictions for condition {i + 1}',
                    'notes': f'Additional notes for condition {i + 1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                batch_records.append(health_condition)
            
            try:
                session.execute(text("""
                    INSERT INTO health_conditions (student_id, condition_name, description, severity, diagnosis_date, 
                                                 treatment, restrictions, notes, created_at, updated_at, 
                                                 last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
                    VALUES (:student_id, :condition_name, :description, :severity, :diagnosis_date, 
                           :treatment, :restrictions, :notes, :created_at, :updated_at, 
                           :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of health_conditions")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ health_conditions already has {current_count} records")

def fix_health_alerts(session: Session, student_ids: list, student_count: int):
    """Fix health_alerts - 1 per 10 students (realistic for alerts)"""
    print("🔧 FIXING health_alerts...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_alerts")).scalar()
    target_count = student_count // 10  # 1 alert per 10 students
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} health_alerts records...")
        
        batch_size = 500
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                health_alert = {
                    'student_id': random.choice(student_ids),
                    'condition_id': None,  # Can be null
                    'alert_type': random.choice(['RISK_THRESHOLD', 'EMERGENCY', 'PROTOCOL', 'MAINTENANCE', 'WEATHER']),
                    'message': f'Health alert message {i + 1}',
                    'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
                    'is_active': random.choice([True, False]),
                    'resolved_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                    'notes': f'Alert notes {i + 1}',
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
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of health_alerts")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ health_alerts already has {current_count} records")

def fix_meals(session: Session, student_ids: list, student_count: int):
    """Fix meals"""
    print("🔧 FIXING meals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM meals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} meals records...")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                meal = {
                    'student_id': random.choice(student_ids),
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT', 'RECOVERY']),
                    'name': f'Meal {i + 1}',
                    'description': f'Meal description {i + 1}',
                    'date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'time': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'total_calories': random.randint(300, 600),
                    'total_protein': round(random.uniform(10, 30), 2),
                    'total_carbohydrates': round(random.uniform(20, 60), 2),
                    'total_fats': round(random.uniform(5, 25), 2),
                    'total_fiber': round(random.uniform(5, 15), 2),
                    'total_sugar': round(random.uniform(5, 20), 2),
                    'total_sodium': round(random.uniform(100, 800), 2),
                    'preparation_time': random.randint(5, 60),
                    'cooking_method': random.choice(['Grilled', 'Baked', 'Fried', 'Steamed', 'Raw', 'Boiled']),
                    'serving_size': random.choice(['Small', 'Medium', 'Large', 'Extra Large']),
                    'temperature': random.choice(['Hot', 'Cold', 'Room Temperature']),
                    'was_consumed': random.choice([True, False]),
                    'consumption_notes': f'Consumption notes {i + 1}',
                    'satisfaction_rating': random.randint(1, 5),
                    'hunger_level_before': random.randint(1, 5),
                    'hunger_level_after': random.randint(1, 5),
                    'additional_data': json.dumps({'source': 'system', 'type': 'meal'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(meal)
            
            try:
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
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of meals")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ meals already has {current_count} records")

def fix_meal_plans(session: Session, nutrition_plan_ids: list, student_count: int):
    """Fix meal_plans"""
    print("🔧 FIXING meal_plans...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM meal_plans")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} meal_plans records...")
        
        if not nutrition_plan_ids:
            print("  ❌ No nutrition plans found, creating basic ones first...")
            # Create basic nutrition plans
            for i in range(10):
                session.execute(text("""
                    INSERT INTO physical_education_nutrition_plans (name, description, created_at, updated_at)
                    VALUES (:name, :description, :created_at, :updated_at)
                """), {
                    'name': f'PE Nutrition Plan {i+1}',
                    'description': f'Physical Education nutrition plan {i+1}',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            session.commit()
            nutrition_plan_ids = [i+1 for i in range(10)]
            print("  ✅ Created 10 physical_education_nutrition_plans")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                meal_plan = {
                    'nutrition_plan_id': random.choice(nutrition_plan_ids),
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT', 'RECOVERY']),
                    'name': f'Meal Plan {i + 1}',
                    'description': f'Meal plan description {i + 1}',
                    'serving_size': random.choice(['Small', 'Medium', 'Large']),
                    'calories': random.randint(300, 600),
                    'protein': round(random.uniform(10, 30), 2),
                    'carbohydrates': round(random.uniform(20, 60), 2),
                    'fats': round(random.uniform(5, 25), 2),
                    'preparation_time': random.randint(5, 60),
                    'ingredients': json.dumps(['Ingredient 1', 'Ingredient 2', 'Ingredient 3']),
                    'instructions': json.dumps(['Step 1', 'Step 2', 'Step 3']),
                    'alternatives': json.dumps(['Alternative 1', 'Alternative 2']),
                    'notes': f'Meal plan notes {i + 1}',
                    'additional_data': json.dumps({'source': 'system', 'type': 'meal_plan'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                }
                batch_records.append(meal_plan)
            
            try:
                session.execute(text("""
                    INSERT INTO meal_plans (nutrition_plan_id, meal_type, name, description, serving_size, calories, 
                                          protein, carbohydrates, fats, preparation_time, ingredients, instructions, 
                                          alternatives, notes, additional_data, created_at)
                    VALUES (:nutrition_plan_id, :meal_type, :name, :description, :serving_size, :calories, 
                           :protein, :carbohydrates, :fats, :preparation_time, :ingredients, :instructions, 
                           :alternatives, :notes, :additional_data, :created_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of meal_plans")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ meal_plans already has {current_count} records")

def fix_nutrition_goals(session: Session, nutrition_plan_ids: list, student_count: int):
    """Fix nutrition_goals - 3 per student"""
    print("🔧 FIXING nutrition_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM nutrition_goals")).scalar()
    target_count = student_count * 3
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} nutrition_goals records...")
        
        if not nutrition_plan_ids:
            print("  ❌ No nutrition plans found, creating basic ones first...")
            # Create basic nutrition plans
            for i in range(10):
                session.execute(text("""
                    INSERT INTO physical_education_nutrition_plans (name, description, created_at, updated_at)
                    VALUES (:name, :description, :created_at, :updated_at)
                """), {
                    'name': f'PE Nutrition Plan {i+1}',
                    'description': f'Physical Education nutrition plan {i+1}',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            session.commit()
            nutrition_plan_ids = [i+1 for i in range(10)]
            print("  ✅ Created 10 physical_education_nutrition_plans")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                nutrition_goal = {
                    'nutrition_plan_id': random.choice(nutrition_plan_ids),
                    'description': f'Nutrition goal description {i + 1}',
                    'target_value': round(random.uniform(50, 200), 2),
                    'current_value': round(random.uniform(10, 150), 2),
                    'unit': random.choice(['grams', 'calories', 'servings', 'cups', 'ounces']),
                    'deadline': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'progress': round(random.uniform(0, 100), 2),
                    'notes': f'Nutrition goal notes {i + 1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(nutrition_goal)
            
            try:
                session.execute(text("""
                    INSERT INTO nutrition_goals (nutrition_plan_id, description, target_value, current_value, 
                                              unit, deadline, progress, notes, created_at, updated_at)
                    VALUES (:nutrition_plan_id, :description, :target_value, :current_value, 
                           :unit, :deadline, :progress, :notes, :created_at, :updated_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of nutrition_goals")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ nutrition_goals already has {current_count} records")

def fix_fitness_goals(session: Session, student_ids: list, student_count: int):
    """Fix fitness_goals"""
    print("🔧 FIXING fitness_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_goals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} fitness_goals records...")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                fitness_goal = {
                    'student_id': random.choice(student_ids),
                    'goal_type': random.choice(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'Cardio']),
                    'description': f'Fitness goal description {i + 1}',
                    'target_value': round(random.uniform(10, 100), 2),
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'status': random.choice(['Not Started', 'In Progress', 'Completed', 'Abandoned', 'On Hold']),
                    'priority': random.randint(1, 5),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(fitness_goal)
            
            try:
                session.execute(text("""
                    INSERT INTO fitness_goals (student_id, goal_type, description, target_value, target_date, 
                                             status, priority, created_at, updated_at)
                    VALUES (:student_id, :goal_type, :description, :target_value, :target_date, 
                           :status, :priority, :created_at, :updated_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of fitness_goals")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ fitness_goals already has {current_count} records")

def main():
    """Main function to fix all remaining tables"""
    print("="*70)
    print("🔧 FIXING ALL REMAINING TABLES - FINAL CORRECTED VERSION")
    print("="*70)
    print("📊 Fixing 9 remaining health, nutrition, and medical tables")
    print("🎯 Target: 3,877 students across all tables")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_ids = get_student_ids(session)
        student_health_ids = get_student_health_ids(session)
        nutrition_plan_ids = get_nutrition_plan_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Student IDs available: {len(student_ids):,}")
        print(f"📊 Students with health records: {len(student_health_ids):,}")
        print(f"📊 Nutrition plans available: {len(nutrition_plan_ids):,}")
        
        if not student_ids:
            print("❌ No students found, cannot proceed with scaling")
            return
        
        # Fix each table individually
        fix_fitness_assessments(session, student_health_ids, student_count)
        fix_physical_education_nutrition_logs(session, student_ids, student_count)
        fix_student_health_fitness_goals(session, student_ids, student_count)
        fix_health_conditions(session, student_ids, student_count)
        fix_health_alerts(session, student_ids, student_count)
        fix_meals(session, student_ids, student_count)
        fix_meal_plans(session, nutrition_plan_ids, student_count)
        fix_nutrition_goals(session, nutrition_plan_ids, student_count)
        fix_fitness_goals(session, student_ids, student_count)
        
        print("\n🎉 All remaining table fixes completed!")
        
    except Exception as e:
        print(f"❌ Error during fixing: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
