"""
Phase 3: Dynamic Health & Fitness System
Dynamically inspects table schemas and adapts to actual column names
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_dynamic(session: Session) -> Dict[str, int]:
    """
    Complete Phase 3 Health & Fitness System with dynamic schema inspection
    """
    print("="*70)
    print("🏥 PHASE 3: DYNAMIC HEALTH & FITNESS SYSTEM")
    print("="*70)
    print("📊 Dynamically inspecting schemas and adapting to actual column names")
    print("🏥 Health assessment & monitoring (12 tables)")
    print("💪 Fitness goals & progress (13 tables)")
    print("🥗 Nutrition & wellness (16 tables)")
    print("="*70)
    
    results = {}
    
    # Get reference data
    student_ids = get_table_ids(session, "students")
    user_ids = get_table_ids(session, "users")
    
    print(f"  📊 Found {len(student_ids)} students, {len(user_ids)} users")
    
    # CRITICAL: Create missing dependency tables first
    print("\n🔧 CREATING MISSING DEPENDENCY TABLES")
    print("-" * 50)
    
    # Create goals table if it doesn't exist
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS goals (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                goal_type VARCHAR(50),
                target_value DECIMAL(10,2),
                current_value DECIMAL(10,2),
                status VARCHAR(20) DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        session.commit()
        print("  ✅ Created goals table")
    except Exception as e:
        print(f"  ⚠️  Goals table creation: {e}")
    
    # Create nutrition_plans table if it doesn't exist
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS nutrition_plans (
                id SERIAL PRIMARY KEY,
                plan_name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        session.commit()
        print("  ✅ Created nutrition_plans table")
    except Exception as e:
        print(f"  ⚠️  Nutrition_plans table creation: {e}")
    
    # Create meals table if it doesn't exist
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS meals (
                id SERIAL PRIMARY KEY,
                meal_name VARCHAR(255) NOT NULL,
                meal_type VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        session.commit()
        print("  ✅ Created meals table")
    except Exception as e:
        print(f"  ⚠️  Meals table creation: {e}")
    
    # Create student_health table if it doesn't exist
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS student_health (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                health_status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        session.commit()
        print("  ✅ Created student_health table")
    except Exception as e:
        print(f"  ⚠️  Student_health table creation: {e}")
    
    # Create fitness_goals table if it doesn't exist
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS fitness_goals (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                goal_type VARCHAR(255) NOT NULL,
                description VARCHAR(255) NOT NULL,
                target_value DECIMAL(10,2),
                target_date TIMESTAMP WITHOUT TIME ZONE,
                status VARCHAR(255) NOT NULL,
                priority INTEGER,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            )
        """))
        session.commit()
        print("  ✅ Created fitness_goals table")
    except Exception as e:
        print(f"  ⚠️  Fitness_goals table creation: {e}")
    
    # Dependency tables are now seeded in Phase 1 - no need to create them here
    print("\nℹ️  DEPENDENCY TABLES")
    print("-" * 50)
    print("  ℹ️  Dependency tables are seeded in Phase 1 - proceeding with Phase 3 tables...")
    
    # Phase 3 tables to seed
    phase3_tables = [
        'health_checks', 'health_conditions', 'health_alerts', 'health_metrics',
        'health_metric_history', 'health_metric_thresholds', 'medical_conditions',
        'emergency_contacts', 'fitness_assessments', 'fitness_metrics', 'fitness_metric_history',
        'fitness_health_metric_history', 'fitness_goals', 'fitness_goal_progress_detailed',
        'fitness_goal_progress_general', 'health_fitness_goals', 'health_fitness_goal_progress',
        'health_fitness_health_alerts', 'health_fitness_health_checks', 'health_fitness_health_conditions',
        'health_fitness_metric_thresholds', 'health_fitness_progress_notes', 'student_health_fitness_goals',
        'student_health_goal_progress', 'student_health_goal_recommendations', 'nutrition_goals',
        'nutrition_logs', 'nutrition_recommendations', 'nutrition_education', 'foods', 'food_items',
        'meals', 'meal_plans', 'meal_food_items', 'physical_education_meals', 'physical_education_meal_foods',
        'physical_education_nutrition_education', 'physical_education_nutrition_goals',
        'physical_education_nutrition_logs', 'physical_education_nutrition_plans',
        'physical_education_nutrition_recommendations'
    ]
    
    print("\n🌱 SEEDING ALL PHASE 3 TABLES DYNAMICALLY")
    print("-" * 60)
    
    # Seed each table dynamically
    for table_name in phase3_tables:
        try:
            result = seed_table_dynamic(session, table_name, student_ids, user_ids)
            results.update(result)
        except Exception as e:
            print(f"  ❌ {table_name}: {str(e)[:50]}...")
            results[table_name] = 0
    
    # Final status check
    print("\n📊 FINAL PHASE 3 STATUS CHECK")
    print("-" * 60)
    
    seeded_count = 0
    for table in phase3_tables:
        try:
            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar()
            if count > 0:
                print(f'✅ {table}: {count} records')
                seeded_count += 1
                results[table] = count
            else:
                print(f'❌ {table}: 0 records')
                results[table] = 0
        except Exception as e:
            print(f'⚠️  {table}: ERROR - {str(e)[:30]}...')
            results[table] = 0
    
    print(f'\\n🎉 PHASE 3 COMPLETION: {seeded_count}/41 ({(seeded_count/41*100):.1f}%)')
    
    if seeded_count == 41:
        print("\\n🏆 PHASE 3 HEALTH & FITNESS SYSTEM: 100% COMPLETE! 🏆")
        print("🎯 All 41 tables successfully seeded!")
        print("🚀 Ready for future phases!")
    
    return results

