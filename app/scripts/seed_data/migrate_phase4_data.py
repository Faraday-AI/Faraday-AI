"""
Migration script for Phase 4 data migration.

This script migrates data from:
- resource_management_usage → dashboard_resource_usage
- resource_thresholds → dashboard_resource_thresholds
- resource_optimizations → dashboard_resource_optimizations
- resource_management_sharing → dashboard_resource_sharing
- optimization_events → dashboard_optimization_events

Runs after Phase 11 completes to ensure all parent tables are seeded.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def migrate_phase4_data(session: Session) -> dict:
    """
    Migrate Phase 4 data from source tables to dashboard_resource_* tables.
    
    Phase 4 Migration:
    - resource_management_usage → dashboard_resource_usage
    - resource_thresholds → dashboard_resource_thresholds
    - resource_optimizations → dashboard_resource_optimizations
    - resource_management_sharing → dashboard_resource_sharing
    - optimization_events → dashboard_optimization_events
    
    Args:
        session: Database session
        
    Returns:
        dict: Migration results with counts
    """
    results = {
        "resource_usage": 0,
        "resource_thresholds": 0,
        "resource_optimizations": 0,
        "resource_sharing": 0,
        "optimization_events": 0,
        "total": 0
    }
    
    try:
        print("\n" + "=" * 60)
        print("📊 PHASE 4 DATA MIGRATION")
        print("=" * 60)
        
        # Check if target tables exist
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'dashboard_resource_usage'
            )
        """)).scalar()
        
        if not table_exists:
            print("⚠️  Target tables do not exist. Skipping Phase 4 migration.")
            return results
        
        # ==================== MIGRATE resource_management_usage ====================
        print("\n📋 Migrating from resource_management_usage...")
        print("-" * 60)
        try:
            total_usage = session.execute(text("""
                SELECT COUNT(*) FROM resource_management_usage
            """)).scalar()
            
            if total_usage > 0:
                # Migrate resource_management_usage to dashboard_resource_usage
                migrated_usage = session.execute(text("""
                    INSERT INTO dashboard_resource_usage (
                        resource_id,
                        resource_type,
                        metric_type,
                        value,
                        unit,
                        timestamp,
                        meta_data,
                        user_id,
                        project_id,
                        organization_id
                    )
                    SELECT 
                        rmu.resource_id,
                        rmu.resource_type::text::resource_type_enum,
                        rmu.metric_type::text::resource_metric_enum,
                        rmu.value,
                        rmu.unit,
                        rmu.timestamp,
                        jsonb_build_object(
                            'migrated_from', 'resource_management_usage',
                            'original_id', rmu.id,
                            'created_at', rmu.created_at,
                            'updated_at', rmu.updated_at
                        ) AS meta_data,
                        rmu.user_id,
                        rmu.project_id,
                        rmu.organization_id
                    FROM resource_management_usage rmu
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_resource_usage dru
                        WHERE dru.resource_id = rmu.resource_id
                        AND dru.resource_type::text = rmu.resource_type::text
                        AND dru.metric_type::text = rmu.metric_type::text
                        AND dru.timestamp = rmu.timestamp
                        AND dru.meta_data::text LIKE '%migrated_from%resource_management_usage%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records using metadata
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_resource_usage
                    WHERE meta_data::text LIKE '%migrated_from%resource_management_usage%'
                """)).scalar()
                
                results["resource_usage"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from resource_management_usage")
            else:
                print(f"  ℹ️  No records in resource_management_usage to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating resource_management_usage: {e}")
            logger.warning(f"Error migrating resource_management_usage: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE resource_thresholds ====================
        print("\n📋 Migrating from resource_thresholds...")
        print("-" * 60)
        try:
            total_thresholds = session.execute(text("""
                SELECT COUNT(*) FROM resource_thresholds
            """)).scalar()
            
            if total_thresholds > 0:
                # Migrate resource_thresholds to dashboard_resource_thresholds
                migrated_thresholds = session.execute(text("""
                    INSERT INTO dashboard_resource_thresholds (
                        resource_type,
                        metric_type,
                        threshold_value,
                        threshold_type,
                        action,
                        meta_data,
                        user_id,
                        project_id,
                        organization_id
                    )
                    SELECT 
                        rt.resource_type::text::resource_type_enum,
                        rt.metric_type::text::resource_metric_enum,
                        rt.threshold_value,
                        rt.threshold_type,
                        rt.action,
                        jsonb_build_object(
                            'migrated_from', 'resource_thresholds',
                            'original_id', rt.id,
                            'is_active', rt.is_active,
                            'created_at', rt.created_at,
                            'updated_at', rt.updated_at
                        ) AS meta_data,
                        rt.user_id,
                        rt.project_id,
                        rt.organization_id
                    FROM resource_thresholds rt
                    WHERE rt.is_active = true
                    AND NOT EXISTS (
                        SELECT 1 FROM dashboard_resource_thresholds drt
                        WHERE drt.resource_type::text = rt.resource_type::text
                        AND drt.metric_type::text = rt.metric_type::text
                        AND drt.threshold_value = rt.threshold_value
                        AND drt.threshold_type = rt.threshold_type
                        AND drt.meta_data::text LIKE '%migrated_from%resource_thresholds%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records using metadata
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_resource_thresholds
                    WHERE meta_data::text LIKE '%migrated_from%resource_thresholds%'
                """)).scalar()
                
                results["resource_thresholds"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from resource_thresholds")
            else:
                print(f"  ℹ️  No records in resource_thresholds to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating resource_thresholds: {e}")
            logger.warning(f"Error migrating resource_thresholds: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE resource_optimizations ====================
        print("\n📋 Migrating from resource_optimizations...")
        print("-" * 60)
        try:
            total_optimizations = session.execute(text("""
                SELECT COUNT(*) FROM resource_optimizations
            """)).scalar()
            
            if total_optimizations > 0:
                # Migrate resource_optimizations to dashboard_resource_optimizations
                migrated_optimizations = session.execute(text("""
                    INSERT INTO dashboard_resource_optimizations (
                        resource_type,
                        metric_type,
                        current_value,
                        recommended_value,
                        potential_savings,
                        confidence_score,
                        recommendation,
                        status,
                        created_at,
                        applied_at,
                        meta_data,
                        user_id,
                        project_id,
                        organization_id
                    )
                    SELECT 
                        ro.resource_type::text::resource_type_enum,
                        ro.metric_type::text::resource_metric_enum,
                        ro.current_value,
                        ro.recommended_value,
                        ro.potential_savings,
                        ro.confidence_score,
                        ro.recommendation,
                        CASE 
                            WHEN ro.applied = true THEN 'applied'
                            ELSE 'pending'
                        END AS status,
                        ro.created_at,
                        ro.applied_at,
                        jsonb_build_object(
                            'migrated_from', 'resource_optimizations',
                            'original_id', ro.id,
                            'original_applied', ro.applied,
                            'updated_at', ro.updated_at
                        ) AS meta_data,
                        ro.user_id,
                        ro.project_id,
                        ro.organization_id
                    FROM resource_optimizations ro
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_resource_optimizations dro
                        WHERE dro.resource_type::text = ro.resource_type::text
                        AND dro.metric_type::text = ro.metric_type::text
                        AND dro.current_value = ro.current_value
                        AND dro.recommended_value = ro.recommended_value
                        AND dro.created_at = ro.created_at
                        AND dro.meta_data::text LIKE '%migrated_from%resource_optimizations%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records using metadata
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_resource_optimizations
                    WHERE meta_data::text LIKE '%migrated_from%resource_optimizations%'
                """)).scalar()
                
                results["resource_optimizations"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from resource_optimizations")
            else:
                print(f"  ℹ️  No records in resource_optimizations to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating resource_optimizations: {e}")
            logger.warning(f"Error migrating resource_optimizations: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE resource_management_sharing ====================
        print("\n📋 Migrating from resource_management_sharing...")
        print("-" * 60)
        try:
            total_sharing = session.execute(text("""
                SELECT COUNT(*) FROM resource_management_sharing
            """)).scalar()
            
            if total_sharing > 0:
                # Migrate resource_management_sharing to dashboard_resource_sharing
                migrated_sharing = session.execute(text("""
                    INSERT INTO dashboard_resource_sharing (
                        resource_id,
                        resource_type,
                        is_shared,
                        sharing_type,
                        sharing_permissions,
                        sharing_scope,
                        shared_at,
                        expires_at,
                        meta_data,
                        owner_id,
                        shared_with_user_id,
                        shared_with_project_id,
                        shared_with_organization_id
                    )
                    SELECT 
                        rms.resource_id,
                        rms.resource_type::text::resource_type_enum,
                        true AS is_shared,
                        rms.sharing_type,
                        rms.sharing_permissions,
                        rms.sharing_scope,
                        rms.created_at AS shared_at,
                        rms.expires_at,
                        jsonb_build_object(
                            'migrated_from', 'resource_management_sharing',
                            'original_id', rms.id,
                            'updated_at', rms.updated_at
                        ) AS meta_data,
                        rms.owner_id,
                        rms.shared_with_user_id,
                        rms.shared_with_project_id,
                        rms.shared_with_organization_id
                    FROM resource_management_sharing rms
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_resource_sharing drs
                        WHERE drs.resource_id = rms.resource_id
                        AND drs.resource_type::text = rms.resource_type::text
                        AND drs.owner_id = rms.owner_id
                        AND drs.shared_at = rms.created_at
                        AND drs.meta_data::text LIKE '%migrated_from%resource_management_sharing%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records using metadata
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_resource_sharing
                    WHERE meta_data::text LIKE '%migrated_from%resource_management_sharing%'
                """)).scalar()
                
                results["resource_sharing"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from resource_management_sharing")
            else:
                print(f"  ℹ️  No records in resource_management_sharing to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating resource_management_sharing: {e}")
            logger.warning(f"Error migrating resource_management_sharing: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE optimization_events ====================
        print("\n📋 Migrating from optimization_events...")
        print("-" * 60)
        try:
            total_events = session.execute(text("""
                SELECT COUNT(*) FROM optimization_events
            """)).scalar()
            
            if total_events > 0:
                # Migrate optimization_events to dashboard_optimization_events
                migrated_events = session.execute(text("""
                    INSERT INTO dashboard_optimization_events (
                        event_type,
                        status,
                        severity,
                        resource_id,
                        resource_type,
                        metric_type,
                        description,
                        action_taken,
                        action_result,
                        detected_at,
                        resolved_at,
                        meta_data,
                        user_id,
                        project_id,
                        organization_id
                    )
                    SELECT 
                        oe.event_type,
                        CASE 
                            WHEN oe.resolved_at IS NOT NULL THEN 'completed'
                            ELSE 'pending'
                        END AS status,
                        oe.severity,
                        oe.resource_id,
                        oe.resource_type::text::resource_type_enum,
                        oe.metric_type::text::resource_metric_enum,
                        oe.description,
                        oe.action_taken,
                        oe.action_result,
                        oe.detected_at,
                        oe.resolved_at,
                        jsonb_build_object(
                            'migrated_from', 'optimization_events',
                            'original_id', oe.id
                        ) AS meta_data,
                        oe.user_id,
                        oe.project_id,
                        oe.organization_id
                    FROM optimization_events oe
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_optimization_events doe
                        WHERE doe.event_type = oe.event_type
                        AND doe.resource_id = oe.resource_id
                        AND doe.resource_type::text = oe.resource_type::text
                        AND doe.metric_type::text = oe.metric_type::text
                        AND doe.detected_at = oe.detected_at
                        AND doe.meta_data::text LIKE '%migrated_from%optimization_events%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records using metadata
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_optimization_events
                    WHERE meta_data::text LIKE '%migrated_from%optimization_events%'
                """)).scalar()
                
                results["optimization_events"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from optimization_events")
            else:
                print(f"  ℹ️  No records in optimization_events to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating optimization_events: {e}")
            logger.warning(f"Error migrating optimization_events: {e}")
            import traceback
            traceback.print_exc()
        
        results["total"] = sum([
            results["resource_usage"],
            results["resource_thresholds"],
            results["resource_optimizations"],
            results["resource_sharing"],
            results["optimization_events"]
        ])
        print(f"\n✅ Phase 4 Data Migration Complete! Total records migrated: {results['total']}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        session.rollback()
        logger.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        raise

