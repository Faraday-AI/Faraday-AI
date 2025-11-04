#!/usr/bin/env python3
"""
Quick script to populate specific tables that need data:
- ai_assistant_templates (Phase 1.10 fix)
- Test student data (if SEED_TEST_STUDENT_DATA=true)
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def main():
    print("=" * 80)
    print("POPULATING SPECIFIC TABLES".center(80))
    print("=" * 80)
    
    session = SessionLocal()
    try:
        # 1. Seed AI Assistant Templates (Phase 1.10 fix)
        print("\n📋 Step 1: Seeding AI Assistant Templates...")
        print("-" * 80)
        from app.scripts.seed_data.seed_ai_assistant_templates import seed_ai_assistant_templates
        
        # Check if already populated
        from sqlalchemy import text
        existing_count = session.execute(text("SELECT COUNT(*) FROM ai_assistant_templates")).scalar()
        
        if existing_count == 0:
            seed_ai_assistant_templates(session)
            session.commit()
            print(f"✅ Seeded 5 AI assistant templates")
        else:
            print(f"ℹ️  AI assistant templates already populated ({existing_count} templates)")
        
        # 2. Optionally seed test student data
        seed_test_data = os.getenv("SEED_TEST_STUDENT_DATA", "").lower() == "true"
        
        if seed_test_data:
            print("\n📋 Step 2: Seeding Test Student Data...")
            print("-" * 80)
            from app.scripts.seed_data.seed_test_student_data import seed_test_student_data
            seed_test_student_data(session, for_tests=True)
            session.commit()
            print("✅ Test student data seeded")
        else:
            print("\n📋 Step 2: Skipping Test Student Data (set SEED_TEST_STUDENT_DATA=true to enable)")
            print("-" * 80)
            print("ℹ️  Test student data is optional and only needed for:")
            print("   - Beta students API endpoint testing")
            print("   - Drivers Ed & Health curriculum testing")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY".center(80))
        print("=" * 80)
        
        ai_count = session.execute(text("SELECT COUNT(*) FROM ai_assistant_templates")).scalar()
        beta_count = session.execute(text("SELECT COUNT(*) FROM beta_students")).scalar()
        drivers_ed_count = session.execute(text("SELECT COUNT(*) FROM drivers_ed_student_progress")).scalar()
        health_count = session.execute(text("SELECT COUNT(*) FROM health_student_progress")).scalar()
        
        print(f"  ✅ ai_assistant_templates: {ai_count} records")
        print(f"  {'✅' if seed_test_data else 'ℹ️ '} beta_students: {beta_count} records")
        print(f"  {'✅' if seed_test_data else 'ℹ️ '} drivers_ed_student_progress: {drivers_ed_count} records")
        print(f"  {'✅' if seed_test_data else 'ℹ️ '} health_student_progress: {health_count} records")
        
        print("\n✅ Table population complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()

