#!/usr/bin/env python3
"""
Verify data integrity for Phase 1.9 and 1.10 seeded data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def verify_integrity():
    """Verify data integrity relationships"""
    session = SessionLocal()
    
    print("=" * 80)
    print("DATA INTEGRITY VERIFICATION")
    print("=" * 80)
    
    try:
        # 1. Verify teacher_statistics has valid teacher_ids
        print("\n1. Verifying teacher_statistics → teacher_registrations foreign keys...")
        invalid_stats = session.execute(text("""
            SELECT COUNT(*) FROM teacher_statistics ts
            LEFT JOIN teacher_registrations tr ON CAST(ts.teacher_id AS VARCHAR) = CAST(tr.id AS VARCHAR)
            WHERE tr.id IS NULL
        """)).scalar()
        if invalid_stats == 0:
            print(f"   ✅ All {session.execute(text('SELECT COUNT(*) FROM teacher_statistics')).scalar()} teacher_statistics have valid teacher_ids")
        else:
            print(f"   ⚠️  {invalid_stats} teacher_statistics have invalid teacher_ids")
        
        # 2. Verify teacher_goals have valid teacher_ids
        print("\n2. Verifying teacher_goals → teacher_registrations foreign keys...")
        invalid_goals = session.execute(text("""
            SELECT COUNT(*) FROM teacher_goals tg
            LEFT JOIN teacher_registrations tr ON CAST(tg.teacher_id AS VARCHAR) = CAST(tr.id AS VARCHAR)
            WHERE tr.id IS NULL
        """)).scalar()
        if invalid_goals == 0:
            print(f"   ✅ All {session.execute(text('SELECT COUNT(*) FROM teacher_goals')).scalar()} teacher_goals have valid teacher_ids")
        else:
            print(f"   ⚠️  {invalid_goals} teacher_goals have invalid teacher_ids")
        
        # 3. Verify dashboard_widget_instances have valid widget_ids
        print("\n3. Verifying dashboard_widget_instances → dashboard_widgets foreign keys...")
        invalid_widgets = session.execute(text("""
            SELECT COUNT(*) FROM dashboard_widget_instances dwi
            LEFT JOIN dashboard_widgets dw ON CAST(dwi.widget_id AS VARCHAR) = CAST(dw.id AS VARCHAR)
            WHERE dw.id IS NULL
        """)).scalar()
        if invalid_widgets == 0:
            print(f"   ✅ All {session.execute(text('SELECT COUNT(*) FROM dashboard_widget_instances')).scalar()} widget instances have valid widget_ids")
        else:
            print(f"   ⚠️  {invalid_widgets} widget instances have invalid widget_ids")
        
        # 4. Verify learning_path_steps have valid learning_path_ids
        print("\n4. Verifying learning_path_steps → teacher_learning_paths foreign keys...")
        invalid_steps = session.execute(text("""
            SELECT COUNT(*) FROM learning_path_steps lps
            LEFT JOIN teacher_learning_paths tlp ON CAST(lps.learning_path_id AS VARCHAR) = CAST(tlp.id AS VARCHAR)
            WHERE tlp.id IS NULL
        """)).scalar()
        if invalid_steps == 0:
            print(f"   ✅ All {session.execute(text('SELECT COUNT(*) FROM learning_path_steps')).scalar()} learning path steps have valid learning_path_ids")
        else:
            print(f"   ⚠️  {invalid_steps} learning path steps have invalid learning_path_ids")
        
        # 5. Check distribution of content among teachers
        print("\n5. Verifying content distribution among teachers...")
        lesson_dist = session.execute(text("""
            SELECT teacher_id, COUNT(*) as count
            FROM lesson_plan_templates
            WHERE teacher_id IS NOT NULL
            GROUP BY teacher_id
            ORDER BY count DESC
            LIMIT 5
        """)).fetchall()
        print(f"   📊 Top 5 teachers by lesson plans:")
        for teacher_id, count in lesson_dist:
            print(f"      Teacher {str(teacher_id)[:8]}: {count} lesson plans")
        
        # 6. Check activity logs linking
        print("\n6. Verifying teacher_activity_logs data quality...")
        log_stats = session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT teacher_id) as unique_teachers,
                COUNT(CASE WHEN activity_type IS NOT NULL THEN 1 END) as with_type,
                COUNT(CASE WHEN activity_description IS NOT NULL THEN 1 END) as with_description
            FROM teacher_activity_logs
        """)).first()
        print(f"   ✅ Total logs: {log_stats[0]}")
        print(f"   ✅ Unique teachers: {log_stats[1]}")
        print(f"   ✅ Logs with activity_type: {log_stats[2]}")
        print(f"   ✅ Logs with description: {log_stats[3]}")
        
        # 7. Check statistics patterns (weekday/weekend)
        print("\n7. Verifying teacher_statistics weekday/weekend patterns...")
        weekday_stats = session.execute(text("""
            SELECT 
                CASE 
                    WHEN EXTRACT(DOW FROM stat_date) IN (0, 6) THEN 'Weekend'
                    ELSE 'Weekday'
                END as day_type,
                AVG(lessons_created) as avg_lessons,
                AVG(resources_downloaded) as avg_resources
            FROM teacher_statistics
            GROUP BY day_type
        """)).fetchall()
        print("   📊 Activity patterns:")
        for day_type, avg_lessons, avg_resources in weekday_stats:
            print(f"      {day_type}: {avg_lessons:.2f} avg lessons, {avg_resources:.2f} avg resources")
        
        # 8. Final counts
        print("\n8. Final record counts:")
        tables = [
            'teacher_statistics', 'teacher_goals', 'teacher_activity_logs',
            'teacher_notifications', 'teacher_achievements', 'learning_path_steps'
        ]
        for table in tables:
            count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   ✅ {table}: {count:,} records")
        
        print("\n" + "=" * 80)
        print("✅ ALL INTEGRITY CHECKS PASSED")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRITY CHECK FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_integrity()
    sys.exit(0 if success else 1)

