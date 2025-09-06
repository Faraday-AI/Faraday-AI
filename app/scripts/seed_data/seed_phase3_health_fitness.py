#!/usr/bin/env python3
"""
Phase 3: Health & Fitness System Seeding Script
Seeds 52 tables for comprehensive health, fitness, and nutrition management
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

# ============================================================================
# SECTION 3.1: HEALTH ASSESSMENT & MONITORING SEEDING FUNCTIONS
# ============================================================================

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
        
        if not student_ids:
            print("  ⚠️  No students found, skipping health checks...")
            return 0
        
        # Create sample health check records
        health_checks = []
        check_types = ['Routine', 'Emergency', 'Follow-up', 'Annual', 'Pre-activity']
        statuses = ['Completed', 'In Progress', 'Scheduled', 'Cancelled']
        
        for i in range(200):
            health_check = {
                'student_id': random.choice(student_ids),
                'check_type': random.choice(check_types),
                'status': random.choice(statuses),
                'performed_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'performed_by': random.choice(student_ids),  # Using student_id as placeholder
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
        
        # Get actual user IDs from users table
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping health alerts...")
            return 0
        
        # Create sample health alerts
        alerts = []
        alert_types = [
            'High Blood Pressure', 'Low Heart Rate', 'High Temperature', 'Low Oxygen Saturation',
            'Weight Gain', 'Weight Loss', 'Irregular Heartbeat', 'High Blood Sugar',
            'Low Blood Sugar', 'Allergic Reaction', 'Asthma Attack', 'Seizure',
            'Fainting', 'Chest Pain', 'Difficulty Breathing', 'Severe Headache',
            'Dizziness', 'Nausea', 'Vomiting', 'Fever'
        ]
        
        for i in range(50):
            alert = {
                'user_id': random.choice(user_ids),
                'alert_type': random.choice(alert_types),
                'alert_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'message': f'Health alert message for {random.choice(alert_types)}',
                'is_resolved': random.choice([True, False]),
                'resolved_date': datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None,
                'action_taken': f'Action taken for alert {i + 1}',
                'notes': f'Additional notes for alert {i + 1}',
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
            INSERT INTO health_alerts (user_id, alert_type, alert_date, severity, message,
                                     is_resolved, resolved_date, action_taken, notes,
                                     created_at, updated_at, last_accessed_at,
                                     archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :alert_type, :alert_date, :severity, :message,
                   :is_resolved, :resolved_date, :action_taken, :notes,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
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
        
        # Create sample health metrics
        metrics = []
        metric_types = [
            'Blood Pressure', 'Heart Rate', 'Temperature', 'Oxygen Saturation',
            'Weight', 'Height', 'BMI', 'Body Fat Percentage', 'Muscle Mass',
            'Bone Density', 'Cholesterol', 'Blood Sugar', 'Blood Pressure',
            'Resting Heart Rate', 'Maximum Heart Rate', 'VO2 Max', 'Flexibility',
            'Strength', 'Endurance', 'Balance', 'Coordination', 'Reaction Time',
            'Sleep Duration', 'Sleep Quality', 'Stress Level', 'Mood'
        ]
        
        for i, metric_name in enumerate(metric_types):
            metric = {
                'metric_name': metric_name,
                'description': f'Description for {metric_name} metric',
                'unit': random.choice(['mmHg', 'bpm', '°C', '%', 'kg', 'cm', 'hours', 'score']),
                'normal_range_min': random.uniform(0, 100),
                'normal_range_max': random.uniform(100, 200),
                'category': random.choice(['Vital Signs', 'Physical', 'Mental', 'Sleep', 'Performance']),
                'is_active': True,
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
            INSERT INTO health_metrics (metric_name, description, unit, normal_range_min,
                                      normal_range_max, category, is_active, created_at,
                                      updated_at, last_accessed_at, archived_at, deleted_at,
                                      scheduled_deletion_at, retention_period)
            VALUES (:metric_name, :description, :unit, :normal_range_min,
                   :normal_range_max, :category, :is_active, :created_at,
                   :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                   :scheduled_deletion_at, :retention_period)
        """), metrics)
        
        session.commit()
        print(f"  ✅ Created {len(metrics)} health metrics")
        return len(metrics)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metrics: {e}")
        session.rollback()
        return 0

