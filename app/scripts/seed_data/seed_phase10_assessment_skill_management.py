"""
Phase 10: Assessment & Skill Management System
=============================================
Comprehensive assessment and skill tracking system
30 tables covering skill assessments, general assessments, and safety/risk management

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

def get_table_ids_safe(session, table_name, limit):
    """Safely get IDs from a table with fallback"""
    try:
        # First check if table exists
        result = session.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print(f"  ⚠️ Table {table_name} does not exist, using fallback IDs")
            return list(range(1, limit + 1))
        
        result = session.execute(text(f"SELECT id FROM {table_name} LIMIT {limit}"))
        ids = [row[0] for row in result.fetchall()]
        return ids if ids else list(range(1, limit + 1))
    except Exception as e:
        print(f"  ⚠️ Error getting IDs from {table_name}: {e}")
        return list(range(1, limit + 1))

def insert_data_flexible(session, table_name, data, schema, batch_size=100):
    """Insert data with flexible schema handling"""
    if not data:
        return 0
    
    try:
        # Filter data to only include columns that exist
        available_columns = set(schema.keys())
        filtered_data = []
        for item in data:
            filtered_item = {k: v for k, v in item.items() if k in available_columns}
            filtered_data.append(filtered_item)
        
        if not filtered_data:
            print(f"  ⚠️ No valid columns found for {table_name}")
            return 0
        
        # Insert in batches
        total_inserted = 0
        for i in range(0, len(filtered_data), batch_size):
            batch = filtered_data[i:i + batch_size]
            if not batch:
                continue
                
            # Build dynamic INSERT statement
            columns = list(batch[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            for item in batch:
                session.execute(text(insert_sql), item)
            total_inserted += len(batch)
        
        return total_inserted
    except Exception as e:
        print(f"  ⚠️ Error inserting into {table_name}: {e}")
        return 0

def recover_transaction(session):
    """Recover from failed transaction by rolling back and starting fresh"""
    try:
        session.rollback()
        print("  🔄 Transaction rolled back, continuing...")
        return True
    except Exception as e:
        print(f"  ❌ Failed to rollback transaction: {e}")
        return False

def safe_execute_with_savepoint(session, operation_name, operation_func):
    """Execute an operation in a savepoint so failures don't abort the entire transaction"""
    savepoint = session.begin_nested()
    try:
        result = operation_func()
        savepoint.commit()
        return result
    except Exception as e:
        savepoint.rollback()
        print(f"  ⚠️ {operation_name}: {e}")
        return None

