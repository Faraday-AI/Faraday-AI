"""
Migration script for Phase 6 data migration.

This script migrates data from:
- core_dashboard_widgets → dashboard_widgets
- beta_widgets → dashboard_widgets (with beta metadata)
- user_preferences → dashboard_users.preferences (JSON) + dashboard_notification_preferences
- teacher_preferences → dashboard_users.preferences (for beta teachers)
- Consolidates theme and filter configurations

Runs after Phase 11 completes to ensure all parent tables are seeded.

⚠️  IMPORTANT: Before running this migration, run the SQL validation tests:
   python app/scripts/seed_data/test_phase6_migration_sql.py
   
   Or run all migration tests:
   python app/scripts/seed_data/test_all_phase_migrations.py --phase 6
   
   This will catch type coercion errors, missing columns, type mismatches, and other
   SQL issues before they occur in the main script.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


def migrate_phase6_data(session: Session) -> dict:
    """
    Migrate Phase 6 data from source tables to dashboard_* tables.
    
    Phase 6 Migration:
    - core_dashboard_widgets → dashboard_widgets
    - beta_widgets → dashboard_widgets (with beta metadata)
    - user_preferences → dashboard_users.preferences + dashboard_notification_preferences
    - teacher_preferences → dashboard_users.preferences (beta teachers)
    - Theme and filter configuration consolidation
    
    Args:
        session: Database session
        
    Returns:
        dict: Migration results with counts
    """
    results = {
        "widgets": 0,
        "beta_widgets": 0,
        "user_preferences": 0,
        "teacher_preferences": 0,
        "notification_preferences": 0,
        "total": 0
    }
    
    try:
        print("\n" + "=" * 60)
        print("🎨 PHASE 6 DATA MIGRATION (Dashboard Preferences & Configuration)")
        print("=" * 60)
        
        # Check if target tables exist
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'dashboard_widgets'
            )
        """)).scalar()
        
        if not table_exists:
            print("⚠️  Target tables do not exist. Skipping Phase 6 migration.")
            return results
        
        # ==================== MIGRATE core_dashboard_widgets ====================
        print("\n📋 Migrating from core_dashboard_widgets...")
        print("-" * 60)
        try:
            total_widgets = session.execute(text("""
                SELECT COUNT(*) FROM core_dashboard_widgets
            """)).scalar()
            
            if total_widgets > 0:
                # First, get or create a default dashboard for widgets
                default_dashboard_id = session.execute(text("""
                    SELECT id FROM dashboards LIMIT 1
                """)).scalar()
                
                if not default_dashboard_id:
                    # Create a default dashboard
                    default_dashboard = session.execute(text("""
                        INSERT INTO dashboards (
                            name,
                            description,
                            layout,
                            is_active,
                            is_public,
                            created_at,
                            updated_at
                        ) VALUES (
                            'Default Dashboard',
                            'Default dashboard for migrated widgets',
                            '{}'::jsonb,
                            TRUE,
                            FALSE,
                            NOW(),
                            NOW()
                        ) RETURNING id
                    """)).scalar()
                    session.commit()
                    default_dashboard_id = default_dashboard
                
                # Migrate core_dashboard_widgets to dashboard_widgets
                migrated_widgets = session.execute(text("""
                    INSERT INTO dashboard_widgets (
                        name,
                        description,
                        widget_type,
                        layout_position,
                        size,
                        configuration,
                        refresh_interval,
                        is_active,
                        is_visible,
                        user_id,
                        dashboard_id,
                        created_at,
                        updated_at,
                        meta_data
                    )
                    SELECT 
                        COALESCE(cdw.name, 'Widget ' || cdw.id::text) AS name,
                        COALESCE(cdw.configuration::jsonb->>'description', 'Migrated widget') AS description,
                        -- Map widget_type to enum (use uppercase enum names)
                        CASE 
                            WHEN cdw.widget_type::text IN ('chart', 'graph', 'visualization', 'CHART') THEN 'CHART'::widget_type_enum
                            WHEN cdw.widget_type::text IN ('table', 'list', 'data', 'TABLE', 'LIST') THEN 
                                CASE WHEN cdw.widget_type::text IN ('list', 'LIST') THEN 'LIST'::widget_type_enum
                                ELSE 'TABLE'::widget_type_enum END
                            WHEN cdw.widget_type::text IN ('metric', 'kpi', 'stat', 'METRIC') THEN 'METRIC'::widget_type_enum
                            WHEN cdw.widget_type::text IN ('text', 'html', 'markdown') THEN 'CUSTOM'::widget_type_enum
                            ELSE 'CUSTOM'::widget_type_enum
                        END AS widget_type,
                        -- Map layout_position to enum (use uppercase enum names)
                        CASE 
                            WHEN cdw.position::text IN ('top_left', 'TOP_LEFT') THEN 'TOP_LEFT'::widget_layout_enum
                            WHEN cdw.position::text IN ('top_right', 'TOP_RIGHT') THEN 'TOP_RIGHT'::widget_layout_enum
                            WHEN cdw.position::text IN ('bottom_left', 'BOTTOM_LEFT') THEN 'BOTTOM_LEFT'::widget_layout_enum
                            WHEN cdw.position::text IN ('bottom_right', 'BOTTOM_RIGHT') THEN 'BOTTOM_RIGHT'::widget_layout_enum
                            WHEN cdw.position::text IN ('center', 'CENTER') THEN 'CENTER'::widget_layout_enum
                            WHEN cdw.position::text IN ('full_width', 'FULL_WIDTH') THEN 'FULL_WIDTH'::widget_layout_enum
                            ELSE 'CENTER'::widget_layout_enum
                        END AS layout_position,
                        -- Map size from position or use default
                        CASE 
                            WHEN cdw.size IS NULL THEN jsonb_build_object('width', 2, 'height', 2)
                            ELSE cdw.size::jsonb
                        END AS size,
                        CASE WHEN cdw.configuration IS NULL THEN '{}'::jsonb ELSE cdw.configuration::jsonb END AS configuration,
                        NULL AS refresh_interval,  -- Default to NULL
                        COALESCE(cdw.is_active, TRUE) AS is_active,
                        COALESCE(cdw.is_active, TRUE) AS is_visible,
                        cdw.user_id,
                        :default_dashboard_id AS dashboard_id,
                        NOW() AS created_at,
                        NOW() AS updated_at,
                        jsonb_build_object(
                            'migrated_from', 'core_dashboard_widgets',
                            'original_id', cdw.id,
                            'original_metadata', cdw.metadata,
                            'original_status', cdw.status
                        ) AS meta_data
                    FROM core_dashboard_widgets cdw
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_widgets dw
                        WHERE dw.name = COALESCE(cdw.name, 'Widget ' || cdw.id::text)
                        AND dw.user_id = cdw.user_id
                        AND dw.created_at::date = NOW()::date
                        AND dw.meta_data::text LIKE '%migrated_from%core_dashboard_widgets%'
                    )
                """), {"default_dashboard_id": default_dashboard_id})
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_widgets
                    WHERE meta_data::text LIKE '%migrated_from%core_dashboard_widgets%'
                """)).scalar()
                
                results["widgets"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from core_dashboard_widgets")
            else:
                print(f"  ℹ️  No records in core_dashboard_widgets to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating core_dashboard_widgets: {e}")
            logger.warning(f"Error migrating core_dashboard_widgets: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE beta_widgets ====================
        print("\n📋 Migrating from beta_widgets...")
        print("-" * 60)
        try:
            total_beta_widgets = session.execute(text("""
                SELECT COUNT(*) FROM beta_widgets
            """)).scalar()
            
            if total_beta_widgets > 0:
                # Get default dashboard for beta widgets
                default_dashboard_id = session.execute(text("""
                    SELECT id FROM dashboards LIMIT 1
                """)).scalar()
                
                if not default_dashboard_id:
                    # Create a default dashboard
                    default_dashboard = session.execute(text("""
                        INSERT INTO dashboards (
                            name,
                            description,
                            layout,
                            is_active,
                            is_public,
                            created_at,
                            updated_at
                        ) VALUES (
                            'Beta Dashboard',
                            'Default dashboard for beta widgets',
                            '{}'::jsonb,
                            TRUE,
                            FALSE,
                            NOW(),
                            NOW()
                        ) RETURNING id
                    """)).scalar()
                    session.commit()
                    default_dashboard_id = default_dashboard
                
                # Migrate beta_widgets to dashboard_widgets with beta metadata
                migrated_beta_widgets = session.execute(text("""
                    INSERT INTO dashboard_widgets (
                        name,
                        description,
                        widget_type,
                        layout_position,
                        size,
                        configuration,
                        refresh_interval,
                        is_active,
                        is_visible,
                        user_id,
                        dashboard_id,
                        created_at,
                        updated_at,
                        meta_data
                    )
                    SELECT 
                        COALESCE(bw.name, 'Beta Widget ' || bw.id::text) AS name,
                        'Beta teacher widget' AS description,
                        -- Map widget_type to enum (use uppercase enum names)
                        CASE 
                            WHEN bw.widget_type::text IN ('chart', 'graph', 'CHART') THEN 'CHART'::widget_type_enum
                            WHEN bw.widget_type::text IN ('table', 'TABLE') THEN 'TABLE'::widget_type_enum
                            WHEN bw.widget_type::text IN ('list', 'LIST') THEN 'LIST'::widget_type_enum
                            WHEN bw.widget_type::text IN ('metric', 'kpi', 'METRIC') THEN 'METRIC'::widget_type_enum
                            ELSE 'CUSTOM'::widget_type_enum
                        END AS widget_type,
                        'CENTER'::widget_layout_enum AS layout_position,
                        jsonb_build_object('width', 2, 'height', 2) AS size,
                        CASE WHEN bw.configuration IS NULL THEN '{}'::jsonb ELSE bw.configuration::jsonb END AS configuration,
                        NULL AS refresh_interval,
                        COALESCE(bw.is_active, TRUE) AS is_active,
                        COALESCE(bw.is_active, TRUE) AS is_visible,
                        -- Beta widgets don't have direct teacher_id, set to NULL
                        -- Beta service will handle user_id mapping
                        NULL AS user_id,
                        :default_dashboard_id AS dashboard_id,
                        COALESCE(bw.created_at, NOW()) AS created_at,
                        COALESCE(bw.updated_at, NOW()) AS updated_at,
                        jsonb_build_object(
                            'migrated_from', 'beta_widgets',
                            'original_id', bw.id,
                            'beta_system', TRUE,
                            'beta_widget_id', bw.id,
                            'needs_user_id_mapping', TRUE  -- Flag for beta service
                        ) AS meta_data
                    FROM beta_widgets bw
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_widgets dw
                        WHERE dw.name = COALESCE(bw.name, 'Beta Widget ' || bw.id::text)
                        AND dw.created_at::date = COALESCE(bw.created_at, NOW())::date
                        AND dw.meta_data::text LIKE '%migrated_from%beta_widgets%'
                    )
                """), {"default_dashboard_id": default_dashboard_id})
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_widgets
                    WHERE meta_data::text LIKE '%migrated_from%beta_widgets%'
                """)).scalar()
                
                results["beta_widgets"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from beta_widgets")
            else:
                print(f"  ℹ️  No records in beta_widgets to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating beta_widgets: {e}")
            logger.warning(f"Error migrating beta_widgets: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE user_preferences ====================
        print("\n📋 Migrating from user_preferences...")
        print("-" * 60)
        try:
            total_prefs = session.execute(text("""
                SELECT COUNT(*) FROM user_preferences
            """)).scalar()
            
            if total_prefs > 0:
                # Migrate user_preferences to dashboard_users.preferences JSON field
                # Also create dashboard_notification_preferences for notification settings
                migrated_prefs = session.execute(text("""
                    UPDATE dashboard_users du
                    SET preferences = jsonb_build_object(
                        'theme', up.theme,
                        'accent_color', up.accent_color,
                        'font_size', up.font_size,
                        'font_family', up.font_family,
                        'dashboard_layout', up.dashboard_layout,
                        'sidebar_position', up.sidebar_position,
                        'sidebar_collapsed', up.sidebar_collapsed,
                        'grid_view', up.grid_view,
                        'language', up.language,
                        'timezone', up.timezone,
                        'date_format', up.date_format,
                        'time_format', up.time_format,
                        'data_sharing', up.data_sharing,
                        'analytics_opt_in', up.analytics_opt_in,
                        'personalized_ads', up.personalized_ads,
                        'high_contrast', up.high_contrast,
                        'reduced_motion', up.reduced_motion,
                        'migrated_from', 'user_preferences',
                        'migrated_at', NOW()::text
                    )
                    FROM user_preferences up
                    WHERE du.core_user_id = up.user_id
                    AND (du.preferences IS NULL OR du.preferences::text NOT LIKE '%migrated_from%user_preferences%')
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_users
                    WHERE preferences::text LIKE '%migrated_from%user_preferences%'
                """)).scalar()
                
                results["user_preferences"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} user preferences to dashboard_users")
                
                # Also migrate notification preferences
                notification_prefs = session.execute(text("""
                    INSERT INTO dashboard_notification_preferences (
                        user_id,
                        channel,
                        type,
                        enabled,
                        priority_threshold,
                        quiet_hours_start,
                        quiet_hours_end,
                        timezone,
                        batching_enabled,
                        batching_interval,
                        status
                    )
                    SELECT 
                        up.user_id,
                        'EMAIL'::notification_channel_enum AS channel,
                        'SYSTEM'::dashboard_notification_type_enum AS type,
                        COALESCE(up.email_notifications, TRUE) AS enabled,
                        'LOW'::dashboard_notification_priority_enum AS priority_threshold,
                        COALESCE(up.quiet_hours::jsonb->>'start', NULL) AS quiet_hours_start,
                        COALESCE(up.quiet_hours::jsonb->>'end', NULL) AS quiet_hours_end,
                        COALESCE(up.timezone, 'UTC') AS timezone,
                        FALSE AS batching_enabled,
                        5 AS batching_interval,
                        'ACTIVE'::base_status_enum AS status
                    FROM user_preferences up
                    WHERE up.email_notifications IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM dashboard_notification_preferences dnp
                        WHERE dnp.user_id = up.user_id
                        AND dnp.channel = 'EMAIL'::notification_channel_enum
                        AND dnp.type = 'SYSTEM'::dashboard_notification_type_enum
                    )
                """))
                
                session.commit()
                
                notification_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_notification_preferences
                    WHERE user_id IN (SELECT user_id FROM user_preferences)
                """)).scalar()
                
                results["notification_preferences"] = notification_count
                print(f"  ✅ Created {notification_count} notification preferences from user_preferences")
            else:
                print(f"  ℹ️  No records in user_preferences to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating user_preferences: {e}")
            logger.warning(f"Error migrating user_preferences: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE teacher_preferences ====================
        print("\n📋 Migrating from teacher_preferences...")
        print("-" * 60)
        try:
            total_teacher_prefs = session.execute(text("""
                SELECT COUNT(*) FROM teacher_preferences
            """)).scalar()
            
            if total_teacher_prefs > 0:
                # Migrate teacher_preferences to dashboard_users.preferences for beta teachers
                migrated_teacher_prefs = session.execute(text("""
                    UPDATE dashboard_users du
                    SET preferences = COALESCE(
                        du.preferences::jsonb,
                        '{}'::jsonb
                    ) || jsonb_build_object(
                        'teacher_preferences', jsonb_build_object(
                            'preference_type', tp.preference_type,
                            'preference_value', tp.preference_value,
                            'preference_metadata', tp.preference_metadata,
                            'migrated_from', 'teacher_preferences',
                            'migrated_at', NOW()::text
                        )
                    )
                    FROM teacher_preferences tp
                    INNER JOIN physical_education_teachers pet ON tp.teacher_id = pet.id
                    INNER JOIN users u ON u.id = pet.user_id
                    WHERE du.core_user_id = u.id
                    AND (du.preferences IS NULL OR du.preferences::text NOT LIKE '%teacher_preferences%')
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_users
                    WHERE preferences::text LIKE '%teacher_preferences%'
                """)).scalar()
                
                results["teacher_preferences"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} teacher preferences to dashboard_users")
            else:
                print(f"  ℹ️  No records in teacher_preferences to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating teacher_preferences: {e}")
            logger.warning(f"Error migrating teacher_preferences: {e}")
            import traceback
            traceback.print_exc()
        
        results["total"] = sum([
            results["widgets"],
            results["beta_widgets"],
            results["user_preferences"],
            results["teacher_preferences"],
            results["notification_preferences"]
        ])
        
        print(f"\n✅ Phase 6 Data Migration Complete! Total records migrated: {results['total']}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        session.rollback()
        logger.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        raise