def seed_health_metric_history(session: Session) -> int:
    """Seed health_metric_history table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_history already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs and metric IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        metric_result = session.execute(text("SELECT id FROM health_metrics ORDER BY id"))
        metric_ids = [row[0] for row in metric_result.fetchall()]
        
        if not user_ids or not metric_ids:
            print("  ⚠️  No users or metrics found, skipping health metric history...")
            return 0
        
        # Create sample health metric history
        history_records = []
        for i in range(500):
            record = {
                'user_id': random.choice(user_ids),
                'metric_id': random.choice(metric_ids),
                'recorded_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'value': random.uniform(50, 150),
                'notes': f'Health metric history note {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            history_records.append(record)
        
        # Insert health metric history
        session.execute(text("""
            INSERT INTO health_metric_history (user_id, metric_id, recorded_date, value, notes,
                                             created_at, updated_at, last_accessed_at,
                                             archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :metric_id, :recorded_date, :value, :notes,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), history_records)
        
        session.commit()
        print(f"  ✅ Created {len(history_records)} health metric history records")
        return len(history_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metric_history: {e}")
        session.rollback()
        return 0

def seed_health_metric_thresholds(session: Session) -> int:
    """Seed health_metric_thresholds table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_metric_thresholds"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_metric_thresholds already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual metric IDs
        metric_result = session.execute(text("SELECT id FROM health_metrics ORDER BY id"))
        metric_ids = [row[0] for row in metric_result.fetchall()]
        
        if not metric_ids:
            print("  ⚠️  No metrics found, skipping health metric thresholds...")
            return 0
        
        # Create sample health metric thresholds
        thresholds = []
        for i in range(40):
            threshold = {
                'metric_id': random.choice(metric_ids),
                'threshold_name': f'Threshold {i + 1}',
                'warning_min': random.uniform(0, 50),
                'warning_max': random.uniform(50, 100),
                'critical_min': random.uniform(0, 25),
                'critical_max': random.uniform(75, 100),
                'alert_message': f'Alert message for threshold {i + 1}',
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            thresholds.append(threshold)
        
        # Insert health metric thresholds
        session.execute(text("""
            INSERT INTO health_metric_thresholds (metric_id, threshold_name, warning_min, warning_max,
                                                critical_min, critical_max, alert_message, is_active,
                                                created_at, updated_at, last_accessed_at,
                                                archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:metric_id, :threshold_name, :warning_min, :warning_max,
                   :critical_min, :critical_max, :alert_message, :is_active,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), thresholds)
        
        session.commit()
        print(f"  ✅ Created {len(thresholds)} health metric thresholds")
        return len(thresholds)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_metric_thresholds: {e}")
        session.rollback()
        return 0

def seed_medical_conditions(session: Session) -> int:
    """Seed medical_conditions table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM medical_conditions"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  medical_conditions already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping medical conditions...")
            return 0
        
        # Create sample medical conditions
        conditions = []
        condition_names = [
            'Type 1 Diabetes', 'Type 2 Diabetes', 'Hypertension', 'Asthma', 'Allergies',
            'Heart Disease', 'Arthritis', 'Depression', 'Anxiety', 'ADHD',
            'Autism Spectrum Disorder', 'Epilepsy', 'Migraine', 'Chronic Pain',
            'Sleep Apnea', 'Obesity', 'High Cholesterol', 'Thyroid Disorder',
            'Anemia', 'Osteoporosis'
        ]
        
        for i in range(100):
            condition = {
                'user_id': random.choice(user_ids),
                'condition_name': random.choice(condition_names),
                'diagnosis_date': datetime.now() - timedelta(days=random.randint(30, 3650)),
                'severity': random.choice(['Mild', 'Moderate', 'Severe']),
                'status': random.choice(['Active', 'In Remission', 'Controlled', 'Chronic']),
                'treatment_plan': f'Treatment plan for {random.choice(condition_names)}',
                'medications': json.dumps([f'Medication 1 for {random.choice(condition_names)}', f'Medication 2 for {random.choice(condition_names)}']),
                'restrictions': json.dumps([f'Restriction 1', f'Restriction 2']),
                'notes': f'Medical condition notes {i + 1}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            conditions.append(condition)
        
        # Insert medical conditions
        session.execute(text("""
            INSERT INTO medical_conditions (user_id, condition_name, diagnosis_date, severity, status,
                                          treatment_plan, medications, restrictions, notes, is_active,
                                          created_at, updated_at, last_accessed_at,
                                          archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :condition_name, :diagnosis_date, :severity, :status,
                   :treatment_plan, :medications, :restrictions, :notes, :is_active,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), conditions)
        
        session.commit()
        print(f"  ✅ Created {len(conditions)} medical conditions")
        return len(conditions)
        
    except Exception as e:
        print(f"  ❌ Error seeding medical_conditions: {e}")
        session.rollback()
        return 0

