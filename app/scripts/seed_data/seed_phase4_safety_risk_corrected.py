"""
Phase 4: Safety & Risk Management System - CORRECTED VERSION
Comprehensive safety infrastructure, risk assessment, and equipment management
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_table_schema(session: Session, table_name: str) -> Dict[str, str]:
    """Get the actual database schema for a table"""
    try:
        result = session.execute(text(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """))
        return {row[0]: row[1] for row in result}
    except Exception as e:
        print(f"Error getting schema for {table_name}: {e}")
        return {}

def create_dynamic_insert(session: Session, table_name: str, data: List[Dict], sample_record: Dict) -> bool:
    """Create and execute INSERT statement using actual table schema"""
    try:
        # Get the actual table schema
        schema = get_table_schema(session, table_name)
        if not schema:
            print(f"  ❌ Could not get schema for {table_name}")
            return False
        
        # Get available columns from sample record
        available_columns = list(sample_record.keys())
        
        # Find matching columns between data and schema
        matching_columns = [col for col in available_columns if col in schema]
        
        if not matching_columns:
            print(f"  ❌ No matching columns found for {table_name}")
            print(f"  📝 Available columns: {available_columns}")
            print(f"  📝 Schema columns: {list(schema.keys())}")
            return False
        
        # Create dynamic INSERT statement
        columns_str = ", ".join(matching_columns)
        values_str = ", ".join([f":{col}" for col in matching_columns])
        
        insert_sql = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({values_str})
        """
        
        # Execute the insert
        print(f"  🔍 Attempting to insert into {table_name} with SQL: {insert_sql}")
        print(f"  📝 Sample data keys: {list(sample_record.keys())}")
        session.execute(text(insert_sql), data)
        session.commit()  # Commit immediately after each table
        print(f"  ✅ {table_name}: {len(data)} records (using columns: {matching_columns})")
        return True
        
    except Exception as e:
        print(f"  ❌ {table_name} ERROR: {e}")
        print(f"  📝 Sample data: {sample_record}")
        session.rollback()
        return False

def get_table_ids(session: Session, table_name: str) -> List[int]:
    """Get IDs from a table for foreign key references"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name} LIMIT 100"))
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"⚠️ No {table_name} found: {e}")
        return []

def seed_phase4_dependencies(session: Session, user_ids: List[int], school_ids: List[int], activity_ids: List[int]) -> Dict[str, int]:
    """Seed Phase 4 dependency tables that other Phase 4 tables depend on"""
    results = {}
    
    print("🔧 SEEDING PHASE 4 DEPENDENCIES")
    print("-" * 50)
    
    # Seed basic safety infrastructure first
    print("📋 Seeding safety infrastructure...")
    results.update(seed_safety_infrastructure(session, user_ids, school_ids, activity_ids))
    
    # Seed equipment management
    print("🔧 Seeding equipment management...")
    results.update(seed_equipment_management(session, user_ids, school_ids, activity_ids))
    
    # Seed environmental monitoring
    print("🌍 Seeding environmental monitoring...")
    results.update(seed_environmental_monitoring(session, user_ids, school_ids, activity_ids))
    
    print(f"✅ Phase 4 dependencies completed: {sum(results.values())} records across {len(results)} tables")
    return results

def seed_phase4_safety_risk(session: Session, user_ids: List[int] = None, school_ids: List[int] = None, activity_ids: List[int] = None, student_ids: List[int] = None) -> Dict[str, int]:
    """
    Complete Phase 4 Safety & Risk Management System
    Seeds all safety, risk, equipment, and compliance tables
    """
    print("="*70)
    print("🛡️ PHASE 4: SAFETY & RISK MANAGEMENT SYSTEM")
    print("="*70)
    print("📊 Seeding comprehensive safety infrastructure")
    print("⚠️ Risk assessment & prevention systems")
    print("🔧 Equipment management & maintenance")
    print("📋 Compliance & audit systems")
    print("="*70)
    
    results = {}
    
    # Get reference data - use provided IDs or get from database
    if student_ids is None:
        student_ids = get_table_ids(session, "students")
    if user_ids is None:
        user_ids = get_table_ids(session, "users")
    if school_ids is None:
        school_ids = get_table_ids(session, "schools")
    if activity_ids is None:
        activity_ids = get_table_ids(session, "activities")
    
    print(f"  📊 Found {len(student_ids)} students, {len(user_ids)} users, {len(school_ids)} schools, {len(activity_ids)} activities")
    
    # 4.1 Seed Phase 4 Dependencies First
    print("\n🔧 PHASE 4 DEPENDENCIES")
    print("-" * 50)
    results.update(seed_phase4_dependencies(session, user_ids, school_ids, activity_ids))
    
    # 4.2 Risk Assessment & Prevention (12 tables)
    print("\n⚠️ RISK ASSESSMENT & PREVENTION (12 tables)")
    print("-" * 50)
    results.update(seed_risk_assessment(session, user_ids, student_ids, activity_ids))
    
    # 4.3 Equipment Management (8 tables)
    print("\n🔧 EQUIPMENT MANAGEMENT (8 tables)")
    print("-" * 50)
    results.update(seed_equipment_management(session, user_ids, school_ids, activity_ids))
    
    # 4.4 Environmental Monitoring (6 tables)
    print("\n🌍 ENVIRONMENTAL MONITORING (6 tables)")
    print("-" * 50)
    results.update(seed_environmental_monitoring(session, user_ids, school_ids, activity_ids))
    
    # 4.5 Compliance & Audit (6 tables)
    print("\n📋 COMPLIANCE & AUDIT (6 tables)")
    print("-" * 50)
    results.update(seed_compliance_audit(session, user_ids, activity_ids))
    
    # Final status check
    print("\n📊 FINAL PHASE 4 STATUS CHECK")
    print("-" * 50)
    
    phase4_tables = [
        'safety_protocols', 'safety_guidelines', 'safety_checklists', 'safety_measures',
        'safety_reports', 'safety_checklist_items', 'injury_risk_factors', 'injury_preventions',
        'injury_risk_assessments', 'injury_prevention_risk_assessments',
        'injury_risk_factor_safety_guidelines', 'prevention_assessments',
        'prevention_measures', 'equipment', 'equipment_categories', 'equipment_conditions',
        'equipment_status', 'equipment_types', 'equipment_usage', 'equipment_maintenance',
        'maintenance_records', 'physical_education_equipment', 'physical_education_equipment_maintenance',
        'environmental_conditions', 'environmental_alerts', 'activity_environmental_impacts',
        'physical_education_environmental_checks', 'skill_assessment_safety_checks',
        'skill_assessment_environmental_checks', 'skill_assessment_equipment_checks', 'audit_logs', 'security_audits',
        'security_incident_management', 'policy_security_audits', 'security_general_audit_logs'
    ]
    
    for table in phase4_tables:
        try:
            count_result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = count_result.scalar()
            status = '✅' if count > 0 else '⚠️'
            print(f"  {status} {table}: {count} records")
        except Exception as e:
            print(f"  ❌ {table}: ERROR - {e}")
    
    total_records = sum(results.values())
    completed_tables = len([t for t in phase4_tables if results.get(t, 0) > 0])
    completion_percentage = (completed_tables / len(phase4_tables)) * 100
    print(f"\n🎉 PHASE 4 COMPLETION: {completed_tables}/{len(phase4_tables)} ({completion_percentage:.1f}%)")
    print(f"🏆 PHASE 4 SAFETY & RISK MANAGEMENT: {completion_percentage:.1f}% COMPLETE! 🏆")
    print(f"🎯 {completed_tables} out of {len(phase4_tables)} tables successfully seeded with {total_records:,} total records!")
    
    return results

