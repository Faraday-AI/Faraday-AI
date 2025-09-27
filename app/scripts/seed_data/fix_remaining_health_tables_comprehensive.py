#!/usr/bin/env python3
"""
Fix Remaining Health Tables - Comprehensive Approach
Fix all remaining health, nutrition, and medical tables that need proper scaling
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

def get_user_ids(session: Session) -> list:
    """Get all user IDs from database"""
    result = session.execute(text("SELECT id FROM users ORDER BY id"))
    return [row[0] for row in result.fetchall()]

def get_student_health_ids(session: Session) -> list:
    """Get all student IDs that have health records"""
    result = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id"))
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
                    'student_id': random.choice(student_health_ids),  # Use only students with health records
                    'assessment_type': random.choice(['Initial', 'Progress', 'Final', 'Quarterly', 'Annual']),
                    'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'score': round(random.uniform(60, 100), 2),
                    'assessment_notes': f'Assessment notes for student {i + 1}',
                    'assessment_metadata': '{"source": "system", "type": "fitness"}',
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
                    'date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                    'foods_consumed': f'PE Food items for meal {i + 1}',
                    'calories': random.randint(200, 800),
                    'carbohydrates': random.randint(20, 100),
                    'fats': random.randint(5, 50),
                    'hydration': random.randint(200, 1000),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                }
                batch_records.append(pe_nutrition_log)
            
            try:
                session.execute(text("""
                    INSERT INTO physical_education_nutrition_logs (student_id, date, meal_type, foods_consumed, calories, carbohydrates, fats, hydration, created_at)
                    VALUES (:student_id, :date, :meal_type, :foods_consumed, :calories, :carbohydrates, :fats, :hydration, :created_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of physical_education_nutrition_logs")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ physical_education_nutrition_logs already has {current_count} records")