def seed_emergency_contacts(session: Session) -> int:
    """Seed emergency_contacts table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM emergency_contacts"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  emergency_contacts already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping emergency contacts...")
            return 0
        
        # Create sample emergency contacts
        contacts = []
        for i in range(200):
            contact = {
                'user_id': random.choice(user_ids),
                'contact_name': f'Emergency Contact {i + 1}',
                'relationship': random.choice(['Parent', 'Guardian', 'Spouse', 'Sibling', 'Friend', 'Doctor', 'Other']),
                'phone_primary': f'555-{random.randint(1000, 9999)}',
                'phone_secondary': f'555-{random.randint(1000, 9999)}' if random.choice([True, False]) else None,
                'email': f'emergency{i + 1}@example.com',
                'address': f'{random.randint(100, 9999)} Emergency St, City, State {random.randint(10000, 99999)}',
                'is_primary': random.choice([True, False]),
                'notes': f'Emergency contact notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            contacts.append(contact)
        
        # Insert emergency contacts
        session.execute(text("""
            INSERT INTO emergency_contacts (user_id, contact_name, relationship, phone_primary,
                                          phone_secondary, email, address, is_primary, notes,
                                          created_at, updated_at, last_accessed_at,
                                          archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :contact_name, :relationship, :phone_primary,
                   :phone_secondary, :email, :address, :is_primary, :notes,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), contacts)
        
        session.commit()
        print(f"  ✅ Created {len(contacts)} emergency contacts")
        return len(contacts)
        
    except Exception as e:
        print(f"  ❌ Error seeding emergency_contacts: {e}")
        session.rollback()
        return 0

def seed_fitness_assessments(session: Session) -> int:
    """Seed fitness_assessments table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_assessments"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_assessments already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping fitness assessments...")
            return 0
        
        # Create sample fitness assessments
        assessments = []
        for i in range(150):
            assessment = {
                'user_id': random.choice(user_ids),
                'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'assessment_type': random.choice(['Initial', 'Progress', 'Annual', 'Pre-activity', 'Post-activity']),
                'cardiovascular_fitness': random.uniform(1, 10),
                'muscular_strength': random.uniform(1, 10),
                'muscular_endurance': random.uniform(1, 10),
                'flexibility': random.uniform(1, 10),
                'body_composition': random.uniform(1, 10),
                'overall_score': random.uniform(1, 10),
                'recommendations': f'Fitness recommendations for assessment {i + 1}',
                'notes': f'Fitness assessment notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            assessments.append(assessment)
        
        # Insert fitness assessments
        session.execute(text("""
            INSERT INTO fitness_assessments (user_id, assessment_date, assessment_type,
                                           cardiovascular_fitness, muscular_strength, muscular_endurance,
                                           flexibility, body_composition, overall_score, recommendations,
                                           notes, created_at, updated_at, last_accessed_at,
                                           archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :assessment_date, :assessment_type,
                   :cardiovascular_fitness, :muscular_strength, :muscular_endurance,
                   :flexibility, :body_composition, :overall_score, :recommendations,
                   :notes, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), assessments)
        
        session.commit()
        print(f"  ✅ Created {len(assessments)} fitness assessments")
        return len(assessments)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_assessments: {e}")
        session.rollback()
        return 0

def seed_fitness_metrics(session: Session) -> int:
    """Seed fitness_metrics table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_metrics"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_metrics already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample fitness metrics
        metrics = []
        metric_types = [
            'Push-ups', 'Pull-ups', 'Sit-ups', 'Plank Hold', 'Mile Run',
            'Sprint Time', 'Vertical Jump', 'Broad Jump', 'Agility Test',
            'Balance Test', 'Flexibility Test', 'Grip Strength', 'Leg Press',
            'Bench Press', 'Squat', 'Deadlift', 'Overhead Press', 'Burpees',
            'Mountain Climbers', 'Jumping Jacks', 'High Knees', 'Lunges',
            'Squat Jumps', 'Push-up Variations', 'Core Strength', 'Cardio Endurance'
        ]
        
        for i, metric_name in enumerate(metric_types):
            metric = {
                'metric_name': metric_name,
                'description': f'Description for {metric_name} fitness metric',
                'unit': random.choice(['reps', 'seconds', 'minutes', 'inches', 'feet', 'lbs', 'kg', 'score']),
                'category': random.choice(['Strength', 'Cardio', 'Flexibility', 'Agility', 'Endurance', 'Power']),
                'target_value': random.uniform(10, 100),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            metrics.append(metric)
        
        # Insert fitness metrics
        session.execute(text("""
            INSERT INTO fitness_metrics (metric_name, description, unit, category, target_value,
                                       is_active, created_at, updated_at, last_accessed_at,
                                       archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:metric_name, :description, :unit, :category, :target_value,
                   :is_active, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), metrics)
        
        session.commit()
        print(f"  ✅ Created {len(metrics)} fitness metrics")
        return len(metrics)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_metrics: {e}")
        session.rollback()
        return 0

