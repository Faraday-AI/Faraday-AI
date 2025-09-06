"""
Phase 3: Complete Health & Fitness System Seeding
Seeds all 52 tables for comprehensive health, fitness, and nutrition data
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_complete(session: Session) -> Dict[str, int]:
    """
    Complete Phase 3 Health & Fitness System seeding
    Seeds all 52 tables as defined in DATABASE_SEEDING_STRATEGY.md
    """
    print("="*60)
    print("🏥 PHASE 3: COMPLETE HEALTH & FITNESS SYSTEM")
    print("="*60)
    print("📊 Seeding all 52 health, fitness, and nutrition tables")
    print("🏥 Health assessment & monitoring (11 tables)")
    print("💪 Fitness goals & progress (13 tables)")
    print("🥗 Nutrition & wellness (28 tables)")
    print("="*60)
    
    results = {}
    
    # 3.1 Health Assessment & Monitoring (11 tables)
    print("\n🏥 HEALTH ASSESSMENT & MONITORING")
    print("-" * 50)
    
    # Already seeded in simple version - skip if exists
    health_tables = [
        'health_checks', 'health_conditions', 'health_alerts', 'health_metrics'
    ]
    
    for table in health_tables:
        try:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            if count > 0:
                print(f"  ⚠️  {table} already has {count} records, skipping...")
                results[table] = count
            else:
                print(f"  ❌ {table} is empty but not seeded in simple version")
                results[table] = 0
        except Exception as e:
            print(f"  ❌ Error checking {table}: {e}")
            results[table] = 0
    
    # Seed remaining health assessment tables
    results.update(seed_health_metric_history(session))
    results.update(seed_health_metric_thresholds(session))
    results.update(seed_medical_conditions(session))
    results.update(seed_emergency_contacts(session))
    results.update(seed_fitness_assessments(session))
    results.update(seed_fitness_metrics(session))
    results.update(seed_fitness_metric_history(session))
    results.update(seed_fitness_health_metric_history(session))
    
    # 3.2 Fitness Goals & Progress (13 tables)
    print("\n💪 FITNESS GOALS & PROGRESS")
    print("-" * 50)
    
    # Already seeded
    try:
        result = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals"))
        count = result.scalar()
        print(f"  ⚠️  student_health_fitness_goals already has {count} records, skipping...")
        results['student_health_fitness_goals'] = count
    except Exception as e:
        print(f"  ❌ Error checking student_health_fitness_goals: {e}")
        results['student_health_fitness_goals'] = 0
    
    # Seed remaining fitness goal tables
    results.update(seed_fitness_goals(session))
    results.update(seed_fitness_goal_progress_detailed(session))
    results.update(seed_fitness_goal_progress_general(session))
    results.update(seed_health_fitness_goals(session))
    results.update(seed_health_fitness_goal_progress(session))
    results.update(seed_health_fitness_health_alerts(session))
    results.update(seed_health_fitness_health_checks(session))
    results.update(seed_health_fitness_health_conditions(session))
    results.update(seed_health_fitness_metric_thresholds(session))
    results.update(seed_health_fitness_progress_notes(session))
    results.update(seed_student_health_goal_progress(session))
    results.update(seed_student_health_goal_recommendations(session))
    
    # 3.3 Nutrition & Wellness (28 tables)
    print("\n🥗 NUTRITION & WELLNESS")
    print("-" * 50)
    
    # Already seeded
    try:
        result = session.execute(text("SELECT COUNT(*) FROM nutrition_goals"))
        count = result.scalar()
        print(f"  ⚠️  nutrition_goals already has {count} records, skipping...")
        results['nutrition_goals'] = count
    except Exception as e:
        print(f"  ❌ Error checking nutrition_goals: {e}")
        results['nutrition_goals'] = 0
    
    # Seed remaining nutrition tables
    results.update(seed_nutrition_logs(session))
    results.update(seed_nutrition_recommendations(session))
    results.update(seed_nutrition_education(session))
    results.update(seed_foods(session))
    results.update(seed_food_items(session))
    results.update(seed_meals(session))
    results.update(seed_meal_plans(session))
    results.update(seed_meal_food_items(session))
    results.update(seed_physical_education_meals(session))
    results.update(seed_physical_education_meal_foods(session))
    results.update(seed_physical_education_nutrition_education(session))
    results.update(seed_physical_education_nutrition_goals(session))
    results.update(seed_physical_education_nutrition_logs(session))
    results.update(seed_physical_education_nutrition_plans(session))
    results.update(seed_physical_education_nutrition_recommendations(session))
    
    # Additional health/fitness tables found in empty list
    print("\n🏃‍♂️ ADDITIONAL HEALTH & FITNESS TABLES")
    print("-" * 50)
    results.update(seed_health_fitness_exercises(session))
    results.update(seed_health_fitness_workouts(session))
    results.update(seed_health_fitness_workout_exercises(session))
    results.update(seed_health_fitness_workout_plans(session))
    results.update(seed_health_fitness_workout_plan_workouts(session))
    results.update(seed_health_fitness_workout_sessions(session))
    results.update(seed_health_fitness_workout_exercises(session))
    
    print("\n" + "="*60)
    print("🎉 PHASE 3 COMPLETE SEEDING FINISHED!")
    print("="*60)
    total_records = sum(results.values())
    print(f"📊 Total records created: {total_records:,}")
    print(f"📋 Tables populated: {len([k for k, v in results.items() if v > 0])}")
    print("="*60)
    
    return results

def seed_health_metric_history(session: Session) -> Dict[str, int]:
    """Seed health_metric_history table"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_history already has {existing_count} records, skipping...")
            return {'health_metric_history': existing_count}
        
        # Get student_health IDs
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not student_health_ids:
            print("  ⚠️  No student_health records found, skipping health_metric_history...")
            return {'health_metric_history': 0}
        
        # Create health metric history records
        records = []
        metric_types = ['HEART_RATE', 'BLOOD_PRESSURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'MUSCLE_MASS']
        
        for i in range(500):
            record = {
                'student_health_id': random.choice(student_health_ids),
                'metric_type': random.choice(metric_types),
                'value': round(random.uniform(50, 200), 2),
                'unit': random.choice(['bpm', 'mmHg', 'kg', 'cm', '%', 'kg']),
                'recorded_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'notes': f'Health metric history record {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO health_metric_history (student_health_id, metric_type, value, unit, recorded_at, notes, created_at, updated_at)
            VALUES (:student_health_id, :metric_type, :value, :unit, :recorded_at, :notes, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} health metric history records")
        return {'health_metric_history': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metric_history: {e}")
        session.rollback()
        return {'health_metric_history': 0}

def seed_health_metric_thresholds(session: Session) -> Dict[str, int]:
    """Seed health_metric_thresholds table"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_thresholds"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_thresholds already has {existing_count} records, skipping...")
            return {'health_metric_thresholds': existing_count}
        
        # Create health metric threshold records
        records = []
        metric_types = ['HEART_RATE', 'BLOOD_PRESSURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'MUSCLE_MASS']
        age_groups = ['CHILD', 'TEEN', 'ADULT', 'SENIOR']
        
        for i in range(40):
            record = {
                'metric_type': random.choice(metric_types),
                'age_group': random.choice(age_groups),
                'min_value': round(random.uniform(50, 100), 2),
                'max_value': round(random.uniform(150, 200), 2),
                'unit': random.choice(['bpm', 'mmHg', 'kg', 'cm', '%', 'kg']),
                'severity_level': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'description': f'Health threshold for {metric_types[i % len(metric_types)]}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO health_metric_thresholds (metric_type, age_group, min_value, max_value, unit, severity_level, description, created_at, updated_at)
            VALUES (:metric_type, :age_group, :min_value, :max_value, :unit, :severity_level, :description, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} health metric threshold records")
        return {'health_metric_thresholds': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metric_thresholds: {e}")
        session.rollback()
        return {'health_metric_thresholds': 0}

def seed_medical_conditions(session: Session) -> Dict[str, int]:
    """Seed medical_conditions table"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM medical_conditions"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  medical_conditions already has {existing_count} records, skipping...")
            return {'medical_conditions': existing_count}
        
        # Get student_health IDs
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not student_health_ids:
            print("  ⚠️  No student_health records found, skipping medical_conditions...")
            return {'medical_conditions': 0}
        
        # Create medical condition records
        records = []
        conditions = ['ASTHMA', 'DIABETES', 'HYPERTENSION', 'ALLERGIES', 'EPILEPSY', 'HEART_CONDITION', 'ARTHRITIS', 'ANEMIA']
        severities = ['MILD', 'MODERATE', 'SEVERE', 'CRITICAL']
        statuses = ['ACTIVE', 'INACTIVE', 'TREATED', 'MONITORING']
        
        for i in range(100):
            record = {
                'student_health_id': random.choice(student_health_ids),
                'condition_name': random.choice(conditions),
                'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 3650)),
                'severity': random.choice(severities),
                'status': random.choice(statuses),
                'description': f'Medical condition description {i + 1}',
                'treatment_notes': f'Treatment notes for condition {i + 1}',
                'medications': json.dumps([f'Medication {j}' for j in range(random.randint(1, 3))]),
                'restrictions': json.dumps([f'Restriction {j}' for j in range(random.randint(0, 2))]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO medical_conditions (student_health_id, condition_name, diagnosis_date, severity, status, description, treatment_notes, medications, restrictions, created_at, updated_at)
            VALUES (:student_health_id, :condition_name, :diagnosis_date, :severity, :status, :description, :treatment_notes, :medications, :restrictions, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} medical condition records")
        return {'medical_conditions': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding medical_conditions: {e}")
        session.rollback()
        return {'medical_conditions': 0}

def seed_emergency_contacts(session: Session) -> Dict[str, int]:
    """Seed emergency_contacts table"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM emergency_contacts"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  emergency_contacts already has {existing_count} records, skipping...")
            return {'emergency_contacts': existing_count}
        
        # Get student_health IDs
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not student_health_ids:
            print("  ⚠️  No student_health records found, skipping emergency_contacts...")
            return {'emergency_contacts': 0}
        
        # Create emergency contact records
        records = []
        relationships = ['PARENT', 'GUARDIAN', 'SIBLING', 'GRANDPARENT', 'AUNT', 'UNCLE', 'FAMILY_FRIEND']
        
        for i in range(200):
            record = {
                'student_health_id': random.choice(student_health_ids),
                'contact_name': f'Emergency Contact {i + 1}',
                'relationship': random.choice(relationships),
                'phone_primary': f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'phone_secondary': f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}' if random.choice([True, False]) else None,
                'email': f'emergency{i+1}@example.com',
                'address': f'{random.randint(100, 9999)} Main St, City, State {random.randint(10000, 99999)}',
                'is_primary': random.choice([True, False]),
                'notes': f'Emergency contact notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO emergency_contacts (student_health_id, contact_name, relationship, phone_primary, phone_secondary, email, address, is_primary, notes, created_at, updated_at)
            VALUES (:student_health_id, :contact_name, :relationship, :phone_primary, :phone_secondary, :email, :address, :is_primary, :notes, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} emergency contact records")
        return {'emergency_contacts': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding emergency_contacts: {e}")
        session.rollback()
        return {'emergency_contacts': 0}

# Continue with remaining functions...
# (This is getting long, so I'll create the remaining functions in the next part)

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase3_complete(session)
        print(f"Phase 3 complete seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
