"""
Phase 3: Corrected Health & Fitness System Seeding
Seeds tables with correct schema matching actual database structure
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_corrected(session: Session) -> Dict[str, int]:
    """
    Corrected Phase 3 Health & Fitness System seeding
    Uses actual database schema
    """
    print("="*60)
    print("🏥 PHASE 3: CORRECTED HEALTH & FITNESS SYSTEM")
    print("="*60)
    print("📊 Seeding health, fitness, and nutrition tables with correct schema")
    print("="*60)
    
    results = {}
    
    # Seed health metric history
    results.update(seed_health_metric_history_corrected(session))
    
    # Seed health metric thresholds  
    results.update(seed_health_metric_thresholds_corrected(session))
    
    # Seed medical conditions
    results.update(seed_medical_conditions_corrected(session))
    
    # Seed emergency contacts
    results.update(seed_emergency_contacts_corrected(session))
    
    # Seed fitness assessments
    results.update(seed_fitness_assessments_corrected(session))
    
    # Seed fitness metrics
    results.update(seed_fitness_metrics_corrected(session))
    
    # Seed fitness metric history
    results.update(seed_fitness_metric_history_corrected(session))
    
    # Seed nutrition tables
    results.update(seed_nutrition_logs_corrected(session))
    results.update(seed_foods_corrected(session))
    results.update(seed_food_items_corrected(session))
    results.update(seed_meals_corrected(session))
    results.update(seed_meal_plans_corrected(session))
    results.update(seed_meal_food_items_corrected(session))
    
    print("\n" + "="*60)
    print("🎉 PHASE 3 CORRECTED SEEDING FINISHED!")
    print("="*60)
    total_records = sum(results.values())
    print(f"📊 Total records created: {total_records:,}")
    print(f"📋 Tables populated: {len([k for k, v in results.items() if v > 0])}")
    print("="*60)
    
    return results

def seed_health_metric_history_corrected(session: Session) -> Dict[str, int]:
    """Seed health_metric_history table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_history already has {existing_count} records, skipping...")
            return {'health_metric_history': existing_count}
        
        # Get health_metrics IDs for foreign key
        health_metrics_result = session.execute(text("SELECT id FROM health_metrics ORDER BY id"))
        health_metrics_ids = [row[0] for row in health_metrics_result.fetchall()]
        
        if not health_metrics_ids:
            print("  ⚠️  No health_metrics found, skipping health_metric_history...")
            return {'health_metric_history': 0}
        
        # Create health metric history records
        records = []
        for i in range(500):
            record = {
                'metric_id': random.choice(health_metrics_ids),
                'value': round(random.uniform(50, 200), 2),
                'recorded_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'notes': f'Health metric history record {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO health_metric_history (metric_id, value, recorded_at, notes, created_at, updated_at, 
                                             last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:metric_id, :value, :recorded_at, :notes, :created_at, :updated_at, 
                   :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} health metric history records")
        return {'health_metric_history': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metric_history: {e}")
        session.rollback()
        return {'health_metric_history': 0}

def seed_health_metric_thresholds_corrected(session: Session) -> Dict[str, int]:
    """Seed health_metric_thresholds table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_thresholds"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_thresholds already has {existing_count} records, skipping...")
            return {'health_metric_thresholds': existing_count}
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        # Get health_metrics IDs
        health_metrics_result = session.execute(text("SELECT id FROM health_metrics ORDER BY id"))
        health_metrics_ids = [row[0] for row in health_metrics_result.fetchall()]
        
        if not student_ids or not health_metrics_ids:
            print("  ⚠️  No students or health_metrics found, skipping health_metric_thresholds...")
            return {'health_metric_thresholds': 0}
        
        # Create health metric threshold records
        records = []
        metric_types = ['HEART_RATE', 'BLOOD_PRESSURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'MUSCLE_MASS']
        
        for i in range(40):
            record = {
                'student_id': random.choice(student_ids),
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

def seed_medical_conditions_corrected(session: Session) -> Dict[str, int]:
    """Seed medical_conditions table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM medical_conditions"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  medical_conditions already has {existing_count} records, skipping...")
            return {'medical_conditions': existing_count}
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping medical_conditions...")
            return {'medical_conditions': 0}
        
        # Create medical condition records
        records = []
        conditions = ['ASTHMA', 'DIABETES', 'HYPERTENSION', 'ALLERGIES', 'EPILEPSY', 'HEART_CONDITION', 'ARTHRITIS', 'ANEMIA']
        severities = ['MILD', 'MODERATE', 'SEVERE', 'CRITICAL']
        
        for i in range(100):
            record = {
                'student_id': random.choice(student_ids),
                'condition_name': random.choice(conditions),
                'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 3650)),
                'severity': random.choice(severities),
                'treatment': f'Treatment plan for {conditions[i % len(conditions)]}',
                'condition_notes': f'Medical condition notes {i + 1}',
                'condition_metadata': json.dumps({
                    "medications": [f'Medication {j}' for j in range(random.randint(1, 3))],
                    "restrictions": [f'Restriction {j}' for j in range(random.randint(0, 2))],
                    "status": random.choice(['ACTIVE', 'INACTIVE', 'TREATED', 'MONITORING'])
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO medical_conditions (student_id, condition_name, diagnosis_date, severity, treatment, condition_notes,
                                          condition_metadata, created_at, updated_at, last_accessed_at, archived_at, deleted_at,
                                          scheduled_deletion_at, retention_period)
            VALUES (:student_id, :condition_name, :diagnosis_date, :severity, :treatment, :condition_notes,
                   :condition_metadata, :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                   :scheduled_deletion_at, :retention_period)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} medical condition records")
        return {'medical_conditions': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding medical_conditions: {e}")
        session.rollback()
        return {'medical_conditions': 0}

def seed_emergency_contacts_corrected(session: Session) -> Dict[str, int]:
    """Seed emergency_contacts table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM emergency_contacts"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  emergency_contacts already has {existing_count} records, skipping...")
            return {'emergency_contacts': existing_count}
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping emergency_contacts...")
            return {'emergency_contacts': 0}
        
        # Create emergency contact records
        records = []
        relationships = ['PARENT', 'GUARDIAN', 'SIBLING', 'GRANDPARENT', 'AUNT', 'UNCLE', 'FAMILY_FRIEND']
        
        for i in range(200):
            record = {
                'student_id': random.choice(student_ids),
                'contact_name': f'Emergency Contact {i + 1}',
                'contact_relationship': random.choice(relationships),
                'phone_number': f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'email': f'emergency{i+1}@example.com',
                'address': f'{random.randint(100, 9999)} Main St, City, State {random.randint(10000, 99999)}',
                'contact_notes': f'Emergency contact notes {i + 1}',
                'contact_metadata': json.dumps({
                    "is_primary": random.choice([True, False]),
                    "phone_secondary": f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}' if random.choice([True, False]) else None
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO emergency_contacts (student_id, contact_name, contact_relationship, phone_number, email, address,
                                          contact_notes, contact_metadata, created_at, updated_at, last_accessed_at, archived_at,
                                          deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:student_id, :contact_name, :contact_relationship, :phone_number, :email, :address,
                   :contact_notes, :contact_metadata, :created_at, :updated_at, :last_accessed_at, :archived_at,
                   :deleted_at, :scheduled_deletion_at, :retention_period)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} emergency contact records")
        return {'emergency_contacts': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding emergency_contacts: {e}")
        session.rollback()
        return {'emergency_contacts': 0}

def seed_fitness_assessments_corrected(session: Session) -> Dict[str, int]:
    """Seed fitness_assessments table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_assessments"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_assessments already has {existing_count} records, skipping...")
            return {'fitness_assessments': existing_count}
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping fitness_assessments...")
            return {'fitness_assessments': 0}
        
        # Create fitness assessment records
        records = []
        assessment_types = ['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'BALANCE', 'AGILITY', 'ENDURANCE']
        
        for i in range(150):
            record = {
                'student_id': random.choice(student_ids),
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

def seed_fitness_metrics_corrected(session: Session) -> Dict[str, int]:
    """Seed fitness_metrics table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_metrics"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_metrics already has {existing_count} records, skipping...")
            return {'fitness_metrics': existing_count}
        
        # Create fitness metric records
        records = []
        metric_names = ['PUSH_UPS', 'SIT_UPS', 'PULL_UPS', 'MILE_RUN', 'FLEXIBILITY_TEST', 'BALANCE_TEST', 'AGILITY_TEST']
        units = ['count', 'seconds', 'minutes', 'inches', 'score']
        
        for i in range(30):
            record = {
                'metric_name': random.choice(metric_names),
                'description': f'Fitness metric description {i + 1}',
                'unit': random.choice(units),
                'category': random.choice(['STRENGTH', 'CARDIOVASCULAR', 'FLEXIBILITY', 'BALANCE', 'AGILITY']),
                'target_value': round(random.uniform(10, 100), 2),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_metrics (metric_name, description, unit, category, target_value, is_active, created_at, updated_at)
            VALUES (:metric_name, :description, :unit, :category, :target_value, :is_active, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} fitness metric records")
        return {'fitness_metrics': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_metrics: {e}")
        session.rollback()
        return {'fitness_metrics': 0}

def seed_fitness_metric_history_corrected(session: Session) -> Dict[str, int]:
    """Seed fitness_metric_history table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_metric_history already has {existing_count} records, skipping...")
            return {'fitness_metric_history': existing_count}
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping fitness_metric_history...")
            return {'fitness_metric_history': 0}
        
        # Create fitness metric history records
        records = []
        metric_types = ['PUSH_UPS', 'SIT_UPS', 'PULL_UPS', 'MILE_RUN', 'FLEXIBILITY_TEST', 'BALANCE_TEST', 'AGILITY_TEST']
        
        for i in range(400):
            record = {
                'student_id': random.choice(student_ids),
                'metric_type': random.choice(metric_types),
                'value': round(random.uniform(1, 100), 2),
                'unit': random.choice(['count', 'seconds', 'minutes', 'inches', 'score']),
                'recorded_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'notes': f'Fitness metric history record {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_metric_history (student_id, metric_type, value, unit, recorded_at, notes, created_at, updated_at)
            VALUES (:student_id, :metric_type, :value, :unit, :recorded_at, :notes, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ Created {len(records)} fitness metric history records")
        return {'fitness_metric_history': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_metric_history: {e}")
        session.rollback()
        return {'fitness_metric_history': 0}

# Nutrition functions - placeholders for now
def seed_nutrition_logs_corrected(session: Session) -> Dict[str, int]:
    """Seed nutrition_logs table - placeholder"""
    print("  ⚠️  nutrition_logs - placeholder (not implemented yet)")
    return {'nutrition_logs': 0}

def seed_foods_corrected(session: Session) -> Dict[str, int]:
    """Seed foods table - placeholder"""
    print("  ⚠️  foods - placeholder (not implemented yet)")
    return {'foods': 0}

def seed_food_items_corrected(session: Session) -> Dict[str, int]:
    """Seed food_items table - placeholder"""
    print("  ⚠️  food_items - placeholder (not implemented yet)")
    return {'food_items': 0}

def seed_meals_corrected(session: Session) -> Dict[str, int]:
    """Seed meals table - placeholder"""
    print("  ⚠️  meals - placeholder (not implemented yet)")
    return {'meals': 0}

def seed_meal_plans_corrected(session: Session) -> Dict[str, int]:
    """Seed meal_plans table - placeholder"""
    print("  ⚠️  meal_plans - placeholder (not implemented yet)")
    return {'meal_plans': 0}

def seed_meal_food_items_corrected(session: Session) -> Dict[str, int]:
    """Seed meal_food_items table - placeholder"""
    print("  ⚠️  meal_food_items - placeholder (not implemented yet)")
    return {'meal_food_items': 0}

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase3_corrected(session)
        print(f"Phase 3 corrected seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