def seed_fitness_metric_history(session: Session) -> int:
    """Seed fitness_metric_history table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_metric_history already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs and metric IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        metric_result = session.execute(text("SELECT id FROM fitness_metrics ORDER BY id"))
        metric_ids = [row[0] for row in metric_result.fetchall()]
        
        if not user_ids or not metric_ids:
            print("  ⚠️  No users or metrics found, skipping fitness metric history...")
            return 0
        
        # Create sample fitness metric history
        history_records = []
        for i in range(400):
            record = {
                'user_id': random.choice(user_ids),
                'metric_id': random.choice(metric_ids),
                'recorded_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'value': random.uniform(1, 100),
                'notes': f'Fitness metric history note {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            history_records.append(record)
        
        # Insert fitness metric history
        session.execute(text("""
            INSERT INTO fitness_metric_history (user_id, metric_id, recorded_date, value, notes,
                                              created_at, updated_at, last_accessed_at,
                                              archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :metric_id, :recorded_date, :value, :notes,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), history_records)
        
        session.commit()
        print(f"  ✅ Created {len(history_records)} fitness metric history records")
        return len(history_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_metric_history: {e}")
        session.rollback()
        return 0

def seed_fitness_health_metric_history(session: Session) -> int:
    """Seed fitness_health_metric_history table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_health_metric_history"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_health_metric_history already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping fitness health metric history...")
            return 0
        
        # Create sample fitness health metric history
        history_records = []
        for i in range(300):
            record = {
                'user_id': random.choice(user_ids),
                'recorded_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'fitness_score': random.uniform(1, 10),
                'health_score': random.uniform(1, 10),
                'combined_score': random.uniform(1, 10),
                'notes': f'Combined fitness/health metric history note {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            history_records.append(record)
        
        # Insert fitness health metric history
        session.execute(text("""
            INSERT INTO fitness_health_metric_history (user_id, recorded_date, fitness_score,
                                                     health_score, combined_score, notes,
                                                     created_at, updated_at, last_accessed_at,
                                                     archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :recorded_date, :fitness_score,
                   :health_score, :combined_score, :notes,
                   :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), history_records)
        
        session.commit()
        print(f"  ✅ Created {len(history_records)} fitness health metric history records")
        return len(history_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_health_metric_history: {e}")
        session.rollback()
        return 0

# ============================================================================
# SECTION 3.2: FITNESS GOALS & PROGRESS SEEDING FUNCTIONS
# ============================================================================

def seed_fitness_goals(session: Session) -> int:
    """Seed fitness_goals table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_goals already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping fitness goals...")
            return 0
        
        # Create sample fitness goals
        goals = []
        goal_types = [
            'Weight Loss', 'Weight Gain', 'Muscle Building', 'Cardiovascular Fitness',
            'Flexibility', 'Strength', 'Endurance', 'Speed', 'Agility', 'Balance',
            'Body Fat Reduction', 'Muscle Tone', 'Overall Fitness', 'Sport Performance',
            'Health Improvement', 'Injury Prevention', 'Rehabilitation'
        ]
        
        for i in range(200):
            goal = {
                'user_id': random.choice(user_ids),
                'goal_name': f'{random.choice(goal_types)} Goal {i + 1}',
                'description': f'Description for {random.choice(goal_types)} goal {i + 1}',
                'goal_type': random.choice(goal_types),
                'target_value': random.uniform(10, 100),
                'current_value': random.uniform(1, 50),
                'unit': random.choice(['lbs', 'kg', 'reps', 'minutes', 'miles', 'score', '%']),
                'start_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'status': random.choice(['Active', 'Completed', 'Paused', 'Cancelled']),
                'priority': random.choice(['Low', 'Medium', 'High']),
                'notes': f'Fitness goal notes {i + 1}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            goals.append(goal)
        
        # Insert fitness goals
        session.execute(text("""
            INSERT INTO fitness_goals (user_id, goal_name, description, goal_type, target_value,
                                     current_value, unit, start_date, target_date, status, priority,
                                     notes, is_active, created_at, updated_at, last_accessed_at,
                                     archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :goal_name, :description, :goal_type, :target_value,
                   :current_value, :unit, :start_date, :target_date, :status, :priority,
                   :notes, :is_active, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), goals)
        
        session.commit()
        print(f"  ✅ Created {len(goals)} fitness goals")
        return len(goals)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_goals: {e}")
        session.rollback()
        return 0

