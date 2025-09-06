#!/usr/bin/env python3
"""
Phase 3: Health & Fitness System Seeding Script (Simplified)
Seeds existing health, fitness, and nutrition tables with correct schema
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import SessionLocal
from app.core.logging import get_logger
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = get_logger(__name__)

def seed_health_checks(session: Session) -> int:
    """Seed health_checks table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_checks"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_checks already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual student IDs from students table
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        # Get actual user IDs for performed_by field
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not student_ids or not user_ids:
            print("  ⚠️  No students or users found, skipping health checks...")
            return 0
        
        # Create sample health check records
        health_checks = []
        check_types = ['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY']
        statuses = ['Completed', 'In Progress', 'Scheduled', 'Cancelled']
        
        for i in range(200):
            health_check = {
                'student_id': random.choice(student_ids),
                'check_type': random.choice(check_types),
                'status': random.choice(statuses),
                'performed_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'performed_by': random.choice(user_ids),  # Using actual user_id
                'notes': f'Health check notes for check {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            health_checks.append(health_check)
        
        # Insert health checks
        session.execute(text("""
            INSERT INTO health_checks (student_id, check_type, status, performed_at, performed_by,
                                     notes, created_at, updated_at, last_accessed_at,
                                     archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:student_id, :check_type, :status, :performed_at, :performed_by,
                   :notes, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), health_checks)
        
        session.commit()
        print(f"  ✅ Created {len(health_checks)} health checks")
        return len(health_checks)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_checks: {e}")
        session.rollback()
        return 0

def seed_health_conditions(session: Session) -> int:
    """Seed health_conditions table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_conditions"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_conditions already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual student IDs from students table
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping health conditions...")
            return 0
        
        # Create sample health conditions
        conditions = []
        condition_names = [
            'Asthma', 'Diabetes', 'Hypertension', 'Allergies', 'Heart Condition',
            'Joint Issues', 'Back Problems', 'Vision Impairment', 'Hearing Loss',
            'Epilepsy', 'Anxiety', 'Depression', 'ADHD', 'Autism', 'Learning Disability',
            'Physical Disability', 'Chronic Pain', 'Sleep Disorder', 'Eating Disorder',
            'Substance Abuse', 'Mental Health', 'Cardiovascular', 'Respiratory',
            'Musculoskeletal', 'Neurological', 'Endocrine', 'Immune System',
            'Digestive', 'Skin Condition', 'Other'
        ]
        severities = ['Mild', 'Moderate', 'Severe', 'Critical']
        
        for i in range(100):
            condition = {
                'student_id': random.choice(student_ids),
                'condition_name': random.choice(condition_names),
                'description': f'Health condition description {i + 1}',
                'severity': random.choice(severities),
                'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 3650)),
                'treatment': f'Treatment plan for condition {i + 1}',
                'restrictions': f'Activity restrictions for condition {i + 1}',
                'notes': f'Health condition notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            conditions.append(condition)
        
        # Insert health conditions
        session.execute(text("""
            INSERT INTO health_conditions (student_id, condition_name, description, severity,
                                         diagnosis_date, treatment, restrictions, notes,
                                         created_at, updated_at, last_accessed_at,
                                         archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:student_id, :condition_name, :description, :severity,
                   :diagnosis_date, :treatment, :restrictions, :notes,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), conditions)
        
        session.commit()
        print(f"  ✅ Created {len(conditions)} health conditions")
        return len(conditions)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_conditions: {e}")
        session.rollback()
        return 0

def seed_health_alerts(session: Session) -> int:
    """Seed health_alerts table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_alerts"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_alerts already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual student IDs and condition IDs
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        condition_result = session.execute(text("SELECT id FROM health_conditions ORDER BY id"))
        condition_ids = [row[0] for row in condition_result.fetchall()]
        
        if not student_ids or not condition_ids:
            print("  ⚠️  No students or conditions found, skipping health alerts...")
            return 0
        
        # Create sample health alerts
        alerts = []
        alert_types = ['RISK_THRESHOLD', 'EMERGENCY', 'PROTOCOL', 'MAINTENANCE', 'WEATHER']
        severities = ['Low', 'Medium', 'High', 'Critical']
        
        for i in range(50):
            alert = {
                'student_id': random.choice(student_ids),
                'condition_id': random.choice(condition_ids),
                'alert_type': random.choice(alert_types),
                'message': f'Health alert message for {random.choice(alert_types)}',
                'severity': random.choice(severities),
                'is_active': random.choice([True, False]),
                'resolved_at': datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None,
                'notes': f'Health alert notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            alerts.append(alert)
        
        # Insert health alerts
        session.execute(text("""
            INSERT INTO health_alerts (student_id, condition_id, alert_type, message, severity,
                                     is_active, resolved_at, notes, created_at, updated_at,
                                     last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:student_id, :condition_id, :alert_type, :message, :severity,
                   :is_active, :resolved_at, :notes, :created_at, :updated_at,
                   :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), alerts)
        
        session.commit()
        print(f"  ✅ Created {len(alerts)} health alerts")
        return len(alerts)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_alerts: {e}")
        session.rollback()
        return 0

def seed_health_metrics(session: Session) -> int:
    """Seed health_metrics table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_metrics"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metrics already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual student IDs from students table
        student_result = session.execute(text("SELECT id FROM students ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️  No students found, skipping health metrics...")
            return 0
        
        # Create sample health metrics
        metrics = []
        metric_types = [
            'Blood Pressure', 'Heart Rate', 'Temperature', 'Oxygen Saturation',
            'Weight', 'Height', 'BMI', 'Body Fat Percentage', 'Muscle Mass',
            'Bone Density', 'Cholesterol', 'Blood Sugar', 'Resting Heart Rate',
            'Maximum Heart Rate', 'VO2 Max', 'Flexibility', 'Strength', 'Endurance',
            'Balance', 'Coordination', 'Reaction Time', 'Sleep Duration', 'Sleep Quality',
            'Stress Level', 'Mood'
        ]
        units = ['mmHg', 'bpm', '°C', '%', 'kg', 'cm', 'hours', 'score', 'mg/dL']
        
        for i in range(500):
            metric = {
                'student_id': random.choice(student_ids),
                'metric_type': random.choice(metric_types),
                'value': random.uniform(50, 150),
                'unit': random.choice(units),
                'recorded_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'metric_metadata': json.dumps({
                    "source": random.choice(['Manual Entry', 'Device', 'Assessment', 'Calculation']),
                    "quality": random.choice(['High', 'Medium', 'Low']),
                    "notes": f'Metric metadata for {random.choice(metric_types)}'
                }),
                'notes': f'Health metric notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            metrics.append(metric)
        
        # Insert health metrics
        session.execute(text("""
            INSERT INTO health_metrics (student_id, metric_type, value, unit, recorded_at,
                                      metric_metadata, notes, created_at, updated_at, last_accessed_at,
                                      archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:student_id, :metric_type, :value, :unit, :recorded_at,
                   :metric_metadata, :notes, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), metrics)
        
        session.commit()
        print(f"  ✅ Created {len(metrics)} health metrics")
        return len(metrics)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metrics: {e}")
        session.rollback()
        return 0

def seed_student_health_fitness_goals(session: Session) -> int:
    """Seed student_health_fitness_goals table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  student_health_fitness_goals already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual student_health IDs (this table references student_health, not students)
        student_health_result = session.execute(text("SELECT id FROM student_health ORDER BY id"))
        student_health_ids = [row[0] for row in student_health_result.fetchall()]
        
        if not student_health_ids:
            print("  ⚠️  No student_health records found, skipping student health fitness goals...")
            return 0
        
        # Create sample student health fitness goals
        goals = []
        goal_types = ['WEIGHT_LOSS', 'MUSCLE_GAIN', 'FLEXIBILITY', 'ENDURANCE', 'STRENGTH', 'SKILL_IMPROVEMENT']
        categories = ['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE', 'BALANCE', 'COORDINATION', 'SPEED', 'AGILITY', 'POWER', 'SPORTS_SPECIFIC', 'GENERAL_FITNESS', 'WEIGHT_MANAGEMENT']
        timeframes = ['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'ACADEMIC_YEAR', 'CUSTOM']
        statuses = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', 'ON_HOLD']
        
        for i in range(200):
            goal = {
                'student_id': random.choice(student_health_ids),
                'goal_type': random.choice(goal_types),
                'category': random.choice(categories),
                'timeframe': random.choice(timeframes),
                'description': f'Health fitness goal description {i + 1}',
                'target_value': random.uniform(10, 100),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'completion_date': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                'status': random.choice(statuses),
                'priority': random.randint(1, 5),
                'notes': f'Student health fitness goal notes {i + 1}',
                'goal_metadata': json.dumps({
                    "difficulty": random.choice(['Easy', 'Medium', 'Hard']),
                    "motivation": random.choice(['High', 'Medium', 'Low']),
                    "support_needed": random.choice(['Yes', 'No']),
                    "tracking_method": random.choice(['Manual', 'Device', 'Assessment'])
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            goals.append(goal)
        
        # Insert student health fitness goals
        session.execute(text("""
            INSERT INTO student_health_fitness_goals (student_id, goal_type, category, timeframe,
                                                    description, target_value, target_date, completion_date,
                                                    status, priority, notes, goal_metadata,
                                                    created_at, updated_at)
            VALUES (:student_id, :goal_type, :category, :timeframe,
                   :description, :target_value, :target_date, :completion_date,
                   :status, :priority, :notes, :goal_metadata,
                   :created_at, :updated_at)
        """), goals)
        
        session.commit()
        print(f"  ✅ Created {len(goals)} student health fitness goals")
        return len(goals)
        
    except Exception as e:
        print(f"  ❌ Error seeding student_health_fitness_goals: {e}")
        session.rollback()
        return 0

def seed_nutrition_goals(session: Session) -> int:
    """Seed nutrition_goals table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM nutrition_goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  nutrition_goals already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual nutrition plan IDs (create some first if needed)
        plan_result = session.execute(text("SELECT id FROM nutrition_plans ORDER BY id"))
        plan_ids = [row[0] for row in plan_result.fetchall()]
        
        if not plan_ids:
            print("  ⚠️  No nutrition plans found, creating some first...")
            # Create some basic nutrition plans
            plans = []
            for i in range(10):
                plan = {
                    'plan_name': f'Nutrition Plan {i + 1}',
                    'description': f'Description for nutrition plan {i + 1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                plans.append(plan)
            
            session.execute(text("""
                INSERT INTO nutrition_plans (plan_name, description, created_at, updated_at)
                VALUES (:plan_name, :description, :created_at, :updated_at)
            """), plans)
            session.commit()
            
            # Get the new plan IDs
            plan_result = session.execute(text("SELECT id FROM nutrition_plans ORDER BY id"))
            plan_ids = [row[0] for row in plan_result.fetchall()]
        
        # Create sample nutrition goals
        goals = []
        goal_types = [
            'Calorie Intake', 'Protein Intake', 'Carbohydrate Intake', 'Fat Intake',
            'Fiber Intake', 'Water Intake', 'Vitamin Intake', 'Mineral Intake',
            'Weight Loss', 'Weight Gain', 'Muscle Building', 'Energy Level',
            'Digestive Health', 'Overall Nutrition'
        ]
        units = ['calories', 'grams', 'mg', 'mcg', 'cups', 'liters', 'servings']
        
        for i in range(100):
            goal = {
                'nutrition_plan_id': random.choice(plan_ids),
                'description': f'{random.choice(goal_types)} Goal {i + 1}',
                'target_value': random.uniform(100, 3000),
                'current_value': random.uniform(50, 1500),
                'unit': random.choice(units),
                'deadline': datetime.now() + timedelta(days=random.randint(30, 365)),
                'progress': random.uniform(0, 100),
                'notes': f'Nutrition goal notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            goals.append(goal)
        
        # Insert nutrition goals
        session.execute(text("""
            INSERT INTO nutrition_goals (nutrition_plan_id, description, target_value, current_value,
                                       unit, deadline, progress, notes, created_at, updated_at)
            VALUES (:nutrition_plan_id, :description, :target_value, :current_value,
                   :unit, :deadline, :progress, :notes, :created_at, :updated_at)
        """), goals)
        
        session.commit()
        print(f"  ✅ Created {len(goals)} nutrition goals")
        return len(goals)
        
    except Exception as e:
        print(f"  ❌ Error seeding nutrition_goals: {e}")
        session.rollback()
        return 0

def seed_phase3_health_fitness(session: Session) -> Dict[str, int]:
    """
    Seed Phase 3: Health & Fitness System (Simplified)
    Returns a dictionary with counts of records created for each table
    """
    print("\n" + "="*60)
    print("🏥 PHASE 3: HEALTH & FITNESS SYSTEM (SIMPLIFIED)")
    print("="*60)
    print("📊 Seeding existing health, fitness, and nutrition tables")
    print("🏥 Health assessment & monitoring")
    print("💪 Student fitness goals")
    print("🥗 Nutrition management")
    print("="*60)
    
    results = {}
    
    try:
        # Health Assessment & Monitoring
        print("\n🏥 HEALTH ASSESSMENT & MONITORING")
        print("-" * 50)
        
        print("Seeding health checks...")
        results['health_checks'] = seed_health_checks(session)
        
        print("Seeding health conditions...")
        results['health_conditions'] = seed_health_conditions(session)
        
        print("Seeding health alerts...")
        results['health_alerts'] = seed_health_alerts(session)
        
        print("Seeding health metrics...")
        results['health_metrics'] = seed_health_metrics(session)
        
        # Student Health & Fitness Goals
        print("\n💪 STUDENT HEALTH & FITNESS GOALS")
        print("-" * 50)
        
        print("Seeding student health fitness goals...")
        results['student_health_fitness_goals'] = seed_student_health_fitness_goals(session)
        
        # Nutrition Management
        print("\n🥗 NUTRITION MANAGEMENT")
        print("-" * 50)
        
        print("Seeding nutrition goals...")
        results['nutrition_goals'] = seed_nutrition_goals(session)
        
        # Calculate total records
        total_records = sum(results.values())
        
        print("\n" + "="*60)
        print("🎉 PHASE 3 SEEDING COMPLETE!")
        print("="*60)
        print(f"📊 Total records created: {total_records:,}")
        print(f"📋 Tables populated: {len(results)}")
        
        # Display results summary
        for table_name, count in results.items():
            print(f"  {table_name}: {count:,} records")
        
        print("="*60)
        
        return results
        
    except Exception as e:
        print(f"❌ Error in Phase 3 seeding: {e}")
        session.rollback()
        return results

if __name__ == "__main__":
    # Test the seeding functions
    session = SessionLocal()
    try:
        print("Testing Phase 3 Health & Fitness seeding (Simplified)...")
        result = seed_phase3_health_fitness(session)
        print(f'Phase 3 seeding completed with {sum(result.values())} total records')
        print('Results:', result)
    finally:
        session.close()
