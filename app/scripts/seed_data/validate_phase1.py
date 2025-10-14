#!/usr/bin/env python3
"""
Phase 1 Validation Script
Stops early if critical Phase 1 tables are not properly populated
"""

import sys
import os
sys.path.insert(0, '/app')

from sqlalchemy import create_engine, text
from app.core.config import settings

def validate_phase1():
    """Validate that Phase 1 critical tables are populated"""
    print("🔍 PHASE 1 VALIDATION SCRIPT")
    print("=" * 50)
    print("This script will stop early if Phase 1 tables are not properly populated")
    print("=" * 50)
    
    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("\n🌱 RUNNING PHASE 1: FOUNDATION & CORE INFRASTRUCTURE")
        print("=" * 60)
        
        try:
            from app.scripts.seed_data.seed_phase1_foundation import seed_phase1_foundation
            seed_phase1_foundation()
            conn.commit()
            print("✅ Phase 1 foundation & core infrastructure completed successfully!")
        except Exception as e:
            print(f"❌ Error seeding Phase 1 foundation: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False
        
        print("\n🔍 VALIDATING CRITICAL PHASE 1 TABLES")
        print("=" * 50)
        
        # Critical tables that must be populated
        critical_tables = {
            'permissions': 'Basic permissions system',
            'role_permissions': 'Role-permission mappings', 
            'permission_overrides': 'Permission overrides',
            'feedback_user_tool_settings': 'User tool settings',
            'user_management_voice_preferences': 'Voice preferences',
            'user_management_preferences': 'User management preferences',
            'user_management_user_organizations': 'User-organization mappings',
            'user_tool_settings': 'User tool configurations',
            'user_tools': 'User tool assignments',
            'user_preference_categories': 'Preference categories',
            'user_preference_templates': 'Preference templates',
            'user_preference_template_assignments': 'Template assignments',
            'user_recommendations': 'User recommendations',
            'role_hierarchy': 'Role hierarchy',
            'role_templates': 'Role templates',
            'security_preferences': 'Security preferences',
            'sessions': 'User sessions',
            'shared_contexts': 'Shared contexts',
            'tool_assignments': 'Tool assignments',
            'voice_templates': 'Voice templates',
            'voices': 'Voice configurations',
            'avatar_templates': 'Avatar templates',
            'avatar_customizations': 'Avatar customizations',
            'user_avatars': 'User avatars',
            'user_avatar_customizations': 'User avatar customizations',
            'student_avatar_customizations': 'Student avatar customizations'
        }
        
        # Check each critical table
        populated_count = 0
        failed_tables = []
        
        for table, description in critical_tables.items():
            try:
                count = conn.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                if count > 0:
                    print(f"  ✅ {table}: {count} records - {description}")
                    populated_count += 1
                else:
                    print(f"  ❌ {table}: 0 records - {description}")
                    failed_tables.append(table)
            except Exception as e:
                print(f"  ⚠️ {table}: Error - {e}")
                failed_tables.append(table)
        
        print(f"\n📊 PHASE 1 VALIDATION RESULTS:")
        print(f"  ✅ Successfully populated: {populated_count}/{len(critical_tables)} tables")
        print(f"  ❌ Failed tables: {len(failed_tables)}")
        
        if failed_tables:
            print(f"\n❌ PHASE 1 VALIDATION FAILED!")
            print(f"   Failed tables: {', '.join(failed_tables)}")
            print(f"   Stopping script early to save time.")
            print(f"   Fix these tables before running the full script.")
            return False
        else:
            print(f"\n✅ PHASE 1 VALIDATION PASSED!")
            print(f"   All critical tables are populated.")
            print(f"   You can now run the full script with confidence.")
            return True

if __name__ == "__main__":
    success = validate_phase1()
    if success:
        print("\n🎉 Phase 1 is ready! You can proceed with the full script.")
        sys.exit(0)
    else:
        print("\n⚠️ Phase 1 needs fixes before running the full script.")
        sys.exit(1)