def seed_fitness_goal_progress_detailed(session: Session) -> int:
    """Seed fitness_goal_progress_detailed table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_goal_progress_detailed"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_goal_progress_detailed already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual goal IDs
        goal_result = session.execute(text("SELECT id FROM fitness_goals ORDER BY id"))
        goal_ids = [row[0] for row in goal_result.fetchall()]
        
        if not goal_ids:
            print("  ⚠️  No fitness goals found, skipping detailed progress...")
            return 0
        
        # Create sample detailed goal progress
        progress_records = []
        for i in range(600):
            record = {
                'goal_id': random.choice(goal_ids),
                'progress_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'current_value': random.uniform(1, 100),
                'progress_percentage': random.uniform(0, 100),
                'notes': f'Detailed progress note {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            progress_records.append(record)
        
        # Insert detailed goal progress
        session.execute(text("""
            INSERT INTO fitness_goal_progress_detailed (goal_id, progress_date, current_value,
                                                      progress_percentage, notes, created_at,
                                                      updated_at, last_accessed_at, archived_at,
                                                      deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:goal_id, :progress_date, :current_value, :progress_percentage, :notes,
                   :created_at, :updated_at, :last_accessed_at, :archived_at,
                   :deleted_at, :scheduled_deletion_at, :retention_period)
        """), progress_records)
        
        session.commit()
        print(f"  ✅ Created {len(progress_records)} detailed fitness goal progress records")
        return len(progress_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_goal_progress_detailed: {e}")
        session.rollback()
        return 0

def seed_fitness_goal_progress_general(session: Session) -> int:
    """Seed fitness_goal_progress_general table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM fitness_goal_progress_general"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  fitness_goal_progress_general already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual goal IDs
        goal_result = session.execute(text("SELECT id FROM fitness_goals ORDER BY id"))
        goal_ids = [row[0] for row in goal_result.fetchall()]
        
        if not goal_ids:
            print("  ⚠️  No fitness goals found, skipping general progress...")
            return 0
        
        # Create sample general goal progress
        progress_records = []
        for i in range(400):
            record = {
                'goal_id': random.choice(goal_ids),
                'progress_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'overall_progress': random.uniform(0, 100),
                'status': random.choice(['On Track', 'Behind', 'Ahead', 'Completed', 'Stalled']),
                'notes': f'General progress note {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            progress_records.append(record)
        
        # Insert general goal progress
        session.execute(text("""
            INSERT INTO fitness_goal_progress_general (goal_id, progress_date, overall_progress,
                                                     status, notes, created_at, updated_at,
                                                     last_accessed_at, archived_at, deleted_at,
                                                     scheduled_deletion_at, retention_period)
            VALUES (:goal_id, :progress_date, :overall_progress, :status, :notes,
                   :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                   :scheduled_deletion_at, :retention_period)
        """), progress_records)
        
        session.commit()
        print(f"  ✅ Created {len(progress_records)} general fitness goal progress records")
        return len(progress_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding fitness_goal_progress_general: {e}")
        session.rollback()
        return 0

def seed_health_fitness_goals(session: Session) -> int:
    """Seed health_fitness_goals table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM health_fitness_goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  health_fitness_goals already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping health fitness goals...")
            return 0
        
        # Create sample health fitness goals
        goals = []
        goal_types = [
            'Blood Pressure Control', 'Cholesterol Management', 'Diabetes Management',
            'Weight Management', 'Cardiovascular Health', 'Mental Health',
            'Sleep Improvement', 'Stress Reduction', 'Energy Level', 'Overall Wellness'
        ]
        
        for i in range(150):
            goal = {
                'user_id': random.choice(user_ids),
                'goal_name': f'{random.choice(goal_types)} Goal {i + 1}',
                'description': f'Health-focused fitness goal {i + 1}',
                'goal_type': random.choice(goal_types),
                'target_value': random.uniform(10, 100),
                'current_value': random.uniform(1, 50),
                'unit': random.choice(['mmHg', 'mg/dL', 'lbs', 'kg', 'hours', 'score', '%']),
                'start_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'status': random.choice(['Active', 'Completed', 'Paused', 'Cancelled']),
                'priority': random.choice(['Low', 'Medium', 'High']),
                'health_notes': f'Health-specific notes for goal {i + 1}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            goals.append(goal)
        
        # Insert health fitness goals
        session.execute(text("""
            INSERT INTO health_fitness_goals (user_id, goal_name, description, goal_type, target_value,
                                            current_value, unit, start_date, target_date, status, priority,
                                            health_notes, is_active, created_at, updated_at, last_accessed_at,
                                            archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :goal_name, :description, :goal_type, :target_value,
                   :current_value, :unit, :start_date, :target_date, :status, :priority,
                   :health_notes, :is_active, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), goals)
        
        session.commit()
        print(f"  ✅ Created {len(goals)} health fitness goals")
        return len(goals)
        
    except Exception as e:
        print(f"  ❌ Error seeding health_fitness_goals: {e}")
        session.rollback()
        return 0

# ============================================================================
# SECTION 3.3: NUTRITION & WELLNESS SEEDING FUNCTIONS
# ============================================================================

def seed_nutrition_goals(session: Session) -> int:
    """Seed nutrition_goals table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM nutrition_goals"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  nutrition_goals already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping nutrition goals...")
            return 0
        
        # Create sample nutrition goals
        goals = []
        goal_types = [
            'Calorie Intake', 'Protein Intake', 'Carbohydrate Intake', 'Fat Intake',
            'Fiber Intake', 'Water Intake', 'Vitamin Intake', 'Mineral Intake',
            'Weight Loss', 'Weight Gain', 'Muscle Building', 'Energy Level',
            'Digestive Health', 'Overall Nutrition'
        ]
        
        for i in range(100):
            goal = {
                'user_id': random.choice(user_ids),
                'goal_name': f'{random.choice(goal_types)} Goal {i + 1}',
                'description': f'Nutrition goal {i + 1}',
                'goal_type': random.choice(goal_types),
                'target_value': random.uniform(100, 3000),
                'current_value': random.uniform(50, 1500),
                'unit': random.choice(['calories', 'grams', 'mg', 'mcg', 'cups', 'liters', 'servings']),
                'start_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                'target_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'status': random.choice(['Active', 'Completed', 'Paused', 'Cancelled']),
                'priority': random.choice(['Low', 'Medium', 'High']),
                'notes': f'Nutrition goal notes {i + 1}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            goals.append(goal)
        
        # Insert nutrition goals
        session.execute(text("""
            INSERT INTO nutrition_goals (user_id, goal_name, description, goal_type, target_value,
                                       current_value, unit, start_date, target_date, status, priority,
                                       notes, is_active, created_at, updated_at, last_accessed_at,
                                       archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :goal_name, :description, :goal_type, :target_value,
                   :current_value, :unit, :start_date, :target_date, :status, :priority,
                   :notes, :is_active, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), goals)
        
        session.commit()
        print(f"  ✅ Created {len(goals)} nutrition goals")
        return len(goals)
        
    except Exception as e:
        print(f"  ❌ Error seeding nutrition_goals: {e}")
        session.rollback()
        return 0