def get_table_ids(session: Session, table_name: str) -> List[int]:
    """Get existing IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name} LIMIT 100"))
        return [row[0] for row in result.fetchall()]
    except:
        return list(range(1, 101))  # Fallback range

def seed_safety_infrastructure(session: Session, user_ids: List[int], school_ids: List[int], activity_ids: List[int]) -> Dict[str, int]:
    """Seed safety infrastructure tables"""
    results = {}
    
    # Safety Protocols
    protocols_data = []
    for i in range(50):
        protocols_data.append({
            'name': f'Safety Protocol {i+1}',
            'description': f'Comprehensive safety protocol for {random.choice(["Equipment", "Activities", "Emergency", "Maintenance", "Environmental"])}',
            'category': random.choice(['EQUIPMENT', 'ACTIVITY', 'EMERGENCY', 'MAINTENANCE', 'ENVIRONMENTAL']),
            'requirements': f'Detailed requirements for protocol {i+1}',
            'procedures': f'Step-by-step procedures for protocol {i+1}',
            'emergency_contacts': f'Emergency contact information for protocol {i+1}',
            'is_active': True,
            'last_reviewed': datetime.now() - timedelta(days=random.randint(1, 90)),
            'reviewed_by': random.choice(user_ids),
            'created_by': random.choice(user_ids),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    # Try dynamic insert first
    if create_dynamic_insert(session, 'safety_protocols', protocols_data, protocols_data[0] if protocols_data else {}):
        results['safety_protocols'] = len(protocols_data)
    else:
        # Fallback to original method
        try:
            session.execute(text("""
                INSERT INTO safety_protocols (name, description, category,
                                            requirements, procedures, emergency_contacts, is_active,
                                            last_reviewed, reviewed_by, created_by, created_at, updated_at)
                VALUES (:name, :description, :category,
                        :requirements, :procedures, :emergency_contacts, :is_active,
                        :last_reviewed, :reviewed_by, :created_by, :created_at, :updated_at)
            """), protocols_data)
            session.commit()  # Commit immediately
            results['safety_protocols'] = len(protocols_data)
            print(f"  ✅ safety_protocols: {len(protocols_data)} records (fallback method)")
        except Exception as e:
            print(f"  ❌ safety_protocols ERROR: {e}")
            print(f"  📝 Protocol data sample: {protocols_data[0] if protocols_data else 'No data'}")
            session.rollback()
            results['safety_protocols'] = 0
    
    # Safety Guidelines
    guidelines_data = []
    for i in range(75):
        guidelines_data.append({
            'name': f'Safety Guideline {i+1}',
            'category': random.choice(['EQUIPMENT', 'ACTIVITY', 'EMERGENCY', 'ENVIRONMENTAL']),
            'description': f'Detailed safety guideline covering {random.choice(["Equipment Use", "Activity Safety", "Emergency Procedures", "Environmental Safety"])}',
            'guidelines': json.dumps({
                'general_guidelines': f'General safety guidelines for {i+1}',
                'specific_requirements': f'Specific requirements for guideline {i+1}',
                'procedures': f'Detailed procedures for guideline {i+1}'
            }),
            'compliance_requirements': json.dumps({
                'mandatory': random.choice([True, False]),
                'frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY']),
                'training_required': random.choice([True, False])
            }),
            'target_activities': json.dumps([f'Activity {j}' for j in range(random.randint(1, 5))]),
            'equipment_requirements': json.dumps([f'Equipment {j}' for j in range(random.randint(1, 3))]),
            'training_requirements': json.dumps({
                'required_training': f'Training required for guideline {i+1}',
                'certification_needed': random.choice([True, False])
            }),
            'supervision_requirements': json.dumps({
                'supervisor_required': random.choice([True, False]),
                'supervisor_ratio': f'1:{random.randint(5, 20)}'
            }),
            'compliance_metrics': json.dumps({
                'success_rate': random.uniform(0.8, 1.0),
                'compliance_score': random.randint(80, 100)
            }),
            'review_frequency': random.choice(['MONTHLY', 'QUARTERLY', 'ANNUALLY']),
            'last_review_date': datetime.now() - timedelta(days=random.randint(1, 90)),
            'next_review_date': datetime.now() + timedelta(days=random.randint(30, 365)),
            'reference_materials': json.dumps([f'Reference {j}' for j in range(random.randint(1, 3))]),
            'emergency_procedures': json.dumps({
                'immediate_action': f'Immediate action for guideline {i+1}',
                'escalation': f'Escalation procedures for guideline {i+1}'
            }),
            'contact_information': json.dumps({
                'primary_contact': f'Contact {i+1}',
                'emergency_contact': f'Emergency contact {i+1}'
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({'guideline_id': i+1, 'version': '1.0'}),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': True
        })
    
    try:
        session.execute(text("""
            INSERT INTO safety_guidelines (name, category, description, 
                                         guidelines, compliance_requirements, target_activities, 
                                         equipment_requirements, training_requirements, supervision_requirements, 
                                         compliance_metrics, review_frequency, last_review_date, next_review_date, 
                                         reference_materials, emergency_procedures, contact_information, 
                                         created_at, updated_at, last_accessed_at, archived_at, deleted_at, 
                                         scheduled_deletion_at, retention_period, metadata, status, is_active)
            VALUES (:name, :category, :description, 
                    :guidelines, :compliance_requirements, :target_activities, 
                    :equipment_requirements, :training_requirements, :supervision_requirements, 
                    :compliance_metrics, :review_frequency, :last_review_date, :next_review_date, 
                    :reference_materials, :emergency_procedures, :contact_information, 
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                    :scheduled_deletion_at, :retention_period, :metadata, :status, :is_active)
        """), guidelines_data)
        results['safety_guidelines'] = len(guidelines_data)
        print(f"  ✅ safety_guidelines: {len(guidelines_data)} records")
    except Exception as e:
        print(f"  ⚠️ safety_guidelines: {e}")
        results['safety_guidelines'] = 0
    
    # Safety Checklists
    checklists_data = []
    for i in range(30):
        checklists_data.append({
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'checklist_date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'checklist_type': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'EMERGENCY']),
            'checklist_metadata': json.dumps({
                'name': f'Safety Checklist {i+1}',
                'description': f'Comprehensive safety checklist for {random.choice(["Daily Operations", "Equipment Inspection", "Emergency Preparedness", "Environmental Monitoring"])}',
                'items_count': random.randint(5, 20),
                'completion_rate': random.uniform(0.8, 1.0)
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO safety_checklists (activity_id, checklist_date, checklist_type, checklist_metadata)
            VALUES (:activity_id, :checklist_date, :checklist_type, :checklist_metadata)
        """), checklists_data)
        session.commit()  # Commit immediately
        results['safety_checklists'] = len(checklists_data)
        print(f"  ✅ safety_checklists: {len(checklists_data)} records")
    except Exception as e:
        print(f"  ⚠️ safety_checklists: {e}")
        session.rollback()
        results['safety_checklists'] = 0
    
    # Safety Measures
    safety_measures_data = []
    for i in range(40):
        safety_measures_data.append({
            'incident_id': random.randint(1, 25),  # Reference to safety_incidents
            'measure_type': random.choice(['PREVENTIVE', 'PROTECTIVE', 'CORRECTIVE', 'EMERGENCY']),
            'description': f'Safety measure {i+1} for {random.choice(["equipment safety", "environmental protection", "emergency response", "preventive maintenance"])}',
            'implementation_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'measure_metadata': json.dumps({
                'name': f'Safety Measure {i+1}',
                'category': random.choice(['EQUIPMENT', 'ENVIRONMENTAL', 'PROCEDURAL', 'TRAINING']),
                'implementation_plan': {
                    'steps': [f'Step {j}' for j in range(random.randint(3, 6))],
                    'timeline': f'{random.randint(1, 12)} weeks',
                    'resources': [f'Resource {j}' for j in range(random.randint(1, 4))]
                },
                'effectiveness_metrics': [f'Metric {j}' for j in range(random.randint(1, 3))],
                'cost_estimate': round(random.uniform(200.0, 2000.0), 2),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'status': random.choice(['PLANNED', 'IN_PROGRESS', 'IMPLEMENTED', 'COMPLETED'])
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO safety_measures (incident_id, measure_type, description, implementation_date, measure_metadata)
            VALUES (:incident_id, :measure_type, :description, :implementation_date, :measure_metadata)
        """), safety_measures_data)
        session.commit()  # Commit immediately
        results['safety_measures'] = len(safety_measures_data)
        print(f"  ✅ safety_measures: {len(safety_measures_data)} records")
    except Exception as e:
        print(f"  ⚠️ safety_measures: {e}")
        session.rollback()
        results['safety_measures'] = 0
    
    # Safety Reports - MOVED TO AFTER EQUIPMENT SEEDING
    # (This will be handled in seed_equipment_management or a separate function)
    
    # Safety Checklist Items
    checklist_items_data = []
    for i in range(100):
        checklist_items_data.append({
            'checklist_id': random.randint(1, 30),
            'item_name': f'Safety checklist item {i+1}',
            'is_checked': random.choice([True, False]),
            'notes': f'Notes for checklist item {i+1}' if random.choice([True, False]) else None,
            'item_metadata': json.dumps({
                'item_type': random.choice(['CHECKBOX', 'TEXT', 'NUMBER', 'SELECT']),
                'is_required': random.choice([True, False]),
                'order_index': i + 1,
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO safety_checklist_items (checklist_id, item_name, is_checked, notes, item_metadata)
            VALUES (:checklist_id, :item_name, :is_checked, :notes, :item_metadata)
        """), checklist_items_data)
        results['safety_checklist_items'] = len(checklist_items_data)
        print(f"  ✅ safety_checklist_items: {len(checklist_items_data)} records")
    except Exception as e:
        print(f"  ⚠️ safety_checklist_items: {e}")
        results['safety_checklist_items'] = 0
    
    session.commit()
    return results

