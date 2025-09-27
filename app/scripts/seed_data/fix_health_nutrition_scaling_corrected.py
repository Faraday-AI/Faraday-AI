#!/usr/bin/env python3
"""
Fix Health, Nutrition & Medical Table Scaling - CORRECTED VERSION
Fixed column names and data types to match actual database schema
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

def scale_health_tables(session: Session, student_ids: list, user_ids: list, student_count: int) -> dict:
    """Scale all health-related tables to student population"""
    print("🏥 SCALING HEALTH TABLES")
    print("-" * 40)
    
    results = {}
    
    # Health checks - 1 per student
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM health_checks")).scalar()
        if current_count < student_count:
            needed = student_count - current_count
            print(f"  📈 Adding {needed} health_checks records...")
            
            health_checks = []
            check_types = ['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY']
            statuses = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'NEEDS_IMPROVEMENT', 'ON_HOLD', 'CANCELLED']
            
            for i in range(needed):
                health_check = {
                    'student_id': random.choice(student_ids),
                    'check_type': random.choice(check_types),
                    'status': random.choice(statuses),
                    'performed_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'performed_by': random.choice(user_ids),
                    'notes': f'Health check notes for check {i + 1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                health_checks.append(health_check)
            
            session.execute(text("""
                INSERT INTO health_checks (student_id, check_type, status, performed_at, performed_by, notes, created_at, updated_at)
                VALUES (:student_id, :check_type, :status, :performed_at, :performed_by, :notes, :created_at, :updated_at)
            """), health_checks)
            
            results['health_checks'] = needed
            print(f"  ✅ Added {needed} health_checks records")
        else:
            print(f"  ✅ health_checks already has {current_count} records")
            results['health_checks'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling health_checks: {e}")
        results['health_checks'] = 0
    
    # Student health - 1 per student
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        if current_count < student_count:
            needed = student_count - current_count
            print(f"  📈 Adding {needed} student_health records...")
            
            student_health_records = []
            health_conditions = ["None", "Asthma", "Allergies", "ADHD", "Diabetes", "Other"]
            
            for i in range(needed):
                student_health_record = {
                    'student_id': random.choice(student_ids),
                    'first_name': f'Student{i + 1}',
                    'last_name': f'Health{i + 1}',
                    'date_of_birth': datetime.now() - timedelta(days=random.randint(365*5, 365*18)),
                    'gender': random.choice(['Male', 'Female', 'Other']),
                    'grade_level': random.choice(['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']),
                    'student_metadata': '{"source": "system", "type": "health_record"}',
                    'health_status': random.choice(['Healthy', 'Under Observation', 'Needs Attention', 'Critical']),
                    'health_notes': f'Health notes for student {i + 1} - {random.choice(health_conditions)}',
                    'health_metadata': f'{{"conditions": "{random.choice(health_conditions)}", "priority": "normal"}}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                student_health_records.append(student_health_record)
            
            session.execute(text("""
                INSERT INTO student_health (student_id, first_name, last_name, date_of_birth, gender, grade_level,
                                         student_metadata, health_status, health_notes, health_metadata,
                                         created_at, updated_at, last_accessed_at, archived_at, deleted_at,
                                         scheduled_deletion_at, retention_period)
                VALUES (:student_id, :first_name, :last_name, :date_of_birth, :gender, :grade_level,
                       :student_metadata, :health_status, :health_notes, :health_metadata,
                       :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                       :scheduled_deletion_at, :retention_period)
            """), student_health_records)
            
            results['student_health'] = needed
            print(f"  ✅ Added {needed} student_health records")
        else:
            print(f"  ✅ student_health already has {current_count} records")
            results['student_health'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling student_health: {e}")
        results['student_health'] = 0
    
    # Fitness assessments - 1 per student
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
        if current_count < student_count:
            needed = student_count - current_count
            print(f"  📈 Adding {needed} fitness_assessments records...")
            
            fitness_assessments = []
            assessment_types = ['Initial', 'Progress', 'Final', 'Quarterly', 'Annual']
            
            for i in range(needed):
                fitness_assessment = {
                    'student_id': random.choice(student_ids),
                    'assessment_type': random.choice(assessment_types),
                    'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'score': round(random.uniform(60, 100), 2),
                    'assessment_notes': f'Assessment notes for student {i + 1}',
                    'assessment_metadata': '{"source": "system", "type": "fitness"}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                fitness_assessments.append(fitness_assessment)
            
            session.execute(text("""
                INSERT INTO fitness_assessments (student_id, assessment_type, assessment_date, score, 
                                               assessment_notes, assessment_metadata, created_at, updated_at)
                VALUES (:student_id, :assessment_type, :assessment_date, :score, 
                       :assessment_notes, :assessment_metadata, :created_at, :updated_at)
            """), fitness_assessments)
            
            results['fitness_assessments'] = needed
            print(f"  ✅ Added {needed} fitness_assessments records")
        else:
            print(f"  ✅ fitness_assessments already has {current_count} records")
            results['fitness_assessments'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling fitness_assessments: {e}")
        results['fitness_assessments'] = 0
    
    return results

def scale_nutrition_tables(session: Session, student_ids: list, student_count: int) -> dict:
    """Scale all nutrition-related tables to student population"""
    print("🥗 SCALING NUTRITION TABLES")
    print("-" * 40)
    
    results = {}
    
    # Nutrition logs - 3 per student (CORRECTED: foods_consumed is JSON)
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
        target_count = student_count * 3
        if current_count < target_count:
            needed = target_count - current_count
            print(f"  📈 Adding {needed} nutrition_logs records...")
            
            nutrition_logs = []
            meal_types = ['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']
            
            for i in range(needed):
                nutrition_log = {
                    'student_id': random.choice(student_ids),
                    'date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'meal_type': random.choice(meal_types),
                    'foods_consumed': json.dumps([f'Food item {j+1}' for j in range(random.randint(1, 5))]),  # JSON array
                    'calories': random.randint(200, 800),
                    'protein': round(random.uniform(10, 50), 2),
                    'carbohydrates': round(random.uniform(20, 100), 2),
                    'fats': round(random.uniform(5, 50), 2),
                    'hydration': round(random.uniform(200, 1000), 2),
                    'notes': f'Nutrition notes for meal {i + 1}',
                    'additional_data': json.dumps({'source': 'system', 'type': 'nutrition'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                }
                nutrition_logs.append(nutrition_log)
            
            session.execute(text("""
                INSERT INTO nutrition_logs (student_id, date, meal_type, foods_consumed, calories, protein, 
                                         carbohydrates, fats, hydration, notes, additional_data, created_at)
                VALUES (:student_id, :date, :meal_type, :foods_consumed, :calories, :protein, 
                       :carbohydrates, :fats, :hydration, :notes, :additional_data, :created_at)
            """), nutrition_logs)
            
            results['nutrition_logs'] = needed
            print(f"  ✅ Added {needed} nutrition_logs records")
        else:
            print(f"  ✅ nutrition_logs already has {current_count} records")
            results['nutrition_logs'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling nutrition_logs: {e}")
        results['nutrition_logs'] = 0
    
    return results

def scale_meal_tables(session: Session, student_count: int) -> dict:
    """Scale all meal-related tables to student population"""
    print("🍽️ SCALING MEAL TABLES")
    print("-" * 40)
    
    results = {}
    
    # Physical education meals - CORRECTED: no student_id, needs nutrition_plan_id
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM physical_education_meals")).scalar()
        if current_count < student_count:
            needed = student_count - current_count
            print(f"  📈 Adding {needed} physical_education_meals records...")
            
            # Get nutrition plan IDs
            nutrition_plan_ids = session.execute(text("SELECT id FROM nutrition_plans LIMIT 100")).fetchall()
            if not nutrition_plan_ids:
                print("  ⚠️  No nutrition plans found, creating basic ones...")
                # Create basic nutrition plans
                for i in range(10):
                    session.execute(text("""
                        INSERT INTO nutrition_plans (name, description, created_at, updated_at)
                        VALUES (:name, :description, :created_at, :updated_at)
                    """), {
                        'name': f'Nutrition Plan {i+1}',
                        'description': f'Basic nutrition plan {i+1}',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                session.commit()
                nutrition_plan_ids = session.execute(text("SELECT id FROM nutrition_plans")).fetchall()
            
            pe_meals = []
            meal_types = ['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']
            
            for i in range(needed):
                pe_meal = {
                    'nutrition_plan_id': random.choice(nutrition_plan_ids)[0],
                    'meal_type': random.choice(meal_types),
                    'meal_time': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'calories': random.randint(300, 600),
                    'protein': round(random.uniform(10, 30), 2),
                    'carbs': round(random.uniform(20, 60), 2),
                    'fat': round(random.uniform(5, 25), 2),
                    'meal_notes': f'PE Meal {i + 1} - {random.choice(meal_types)}',
                    'meal_metadata': json.dumps({'source': 'system', 'type': 'pe_meal'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                pe_meals.append(pe_meal)
            
            session.execute(text("""
                INSERT INTO physical_education_meals (nutrition_plan_id, meal_type, meal_time, calories, protein, 
                                                    carbs, fat, meal_notes, meal_metadata, created_at, updated_at,
                                                    last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
                VALUES (:nutrition_plan_id, :meal_type, :meal_time, :calories, :protein, 
                       :carbs, :fat, :meal_notes, :meal_metadata, :created_at, :updated_at,
                       :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
            """), pe_meals)
            
            results['physical_education_meals'] = needed
            print(f"  ✅ Added {needed} physical_education_meals records")
        else:
            print(f"  ✅ physical_education_meals already has {current_count} records")
            results['physical_education_meals'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling physical_education_meals: {e}")
        results['physical_education_meals'] = 0
    
    return results

def scale_health_fitness_tables(session: Session, student_ids: list, student_count: int) -> dict:
    """Scale all health_fitness tables to student population"""
    print("💪 SCALING HEALTH_FITNESS TABLES")
    print("-" * 40)
    
    results = {}
    
    # Health fitness health checks - CORRECTED: no performed_at, different columns
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM health_fitness_health_checks")).scalar()
        if current_count < student_count:
            needed = student_count - current_count
            print(f"  📈 Adding {needed} health_fitness_health_checks records...")
            
            hf_health_checks = []
            check_types = ['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY']
            statuses = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'NEEDS_IMPROVEMENT', 'ON_HOLD', 'CANCELLED']
            
            for i in range(needed):
                hf_health_check = {
                    'student_id': random.choice(student_ids),
                    'check_type': random.choice(check_types),
                    'performed_by': f'Staff Member {random.randint(1, 50)}',
                    'findings': json.dumps({'status': 'normal', 'notes': f'Check findings {i + 1}'}),
                    'recommendations': f'Recommendations for check {i + 1}',
                    'status': random.choice(statuses),
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
                hf_health_checks.append(hf_health_check)
            
            session.execute(text("""
                INSERT INTO health_fitness_health_checks (student_id, check_type, performed_by, findings, 
                                                        recommendations, status, is_active, metadata, created_at, updated_at,
                                                        last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
                VALUES (:student_id, :check_type, :performed_by, :findings, 
                       :recommendations, :status, :is_active, :metadata, :created_at, :updated_at,
                       :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
            """), hf_health_checks)
            
            results['health_fitness_health_checks'] = needed
            print(f"  ✅ Added {needed} health_fitness_health_checks records")
        else:
            print(f"  ✅ health_fitness_health_checks already has {current_count} records")
            results['health_fitness_health_checks'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling health_fitness_health_checks: {e}")
        results['health_fitness_health_checks'] = 0
    
    return results

def scale_medical_tables(session: Session, student_ids: list, student_count: int) -> dict:
    """Scale all medical-related tables to student population"""
    print("🏥 SCALING MEDICAL TABLES")
    print("-" * 40)
    
    results = {}
    
    # Medical conditions - CORRECTED: treatment instead of treatment_notes
    try:
        current_count = session.execute(text("SELECT COUNT(*) FROM medical_conditions")).scalar()
        if current_count < student_count:
            needed = student_count - current_count
            print(f"  📈 Adding {needed} medical_conditions records...")
            
            medical_conditions = []
            condition_types = ['Asthma', 'Allergies', 'ADHD', 'Diabetes', 'Epilepsy', 'None', 'Other']
            severities = ['Mild', 'Moderate', 'Severe']
            
            for i in range(needed):
                medical_condition = {
                    'student_id': random.choice(student_ids),
                    'condition_name': random.choice(condition_types),
                    'severity': random.choice(severities),
                    'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 365*5)),
                    'treatment': f'Treatment plan for condition {i + 1}',
                    'condition_notes': f'Notes for condition {i + 1}',
                    'condition_metadata': json.dumps({'source': 'system', 'type': 'medical'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now(),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                medical_conditions.append(medical_condition)
            
            session.execute(text("""
                INSERT INTO medical_conditions (student_id, condition_name, severity, diagnosis_date, treatment, 
                                             condition_notes, condition_metadata, created_at, updated_at,
                                             last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
                VALUES (:student_id, :condition_name, :severity, :diagnosis_date, :treatment, 
                       :condition_notes, :condition_metadata, :created_at, :updated_at,
                       :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
            """), medical_conditions)
            
            results['medical_conditions'] = needed
            print(f"  ✅ Added {needed} medical_conditions records")
        else:
            print(f"  ✅ medical_conditions already has {current_count} records")
            results['medical_conditions'] = 0
    except Exception as e:
        print(f"  ❌ Error scaling medical_conditions: {e}")
        results['medical_conditions'] = 0
    
    return results

def main():
    """Main function to scale all health, nutrition, meal, and medical tables"""
    print("="*70)
    print("🔧 FIXING HEALTH, NUTRITION, MEAL & MEDICAL TABLE SCALING - CORRECTED")
    print("="*70)
    print("📊 Scaling all health, nutrition, meal, and medical tables to student population")
    print("🎯 Target: 3,877 students across all relevant tables")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Get reference data
        student_count = get_student_count(session)
        student_ids = get_student_ids(session)
        user_ids = get_user_ids(session)
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Student IDs available: {len(student_ids):,}")
        print(f"📊 User IDs available: {len(user_ids):,}")
        
        if not student_ids:
            print("❌ No students found, cannot proceed with scaling")
            return
        
        # Scale all table categories
        all_results = {}
        
        # Health tables
        health_results = scale_health_tables(session, student_ids, user_ids, student_count)
        all_results.update(health_results)
        session.commit()
        
        # Nutrition tables
        nutrition_results = scale_nutrition_tables(session, student_ids, student_count)
        all_results.update(nutrition_results)
        session.commit()
        
        # Meal tables
        meal_results = scale_meal_tables(session, student_count)
        all_results.update(meal_results)
        session.commit()
        
        # Health fitness tables
        hf_results = scale_health_fitness_tables(session, student_ids, student_count)
        all_results.update(hf_results)
        session.commit()
        
        # Medical tables
        medical_results = scale_medical_tables(session, student_ids, student_count)
        all_results.update(medical_results)
        session.commit()
        
        # Summary
        print("\n📊 SCALING SUMMARY")
        print("-" * 50)
        total_added = sum(all_results.values())
        print(f"✅ Total records added: {total_added:,}")
        
        for table_name, count in all_results.items():
            if count > 0:
                print(f"  📈 {table_name}: +{count:,} records")
        
        print("\n🎉 All health, nutrition, meal, and medical tables scaled successfully!")
        
    except Exception as e:
        print(f"❌ Error during scaling: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