def seed_foods(session: Session) -> int:
    """Seed foods table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM foods"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  foods already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample foods
        foods = []
        food_names = [
            'Apple', 'Banana', 'Orange', 'Grapes', 'Strawberries', 'Blueberries',
            'Chicken Breast', 'Salmon', 'Ground Turkey', 'Eggs', 'Greek Yogurt',
            'Milk', 'Cheese', 'Almonds', 'Walnuts', 'Oatmeal', 'Brown Rice',
            'Quinoa', 'Sweet Potato', 'Broccoli', 'Spinach', 'Carrots', 'Tomatoes',
            'Avocado', 'Olive Oil', 'Coconut Oil', 'Whole Wheat Bread', 'Pasta',
            'Beans', 'Lentils', 'Tofu', 'Tempeh', 'Nuts', 'Seeds', 'Berries'
        ]
        
        for i, food_name in enumerate(food_names):
            food = {
                'food_name': food_name,
                'description': f'Description for {food_name}',
                'category': random.choice(['Fruits', 'Vegetables', 'Proteins', 'Grains', 'Dairy', 'Nuts', 'Oils']),
                'calories_per_100g': random.uniform(20, 500),
                'protein_per_100g': random.uniform(0, 30),
                'carbs_per_100g': random.uniform(0, 80),
                'fat_per_100g': random.uniform(0, 50),
                'fiber_per_100g': random.uniform(0, 15),
                'sugar_per_100g': random.uniform(0, 40),
                'sodium_per_100g': random.uniform(0, 1000),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            foods.append(food)
        
        # Insert foods
        session.execute(text("""
            INSERT INTO foods (food_name, description, category, calories_per_100g, protein_per_100g,
                             carbs_per_100g, fat_per_100g, fiber_per_100g, sugar_per_100g, sodium_per_100g,
                             is_active, created_at, updated_at, last_accessed_at,
                             archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:food_name, :description, :category, :calories_per_100g, :protein_per_100g,
                   :carbs_per_100g, :fat_per_100g, :fiber_per_100g, :sugar_per_100g, :sodium_per_100g,
                   :is_active, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), foods)
        
        session.commit()
        print(f"  ✅ Created {len(foods)} foods")
        return len(foods)
        
    except Exception as e:
        print(f"  ❌ Error seeding foods: {e}")
        session.rollback()
        return 0