def seed_phase10_assessment_skill_management(session):
    """
    Seed Phase 10: Assessment & Skill Management System
    Creates 30 tables for comprehensive assessment and skill tracking
    Flexible approach for development database regeneration
    """
    print("\n" + "="*80)
    print("🎯 PHASE 10: ASSESSMENT & SKILL MANAGEMENT SYSTEM")
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
        
        # Get students, users, activities, assessments, curriculum with fallbacks
        student_ids = get_table_ids_safe(session, "students", 100)
        user_ids = get_table_ids_safe(session, "users", 50)
        activity_ids = get_table_ids_safe(session, "activities", 100)
        curriculum_ids = get_table_ids_safe(session, "curriculum", 10)
        assessment_ids = get_table_ids_safe(session, "skill_assessment_skill_assessments", 50)
        
        # Fallback to general_assessments if skill_assessment_skill_assessments doesn't exist
        if not assessment_ids:
            assessment_ids = get_table_ids_safe(session, "general_assessments", 50)
        
        print(f"✅ Retrieved dependency IDs: {len(user_ids)} users, {len(student_ids)} students, {len(activity_ids)} activities, {len(curriculum_ids)} curriculum, {len(assessment_ids)} assessments")
        
        # 10.1 SKILL ASSESSMENT SYSTEM (6 tables)
        print("\n📊 10.1 SKILL ASSESSMENT SYSTEM")
        print("-" * 50)
        
        # skill_assessment_assessment_metrics
        print("  Seeding skill_assessment_assessment_metrics...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_assessment_metrics"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_assessment_metrics already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                metrics_data = []
                for i in range(100):
                    recent_avg = random.uniform(60, 95)
                    historical_avg = random.uniform(55, 90)
                    trend = random.uniform(-5, 10)
                    volatility = random.uniform(0.1, 2.0)
                    improvement_rate = random.uniform(0.5, 3.0)
                    
                    metrics_data.append({
                        'assessment_id': random.choice(assessment_ids) if assessment_ids else None,
                        'student_id': random.choice(student_ids),
                        'activity_id': random.choice(activity_ids),
                        'recent_average': recent_avg,
                        'historical_average': historical_avg,
                        'trend': trend,
                        'volatility': volatility,
                        'improvement_rate': improvement_rate,
                        'performance_level': random.choice(['excellent', 'good', 'average', 'needs_improvement', 'poor']),
                        'progress_level': random.choice(['rapid', 'steady', 'slow', 'no_progress', 'declining']),
                        'metrics_data': json.dumps({
                            'assessment_type': random.choice(['SKILL', 'FITNESS', 'MOVEMENT', 'BEHAVIORAL', 'PROGRESS']),
                            'evaluation_criteria': ['technical_skill', 'physical_fitness', 'safety_awareness'],
                            'scoring_method': 'weighted_average'
                        }),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for metric in metrics_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_assessment_metrics (
                            assessment_id, student_id, activity_id, recent_average, historical_average, trend, volatility, improvement_rate, performance_level, progress_level, metrics_data,
                            created_at, updated_at
                        ) VALUES (
                            :assessment_id, :student_id, :activity_id, :recent_average, :historical_average, :trend, :volatility, :improvement_rate, :performance_level, :progress_level, :metrics_data,
                            :created_at, :updated_at
                        )
                    """), metric)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(metrics_data)} skill assessment metrics")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_assessment_metrics: {e}")
            savepoint.rollback()
        
        # skill_assessment_assessments
        print("  Seeding skill_assessment_assessments...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_assessments"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_assessments already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                assessments_data = []
                skill_types = ['MOTOR_SKILLS', 'COGNITIVE_SKILLS', 'SOCIAL_SKILLS', 'PHYSICAL_SKILLS', 'ACADEMIC_SKILLS']
                assessment_statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
                
                for i in range(1000):
                    student_id = random.choice(student_ids)
                    assessor_id = random.choice(user_ids)
                    curriculum_id = random.choice(curriculum_ids) if curriculum_ids else None
                    start_date = datetime.now() - timedelta(days=random.randint(1, 365))
                    
                    assessments_data.append({
                        'student_id': student_id,
                        'assessor_id': assessor_id,
                        'curriculum_id': curriculum_id,
                        'assessment_date': start_date,
                        'assessment_type': random.choice(['SKILL', 'FITNESS', 'MOVEMENT', 'BEHAVIORAL', 'PROGRESS']),
                        'score': random.uniform(0, 100),
                        'notes': f'Assessment notes for student {student_id} - {random.choice(["Excellent progress", "Needs improvement", "On track", "Requires attention"])}',
                        'assessment_metadata': json.dumps({
                            'assessment_version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}',
                            'difficulty_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                            'duration_minutes': random.randint(15, 120),
                            'environment': random.choice(['CLASSROOM', 'GYM', 'OUTDOOR', 'LAB']),
                            'equipment_used': [f'Equipment {j}' for j in range(random.randint(0, 3))],
                            'observations': [f'Observation {j}' for j in range(random.randint(1, 5))]
                        }),
                        'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
                        'is_active': random.choice([True, False]),
                        'created_at': start_date - timedelta(days=random.randint(1, 7)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                # Insert in batches
                batch_size = 100
                for i in range(0, len(assessments_data), batch_size):
                    batch = assessments_data[i:i+batch_size]
                    for assessment in batch:
                        session.execute(text("""
                            INSERT INTO skill_assessment_assessments (
                                student_id, assessor_id, curriculum_id, assessment_date, assessment_type, score, notes, assessment_metadata, status, is_active, created_at, updated_at
                            ) VALUES (
                                :student_id, :assessor_id, :curriculum_id, :assessment_date, :assessment_type, :score, :notes, :assessment_metadata, :status, :is_active, :created_at, :updated_at
                            )
                        """), assessment)
                    
                    print(f"    📊 Processed {min(i+batch_size, len(assessments_data))}/{len(assessments_data)} skill assessments...")
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(assessments_data)} skill assessments")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_assessments: {e}")
            savepoint.rollback()
        
        # skill_assessment_risk_assessments
        print("  Seeding skill_assessment_risk_assessments...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_risk_assessments"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_risk_assessments already has data")
            else:
                risk_data = []
                risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                risk_types = ['PHYSICAL', 'EMOTIONAL', 'BEHAVIORAL', 'ACADEMIC', 'SOCIAL']
                
                for i in range(500):
                    student_id = random.choice(student_ids)
                    assessor_id = random.choice(user_ids)
                    assessment_id = random.choice(assessment_ids) if assessment_ids else None
                    
                    risk_data.append({
                        'activity_id': random.choice(activity_ids),
                        'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                        'factors': json.dumps({
                            'physical_factors': [f'Physical factor {j}' for j in range(random.randint(1, 3))],
                            'environmental_factors': [f'Environmental factor {j}' for j in range(random.randint(1, 2))],
                            'behavioral_factors': [f'Behavioral factor {j}' for j in range(random.randint(1, 2))]
                        }),
                        'mitigation_measures': json.dumps({
                            'supervision_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                            'safety_equipment': [f'Equipment {j}' for j in range(random.randint(1, 3))],
                            'modifications': [f'Modification {j}' for j in range(random.randint(1, 2))]
                        }),
                        'environmental_conditions': json.dumps({
                            'temperature': random.uniform(15, 35),
                            'humidity': random.uniform(30, 80),
                            'lighting': random.choice(['GOOD', 'FAIR', 'POOR']),
                            'noise_level': random.choice(['LOW', 'MEDIUM', 'HIGH'])
                        }),
                        'equipment_status': json.dumps({
                            'condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR']),
                            'last_inspection': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                            'maintenance_required': random.choice([True, False])
                        }),
                        'student_health_considerations': json.dumps({
                            'medical_conditions': [f'Condition {j}' for j in range(random.randint(0, 2))],
                            'allergies': [f'Allergy {j}' for j in range(random.randint(0, 2))],
                            'physical_limitations': [f'Limitation {j}' for j in range(random.randint(0, 2))]
                        }),
                        'weather_conditions': json.dumps({
                            'temperature': random.uniform(10, 40),
                            'precipitation': random.choice(['NONE', 'LIGHT', 'MODERATE', 'HEAVY']),
                            'wind_speed': random.uniform(0, 30),
                            'visibility': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR'])
                        }),
                        'assessed_by': random.choice(user_ids),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 180)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for risk in risk_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_risk_assessments (
                            activity_id, risk_level, factors, mitigation_measures, environmental_conditions, equipment_status, student_health_considerations, weather_conditions, assessed_by, created_at, updated_at
                        ) VALUES (
                            :activity_id, :risk_level, :factors, :mitigation_measures, :environmental_conditions, :equipment_status, :student_health_considerations, :weather_conditions, :assessed_by, :created_at, :updated_at
                        )
                    """), risk)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(risk_data)} risk assessments")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_risk_assessments: {e}")
            savepoint.rollback()
        
        # skill_assessment_safety_alerts
        print("  Seeding skill_assessment_safety_alerts...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_safety_alerts"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_safety_alerts already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                alerts_data = []
                alert_types = ['EQUIPMENT_SAFETY', 'ENVIRONMENT_SAFETY', 'BEHAVIOR_SAFETY', 'MEDICAL_SAFETY', 'EMERGENCY_SAFETY']
                alert_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                alert_statuses = ['ACTIVE', 'RESOLVED', 'ACKNOWLEDGED', 'ESCALATED']
                
                for i in range(200):
                    student_id = random.choice(student_ids)
                    assessor_id = random.choice(user_ids)
                    assessment_id = random.choice(assessment_ids) if assessment_ids else None
                    
                    alerts_data.append({
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
                
                for alert in alerts_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_safety_alerts (
                            alert_type, severity, message, recipients, activity_id, equipment_id, resolved_at, resolution_notes, created_by, created_at, updated_at
                        ) VALUES (
                            :alert_type, :severity, :message, :recipients, :activity_id, :equipment_id, :resolved_at, :resolution_notes, :created_by, :created_at, :updated_at
                        )
                    """), alert)
                
                print(f"  ✅ Created {len(alerts_data)} safety alerts")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_safety_alerts: {e}")
        
        # skill_assessment_safety_incidents
        print("  Seeding skill_assessment_safety_incidents...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_safety_incidents"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_safety_incidents already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                incidents_data = []
                incident_types = ['MINOR_INJURY', 'EQUIPMENT_FAILURE', 'BEHAVIORAL_INCIDENT', 'MEDICAL_EMERGENCY', 'ENVIRONMENTAL_HAZARD']
                severity_levels = ['MINOR', 'MODERATE', 'MAJOR', 'SEVERE']
                incident_statuses = ['REPORTED', 'INVESTIGATING', 'RESOLVED', 'CLOSED']
                
                for i in range(100):
                    student_id = random.choice(student_ids)
                    assessor_id = random.choice(user_ids)
                    assessment_id = random.choice(assessment_ids) if assessment_ids else None
                    
                    incidents_data.append({
                        'activity_id': random.choice(activity_ids),
                        'student_id': student_id,
                        'safety_id': None,  # Make optional since safety table might be empty
                        'incident_type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL', 'BEHAVIORAL']),
                        'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                        'description': f'Detailed incident report for student {student_id} - {random.choice(["Minor scrape during activity", "Equipment stopped working", "Student became agitated", "Medical attention required"])}',
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
                
                for incident in incidents_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_safety_incidents (
                            activity_id, student_id, safety_id, incident_type, severity, description, response_taken, reported_by, location, equipment_involved, witnesses, follow_up_required, follow_up_notes, date, created_at, updated_at
                        ) VALUES (
                            :activity_id, :student_id, :safety_id, :incident_type, :severity, :description, :response_taken, :reported_by, :location, :equipment_involved, :witnesses, :follow_up_required, :follow_up_notes, :date, :created_at, :updated_at
                        )
                    """), incident)
                
                print(f"  ✅ Created {len(incidents_data)} safety incidents")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_safety_incidents: {e}")
        
        # skill_assessment_safety_protocols
        print("  Seeding skill_assessment_safety_protocols...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_safety_protocols"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_safety_protocols already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                protocols_data = []
                protocol_types = ['EQUIPMENT_SAFETY', 'ENVIRONMENT_SAFETY', 'BEHAVIOR_SAFETY', 'MEDICAL_SAFETY', 'EMERGENCY_RESPONSE']
                protocol_levels = ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
                
                for i in range(150):
                    protocols_data.append({
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
                
                for protocol in protocols_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_safety_protocols (
                            description, activity_type, protocol_type, steps, required_equipment, emergency_contacts, created_by, safety_id, last_reviewed, next_review, created_at, updated_at
                        ) VALUES (
                            :description, :activity_type, :protocol_type, :steps, :required_equipment, :emergency_contacts, :created_by, :safety_id, :last_reviewed, :next_review, :created_at, :updated_at
                        )
                    """), protocol)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(protocols_data)} safety protocols")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_safety_protocols: {e}")
            savepoint.rollback()
        
        # 10.2 GENERAL ASSESSMENT SYSTEM (5 tables)
        print("\n📊 10.2 GENERAL ASSESSMENT SYSTEM")
        print("-" * 50)
        
        # general_assessments (must be seeded first, as other tables depend on it)
        print("  Seeding general_assessments...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM general_assessments"))
            if result.scalar() > 0:
                print("  ✅ general_assessments already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                assessments_data = []
                # Use actual enum values from database
                assessment_types = ['SKILL', 'FITNESS', 'BEHAVIOR', 'PROGRESS', 'SAFETY', 'MOVEMENT']
                assessment_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED']
                assessment_levels = ['EXCELLENT', 'GOOD', 'AVERAGE', 'NEEDS_IMPROVEMENT', 'POOR']
                assessment_triggers = ['MANUAL', 'SCHEDULED', 'PERFORMANCE', 'PROGRESS', 'SAFETY', 'ADAPTATION', 'SYSTEM']
                assessment_results = ['PASS', 'FAIL', 'INCOMPLETE', 'NEEDS_REVIEW', 'EXEMPT', 'PENDING']
                
                for i in range(500):  # 500 general assessments for district scale
                    student_id = random.choice(student_ids)
                    assessor_id = random.choice(user_ids)
                    activity_id = random.choice(activity_ids)
                    assessment_date = datetime.now() - timedelta(days=random.randint(1, 365))
                    created_at = assessment_date - timedelta(days=random.randint(1, 7))
                    updated_at = datetime.now() - timedelta(days=random.randint(1, 30))
                    completed_at = assessment_date if random.choice([True, False]) else None
                    
                    assessments_data.append({
                        'activity_id': activity_id,
                        'student_id': student_id,
                        'type': random.choice(assessment_types),
                        'status': random.choice(assessment_statuses),
                        'level': random.choice(assessment_levels),
                        'trigger': random.choice(assessment_triggers),
                        'result': random.choice(assessment_results) if random.choice([True, False]) else None,
                        'score': random.uniform(0, 100),
                        'feedback': f'Assessment feedback for student {student_id}: {random.choice(["Excellent progress", "Needs improvement", "On track", "Requires attention"])}',
                        'criteria': json.dumps({
                            'technical': random.uniform(0, 100),
                            'performance': random.uniform(0, 100),
                            'safety': random.uniform(0, 100)
                        }),
                        'meta_data': json.dumps({
                            'assessment_version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}',
                            'duration_minutes': random.randint(15, 120),
                            'environment': random.choice(['CLASSROOM', 'GYM', 'OUTDOOR', 'LAB'])
                        }),
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'completed_at': completed_at
                    })
                
                # Insert in batches
                batch_size = 100
                for i in range(0, len(assessments_data), batch_size):
                    batch = assessments_data[i:i+batch_size]
                    for assessment in batch:
                        session.execute(text("""
                            INSERT INTO general_assessments (
                                activity_id, student_id, type, status, level, trigger, result, score, feedback,
                                criteria, meta_data, created_at, updated_at, completed_at
                            ) VALUES (
                                :activity_id, :student_id, :type, :status, :level, :trigger, :result, :score, :feedback,
                                :criteria, :meta_data, :created_at, :updated_at, :completed_at
                            )
                        """), assessment)
                    
                    print(f"    📊 Processed {min(i+batch_size, len(assessments_data))}/{len(assessments_data)} general assessments...")
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(assessments_data)} general assessments")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ general_assessments: {e}")
            savepoint.rollback()
        
        # general_assessment_criteria
        print("  Seeding general_assessment_criteria...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM general_assessment_criteria"))
            if result.scalar() > 0:
                print("  ✅ general_assessment_criteria already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                # Ensure we see latest committed data
                session.flush()
                # Get fresh general_assessments IDs from database (recreated on each run)
                try:
                    general_assessment_result = session.execute(text("SELECT id FROM general_assessments ORDER BY id"))
                    general_assessment_ids = [row[0] for row in general_assessment_result.fetchall()]
                    if not general_assessment_ids:
                        print("  ⚠️ No general_assessments found, skipping general_assessment_criteria")
                        savepoint.rollback()
                    else:
                        # Validate IDs actually exist by checking the first ID
                        if len(general_assessment_ids) > 0:
                            validation_result = session.execute(
                                text("SELECT COUNT(*) FROM general_assessments WHERE id = :id"),
                                {"id": general_assessment_ids[0]}
                            )
                            validation_count = validation_result.scalar() or 0
                            if validation_count == 0:
                                print(f"  ⚠️ Found {len(general_assessment_ids)} IDs but first ID {general_assessment_ids[0]} doesn't exist, skipping general_assessment_criteria")
                                savepoint.rollback()
                            else:
                                print(f"  📋 Found {len(general_assessment_ids)} general_assessments in database (validated first ID: {general_assessment_ids[0]})")
                                criteria_data = []
                                criteria_types = ['PERFORMANCE', 'KNOWLEDGE', 'SKILL', 'BEHAVIOR', 'ATTITUDE', 'PROGRESS']
                                criteria_levels = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
                                
                                # Limit to available assessments to avoid foreign key violations
                                for i in range(min(200, len(general_assessment_ids) * 5)):
                                    criteria_data.append({
                                        'assessment_id': random.choice(general_assessment_ids),  # Use only IDs that exist
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
                                
                                for criteria in criteria_data:
                                    session.execute(text("""
                                        INSERT INTO general_assessment_criteria (
                                            assessment_id, type, score, feedback, meta_data, created_at, updated_at
                                        ) VALUES (
                                            :assessment_id, :type, :score, :feedback, :meta_data, :created_at, :updated_at
                                        )
                                    """), criteria)
                                
                                savepoint.commit()
                                session.commit()
                                print(f"  ✅ Created {len(criteria_data)} assessment criteria")
                                successful_tables += 1
                except Exception as e:
                    print(f"  ⚠️ Error querying/seeding general_assessment_criteria: {e}")
                    savepoint.rollback()
        except Exception as e:
            print(f"  ⚠️ general_assessment_criteria: {e}")
            try:
                savepoint.rollback()
            except:
                pass
        
        # general_assessment_history
        print("  Seeding general_assessment_history...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM general_assessment_history"))
            if result.scalar() > 0:
                print("  ✅ general_assessment_history already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                # Ensure we see latest committed data
                session.flush()
                # Get fresh general_assessments IDs from database (must use general_assessments, not skill_assessment_assessments)
                try:
                    general_assessment_result = session.execute(text("SELECT id FROM general_assessments ORDER BY id"))
                    general_assessment_ids = [row[0] for row in general_assessment_result.fetchall()]
                    if not general_assessment_ids:
                        print("  ⚠️ No general_assessments found, skipping general_assessment_history")
                        savepoint.rollback()
                    else:
                        history_data = []
                        statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED']
                        
                        # Limit to available assessments to avoid foreign key violations
                        for i in range(min(2000, len(general_assessment_ids) * 10)):
                            assessment_id = random.choice(general_assessment_ids)  # Use only IDs that exist
                            assessment_date = datetime.now() - timedelta(days=random.randint(1, 365))
                            
                            history_data.append({
                                'assessment_id': assessment_id,
                                'status': random.choice(statuses),
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
                                'created_at': assessment_date,
                                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                            })
                        
                        # Insert in batches
                        batch_size = 200
                        for i in range(0, len(history_data), batch_size):
                            batch = history_data[i:i+batch_size]
                            for history in batch:
                                session.execute(text("""
                                    INSERT INTO general_assessment_history (
                                        assessment_id, status, score, feedback, criteria_results, meta_data, created_at, updated_at
                                    ) VALUES (
                                        :assessment_id, :status, :score, :feedback, :criteria_results, :meta_data, :created_at, :updated_at
                                    )
                                """), history)
                            
                            print(f"    📊 Processed {min(i+batch_size, len(history_data))}/{len(history_data)} assessment history records...")
                        
                        savepoint.commit()
                        session.commit()
                        print(f"  ✅ Created {len(history_data)} assessment history records")
                        successful_tables += 1
                except Exception as e:
                    print(f"  ⚠️ Error querying/seeding general_assessment_history: {e}")
                    savepoint.rollback()
        except Exception as e:
            print(f"  ⚠️ general_assessment_history: {e}")
            savepoint.rollback()
        
        # assessment_changes
        print("  Seeding assessment_changes...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM assessment_changes"))
            if result.scalar() > 0:
                print("  ✅ assessment_changes already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                # Use flexible schema detection for assessment_changes
                table_name = "assessment_changes"
                schema = get_table_schema(session, table_name)
                if not schema:
                    print(f"  ⚠️ Could not get schema for {table_name}, skipping")
                else:
                    changes_data = []
                    change_types = ['SCORE_UPDATE', 'STATUS_CHANGE', 'FEEDBACK_UPDATE', 'GRADE_CHANGE', 'METADATA_UPDATE']
                    change_reasons = ['CORRECTION', 'APPEAL', 'REVIEW', 'UPDATE', 'ADJUSTMENT']
                    
                    for i in range(500):
                        change_data = {
                            'assessor_id': random.choice(user_ids),
                            'assessment_id': random.choice(assessment_ids) if assessment_ids else random.randint(1, 50),
                            'change_type': random.choice(change_types),
                            'change_reason': random.choice(change_reasons),
                            'type': random.choice(['CREATED', 'UPDATED', 'COMPLETED', 'ARCHIVED']),
                            'changed_by': random.choice(user_ids),
                            'changed_at': datetime.now() - timedelta(days=random.randint(1, 180)),
                            'old_value': json.dumps({'value': f'Old value {i+1}', 'type': 'string'}),
                            'new_value': json.dumps({'value': f'New value {i+1}', 'type': 'string'}),
                            'description': f'Assessment change: {random.choice(["Score updated", "Status changed", "Feedback modified", "Grade adjusted", "Metadata updated"])}',
                            'change_date': datetime.now() - timedelta(days=random.randint(1, 180)),
                            'approved_by': random.choice(user_ids),
                            'metadata': json.dumps({
                                'change_source': random.choice(['Manual', 'System', 'Appeal', 'Review']),
                                'justification': f'Justification for change {i+1}',
                                'impact_level': random.choice(['Low', 'Medium', 'High']),
                                'requires_approval': random.choice([True, False])
                            }),
                            'created_at': datetime.now() - timedelta(days=random.randint(1, 180)),
                            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                        }
                        
                        # Only add student_id if the column exists
                        if 'student_id' in schema:
                            change_data['student_id'] = random.choice(student_ids)
                        
                        changes_data.append(change_data)
                    
                    # Use flexible insert
                    inserted = insert_data_flexible(session, table_name, changes_data, schema, batch_size=50)
                    if inserted > 0:
                        savepoint.commit()
                        session.commit()
                        print(f"  ✅ Created {inserted} assessment changes")
                        successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ assessment_changes: {e}")
            savepoint.rollback()
        
        # analysis_movement_feedback
        print("  Seeding analysis_movement_feedback...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM analysis_movement_feedback"))
            if result.scalar() > 0:
                print("  ✅ analysis_movement_feedback already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                # Use flexible schema detection for analysis_movement_feedback
                table_name = "analysis_movement_feedback"
                schema = get_table_schema(session, table_name)
                if not schema:
                    print(f"  ⚠️ Could not get schema for {table_name}, skipping")
                else:
                    feedback_data = []
                    feedback_types = ['MOVEMENT', 'TECHNIQUE', 'PERFORMANCE', 'PROGRESS']
                    feedback_levels = ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
                    
                    for i in range(1000):
                        feedback_item = {
                            'assessor_id': random.choice(user_ids),
                            'assessment_id': random.choice(assessment_ids) if assessment_ids else random.randint(1, 50),
                            'analysis_id': random.randint(1, 100),  # Add required analysis_id
                            'severity': random.choice(['EXCELLENT', 'GOOD', 'SATISFACTORY', 'NEEDS_IMPROVEMENT', 'POOR']),  # Add required severity
                            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),  # Add required status
                            'feedback_type': random.choice(feedback_types),
                            'feedback_level': random.choice(feedback_levels),
                            'title': f'Movement Feedback {i+1}',
                            'description': f'Detailed movement analysis feedback: {random.choice(["Excellent technique", "Good form", "Needs improvement", "Outstanding performance", "Requires attention"])}',
                            'movement_quality_score': random.uniform(1, 10),
                            'technique_score': random.uniform(1, 10),
                            'improvement_suggestions': json.dumps([
                                f'Suggestion {j+1}: {random.choice(["Focus on form", "Increase speed", "Improve balance", "Work on coordination", "Practice more"])}'
                                for j in range(random.randint(2, 5))
                            ]),
                            'video_analysis': json.dumps({
                                'video_url': f'https://example.com/video/{i+1}',
                                'timestamp': random.randint(0, 300),
                                'key_frames': [random.randint(0, 300) for _ in range(random.randint(3, 8))],
                                'analysis_notes': f'Video analysis notes for feedback {i+1}'
                            }),
                            'metadata': json.dumps({
                                'movement_category': random.choice(['Running', 'Jumping', 'Throwing', 'Catching', 'Balancing']),
                                'difficulty_level': random.choice(['Beginner', 'Intermediate', 'Advanced']),
                                'environment': random.choice(['Indoor', 'Outdoor', 'Gym', 'Field']),
                                'equipment_used': [f'Equipment {j}' for j in range(random.randint(0, 2))]
                            }),
                            'feedback_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                            'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
                            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                        }
                        
                        # Only add student_id if the column exists
                        if 'student_id' in schema:
                            feedback_item['student_id'] = random.choice(student_ids)
                        
                        feedback_data.append(feedback_item)
                    
                    # Use flexible insert
                    inserted = insert_data_flexible(session, table_name, feedback_data, schema, batch_size=100)
                    if inserted > 0:
                        savepoint.commit()
                        session.commit()
                        print(f"  ✅ Created {inserted} movement feedback records")
                        successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ analysis_movement_feedback: {e}")
            savepoint.rollback()
        
        # 10.3 ADDITIONAL SKILL ASSESSMENT TABLES (4 tables)
        print("\n📊 10.3 ADDITIONAL SKILL ASSESSMENT TABLES")
        print("-" * 50)
        
        # skill_assessment_assessment_criteria
        print("  Seeding skill_assessment_assessment_criteria...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_assessment_criteria"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_assessment_criteria already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                criteria_data = []
                for i in range(100):
                    criteria_data.append({
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
                
                for criteria in criteria_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_assessment_criteria (
                            assessment_id, criteria_name, criteria_type, description, max_score, weight, is_active, created_at, updated_at
                        ) VALUES (
                            :assessment_id, :criteria_name, :criteria_type, :description, :max_score, :weight, :is_active, :created_at, :updated_at
                        )
                    """), criteria)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(criteria_data)} assessment criteria")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_assessment_criteria: {e}")
            savepoint.rollback()
        
        # skill_assessment_assessment_history
        print("  Seeding skill_assessment_assessment_history...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_assessment_history"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_assessment_history already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                history_data = []
                for i in range(500):
                    history_data.append({
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
                
                for history in history_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_assessment_history (
                            assessment_id, student_id, assessor_id, status, score, feedback, assessment_date, completion_date, created_at, updated_at
                        ) VALUES (
                            :assessment_id, :student_id, :assessor_id, :status, :score, :feedback, :assessment_date, :completion_date, :created_at, :updated_at
                        )
                    """), history)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(history_data)} assessment history records")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_assessment_history: {e}")
            savepoint.rollback()
        
        # skill_assessment_assessment_results
        print("  Seeding skill_assessment_assessment_results...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_assessment_results"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_assessment_results already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                results_data = []
                for i in range(300):
                    results_data.append({
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
                
                for result in results_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_assessment_results (
                            assessment_id, student_id, score, max_score, grade, feedback, completed_at, created_at, updated_at
                        ) VALUES (
                            :assessment_id, :student_id, :score, :max_score, :grade, :feedback, :completed_at, :created_at, :updated_at
                        )
                    """), result)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(results_data)} assessment results")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_assessment_results: {e}")
            savepoint.rollback()
        
        # skill_assessment_skill_assessments
        print("  Seeding skill_assessment_skill_assessments...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM skill_assessment_skill_assessments"))
            if result.scalar() > 0:
                print("  ✅ skill_assessment_skill_assessments already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                skill_assessments_data = []
                for i in range(200):
                    skill_assessments_data.append({
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
                
                for skill_assessment in skill_assessments_data:
                    session.execute(text("""
                        INSERT INTO skill_assessment_skill_assessments (
                            student_id, skill_id, assessor_id, assessment_date, score, level, notes, created_at, updated_at
                        ) VALUES (
                            :student_id, :skill_id, :assessor_id, :assessment_date, :score, :level, :notes, :created_at, :updated_at
                        )
                    """), skill_assessment)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(skill_assessments_data)} skill assessments")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ skill_assessment_skill_assessments: {e}")
            savepoint.rollback()

        # 10.4 ADDITIONAL GENERAL ASSESSMENT TABLES (2 tables)
        print("\n📊 10.4 ADDITIONAL GENERAL ASSESSMENT TABLES")
        print("-" * 50)
        
        # general_skill_assessments
        print("  Seeding general_skill_assessments...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM general_skill_assessments"))
            if result.scalar() > 0:
                print("  ✅ general_skill_assessments already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                general_skill_data = []
                for i in range(150):
                    general_skill_data.append({
                        'student_id': random.choice(student_ids),
                        'skill_name': f'Skill {i+1}',
                        'skill_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                        'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'score': random.uniform(0, 100),
                        'notes': f'General skill assessment for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for skill in general_skill_data:
                    session.execute(text("""
                        INSERT INTO general_skill_assessments (
                            student_id, skill_name, skill_level, assessment_date, score, notes, created_at, updated_at
                        ) VALUES (
                            :student_id, :skill_name, :skill_level, :assessment_date, :score, :notes, :created_at, :updated_at
                        )
                    """), skill)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(general_skill_data)} general skill assessments")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ general_skill_assessments: {e}")
            savepoint.rollback()
        
        # student_health_skill_assessments
        print("  Seeding student_health_skill_assessments...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM student_health_skill_assessments"))
            if result.scalar() > 0:
                print("  ✅ student_health_skill_assessments already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                health_skill_data = []
                for i in range(100):
                    health_skill_data.append({
                        'student_id': random.choice(student_ids),
                        'health_skill': f'Health Skill {i+1}',
                        'assessment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'score': random.uniform(0, 100),
                        'notes': f'Health skill assessment for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for health_skill in health_skill_data:
                    session.execute(text("""
                        INSERT INTO student_health_skill_assessments (
                            student_id, health_skill, assessment_date, score, notes, created_at, updated_at
                        ) VALUES (
                            :student_id, :health_skill, :assessment_date, :score, :notes, :created_at, :updated_at
                        )
                    """), health_skill)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(health_skill_data)} student health skill assessments")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ student_health_skill_assessments: {e}")
            savepoint.rollback()

        # 10.5 MOVEMENT ANALYSIS SYSTEM (4 tables)
        print("\n📊 10.5 MOVEMENT ANALYSIS SYSTEM")
        print("-" * 50)
        
        # movement_analysis_metrics
        print("  Seeding movement_analysis_metrics...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM movement_analysis_metrics"))
            if result.scalar() > 0:
                print("  ✅ movement_analysis_metrics already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                metrics_data = []
                for i in range(200):
                    metrics_data.append({
                        'analysis_id': random.randint(1, 100),
                        'metric_name': f'Movement Metric {i+1}',
                        'metric_value': random.uniform(0, 100),
                        'unit': random.choice(['seconds', 'meters', 'degrees', 'count']),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for metric in metrics_data:
                    session.execute(text("""
                        INSERT INTO movement_analysis_metrics (
                            analysis_id, metric_name, metric_value, unit, created_at, updated_at
                        ) VALUES (
                            :analysis_id, :metric_name, :metric_value, :unit, :created_at, :updated_at
                        )
                    """), metric)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(metrics_data)} movement analysis metrics")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ movement_analysis_metrics: {e}")
            savepoint.rollback()
        
        # movement_analysis_patterns
        print("  Seeding movement_analysis_patterns...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM movement_analysis_patterns"))
            if result.scalar() > 0:
                print("  ✅ movement_analysis_patterns already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                patterns_data = []
                for i in range(150):
                    patterns_data.append({
                        'analysis_id': random.randint(1, 100),
                        'pattern_name': f'Movement Pattern {i+1}',
                        'pattern_type': random.choice(['GAIT', 'POSTURE', 'COORDINATION', 'BALANCE']),
                        'confidence': random.uniform(0, 1),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for pattern in patterns_data:
                    session.execute(text("""
                        INSERT INTO movement_analysis_patterns (
                            analysis_id, pattern_name, pattern_type, confidence, created_at, updated_at
                        ) VALUES (
                            :analysis_id, :pattern_name, :pattern_type, :confidence, :created_at, :updated_at
                        )
                    """), pattern)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(patterns_data)} movement analysis patterns")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ movement_analysis_patterns: {e}")
            savepoint.rollback()
        
        # physical_education_movement_analysis
        print("  Seeding physical_education_movement_analysis...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM physical_education_movement_analysis"))
            if result.scalar() > 0:
                print("  ✅ physical_education_movement_analysis already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                pe_analysis_data = []
                for i in range(100):
                    pe_analysis_data.append({
                        'student_id': random.choice(student_ids),
                        'activity_id': random.choice(activity_ids),
                        'analysis_type': random.choice(['RUNNING', 'JUMPING', 'THROWING', 'CATCHING']),
                        'score': random.uniform(0, 100),
                        'notes': f'PE movement analysis for student {random.choice(student_ids)}: {random.choice(["Excellent", "Good", "Fair", "Needs work"])}',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for analysis in pe_analysis_data:
                    session.execute(text("""
                        INSERT INTO physical_education_movement_analysis (
                            student_id, activity_id, analysis_type, score, notes, created_at, updated_at
                        ) VALUES (
                            :student_id, :activity_id, :analysis_type, :score, :notes, :created_at, :updated_at
                        )
                    """), analysis)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(pe_analysis_data)} physical education movement analyses")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ physical_education_movement_analysis: {e}")
            savepoint.rollback()

        # 10.6 ADDITIONAL SAFETY & RISK MANAGEMENT (5 tables)
        print("\n📊 10.6 ADDITIONAL SAFETY & RISK MANAGEMENT")
        print("-" * 50)
        
        # safety_incidents
        print("  Seeding safety_incidents...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_incidents"))
            if result.scalar() > 0:
                print("  ✅ safety_incidents already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                incidents_data = []
                for i in range(100):
                    incidents_data.append({
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
                
                for incident in incidents_data:
                    session.execute(text("""
                        INSERT INTO safety_incidents (
                            student_id, activity_id, incident_type, severity, description, reported_by, incident_date, created_at, updated_at
                        ) VALUES (
                            :student_id, :activity_id, :incident_type, :severity, :description, :reported_by, :incident_date, :created_at, :updated_at
                        )
                    """), incident)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(incidents_data)} safety incidents")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ safety_incidents: {e}")
            savepoint.rollback()
        
        # safety_guidelines
        print("  Seeding safety_guidelines...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_guidelines"))
            if result.scalar() > 0:
                print("  ✅ safety_guidelines already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                guidelines_data = []
                for i in range(50):
                    guidelines_data.append({
                        'guideline_name': f'Safety Guideline {i+1}',
                        'guideline_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'BEHAVIOR', 'EMERGENCY']),
                        'description': f'Safety guideline for {random.choice(["equipment use", "environmental safety", "behavioral management", "emergency response"])}',
                        'is_active': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for guideline in guidelines_data:
                    session.execute(text("""
                        INSERT INTO safety_guidelines (
                            guideline_name, guideline_type, description, is_active, created_at, updated_at
                        ) VALUES (
                            :guideline_name, :guideline_type, :description, :is_active, :created_at, :updated_at
                        )
                    """), guideline)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(guidelines_data)} safety guidelines")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ safety_guidelines: {e}")
            savepoint.rollback()
        
        # safety_protocols
        print("  Seeding safety_protocols...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_protocols"))
            if result.scalar() > 0:
                print("  ✅ safety_protocols already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                protocols_data = []
                for i in range(75):
                    protocols_data.append({
                        'protocol_name': f'Safety Protocol {i+1}',
                        'protocol_type': random.choice(['EMERGENCY', 'PREVENTIVE', 'MAINTENANCE', 'TRAINING']),
                        'description': f'Safety protocol for {random.choice(["emergency response", "preventive measures", "equipment maintenance", "staff training"])}',
                        'is_active': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for protocol in protocols_data:
                    session.execute(text("""
                        INSERT INTO safety_protocols (
                            protocol_name, protocol_type, description, is_active, created_at, updated_at
                        ) VALUES (
                            :protocol_name, :protocol_type, :description, :is_active, :created_at, :updated_at
                        )
                    """), protocol)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(protocols_data)} safety protocols")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ safety_protocols: {e}")
            savepoint.rollback()
        
        # safety_reports
        print("  Seeding safety_reports...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_reports"))
            if result.scalar() > 0:
                print("  ✅ safety_reports already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                reports_data = []
                for i in range(100):
                    reports_data.append({
                        'student_id': random.choice(student_ids),
                        'activity_id': random.choice(activity_ids),
                        'report_type': random.choice(['INCIDENT', 'INSPECTION', 'AUDIT', 'MAINTENANCE']),
                        'description': f'Safety report for student {random.choice(student_ids)}: {random.choice(["Incident report", "Inspection report", "Audit report", "Maintenance report"])}',
                        'reported_by': random.choice(user_ids),
                        'report_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for report in reports_data:
                    session.execute(text("""
                        INSERT INTO safety_reports (
                            student_id, activity_id, report_type, description, reported_by, report_date, created_at, updated_at
                        ) VALUES (
                            :student_id, :activity_id, :report_type, :description, :reported_by, :report_date, :created_at, :updated_at
                        )
                    """), report)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(reports_data)} safety reports")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ safety_reports: {e}")
            savepoint.rollback()
        
        # safety_measures
        print("  Seeding safety_measures...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_measures"))
            if result.scalar() > 0:
                print("  ✅ safety_measures already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                measures_data = []
                for i in range(80):
                    measures_data.append({
                        'measure_name': f'Safety Measure {i+1}',
                        'measure_type': random.choice(['PREVENTIVE', 'PROTECTIVE', 'EMERGENCY', 'TRAINING']),
                        'description': f'Safety measure for {random.choice(["prevention", "protection", "emergency response", "training"])}',
                        'is_active': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for measure in measures_data:
                    session.execute(text("""
                        INSERT INTO safety_measures (
                            measure_name, measure_type, description, is_active, created_at, updated_at
                        ) VALUES (
                            :measure_name, :measure_type, :description, :is_active, :created_at, :updated_at
                        )
                    """), measure)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(measures_data)} safety measures")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ safety_measures: {e}")
            savepoint.rollback()
        
        # safety_checklists
        print("  Seeding safety_checklists...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_checklists"))
            if result.scalar() > 0:
                print("  ✅ safety_checklists already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                checklists_data = []
                for i in range(60):
                    checklists_data.append({
                        'checklist_name': f'Safety Checklist {i+1}',
                        'checklist_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'ACTIVITY', 'EMERGENCY']),
                        'description': f'Safety checklist for {random.choice(["equipment inspection", "environmental assessment", "activity preparation", "emergency procedures"])}',
                        'is_active': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for checklist in checklists_data:
                    session.execute(text("""
                        INSERT INTO safety_checklists (
                            checklist_name, checklist_type, description, is_active, created_at, updated_at
                        ) VALUES (
                            :checklist_name, :checklist_type, :description, :is_active, :created_at, :updated_at
                        )
                    """), checklist)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(checklists_data)} safety checklists")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ safety_checklists: {e}")
            savepoint.rollback()

        # 10.7 ADDITIONAL INJURY PREVENTION (1 table)
        print("\n📊 10.7 ADDITIONAL INJURY PREVENTION")
        print("-" * 50)
        
        # injury_preventions
        print("  Seeding injury_preventions...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM injury_preventions"))
            if result.scalar() > 0:
                print("  ✅ injury_preventions already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                injury_prevention_data = []
                for i in range(100):
                    injury_prevention_data.append({
                        'prevention_name': f'Injury Prevention {i+1}',
                        'prevention_type': random.choice(['EQUIPMENT', 'TRAINING', 'ENVIRONMENT', 'BEHAVIOR']),
                        'description': f'Injury prevention measure for {random.choice(["equipment safety", "training protocols", "environmental control", "behavioral management"])}',
                        'is_active': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for prevention in injury_prevention_data:
                    session.execute(text("""
                        INSERT INTO injury_preventions (
                            prevention_name, prevention_type, description, is_active, created_at, updated_at
                        ) VALUES (
                            :prevention_name, :prevention_type, :description, :is_active, :created_at, :updated_at
                        )
                    """), prevention)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(injury_prevention_data)} injury preventions")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ injury_preventions: {e}")
            savepoint.rollback()

        # 10.8 SAFETY & RISK MANAGEMENT (4 tables)
        print("\n📊 10.8 SAFETY & RISK MANAGEMENT")
        print("-" * 50)
        
        # safety
        print("  Seeding safety...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety"))
            if result.scalar() > 0:
                print("  ✅ safety already has data")
                savepoint.commit()
            else:
                safety_data = []
                safety_types = ['INCIDENT', 'NEAR_MISS', 'HAZARD', 'INSPECTION', 'TRAINING']
                severity_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                statuses = ['OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED']
                
                # Get schema for safety table
                schema_result = session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'safety' 
                    ORDER BY ordinal_position
                """))
                schema = {row[0]: row[1] for row in schema_result.fetchall()}
                
                for i in range(300):
                    incident_date = datetime.now() - timedelta(days=random.randint(1, 120))
                    
                    safety_item = {
                        'reporter_id': random.choice(user_ids),
                        'activity_id': random.choice(activity_ids),  # Always provide activity_id since it's NOT NULL
                        'safety_type': random.choice(safety_types),
                        'severity_level': random.choice(severity_levels),
                        'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),  # Add required risk_level
                        'title': f'Safety Report {i+1}: {random.choice(["Minor incident", "Equipment issue", "Environmental hazard", "Behavioral concern", "Medical alert"])}',
                        'description': f'Detailed safety report {i+1}: {random.choice(["Student reported minor discomfort", "Equipment malfunction observed", "Environmental condition noted", "Behavioral issue documented", "Medical attention required"])}',
                        'status': random.choice(statuses),
                        'incident_date': incident_date,
                        'resolved_date': incident_date + timedelta(days=random.randint(1, 30)) if random.random() > 0.3 else None,
                        'action_taken': f'Action: {random.choice(["First aid applied", "Equipment replaced", "Environment modified", "Student counseled", "Medical team contacted"])}',
                        'prevention_measures': f'Prevention: {random.choice(["Additional training", "Equipment check", "Supervision increased", "Protocol updated", "Environmental assessment"])}',
                        'metadata': json.dumps({
                            'location': random.choice(['Classroom A', 'Gymnasium', 'Playground', 'Lab', 'Office', 'Hallway']),
                            'time_of_day': random.choice(['Morning', 'Afternoon', 'Evening']),
                            'weather_conditions': random.choice(['Clear', 'Rainy', 'Windy', 'Hot', 'Cold', 'Snowy']),
                            'staff_present': [f'Staff {j}' for j in range(random.randint(1, 3))],
                            'witnesses': [f'Witness {j}' for j in range(random.randint(0, 2))],
                            'equipment_involved': [f'Equipment {j}' for j in range(random.randint(0, 2))]
                        }),
                        'created_at': incident_date,
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    }
                    
                    # Only add student_id if the column exists
                    if 'student_id' in schema:
                        safety_item['student_id'] = random.choice(student_ids) if random.random() > 0.3 else None
                    
                    safety_data.append(safety_item)
                
                # Use flexible insert
                inserted = insert_data_flexible(session, 'safety', safety_data, schema)
                if inserted > 0:
                    savepoint.commit()
                    session.commit()
                    print(f"  ✅ Created {inserted} safety records")
        except Exception as e:
            print(f"  ⚠️ safety: {e}")
            savepoint.rollback()
        
        # safety_incident_base
        print("  Seeding safety_incident_base...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM safety_incident_base"))
            if result.scalar() > 0:
                print("  ✅ safety_incident_base already has data")
                savepoint.commit()
            else:
                # Get schema for safety_incident_base table
                schema_result = session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'safety_incident_base' 
                    ORDER BY ordinal_position
                """))
                schema = {row[0]: row[1] for row in schema_result.fetchall()}
                
                base_data = []
                incident_categories = ['EQUIPMENT', 'ENVIRONMENT', 'BEHAVIOR', 'MEDICAL', 'EMERGENCY']
                severity_levels = ['MINOR', 'MODERATE', 'MAJOR', 'SEVERE']
                
                for i in range(200):
                    base_item = {
                        'type': random.choice(['INJURY', 'NEAR_MISS', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL']),  # Add required type
                        'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),  # Add required severity
                        'location': random.choice(['Classroom A', 'Gymnasium', 'Playground', 'Lab', 'Office', 'Hallway']),  # Add required location
                        'teacher_id': random.choice(user_ids),  # Add required teacher_id
                        'severity_level': random.choice(severity_levels),
                        'title': f'Base Incident {i+1}',
                        'description': f'Base incident template for {random.choice(["equipment failure", "environmental hazard", "behavioral issue", "medical emergency", "safety concern"])}',
                        'action_taken': f'Action: {random.choice(["First aid applied", "Equipment replaced", "Environment modified", "Student counseled", "Medical team contacted"])}',  # Add required action_taken
                        'standard_response': f'Standard response: {random.choice(["Assess situation", "Provide first aid", "Contact supervisor", "Document incident", "Follow protocol"])}',
                        'prevention_tips': json.dumps([
                            f'Tip {j+1}: {random.choice(["Regular equipment checks", "Environmental monitoring", "Behavioral observation", "Medical screening", "Safety training"])}'
                            for j in range(random.randint(3, 6))
                        ]),
                        'is_active': random.choice([True, False]),
                        'version': f'v{random.randint(1, 3)}.{random.randint(0, 9)}',
                        'created_at': datetime.now() - timedelta(days=random.randint(30, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    }
                    
                    # Only add incident_category if the column exists
                    if 'incident_category' in schema:
                        base_item['incident_category'] = random.choice(incident_categories)
                    
                    base_data.append(base_item)
                
                # Use flexible insert
                inserted = insert_data_flexible(session, 'safety_incident_base', base_data, schema)
                if inserted > 0:
                    savepoint.commit()
                    session.commit()
                    print(f"  ✅ Created {inserted} safety incident base records")
        except Exception as e:
            print(f"  ⚠️ safety_incident_base: {e}")
            savepoint.rollback()
        
        # activity_injury_preventions
        print("  Seeding activity_injury_preventions...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM activity_injury_preventions"))
            if result.scalar() > 0:
                print("  ✅ activity_injury_preventions already has data")
                savepoint.commit()
                successful_tables += 1
            else:
                prevention_data = []
                prevention_types = ['EQUIPMENT_SAFETY', 'ENVIRONMENT_SAFETY', 'TECHNIQUE_SAFETY', 'SUPERVISION_SAFETY']
                priority_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                
                for i in range(150):
                    activity_id = random.choice(activity_ids)
                    prevention_id = random.randint(1, 50)
                    
                    prevention_data.append({
                        'activity_id': activity_id,
                        'prevention_id': prevention_id,
                        'prevention_type': random.choice(prevention_types),
                        'priority': random.choice(priority_levels),
                        'description': f'Injury prevention for activity {activity_id}: {random.choice(["Equipment check required", "Environmental assessment needed", "Technique training essential", "Supervision level critical"])}',
                        'prevention_measures': json.dumps([
                            f'Measure {j+1}: {random.choice(["Equipment inspection", "Environmental check", "Technique review", "Supervision increase"])}'
                            for j in range(random.randint(2, 5))
                        ]),
                        'effectiveness_rating': random.uniform(1, 10),
                        'implementation_difficulty': random.choice(['EASY', 'MEDIUM', 'HARD']),
                        'required_training': random.choice(['NONE', 'BASIC', 'ADVANCED', 'EXPERT']),
                        'is_active': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                for prevention in prevention_data:
                    session.execute(text("""
                        INSERT INTO activity_injury_preventions (
                            activity_id, prevention_id, prevention_type, priority, description, prevention_measures,
                            effectiveness_rating, implementation_difficulty, required_training, is_active, created_at, updated_at
                        ) VALUES (
                            :activity_id, :prevention_id, :prevention_type, :priority, :description, :prevention_measures,
                            :effectiveness_rating, :implementation_difficulty, :required_training, :is_active, :created_at, :updated_at
                        )
                    """), prevention)
                
                savepoint.commit()
                session.commit()
                print(f"  ✅ Created {len(prevention_data)} activity injury prevention records")
                successful_tables += 1
        except Exception as e:
            print(f"  ⚠️ activity_injury_preventions: {e}")
            savepoint.rollback()
        
        # activity_logs (already seeded in main script, but ensure it's working)
        print("  Seeding activity_logs...")
        savepoint = session.begin_nested()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM activity_logs"))
            count = result.scalar()
            if count > 0:
                print(f"  ✅ activity_logs already has {count} records")
                savepoint.commit()
                successful_tables += 1
            else:
                print("  ⚠️ activity_logs is empty - this should have been seeded in main script")
                savepoint.rollback()
        except Exception as e:
            print(f"  ⚠️ activity_logs: {e}")
            savepoint.rollback()
        
        # Count actually populated tables - All 30 Phase 10 tables
        phase10_tables = [
            # Skill Assessment System (10 tables)
            'skill_assessment_assessment_metrics', 'skill_assessment_assessments', 'skill_assessment_risk_assessments',
            'skill_assessment_safety_alerts', 'skill_assessment_safety_incidents', 'skill_assessment_safety_protocols',
            'skill_assessment_assessment_criteria', 'skill_assessment_assessment_history', 'skill_assessment_assessment_results',
            'skill_assessment_skill_assessments',
            
            # General Assessment System (4 tables)
            'general_assessment_criteria', 'general_assessment_history', 'general_skill_assessments',
            'student_health_skill_assessments',
            
            # Assessment Changes & Movement Analysis (3 tables)
            'assessment_changes', 'analysis_movement_feedback', 'movement_analysis_metrics', 'movement_analysis_patterns',
            'physical_education_movement_analysis',
            
            # Safety & Risk Management (8 tables)
            'safety', 'safety_incident_base', 'safety_incidents', 'safety_guidelines', 'safety_protocols',
            'safety_reports', 'safety_measures', 'safety_checklists',
            
            # Injury Prevention & Activity Management (3 tables)
            'activity_injury_preventions', 'injury_preventions', 'activity_logs'
        ]
        
        populated_count = 0
        failed_tables = []
        for table in phase10_tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                if count > 0:
                    populated_count += 1
                else:
                    failed_tables.append(f"{table} (0 records)")
            except Exception as e:
                failed_tables.append(f"{table} (error: {str(e)[:50]})")
        
        if failed_tables:
            print(f"  ⚠️ Failed tables: {', '.join(failed_tables)}")
        
        print(f"\n🎉 Phase 10 Assessment & Skill Management: {populated_count}/{total_tables} tables populated")
        print(f"📊 Total tables processed: {total_tables}")
        print(f"✅ Successfully populated {populated_count} working tables")
        if populated_count == total_tables:
            print("✅ Phase 10 assessment & skill management completed successfully!")
        else:
            print(f"⚠️ Phase 10 partially completed - {total_tables - populated_count} tables failed")
        
        return populated_count == total_tables
        
    except Exception as e:
        print(f"❌ Error in Phase 10: {e}")
        recover_transaction(session)
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
