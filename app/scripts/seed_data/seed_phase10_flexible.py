"""
Phase 10: Assessment & Skill Management System - FLEXIBLE VERSION
================================================================
Comprehensive assessment and skill tracking system
30 tables covering skill assessments, general assessments, and safety/risk management

FLEXIBLE APPROACH FOR DEVELOPMENT DATABASE REGENERATION
- Dynamic schema detection
- Robust foreign key handling with fallbacks
- Graceful error handling for missing tables/columns
- Adapts to schema changes automatically

Priority: HIGH
Estimated Time: 40 minutes
Target: 30 tables with proper scaling for 4,000+ student district
"""

import random
import json
from datetime import datetime, timedelta
from sqlalchemy import text
from app.core.database import SessionLocal


def get_table_schema(session, table_name):
    """Get the actual schema for a table dynamically"""
    try:
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            ORDER BY ordinal_position
        """), {'table_name': table_name})
        return {row[0]: {'type': row[1], 'nullable': row[2] == 'YES'} for row in result.fetchall()}
    except:
        return {}


def get_table_ids_safe(session, table_name, limit):
    """Safely get IDs from a table with fallback"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name} LIMIT {limit}"))
        ids = [row[0] for row in result.fetchall()]
        return ids if ids else list(range(1, limit + 1))
    except:
        return list(range(1, limit + 1))


def safe_insert_data(session, table_name, data_list, batch_size=100):
    """Safely insert data with dynamic schema detection"""
    if not data_list:
        return 0
    
    try:
        # Get table schema
        schema = get_table_schema(session, table_name)
        if not schema:
            print(f"  ⚠️ Table {table_name} not found or no schema")
            return 0
        
        # Get the first data item to determine columns
        sample_data = data_list[0]
        available_columns = [col for col in sample_data.keys() if col in schema]
        
        if not available_columns:
            print(f"  ⚠️ No matching columns found for {table_name}")
            return 0
        
        # Build dynamic INSERT statement
        columns_str = ', '.join(available_columns)
        values_str = ', '.join([f':{col}' for col in available_columns])
        
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        
        # Insert in batches
        total_inserted = 0
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            for item in batch:
                # Filter data to only include available columns
                filtered_item = {k: v for k, v in item.items() if k in available_columns}
                session.execute(text(insert_sql), filtered_item)
            total_inserted += len(batch)
            
            if len(data_list) > batch_size:
                print(f"    📊 Processed {min(i+batch_size, len(data_list))}/{len(data_list)} records...")
        
        return total_inserted
    except Exception as e:
        print(f"  ⚠️ Error inserting into {table_name}: {e}")
        return 0


