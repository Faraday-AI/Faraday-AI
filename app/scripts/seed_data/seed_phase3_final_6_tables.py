"""
Phase 3: Fix Final 6 Tables - ULTIMATE COMPLETE VERSION
Seeds the remaining 6 tables with correct column names
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_final_6_tables(session: Session) -> Dict[str, int]:
    """
    Fix the final 6 tables with correct column names
    """
    print("="*70)
    print("🏥 PHASE 3: FIX FINAL 6 TABLES - ULTIMATE COMPLETE")
    print("="*70)
    print("📊 Seeding the remaining 6 tables with correct column names")
    print("="*70)
    
    results = {}
    
    # Get reference data
    student_ids = get_table_ids(session, "students")
    meal_ids = get_table_ids(session, "meals")
    food_item_ids = get_table_ids(session, "food_items")
    
    print(f"  📊 Found {len(student_ids)} students, {len(meal_ids)} meals, {len(food_item_ids)} food_items")
    
    # Create missing tables and seed them
    create_and_seed_missing_tables(session, student_ids)
    
    # Get IDs from newly created tables
    progress_ids = get_table_ids(session, "progress")
    goal_ids = get_table_ids(session, "goals")
    
    print(f"  📊 Found {len(progress_ids)} progress records, {len(goal_ids)} goals")
    
    # Fix the 6 remaining tables
    print("\n🔧 FIXING REMAINING 6 TABLES")
    print("-" * 60)
    
    # 1. health_fitness_goal_progress
    results.update(seed_health_fitness_goal_progress_final(session, goal_ids, student_ids))
    
    # 2. health_fitness_progress_notes  
    results.update(seed_health_fitness_progress_notes_final(session, progress_ids))
    
    # 3. student_health_goal_progress
    results.update(seed_student_health_goal_progress_final(session, goal_ids))
    
    # 4. meal_food_items (with correct column names)
    results.update(seed_meal_food_items_final_correct(session, meal_ids, food_item_ids))
    
    # 5. physical_education_meal_foods (with correct column names)
    results.update(seed_physical_education_meal_foods_final_correct(session, meal_ids))
    
    # 6. Check all tables status
    print("\n📊 FINAL PHASE 3 STATUS CHECK")
    print("-" * 60)
    
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
    
    print(f'\\n📈 PHASE 3 COMPLETION: {seeded_count}/42 ({(seeded_count/42*100):.1f}%)')
    
    return results

def get_table_ids(session: Session, table_name: str) -> List[int]:
    """Get all IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def create_and_seed_missing_tables(session: Session, student_ids: List[int]):
    """Create and seed missing tables"""
    try:
        # Create progress table with correct schema
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS progress (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                progress_value DOUBLE PRECISION NOT NULL,
                progress_date TIMESTAMP NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create goals table with correct schema
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS goals (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                goal_type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                target_value DOUBLE PRECISION,
                current_value DOUBLE PRECISION,
                target_date TIMESTAMP,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        session.commit()
        print("  ✅ Created missing tables: progress, goals")
        
        # Seed the new tables
        seed_progress_table_correct(session, student_ids)
        seed_goals_table_correct(session, student_ids)
        
    except Exception as e:
        print(f"  ❌ Error creating missing tables: {e}")
        session.rollback()

def seed_progress_table_correct(session: Session, student_ids: List[int]):
    """Seed progress table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM progress"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            return
        
        records = []
        for i in range(50):
            record = {
                'student_id': random.choice(student_ids),
                'progress_value': round(random.uniform(10, 100), 2),
                'progress_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'notes': f'Progress record {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO progress (student_id, progress_value, progress_date, notes, created_at)
            VALUES (:student_id, :progress_value, :progress_date, :notes, :created_at)
        """), records)
        
        session.commit()
        print(f"  ✅ progress: {len(records)} records created")
        
    except Exception as e:
        print(f"  ❌ Error seeding progress table: {e}")
        session.rollback()

