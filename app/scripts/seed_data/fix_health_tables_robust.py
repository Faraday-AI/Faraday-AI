#!/usr/bin/env python3
"""
Fix Health Tables - Robust Version for Main Script Integration
This script is designed to work reliably when called from the main seeding script
Uses deterministic approaches that work regardless of data recreation
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

def get_nutrition_plan_ids(session: Session) -> list:
    """Get all nutrition plan IDs, create if needed"""
    result = session.execute(text("SELECT id FROM physical_education_nutrition_plans ORDER BY id"))
    nutrition_plan_ids = [row[0] for row in result.fetchall()]
    
    if not nutrition_plan_ids:
        print("  📝 Creating physical_education_nutrition_plans...")
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
        result = session.execute(text("SELECT id FROM physical_education_nutrition_plans ORDER BY id"))
        nutrition_plan_ids = [row[0] for row in result.fetchall()]
    
    return nutrition_plan_ids

def fix_fitness_assessments(session: Session, student_health_ids: list, student_count: int):
    """Fix fitness_assessments - use only students with health records"""
    print("🔧 FIXING fitness_assessments...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} fitness_assessments records...")
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping fitness_assessments")
            return
        
        # Create one fitness assessment per student with health record
        batch_records = []
        for i, student_id in enumerate(student_health_ids[:needed]):
            fitness_assessment = {
                'student_id': student_id,
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
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping student_health_fitness_goals")
            return
        
        # Create one fitness goal per student with health record
        batch_records = []
        for i, student_id in enumerate(student_health_ids[:needed]):
            student_hf_goal = {
                'student_id': student_id,
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
    """Fix health_alerts - 1 per 10 students using only students with health records"""
    print("🔧 FIXING health_alerts...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_alerts")).scalar()
    target_count = student_count // 10  # 1 alert per 10 students
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} health_alerts records...")
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping health_alerts")
            return
        
        # Create alerts using actual student_health IDs
        batch_records = []
        for i in range(needed):
            student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
            health_alert = {
                'student_id': student_id,
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

def fix_physical_education_nutrition_logs(session: Session, student_health_ids: list, student_count: int):
    """Fix physical_education_nutrition_logs - 3 per student using only students with health records"""
    print("🔧 FIXING physical_education_nutrition_logs...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_logs")).scalar()
    target_count = student_count * 3
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} physical_education_nutrition_logs records...")
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping physical_education_nutrition_logs")
            return
        
        batch_records = []
        for i in range(needed):
            student_id = student_health_ids[i % len(student_health_ids)]  # Cycle through available IDs
            pe_nutrition_log = {
                'student_id': student_id,
                'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                'log_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'calories': random.randint(200, 800),
                'protein': round(random.uniform(10, 50), 2),
                'carbohydrates': round(random.uniform(20, 100), 2),
                'fats': round(random.uniform(5, 30), 2),
                'hydration': round(random.uniform(200, 1000), 2),
                'notes': f'PE nutrition log notes for student {student_id}',
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
            print(f"  ✅ Added {len(batch_records)} physical_education_nutrition_logs records")
        except Exception as e:
            print(f"  ❌ Error adding physical_education_nutrition_logs: {e}")
            session.rollback()
    else:
        print(f"  ✅ physical_education_nutrition_logs already has {current_count} records")

def fix_meals(session: Session, student_health_ids: list, student_count: int):
    """Fix meals using only students with health records"""
    print("🔧 FIXING meals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM meals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} meals records...")
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping meals")
            return
        
        batch_records = []
        for i, student_id in enumerate(student_health_ids[:needed]):
            meal = {
                'student_id': student_id,
                'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT', 'RECOVERY']),
                'name': f'Meal for student {student_id}',
                'description': f'Meal description for student {student_id}',
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
                'consumption_notes': f'Consumption notes for student {student_id}',
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
            print(f"  ✅ Added {len(batch_records)} meals records")
        except Exception as e:
            print(f"  ❌ Error adding meals: {e}")
            session.rollback()
    else:
        print(f"  ✅ meals already has {current_count} records")

def fix_meal_plans(session: Session, nutrition_plan_ids: list, student_count: int):
    """Fix meal_plans using nutrition plan IDs"""
    print("🔧 FIXING meal_plans...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM meal_plans")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} meal_plans records...")
        
        if not nutrition_plan_ids:
            print("  ❌ No nutrition plans found, skipping meal_plans")
            return
        
        batch_records = []
        for i in range(needed):
            nutrition_plan_id = nutrition_plan_ids[i % len(nutrition_plan_ids)]  # Cycle through available IDs
            meal_plan = {
                'nutrition_plan_id': nutrition_plan_id,
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
            print(f"  ✅ Added {len(batch_records)} meal_plans records")
        except Exception as e:
            print(f"  ❌ Error adding meal_plans: {e}")
            session.rollback()
    else:
        print(f"  ✅ meal_plans already has {current_count} records")

def fix_nutrition_goals(session: Session, nutrition_plan_ids: list, student_count: int):
    """Fix nutrition_goals - 3 per student using nutrition plan IDs"""
    print("🔧 FIXING nutrition_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM nutrition_goals")).scalar()
    target_count = student_count * 3
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} nutrition_goals records...")
        
        if not nutrition_plan_ids:
            print("  ❌ No nutrition plans found, skipping nutrition_goals")
            return
        
        batch_records = []
        for i in range(needed):
            nutrition_plan_id = nutrition_plan_ids[i % len(nutrition_plan_ids)]  # Cycle through available IDs
            nutrition_goal = {
                'nutrition_plan_id': nutrition_plan_id,
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
            print(f"  ✅ Added {len(batch_records)} nutrition_goals records")
        except Exception as e:
            print(f"  ❌ Error adding nutrition_goals: {e}")
            session.rollback()
    else:
        print(f"  ✅ nutrition_goals already has {current_count} records")

def fix_fitness_goals(session: Session, student_health_ids: list, student_count: int):
    """Fix fitness_goals using only students with health records"""
    print("🔧 FIXING fitness_goals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_goals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} fitness_goals records...")
        
        if not student_health_ids:
            print("  ❌ No students with health records found, skipping fitness_goals")
            return
        
        batch_records = []
        for i, student_id in enumerate(student_health_ids[:needed]):
            fitness_goal = {
                'student_id': student_id,
                'goal_type': random.choice(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'Cardio']),
                'description': f'Fitness goal description for student {student_id}',
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
            print(f"  ✅ Added {len(batch_records)} fitness_goals records")
        except Exception as e:
            print(f"  ❌ Error adding fitness_goals: {e}")
            session.rollback()
    else:
        print(f"  ✅ fitness_goals already has {current_count} records")

def main():
    """Main function to fix all health tables robustly"""
    print("="*70)
    print("🔧 FIXING HEALTH TABLES - ROBUST VERSION FOR MAIN SCRIPT")
    print("="*70)
    print("📊 Fixing all health, nutrition, and medical tables")
    print("🎯 Using deterministic approaches that work on data recreation")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_health_ids = get_student_health_ids(session)
        nutrition_plan_ids = get_nutrition_plan_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Students with health records: {len(student_health_ids):,}")
        print(f"📊 Nutrition plans available: {len(nutrition_plan_ids):,}")
        
        if not student_health_ids:
            print("❌ No students with health records found, cannot proceed with scaling")
            return
        
        # Fix each table individually
        fix_fitness_assessments(session, student_health_ids, student_count)
        fix_student_health_fitness_goals(session, student_health_ids, student_count)
        fix_health_alerts(session, student_health_ids, student_count)
        fix_physical_education_nutrition_logs(session, student_health_ids, student_count)
        fix_meals(session, student_health_ids, student_count)
        fix_meal_plans(session, nutrition_plan_ids, student_count)
        fix_nutrition_goals(session, nutrition_plan_ids, student_count)
        fix_fitness_goals(session, student_health_ids, student_count)
        
        print("\n🎉 All health table fixes completed robustly!")
        
    except Exception as e:
        print(f"❌ Error during fixing: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