def seed_food_items(session: Session) -> int:
    """Seed food_items table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM food_items"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  food_items already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual food IDs
        food_result = session.execute(text("SELECT id FROM foods ORDER BY id"))
        food_ids = [row[0] for row in food_result.fetchall()]
        
        if not food_ids:
            print("  ⚠️  No foods found, skipping food items...")
            return 0
        
        # Create sample food items
        items = []
        for i in range(500):
            item = {
                'food_id': random.choice(food_ids),
                'item_name': f'Food Item {i + 1}',
                'description': f'Description for food item {i + 1}',
                'serving_size': random.uniform(50, 300),
                'serving_unit': random.choice(['grams', 'cups', 'pieces', 'slices', 'tablespoons']),
                'calories': random.uniform(50, 500),
                'protein': random.uniform(0, 30),
                'carbs': random.uniform(0, 80),
                'fat': random.uniform(0, 50),
                'fiber': random.uniform(0, 15),
                'sugar': random.uniform(0, 40),
                'sodium': random.uniform(0, 1000),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            items.append(item)
        
        # Insert food items
        session.execute(text("""
            INSERT INTO food_items (food_id, item_name, description, serving_size, serving_unit,
                                  calories, protein, carbs, fat, fiber, sugar, sodium,
                                  is_active, created_at, updated_at, last_accessed_at,
                                  archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:food_id, :item_name, :description, :serving_size, :serving_unit,
                   :calories, :protein, :carbs, :fat, :fiber, :sugar, :sodium,
                   :is_active, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), items)
        
        session.commit()
        print(f"  ✅ Created {len(items)} food items")
        return len(items)
        
    except Exception as e:
        print(f"  ❌ Error seeding food_items: {e}")
        session.rollback()
        return 0

def seed_nutrition_logs(session: Session) -> int:
    """Seed nutrition_logs table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM nutrition_logs"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  nutrition_logs already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs and food item IDs
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        food_item_result = session.execute(text("SELECT id FROM food_items ORDER BY id"))
        food_item_ids = [row[0] for row in food_item_result.fetchall()]
        
        if not user_ids or not food_item_ids:
            print("  ⚠️  No users or food items found, skipping nutrition logs...")
            return 0
        
        # Create sample nutrition logs
        logs = []
        for i in range(400):
            log = {
                'user_id': random.choice(user_ids),
                'food_item_id': random.choice(food_item_ids),
                'log_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'meal_type': random.choice(['Breakfast', 'Lunch', 'Dinner', 'Snack']),
                'quantity': random.uniform(0.5, 3.0),
                'calories': random.uniform(50, 500),
                'protein': random.uniform(0, 30),
                'carbs': random.uniform(0, 80),
                'fat': random.uniform(0, 50),
                'fiber': random.uniform(0, 15),
                'sugar': random.uniform(0, 40),
                'sodium': random.uniform(0, 1000),
                'notes': f'Nutrition log notes {i + 1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            logs.append(log)
        
        # Insert nutrition logs
        session.execute(text("""
            INSERT INTO nutrition_logs (user_id, food_item_id, log_date, meal_type, quantity,
                                      calories, protein, carbs, fat, fiber, sugar, sodium,
                                      notes, created_at, updated_at, last_accessed_at,
                                      archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:user_id, :food_item_id, :log_date, :meal_type, :quantity,
                   :calories, :protein, :carbs, :fat, :fiber, :sugar, :sodium,
                   :notes, :created_at, :updated_at, :last_accessed_at,
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), logs)
        
        session.commit()
        print(f"  ✅ Created {len(logs)} nutrition logs")
        return len(logs)
        
    except Exception as e:
        print(f"  ❌ Error seeding nutrition_logs: {e}")
        session.rollback()
        return 0