def seed_risk_assessment(session: Session, user_ids: List[int], student_ids: List[int], activity_ids: List[int]) -> Dict[str, int]:
    """Seed risk assessment and prevention tables"""
    results = {}
    
    # Injury Risk Factors
    risk_factors_data = []
    risk_factors = [
        'Slip and fall hazards', 'Equipment malfunction', 'Weather conditions',
        'Student behavior', 'Inadequate supervision', 'Environmental factors',
        'Equipment age', 'Maintenance issues', 'Training gaps', 'Communication failures'
    ]
    
    for i, factor in enumerate(risk_factors):
        risk_factors_data.append({
            'name': factor,
            'description': f'Risk factor: {factor}',
            'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'category': random.choice(['EQUIPMENT', 'ENVIRONMENTAL', 'HUMAN', 'PROCEDURAL']),
            'affected_activities': json.dumps([f'Activity {j}' for j in range(random.randint(1, 5))]),
            'prevention_strategies': json.dumps([f'Strategy {j}' for j in range(random.randint(1, 3))]),
            'monitoring_frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']),
            'prevention_program_id': None,
            'risk_indicators': json.dumps([f'Indicator {j}' for j in range(random.randint(1, 3))]),
            'contributing_factors': json.dumps([f'Factor {j}' for j in range(random.randint(1, 3))]),
            'early_warning_signs': json.dumps([f'Warning {j}' for j in range(random.randint(1, 3))]),
            'impact_severity': random.choice(['MINOR', 'MODERATE', 'MAJOR', 'SEVERE']),
            'occurrence_likelihood': random.choice(['RARE', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'CERTAIN']),
            'prevention_priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'required_resources': json.dumps([f'Resource {j}' for j in range(random.randint(1, 3))]),
            'implementation_timeline': json.dumps({
                'start_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'end_date': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }),
            'success_metrics': json.dumps([f'Metric {j}' for j in range(random.randint(1, 3))]),
            'validation_criteria': json.dumps([f'Criteria {j}' for j in range(random.randint(1, 3))]),
            'next_assessment': datetime.now() + timedelta(days=random.randint(30, 365)),
            'monitoring_history': json.dumps([f'History {j}' for j in range(random.randint(1, 5))]),
            'incident_history': json.dumps([f'Incident {j}' for j in range(random.randint(1, 3))]),
            'effectiveness_metrics': json.dumps([f'Effectiveness {j}' for j in range(random.randint(1, 3))]),
            'training_requirements': json.dumps([f'Training {j}' for j in range(random.randint(1, 3))]),
            'awareness_materials': json.dumps([f'Material {j}' for j in range(random.randint(1, 3))]),
            'communication_plan': json.dumps([f'Plan {j}' for j in range(random.randint(1, 3))]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({'risk_factor_id': i+1, 'version': '1.0'}),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': True,
            'factor_metadata': json.dumps({'factor_id': i+1, 'severity_score': random.randint(1, 10)})
        })
    
    try:
        session.execute(text("""
            INSERT INTO injury_risk_factors (description, risk_level, category, affected_activities,
                                           prevention_strategies, monitoring_frequency, prevention_program_id,
                                           risk_indicators, contributing_factors, early_warning_signs,
                                           impact_severity, occurrence_likelihood, prevention_priority,
                                           required_resources, implementation_timeline, success_metrics,
                                           validation_criteria, next_assessment, monitoring_history,
                                           incident_history, effectiveness_metrics, training_requirements,
                                           awareness_materials, communication_plan, created_at, updated_at,
                                           last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                           retention_period, metadata, is_active, factor_metadata, name, status)
            VALUES (:description, :risk_level, :category, :affected_activities,
                    :prevention_strategies, :monitoring_frequency, :prevention_program_id,
                    :risk_indicators, :contributing_factors, :early_warning_signs,
                    :impact_severity, :occurrence_likelihood, :prevention_priority,
                    :required_resources, :implementation_timeline, :success_metrics,
                    :validation_criteria, :next_assessment, :monitoring_history,
                    :incident_history, :effectiveness_metrics, :training_requirements,
                    :awareness_materials, :communication_plan, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                    :retention_period, :metadata, :is_active, :factor_metadata, :name, :status)
        """), risk_factors_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['injury_risk_factors'] = len(risk_factors_data)
        print(f"  ✅ injury_risk_factors: {len(risk_factors_data)} records")
    except Exception as e:
        print(f"  ⚠️ injury_risk_factors: {e}")
        session.rollback()  # Rollback on error
        results['injury_risk_factors'] = 0
    
    # Injury Preventions
    preventions_data = []
    for i in range(40):
        preventions_data.append({
            'name': f'Prevention Measure {i+1}',
            'description': f'Preventive measure to reduce {random.choice(["slip hazards", "equipment risks", "environmental dangers", "behavioral issues"])}',
            'target_population': json.dumps([f'Population {j}' for j in range(random.randint(1, 3))]),
            'implementation_plan': json.dumps({
                'steps': [f'Step {j}' for j in range(random.randint(3, 8))],
                'timeline': f'{random.randint(1, 12)} months',
                'resources': [f'Resource {j}' for j in range(random.randint(1, 5))]
            }),
            'effectiveness_metrics': json.dumps([f'Metric {j}' for j in range(random.randint(1, 3))]),
            'cost_estimates': json.dumps({
                'implementation': random.randint(1000, 10000),
                'maintenance': random.randint(100, 1000)
            }),
            'timeline': json.dumps({
                'start_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'end_date': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }),
            'program_type': random.choice(['TRAINING', 'EQUIPMENT', 'PROCEDURAL', 'ENVIRONMENTAL']),
            'risk_factors_addressed': json.dumps([f'Risk Factor {j}' for j in range(random.randint(1, 3))]),
            'prevention_strategies': json.dumps([f'Strategy {j}' for j in range(random.randint(1, 4))]),
            'training_requirements': json.dumps([f'Training {j}' for j in range(random.randint(1, 3))]),
            'equipment_needed': json.dumps([f'Equipment {j}' for j in range(random.randint(1, 3))]),
            'success_criteria': json.dumps([f'Criteria {j}' for j in range(random.randint(1, 3))]),
            'monitoring_frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']),
            'evaluation_methods': json.dumps([f'Method {j}' for j in range(random.randint(1, 3))]),
            'reporting_requirements': json.dumps([f'Requirement {j}' for j in range(random.randint(1, 3))]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({'prevention_id': i+1, 'version': '1.0'}),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': True,
            'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'prevention_metadata': json.dumps({'prevention_id': i+1, 'effectiveness_score': random.randint(1, 10)})
        })
    
    try:
        session.execute(text("""
            INSERT INTO injury_preventions (description, target_population, implementation_plan,
                                          effectiveness_metrics, cost_estimates, timeline, program_type,
                                          risk_factors_addressed, prevention_strategies, training_requirements,
                                          equipment_needed, success_criteria, monitoring_frequency,
                                          evaluation_methods, reporting_requirements, created_at, updated_at,
                                          last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                          retention_period, metadata, name, status, is_active, risk_level, prevention_metadata)
            VALUES (:description, :target_population, :implementation_plan,
                    :effectiveness_metrics, :cost_estimates, :timeline, :program_type,
                    :risk_factors_addressed, :prevention_strategies, :training_requirements,
                    :equipment_needed, :success_criteria, :monitoring_frequency,
                    :evaluation_methods, :reporting_requirements, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                    :retention_period, :metadata, :name, :status, :is_active, :risk_level, :prevention_metadata)
        """), preventions_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['injury_preventions'] = len(preventions_data)
        print(f"  ✅ injury_preventions: {len(preventions_data)} records")
    except Exception as e:
        print(f"  ⚠️ injury_preventions: {e}")
        session.rollback()  # Rollback on error
        results['injury_preventions'] = 0
    
    # Activity Injury Preventions (linking activities to injury prevention measures)
    try:
        # Get actual prevention IDs that were just created
        prevention_result = session.execute(text("SELECT id FROM injury_preventions ORDER BY id"))
        prevention_ids = [row[0] for row in prevention_result]
        print(f"  📋 Found {len(prevention_ids)} prevention IDs for activity associations")
    except Exception as e:
        print(f"  ⚠️ Error getting prevention IDs for activity associations: {e}")
        prevention_ids = [121, 122, 123, 124, 125]
    
    activity_injury_preventions_data = []
    for i in range(150):  # 150 activity-injury prevention associations
        activity_injury_preventions_data.append({
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'prevention_id': random.choice(prevention_ids),
            'priority': random.randint(1, 5),  # 1=lowest, 5=highest priority
            'prevention_metadata': json.dumps({
                'association_id': i+1,
                'effectiveness_rating': random.randint(1, 10),
                'implementation_difficulty': random.choice(['EASY', 'MEDIUM', 'HARD']),
                'required_training': random.choice(['NONE', 'BASIC', 'ADVANCED', 'EXPERT']),
                'equipment_needed': [f'Equipment {j}' for j in range(random.randint(0, 3))],
                'time_required': random.randint(5, 60),  # minutes
                'cost_estimate': round(random.uniform(0, 1000), 2),
                'success_rate': round(random.uniform(0.5, 1.0), 2),
                'notes': f'Activity-injury prevention association {i+1}',
                'last_reviewed': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                'next_review': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(365, 2555)  # 1-7 years
        })
    
    try:
        session.execute(text("""
            INSERT INTO activity_injury_preventions (activity_id, prevention_id, priority, prevention_metadata,
                                                   created_at, updated_at, last_accessed_at, archived_at,
                                                   deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:activity_id, :prevention_id, :priority, :prevention_metadata,
                    :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period)
        """), activity_injury_preventions_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['activity_injury_preventions'] = len(activity_injury_preventions_data)
        print(f"  ✅ activity_injury_preventions: {len(activity_injury_preventions_data)} records")
    except Exception as e:
        print(f"  ⚠️ activity_injury_preventions: {e}")
        session.rollback()  # Rollback on error
        results['activity_injury_preventions'] = 0
    
    # Injury Risk Assessments
    # Get actual risk factor IDs that were just created
    try:
        risk_factor_result = session.execute(text("SELECT id FROM injury_risk_factors ORDER BY id"))
        risk_factor_ids = [row[0] for row in risk_factor_result]
        print(f"  📋 Found {len(risk_factor_ids)} risk factor IDs for assessments")
    except Exception as e:
        print(f"  ⚠️ Error getting risk factor IDs for assessments: {e}")
        risk_factor_ids = [31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    
    risk_assessments_data = []
    for i in range(25):
        risk_assessments_data.append({
            'risk_factor_id': random.choice(risk_factor_ids),  # Use actual IDs from injury_risk_factors
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'risk_score': round(random.uniform(1.0, 10.0), 2),
            'factors_considered': json.dumps({
                'hazards_identified': [f'Hazard {j}' for j in range(random.randint(1, 5))],
                'environmental_factors': [f'Environmental Factor {j}' for j in range(random.randint(1, 3))],
                'equipment_factors': [f'Equipment Factor {j}' for j in range(random.randint(1, 3))],
                'human_factors': [f'Human Factor {j}' for j in range(random.randint(1, 3))]
            }),
            'mitigation_plan': json.dumps({
                'control_measures': [f'Control {j}' for j in range(random.randint(1, 4))],
                'preventive_actions': [f'Preventive Action {j}' for j in range(random.randint(1, 3))],
                'emergency_procedures': [f'Emergency Procedure {j}' for j in range(random.randint(1, 2))]
            }),
            'assessment_method': random.choice(['QUANTITATIVE', 'QUALITATIVE', 'MIXED', 'EXPERT_JUDGMENT']),
            'data_sources': json.dumps({
                'historical_data': f'Historical data source {i}',
                'expert_opinions': f'Expert opinion {i}',
                'statistical_models': f'Statistical model {i}'
            }),
            'assessment_scope': json.dumps({
                'geographic_scope': f'Location {i}',
                'time_scope': f'{random.randint(1, 12)} months',
                'population_scope': f'{random.randint(10, 100)} people'
            }),
            'limitations': json.dumps({
                'data_limitations': [f'Data limitation {j}' for j in range(random.randint(1, 3))],
                'methodology_limitations': [f'Methodology limitation {j}' for j in range(random.randint(1, 2))],
                'assumptions': [f'Assumption {j}' for j in range(random.randint(1, 3))]
            }),
            'probability_score': round(random.uniform(0.1, 1.0), 2),
            'impact_score': round(random.uniform(0.1, 1.0), 2),
            'risk_matrix': json.dumps({
                'probability_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'impact_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'overall_risk': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
            }),
            'risk_trends': json.dumps({
                'trend_direction': random.choice(['INCREASING', 'DECREASING', 'STABLE']),
                'trend_factors': [f'Trend factor {j}' for j in range(random.randint(1, 3))],
                'projected_risk': round(random.uniform(1.0, 10.0), 2)
            }),
            'existing_controls': json.dumps({
                'administrative_controls': [f'Admin control {j}' for j in range(random.randint(1, 3))],
                'engineering_controls': [f'Engineering control {j}' for j in range(random.randint(1, 3))],
                'ppe_controls': [f'PPE control {j}' for j in range(random.randint(1, 2))]
            }),
            'proposed_controls': json.dumps({
                'new_controls': [f'New control {j}' for j in range(random.randint(1, 3))],
                'improvements': [f'Improvement {j}' for j in range(random.randint(1, 2))],
                'cost_estimate': random.randint(1000, 10000)
            }),
            'control_effectiveness': json.dumps({
                'effectiveness_rating': random.randint(1, 10),
                'implementation_status': random.choice(['PLANNED', 'IN_PROGRESS', 'COMPLETED']),
                'effectiveness_notes': f'Effectiveness notes for assessment {i}'
            }),
            'residual_risk': round(random.uniform(0.1, 5.0), 2),
            'action_items': json.dumps({
                'immediate_actions': [f'Immediate action {j}' for j in range(random.randint(1, 3))],
                'short_term_actions': [f'Short term action {j}' for j in range(random.randint(1, 3))],
                'long_term_actions': [f'Long term action {j}' for j in range(random.randint(1, 2))]
            }),
            'responsible_parties': json.dumps({
                'primary_responsible': f'Person {random.randint(1, 10)}',
                'supporting_team': [f'Team member {j}' for j in range(random.randint(1, 3))],
                'oversight': f'Oversight person {random.randint(1, 5)}'
            }),
            'timeline': json.dumps({
                'start_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'target_completion': (datetime.now() + timedelta(days=random.randint(30, 90))).isoformat(),
                'milestones': [f'Milestone {j}' for j in range(random.randint(1, 3))]
            }),
            'resource_requirements': json.dumps({
                'budget_required': random.randint(5000, 50000),
                'personnel_hours': random.randint(40, 200),
                'equipment_needed': [f'Equipment {j}' for j in range(random.randint(1, 3))]
            }),
            'monitoring_requirements': json.dumps({
                'frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']),
                'metrics': [f'Metric {j}' for j in range(random.randint(1, 3))],
                'reporting_requirements': [f'Report {j}' for j in range(random.randint(1, 2))]
            }),
            'review_frequency': random.choice(['MONTHLY', 'QUARTERLY', 'ANNUALLY', 'AS_NEEDED']),
            'next_review_date': datetime.now() + timedelta(days=random.randint(30, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'last_accessed_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({
                'assessment_id': i + 1,
                'version': '1.0',
                'assessor_id': random.choice(user_ids)
            }),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED']),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO injury_risk_assessments (risk_factor_id, activity_id, risk_score, factors_considered,
                                               mitigation_plan, assessment_method, data_sources, assessment_scope,
                                               limitations, probability_score, impact_score, risk_matrix, risk_trends,
                                               existing_controls, proposed_controls, control_effectiveness, residual_risk,
                                               action_items, responsible_parties, timeline, resource_requirements,
                                               monitoring_requirements, review_frequency, next_review_date, created_at,
                                               updated_at, last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                               retention_period, metadata, status, is_active)
            VALUES (:risk_factor_id, :activity_id, :risk_score, :factors_considered,
                    :mitigation_plan, :assessment_method, :data_sources, :assessment_scope,
                    :limitations, :probability_score, :impact_score, :risk_matrix, :risk_trends,
                    :existing_controls, :proposed_controls, :control_effectiveness, :residual_risk,
                    :action_items, :responsible_parties, :timeline, :resource_requirements,
                    :monitoring_requirements, :review_frequency, :next_review_date, :created_at,
                    :updated_at, :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                    :retention_period, :metadata, :status, :is_active)
        """), risk_assessments_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['injury_risk_assessments'] = len(risk_assessments_data)
        print(f"  ✅ injury_risk_assessments: {len(risk_assessments_data)} records")
    except Exception as e:
        print(f"  ⚠️ injury_risk_assessments: {e}")
        session.rollback()  # Rollback on error
        results['injury_risk_assessments'] = 0
    
    # Injury Prevention Risk Assessments
    # Get actual prevention IDs that were just created
    try:
        prevention_result = session.execute(text("SELECT id FROM injury_preventions ORDER BY id"))
        prevention_ids = [row[0] for row in prevention_result]
        print(f"  📋 Found {len(prevention_ids)} prevention IDs for assessments")
    except Exception as e:
        print(f"  ⚠️ Error getting prevention IDs for assessments: {e}")
        prevention_ids = [121, 122, 123, 124, 125]
    
    prevention_assessments_data = []
    for i in range(20):
        prevention_assessments_data.append({
            'prevention_program_id': random.choice(prevention_ids),  # Use actual IDs from injury_preventions
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 60)),
            'overall_risk_score': random.uniform(1.0, 10.0),
            'risk_factors_evaluated': json.dumps([f'Risk Factor {j}' for j in range(random.randint(1, 5))]),
            'recommendations': json.dumps([f'Recommendation {j}' for j in range(random.randint(1, 3))]),
            'assessment_method': random.choice(['QUANTITATIVE', 'QUALITATIVE', 'MIXED', 'EXPERT_JUDGMENT']),
            'assessor': f'Assessor {random.randint(1, 20)}',
            'data_sources': json.dumps([f'Source {j}' for j in range(random.randint(1, 3))]),
            'limitations': json.dumps([f'Limitation {j}' for j in range(random.randint(1, 3))]),
            'high_risk_areas': json.dumps([f'High Risk Area {j}' for j in range(random.randint(1, 3))]),
            'medium_risk_areas': json.dumps([f'Medium Risk Area {j}' for j in range(random.randint(1, 3))]),
            'low_risk_areas': json.dumps([f'Low Risk Area {j}' for j in range(random.randint(1, 3))]),
            'risk_trends': json.dumps([f'Trend {j}' for j in range(random.randint(1, 3))]),
            'immediate_actions': json.dumps([f'Immediate Action {j}' for j in range(random.randint(1, 3))]),
            'short_term_actions': json.dumps([f'Short Term Action {j}' for j in range(random.randint(1, 3))]),
            'long_term_actions': json.dumps([f'Long Term Action {j}' for j in range(random.randint(1, 3))]),
            'responsible_parties': json.dumps([f'Party {j}' for j in range(random.randint(1, 3))]),
            'next_assessment_date': datetime.now() + timedelta(days=random.randint(90, 365)),
            'monitoring_plan': json.dumps([f'Plan {j}' for j in range(random.randint(1, 3))]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({'assessment_id': i+1, 'version': '1.0'}),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO injury_prevention_risk_assessments (prevention_program_id, assessment_date, overall_risk_score,
                                                          risk_factors_evaluated, recommendations, assessment_method,
                                                          assessor, data_sources, limitations, high_risk_areas,
                                                          medium_risk_areas, low_risk_areas, risk_trends,
                                                          immediate_actions, short_term_actions, long_term_actions,
                                                          responsible_parties, next_assessment_date, monitoring_plan,
                                                          created_at, updated_at, last_accessed_at, archived_at,
                                                          deleted_at, scheduled_deletion_at, retention_period,
                                                          metadata, status, is_active)
            VALUES (:prevention_program_id, :assessment_date, :overall_risk_score,
                    :risk_factors_evaluated, :recommendations, :assessment_method,
                    :assessor, :data_sources, :limitations, :high_risk_areas,
                    :medium_risk_areas, :low_risk_areas, :risk_trends,
                    :immediate_actions, :short_term_actions, :long_term_actions,
                    :responsible_parties, :next_assessment_date, :monitoring_plan,
                    :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period,
                    :metadata, :status, :is_active)
        """), prevention_assessments_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['injury_prevention_risk_assessments'] = len(prevention_assessments_data)
        print(f"  ✅ injury_prevention_risk_assessments: {len(prevention_assessments_data)} records")
    except Exception as e:
        print(f"  ⚠️ injury_prevention_risk_assessments: {e}")
        session.rollback()  # Rollback on error
        results['injury_prevention_risk_assessments'] = 0
    
    # Injury Risk Factor Safety Guidelines
    # Generate unique combinations to avoid duplicate key violations
    risk_guidelines_data = []
    used_combinations = set()
    
    # Get actual risk factor IDs
    try:
        risk_factor_result = session.execute(text("SELECT id FROM injury_risk_factors ORDER BY id"))
        risk_factor_ids = [row[0] for row in risk_factor_result]
        print(f"  📋 Found {len(risk_factor_ids)} risk factor IDs")
    except Exception as e:
        print(f"  ⚠️ Error getting risk factor IDs: {e}")
        risk_factor_ids = [31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    
    # Get actual safety guideline IDs
    try:
        guideline_result = session.execute(text("SELECT id FROM safety_guidelines ORDER BY id"))
        guideline_ids = [row[0] for row in guideline_result]
        print(f"  📋 Found {len(guideline_ids)} safety guideline IDs")
    except Exception as e:
        print(f"  ⚠️ Error getting safety guideline IDs: {e}")
        guideline_ids = list(range(1, 76))
    
    # Generate unique combinations
    max_combinations = min(15, len(risk_factor_ids) * len(guideline_ids))
    attempts = 0
    max_attempts = 1000
    
    while len(risk_guidelines_data) < max_combinations and attempts < max_attempts:
        risk_factor_id = random.choice(risk_factor_ids)
        guideline_id = random.choice(guideline_ids)
        combination = (risk_factor_id, guideline_id)
        
        if combination not in used_combinations:
            used_combinations.add(combination)
            risk_guidelines_data.append({
                'risk_factor_id': risk_factor_id,
                'safety_guideline_id': guideline_id
            })
        attempts += 1
    
    try:
        session.execute(text("""
            INSERT INTO injury_risk_factor_safety_guidelines (risk_factor_id, safety_guideline_id)
            VALUES (:risk_factor_id, :safety_guideline_id)
        """), risk_guidelines_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['injury_risk_factor_safety_guidelines'] = len(risk_guidelines_data)
        print(f"  ✅ injury_risk_factor_safety_guidelines: {len(risk_guidelines_data)} records")
    except Exception as e:
        print(f"  ⚠️ injury_risk_factor_safety_guidelines: {e}")
        session.rollback()  # Rollback on error
        results['injury_risk_factor_safety_guidelines'] = 0
    
    # Prevention Measures (must come first since prevention_assessments depends on it)
    # Get actual risk factor IDs that were just created
    try:
        risk_factor_result = session.execute(text("SELECT id FROM injury_risk_factors ORDER BY id"))
        risk_factor_ids = [row[0] for row in risk_factor_result]
        print(f"  📋 Found {len(risk_factor_ids)} risk factor IDs for measures")
    except Exception as e:
        print(f"  ⚠️ Error getting risk factor IDs for measures: {e}")
        risk_factor_ids = [31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    
    prevention_measures_data = []
    for i in range(50):
        prevention_measures_data.append({
            'risk_factor_id': random.choice(risk_factor_ids),  # Use actual IDs from injury_risk_factors
            'description': f'Preventive measure {i+1} for safety improvement',
            'implementation_steps': json.dumps({
                'steps': [f'Step {j}' for j in range(random.randint(3, 6))],
                'timeline': f'{random.randint(1, 8)} weeks',
                'resources': [f'Resource {j}' for j in range(random.randint(1, 4))]
            }),
            'effectiveness_rating': round(random.uniform(1.0, 10.0), 2),
            'next_scheduled': datetime.now() + timedelta(days=random.randint(30, 365)),
            'target_population': json.dumps([f'Population {j}' for j in range(random.randint(1, 3))]),
            'required_equipment': json.dumps([f'Equipment {j}' for j in range(random.randint(1, 3))]),
            'training_needed': json.dumps([f'Training {j}' for j in range(random.randint(1, 3))]),
            'cost_estimates': json.dumps({
                'implementation': random.randint(1000, 10000),
                'maintenance': random.randint(100, 1000)
            }),
            'timeline': json.dumps({
                'start_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'end_date': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }),
            'success_criteria': json.dumps([f'Criteria {j}' for j in range(random.randint(1, 3))]),
            'monitoring_metrics': json.dumps([f'Metric {j}' for j in range(random.randint(1, 3))]),
            'evaluation_frequency': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']),
            'compliance_metrics': json.dumps([f'Compliance {j}' for j in range(random.randint(1, 3))]),
            'feedback_mechanism': json.dumps([f'Feedback {j}' for j in range(random.randint(1, 3))]),
            'modification_history': json.dumps([f'Modification {j}' for j in range(random.randint(1, 3))]),
            'improvement_suggestions': json.dumps([f'Suggestion {j}' for j in range(random.randint(1, 3))]),
            'lessons_learned': json.dumps([f'Lesson {j}' for j in range(random.randint(1, 3))]),
            'documentation_required': json.dumps([f'Document {j}' for j in range(random.randint(1, 3))]),
            'reporting_requirements': json.dumps([f'Requirement {j}' for j in range(random.randint(1, 3))]),
            'review_schedule': json.dumps([f'Schedule {j}' for j in range(random.randint(1, 3))]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({'measure_id': i+1, 'version': '1.0'}),
            'name': f'Prevention Measure {i+1}',
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': True,
            'effectiveness': random.choice(['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']),
            'measure_metadata': json.dumps({'measure_id': i+1, 'effectiveness_score': random.randint(1, 10)})
        })
    
    try:
        session.execute(text("""
            INSERT INTO prevention_measures (risk_factor_id, description, implementation_steps,
                                           effectiveness_rating, next_scheduled, target_population,
                                           required_equipment, training_needed, cost_estimates,
                                           timeline, success_criteria, monitoring_metrics,
                                           evaluation_frequency, compliance_metrics, feedback_mechanism,
                                           modification_history, improvement_suggestions, lessons_learned,
                                           documentation_required, reporting_requirements, review_schedule,
                                           created_at, updated_at, last_accessed_at, archived_at,
                                           deleted_at, scheduled_deletion_at, retention_period,
                                           metadata, name, status, is_active, effectiveness, measure_metadata)
            VALUES (:risk_factor_id, :description, :implementation_steps,
                    :effectiveness_rating, :next_scheduled, :target_population,
                    :required_equipment, :training_needed, :cost_estimates,
                    :timeline, :success_criteria, :monitoring_metrics,
                    :evaluation_frequency, :compliance_metrics, :feedback_mechanism,
                    :modification_history, :improvement_suggestions, :lessons_learned,
                    :documentation_required, :reporting_requirements, :review_schedule,
                    :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period,
                    :metadata, :name, :status, :is_active, :effectiveness, :measure_metadata)
        """), prevention_measures_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['prevention_measures'] = len(prevention_measures_data)
        print(f"  ✅ prevention_measures: {len(prevention_measures_data)} records")
    except Exception as e:
        print(f"  ⚠️ prevention_measures: {e}")
        session.rollback()  # Rollback on error
        results['prevention_measures'] = 0
    
    # Prevention Assessments (depends on prevention_measures)
    # Get actual measure IDs that were just created
    try:
        measure_result = session.execute(text("SELECT id FROM prevention_measures ORDER BY id"))
        measure_ids = [row[0] for row in measure_result]
        print(f"  📋 Found {len(measure_ids)} measure IDs for assessments")
    except Exception as e:
        print(f"  ⚠️ Error getting measure IDs for assessments: {e}")
        measure_ids = list(range(1, 51))
    
    prevention_assessments_data = []
    for i in range(30):
        prevention_assessments_data.append({
            'measure_id': random.choice(measure_ids),  # Use actual IDs from prevention_measures
            'effectiveness_score': round(random.uniform(1.0, 10.0), 2),
            'compliance_rate': round(random.uniform(0.0, 1.0), 2),
            'feedback': f'Assessment feedback {i+1}',
            'recommendations': f'Recommendations for assessment {i+1}',
            'next_assessment_date': datetime.now() + timedelta(days=random.randint(30, 180)),
            'assessment_type': random.choice(['QUARTERLY', 'ANNUAL', 'AD_HOC', 'FOLLOW_UP']),
            'assessment_method': random.choice(['QUANTITATIVE', 'QUALITATIVE', 'MIXED', 'EXPERT_JUDGMENT']),
            'data_collected': json.dumps([f'Data {j}' for j in range(random.randint(1, 3))]),
            'analysis_results': json.dumps([f'Result {j}' for j in range(random.randint(1, 3))]),
            'key_findings': json.dumps([f'Finding {j}' for j in range(random.randint(1, 3))]),
            'impact_metrics': json.dumps([f'Metric {j}' for j in range(random.randint(1, 3))]),
            'cost_benefit_analysis': json.dumps([f'Analysis {j}' for j in range(random.randint(1, 3))]),
            'resource_utilization': json.dumps([f'Resource {j}' for j in range(random.randint(1, 3))]),
            'implementation_quality': round(random.uniform(1.0, 10.0), 2),
            'action_items': json.dumps([f'Action {j}' for j in range(random.randint(1, 3))]),
            'follow_up_required': random.choice([True, False]),
            'follow_up_date': datetime.now() + timedelta(days=random.randint(30, 90)),
            'responsible_parties': json.dumps([f'Party {j}' for j in range(random.randint(1, 3))]),
            'supporting_evidence': json.dumps([f'Evidence {j}' for j in range(random.randint(1, 3))]),
            'assessment_notes': f'Assessment notes {i+1}',
            'limitations': json.dumps([f'Limitation {j}' for j in range(random.randint(1, 3))]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 45)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7),
            'metadata': json.dumps({'assessment_id': i+1, 'version': '1.0'}),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': True,
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'risk_factor_id': random.choice(risk_factor_ids),
            'assessment_date': datetime.now() - timedelta(days=random.randint(1, 45)),
            'effectiveness': random.choice(['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']),
            'assessment_metadata': json.dumps({'assessment_id': i+1, 'effectiveness_score': random.randint(1, 10)})
        })
    
    try:
        session.execute(text("""
            INSERT INTO prevention_assessments (measure_id, effectiveness_score, compliance_rate,
                                              feedback, recommendations, next_assessment_date,
                                              assessment_type, assessment_method, data_collected,
                                              analysis_results, key_findings, impact_metrics,
                                              cost_benefit_analysis, resource_utilization,
                                              implementation_quality, action_items, follow_up_required,
                                              follow_up_date, responsible_parties, supporting_evidence,
                                              assessment_notes, limitations, created_at, updated_at,
                                              last_accessed_at, archived_at, deleted_at,
                                              scheduled_deletion_at, retention_period, metadata,
                                              status, is_active, activity_id, risk_factor_id,
                                              assessment_date, effectiveness, assessment_metadata)
            VALUES (:measure_id, :effectiveness_score, :compliance_rate,
                    :feedback, :recommendations, :next_assessment_date,
                    :assessment_type, :assessment_method, :data_collected,
                    :analysis_results, :key_findings, :impact_metrics,
                    :cost_benefit_analysis, :resource_utilization,
                    :implementation_quality, :action_items, :follow_up_required,
                    :follow_up_date, :responsible_parties, :supporting_evidence,
                    :assessment_notes, :limitations, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period, :metadata,
                    :status, :is_active, :activity_id, :risk_factor_id,
                    :assessment_date, :effectiveness, :assessment_metadata)
        """), prevention_assessments_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['prevention_assessments'] = len(prevention_assessments_data)
        print(f"  ✅ prevention_assessments: {len(prevention_assessments_data)} records")
    except Exception as e:
        print(f"  ⚠️ prevention_assessments: {e}")
        session.rollback()  # Rollback on error
        results['prevention_assessments'] = 0
    
    return results

def seed_equipment_management(session: Session, user_ids: List[int], school_ids: List[int], activity_ids: List[int]) -> Dict[str, int]:
    """Seed equipment management tables"""
    results = {}
    
    # Equipment Categories
    categories_data = []
    categories = [
        'Sports Equipment', 'Safety Equipment', 'Maintenance Tools', 'Technology Equipment',
        'Emergency Equipment', 'Environmental Equipment', 'Medical Equipment', 'Communication Equipment'
    ]
    
    for i, category in enumerate(categories):
        categories_data.append({
            'name': category,
            'description': f'Equipment category for {category.lower()}',
            'parent_id': None,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_categories (name, description, parent_id, created_at, updated_at,
                                            last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :parent_id, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), categories_data)
        results['equipment_categories'] = len(categories_data)
        print(f"  ✅ equipment_categories: {len(categories_data)} records")
        
        # Get the actual category IDs that were created
        category_result = session.execute(text("SELECT id FROM equipment_categories ORDER BY id"))
        category_ids = [row[0] for row in category_result.fetchall()]
        print(f"  📋 Created category IDs: {category_ids}")
    except Exception as e:
        print(f"  ⚠️ equipment_categories: {e}")
        results['equipment_categories'] = 0
        category_ids = []
    
    # Equipment Types
    types_data = []
    equipment_types = [
        'Basketball', 'Soccer Ball', 'Safety Helmet', 'First Aid Kit', 'Fire Extinguisher',
        'Computer', 'Projector', 'Communication Radio', 'Weather Station', 'Maintenance Tool'
    ]
    
    for i, eq_type in enumerate(equipment_types):
        types_data.append({
            'name': eq_type,
            'description': f'Equipment type: {eq_type}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_types (name, description, created_at, updated_at,
                                       last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), types_data)
        results['equipment_types'] = len(types_data)
        print(f"  ✅ equipment_types: {len(types_data)} records")
        
        # Get the actual type IDs that were created
        type_result = session.execute(text("SELECT id FROM equipment_types ORDER BY id"))
        type_ids = [row[0] for row in type_result.fetchall()]
        print(f"  📋 Created type IDs: {type_ids}")
    except Exception as e:
        print(f"  ⚠️ equipment_types: {e}")
        results['equipment_types'] = 0
        type_ids = []
    
    # Equipment Conditions (must be created before physical_education_equipment)
    conditions_data = []
    for i in range(5):
        conditions_data.append({
            'name': f'Condition {i+1}',
            'description': f'Equipment condition level {i+1}',
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_conditions (name, description, severity, created_at, updated_at,
                                            last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :severity, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), conditions_data)
        results['equipment_conditions'] = len(conditions_data)
        print(f"  ✅ equipment_conditions: {len(conditions_data)} records")
        
        # Get the actual condition IDs that were created
        condition_result = session.execute(text("SELECT id FROM equipment_conditions ORDER BY id"))
        condition_ids = [row[0] for row in condition_result.fetchall()]
        print(f"  📋 Created condition IDs: {condition_ids}")
    except Exception as e:
        print(f"  ⚠️ equipment_conditions: {e}")
        results['equipment_conditions'] = 0
        condition_ids = []
    
    # Physical Education Equipment (main equipment table)
    pe_equipment_data = []
    for i in range(100):
        pe_equipment_data.append({
            'name': f'Equipment {i+1}',
            'description': f'Equipment item {i+1} for {random.choice(["sports", "safety", "maintenance", "technology"])}',
            'quantity': random.randint(1, 10),
            'condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL']),
            'condition_id': random.choice(condition_ids) if condition_ids else 1, # References equipment_conditions
            'location': f'Location {random.randint(1, 20)}',
            'equipment_metadata': json.dumps({
                'serial_number': f'SN{random.randint(100000, 999999)}',
                'model': f'Model {random.randint(1, 50)}',
                'manufacturer': random.choice(['Nike', 'Adidas', 'Wilson', 'Spalding', 'Generic']),
                'purchase_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).isoformat(),
                'warranty_expiry': (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat(),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'MAINTENANCE', 'RETIRED']),
                'last_inspection': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                'next_inspection': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }),
            'category_id': random.choice(category_ids) if category_ids else 1,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO physical_education_equipment (name, description, quantity, condition, condition_id,
                                                    location, equipment_metadata, category_id, created_at, updated_at,
                                                    last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :quantity, :condition, :condition_id,
                    :location, :equipment_metadata, :category_id, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), pe_equipment_data)
        results['physical_education_equipment'] = len(pe_equipment_data)
        print(f"  ✅ physical_education_equipment: {len(pe_equipment_data)} records")
        
        # Get the actual equipment IDs that were created
        equipment_result = session.execute(text("SELECT id FROM physical_education_equipment ORDER BY id"))
        equipment_ids = [row[0] for row in equipment_result.fetchall()]
        print(f"  📋 Created equipment IDs: {equipment_ids[:10]}... (showing first 10)")
    except Exception as e:
        print(f"  ⚠️ physical_education_equipment: {e}")
        results['physical_education_equipment'] = 0
        equipment_ids = []
    
    # Equipment Checks (references physical_education_equipment)
    equipment_checks_data = []
    for i in range(150):
        equipment_checks_data.append({
            'class_id': random.choice([1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]),  # Random class ID
            'equipment_id': str(random.choice(equipment_ids)) if equipment_ids else '1',  # String equipment ID
            'check_date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'maintenance_status': random.choice([True, False]),
            'damage_status': random.choice([True, False]),
            'age_status': random.choice([True, False]),
            'last_maintenance': datetime.now() - timedelta(days=random.randint(1, 90)) if random.choice([True, False]) else None,
            'purchase_date': datetime.now() - timedelta(days=random.randint(365, 1095)),
            'max_age_years': random.uniform(5.0, 15.0),
            'equipment_metadata': json.dumps({
                'check_notes': f'Equipment check notes for equipment {i+1}',
                'inspected_by': random.choice(user_ids),
                'check_type': random.choice(['ROUTINE', 'INSPECTION', 'MAINTENANCE', 'SAFETY']),
                'condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL'])
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_checks (class_id, equipment_id, check_date, maintenance_status,
                                        damage_status, age_status, last_maintenance, purchase_date,
                                        max_age_years, equipment_metadata)
            VALUES (:class_id, :equipment_id, :check_date, :maintenance_status,
                    :damage_status, :age_status, :last_maintenance, :purchase_date,
                    :max_age_years, :equipment_metadata)
        """), equipment_checks_data)
        results['equipment_checks'] = len(equipment_checks_data)
        print(f"  ✅ equipment_checks: {len(equipment_checks_data)} records")
    except Exception as e:
        print(f"  ⚠️ equipment_checks: {e}")
        results['equipment_checks'] = 0
    
    # Equipment Status (lookup table for status definitions)
    status_data = []
    status_names = ['AVAILABLE', 'IN_USE', 'MAINTENANCE', 'OUT_OF_ORDER', 'RETIRED', 'ASSIGNED', 'PENDING', 'ACTIVE', 'INACTIVE']
    for i, status_name in enumerate(status_names):
        status_data.append({
            'name': status_name,
            'description': f'Equipment status: {status_name.lower().replace("_", " ")}',
            'is_active': True,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_status (name, description, is_active, created_at, updated_at,
                                        last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :is_active, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), status_data)
        results['equipment_status'] = len(status_data)
        print(f"  ✅ equipment_status: {len(status_data)} records")
    except Exception as e:
        print(f"  ⚠️ equipment_status: {e}")
        results['equipment_status'] = 0
    
    # Equipment Usage
    usage_data = []
    for i in range(200):
        usage_data.append({
            'equipment_id': random.choice(equipment_ids) if equipment_ids else 1,
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'usage_date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'quantity_used': random.randint(1, 10),
            'usage_notes': f'Usage notes for equipment {i+1}',
            'usage_metadata': json.dumps({
                'user_id': random.choice(user_ids),
                'duration_minutes': random.randint(15, 120),
                'usage_type': random.choice(['PRACTICE', 'COMPETITION', 'TRAINING', 'DEMONSTRATION']),
                'location': f'Location {random.randint(1, 20)}',
                'instructor': f'Instructor {random.randint(1, 10)}',
                'weather_conditions': random.choice(['SUNNY', 'CLOUDY', 'RAINY', 'WINDY']),
                'equipment_condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR'])
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_usage (equipment_id, activity_id, usage_date, quantity_used,
                                       usage_notes, usage_metadata, created_at, updated_at,
                                       last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:equipment_id, :activity_id, :usage_date, :quantity_used,
                    :usage_notes, :usage_metadata, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), usage_data)
        results['equipment_usage'] = len(usage_data)
        print(f"  ✅ equipment_usage: {len(usage_data)} records")
    except Exception as e:
        print(f"  ⚠️ equipment_usage: {e}")
        results['equipment_usage'] = 0
    
    # First, populate the equipment table with IDs from equipment_base
    equipment_base_result = session.execute(text('SELECT id FROM equipment_base ORDER BY id'))
    equipment_base_ids = [row[0] for row in equipment_base_result.fetchall()]
    
    if equipment_base_ids:
        # Insert equipment IDs that reference equipment_base
        equipment_data = [{'id': eq_id} for eq_id in equipment_base_ids]
        try:
            session.execute(text("""
                INSERT INTO equipment (id) 
                VALUES (:id) 
                ON CONFLICT (id) DO NOTHING
            """), equipment_data)
            results['equipment'] = len(equipment_data)
            print(f"  ✅ equipment: {len(equipment_data)} records (referencing equipment_base)")
        except Exception as e:
            print(f"  ⚠️ equipment: {e}")
    
    # Equipment Maintenance
    maintenance_data = []
    for i in range(75):
        maintenance_data.append({
            'equipment_id': random.choice(equipment_base_ids) if equipment_base_ids else random.randint(1, 25),
            'maintenance_type': random.choice(['ROUTINE', 'REPAIR', 'INSPECTION', 'CLEANING', 'CALIBRATION']),
            'description': f'Maintenance performed on equipment {i+1}',
            'performed_by': f'Technician {random.randint(1, 10)}',
            'cost': round(random.uniform(50.0, 500.0), 2),
            'notes': f'Maintenance notes for equipment {i+1}'
        })
    
    try:
        session.execute(text("""
            INSERT INTO equipment_maintenance (equipment_id, maintenance_type, description,
                                             performed_by, cost, notes)
            VALUES (:equipment_id, :maintenance_type, :description,
                    :performed_by, :cost, :notes)
        """), maintenance_data)
        results['equipment_maintenance'] = len(maintenance_data)
        print(f"  ✅ equipment_maintenance: {len(maintenance_data)} records")
    except Exception as e:
        print(f"  ⚠️ equipment_maintenance: {e}")
        results['equipment_maintenance'] = 0
    
    # Maintenance Records
    maintenance_records_data = []
    for i in range(100):
        maintenance_records_data.append({
            'equipment_id': random.choice(equipment_ids) if equipment_ids else random.randint(1, 100),
            'maintenance_type': random.choice(['SCHEDULED', 'EMERGENCY', 'PREVENTIVE', 'CORRECTIVE']),
            'maintenance_date': datetime.now() - timedelta(days=random.randint(1, 60)),
            'description': f'Maintenance record for equipment {i+1}',
            'performed_by': f'Technician {random.randint(1, 10)}',
            'maintainer_id': random.randint(1, 10),
            'cost': round(random.uniform(25.0, 300.0), 2),
            'record_metadata': json.dumps({
                'duration_hours': round(random.uniform(0.5, 8.0), 1),
                'parts_used': [f'Part {j}' for j in range(random.randint(0, 3))],
                'notes': f'Maintenance notes for record {i+1}',
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'location': f'Location {random.randint(1, 20)}'
            }),
            'next_maintenance_date': datetime.now() + timedelta(days=random.randint(30, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO maintenance_records (equipment_id, maintenance_type, maintenance_date,
                                           description, performed_by, maintainer_id, cost,
                                           record_metadata, next_maintenance_date, created_at,
                                           updated_at, last_accessed_at, archived_at, deleted_at,
                                           scheduled_deletion_at, retention_period)
            VALUES (:equipment_id, :maintenance_type, :maintenance_date,
                    :description, :performed_by, :maintainer_id, :cost,
                    :record_metadata, :next_maintenance_date, :created_at,
                    :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), maintenance_records_data)
        results['maintenance_records'] = len(maintenance_records_data)
        print(f"  ✅ maintenance_records: {len(maintenance_records_data)} records")
    except Exception as e:
        print(f"  ⚠️ maintenance_records: {e}")
        results['maintenance_records'] = 0
    
    # Physical Education Equipment (equipment definitions, not assignments)
    pe_equipment_data = []
    equipment_names = [
        'Basketball', 'Soccer Ball', 'Volleyball', 'Tennis Racket', 'Baseball Bat',
        'Jump Rope', 'Hula Hoop', 'Frisbee', 'Cones', 'Stopwatch',
        'Yoga Mat', 'Resistance Bands', 'Medicine Ball', 'Agility Ladder', 'Balance Beam',
        'Trampoline', 'Climbing Rope', 'Parallel Bars', 'Vaulting Box', 'Pommel Horse'
    ]
    
    for i in range(50):
        pe_equipment_data.append({
            'name': f'{random.choice(equipment_names)} {i+1}',
            'description': f'Physical education equipment item {i+1} for various activities',
            'quantity': random.randint(1, 20),
            'condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR']),
            'condition_id': random.choice(condition_ids) if condition_ids else random.randint(1, 5),
            'location': f'Storage Room {random.randint(1, 10)}',
            'equipment_metadata': json.dumps({
                'brand': f'Brand {random.randint(1, 10)}',
                'model': f'Model {random.randint(1, 100)}',
                'purchase_date': (datetime.now() - timedelta(days=random.randint(30, 1000))).isoformat(),
                'warranty_expires': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                'maintenance_notes': f'Maintenance notes for equipment {i+1}',
                'safety_requirements': random.choice(['NONE', 'HELMET', 'PADS', 'SUPERVISION']),
                'age_group': random.choice(['ELEMENTARY', 'MIDDLE', 'HIGH', 'ALL'])
            }),
            'category_id': random.choice(category_ids) if category_ids else random.randint(1, 8),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO physical_education_equipment (name, description, quantity, condition,
                                                    condition_id, location, equipment_metadata,
                                                    category_id, created_at, updated_at,
                                                    last_accessed_at, archived_at, deleted_at,
                                                    scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :quantity, :condition,
                    :condition_id, :location, :equipment_metadata,
                    :category_id, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), pe_equipment_data)
        results['physical_education_equipment'] = len(pe_equipment_data)
        print(f"  ✅ physical_education_equipment: {len(pe_equipment_data)} records")
    except Exception as e:
        print(f"  ⚠️ physical_education_equipment: {e}")
        results['physical_education_equipment'] = 0
    
    # Physical Education Equipment Maintenance
    pe_maintenance_data = []
    for i in range(30):
        pe_maintenance_data.append({
            'equipment_id': random.choice(equipment_ids) if equipment_ids else random.randint(1, 100),
            'maintenance_date': datetime.now() - timedelta(days=random.randint(1, 45)),
            'maintenance_type': random.choice(['CLEANING', 'INSPECTION', 'REPAIR', 'REPLACEMENT']),
            'description': f'PE equipment maintenance {i+1}',
            'cost': round(random.uniform(20.0, 200.0), 2),
            'performed_by': f'Technician {random.randint(1, 10)}',
            'maintenance_metadata': json.dumps({
                'technician_id': random.choice(user_ids),
                'duration_hours': round(random.uniform(0.5, 4.0), 1),
                'parts_used': [f'Part {j}' for j in range(random.randint(0, 2))],
                'notes': f'Maintenance notes for PE equipment {i+1}',
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'location': f'Storage Room {random.randint(1, 10)}'
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 45)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 45)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO physical_education_equipment_maintenance (equipment_id, maintenance_date,
                                                                maintenance_type, description, cost,
                                                                performed_by, maintenance_metadata,
                                                                created_at, updated_at, last_accessed_at,
                                                                archived_at, deleted_at, scheduled_deletion_at,
                                                                retention_period)
            VALUES (:equipment_id, :maintenance_date,
                    :maintenance_type, :description, :cost,
                    :performed_by, :maintenance_metadata,
                    :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at,
                    :retention_period)
        """), pe_maintenance_data)
        results['physical_education_equipment_maintenance'] = len(pe_maintenance_data)
        print(f"  ✅ physical_education_equipment_maintenance: {len(pe_maintenance_data)} records")
    except Exception as e:
        print(f"  ⚠️ physical_education_equipment_maintenance: {e}")
        results['physical_education_equipment_maintenance'] = 0
    
    # Safety Reports (after equipment is seeded)
    print("  📋 Seeding safety reports...")
    safety_reports_data = []
    for i in range(25):
        safety_reports_data.append({
            'equipment_id': random.choice(equipment_ids) if equipment_ids else random.randint(1, 100),  # Use actual physical_education_equipment IDs
            'reported_by': random.choice(user_ids),
            'report_type': random.choice(['INCIDENT', 'INSPECTION', 'AUDIT', 'COMPLIANCE']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'description': f'Detailed safety report {i+1} covering {random.choice(["incident investigation", "safety inspection", "compliance audit", "risk assessment"])}',
            'action_needed': f'Action required for safety report {i+1}: {random.choice(["Immediate inspection", "Equipment replacement", "Training update", "Procedure review"])}',
            'is_resolved': random.choice([True, False]),
            'resolved_at': datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None,
            'resolution_notes': f'Resolution notes for safety report {i+1}' if random.choice([True, False]) else None,
            'images': json.dumps([f'image_{j}.jpg' for j in range(random.randint(0, 3))]),
            'report_metadata': json.dumps({
                'title': f'Safety Report {i+1}',
                'findings': {
                    'issues_identified': [f'Issue {j}' for j in range(random.randint(1, 4))],
                    'recommendations': [f'Recommendation {j}' for j in range(random.randint(1, 3))],
                    'action_items': [f'Action {j}' for j in range(random.randint(1, 3))]
                },
                'status': random.choice(['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'CLOSED']),
                'follow_up_required': random.choice([True, False]),
                'follow_up_date': (datetime.now() + timedelta(days=random.randint(7, 30))).isoformat() if random.choice([True, False]) else None
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'retention_period': random.randint(30, 365)
        })
    
    try:
        session.execute(text("""
            INSERT INTO safety_reports (equipment_id, reported_by, report_type, severity, description, action_needed,
                                      is_resolved, resolved_at, resolution_notes, images, report_metadata,
                                      created_at, updated_at, last_accessed_at, retention_period)
            VALUES (:equipment_id, :reported_by, :report_type, :severity, :description, :action_needed,
                    :is_resolved, :resolved_at, :resolution_notes, :images, :report_metadata,
                    :created_at, :updated_at, :last_accessed_at, :retention_period)
        """), safety_reports_data)
        results['safety_reports'] = len(safety_reports_data)
        print(f"  ✅ safety_reports: {len(safety_reports_data)} records")
    except Exception as e:
        print(f"  ⚠️ safety_reports: {e}")
        results['safety_reports'] = 0
    
    session.commit()
    return results

def seed_environmental_monitoring(session: Session, user_ids: List[int], school_ids: List[int], activity_ids: List[int]) -> Dict[str, int]:
    """Seed environmental monitoring tables"""
    results = {}
    
    # Environmental Conditions
    conditions_data = []
    for i in range(200):
        conditions_data.append({
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'temperature': round(random.uniform(15.0, 35.0), 1),
            'humidity': round(random.uniform(30.0, 80.0), 1),
            'wind_speed': round(random.uniform(0.0, 30.0), 1),
            'precipitation': random.choice(['NONE', 'LIGHT', 'MODERATE', 'HEAVY', 'STORM']),
            'air_quality': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'HAZARDOUS']),
            'condition_metadata': json.dumps({
                'location': f'Location {random.randint(1, 20)}',
                'weather_condition': random.choice(['SUNNY', 'CLOUDY', 'RAINY', 'WINDY', 'STORMY']),
                'visibility': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR']),
                'recorded_by': random.choice(user_ids)
            }),
            'created_at': datetime.now() - timedelta(hours=random.randint(1, 168)),
            'updated_at': datetime.now() - timedelta(hours=random.randint(1, 168)),
            'last_accessed_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO environmental_conditions (activity_id, temperature, humidity, wind_speed,
                                                precipitation, air_quality, condition_metadata,
                                                created_at, updated_at, last_accessed_at,
                                                archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:activity_id, :temperature, :humidity, :wind_speed,
                    :precipitation, :air_quality, :condition_metadata,
                    :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), conditions_data)
        results['environmental_conditions'] = len(conditions_data)
        print(f"  ✅ environmental_conditions: {len(conditions_data)} records")
    except Exception as e:
        print(f"  ⚠️ environmental_conditions: {e}")
        results['environmental_conditions'] = 0
    
    # Environmental Alerts (depends on environmental_conditions)
    # Get the actual condition IDs that were just created
    try:
        condition_result = session.execute(text("SELECT id FROM environmental_conditions ORDER BY id"))
        condition_ids = [row[0] for row in condition_result]
        print(f"  📋 Found {len(condition_ids)} environmental condition IDs")
    except Exception as e:
        print(f"  ⚠️ Error getting condition IDs: {e}")
        condition_ids = []
    
    alerts_data = []
    for i in range(30):
        alerts_data.append({
            'condition_id': random.choice(condition_ids) if condition_ids else random.randint(1, 200),
            'alert_type': random.choice(['WEATHER', 'AIR_QUALITY', 'TEMPERATURE', 'WIND', 'VISIBILITY']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'message': f'Environmental alert {i+1}: {random.choice(["High wind warning", "Poor air quality", "Extreme temperature", "Low visibility"])}',
            'is_active': random.choice([True, False]),
            'alert_metadata': json.dumps({
                'threshold_value': round(random.uniform(10.0, 100.0), 1),
                'current_value': round(random.uniform(5.0, 120.0), 1),
                'location': f'Location {random.randint(1, 20)}',
                'alert_date': (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat(),
                'expires_at': (datetime.now() + timedelta(days=random.randint(1, 3))).isoformat(),
                'created_by': random.choice(user_ids)
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 3)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 2)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO environmental_alerts (condition_id, alert_type, severity, message, is_active,
                                            alert_metadata, created_at, updated_at, last_accessed_at,
                                            archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:condition_id, :alert_type, :severity, :message, :is_active,
                    :alert_metadata, :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), alerts_data)
        results['environmental_alerts'] = len(alerts_data)
        print(f"  ✅ environmental_alerts: {len(alerts_data)} records")
    except Exception as e:
        print(f"  ⚠️ environmental_alerts: {e}")
        results['environmental_alerts'] = 0
    
    # Activity Environmental Impacts (depends on activities and environmental_conditions)
    # Get the actual condition IDs that were just created
    try:
        condition_result = session.execute(text("SELECT id FROM environmental_conditions ORDER BY id"))
        condition_ids = [row[0] for row in condition_result]
        print(f"  📋 Found {len(condition_ids)} environmental condition IDs for impacts")
    except Exception as e:
        print(f"  ⚠️ Error getting condition IDs for impacts: {e}")
        condition_ids = []

    activity_impacts_data = []
    for i in range(50):
        activity_impacts_data.append({
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'condition_id': random.choice(condition_ids) if condition_ids else random.randint(1, 200),
            'impact_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'description': f'Environmental impact {i+1} on activity',
            'mitigation_strategy': f'Mitigation strategy for impact {i+1}',
            'impact_metadata': json.dumps({
                'environmental_factor': random.choice(['TEMPERATURE', 'HUMIDITY', 'WIND', 'PRECIPITATION', 'AIR_QUALITY']),
                'mitigation_measures': [f'Mitigation {j}' for j in range(random.randint(1, 3))],
                'monitoring_frequency': random.choice(['CONTINUOUS', 'HOURLY', 'DAILY', 'WEEKLY']),
                'severity': random.choice(['MINOR', 'MODERATE', 'MAJOR', 'CRITICAL']),
                'affected_area': f'Area {random.randint(1, 10)}',
                'estimated_duration': f'{random.randint(1, 30)} days'
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO activity_environmental_impacts (activity_id, condition_id, impact_level,
                                                      description, mitigation_strategy, impact_metadata,
                                                      created_at, updated_at, last_accessed_at,
                                                      archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:activity_id, :condition_id, :impact_level,
                    :description, :mitigation_strategy, :impact_metadata,
                    :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), activity_impacts_data)
        results['activity_environmental_impacts'] = len(activity_impacts_data)
        print(f"  ✅ activity_environmental_impacts: {len(activity_impacts_data)} records")
    except Exception as e:
        print(f"  ⚠️ activity_environmental_impacts: {e}")
        results['activity_environmental_impacts'] = 0
    
    # Physical Education Environmental Checks
    # Get actual physical education class IDs
    try:
        class_result = session.execute(text("SELECT id FROM physical_education_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result]
        print(f"  📋 Found {len(class_ids)} physical education class IDs")
    except Exception as e:
        print(f"  ⚠️ Error getting class IDs: {e}")
        class_ids = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]

    pe_checks_data = []
    for i in range(40):
        pe_checks_data.append({
            'class_id': random.choice(class_ids),
            'check_date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'checked_by': random.choice(user_ids),
            'temperature': round(random.uniform(15.0, 35.0), 1),
            'humidity': round(random.uniform(30.0, 80.0), 1),
            'air_quality': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'HAZARDOUS']),
            'lighting_conditions': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'INADEQUATE']),
            'surface_condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'HAZARDOUS']),
            'weather_conditions': random.choice(['CLEAR', 'CLOUDY', 'RAINY', 'WINDY', 'STORMY']),
            'status': random.choice(['SAFE', 'CAUTION', 'UNSAFE', 'MAINTENANCE_REQUIRED']),
            'notes': f'Environmental check notes {i+1}: {random.choice(["All conditions normal", "Minor issues noted", "Maintenance required", "Excellent conditions"])}'
        })
    
    try:
        session.execute(text("""
            INSERT INTO physical_education_environmental_checks (class_id, check_date, checked_by,
                                                               temperature, humidity, air_quality,
                                                               lighting_conditions, surface_condition,
                                                               weather_conditions, status, notes)
            VALUES (:class_id, :check_date, :checked_by,
                    :temperature, :humidity, :air_quality,
                    :lighting_conditions, :surface_condition,
                    :weather_conditions, :status, :notes)
        """), pe_checks_data)
        results['physical_education_environmental_checks'] = len(pe_checks_data)
        print(f"  ✅ physical_education_environmental_checks: {len(pe_checks_data)} records")
    except Exception as e:
        print(f"  ⚠️ physical_education_environmental_checks: {e}")
        results['physical_education_environmental_checks'] = 0
    
    # Skill Assessment Safety Checks (must be seeded first)
    skill_safety_checks_data = []
    for i in range(50):
        skill_safety_checks_data.append({
            'check_type': random.choice(['EQUIPMENT', 'ENVIRONMENT', 'STUDENT', 'ACTIVITY']),
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'performed_by': random.choice(user_ids),
            'safety_id': None,  # safety table is empty, so use NULL
            'status': random.choice(['PASSED', 'FAILED', 'PENDING', 'IN_PROGRESS']),
            'notes': f'Safety check notes {i+1}: {random.choice(["All checks passed", "Minor issues noted", "Major issues found", "Requires attention"])}',
            'issues_found': json.dumps([f'Issue {j}' for j in range(random.randint(0, 3))]),
            'actions_taken': json.dumps([f'Action {j}' for j in range(random.randint(0, 3))]),
            'follow_up_required': random.choice([True, False]),
            'follow_up_notes': f'Follow-up notes {i+1}' if random.choice([True, False]) else None,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 3)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })

    try:
        session.execute(text("""
            INSERT INTO skill_assessment_safety_checks (check_type, activity_id, performed_by, safety_id,
                                                      status, notes, issues_found, actions_taken,
                                                      follow_up_required, follow_up_notes, created_at, updated_at,
                                                      last_accessed_at, archived_at, deleted_at,
                                                      scheduled_deletion_at, retention_period)
            VALUES (:check_type, :activity_id, :performed_by, :safety_id,
                    :status, :notes, :issues_found, :actions_taken,
                    :follow_up_required, :follow_up_notes, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), skill_safety_checks_data)
        results['skill_assessment_safety_checks'] = len(skill_safety_checks_data)
        print(f"  ✅ skill_assessment_safety_checks: {len(skill_safety_checks_data)} records")
    except Exception as e:
        print(f"  ⚠️ skill_assessment_safety_checks: {e}")
        results['skill_assessment_safety_checks'] = 0

    # Skill Assessment Environmental Checks (depends on skill_assessment_safety_checks)
    # Get actual safety check IDs
    try:
        safety_check_result = session.execute(text("SELECT id FROM skill_assessment_safety_checks ORDER BY id"))
        safety_check_ids = [row[0] for row in safety_check_result]
        print(f"  📋 Found {len(safety_check_ids)} safety check IDs")
    except Exception as e:
        print(f"  ⚠️ Error getting safety check IDs: {e}")
        safety_check_ids = list(range(1, 51))

    skill_checks_data = []
    for i in range(35):
        skill_checks_data.append({
            'safety_check_id': random.choice(safety_check_ids),  # Use actual IDs
            'temperature': random.randint(15, 35),
            'humidity': random.randint(30, 80),
            'lighting_level': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'INADEQUATE']),
            'ventilation_status': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'INADEQUATE']),
            'surface_condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'HAZARDOUS']),
            'hazards_present': json.dumps([f'Hazard {j}' for j in range(random.randint(0, 3))]),
            'weather_conditions': json.dumps({
                'condition': random.choice(['CLEAR', 'CLOUDY', 'RAINY', 'WINDY', 'STORMY']),
                'wind_speed': round(random.uniform(0.0, 25.0), 1),
                'visibility': round(random.uniform(0.0, 10.0), 1)
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO skill_assessment_environmental_checks (safety_check_id, temperature, humidity,
                                                             lighting_level, ventilation_status,
                                                             surface_condition, hazards_present,
                                                             weather_conditions, created_at, updated_at,
                                                             last_accessed_at, archived_at, deleted_at,
                                                             scheduled_deletion_at, retention_period)
            VALUES (:safety_check_id, :temperature, :humidity,
                    :lighting_level, :ventilation_status,
                    :surface_condition, :hazards_present,
                    :weather_conditions, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), skill_checks_data)
        results['skill_assessment_environmental_checks'] = len(skill_checks_data)
        print(f"  ✅ skill_assessment_environmental_checks: {len(skill_checks_data)} records")
    except Exception as e:
        print(f"  ⚠️ skill_assessment_environmental_checks: {e}")
        results['skill_assessment_environmental_checks'] = 0
    
    # Skill Assessment Equipment Checks (depends on skill_assessment_safety_checks)
    # Get actual equipment IDs from physical_education_equipment table
    try:
        equipment_result = session.execute(text("SELECT id FROM physical_education_equipment LIMIT 100"))
        equipment_ids = [row[0] for row in equipment_result.fetchall()]
        print(f"  📋 Found {len(equipment_ids)} equipment IDs for skill_assessment_equipment_checks")
    except Exception as e:
        print(f"  ⚠️ Could not get equipment IDs: {e}")
        equipment_ids = list(range(1, 101))  # Fallback range
    
    equipment_checks_data = []
    for i in range(45):
        equipment_checks_data.append({
            'safety_check_id': random.choice(safety_check_ids),  # Use actual IDs
            'equipment_id': random.choice(equipment_ids) if equipment_ids else random.randint(1, 100),
            'condition': random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'UNUSABLE']),
            'maintenance_needed': random.choice([True, False]),
            'maintenance_type': random.choice(['ROUTINE', 'REPAIR', 'REPLACEMENT', 'CLEANING', 'CALIBRATION']),
            'last_maintenance': datetime.now() - timedelta(days=random.randint(1, 90)),
            'next_maintenance': datetime.now() + timedelta(days=random.randint(1, 30)),
            'inspection_points': json.dumps([f'Point {j}' for j in range(random.randint(1, 5))]),
            'damage_description': f'Damage description {i+1}: {random.choice(["Minor wear", "Significant damage", "No damage", "Requires attention"])}',
            'replacement_needed': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO skill_assessment_equipment_checks (safety_check_id, equipment_id, condition,
                                                         maintenance_needed, maintenance_type,
                                                         last_maintenance, next_maintenance,
                                                         inspection_points, damage_description,
                                                         replacement_needed, created_at, updated_at,
                                                         last_accessed_at, archived_at, deleted_at,
                                                         scheduled_deletion_at, retention_period)
            VALUES (:safety_check_id, :equipment_id, :condition,
                    :maintenance_needed, :maintenance_type,
                    :last_maintenance, :next_maintenance,
                    :inspection_points, :damage_description,
                    :replacement_needed, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), equipment_checks_data)
        results['skill_assessment_equipment_checks'] = len(equipment_checks_data)
        print(f"  ✅ skill_assessment_equipment_checks: {len(equipment_checks_data)} records")
    except Exception as e:
        print(f"  ⚠️ skill_assessment_equipment_checks: {e}")
        results['skill_assessment_equipment_checks'] = 0
    
    session.commit()
    return results

def seed_compliance_audit(session: Session, user_ids: List[int], activity_ids: List[int]) -> Dict[str, int]:
    """Seed compliance and audit tables"""
    results = {}
    
    # Audit Logs
    audit_logs_data = []
    for i in range(150):
        audit_logs_data.append({
            'user_id': random.choice(user_ids),
            'action': random.choice(['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT']),
            'resource_type': random.choice(['safety_protocols', 'equipment', 'safety_incidents', 'users']),
            'resource_id': random.randint(1, 1000),
            'details': json.dumps({
                'old_values': {'field': 'old_value'},
                'new_values': {'field': 'new_value'},
                'changes': ['field_updated']
            }),
            'ip_address': f'192.168.1.{random.randint(1, 254)}',
            'user_agent': 'Mozilla/5.0 (compatible; System)',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details,
                                   ip_address, user_agent, created_at, updated_at)
            VALUES (:user_id, :action, :resource_type, :resource_id, :details,
                    :ip_address, :user_agent, :created_at, :updated_at)
        """), audit_logs_data)
        results['audit_logs'] = len(audit_logs_data)
        print(f"  ✅ audit_logs: {len(audit_logs_data)} records")
    except Exception as e:
        print(f"  ⚠️ audit_logs: {e}")
        results['audit_logs'] = 0
    
    # Security Audits
    security_audits_data = []
    for i in range(25):
        security_audits_data.append({
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 60)),
            'user_id': random.choice(user_ids),
            'action': random.choice(['SECURITY_AUDIT', 'COMPLIANCE_CHECK', 'ACCESS_REVIEW', 'DATA_AUDIT']),
            'resource_type': f'security_audit_{i+1}',
            'resource_id': str(random.randint(1, 1000)),
            'details': json.dumps({
                'scope': f'Security audit scope {i+1}',
                'issues_found': [f'Issue {j}' for j in range(random.randint(1, 4))],
                'recommendations': [f'Recommendation {j}' for j in range(random.randint(1, 3))],
                'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE'])
            }),
            'ip_address': f'192.168.1.{random.randint(1, 254)}',
            'user_agent': 'Security Audit System'
        })
    
    try:
        session.execute(text("""
            INSERT INTO security_audits (timestamp, user_id, action, resource_type, resource_id, details, ip_address, user_agent)
            VALUES (:timestamp, :user_id, :action, :resource_type, :resource_id, :details, :ip_address, :user_agent)
        """), security_audits_data)
        results['security_audits'] = len(security_audits_data)
        print(f"  ✅ security_audits: {len(security_audits_data)} records")
    except Exception as e:
        print(f"  ⚠️ security_audits: {e}")
        results['security_audits'] = 0
    
    # Security Incident Management
    incident_management_data = []
    for i in range(20):
        incident_management_data.append({
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'title': f'Security Incident {i+1}',
            'description': f'Security incident {i+1} description',
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'status': random.choice(['OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED']),
            'reported_by': random.choice(user_ids),
            'assigned_to': random.choice(user_ids),
            'details': json.dumps({
                'incident_type': random.choice(['DATA_LEAK', 'SECURITY_BREACH', 'UNAUTHORIZED_ACCESS', 'SYSTEM_COMPROMISE']),
                'location': f'Location {random.randint(1, 10)}',
                'affected_systems': [f'System {j}' for j in range(random.randint(1, 3))],
                'impact_level': random.choice(['MINOR', 'MODERATE', 'MAJOR', 'CRITICAL'])
            }),
            'resolution': f'Resolution for incident {i+1}',
            'resolved_at': datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None
        })
    
    try:
        session.execute(text("""
            INSERT INTO security_incident_management (timestamp, title, description, severity, status,
                                                    reported_by, assigned_to, details, resolution, resolved_at)
            VALUES (:timestamp, :title, :description, :severity, :status,
                    :reported_by, :assigned_to, :details, :resolution, :resolved_at)
        """), incident_management_data)
        results['security_incident_management'] = len(incident_management_data)
        print(f"  ✅ security_incident_management: {len(incident_management_data)} records")
    except Exception as e:
        print(f"  ⚠️ security_incident_management: {e}")
        results['security_incident_management'] = 0
    
    # Policy Security Audits
    policy_audits_data = []
    for i in range(15):
        policy_audits_data.append({
            'policy_id': random.choice([1, 2, 3, 4, 5]),  # Use actual existing policy IDs
            'rule_id': random.choice([1, 2, 3, 4, 5]),   # Use actual existing rule IDs
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'student_id': random.randint(1, 100),
            'audit_type': random.choice(['COMPLIANCE', 'SECURITY', 'ACCESS', 'DATA']),
            'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED']),
            'details': json.dumps({
                'compliance_score': random.randint(60, 100),
                'compliant_areas': [f'Area {j}' for j in range(random.randint(1, 3))],
                'non_compliant_areas': [f'Area {j}' for j in range(random.randint(1, 2))],
                'recommendations': [f'Recommendation {j}' for j in range(random.randint(1, 3))],
                'auditor_id': random.choice(user_ids)
            }),
            'audit_metadata': json.dumps({
                'audit_date': (datetime.now() - timedelta(days=random.randint(1, 45))).isoformat(),
                'duration_minutes': random.randint(30, 180),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 45)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'last_accessed_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(1, 7)
        })
    
    try:
        session.execute(text("""
            INSERT INTO policy_security_audits (policy_id, rule_id, activity_id, student_id, audit_type,
                                              status, details, audit_metadata, created_at, updated_at,
                                              last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:policy_id, :rule_id, :activity_id, :student_id, :audit_type,
                    :status, :details, :audit_metadata, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), policy_audits_data)
        results['policy_security_audits'] = len(policy_audits_data)
        print(f"  ✅ policy_security_audits: {len(policy_audits_data)} records")
    except Exception as e:
        print(f"  ⚠️ policy_security_audits: {e}")
        results['policy_security_audits'] = 0
    
    # Security General Audit Logs
    general_audit_logs_data = []
    for i in range(100):
        general_audit_logs_data.append({
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'user_id': random.choice(user_ids),
            'action': random.choice(['LOGIN', 'LOGOUT', 'ACCESS', 'MODIFY', 'DELETE', 'EXPORT']),
            'module': random.choice(['AUTHENTICATION', 'USER_MANAGEMENT', 'DATA_ACCESS', 'SYSTEM_ADMIN', 'REPORTING']),
            'details': json.dumps({
                'resource': f'Resource {random.randint(1, 50)}',
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser {random.randint(1, 10)}',
                'success': random.choice([True, False]),
                'session_id': f'session_{random.randint(1000, 9999)}',
                'request_id': f'req_{random.randint(10000, 99999)}'
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO security_general_audit_logs (timestamp, user_id, action, module, details)
            VALUES (:timestamp, :user_id, :action, :module, :details)
        """), general_audit_logs_data)
        results['security_general_audit_logs'] = len(general_audit_logs_data)
        print(f"  ✅ security_general_audit_logs: {len(general_audit_logs_data)} records")
    except Exception as e:
        print(f"  ⚠️ security_general_audit_logs: {e}")
        results['security_general_audit_logs'] = 0
    
    # Activity Injury Preventions (linking activities to injury prevention measures)
    try:
        # Get actual prevention IDs that were just created
        prevention_result = session.execute(text("SELECT id FROM injury_preventions ORDER BY id"))
        prevention_ids = [row[0] for row in prevention_result]
        print(f"  📋 Found {len(prevention_ids)} prevention IDs for activity associations")
    except Exception as e:
        print(f"  ⚠️ Error getting prevention IDs for activity associations: {e}")
        prevention_ids = [121, 122, 123, 124, 125]
    
    activity_injury_preventions_data = []
    for i in range(150):  # 150 activity-injury prevention associations
        activity_injury_preventions_data.append({
            'activity_id': random.choice(activity_ids) if activity_ids else random.randint(1, 100),
            'prevention_id': random.choice(prevention_ids),
            'priority': random.randint(1, 5),  # 1=lowest, 5=highest priority
            'prevention_metadata': json.dumps({
                'association_id': i+1,
                'effectiveness_rating': random.randint(1, 10),
                'implementation_difficulty': random.choice(['EASY', 'MEDIUM', 'HARD']),
                'required_training': random.choice(['NONE', 'BASIC', 'ADVANCED', 'EXPERT']),
                'equipment_needed': [f'Equipment {j}' for j in range(random.randint(0, 3))],
                'time_required': random.randint(5, 60),  # minutes
                'cost_estimate': round(random.uniform(0, 1000), 2),
                'success_rate': round(random.uniform(0.5, 1.0), 2),
                'notes': f'Activity-injury prevention association {i+1}',
                'last_reviewed': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                'next_review': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(365, 2555)  # 1-7 years
        })
    
    try:
        session.execute(text("""
            INSERT INTO activity_injury_preventions (activity_id, prevention_id, priority, prevention_metadata,
                                                   created_at, updated_at, last_accessed_at, archived_at,
                                                   deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:activity_id, :prevention_id, :priority, :prevention_metadata,
                    :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period)
        """), activity_injury_preventions_data)
        session.commit()  # Commit after each table to prevent transaction errors
        results['activity_injury_preventions'] = len(activity_injury_preventions_data)
        print(f"  ✅ activity_injury_preventions: {len(activity_injury_preventions_data)} records")
    except Exception as e:
        print(f"  ⚠️ activity_injury_preventions: {e}")
        session.rollback()  # Rollback on error
        results['activity_injury_preventions'] = 0
    
    session.commit()
    return results