def seed_goals_table_correct(session: Session, student_ids: List[int]):
    """Seed goals table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            return
        
        records = []
        for i in range(50):
            record = {
                'student_id': random.choice(student_ids),
                'goal_type': random.choice(['FITNESS', 'HEALTH', 'NUTRITION', 'ACADEMIC']),
                'description': f'Goal {i + 1}: Improve overall performance',
                'target_value': round(random.uniform(50, 200), 2),
                'current_value': round(random.uniform(10, 100), 2),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'status': random.choice(['ACTIVE', 'COMPLETED', 'PAUSED']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO goals (student_id, goal_type, description, target_value, current_value, 
                             target_date, status, created_at)
            VALUES (:student_id, :goal_type, :description, :target_value, :current_value, 
                   :target_date, :status, :created_at)
        """), records)
        
        session.commit()
        print(f"  ✅ goals: {len(records)} records created")
        
    except Exception as e:
        print(f"  ❌ Error seeding goals table: {e}")
        session.rollback()

def seed_health_fitness_goal_progress_final(session: Session, goal_ids: List[int], student_ids: List[int]) -> Dict[str, int]:
    """Seed health_fitness_goal_progress with proper foreign keys"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_fitness_goal_progress"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ health_fitness_goal_progress: {existing_count} records (already seeded)")
            return {'health_fitness_goal_progress': existing_count}
        
        if not goal_ids or not student_ids:
            print("  ⚠️  Missing required data, skipping health_fitness_goal_progress...")
            return {'health_fitness_goal_progress': 0}
        
        records = []
        for i in range(100):
            record = {
                'goal_id': random.choice(goal_ids),
                'student_id': random.choice(student_ids),
                'progress_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'current_value': round(random.uniform(10, 100), 2),
                'target_value': round(random.uniform(50, 200), 2),
                'progress_percentage': round(random.uniform(0, 100), 2),
                'notes': f'Health fitness goal progress {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO health_fitness_goal_progress (goal_id, student_id, progress_date, current_value, 
                                                    target_value, progress_percentage, notes, created_at, updated_at)
            VALUES (:goal_id, :student_id, :progress_date, :current_value, :target_value, 
                   :progress_percentage, :notes, :created_at, :updated_at)
        """), records)
        
        session.commit()
        print(f"  ✅ health_fitness_goal_progress: {len(records)} records created")
        return {'health_fitness_goal_progress': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding health_fitness_goal_progress: {e}")
        session.rollback()
        return {'health_fitness_goal_progress': 0}

def seed_health_fitness_progress_notes_final(session: Session, progress_ids: List[int]) -> Dict[str, int]:
    """Seed health_fitness_progress_notes with correct foreign key reference"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM health_fitness_progress_notes"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ health_fitness_progress_notes: {existing_count} records (already seeded)")
            return {'health_fitness_progress_notes': existing_count}
        
        if not progress_ids:
            print("  ⚠️  Missing required data, skipping health_fitness_progress_notes...")
            return {'health_fitness_progress_notes': 0}
        
        records = []
        for i in range(50):  # Reduced count for complex table
            record = {
                'progress_id': random.choice(progress_ids),
                'note_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'note_type': random.choice(['PROGRESS', 'MILESTONE', 'CHALLENGE', 'ACHIEVEMENT']),
                'note_period': random.choice(['WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY']),
                'note_data': json.dumps({"content": f"Progress note {i + 1}", "priority": random.randint(1, 5)}),
                'performance_summary': json.dumps({"overall": "good", "trend": "improving"}),
                'achievement_highlights': json.dumps(["Goal achieved", "Milestone reached"]),
                'areas_for_improvement': json.dumps(["Consistency", "Endurance"]),
                'recommendations': f"Continue current approach for note {i + 1}",
                'next_steps': f"Focus on improvement areas for note {i + 1}",
                'parent_feedback': f"Parent feedback for note {i + 1}",
                'teacher_feedback': f"Teacher feedback for note {i + 1}",
                'student_feedback': f"Student feedback for note {i + 1}",
                'trend_analysis': json.dumps({"direction": "up", "rate": 0.1}),
                'comparative_metrics': json.dumps({"peer_average": 75, "student_score": 80}),
                'risk_factors': json.dumps(["Injury risk", "Overtraining"]),
                'success_factors': json.dumps(["Consistent practice", "Good nutrition"]),
                'created_by': f"teacher_{i + 1}",
                'updated_by': f"teacher_{i + 1}",
                'audit_trail': json.dumps({"changes": [], "version": 1}),
                'last_audit_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'audit_status': random.choice(['PENDING', 'APPROVED', 'REJECTED']),
                'is_valid': random.choice([True, False]),
                'validation_errors': json.dumps([]),
                'last_validated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'validation_score': round(random.uniform(0, 100), 2),
                'validation_history': json.dumps([{"date": "2024-01-01", "score": 85}]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(365, 2555),
                'metadata': json.dumps({"source": "manual", "quality": "high"}),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
                'is_active': random.choice([True, False])
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO health_fitness_progress_notes (progress_id, note_date, note_type, note_period, note_data, 
                                                     performance_summary, achievement_highlights, areas_for_improvement, 
                                                     recommendations, next_steps, parent_feedback, teacher_feedback, 
                                                     student_feedback, trend_analysis, comparative_metrics, risk_factors, 
                                                     success_factors, created_by, updated_by, audit_trail, last_audit_at, 
                                                     audit_status, is_valid, validation_errors, last_validated_at, 
                                                     validation_score, validation_history, created_at, updated_at, 
                                                     last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, 
                                                     retention_period, metadata, status, is_active)
            VALUES (:progress_id, :note_date, :note_type, :note_period, :note_data, :performance_summary, 
                   :achievement_highlights, :areas_for_improvement, :recommendations, :next_steps, :parent_feedback, 
                   :teacher_feedback, :student_feedback, :trend_analysis, :comparative_metrics, :risk_factors, 
                   :success_factors, :created_by, :updated_by, :audit_trail, :last_audit_at, :audit_status, 
                   :is_valid, :validation_errors, :last_validated_at, :validation_score, :validation_history, 
                   :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, 
                   :retention_period, :metadata, :status, :is_active)
        """), records)
        
        session.commit()
        print(f"  ✅ health_fitness_progress_notes: {len(records)} records created")
        return {'health_fitness_progress_notes': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding health_fitness_progress_notes: {e}")
        session.rollback()
        return {'health_fitness_progress_notes': 0}

def seed_student_health_goal_progress_final(session: Session, goal_ids: List[int]) -> Dict[str, int]:
    """Seed student_health_goal_progress with correct foreign key reference"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM student_health_goal_progress"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ student_health_goal_progress: {existing_count} records (already seeded)")
            return {'student_health_goal_progress': existing_count}
        
        if not goal_ids:
            print("  ⚠️  Missing required data, skipping student_health_goal_progress...")
            return {'student_health_goal_progress': 0}
        
        records = []
        for i in range(100):
            record = {
                'goal_id': random.choice(goal_ids),
                'current_value': round(random.uniform(10, 100), 2),
                'progress_percentage': round(random.uniform(0, 100), 2),
                'notes': f'Student health goal progress {i + 1}',
                'is_milestone': random.choice([True, False]),
                'progress_metadata': json.dumps({"milestone_type": "achievement", "celebration": "completed"}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'progress_date': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO student_health_goal_progress (goal_id, current_value, progress_percentage, notes, is_milestone, 
                                                    progress_metadata, created_at, updated_at, progress_date)
            VALUES (:goal_id, :current_value, :progress_percentage, :notes, :is_milestone, :progress_metadata, 
                   :created_at, :updated_at, :progress_date)
        """), records)
        
        session.commit()
        print(f"  ✅ student_health_goal_progress: {len(records)} records created")
        return {'student_health_goal_progress': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding student_health_goal_progress: {e}")
        session.rollback()
        return {'student_health_goal_progress': 0}

def seed_meal_food_items_final_correct(session: Session, meal_ids: List[int], food_item_ids: List[int]) -> Dict[str, int]:
    """Seed meal_food_items with correct column names"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM meal_food_items"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ meal_food_items: {existing_count} records (already seeded)")
            return {'meal_food_items': existing_count}
        
        if not meal_ids or not food_item_ids:
            print("  ⚠️  Missing required data, skipping meal_food_items...")
            return {'meal_food_items': 0}
        
        records = []
        for i in range(200):
            record = {
                'meal_id': random.choice(meal_ids),
                'food_item_id': random.choice(food_item_ids),  # Correct column name
                'quantity': round(random.uniform(0.5, 5.0), 2),
                'unit': random.choice(['g', 'kg', 'ml', 'l', 'cups', 'tbsp', 'tsp']),
                'calories': random.randint(50, 500),
                'protein': round(random.uniform(5, 50), 2),
                'carbohydrates': round(random.uniform(10, 100), 2),
                'fats': round(random.uniform(2, 30), 2),
                'fiber': round(random.uniform(1, 15), 2),
                'sugar': round(random.uniform(1, 40), 2),
                'sodium': round(random.uniform(50, 1000), 2),
                'preparation_method': random.choice(['BAKED', 'FRIED', 'GRILLED', 'STEAMED', 'RAW']),
                'cooking_time': random.randint(5, 60),
                'temperature': random.choice(['HOT', 'COLD', 'ROOM_TEMPERATURE']),
                'notes': f'Food item {i + 1} in meal',
                'additional_data': json.dumps({"source": "manual", "quality": "high"}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO meal_food_items (meal_id, food_item_id, quantity, unit, calories, protein, 
                                       carbohydrates, fats, fiber, sugar, sodium, preparation_method, 
                                       cooking_time, temperature, notes, additional_data, created_at)
            VALUES (:meal_id, :food_item_id, :quantity, :unit, :calories, :protein, :carbohydrates, 
                   :fats, :fiber, :sugar, :sodium, :preparation_method, :cooking_time, :temperature, 
                   :notes, :additional_data, :created_at)
        """), records)
        
        session.commit()
        print(f"  ✅ meal_food_items: {len(records)} records created")
        return {'meal_food_items': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding meal_food_items: {e}")
        session.rollback()
        return {'meal_food_items': 0}

def seed_physical_education_meal_foods_final_correct(session: Session, meal_ids: List[int]) -> Dict[str, int]:
    """Seed physical_education_meal_foods with correct column names"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_meal_foods"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ physical_education_meal_foods: {existing_count} records (already seeded)")
            return {'physical_education_meal_foods': existing_count}
        
        if not meal_ids:
            print("  ⚠️  Missing required data, skipping physical_education_meal_foods...")
            return {'physical_education_meal_foods': 0}
        
        records = []
        for i in range(150):
            record = {
                'meal_id': random.choice(meal_ids),
                'food_name': f'PE Food {i + 1}',  # Correct column name
                'quantity': round(random.uniform(0.5, 5.0), 2),
                'unit': random.choice(['g', 'kg', 'ml', 'l', 'cups', 'tbsp', 'tsp']),
                'calories': random.randint(50, 500),
                'protein': round(random.uniform(5, 50), 2),
                'carbs': round(random.uniform(10, 100), 2),
                'fat': round(random.uniform(2, 30), 2),
                'food_notes': f'PE meal food item {i + 1}',
                'food_metadata': json.dumps({"activity": "PE class", "intensity": "moderate"}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(365, 2555)
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO physical_education_meal_foods (meal_id, food_name, quantity, unit, calories, protein, 
                                                     carbs, fat, food_notes, food_metadata, created_at, updated_at, 
                                                     last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, 
                                                     retention_period)
            VALUES (:meal_id, :food_name, :quantity, :unit, :calories, :protein, :carbs, :fat, :food_notes, 
                   :food_metadata, :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                   :scheduled_deletion_at, :retention_period)
        """), records)
        
        session.commit()
        print(f"  ✅ physical_education_meal_foods: {len(records)} records created")
        return {'physical_education_meal_foods': len(records)}
        
    except Exception as e:
        print(f"  ❌ Error seeding physical_education_meal_foods: {e}")
        session.rollback()
        return {'physical_education_meal_foods': 0}

if __name__ == "__main__":
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        results = seed_phase3_final_6_tables(session)
        print(f"Phase 3 final 6 tables seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