def check_table_exists(session, table_name):
    """Check if a table exists"""
    try:
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = :table_name
            )
        """), {'table_name': table_name})
        return result.scalar()
    except Exception as e:
        print(f"  ⚠️ Error checking table {table_name}: {e}")
        return False


def seed_phase10_assessment_skill_management(session):
    """
    Seed Phase 10: Assessment & Skill Management System
    Creates 30 tables for comprehensive assessment and skill tracking
    Flexible approach for development database regeneration
    """
    print("\n" + "="*80)
    print("🎯 PHASE 10: ASSESSMENT & SKILL MANAGEMENT SYSTEM (FLEXIBLE)")
    print("="*80)
    print("📊 Seeding comprehensive assessment and skill tracking system")
    print("🎯 Flexible approach for development database regeneration")
    print("🎯 Properly scaled for 4,000+ student district")
    print("="*80)
    
    try:
        # Track successful table seeding
        successful_tables = 0
        total_tables = 30  # Total tables this script attempts to seed
        
        # Get dependency IDs with fallbacks
        print("🔍 Retrieving dependency IDs...")
        
        # Get students, users, activities, assessments with fallbacks
        student_ids = get_table_ids_safe(session, "students", 100)
        user_ids = get_table_ids_safe(session, "users", 50)
        activity_ids = get_table_ids_safe(session, "activities", 100)
        assessment_ids = get_table_ids_safe(session, "skill_assessment_skill_assessments", 50)
        
        # Fallback to general_assessments if skill_assessment_skill_assessments doesn't exist
        if not assessment_ids:
            assessment_ids = get_table_ids_safe(session, "general_assessments", 50)
        
        print(f"✅ Retrieved dependency IDs: {len(user_ids)} users, {len(student_ids)} students, {len(activity_ids)} activities, {len(assessment_ids)} assessments")
        
        # Define all 30 Phase 10 tables with their seeding functions
        phase10_tables = [
            # Skill Assessment System (10 tables)
            ('skill_assessment_assessment_metrics', seed_skill_assessment_metrics),
            ('skill_assessment_assessments', seed_skill_assessment_assessments),
            ('skill_assessment_risk_assessments', seed_skill_assessment_risk_assessments),
            ('skill_assessment_safety_alerts', seed_skill_assessment_safety_alerts),
            ('skill_assessment_safety_incidents', seed_skill_assessment_safety_incidents),
            ('skill_assessment_safety_protocols', seed_skill_assessment_safety_protocols),
            ('skill_assessment_assessment_criteria', seed_skill_assessment_criteria),
            ('skill_assessment_assessment_history', seed_skill_assessment_history),
            ('skill_assessment_assessment_results', seed_skill_assessment_results),
            ('skill_assessment_skill_assessments', seed_skill_assessment_skill_assessments),
            
            # General Assessment System (5 tables)
            ('general_assessment_criteria', seed_general_assessment_criteria),
            ('general_assessment_history', seed_general_assessment_history),
            ('general_assessments', seed_general_assessments),
            ('general_skill_assessments', seed_general_skill_assessments),
            ('student_health_skill_assessments', seed_student_health_skill_assessments),
            
            # Movement Analysis System (4 tables)
            ('movement_analysis_analyses', seed_movement_analysis_analyses),
            ('movement_analysis_metrics', seed_movement_analysis_metrics),
            ('movement_analysis_patterns', seed_movement_analysis_patterns),
            ('physical_education_movement_analysis', seed_physical_education_movement_analysis),
            
            # Safety & Risk Management (8 tables)
            ('safety', seed_safety),
            ('safety_incident_base', seed_safety_incident_base),
            ('safety_incidents', seed_safety_incidents),
            ('safety_guidelines', seed_safety_guidelines),
            ('safety_protocols', seed_safety_protocols),
            ('safety_reports', seed_safety_reports),
            ('safety_measures', seed_safety_measures),
            ('safety_checklists', seed_safety_checklists),
            
            # Injury Prevention & Activity Management (3 tables)
            ('activity_injury_preventions', seed_activity_injury_preventions),
            ('injury_preventions', seed_injury_preventions),
            ('activity_logs', seed_activity_logs)
        ]
        
        # Seed each table
        for table_name, seed_function in phase10_tables:
            print(f"\n📊 Seeding {table_name}...")
            try:
                if check_table_exists(session, table_name):
                    # Check if table already has data
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    if result.scalar() > 0:
                        print(f"  ✅ {table_name} already has data")
                        successful_tables += 1
                    else:
                        # Seed the table
                        if seed_function(session, student_ids, user_ids, activity_ids, assessment_ids):
                            successful_tables += 1
                else:
                    print(f"  ⚠️ Table {table_name} does not exist, skipping")
            except Exception as e:
                print(f"  ⚠️ {table_name}: {e}")
        
        print(f"\n🎉 Phase 10 Assessment & Skill Management: {successful_tables}/{total_tables} tables populated")
        print(f"📊 Total tables processed: {total_tables}")
        print(f"✅ Successfully populated {successful_tables} working tables")
        if successful_tables == total_tables:
            print("✅ Phase 10 assessment & skill management completed successfully!")
        else:
            print(f"⚠️ Phase 10 partially completed - {total_tables - successful_tables} tables failed")
        
        return successful_tables == total_tables
        
    except Exception as e:
        print(f"❌ Error in Phase 10: {e}")
        return False


# Seeding functions for each table
def seed_skill_assessment_metrics(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_assessment_metrics table"""
    data = []
    for i in range(100):
        data.append({
            'assessment_id': random.choice(assessment_ids),
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'recent_average': random.uniform(60, 100),
            'historical_average': random.uniform(50, 95),
            'trend': random.uniform(-5, 10),  # Numeric trend value
            'volatility': random.uniform(0, 20),
            'improvement_rate': random.uniform(0, 15),
            'performance_level': random.choice(['excellent', 'good', 'average', 'needs_improvement', 'poor']),
            'progress_level': random.choice(['rapid', 'steady', 'slow', 'no_progress', 'declining']),
            'metrics_data': json.dumps({
                'accuracy': random.uniform(70, 100),
                'speed': random.uniform(60, 100),
                'consistency': random.uniform(65, 100),
                'effort': random.uniform(70, 100)
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_assessment_metrics', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} skill assessment metrics")
        return True
    return False


def seed_skill_assessment_assessments(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_assessments table"""
    data = []
    for i in range(1000):
        data.append({
            'student_id': random.choice(student_ids),
            'assessor_id': random.choice(user_ids),
            'curriculum_id': random.randint(1, 5),
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'assessment_type': random.choice(['SKILL', 'FITNESS', 'MOVEMENT', 'BEHAVIORAL', 'PROGRESS']),
            'score': random.uniform(0, 100),
            'notes': f'Assessment notes for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
            'assessment_metadata': json.dumps({
                'duration_minutes': random.randint(15, 120),
                'environment': random.choice(['Classroom', 'Gym', 'Lab', 'Outdoor']),
                'difficulty_level': random.choice(['Easy', 'Medium', 'Hard', 'Expert'])
            }),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_assessments', data, 200)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} skill assessments")
        return True
    return False


def seed_skill_assessment_risk_assessments(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_risk_assessments table"""
    data = []
    for i in range(500):
        data.append({
            'activity_id': random.choice(activity_ids),
            'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'factors': json.dumps({
                'environmental': random.choice(['Safe', 'Moderate', 'Risky']),
                'equipment': random.choice(['Good', 'Fair', 'Poor']),
                'supervision': random.choice(['Adequate', 'Limited', 'Minimal'])
            }),
            'mitigation_measures': json.dumps([
                f'Measure {j+1}' for j in range(random.randint(1, 3))
            ]),
            'environmental_conditions': json.dumps({
                'type': random.choice(['Indoor', 'Outdoor', 'Mixed']),
                'temperature': random.choice(['Cold', 'Moderate', 'Warm', 'Hot']),
                'humidity': random.choice(['Low', 'Moderate', 'High'])
            }),
            'equipment_status': json.dumps({
                'status': random.choice(['Good', 'Fair', 'Needs attention']),
                'last_inspected': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'condition_notes': f'Equipment condition notes for activity {random.choice(activity_ids)}'
            }),
            'student_health_considerations': json.dumps({
                'level': random.choice(['None', 'Minor', 'Moderate', 'Significant']),
                'notes': f'Health considerations for student assessment',
                'requires_attention': random.choice([True, False])
            }),
            'weather_conditions': json.dumps({
                'condition': random.choice(['Clear', 'Cloudy', 'Rainy', 'Windy']),
                'temperature': random.randint(60, 85),
                'humidity': random.randint(30, 90)
            }),
            'assessed_by': random.choice(user_ids),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_risk_assessments', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} risk assessments")
        return True
    return False


def seed_skill_assessment_safety_alerts(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_safety_alerts table"""
    data = []
    for i in range(200):
        data.append({
            'alert_type': random.choice(['RISK_THRESHOLD', 'EMERGENCY', 'PROTOCOL', 'MAINTENANCE', 'WEATHER']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'message': f'Safety alert for activity {random.choice(activity_ids)}: {random.choice(["Equipment check required", "Environmental assessment needed", "Supervision level critical", "Medical clearance required"])}',
            'recipients': json.dumps({
                'teachers': [f'Teacher {j}' for j in range(random.randint(1, 3))],
                'administrators': [f'Admin {j}' for j in range(random.randint(1, 2))],
                'parents': [f'Parent {j}' for j in range(random.randint(0, 2))]
            }),
            'activity_id': random.choice(activity_ids),
            'equipment_id': random.randint(1, 25) if random.choice([True, False]) else None,
            'resolved_at': datetime.now() + timedelta(days=random.randint(1, 14)) if random.choice([True, False]) else None,
            'resolution_notes': f'Resolution notes: {random.choice(["Equipment replaced", "Supervision increased", "Activity modified", "Medical attention provided"])}' if random.choice([True, False]) else None,
            'created_by': random.choice(user_ids),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_safety_alerts', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety alerts")
        return True
    return False


def seed_skill_assessment_safety_incidents(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_safety_incidents table"""
    data = []
    for i in range(100):
        data.append({
            'activity_id': random.choice(activity_ids),
            'student_id': random.choice(student_ids),
            'safety_id': None,  # Make optional since safety table might be empty
            'incident_type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL', 'BEHAVIORAL']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'description': f'Detailed incident report for student {random.choice(student_ids)} - {random.choice(["Minor scrape during activity", "Equipment stopped working", "Student became agitated", "Medical attention required"])}',
            'response_taken': f'Response: {random.choice(["First aid applied", "Equipment replaced", "Student calmed", "Medical team called"])}',
            'reported_by': random.choice(user_ids),
            'location': random.choice(['Classroom A', 'Gymnasium', 'Playground', 'Lab', 'Office']),
            'equipment_involved': json.dumps([f'Equipment {j}' for j in range(random.randint(0, 2))]),
            'witnesses': json.dumps([f'Witness {j}' for j in range(random.randint(1, 2))]),
            'follow_up_required': random.choice([True, False]),
            'follow_up_notes': f'Follow-up notes: {random.choice(["Additional training", "Equipment check", "Supervision increased", "Protocol updated"])}' if random.choice([True, False]) else None,
            'date': datetime.now() - timedelta(days=random.randint(1, 60)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_safety_incidents', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety incidents")
        return True
    return False


def seed_skill_assessment_safety_protocols(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_safety_protocols table"""
    data = []
    for i in range(150):
        data.append({
            'description': f'Comprehensive safety protocol for {random.choice(["equipment use", "environmental safety", "behavioral management", "medical emergencies", "emergency response"])}',
            'activity_type': random.choice(['PHYSICAL_EDUCATION', 'SPORTS', 'RECREATION', 'FITNESS', 'MOVEMENT']),
            'protocol_type': random.choice(['EMERGENCY', 'PREVENTIVE', 'MAINTENANCE', 'TRAINING', 'ASSESSMENT']),
            'steps': json.dumps([
                f'Step {j+1}: {random.choice(["Check equipment", "Assess environment", "Monitor behavior", "Verify medical clearance", "Confirm emergency contacts"])}'
                for j in range(random.randint(3, 8))
            ]),
            'required_equipment': json.dumps([f'Equipment {j+1}' for j in range(random.randint(2, 5))]),
            'emergency_contacts': json.dumps({
                'primary': f'Primary Contact {random.randint(1, 3)}',
                'secondary': f'Secondary Contact {random.randint(1, 3)}',
                'medical': f'Medical Contact {random.randint(1, 2)}'
            }),
            'created_by': random.choice(user_ids),
            'safety_id': None,  # Make optional since safety table might be empty
            'last_reviewed': datetime.now() - timedelta(days=random.randint(1, 90)),
            'next_review': datetime.now() + timedelta(days=random.randint(30, 180)),
            'created_at': datetime.now() - timedelta(days=random.randint(30, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_safety_protocols', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety protocols")
        return True
    return False


# Continue with remaining seeding functions...
def seed_skill_assessment_criteria(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_assessment_criteria table"""
    data = []
    for i in range(100):
        data.append({
            'assessment_id': random.randint(1, 50),
            'criteria_name': f'Assessment Criteria {i+1}',
            'criteria_type': random.choice(['TECHNICAL', 'PERFORMANCE', 'PROGRESS', 'SAFETY']),
            'description': f'Assessment criteria for skill evaluation {i+1}',
            'max_score': random.randint(10, 100),
            'weight': random.uniform(0.1, 1.0),
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_assessment_criteria', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} assessment criteria")
        return True
    return False


def seed_skill_assessment_history(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_assessment_history table"""
    data = []
    for i in range(500):
        data.append({
            'assessment_id': random.randint(1, 50),
            'student_id': random.choice(student_ids),
            'assessor_id': random.choice(user_ids),
            'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'REVIEWED', 'ARCHIVED']),
            'score': random.uniform(0, 100),
            'feedback': f'Assessment feedback for student {random.choice(student_ids)}: {random.choice(["Excellent progress", "Needs improvement", "On track", "Requires attention"])}',
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'completion_date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_assessment_history', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} assessment history records")
        return True
    return False


def seed_skill_assessment_results(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_assessment_results table"""
    data = []
    for i in range(300):
        data.append({
            'assessment_id': random.randint(1, 50),
            'student_id': random.choice(student_ids),
            'score': random.uniform(0, 100),
            'max_score': 100,
            'grade': random.choice(['A', 'B', 'C', 'D', 'F']),
            'feedback': f'Assessment result for student {random.choice(student_ids)}: {random.choice(["Outstanding", "Good", "Satisfactory", "Needs improvement"])}',
            'completed_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_assessment_results', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} assessment results")
        return True
    return False


def seed_skill_assessment_skill_assessments(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed skill_assessment_skill_assessments table"""
    data = []
    for i in range(200):
        data.append({
            'student_id': random.choice(student_ids),
            'skill_id': random.randint(1, 50),
            'assessor_id': random.choice(user_ids),
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'score': random.uniform(0, 100),
            'level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
            'notes': f'Skill assessment for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'skill_assessment_skill_assessments', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} skill assessments")
        return True
    return False


# General Assessment System functions
def seed_general_assessment_criteria(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed general_assessment_criteria table"""
    data = []
    for i in range(200):
        data.append({
            'assessment_id': random.randint(1, 50),
            'type': random.choice(['TECHNICAL', 'PERFORMANCE', 'PROGRESS', 'SAFETY']),
            'score': random.uniform(0, 100),
            'feedback': f'Assessment feedback for criteria {i+1}: {random.choice(["Excellent progress", "Needs improvement", "On track", "Requires attention"])}',
            'meta_data': json.dumps({
                'level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                'weight': random.uniform(0.1, 1.0),
                'max_score': random.randint(10, 100),
                'evaluation_notes': f'Evaluation notes for criteria {i+1}'
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'general_assessment_criteria', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} assessment criteria")
        return True
    return False


def seed_general_assessment_history(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed general_assessment_history table"""
    data = []
    for i in range(2000):
        data.append({
            'assessment_id': random.randint(1, 50),
            'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED']),
            'score': random.uniform(0, 100),
            'feedback': f'Assessment feedback for history record {i+1}: {random.choice(["Excellent work", "Good progress", "Needs improvement", "Outstanding performance", "Requires attention"])}',
            'criteria_results': json.dumps({
                'criteria_1': random.uniform(0, 100),
                'criteria_2': random.uniform(0, 100),
                'criteria_3': random.uniform(0, 100),
                'overall_score': random.uniform(0, 100)
            }),
            'meta_data': json.dumps({
                'duration_minutes': random.randint(15, 120),
                'environment': random.choice(['Classroom', 'Gym', 'Lab', 'Outdoor', 'Online']),
                'difficulty_level': random.choice(['Easy', 'Medium', 'Hard', 'Expert']),
                'attempts': random.randint(1, 3),
                'improvement_areas': [f'Area {j}' for j in range(random.randint(1, 3))]
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'general_assessment_history', data, 200)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} assessment history records")
        return True
    return False


def seed_general_assessments(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed general_assessments table"""
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'assessor_id': random.choice(user_ids),
            'assessment_type': random.choice(['FORMATIVE', 'SUMMATIVE', 'DIAGNOSTIC', 'PLACEMENT']),
            'title': f'General Assessment {i+1}',
            'description': f'Assessment description for student {random.choice(student_ids)}',
            'score': random.uniform(0, 100),
            'max_score': 100,
            'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED']),
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'general_assessments', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} general assessments")
        return True
    return False


def seed_general_skill_assessments(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed general_skill_assessments table"""
    data = []
    for i in range(150):
        data.append({
            'student_id': random.choice(student_ids),
            'skill_name': f'Skill {i+1}',
            'skill_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'score': random.uniform(0, 100),
            'notes': f'General skill assessment for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'general_skill_assessments', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} general skill assessments")
        return True
    return False


def seed_student_health_skill_assessments(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed student_health_skill_assessments table"""
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'health_skill': f'Health Skill {i+1}',
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'score': random.uniform(0, 100),
            'notes': f'Health skill assessment for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'student_health_skill_assessments', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} student health skill assessments")
        return True
    return False


# Movement Analysis System functions
def seed_movement_analysis_analyses(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed movement_analysis_analyses table"""
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'analysis_type': random.choice(['RUNNING', 'JUMPING', 'THROWING', 'CATCHING']),
            'score': random.uniform(0, 100),
            'notes': f'Movement analysis for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'movement_analysis_analyses', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} movement analyses")
        return True
    return False


def seed_movement_analysis_metrics(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed movement_analysis_metrics table"""
    data = []
    for i in range(200):
        data.append({
            'analysis_id': random.randint(1, 100),
            'metric_name': f'Movement Metric {i+1}',
            'metric_value': random.uniform(0, 100),
            'unit': random.choice(['seconds', 'meters', 'degrees', 'count']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'movement_analysis_metrics', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} movement analysis metrics")
        return True
    return False


def seed_movement_analysis_patterns(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed movement_analysis_patterns table"""
    data = []
    for i in range(150):
        data.append({
            'analysis_id': random.randint(1, 100),
            'pattern_name': f'Movement Pattern {i+1}',
            'pattern_type': random.choice(['GAIT', 'POSTURE', 'COORDINATION', 'BALANCE']),
            'confidence': random.uniform(0, 1),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'movement_analysis_patterns', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} movement analysis patterns")
        return True
    return False


def seed_physical_education_movement_analysis(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed physical_education_movement_analysis table"""
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'analysis_type': random.choice(['RUNNING', 'JUMPING', 'THROWING', 'CATCHING']),
            'score': random.uniform(0, 100),
            'notes': f'PE movement analysis for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'physical_education_movement_analysis', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} physical education movement analyses")
        return True
    return False


# Safety & Risk Management functions
def seed_safety(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety table"""
    data = []
    for i in range(300):
        data.append({
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'status': random.choice(['OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED']),
            'incident_type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL', 'BEHAVIORAL']),
            'description': f'Safety record for student {random.choice(student_ids)}: {random.choice(["Minor incident", "Equipment issue", "Environmental concern"])}',
            'reported_by': random.choice(user_ids),
            'incident_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety records")
        return True
    return False


def seed_safety_incident_base(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_incident_base table"""
    data = []
    for i in range(200):
        data.append({
            'type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL']),
            'incident_type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'description': f'Base safety incident {i+1}: {random.choice(["Minor injury", "Equipment issue", "Environmental concern"])}',
            'location': random.choice(['Classroom A', 'Gymnasium', 'Playground', 'Lab', 'Office', 'Outdoor Field']),
            'teacher_id': random.choice(user_ids),
            'action_taken': f'Action taken for incident {i+1}: {random.choice(["First aid applied", "Equipment replaced", "Student calmed", "Medical attention provided", "Supervision increased"])}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_incident_base', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety incident base records")
        return True
    return False


def seed_safety_incidents(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_incidents table"""
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'incident_type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'description': f'Safety incident for student {random.choice(student_ids)}: {random.choice(["Minor injury", "Equipment issue", "Environmental concern"])}',
            'reported_by': random.choice(user_ids),
            'incident_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_incidents', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety incidents")
        return True
    return False


def seed_safety_guidelines(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_guidelines table"""
    data = []
    for i in range(50):
        data.append({
            'guideline_name': f'Safety Guideline {i+1}',
            'guideline_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'BEHAVIOR', 'EMERGENCY']),
            'description': f'Safety guideline for {random.choice(["equipment use", "environmental safety", "behavioral management", "emergency response"])}',
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_guidelines', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety guidelines")
        return True
    return False


def seed_safety_protocols(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_protocols table"""
    data = []
    for i in range(75):
        data.append({
            'protocol_name': f'Safety Protocol {i+1}',
            'protocol_type': random.choice(['EMERGENCY', 'PREVENTIVE', 'MAINTENANCE', 'TRAINING']),
            'description': f'Safety protocol for {random.choice(["emergency response", "preventive measures", "equipment maintenance", "staff training"])}',
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_protocols', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety protocols")
        return True
    return False


def seed_safety_reports(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_reports table"""
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'report_type': random.choice(['INCIDENT', 'INSPECTION', 'AUDIT', 'MAINTENANCE']),
            'description': f'Safety report for student {random.choice(student_ids)}: {random.choice(["Incident report", "Inspection report", "Audit report", "Maintenance report"])}',
            'reported_by': random.choice(user_ids),
            'report_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_reports', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety reports")
        return True
    return False


def seed_safety_measures(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_measures table"""
    data = []
    for i in range(80):
        data.append({
            'measure_name': f'Safety Measure {i+1}',
            'measure_type': random.choice(['PREVENTIVE', 'PROTECTIVE', 'EMERGENCY', 'TRAINING']),
            'description': f'Safety measure for {random.choice(["prevention", "protection", "emergency response", "training"])}',
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_measures', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety measures")
        return True
    return False


def seed_safety_checklists(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed safety_checklists table"""
    data = []
    for i in range(60):
        data.append({
            'checklist_name': f'Safety Checklist {i+1}',
            'checklist_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'ACTIVITY', 'EMERGENCY']),
            'description': f'Safety checklist for {random.choice(["equipment inspection", "environmental assessment", "activity preparation", "emergency procedures"])}',
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'safety_checklists', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} safety checklists")
        return True
    return False


# Injury Prevention & Activity Management functions
def seed_activity_injury_preventions(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed activity_injury_preventions table"""
    data = []
    for i in range(150):
        data.append({
            'activity_id': random.choice(activity_ids),
            'prevention_type': random.choice(['EQUIPMENT', 'TRAINING', 'ENVIRONMENT', 'BEHAVIOR']),
            'description': f'Injury prevention for activity {random.choice(activity_ids)}: {random.choice(["Equipment safety", "Training protocols", "Environmental control", "Behavioral management"])}',
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'activity_injury_preventions', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} activity injury preventions")
        return True
    return False


def seed_injury_preventions(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed injury_preventions table"""
    data = []
    for i in range(100):
        data.append({
            'prevention_name': f'Injury Prevention {i+1}',
            'prevention_type': random.choice(['EQUIPMENT', 'TRAINING', 'ENVIRONMENT', 'BEHAVIOR']),
            'description': f'Injury prevention measure for {random.choice(["equipment safety", "training protocols", "environmental control", "behavioral management"])}',
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'injury_preventions', data)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} injury preventions")
        return True
    return False


def seed_activity_logs(session, student_ids, user_ids, activity_ids, assessment_ids):
    """Seed activity_logs table"""
    data = []
    for i in range(2000):
        data.append({
            'student_id': random.choice(student_ids),
            'activity_id': random.choice(activity_ids),
            'log_type': random.choice(['PARTICIPATION', 'PERFORMANCE', 'INCIDENT', 'OBSERVATION']),
            'description': f'Activity log for student {random.choice(student_ids)}: {random.choice(["Participated in activity", "Showed good performance", "Minor incident occurred", "Observation noted"])}',
            'logged_by': random.choice(user_ids),
            'log_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    inserted_count = safe_insert_data(session, 'activity_logs', data, 200)
    if inserted_count > 0:
        print(f"  ✅ Created {inserted_count} activity logs")
        return True
    return False


if __name__ == "__main__":
    session = SessionLocal()
    try:
        success = seed_phase10_assessment_skill_management(session)
        if success:
            print("🎉 Phase 10 completed successfully!")
        else:
            print("❌ Phase 10 failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()