def fix_physical_education_meals(session: Session, student_count: int):
    """Fix physical_education_meals - create nutrition plans first if needed"""
    print("🔧 FIXING physical_education_meals...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM physical_education_meals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} physical_education_meals records...")
        
        # Check if we have nutrition plans
        nutrition_plan_count = session.execute(text("SELECT COUNT(*) FROM physical_education_nutrition_plans")).scalar()
        if nutrition_plan_count == 0:
            print("  📝 Creating physical_education_nutrition_plans first...")
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
            print("  ✅ Created 10 physical_education_nutrition_plans")
        
        # Get nutrition plan IDs
        nutrition_plan_ids = session.execute(text("SELECT id FROM physical_education_nutrition_plans")).fetchall()
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                pe_meal = {
                    'nutrition_plan_id': random.choice(nutrition_plan_ids)[0],
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                    'meal_time': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'calories': random.randint(300, 600),
                    'protein': round(random.uniform(10, 30), 2),
                    'carbs': round(random.uniform(20, 60), 2),
                    'fat': round(random.uniform(5, 25), 2),
                    'meal_notes': f'PE Meal {i + 1} - {random.choice(["BREAKFAST", "LUNCH", "DINNER", "SNACK"])}',
                    'meal_metadata': json.dumps({'source': 'system', 'type': 'pe_meal'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                batch_records.append(pe_meal)
            
            try:
                session.execute(text("""
                    INSERT INTO physical_education_meals (nutrition_plan_id, meal_type, meal_time, calories, protein, 
                                                        carbs, fat, meal_notes, meal_metadata, created_at, updated_at,
                                                        last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
                    VALUES (:nutrition_plan_id, :meal_type, :meal_time, :calories, :protein, 
                           :carbs, :fat, :meal_notes, :meal_metadata, :created_at, :updated_at,
                           :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of physical_education_meals")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ physical_education_meals already has {current_count} records")

def fix_health_fitness_health_checks(session: Session, student_ids: list, student_count: int):
    """Fix health_fitness_health_checks - fix enum values"""
    print("🔧 FIXING health_fitness_health_checks...")
    
    current_count = session.execute(text("SELECT COUNT(*) FROM health_fitness_health_checks")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} health_fitness_health_checks records...")
        
        batch_size = 1000
        for batch_start in range(0, needed, batch_size):
            batch_end = min(batch_start + batch_size, needed)
            batch_records = []
            
            for i in range(batch_start, batch_end):
                hf_health_check = {
                    'student_id': random.choice(student_ids),
                    'check_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY']),
                    'performed_by': f'Staff Member {random.randint(1, 50)}',
                    'findings': json.dumps({'status': 'normal', 'notes': f'Check findings {i + 1}'}),
                    'recommendations': f'Recommendations for check {i + 1}',
                    'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED']),  # Use correct enum values
                    'is_active': random.choice([True, False]),
                    'metadata': json.dumps({'source': 'system', 'type': 'health_fitness'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                batch_records.append(hf_health_check)
            
            try:
                session.execute(text("""
                    INSERT INTO health_fitness_health_checks (student_id, check_type, performed_by, findings, 
                                                            recommendations, status, is_active, metadata, created_at, updated_at,
                                                            last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
                    VALUES (:student_id, :check_type, :performed_by, :findings, 
                           :recommendations, :status, :is_active, :metadata, :created_at, :updated_at,
                           :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of health_fitness_health_checks")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ health_fitness_health_checks already has {current_count} records")

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
                    'goal_type': random.choice(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'Cardio']),
                    'target_value': random.randint(10, 100),
                    'current_value': random.randint(5, 95),
                    'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(student_hf_goal)
            
            try:
                session.execute(text("""
                    INSERT INTO student_health_fitness_goals (student_id, goal_type, target_value, current_value, target_date, created_at, updated_at)
                    VALUES (:student_id, :goal_type, :target_value, :current_value, :target_date, :created_at, :updated_at)
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
                    'condition_type': random.choice(['Chronic', 'Acute', 'Genetic', 'Environmental', 'None']),
                    'description': f'Health condition description for student {i + 1}',
                    'severity_level': random.choice(['Low', 'Medium', 'High']),
                    'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 365*3)),
                    'treatment_plan': f'Treatment plan for condition {i + 1}',
                    'is_ongoing': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                batch_records.append(health_condition)
            
            try:
                session.execute(text("""
                    INSERT INTO health_conditions (student_id, condition_type, description, severity_level, diagnosis_date, treatment_plan, is_ongoing, created_at, updated_at)
                    VALUES (:student_id, :condition_type, :description, :severity_level, :diagnosis_date, :treatment_plan, :is_ongoing, :created_at, :updated_at)
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
                    'alert_type': random.choice(['Allergy Alert', 'Medication Reminder', 'Health Check Due', 'Emergency Contact', 'Medical Appointment']),
                    'priority': random.choice(['Low', 'Medium', 'High', 'Critical']),
                    'message': f'Health alert message {i + 1}',
                    'alert_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'is_resolved': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now()
                }
                batch_records.append(health_alert)
            
            try:
                session.execute(text("""
                    INSERT INTO health_alerts (student_id, alert_type, priority, message, alert_date, is_resolved, created_at, updated_at)
                    VALUES (:student_id, :alert_type, :priority, :message, :alert_date, :is_resolved, :created_at, :updated_at)
                """), batch_records)
                session.commit()
                print(f"  ✅ Added batch {batch_start+1}-{batch_end} of health_alerts")
            except Exception as e:
                print(f"  ❌ Error in batch {batch_start+1}-{batch_end}: {e}")
                session.rollback()
    else:
        print(f"  ✅ health_alerts already has {current_count} records")

def fix_meals_and_plans(session: Session, student_count: int):
    """Fix meals, meal_plans, nutrition_goals, fitness_goals"""
    print("🔧 FIXING meals, meal_plans, nutrition_goals, fitness_goals...")
    
    # Fix meals
    current_count = session.execute(text("SELECT COUNT(*) FROM meals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} meals records...")
        
        batch_records = []
        for i in range(needed):
            meal = {
                'meal_name': f'Meal {i + 1}',
                'description': f'Meal description {i + 1}',
                'calories': random.randint(300, 600),
                'protein': round(random.uniform(10, 30), 2),
                'carbs': round(random.uniform(20, 60), 2),
                'fat': round(random.uniform(5, 25), 2),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            batch_records.append(meal)
        
        try:
            session.execute(text("""
                INSERT INTO meals (meal_name, description, calories, protein, carbs, fat, created_at, updated_at)
                VALUES (:meal_name, :description, :calories, :protein, :carbs, :fat, :created_at, :updated_at)
            """), batch_records)
            session.commit()
            print(f"  ✅ Added {needed} meals records")
        except Exception as e:
            print(f"  ❌ Error adding meals: {e}")
            session.rollback()
    else:
        print(f"  ✅ meals already has {current_count} records")
    
    # Fix meal_plans
    current_count = session.execute(text("SELECT COUNT(*) FROM meal_plans")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} meal_plans records...")
        
        batch_records = []
        for i in range(needed):
            meal_plan = {
                'plan_name': f'Meal Plan {i + 1}',
                'description': f'Meal plan description {i + 1}',
                'total_calories': random.randint(1500, 2500),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            batch_records.append(meal_plan)
        
        try:
            session.execute(text("""
                INSERT INTO meal_plans (plan_name, description, total_calories, created_at, updated_at)
                VALUES (:plan_name, :description, :total_calories, :created_at, :updated_at)
            """), batch_records)
            session.commit()
            print(f"  ✅ Added {needed} meal_plans records")
        except Exception as e:
            print(f"  ❌ Error adding meal_plans: {e}")
            session.rollback()
    else:
        print(f"  ✅ meal_plans already has {current_count} records")
    
    # Fix nutrition_goals
    current_count = session.execute(text("SELECT COUNT(*) FROM nutrition_goals")).scalar()
    target_count = student_count * 3
    if current_count < target_count:
        needed = target_count - current_count
        print(f"  📈 Adding {needed} nutrition_goals records...")
        
        batch_records = []
        for i in range(needed):
            nutrition_goal = {
                'goal_name': f'Nutrition Goal {i + 1}',
                'description': f'Nutrition goal description {i + 1}',
                'target_calories': random.randint(1500, 2500),
                'target_protein': round(random.uniform(50, 150), 2),
                'target_carbs': round(random.uniform(100, 300), 2),
                'target_fat': round(random.uniform(30, 100), 2),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            batch_records.append(nutrition_goal)
        
        try:
            session.execute(text("""
                INSERT INTO nutrition_goals (goal_name, description, target_calories, target_protein, target_carbs, target_fat, created_at, updated_at)
                VALUES (:goal_name, :description, :target_calories, :target_protein, :target_carbs, :target_fat, :created_at, :updated_at)
            """), batch_records)
            session.commit()
            print(f"  ✅ Added {needed} nutrition_goals records")
        except Exception as e:
            print(f"  ❌ Error adding nutrition_goals: {e}")
            session.rollback()
    else:
        print(f"  ✅ nutrition_goals already has {current_count} records")
    
    # Fix fitness_goals
    current_count = session.execute(text("SELECT COUNT(*) FROM fitness_goals")).scalar()
    if current_count < student_count:
        needed = student_count - current_count
        print(f"  📈 Adding {needed} fitness_goals records...")
        
        batch_records = []
        for i in range(needed):
            fitness_goal = {
                'goal_name': f'Fitness Goal {i + 1}',
                'description': f'Fitness goal description {i + 1}',
                'target_value': random.randint(10, 100),
                'current_value': random.randint(5, 95),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            batch_records.append(fitness_goal)
        
        try:
            session.execute(text("""
                INSERT INTO fitness_goals (goal_name, description, target_value, current_value, target_date, created_at, updated_at)
                VALUES (:goal_name, :description, :target_value, :current_value, :target_date, :created_at, :updated_at)
            """), batch_records)
            session.commit()
            print(f"  ✅ Added {needed} fitness_goals records")
        except Exception as e:
            print(f"  ❌ Error adding fitness_goals: {e}")
            session.rollback()
    else:
        print(f"  ✅ fitness_goals already has {current_count} records")

def main():
    """Main function to fix all remaining health tables"""
    print("="*70)
    print("🔧 FIXING ALL REMAINING HEALTH, NUTRITION & MEDICAL TABLES")
    print("="*70)
    print("📊 Comprehensive fix for all remaining health tables")
    print("🎯 Target: 3,877 students across all health tables")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_ids = get_student_ids(session)
        student_health_ids = get_student_health_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Student IDs available: {len(student_ids):,}")
        print(f"📊 Students with health records: {len(student_health_ids):,}")
        
        if not student_ids:
            print("❌ No students found, cannot proceed with scaling")
            return
        
        # Fix each table individually
        fix_fitness_assessments(session, student_health_ids, student_count)
        fix_physical_education_nutrition_logs(session, student_ids, student_count)
        fix_physical_education_meals(session, student_count)
        fix_health_fitness_health_checks(session, student_ids, student_count)
        fix_student_health_fitness_goals(session, student_ids, student_count)
        fix_health_conditions(session, student_ids, student_count)
        fix_health_alerts(session, student_ids, student_count)
        fix_meals_and_plans(session, student_count)
        
        print("\n🎉 All remaining health table fixes completed!")
        
    except Exception as e:
        print(f"❌ Error during fixing: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
