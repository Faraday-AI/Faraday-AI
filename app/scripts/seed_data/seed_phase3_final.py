"""
Phase 3: Final Health & Fitness System Seeding
Seeds tables with correct schema and foreign key relationships
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_final(session: Session) -> Dict[str, int]:
    """
    Final Phase 3 Health & Fitness System seeding
    Uses correct foreign keys and column names
    """
    print("="*60)
    print("🏥 PHASE 3: FINAL HEALTH & FITNESS SYSTEM")
    print("="*60)
    print("📊 Seeding health, fitness, and nutrition tables with correct relationships")
    print("="*60)
    
    results = {}
    
    # Seed health metric thresholds (uses student_health.id)
    results.update(seed_health_metric_thresholds_final(session))
    
    # Seed fitness assessments (uses student_health.id)
    results.update(seed_fitness_assessments_final(session))
    
    # Seed fitness metrics (uses students.id)
    results.update(seed_fitness_metrics_final(session))
    
    # Seed fitness metric history (uses fitness_metrics.id)
    results.update(seed_fitness_metric_history_final(session))
    
    # Seed nutrition tables
    results.update(seed_nutrition_logs_final(session))
    results.update(seed_foods_final(session))
    results.update(seed_food_items_final(session))
    results.update(seed_meals_final(session))
    results.update(seed_meal_plans_final(session))
    results.update(seed_meal_food_items_final(session))
    
    print("\n" + "="*60)
    print("🎉 PHASE 3 FINAL SEEDING COMPLETED!")
    print("="*60)
    total_records = sum(results.values())
    print(f"📊 Total records created: {total_records:,}")
    print(f"📋 Tables populated: {len([k for k, v in results.items() if v > 0])}")
    print("="*60)
    
    return results

def seed_health_metric_thresholds_final(session: Session) -> Dict[str, int]:
    """Seed health_metric_thresholds table with student_health.id foreign key"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_thresholds"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_thresholds already has {existing_count} records, skipping...")
            return {'health_metric_thresholds': existing_count}
        
        # Get student_health IDs (correct foreign key)
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        # Get health_metrics IDs
        health_metrics_result = session.execute(text("SELECT id FROM health_metrics ORDER BY id"))
        health_metrics_ids = [row[0] for row in health_metrics_result.fetchall()]
        
        if not student_health_ids or not health_metrics_ids:
            print("  ⚠️  No student_health or health_metrics found, skipping health_metric_thresholds...")
            return {'health_metric_thresholds': 0}
        
        # Create health metric threshold records
        records = []
        metric_types = ['HEART_RATE', 'BLOOD_PRESSURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'MUSCLE_MASS']
        
        for i in range(40):
            record = {
                'student_id': random.choice(student_health_ids),  # This is actually student_health.id
                'metric_type': random.choice(metric_types),
                'min_value': round(random.uniform(50, 100), 2),
                'max_value': round(random.uniform(150, 200), 2),
                'threshold_metadata': json.dumps({
                    "severity_level": random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                    "age_group": random.choice(['CHILD', 'TEEN', 'ADULT', 'SENIOR']),
                    "description": f'Health threshold for {metric_types[i % len(metric_types)]}'
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'metric_id': random.choice(health_metrics_ids),
                'unit': random.choice(['bpm', 'mmHg', 'kg', 'cm', '%'])
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO health_metric_thresholds (student_id, metric_type, min_value, max_value, threshold_metadata, 
                                                created_at, updated_at, metric_id, unit)
            VALUES (:student_id, :metric_type, :min_value, :max_value, :threshold_metadata, 
                   :created_at, :updated_at, :metric_id, :unit)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} health metric threshold records")
        return {'health_metric_thresholds': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metric_thresholds: {e}")
        session.rollback()
        return {'health_metric_thresholds': 0}

def seed_fitness_assessments_final(session: Session) -> Dict[str, int]:
    """Seed fitness_assessments table with student_health.id foreign key"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_assessments"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_assessments already has {existing_count} records, skipping...")
            return {'fitness_assessments': existing_count}
        
        # Get student_health IDs (correct foreign key)
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not student_health_ids:
            print("  ⚠️  No student_health found, skipping fitness_assessments...")
            return {'fitness_assessments': 0}
        
        # Create fitness assessment records
        records = []
        assessment_types = ['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'BALANCE', 'AGILITY', 'ENDURANCE']
        
        for i in range(150):
            record = {
                'student_id': random.choice(student_health_ids),  # This is actually student_health.id
                'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'assessment_type': random.choice(assessment_types),
                'score': round(random.uniform(0, 100), 2),
                'assessment_notes': f'Fitness assessment notes {i + 1}',
                'assessment_metadata': json.dumps({
                    "max_score": 100,
                    "assessor_name": f'Assessor {random.randint(1, 10)}',
                    "status": random.choice(['COMPLETED', 'IN_PROGRESS', 'SCHEDULED', 'CANCELLED'])
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_assessments (student_id, assessment_date, assessment_type, score, assessment_notes,
                                           assessment_metadata, created_at, updated_at)
            VALUES (:student_id, :assessment_date, :assessment_type, :score, :assessment_notes,
                   :assessment_metadata, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} fitness assessment records")
        return {'fitness_assessments': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_assessments: {e}")
        session.rollback()
        return {'fitness_assessments': 0}

def seed_fitness_metrics_final(session: Session) -> Dict[str, int]:
    """Seed fitness_metrics table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_metrics"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_metrics already has {existing_count} records, skipping...")
            return {'fitness_metrics': existing_count}
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping fitness_metrics...")
            return {'fitness_metrics': 0}
        
        # Create fitness metric records with correct schema
        records = []
        metric_types = ['PUSH_UPS', 'SIT_UPS', 'PULL_UPS', 'MILE_RUN', 'FLEXIBILITY_TEST', 'BALANCE_TEST', 'AGILITY_TEST']
        units = ['count', 'seconds', 'minutes', 'inches', 'score']
        
        for i in range(30):
            record = {
                'student_id': random.choice(student_ids),
                'metric_type': random.choice(metric_types),
                'value': round(random.uniform(1, 100), 2),
                'unit': random.choice(units),
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 365)),
                'notes': f'Fitness metric notes {i + 1}',
                'metric_metadata': json.dumps({
                    "category": random.choice(['STRENGTH', 'CARDIOVASCULAR', 'FLEXIBILITY', 'BALANCE', 'AGILITY']),
                    "target_value": round(random.uniform(10, 100), 2),
                    "is_active": random.choice([True, False])
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_metrics (student_id, metric_type, value, unit, timestamp, notes, metric_metadata, created_at, updated_at)
            VALUES (:student_id, :metric_type, :value, :unit, :timestamp, :notes, :metric_metadata, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} fitness metric records")
        return {'fitness_metrics': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_metrics: {e}")
        session.rollback()
        return {'fitness_metrics': 0}

def seed_fitness_metric_history_final(session: Session) -> Dict[str, int]:
    """Seed fitness_metric_history table with fitness_metrics.id foreign key"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_metric_history already has {existing_count} records, skipping...")
            return {'fitness_metric_history': existing_count}
        
        # Get fitness_metrics IDs for foreign key
        fitness_metrics_result = session.execute(text("SELECT id FROM fitness_metrics ORDER BY id"))
        fitness_metrics_ids = [row[0] for row in fitness_metrics_result.fetchall()]
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not fitness_metrics_ids or not student_ids:
            print("  ⚠️  No fitness_metrics or students found, skipping fitness_metric_history...")
            return {'fitness_metric_history': 0}
        
        # Create fitness metric history records with correct schema
        records = []
        for i in range(400):
            record = {
                'metric_id': random.choice(fitness_metrics_ids),
                'student_id': random.choice(student_ids),
                'old_value': round(random.uniform(1, 50), 2),
                'new_value': round(random.uniform(51, 100), 2),
                'change_reason': random.choice(['IMPROVEMENT', 'DECLINE', 'MAINTENANCE', 'TRAINING', 'INJURY']),
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 365)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_metric_history (metric_id, student_id, old_value, new_value, change_reason, timestamp, created_at)
            VALUES (:metric_id, :student_id, :old_value, :new_value, :change_reason, :timestamp, :created_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} fitness metric history records")
        return {'fitness_metric_history': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_metric_history: {e}")
        session.rollback()
        return {'fitness_metric_history': 0}

# Nutrition functions - simplified implementations
def seed_nutrition_logs_final(session: Session) -> Dict[str, int]:
    """Seed nutrition_logs table - placeholder"""
    print("  ⚠️  nutrition_logs - placeholder (not implemented yet)")
    return {'nutrition_logs': 0}

def seed_foods_final(session: Session) -> Dict[str, int]:
    """Seed foods table - placeholder"""
    print("  ⚠️  foods - placeholder (not implemented yet)")
    return {'foods': 0}

def seed_food_items_final(session: Session) -> Dict[str, int]:
    """Seed food_items table - placeholder"""
    print("  ⚠️  food_items - placeholder (not implemented yet)")
    return {'food_items': 0}

def seed_meals_final(session: Session) -> Dict[str, int]:
    """Seed meals table - placeholder"""
    print("  ⚠️  meals - placeholder (not implemented yet)")
    return {'meals': 0}

def seed_meal_plans_final(session: Session) -> Dict[str, int]:
    """Seed meal_plans table - placeholder"""
    print("  ⚠️  meal_plans - placeholder (not implemented yet)")
    return {'meal_plans': 0}

def seed_meal_food_items_final(session: Session) -> Dict[str, int]:
    """Seed meal_food_items table - placeholder"""
    print("  ⚠️  meal_food_items - placeholder (not implemented yet)")
    return {'meal_food_items': 0}

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase3_final(session)
        print(f"Phase 3 final seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