def get_table_ids(session: Session, table_name: str) -> List[int]:
    """Get all IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def get_table_schema(session: Session, table_name: str) -> Dict[str, str]:
    """Get table schema with column names and data types"""
    try:
        result = session.execute(text(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """))
        
        schema = {}
        for row in result.fetchall():
            schema[row[0]] = {
                'data_type': row[1],
                'is_nullable': row[2] == 'YES'
            }
        return schema
    except:
        return {}

def get_enum_values(session: Session, enum_type: str) -> List[str]:
    """Get valid enum values"""
    try:
        result = session.execute(text(f"SELECT unnest(enum_range(NULL::{enum_type}))"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def seed_table_dynamic(session: Session, table_name: str, student_ids: List[int], user_ids: List[int]) -> Dict[str, int]:
    """Dynamically seed a table based on its actual schema"""
    try:
        # Check if table exists
        result = session.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
            )
        """))
        
        if not result.scalar():
            print(f"  ⚠️  {table_name}: Table does not exist")
            return {table_name: 0}
        
        # Get table schema
        schema = get_table_schema(session, table_name)
        if not schema:
            print(f"  ⚠️  {table_name}: Could not get schema")
            return {table_name: 0}
        
        # Check if table already has data
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ {table_name}: {existing_count} records (already seeded)")
            return {table_name: existing_count}
        
        # Special handling for student_health_goal_recommendations
        if table_name == 'student_health_goal_recommendations':
            return seed_student_health_goal_recommendations(session, student_ids)
        
        # Generate data based on actual schema
        records = generate_table_data_dynamic(table_name, schema, student_ids, user_ids)
        
        if not records:
            print(f"  ⚠️  {table_name}: No data generated")
            return {table_name: 0}
        
        # Insert data
        insert_data_dynamic(session, table_name, records, schema)
        
        print(f"  ✅ {table_name}: {len(records)} records")
        return {table_name: len(records)}
        
    except Exception as e:
        print(f"  ❌ {table_name}: {e}")
        session.rollback()
        return {table_name: 0}

def generate_table_data_dynamic(table_name: str, schema: Dict[str, Dict], student_ids: List[int], user_ids: List[int]) -> List[Dict]:
    """Generate data for a table based on its actual schema"""
    records = []
    
    # Determine number of records to generate
    record_count = get_record_count_for_table(table_name)
    
    for i in range(record_count):
        record = {}
        
        for column_name, column_info in schema.items():
            if column_name == 'id':
                continue  # Skip ID columns (auto-generated)
            
            # Generate appropriate data based on column name and type
            value = generate_column_value(column_name, column_info, student_ids, user_ids, i, table_name)
            if value is not None:
                record[column_name] = value
        
        records.append(record)
    
    return records

def get_record_count_for_table(table_name: str) -> int:
    """Get appropriate record count for each table"""
    counts = {
        'health_checks': 200,
        'health_conditions': 100,
        'health_alerts': 50,
        'health_metrics': 100,  # Reduced to prevent connection timeout
        'health_metric_history': 100,  # Reduced to prevent connection timeout
        'health_metric_thresholds': 40,
        'medical_conditions': 100,
        'emergency_contacts': 200,
        'fitness_assessments': 150,
        'fitness_metrics': 30,
        'fitness_metric_history': 100,  # Reduced to prevent connection timeout
        'fitness_health_metric_history': 50,  # Reduced to prevent connection timeout
        'fitness_goals': 200,
        'fitness_goal_progress_detailed': 100,
        'fitness_goal_progress_general': 100,
        'health_fitness_goals': 100,
        'health_fitness_goal_progress': 100,
        'health_fitness_health_alerts': 100,
        'health_fitness_health_checks': 100,
        'health_fitness_health_conditions': 100,
        'health_fitness_metric_thresholds': 50,
        'health_fitness_progress_notes': 50,
        'student_health_fitness_goals': 200,
        'student_health_goal_progress': 100,
        'student_health_goal_recommendations': 100,
        'nutrition_goals': 100,
        'nutrition_logs': 100,
        'nutrition_recommendations': 100,
        'nutrition_education': 50,
        'foods': 50,
        'food_items': 50,
        'meals': 100,
        'meal_plans': 100,
        'meal_food_items': 200,
        'physical_education_meals': 100,
        'physical_education_meal_foods': 150,
        'physical_education_nutrition_education': 50,
        'physical_education_nutrition_goals': 50,
        'physical_education_nutrition_logs': 50,
        'physical_education_nutrition_plans': 50,
        'physical_education_nutrition_recommendations': 50
    }
    
    return counts.get(table_name, 50)  # Default to 50 records

def generate_column_value(column_name: str, column_info: Dict, student_ids: List[int], user_ids: List[int], record_index: int, table_name: str = None) -> Any:
    """Generate appropriate value for a column based on its name and type"""
    data_type = column_info.get('data_type', 'text')
    is_nullable = column_info.get('is_nullable', True)
    
    # Handle nullable columns - but ensure required columns always have values
    if is_nullable and random.random() < 0.1:  # 10% chance of null
        return None
    
    # Handle enum types first
    if data_type == 'USER-DEFINED':  # Enum type
        return generate_enum_value(column_name, table_name)
    
    # Handle timestamp columns FIRST - MUST be before other patterns
    if 'last_validated_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    # Handle JSON columns FIRST - MUST be before other patterns
    if column_name.lower() == 'evidence':
        return json.dumps({"evidence_type": "photo", "url": f"https://example.com/evidence_{record_index}.jpg"})
    elif column_name.lower() in ['metrics', 'metadata', 'goal_metadata', 'threshold_metadata', 'assessment_metadata', 'recommendation_data', 'additional_data', 'food_metadata', 'meal_metadata', 'log_metadata', 'plan_metadata', 'education_metadata', 'audit_trail', 'validation_history', 'validation_errors', 'note_data', 'performance_summary', 'achievement_highlights', 'areas_for_improvement', 'trend_analysis', 'comparative_metrics', 'risk_factors', 'success_factors']:
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    # Handle boolean columns specifically - MUST be before other patterns
    if any(bool_col in column_name.lower() for bool_col in ['is_valid', 'is_active', 'is_implemented', 'is_template', 'is_recurring']):
        return random.choice([True, False])
    
    # Generate values based on column name patterns
    if 'student_id' in column_name.lower():
        # For foreign key references, use only valid student IDs from dependency tables
        # student_health table only has IDs 1-100, so limit to that range
        return random.randint(1, 100)
    
    if 'user_id' in column_name.lower() or 'performed_by' in column_name.lower():
        return random.choice(user_ids) if user_ids else 1
    
    if 'id' in column_name.lower() and column_name != 'id':
        # Handle foreign key references more intelligently
        if 'goal_id' in column_name.lower():
            # Use existing goal IDs from goals table (1-50)
            return random.randint(1, 50)
        elif 'fitness_goal_id' in column_name.lower():
            # Use existing fitness goal IDs from health_fitness_goals table (1-100)
            return random.randint(1, 100)
        elif 'nutrition_plan_id' in column_name.lower():
            # Use existing nutrition plan IDs from physical_education_nutrition_plans (1-50)
            return random.randint(1, 50)
        elif 'meal_id' in column_name.lower():
            # Use existing meal IDs from physical_education_meals table (1-100)
            return random.randint(1, 100)
        elif 'food_item_id' in column_name.lower():
            # Use existing food item IDs
            return random.randint(1, 25)  # More realistic range for food items
        elif 'metric_id' in column_name.lower():
            # Use existing metric IDs
            return random.randint(1, 20)  # More realistic range for metrics
        elif 'condition_id' in column_name.lower():
            # Use existing health condition IDs
            return random.randint(1, 100)  # Range for health conditions
        elif 'progress_id' in column_name.lower():
            # Use existing progress IDs from progress table (1-100)
            return random.randint(1, 100)
        elif 'student_id' in column_name.lower():
            # Use only valid student IDs from dependency tables (1-100)
            return random.randint(1, 100)
        else:
            return random.randint(1, 100)
    
    # Handle specific required parameters
    if 'learning_objectives' in column_name.lower():
        return json.dumps({"objective": f"Learning objective {record_index + 1}: Master key concepts and apply practical skills"})
    
    if 'retention_period' in column_name.lower():
        return random.randint(30, 365)  # 30 days to 1 year
    
    if 'fat_goal' in column_name.lower():
        return round(random.uniform(20.0, 35.0), 1)  # 20-35% body fat goal
    
    if 'archived_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 30))
    
    if 'deleted_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 7))
    
    if 'scheduled_deletion_at' in column_name.lower():
        return datetime.now() + timedelta(days=random.randint(30, 90))
    
    if 'last_accessed_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 7))
    
    if 'goal_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'metadata' in column_name.lower() and 'goal_metadata' not in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'protein_goal' in column_name.lower():
        return round(random.uniform(50.0, 200.0), 1)  # 50-200g protein goal
    
    if 'carbs_goal' in column_name.lower():
        return round(random.uniform(100.0, 400.0), 1)  # 100-400g carbs goal
    
    if 'fat_goal' in column_name.lower():
        return round(random.uniform(30.0, 150.0), 1)  # 30-150g fat goal
    
    if 'archived_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 30))
    
    if 'activities' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'resources' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'daily_calories' in column_name.lower():
        return random.randint(1200, 3000)  # 1200-3000 daily calories
    
    if 'nutrient_targets' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'hydration' in column_name.lower():
        return round(random.uniform(1.0, 5.0), 1)  # 1-5 liters hydration
    
    if 'reasoning' in column_name.lower():
        return f"Reasoning for record {record_index + 1}"
    
    if 'suggested_foods' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'plan_notes' in column_name.lower():
        return f"Plan notes for record {record_index + 1}"
    
    if 'log_notes' in column_name.lower():
        return f"Log notes for record {record_index + 1}"
    
    if 'food_notes' in column_name.lower():
        return f"Food notes for record {record_index + 1}"
    
    if 'meal_notes' in column_name.lower():
        return f"Meal notes for record {record_index + 1}"
    
    if 'plan_name' in column_name.lower():
        return f"Plan {record_index + 1}"
    
    
    # JSON columns already handled at the top of the function
    
    # Handle integer columns that should NOT be JSON
    if any(int_col in column_name.lower() for int_col in ['validation_score', 'retention_period']):
        return random.randint(0, 100)
    
    # Handle timestamp columns
    if 'last_validated_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    
    if 'log_date' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    if 'start_date' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    if 'end_date' in column_name.lower():
        return datetime.now() + timedelta(days=random.randint(1, 365))
    
    if 'age_group' in column_name.lower():
        return random.choice(['CHILD', 'TEEN', 'ADULT', 'SENIOR'])
    
    if 'content' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'education_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'log_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'plan_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'recommendation_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'food_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'meal_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'quantity' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'unit' in column_name.lower():
        return f"Text value {record_index + 1}"
    
    if 'calories' in column_name.lower():
        return random.randint(10, 1000)
    
    if 'protein' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'carbohydrates' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'fats' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'carbs' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'fat' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'food_name' in column_name.lower():
        return f"Name {record_index + 1}"
    
    if 'meal_id' in column_name.lower():
        return random.randint(2, 101)  # Reference physical_education_meals (IDs 2-101)
    
    if 'food_id' in column_name.lower():
        return random.randint(1, 1000)
    
    if 'target_value' in column_name.lower():
        return round(random.uniform(1.0, 100.0), 2)
    
    if 'current_value' in column_name.lower():
        return round(random.uniform(1.0, 100.0), 2)
    
    
    
    if 'title' in column_name.lower():
        return f"Title {record_index + 1}"
    
    if 'description' in column_name.lower():
        return f"Description for record {record_index + 1}"
    
    if 'notes' in column_name.lower():
        return f"Notes for record {record_index + 1}"
    
    if 'message' in column_name.lower():
        return f"Message {record_index + 1}"
    
    if 'email' in column_name.lower():
        return f"user{record_index + 1}@example.com"
    
    if 'phone' in column_name.lower():
        return f"555-{random.randint(1000, 9999)}"
    
    if 'address' in column_name.lower():
        return f"Address {record_index + 1}"
    
    if 'name' in column_name.lower():
        return f"Name {record_index + 1}"
    
    
    if 'status' in column_name.lower():
        return random.choice(['active', 'inactive', 'pending', 'completed'])
    
    if 'severity' in column_name.lower():
        return random.choice(['low', 'medium', 'high', 'critical'])
    
    # Handle additional missing parameters
    if 'learning_objectives' in column_name.lower():
        return json.dumps({"objective": f"Learning objective {record_index + 1}: Master key concepts and apply practical skills"})
    
    if 'last_accessed_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 7))
    
    if 'carbohydrates' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'carbs_goal' in column_name.lower():
        return round(random.uniform(100.0, 400.0), 1)  # 100-400g carbs goal
    
    if 'retention_period' in column_name.lower():
        return random.randint(30, 365)  # 30 days to 1 year
    
    if 'fat_goal' in column_name.lower():
        return round(random.uniform(30.0, 150.0), 1)  # 30-150g fat goal
    
    if 'archived_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 30))
    
    if 'deleted_at' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 7))
    
    if 'scheduled_deletion_at' in column_name.lower():
        return datetime.now() + timedelta(days=random.randint(30, 90))
    
    if 'goal_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'metadata' in column_name.lower() and 'goal_metadata' not in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'protein_goal' in column_name.lower():
        return round(random.uniform(50.0, 200.0), 1)  # 50-200g protein goal
    
    if 'carb_goal' in column_name.lower():
        return round(random.uniform(100.0, 400.0), 1)  # 100-400g carbs goal
    
    if 'fat_goal' in column_name.lower():
        return round(random.uniform(30.0, 150.0), 1)  # 30-150g fat goal
    
    if 'activities' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'resources' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'daily_calories' in column_name.lower():
        return random.randint(1200, 3000)  # 1200-3000 daily calories
    
    if 'nutrient_targets' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'hydration' in column_name.lower():
        return round(random.uniform(1.0, 5.0), 1)  # 1-5 liters hydration
    
    if 'reasoning' in column_name.lower():
        return f"Reasoning for record {record_index + 1}"
    
    if 'suggested_foods' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'plan_notes' in column_name.lower():
        return f"Plan notes for record {record_index + 1}"
    
    if 'log_notes' in column_name.lower():
        return f"Log notes for record {record_index + 1}"
    
    if 'food_notes' in column_name.lower():
        return f"Food notes for record {record_index + 1}"
    
    if 'meal_notes' in column_name.lower():
        return f"Meal notes for record {record_index + 1}"
    
    if 'plan_name' in column_name.lower():
        return f"Plan {record_index + 1}"
    
    
    if 'log_date' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    if 'start_date' in column_name.lower():
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    if 'end_date' in column_name.lower():
        return datetime.now() + timedelta(days=random.randint(1, 365))
    
    if 'age_group' in column_name.lower():
        return random.choice(['CHILD', 'TEEN', 'ADULT', 'SENIOR'])
    
    if 'content' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'education_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'log_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'plan_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'recommendation_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'food_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'meal_metadata' in column_name.lower():
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    if 'quantity' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'unit' in column_name.lower():
        return f"Text value {record_index + 1}"
    
    if 'calories' in column_name.lower():
        return random.randint(10, 1000)
    
    if 'protein' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'carbohydrates' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'fats' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'carbs' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'fat' in column_name.lower():
        return round(random.uniform(0.1, 100.0), 2)
    
    if 'food_name' in column_name.lower():
        return f"Name {record_index + 1}"
    
    if 'meal_id' in column_name.lower():
        return random.randint(2, 101)  # Reference physical_education_meals (IDs 2-101)
    
    if 'food_id' in column_name.lower():
        return random.randint(1, 1000)
    
    if 'target_value' in column_name.lower():
        return round(random.uniform(1.0, 100.0), 2)
    
    if 'current_value' in column_name.lower():
        return round(random.uniform(1.0, 100.0), 2)
    
    
    
    if 'title' in column_name.lower():
        return f"Title {record_index + 1}"
    
    if 'description' in column_name.lower():
        return f"Description for record {record_index + 1}"
    
    if 'notes' in column_name.lower():
        return f"Notes for record {record_index + 1}"
    
    if 'message' in column_name.lower():
        return f"Message {record_index + 1}"
    
    if 'email' in column_name.lower():
        return f"user{record_index + 1}@example.com"
    
    if 'phone' in column_name.lower():
        return f"555-{random.randint(1000, 9999)}"
    
    if 'address' in column_name.lower():
        return f"Address {record_index + 1}"
    
    if 'name' in column_name.lower():
        return f"Name {record_index + 1}"
    
    
    if 'status' in column_name.lower():
        return random.choice(['active', 'inactive', 'pending', 'completed'])
    
    if 'severity' in column_name.lower():
        return random.choice(['low', 'medium', 'high', 'critical'])
    
    # Generate values based on data type
    if data_type == 'integer':
        return random.randint(1, 1000)
    
    elif data_type == 'double precision' or data_type == 'numeric':
        return round(random.uniform(1, 100), 2)
    
    elif data_type == 'boolean':
        return random.choice([True, False])
    
    # Handle specific boolean column names
    if column_name.lower() in ['is_valid', 'is_active', 'is_milestone', 'is_implemented', 'was_consumed']:
        return random.choice([True, False])
    
    # JSON columns already handled at the top of the function
    
    # Handle specific text column names that should be JSON
    if column_name.lower() in ['learning_objectives']:
        return json.dumps({"objective": f"Learning objective {record_index + 1}: Master key concepts and apply practical skills"})
    
    # Handle specific integer columns that should not be JSON
    if column_name.lower() in ['validation_score']:
        return random.randint(1, 1000)
    
    
    elif data_type == 'timestamp without time zone':
        return datetime.now() - timedelta(days=random.randint(1, 365))
    
    elif data_type == 'character varying' or data_type == 'text':
        return generate_text_value(column_name, record_index)
    
    elif data_type == 'json':
        return json.dumps({"key": f"value_{record_index}", "data": random.randint(1, 100)})
    
    
    else:
        return f"value_{record_index}"

def generate_text_value(column_name: str, record_index: int) -> str:
    """Generate appropriate text value based on column name"""
    if 'name' in column_name.lower():
        return f"Name {record_index + 1}"
    elif 'description' in column_name.lower():
        return f"Description for record {record_index + 1}"
    elif 'notes' in column_name.lower():
        return f"Notes for record {record_index + 1}"
    elif 'message' in column_name.lower():
        return f"Message {record_index + 1}"
    elif 'email' in column_name.lower():
        return f"user{record_index + 1}@example.com"
    elif 'phone' in column_name.lower():
        return f"555-{random.randint(1000, 9999)}"
    elif 'address' in column_name.lower():
        return f"Address {record_index + 1}"
    elif 'type' in column_name.lower():
        return f"Type {record_index + 1}"
    elif 'status' in column_name.lower():
        return random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED'])
    elif 'severity' in column_name.lower():
        return random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
    elif 'reasoning' in column_name.lower():
        return f"Reasoning for record {record_index + 1}"
    elif 'title' in column_name.lower():
        return f"Title {record_index + 1}"
    elif 'content' in column_name.lower():
        return f"Content for record {record_index + 1}"
    elif 'age_group' in column_name.lower():
        return random.choice(['CHILD', 'TEEN', 'ADULT', 'SENIOR'])
    elif 'meal_type' in column_name.lower():
        return random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK'])
    elif 'plan_name' in column_name.lower():
        return f"Plan {record_index + 1}"
    else:
        return f"Text value {record_index + 1}"

def generate_enum_value(column_name: str, table_name: str = None) -> str:
    """Generate appropriate enum value based on column name"""
    # Direct column name matches first (most specific)
    if column_name.lower() == 'check_type':
        return random.choice(['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY'])
    elif column_name.lower() == 'alert_type':
        return random.choice(['RISK_THRESHOLD', 'EMERGENCY', 'PROTOCOL', 'MAINTENANCE', 'WEATHER'])
    elif column_name.lower() == 'metric_type':
        return random.choice(['HEART_RATE', 'BLOOD_PRESSURE', 'BODY_TEMPERATURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'OXYGEN_SATURATION', 'RESPIRATORY_RATE', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'BALANCE', 'COORDINATION'])
    elif column_name.lower() == 'meal_type':
        return random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT'])
    elif column_name.lower() == 'nutrition_category':
        return random.choice(['GENERAL', 'SPORTS', 'WEIGHT_MANAGEMENT', 'HEALTH_CONDITION', 'PERFORMANCE', 'RECOVERY'])
    elif column_name.lower() == 'goal_type':
        return random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT'])
    # Removed old status logic - now handled by pattern-based matches below
    elif column_name.lower() == 'severity':
        return random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'MILD', 'MODERATE', 'SEVERE'])
    # Removed old category logic - now handled by pattern-based matches below
    elif column_name.lower() == 'timeframe':
        return random.choice(['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'ACADEMIC_YEAR', 'CUSTOM'])
    elif 'student_health_fitness_goal_status' in column_name.lower():
        return random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD'])
    elif column_name.lower() == 'tracking_period':
        return random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY'])
    elif column_name.lower() == 'note_type':
        return random.choice(['PROGRESS', 'OBSERVATION', 'RECOMMENDATION', 'WARNING', 'SUCCESS'])
    elif column_name.lower() == 'audit_status':
        return random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED'])
    elif column_name.lower() == 'unit':
        return random.choice(['KG', 'LBS', 'CM', 'INCHES', 'CELSIUS', 'FAHRENHEIT', 'BPM', 'MMHG', 'PERCENT', 'SECONDS', 'MINUTES', 'METERS', 'KILOMETERS', 'MILES', 'SCORE', 'LEVEL'])
    elif column_name.lower() == 'age_group':
        return random.choice(['CHILD', 'TEEN', 'ADULT', 'SENIOR'])
    elif column_name.lower() == 'gender':
        return random.choice(['MALE', 'FEMALE', 'OTHER'])
    elif column_name.lower() == 'activity_level':
        return random.choice(['SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE', 'VERY_ACTIVE'])
    
    # Pattern-based matches - more comprehensive
    if 'category' in column_name.lower():
        # Use table name context to determine the correct enum type
        if table_name and 'nutrition' in table_name.lower():
            return random.choice(['GENERAL', 'SPORTS', 'WEIGHT_MANAGEMENT', 'HEALTH_CONDITION', 'PERFORMANCE', 'RECOVERY'])
        elif table_name and ('fitness' in table_name.lower() or 'health' in table_name.lower()):
            return random.choice(['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION', 'SPEED', 'AGILITY', 'POWER', 'SPORTS_SPECIFIC', 'GENERAL_FITNESS', 'WEIGHT_MANAGEMENT'])
        else:
            # Default to fitness categories for generic category columns
            return random.choice(['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION', 'SPEED', 'AGILITY', 'POWER', 'SPORTS_SPECIFIC', 'GENERAL_FITNESS', 'WEIGHT_MANAGEMENT'])
    elif 'goal' in column_name.lower() and 'type' in column_name.lower():
        return random.choice(['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT'])
    elif 'meal' in column_name.lower() and 'type' in column_name.lower():
        return random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT'])
    elif 'metric' in column_name.lower() and 'type' in column_name.lower():
        return random.choice(['HEART_RATE', 'BLOOD_PRESSURE', 'BODY_TEMPERATURE', 'WEIGHT', 'HEIGHT', 'BMI', 'BODY_FAT', 'OXYGEN_SATURATION', 'RESPIRATORY_RATE', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'BALANCE', 'COORDINATION'])
    elif 'timeframe' in column_name.lower():
        return random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY'])
    elif 'status' in column_name.lower():
        # Check if this is the student_health_fitness_goal_status_enum
        if table_name and 'student_health_fitness_goals' in table_name.lower():
            return random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD'])
        else:
            return random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD'])
    elif 'severity' in column_name.lower():
        return random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'MILD', 'MODERATE', 'SEVERE'])
    elif 'unit' in column_name.lower():
        return random.choice(['KG', 'LBS', 'CM', 'INCHES', 'CELSIUS', 'FAHRENHEIT', 'BPM', 'MMHG', 'PERCENT', 'SECONDS', 'MINUTES', 'METERS', 'KILOMETERS', 'MILES', 'SCORE', 'LEVEL'])
    elif 'age_group' in column_name.lower():
        return random.choice(['CHILD', 'TEEN', 'ADULT', 'SENIOR'])
    elif 'gender' in column_name.lower():
        return random.choice(['MALE', 'FEMALE', 'OTHER'])
    elif 'activity_level' in column_name.lower():
        return random.choice(['SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE', 'VERY_ACTIVE'])
    elif 'type' in column_name.lower():
        return random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED'])
    
    # Default fallback
    return random.choice(['ACTIVE', 'PENDING', 'COMPLETED'])

def insert_data_dynamic(session: Session, table_name: str, records: List[Dict], schema: Dict[str, Dict]):
    """Insert data into table using dynamic column names"""
    if not records:
        return
    
    # Get all columns from schema (excluding 'id' if it exists)
    all_columns = [col for col in schema.keys() if col != 'id']
    
    # Ensure all records have all required columns
    for record in records:
        for col in all_columns:
            if col not in record:
                # Generate missing value for required column
                record[col] = generate_column_value(col, schema[col], [], [], 0)
    
    # Build INSERT statement with all columns
    columns_str = ', '.join(all_columns)
    placeholders = ', '.join([f':{col}' for col in all_columns])
    
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Execute insert
    session.execute(text(query), records)
    session.commit()

def seed_student_health_goal_recommendations(session: Session, student_ids: List[int]) -> Dict[str, int]:
    """Seed student_health_goal_recommendations table by referencing student_health_fitness_goals"""
    try:
        # First check if table exists
        table_exists = session.execute(text("""
            SELECT EXISTS(SELECT FROM information_schema.tables 
                         WHERE table_name = 'student_health_goal_recommendations')
        """)).scalar()
        
        if not table_exists:
            print(f"  ⚠️  student_health_goal_recommendations: Table does not exist")
            return {'student_health_goal_recommendations': 0}
        
        # Get student health fitness goals to create recommendations
        goal_data = session.execute(text("""
            SELECT id, student_id, goal_type, target_value
            FROM student_health_fitness_goals
            LIMIT 100
        """)).fetchall()
        
        if not goal_data:
            print(f"  ⚠️  student_health_goal_recommendations: No student_health_fitness_goals data found")
            # Create some fallback data using student_ids
            print(f"  🔧 Creating fallback recommendations using student_ids...")
            recommendations_created = 0
            recommendation_types = ['NUTRITION', 'EXERCISE', 'SLEEP', 'HYDRATION', 'STRESS_MANAGEMENT']
            recommendation_levels = ['LOW', 'MEDIUM', 'HIGH']
            
            for i, student_id in enumerate(student_ids[:50]):  # Limit to 50 recommendations
                try:
                    insert_query = text("""
                        INSERT INTO student_health_goal_recommendations 
                        (goal_id, student_id, recommendation_type, description, priority, 
                         is_implemented, created_at, updated_at)
                        VALUES (:goal_id, :student_id, :recommendation_type, :description, 
                                :priority, :is_implemented, :created_at, :updated_at)
                    """)
                    
                    description = f"General health recommendation for student {student_id}"
                    
                    session.execute(insert_query, {
                        'goal_id': i + 1,  # Use sequential ID
                        'student_id': student_id,
                        'recommendation_type': random.choice(recommendation_types),
                        'description': description,
                        'priority': random.randint(1, 5),  # Use integer priority instead of string
                        'is_implemented': random.choice([True, False]),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    recommendations_created += 1
                    
                except Exception as e:
                    print(f"      ⚠️  Could not create fallback recommendation record: {e}")
                    continue
            
            session.commit()
            print(f"  ✅ student_health_goal_recommendations: {recommendations_created} records (fallback)")
            return {'student_health_goal_recommendations': recommendations_created}
        
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
        
        session.commit()
        print(f"  ✅ student_health_goal_recommendations: {recommendations_created} records")
        return {'student_health_goal_recommendations': recommendations_created}
        
    except Exception as e:
        print(f"  ❌ student_health_goal_recommendations: {e}")
        session.rollback()
        return {'student_health_goal_recommendations': 0}

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase3_dynamic(session)
        print(f"Phase 3 dynamic seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
