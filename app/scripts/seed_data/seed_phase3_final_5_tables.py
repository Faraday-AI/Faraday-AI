"""
Phase 3: Complete Final 5 Tables - ULTIMATE COMPLETE VERSION
Seeds the remaining 5 tables with correct schema and foreign key references
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_phase3_final_5_tables(session: Session) -> Dict[str, int]:
    """
    Complete the final 5 tables with correct schema and foreign key references
    """
    print("="*70)
    print("🏥 PHASE 3: COMPLETE FINAL 5 TABLES - ULTIMATE COMPLETE")
    print("="*70)
    print("📊 Seeding the remaining 5 tables with correct schema")
    print("="*70)
    
    results = {}
    
    # Get reference data
    student_ids = get_table_ids(session, "students")
    progress_ids = get_table_ids(session, "progress")
    goal_ids = get_table_ids(session, "goals")
    pe_meal_ids = get_table_ids(session, "physical_education_meals")
    
    print(f"  📊 Found {len(student_ids)} students, {len(progress_ids)} progress records")
    print(f"  📊 Found {len(goal_ids)} goals, {len(pe_meal_ids)} physical_education_meals")
    
    # Seed the missing progress and goals data if needed
    if not progress_ids:
        print("  🔧 Seeding progress table...")
        seed_progress_table_correct(session, student_ids)
        progress_ids = get_table_ids(session, "progress")
        print(f"  ✅ progress: {len(progress_ids)} records created")
    
    if not goal_ids:
        print("  🔧 Seeding goals table...")
        seed_goals_table_correct(session, student_ids)
        goal_ids = get_table_ids(session, "goals")
        print(f"  ✅ goals: {len(goal_ids)} records created")
    
    # Fix the 5 remaining tables
    print("\n🔧 COMPLETING FINAL 5 TABLES")
    print("-" * 60)
    
    # 1. health_fitness_goal_progress
    results.update(seed_health_fitness_goal_progress_final(session, goal_ids, student_ids))
    
    # 2. health_fitness_progress_notes  
    results.update(seed_health_fitness_progress_notes_final(session, progress_ids))
    
    # 3. student_health_goal_progress
    results.update(seed_student_health_goal_progress_final(session, goal_ids))
    
    # 4. physical_education_meal_foods (with correct foreign key reference)
    results.update(seed_physical_education_meal_foods_final_correct(session, pe_meal_ids))
    
    # 5. Check all Phase 3 tables status
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
    
    print(f'\\n🎉 PHASE 3 COMPLETION: {seeded_count}/42 ({(seeded_count/42*100):.1f}%)')
    
    return results

def get_table_ids(session: Session, table_name: str) -> List[int]:
    """Get all IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def seed_progress_table_correct(session: Session, student_ids: List[int]):
    """Seed progress table with correct schema"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM progress"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            return
        
        records = []
        tracking_periods = ['WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY']
        statuses = ['ACTIVE', 'COMPLETED', 'PAUSED', 'CANCELLED']
        
        for i in range(50):
            start_date = datetime.now() - timedelta(days=random.randint(1, 365))
            end_date = start_date + timedelta(days=random.randint(30, 180))
            
            record = {
                'student_id': random.choice(student_ids),
                'tracking_period': random.choice(tracking_periods),
                'start_date': start_date,
                'end_date': end_date,
                'progress_metrics': json.dumps({"overall_score": random.randint(60, 100), "improvement": random.randint(5, 25)}),
                'baseline_data': json.dumps({"initial_score": random.randint(40, 80), "baseline_date": start_date.isoformat()}),
                'current_data': json.dumps({"current_score": random.randint(60, 100), "last_updated": datetime.now().isoformat()}),
                'improvement_rate': round(random.uniform(0.1, 2.0), 2),
                'fitness_metrics': json.dumps({"strength": random.randint(1, 10), "endurance": random.randint(1, 10)}),
                'skill_assessments': json.dumps({"technical_skills": random.randint(1, 10), "tactical_skills": random.randint(1, 10)}),
                'attendance_record': json.dumps({"attendance_rate": random.uniform(0.7, 1.0), "total_sessions": random.randint(10, 50)}),
                'goals_progress': json.dumps({"goals_achieved": random.randint(1, 5), "goals_pending": random.randint(1, 3)}),
                'challenges_faced': json.dumps(["Motivation", "Time management", "Skill development"]),
                'support_provided': json.dumps({"coaching_hours": random.randint(5, 20), "mentor_sessions": random.randint(2, 10)}),
                'next_evaluation_date': end_date + timedelta(days=random.randint(7, 30)),
                'is_on_track': random.choice([True, False]),
                'strength_score': round(random.uniform(1, 10), 2),
                'endurance_score': round(random.uniform(1, 10), 2),
                'flexibility_score': round(random.uniform(1, 10), 2),
                'coordination_score': round(random.uniform(1, 10), 2),
                'created_by': f"coach_{i + 1}",
                'updated_by': f"coach_{i + 1}",
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
                'status': random.choice(statuses),
                'is_active': random.choice([True, False])
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO progress (student_id, tracking_period, start_date, end_date, progress_metrics, 
                               baseline_data, current_data, improvement_rate, fitness_metrics, skill_assessments, 
                               attendance_record, goals_progress, challenges_faced, support_provided, 
                               next_evaluation_date, is_on_track, strength_score, endurance_score, 
                               flexibility_score, coordination_score, created_by, updated_by, audit_trail, 
                               last_audit_at, audit_status, is_valid, validation_errors, last_validated_at, 
                               validation_score, validation_history, created_at, updated_at, last_accessed_at, 
                               archived_at, deleted_at, scheduled_deletion_at, retention_period, metadata, 
                               status, is_active)
            VALUES (:student_id, :tracking_period, :start_date, :end_date, :progress_metrics, 
                   :baseline_data, :current_data, :improvement_rate, :fitness_metrics, :skill_assessments, 
                   :attendance_record, :goals_progress, :challenges_faced, :support_provided, 
                   :next_evaluation_date, :is_on_track, :strength_score, :endurance_score, 
                   :flexibility_score, :coordination_score, :created_by, :updated_by, :audit_trail, 
                   :last_audit_at, :audit_status, :is_valid, :validation_errors, :last_validated_at, 
                   :validation_score, :validation_history, :created_at, :updated_at, :last_accessed_at, 
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period, :metadata, 
                   :status, :is_active)
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
        goal_types = ['FITNESS', 'HEALTH', 'NUTRITION', 'ACADEMIC', 'SKILL_DEVELOPMENT']
        priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        difficulty_levels = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
        statuses = ['ACTIVE', 'COMPLETED', 'PAUSED', 'CANCELLED']
        
        for i in range(50):
            start_date = datetime.now() - timedelta(days=random.randint(1, 365))
            target_date = start_date + timedelta(days=random.randint(30, 365))
            
            record = {
                'student_id': random.choice(student_ids),
                'goal_type': random.choice(goal_types),
                'description': f'Goal {i + 1}: Improve overall performance in {random.choice(goal_types).lower()}',
                'target_date': target_date,
                'start_date': start_date,
                'priority': random.choice(priorities),
                'target_metrics': json.dumps({"target_score": random.randint(70, 100), "target_duration": random.randint(30, 180)}),
                'current_progress': json.dumps({"current_score": random.randint(40, 90), "progress_percentage": random.randint(10, 90)}),
                'completion_percentage': round(random.uniform(0, 100), 2),
                'difficulty_level': random.choice(difficulty_levels),
                'expected_duration': random.randint(30, 365),
                'required_resources': json.dumps({"equipment": ["Basic equipment"], "time_commitment": "2-3 hours per week"}),
                'success_criteria': json.dumps({"minimum_score": 70, "consistency_required": True}),
                'risk_factors': json.dumps(["Lack of motivation", "Time constraints", "Injury risk"]),
                'support_needed': json.dumps({"coaching": True, "peer_support": True, "family_support": False}),
                'last_progress_update': datetime.now() - timedelta(days=random.randint(1, 30)),
                'progress_history': json.dumps([{"date": start_date.isoformat(), "score": 50}, {"date": datetime.now().isoformat(), "score": 75}]),
                'blockers': json.dumps(["Time management", "Resource availability"]),
                'achievements': json.dumps(["First milestone reached", "Consistent progress"]),
                'motivation_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'engagement_metrics': json.dumps({"participation_rate": random.uniform(0.7, 1.0), "effort_level": random.randint(1, 10)}),
                'reward_system': json.dumps({"milestone_rewards": True, "completion_reward": "Certificate"}),
                'parent_goal_id': None,
                'is_template': False,
                'is_recurring': random.choice([True, False]),
                'recurrence_pattern': json.dumps({"frequency": "MONTHLY", "interval": 1}),
                'name': f'Goal {i + 1}',
                'status': random.choice(statuses),
                'is_active': random.choice([True, False])
            }
            records.append(record)
        
        session.execute(text("""
            INSERT INTO goals (student_id, goal_type, description, target_date, start_date, priority, 
                             target_metrics, current_progress, completion_percentage, difficulty_level, 
                             expected_duration, required_resources, success_criteria, risk_factors, 
                             support_needed, last_progress_update, progress_history, blockers, achievements, 
                             motivation_level, engagement_metrics, reward_system, parent_goal_id, is_template, 
                             is_recurring, recurrence_pattern, name, status, is_active)
            VALUES (:student_id, :goal_type, :description, :target_date, :start_date, :priority, 
                   :target_metrics, :current_progress, :completion_percentage, :difficulty_level, 
                   :expected_duration, :required_resources, :success_criteria, :risk_factors, 
                   :support_needed, :last_progress_update, :progress_history, :blockers, :achievements, 
                   :motivation_level, :engagement_metrics, :reward_system, :parent_goal_id, :is_template, 
                   :is_recurring, :recurrence_pattern, :name, :status, :is_active)
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

def seed_physical_education_meal_foods_final_correct(session: Session, pe_meal_ids: List[int]) -> Dict[str, int]:
    """Seed physical_education_meal_foods with correct foreign key reference"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_meal_foods"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ✅ physical_education_meal_foods: {existing_count} records (already seeded)")
            return {'physical_education_meal_foods': existing_count}
        
        if not pe_meal_ids:
            print("  ⚠️  Missing required data, skipping physical_education_meal_foods...")
            return {'physical_education_meal_foods': 0}
        
        records = []
        for i in range(150):
            record = {
                'meal_id': random.choice(pe_meal_ids),  # Use physical_education_meals IDs
                'food_name': f'PE Food {i + 1}',
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
        results = seed_phase3_final_5_tables(session)
        print(f"Phase 3 final 5 tables seeding finished with {sum(results.values())} total records")
    finally:
        session.close()
