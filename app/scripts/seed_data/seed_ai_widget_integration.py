"""
Seed AI Widget Integration Data - COMPREHENSIVE MIGRATION

This script migrates data from ALL 540 tables to populate AI widget test data.
It finds data wherever it exists and migrates it to the target tables.
"""

from datetime import datetime, timedelta, date
import random
import json
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Dict, List, Optional

def find_tables_with_data(session: Session, keywords: List[str]) -> Dict[str, int]:
    """Find all tables containing data matching keywords."""
    inspector = inspect(session.bind)
    all_tables = inspector.get_table_names()
    
    found_tables = {}
    for table in all_tables:
        if any(kw.lower() in table.lower() for kw in keywords):
            try:
                count = session.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
                if count > 0:
                    found_tables[table] = count
            except Exception:
                pass
    return found_tables

def get_table_columns(session: Session, table_name: str) -> List[str]:
    """Get column names for a table."""
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        return [col['name'] for col in columns]
    except Exception:
        return []

def seed_ai_widget_integration(session: Session) -> Dict[str, int]:
    """
    Comprehensive migration from ALL 540 tables to populate AI widget data.
    Finds data wherever it exists and migrates to target tables.
    """
    print("\n" + "="*70)
    print("🤖 COMPREHENSIVE AI WIDGET DATA MIGRATION")
    print("="*70)
    
    results = {}
    
    # ==================== 1. ENROLLMENT MIGRATION ====================
    print("\n👥 MIGRATING ENROLLMENTS FROM ALL SOURCES...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM physical_education_class_students
            WHERE status = 'ACTIVE'
        """)).scalar()
        
        print(f"  📊 Current target enrollments: {target_count}")
        
        if target_count == 0:
            # Find all enrollment source tables
            enrollment_sources = find_tables_with_data(session, [
                'class_student', 'enrollment', 'student_class', 'educational_class_student'
            ])
            
            print(f"  🔍 Found {len(enrollment_sources)} potential source tables:")
            for table, count in enrollment_sources.items():
                print(f"    - {table}: {count} records")
            
            # Try to migrate from educational_class_students
            if 'educational_class_students' in enrollment_sources:
                print(f"  🔄 Migrating from educational_class_students...")
                try:
                    cols = get_table_columns(session, 'educational_class_students')
                    print(f"    Columns: {cols[:10]}")
                    
                    # Map columns
                    class_id_col = 'class_id' if 'class_id' in cols else 'educational_class_id'
                    student_id_col = 'student_id' if 'student_id' in cols else None
                    status_col = 'status' if 'status' in cols else None
                    
                    if class_id_col and student_id_col:
                        # Get PE classes
                        pe_classes = session.execute(text("""
                            SELECT id FROM physical_education_classes LIMIT 100
                        """)).fetchall()
                        pe_class_ids = [r[0] for r in pe_classes]
                        
                        if pe_class_ids:
                            # Migrate enrollments
                            migrated = session.execute(text(f"""
                                INSERT INTO physical_education_class_students
                                (class_id, student_id, enrollment_date, status, created_at, updated_at)
                                SELECT DISTINCT
                                    :pe_class_id,
                                    ecs.{student_id_col},
                                    COALESCE(ecs.enrollment_date, NOW()::date) as enrollment_date,
                                    CASE 
                                        WHEN '{status_col}' IS NOT NULL AND ecs.{status_col} ILIKE 'active' THEN 'ACTIVE'
                                        ELSE 'ACTIVE'
                                    END as status,
                                    COALESCE(ecs.created_at, NOW()) as created_at,
                                    COALESCE(ecs.updated_at, NOW()) as updated_at
                                FROM educational_class_students ecs
                                WHERE ecs.{student_id_col} IN (SELECT id FROM students LIMIT 500)
                                AND NOT EXISTS (
                                    SELECT 1 FROM physical_education_class_students pcs
                                    WHERE pcs.class_id = :pe_class_id 
                                    AND pcs.student_id = ecs.{student_id_col}
                                )
                                LIMIT 20
                            """), {"pe_class_id": pe_class_ids[0]}).rowcount
                            
                            session.commit()
                            print(f"    ✅ Migrated {migrated} enrollments")
                            results['enrollments_migrated'] = migrated
                except Exception as e:
                    print(f"    ⚠️  Migration error: {e}")
                    session.rollback()
        else:
            print(f"  ✅ Enrollments already exist: {target_count}")
            results['enrollments_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    # ==================== 2. ATTENDANCE MIGRATION ====================
    print("\n📅 MIGRATING ATTENDANCE FROM ALL SOURCES...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM physical_education_attendance
        """)).scalar()
        
        print(f"  📊 Current target attendance: {target_count}")
        
        if target_count < 100:
            # Find all attendance source tables
            attendance_sources = find_tables_with_data(session, ['attend', 'presence'])
            
            print(f"  🔍 Found {len(attendance_sources)} potential source tables:")
            for table, count in attendance_sources.items():
                print(f"    - {table}: {count} records")
            
            # Migrate from class_attendance
            if 'class_attendance' in attendance_sources:
                print(f"  🔄 Migrating from class_attendance...")
                try:
                    migrated = session.execute(text("""
                        INSERT INTO physical_education_attendance
                        (student_id, date, status, created_at, updated_at)
                        SELECT DISTINCT
                            ca.student_id,
                            DATE(ca.attendance_date) as date,
                            CASE 
                                WHEN ca.attendance_status ILIKE 'present' THEN 'PRESENT'
                                WHEN ca.attendance_status ILIKE 'absent' THEN 'ABSENT'
                                WHEN ca.attendance_status ILIKE 'late' THEN 'LATE'
                                WHEN ca.attendance_status ILIKE 'excused' THEN 'EXCUSED'
                                ELSE UPPER(ca.attendance_status)
                            END as status,
                            COALESCE(ca.created_at, NOW()) as created_at,
                            COALESCE(ca.updated_at, NOW()) as updated_at
                        FROM class_attendance ca
                        WHERE ca.student_id IN (SELECT id FROM students LIMIT 1000)
                        AND NOT EXISTS (
                            SELECT 1 FROM physical_education_attendance pea
                            WHERE pea.student_id = ca.student_id
                            AND pea.date = DATE(ca.attendance_date)
                        )
                        LIMIT 2000
                    """)).rowcount
                    
                    session.commit()
                    print(f"    ✅ Migrated {migrated} attendance records")
                    results['attendance_migrated'] = migrated
                except Exception as e:
                    print(f"    ⚠️  Migration error: {e}")
                    session.rollback()
        else:
            print(f"  ✅ Attendance already sufficient: {target_count}")
            results['attendance_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    # ==================== 3. HEALTH METRICS MIGRATION ====================
    print("\n🏥 MIGRATING HEALTH METRICS FROM ALL SOURCES...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM health_metrics
        """)).scalar()
        
        print(f"  📊 Current target health metrics: {target_count}")
        
        if target_count < 50:
            # Find all health metric source tables
            health_sources = find_tables_with_data(session, [
                'health_metric', 'fitness_health', 'general_health'
            ])
            
            print(f"  🔍 Found {len(health_sources)} potential source tables:")
            for table, count in health_sources.items():
                print(f"    - {table}: {count} records")
            
            # Migrate from general_health_metrics
            for source_table in ['general_health_metrics', 'fitness_health_metrics']:
                if source_table in health_sources:
                    print(f"  🔄 Migrating from {source_table}...")
                    try:
                        cols = get_table_columns(session, source_table)
                        student_id_col = 'student_id' if 'student_id' in cols else None
                        metric_type_col = 'metric_type' if 'metric_type' in cols else 'type'
                        value_col = 'value' if 'value' in cols else 'metric_value'
                        recorded_at_col = 'recorded_at' if 'recorded_at' in cols else 'created_at'
                        
                        if student_id_col:
                            migrated = session.execute(text(f"""
                                INSERT INTO health_metrics
                                (student_id, metric_type, value, unit, recorded_at, created_at, updated_at)
                                SELECT DISTINCT
                                    ghm.{student_id_col},
                                    COALESCE(ghm.{metric_type_col}, 'HEART_RATE') as metric_type,
                                    ghm.{value_col} as value,
                                    COALESCE(ghm.unit, 'bpm') as unit,
                                    COALESCE(ghm.{recorded_at_col}, NOW()) as recorded_at,
                                    COALESCE(ghm.created_at, NOW()) as created_at,
                                    COALESCE(ghm.updated_at, NOW()) as updated_at
                                FROM {source_table} ghm
                                WHERE ghm.{student_id_col} IN (SELECT id FROM students LIMIT 500)
                                AND NOT EXISTS (
                                    SELECT 1 FROM health_metrics hm
                                    WHERE hm.student_id = ghm.{student_id_col}
                                    AND hm.metric_type = COALESCE(ghm.{metric_type_col}, 'HEART_RATE')
                                    AND hm.recorded_at::date = COALESCE(ghm.{recorded_at_col}, NOW())::date
                                )
                                LIMIT 500
                            """)).rowcount
                            
                            session.commit()
                            print(f"    ✅ Migrated {migrated} health metrics from {source_table}")
                            results[f'health_migrated_{source_table}'] = migrated
                    except Exception as e:
                        print(f"    ⚠️  Migration error from {source_table}: {e}")
                        session.rollback()
        else:
            print(f"  ✅ Health metrics already sufficient: {target_count}")
            results['health_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    # ==================== 4. PERFORMANCE DATA MIGRATION ====================
    print("\n📈 MIGRATING PERFORMANCE DATA FROM ALL SOURCES...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM student_activity_performances
        """)).scalar()
        
        print(f"  📊 Current target performances: {target_count}")
        
        if target_count < 100:
            # Find all performance source tables
            perf_sources = find_tables_with_data(session, [
                'performance', 'activity_performance', 'exercise_performance', 'workout_performance'
            ])
            
            print(f"  🔍 Found {len(perf_sources)} potential source tables:")
            for table, count in perf_sources.items():
                print(f"    - {table}: {count} records")
            
            # Migrate from activity_performances
            for source_table in ['activity_performances', 'exercise_performances', 'workout_performances']:
                if source_table in perf_sources:
                    print(f"  🔄 Migrating from {source_table}...")
                    try:
                        cols = get_table_columns(session, source_table)
                        student_id_col = 'student_id' if 'student_id' in cols else None
                        activity_id_col = 'activity_id' if 'activity_id' in cols else 'exercise_id' if 'exercise_id' in cols else None
                        score_col = 'score' if 'score' in cols else 'performance_score'
                        recorded_at_col = 'recorded_at' if 'recorded_at' in cols else 'created_at'
                        
                        if student_id_col and activity_id_col:
                            migrated = session.execute(text(f"""
                                INSERT INTO student_activity_performances
                                (student_id, activity_id, score, recorded_at, created_at, updated_at)
                                SELECT DISTINCT
                                    ap.{student_id_col},
                                    ap.{activity_id_col},
                                    COALESCE(ap.{score_col}, 0) as score,
                                    COALESCE(ap.{recorded_at_col}, NOW()) as recorded_at,
                                    COALESCE(ap.created_at, NOW()) as created_at,
                                    COALESCE(ap.updated_at, NOW()) as updated_at
                                FROM {source_table} ap
                                WHERE ap.{student_id_col} IN (SELECT id FROM students LIMIT 500)
                                AND ap.{activity_id_col} IN (SELECT id FROM activities LIMIT 100)
                                AND NOT EXISTS (
                                    SELECT 1 FROM student_activity_performances sap
                                    WHERE sap.student_id = ap.{student_id_col}
                                    AND sap.activity_id = ap.{activity_id_col}
                                    AND sap.recorded_at::date = COALESCE(ap.{recorded_at_col}, NOW())::date
                                )
                                LIMIT 2000
                            """)).rowcount
                            
                            session.commit()
                            print(f"    ✅ Migrated {migrated} performances from {source_table}")
                            results[f'perf_migrated_{source_table}'] = migrated
                    except Exception as e:
                        print(f"    ⚠️  Migration error from {source_table}: {e}")
                        session.rollback()
        else:
            print(f"  ✅ Performance data already sufficient: {target_count}")
            results['perf_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    # ==================== 5. COMMUNICATION RECORDS MIGRATION ====================
    print("\n📧 MIGRATING COMMUNICATION RECORDS FROM ALL SOURCES...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM communication_records
        """)).scalar()
        
        print(f"  📊 Current target communication records: {target_count}")
        
        if target_count < 50:
            # Find all communication/message source tables
            comm_sources = find_tables_with_data(session, [
                'message', 'communication', 'notification', 'email_log', 'sms_log'
            ])
            
            print(f"  🔍 Found {len(comm_sources)} potential source tables:")
            for table, count in comm_sources.items():
                print(f"    - {table}: {count} records")
            
            # Migrate from messages table
            if 'messages' in comm_sources:
                print(f"  🔄 Migrating from messages...")
                try:
                    cols = get_table_columns(session, 'messages')
                    sender_id_col = 'sender_id' if 'sender_id' in cols else None
                    recipient_id_col = 'recipient_id' if 'recipient_id' in cols else None
                    content_col = 'content' if 'content' in cols else 'message'
                    subject_col = 'subject' if 'subject' in cols else None
                    sent_at_col = 'sent_at' if 'sent_at' in cols else 'created_at'
                    status_col = 'status' if 'status' in cols else None
                    
                    if sender_id_col and recipient_id_col:
                        # Check if recipient is a student, teacher, or administrator
                        # Note: recipients from users table are teachers/admins, students are in students table
                        migrated = session.execute(text(f"""
                            INSERT INTO communication_records
                            (communication_type, channels, student_id, teacher_id, recipient_email, 
                             subject, message, status, sent_at, sender_id, created_at, updated_at)
                            SELECT 
                                CASE 
                                    WHEN r.role = 'admin' OR r.role = 'administrator' THEN 'ADMINISTRATOR'::communication_type_enum
                                    WHEN r.role = 'teacher' OR r.role IS NULL THEN 'TEACHER'::communication_type_enum
                                    ELSE 'TEACHER'::communication_type_enum
                                END as communication_type,
                                json_build_array('email')::jsonb as channels,
                                NULL as student_id,  -- Recipients from users table are not students
                                r.id as teacher_id,
                                r.email as recipient_email,
                                COALESCE(m.{subject_col}, 'Message') as subject,
                                m.{content_col} as message,
                                CASE 
                                    WHEN m.{status_col} IS NOT NULL AND m.{status_col} ILIKE 'sent' THEN 'SENT'::communication_status_enum
                                    WHEN m.{status_col} IS NOT NULL AND m.{status_col} ILIKE 'delivered' THEN 'DELIVERED'::communication_status_enum
                                    WHEN m.{status_col} IS NOT NULL AND m.{status_col} ILIKE 'read' THEN 'DELIVERED'::communication_status_enum
                                    ELSE 'SENT'::communication_status_enum
                                END as status,
                                COALESCE(m.{sent_at_col}, NOW()) as sent_at,
                                m.{sender_id_col} as sender_id,
                                COALESCE(m.{sent_at_col}, NOW()) as created_at,
                                COALESCE(m.{sent_at_col}, NOW()) as updated_at
                            FROM messages m
                            INNER JOIN users r ON m.{recipient_id_col} = r.id
                            WHERE m.{sender_id_col} IN (SELECT id FROM users WHERE is_active = TRUE)
                            AND NOT EXISTS (
                                SELECT 1 FROM communication_records cr
                                WHERE cr.sender_id = m.{sender_id_col}
                                AND cr.recipient_email = r.email
                                AND cr.sent_at::date = COALESCE(m.{sent_at_col}, NOW())::date
                            )
                            LIMIT 1000
                        """)).rowcount
                        
                        session.commit()
                        print(f"    ✅ Migrated {migrated} communication records from messages")
                        results['communication_migrated'] = migrated
                except Exception as e:
                    print(f"    ⚠️  Migration error: {e}")
                    session.rollback()
        else:
            print(f"  ✅ Communication records already sufficient: {target_count}")
            results['communication_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    # ==================== 6. ASSIGNMENT TRANSLATIONS ====================
    print("\n📝 MIGRATING/CREATING ASSIGNMENT TRANSLATIONS...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM assignment_translations
        """)).scalar()
        
        print(f"  📊 Current assignment_translations: {target_count}")
        
        if target_count < 50:
            # Create assignment translations from assignments and students
            # These represent translations of assignments sent to students
            try:
                migrated = session.execute(text("""
                    INSERT INTO assignment_translations
                    (assignment_id, student_id, source_language, target_language, 
                     original_text, translated_text, status, sent_at, created_at, updated_at)
                    SELECT DISTINCT
                        a.id as assignment_id,
                        s.id as student_id,
                        'en' as source_language,
                        CASE 
                            WHEN random() < 0.3 THEN 'es'
                            WHEN random() < 0.5 THEN 'fr'
                            ELSE 'en'
                        END as target_language,
                        COALESCE(a.description, a.title, 'Assignment') as original_text,
                        COALESCE(a.description, a.title, 'Assignment') || ' [Translated]' as translated_text,
                        CASE 
                            WHEN random() < 0.7 THEN 'SENT'::translation_status_enum
                            WHEN random() < 0.9 THEN 'DELIVERED'::translation_status_enum
                            ELSE 'PENDING'::translation_status_enum
                        END as status,
                        CASE 
                            WHEN random() < 0.8 THEN NOW() - (random() * INTERVAL '30 days')
                            ELSE NULL
                        END as sent_at,
                        COALESCE(a.created_at, NOW()) as created_at,
                        COALESCE(a.updated_at, NOW()) as updated_at
                    FROM assignments a
                    CROSS JOIN LATERAL (
                        SELECT id FROM students 
                        ORDER BY random() 
                        LIMIT 1
                    ) s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM assignment_translations at
                        WHERE at.assignment_id = a.id
                        AND at.student_id = s.id
                    )
                    LIMIT 500
                """)).rowcount
                
                session.commit()
                print(f"    ✅ Created {migrated} assignment translation records")
                results['assignment_translations_created'] = migrated
            except Exception as e:
                print(f"    ⚠️  Migration error: {e}")
                session.rollback()
        else:
            print(f"  ✅ Assignment translations already sufficient: {target_count}")
            results['assignment_translations_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    # ==================== 7. SUBMISSION TRANSLATIONS ====================
    print("\n📄 MIGRATING/CREATING SUBMISSION TRANSLATIONS...")
    try:
        target_count = session.execute(text("""
            SELECT COUNT(*) FROM submission_translations
        """)).scalar()
        
        print(f"  📊 Current submission_translations: {target_count}")
        
        if target_count < 50:
            # Create submission translations from assignments and students
            # These represent translations of student submissions
            try:
                migrated = session.execute(text("""
                    INSERT INTO submission_translations
                    (assignment_id, student_id, source_language, target_language, 
                     original_text, translated_text, confidence, translated_at, created_at, updated_at)
                    SELECT DISTINCT
                        a.id as assignment_id,
                        s.id as student_id,
                        CASE 
                            WHEN random() < 0.3 THEN 'es'
                            WHEN random() < 0.5 THEN 'fr'
                            ELSE 'en'
                        END as source_language,
                        'en' as target_language,
                        'Student submission text for assignment: ' || a.title as original_text,
                        'Student submission text for assignment: ' || a.title || ' [Translated to English]' as translated_text,
                        CASE 
                            WHEN random() < 0.7 THEN 'high'
                            WHEN random() < 0.9 THEN 'medium'
                            ELSE 'low'
                        END as confidence,
                        NOW() - (random() * INTERVAL '30 days') as translated_at,
                        NOW() - (random() * INTERVAL '30 days') as created_at,
                        NOW() - (random() * INTERVAL '30 days') as updated_at
                    FROM assignments a
                    CROSS JOIN LATERAL (
                        SELECT id FROM students 
                        ORDER BY random() 
                        LIMIT 1
                    ) s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM submission_translations st
                        WHERE st.assignment_id = a.id
                        AND st.student_id = s.id
                    )
                    LIMIT 500
                """)).rowcount
                
                session.commit()
                print(f"    ✅ Created {migrated} submission translation records")
                results['submission_translations_created'] = migrated
            except Exception as e:
                print(f"    ⚠️  Migration error: {e}")
                session.rollback()
        else:
            print(f"  ✅ Submission translations already sufficient: {target_count}")
            results['submission_translations_existing'] = target_count
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        session.rollback()
    
    print("\n" + "="*70)
    print("✅ MIGRATION COMPLETE")
    print("="*70)
    print(f"\nResults: {json.dumps(results, indent=2)}")
    
    return results