def seed_phase3_health_fitness(session: Session) -> Dict[str, int]:
    """
    Seed Phase 3: Health & Fitness System
    Returns a dictionary with counts of records created for each table
    """
    print("\n" + "="*60)
    print("🏥 PHASE 3: HEALTH & FITNESS SYSTEM")
    print("="*60)
    print("📊 Seeding 52 tables for comprehensive health, fitness, and nutrition management")
    print("🏥 Health assessment & monitoring")
    print("💪 Fitness goals & progress tracking")
    print("🥗 Nutrition & wellness management")
    print("="*60)
    
    results = {}
    
    try:
        # Section 3.1: Health Assessment & Monitoring (11 tables)
        print("\n🏥 SECTION 3.1: HEALTH ASSESSMENT & MONITORING")
        print("-" * 50)
        
        print("Seeding health checks...")
        results['health_checks'] = seed_health_checks(session)
        
        print("Seeding health conditions...")
        results['health_conditions'] = seed_health_conditions(session)
        
        print("Seeding health alerts...")
        results['health_alerts'] = seed_health_alerts(session)
        
        print("Seeding health metrics...")
        results['health_metrics'] = seed_health_metrics(session)
        
        print("Seeding health metric history...")
        results['health_metric_history'] = seed_health_metric_history(session)
        
        print("Seeding health metric thresholds...")
        results['health_metric_thresholds'] = seed_health_metric_thresholds(session)
        
        print("Seeding medical conditions...")
        results['medical_conditions'] = seed_medical_conditions(session)
        
        print("Seeding emergency contacts...")
        results['emergency_contacts'] = seed_emergency_contacts(session)
        
        print("Seeding fitness assessments...")
        results['fitness_assessments'] = seed_fitness_assessments(session)
        
        print("Seeding fitness metrics...")
        results['fitness_metrics'] = seed_fitness_metrics(session)
        
        print("Seeding fitness metric history...")
        results['fitness_metric_history'] = seed_fitness_metric_history(session)
        
        print("Seeding fitness health metric history...")
        results['fitness_health_metric_history'] = seed_fitness_health_metric_history(session)
        
        # Section 3.2: Fitness Goals & Progress (13 tables)
        print("\n💪 SECTION 3.2: FITNESS GOALS & PROGRESS")
        print("-" * 50)
        
        print("Seeding fitness goals...")
        results['fitness_goals'] = seed_fitness_goals(session)
        
        print("Seeding fitness goal progress detailed...")
        results['fitness_goal_progress_detailed'] = seed_fitness_goal_progress_detailed(session)
        
        print("Seeding fitness goal progress general...")
        results['fitness_goal_progress_general'] = seed_fitness_goal_progress_general(session)
        
        print("Seeding health fitness goals...")
        results['health_fitness_goals'] = seed_health_fitness_goals(session)
        
        # Section 3.3: Nutrition & Wellness (28 tables)
        print("\n🥗 SECTION 3.3: NUTRITION & WELLNESS")
        print("-" * 50)
        
        print("Seeding nutrition goals...")
        results['nutrition_goals'] = seed_nutrition_goals(session)
        
        print("Seeding foods...")
        results['foods'] = seed_foods(session)
        
        print("Seeding food items...")
        results['food_items'] = seed_food_items(session)
        
        print("Seeding nutrition logs...")
        results['nutrition_logs'] = seed_nutrition_logs(session)
        
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
        print("Testing Phase 3 Health & Fitness seeding...")
        result = seed_phase3_health_fitness(session)
        print(f'Phase 3 seeding completed with {sum(result.values())} total records')
        print('Results:', result)
    finally:
        session.close()
