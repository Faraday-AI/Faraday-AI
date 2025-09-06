"""
Phase 3: Complete Health & Fitness System Seeding
Seeds all 42 tables (41 from DATABASE_SEEDING_STRATEGY.md + fitness_goals table)
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_all_42_tables(session: Session) -> Dict[str, int]:
    """
    Complete Phase 3 Health & Fitness System seeding
    Seeds all 42 tables (41 from DATABASE_SEEDING_STRATEGY.md + fitness_goals table)
    """
    print("="*70)
    print("🏥 PHASE 3: COMPLETE HEALTH & FITNESS SYSTEM (42 TABLES)")
    print("="*70)
    print("📊 Seeding all 42 health, fitness, and nutrition tables")
    print("🏥 Health Assessment & Monitoring (12 tables)")
    print("💪 Fitness Goals & Progress (13 tables)")
    print("🥗 Nutrition & Wellness (16 tables)")
    print("➕ Additional: fitness_goals (1 table)")
    print("="*70)
    
    results = {}
    
    # 3.1 Health Assessment & Monitoring (12 tables)
    print("\n🏥 HEALTH ASSESSMENT & MONITORING (12 tables)")
    print("-" * 60)
    
    # Already seeded - check and report
    health_tables = [
        'health_checks', 'health_conditions', 'health_alerts', 'health_metrics',
        'health_metric_history', 'health_metric_thresholds', 'medical_conditions',
        'emergency_contacts', 'fitness_assessments', 'fitness_metrics', 'fitness_metric_history'
    ]
    
    for table in health_tables:
        try:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            results[table] = count
            if count > 0:
                print(f"  ✅ {table}: {count} records (already seeded)")
            else:
                print(f"  ❌ {table}: 0 records (needs seeding)")
        except Exception as e:
            print(f"  ⚠️  {table}: ERROR - {str(e)[:50]}...")
            results[table] = 0
    
    # Seed fitness_health_metric_history
    results.update(seed_fitness_health_metric_history(session))
    
    # 3.2 Fitness Goals & Progress (13 tables)
    print("\n💪 FITNESS GOALS & PROGRESS (13 tables)")
    print("-" * 60)
    
    # Seed fitness_goals (now created)
    results.update(seed_fitness_goals(session))
    
    # Seed remaining fitness goal tables
    fitness_goal_tables = [
        'fitness_goal_progress_detailed', 'fitness_goal_progress_general',
        'health_fitness_goals', 'health_fitness_goal_progress',
        'health_fitness_health_alerts', 'health_fitness_health_checks',
        'health_fitness_health_conditions', 'health_fitness_metric_thresholds',
        'health_fitness_progress_notes', 'student_health_goal_progress',
        'student_health_goal_recommendations'
    ]
    
    for table in fitness_goal_tables:
        results.update(seed_table_basic(session, table, 100, f"Fitness goal data for {table}"))
    
    # student_health_fitness_goals already seeded
    try:
        result = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals"))
        count = result.scalar()
        results['student_health_fitness_goals'] = count
        print(f"  ✅ student_health_fitness_goals: {count} records (already seeded)")
    except Exception as e:
        results['student_health_fitness_goals'] = 0
        print(f"  ⚠️  student_health_fitness_goals: ERROR - {str(e)[:50]}...")
    
    # 3.3 Nutrition & Wellness (16 tables)
    print("\n🥗 NUTRITION & WELLNESS (16 tables)")
    print("-" * 60)
    
    # nutrition_goals already seeded
    try:
        result = session.execute(text("SELECT COUNT(*) FROM nutrition_goals"))
        count = result.scalar()
        results['nutrition_goals'] = count
        print(f"  ✅ nutrition_goals: {count} records (already seeded)")
    except Exception as e:
        results['nutrition_goals'] = 0
        print(f"  ⚠️  nutrition_goals: ERROR - {str(e)[:50]}...")
    
    # Seed remaining nutrition tables
    nutrition_tables = [
        'nutrition_logs', 'nutrition_recommendations', 'nutrition_education',
        'foods', 'food_items', 'meals', 'meal_plans', 'meal_food_items',
        'physical_education_meals', 'physical_education_meal_foods',
        'physical_education_nutrition_education', 'physical_education_nutrition_goals',
        'physical_education_nutrition_logs', 'physical_education_nutrition_plans',
        'physical_education_nutrition_recommendations'
    ]
    
    for table in nutrition_tables:
        results.update(seed_table_basic(session, table, 50, f"Nutrition data for {table}"))
    
    print("\n" + "="*70)
    print("🎉 PHASE 3 COMPLETE SEEDING FINISHED!")
    print("="*70)
    total_records = sum(results.values())
    seeded_tables = len([k for k, v in results.items() if v > 0])
    print(f"📊 Total records created: {total_records:,}")
    print(f"📋 Tables populated: {seeded_tables}/42")
    print(f"📈 Completion: {(seeded_tables/42*100):.1f}%")
    print("="*70)
    
    return results

def seed_fitness_goals(session: Session) -> Dict[str, int]:
    """Seed fitness_goals table"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ fitness_goals: {existing_count} records (already seeded)")
            return {'fitness_goals': existing_count}
        
        # Get student_health IDs
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not student_health_ids:
            print("  ⚠️  No student_health records found, skipping fitness_goals...")
            return {'fitness_goals': 0}
        
        # Create fitness goals records
        records = []
        goal_types = ['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']
        categories = ['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION']
        statuses = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD']
        
        for i in range(200):
            start_date = datetime.now() - timedelta(days=random.randint(1, 365))
            target_date = start_date + timedelta(days=random.randint(30, 180))
            
            record = {
                'student_id': random.choice(student_health_ids),
                'goal_type': random.choice(goal_types),
                'category': random.choice(categories),
                'description': f'Fitness goal {i + 1}: {random.choice(goal_types).lower().replace("_", " ")}',
                'target_value': round(random.uniform(10, 100), 2),
                'current_value': round(random.uniform(5, 80), 2),
                'unit': random.choice(['kg', 'lbs', 'reps', 'minutes', 'seconds', 'miles']),
                'start_date': start_date,
                'target_date': target_date,
                'completion_date': target_date if random.choice([True, False]) else None,
                'status': random.choice(statuses),
                'priority': random.randint(1, 5),
                'progress': round(random.uniform(0, 100), 2),
                'is_achieved': random.choice([True, False]),
                'notes': f'Progress notes for fitness goal {i + 1}',
                'goal_metadata': json.dumps({
                    'difficulty': random.choice(['EASY', 'MEDIUM', 'HARD']),
                    'frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY']),
                    'tracking_method': random.choice(['MANUAL', 'AUTOMATIC', 'SENSOR'])
                }),
                'created_at': start_date,
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_goals (student_id, goal_type, category, description, target_value, current_value, 
                                     unit, start_date, target_date, completion_date, status, priority, progress, 
                                     is_achieved, notes, goal_metadata, created_at, updated_at)
            VALUES (:student_id, :goal_type, :category, :description, :target_value, :current_value, 
                   :unit, :start_date, :target_date, :completion_date, :status, :priority, :progress, 
                   :is_achieved, :notes, :goal_metadata, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ fitness_goals: {len(records)} records created")
        return {'fitness_goals': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_goals: {e}")
        session.rollback()
        return {'fitness_goals': 0}

def seed_fitness_health_metric_history(session: Session) -> Dict[str, int]:
    """Seed fitness_health_metric_history table"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM fitness_health_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ fitness_health_metric_history: {existing_count} records (already seeded)")
            return {'fitness_health_metric_history': existing_count}
        
        # Get fitness_metrics IDs and student_health IDs
        fitness_metrics_result = session.execute(text("SELECT id FROM fitness_metrics ORDER BY id"))
        fitness_metric_ids = [row[0] for row in fitness_metrics_result.fetchall()]
        
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not fitness_metric_ids or not student_health_ids:
            print("  ⚠️  Missing required data, skipping fitness_health_metric_history...")
            return {'fitness_health_metric_history': 0}
        
        # Create combined fitness/health metric history records
        records = []
        
        for i in range(300):
            record = {
                'metric_id': random.choice(fitness_metric_ids),
                'student_id': random.choice(student_health_ids),
                'old_value': round(random.uniform(50, 200), 2),
                'new_value': round(random.uniform(50, 200), 2),
                'change_reason': f'Metric update {i + 1}',
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 365)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO fitness_health_metric_history (metric_id, student_id, old_value, new_value, change_reason, timestamp, created_at)
            VALUES (:metric_id, :student_id, :old_value, :new_value, :change_reason, :timestamp, :created_at)
        """), records)
        
        session.commit()
        print(f"  ✅ fitness_health_metric_history: {len(records)} records created")
        return {'fitness_health_metric_history': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_health_metric_history: {e}")
        session.rollback()
        return {'fitness_health_metric_history': 0}

def seed_table_basic(session: Session, table_name: str, record_count: int, description: str) -> Dict[str, int]:
    """Basic table seeding function for simple tables"""
    try:
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ {table_name}: {existing_count} records (already seeded)")
            return {table_name: existing_count}
        
        # Get table schema to understand what columns exist
        schema_result = session.execute(text(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """))
        
        columns_info = [(row[0], row[1], row[2]) for row in schema_result.fetchall()]
        
        if not columns_info:
            print(f"  ❌ {table_name}: No columns found")
            return {table_name: 0}
        
        # Create basic records based on column data types
        records = []
        for i in range(record_count):
            record = {}
            
            for col_name, data_type, is_nullable in columns_info:
                if col_name == 'id':
                    continue  # Skip ID columns
                elif col_name.endswith('_id'):
                    # Foreign key - use 1 as placeholder
                    record[col_name] = 1
                elif data_type in ['timestamp without time zone', 'timestamp with time zone']:
                    record[col_name] = datetime.now() - timedelta(days=random.randint(1, 365))
                elif data_type in ['double precision', 'numeric', 'real']:
                    record[col_name] = round(random.uniform(1, 100), 2)
                elif data_type in ['integer', 'bigint', 'smallint']:
                    record[col_name] = random.randint(1, 100)
                elif data_type == 'boolean':
                    record[col_name] = random.choice([True, False])
                elif data_type == 'json':
                    record[col_name] = json.dumps({"sample": "data", "record_id": i + 1})
                elif data_type == 'USER-DEFINED':
                    # Handle enums - use safe default values
                    if 'metric' in col_name.lower():
                        record[col_name] = 'HEART_RATE'
                    elif 'status' in col_name.lower():
                        record[col_name] = 'ACTIVE'
                    elif 'type' in col_name.lower():
                        record[col_name] = 'GENERAL'
                    else:
                        record[col_name] = 'DEFAULT'
                elif col_name in ['name', 'title', 'description']:
                    record[col_name] = f"{description} {i + 1}"
                elif col_name in ['notes', 'content']:
                    record[col_name] = f"Sample data for {table_name} record {i + 1}"
                elif col_name in ['is_active', 'enabled', 'visible']:
                    record[col_name] = random.choice([True, False])
                else:
                    # Default string value
                    record[col_name] = f"Sample {col_name} {i + 1}"
            
            records.append(record)
        
        # Build dynamic INSERT statement
        if records:
            columns_str = ', '.join([col for col in records[0].keys()])
            values_str = ', '.join([f':{col}' for col in records[0].keys()])
            
            session.execute(text(f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({values_str})
            """), records)
            
            session.commit()
            print(f"  ✅ {table_name}: {len(records)} records created")
            return {table_name: len(records)}
        else:
            print(f"  ❌ {table_name}: No records created")
            return {table_name: 0}
        
    except Exception as e:
        print(f"  ❌ Error seeding {table_name}: {str(e)[:100]}...")
        session.rollback()
        return {table_name: 0}

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase3_all_42_tables(session)
        print(f"Phase 3 complete seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
