"""
Migration script for Phase 5 data migration.

This script migrates data from:
- gpt_interaction_contexts → dashboard_gpt_contexts
- gpt_context_interactions → dashboard_context_interactions
- gpt_context_summaries → dashboard_context_summaries
- gpt_context_backups → dashboard_context_backups
- gpt_context_metrics → dashboard_context_metrics
- gpt_context_sharing → dashboard_shared_contexts (mapped appropriately)
- shared_contexts → dashboard_shared_contexts (mapped appropriately)

Runs after Phase 11 completes to ensure all parent tables are seeded.

⚠️  IMPORTANT: Before running this migration, run the SQL validation tests:
   python app/scripts/seed_data/test_phase5_migration_sql.py
   
   Or run all migration tests:
   python app/scripts/seed_data/test_all_phase_migrations.py --phase 5
   
   This will catch type coercion errors, missing columns, and other SQL issues
   before they occur in the main script.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def migrate_phase5_data(session: Session) -> dict:
    """
    Migrate Phase 5 data from source GPT context tables to dashboard_context_* tables.
    
    Phase 5 Migration:
    - gpt_interaction_contexts → dashboard_gpt_contexts
    - gpt_context_interactions → dashboard_context_interactions
    - gpt_context_summaries → dashboard_context_summaries
    - gpt_context_backups → dashboard_context_backups
    - gpt_context_metrics → dashboard_context_metrics
    - gpt_context_sharing → dashboard_shared_contexts
    - shared_contexts → dashboard_shared_contexts
    
    Args:
        session: Database session
        
    Returns:
        dict: Migration results with counts
    """
    results = {
        "gpt_contexts": 0,
        "context_interactions": 0,
        "context_summaries": 0,
        "context_backups": 0,
        "context_metrics": 0,
        "shared_contexts": 0,
        "total": 0
    }
    
    try:
        print("\n" + "=" * 60)
        print("🤖 PHASE 5 DATA MIGRATION (GPT Context Analytics)")
        print("=" * 60)
        
        # Check if target tables exist
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'dashboard_gpt_contexts'
            )
        """)).scalar()
        
        if not table_exists:
            print("⚠️  Target tables do not exist. Skipping Phase 5 migration.")
            return results
        
        # ==================== MIGRATE gpt_interaction_contexts ====================
        print("\n📋 Migrating from gpt_interaction_contexts...")
        print("-" * 60)
        try:
            total_contexts = session.execute(text("""
                SELECT COUNT(*) FROM gpt_interaction_contexts
            """)).scalar()
            
            if total_contexts > 0:
                # Migrate gpt_interaction_contexts to dashboard_gpt_contexts
                # Need to map user_id from users to dashboard_users
                migrated_contexts = session.execute(text("""
                    INSERT INTO dashboard_gpt_contexts (
                        user_id,
                        primary_gpt_id,
                        name,
                        description,
                        context_data,
                        is_active,
                        created_at,
                        updated_at
                    )
                    SELECT 
                        COALESCE(du.id, gic.user_id) AS user_id,  -- Map to dashboard_users if exists, else use original
                        gic.primary_gpt_id,
                        gic.name,
                        gic.description,
                        -- Preserve beta system metadata if present
                        -- Cast JSON to JSONB first to avoid type coercion errors
                        CASE 
                            WHEN gic.context_data::text LIKE '%beta_teacher_id%' OR gic.context_data::text LIKE '%beta_system%' THEN
                                gic.context_data::jsonb
                            WHEN gic.context_data IS NULL THEN
                                '{}'::jsonb
                            ELSE
                                gic.context_data::jsonb
                        END AS context_data,
                        CASE 
                            WHEN gic.status IS NULL THEN TRUE
                            WHEN gic.status::text = 'inactive' THEN FALSE
                            ELSE TRUE
                        END AS is_active,
                        COALESCE(gic.created_at, NOW()) AS created_at,
                        COALESCE(gic.updated_at, NOW()) AS updated_at
                    FROM gpt_interaction_contexts gic
                    LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_gpt_contexts dgc
                        WHERE dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                        AND dgc.created_at::date = COALESCE(gic.created_at, NOW())::date
                    )
                """))
                
                session.commit()
                
                # Count migrated records using metadata pattern (if we track it)
                # Since we're using name matching, count by checking for contexts that match migrated patterns
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_gpt_contexts dgc
                    WHERE EXISTS (
                        SELECT 1 FROM gpt_interaction_contexts gic
                        LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                        WHERE dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                    )
                """)).scalar()
                
                results["gpt_contexts"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from gpt_interaction_contexts")
            else:
                print(f"  ℹ️  No records in gpt_interaction_contexts to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating gpt_interaction_contexts: {e}")
            logger.warning(f"Error migrating gpt_interaction_contexts: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE gpt_context_interactions ====================
        print("\n📋 Migrating from gpt_context_interactions...")
        print("-" * 60)
        try:
            total_interactions = session.execute(text("""
                SELECT COUNT(*) FROM gpt_context_interactions
            """)).scalar()
            
            if total_interactions > 0:
                # Migrate gpt_context_interactions to dashboard_context_interactions
                # Need to map context_id from gpt_interaction_contexts to dashboard_gpt_contexts
                migrated_interactions = session.execute(text("""
                    INSERT INTO dashboard_context_interactions (
                        context_id,
                        gpt_id,
                        interaction_type,
                        content,
                        meta_data,
                        timestamp
                    )
                    SELECT 
                        dgc.id AS context_id,  -- Map to dashboard_gpt_contexts
                        gci.gpt_id,
                        -- Convert enum to text (handle NULL case)
                        CASE 
                            WHEN gci.interaction_type IS NULL THEN 'message'
                            ELSE gci.interaction_type::text
                        END AS interaction_type,
                        CASE 
                            WHEN gci.content IS NULL THEN '{}'::jsonb
                            ELSE gci.content::jsonb
                        END AS content,
                        jsonb_build_object(
                            'migrated_from', 'gpt_context_interactions',
                            'original_id', gci.id,
                            'role', gci.role,
                            'token_count', gci.token_count,
                            'processing_time', gci.processing_time,
                            'processed_at', gci.processed_at,
                            'user_id', gci.user_id,
                            'project_id', gci.project_id,
                            'organization_id', gci.organization_id
                        ) AS meta_data,
                        COALESCE(gci.processed_at, NOW()) AS timestamp
                    FROM gpt_context_interactions gci
                    INNER JOIN gpt_interaction_contexts gic ON gci.context_id = gic.id
                    LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                    INNER JOIN dashboard_gpt_contexts dgc ON (
                        dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                    )
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_context_interactions dci
                        WHERE dci.context_id = dgc.id
                        AND dci.gpt_id = gci.gpt_id
                        AND dci.interaction_type = gci.interaction_type::text
                        AND dci.timestamp = COALESCE(gci.processed_at, NOW())
                        AND dci.meta_data::text LIKE '%migrated_from%gpt_context_interactions%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_context_interactions
                    WHERE meta_data::text LIKE '%migrated_from%gpt_context_interactions%'
                """)).scalar()
                
                results["context_interactions"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from gpt_context_interactions")
            else:
                print(f"  ℹ️  No records in gpt_context_interactions to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating gpt_context_interactions: {e}")
            logger.warning(f"Error migrating gpt_context_interactions: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE gpt_context_summaries ====================
        print("\n📋 Migrating from gpt_context_summaries...")
        print("-" * 60)
        try:
            total_summaries = session.execute(text("""
                SELECT COUNT(*) FROM gpt_context_summaries
            """)).scalar()
            
            if total_summaries > 0:
                # Migrate gpt_context_summaries to dashboard_context_summaries
                # Convert summary structure to JSON format
                migrated_summaries = session.execute(text("""
                    INSERT INTO dashboard_context_summaries (
                        context_id,
                        summary,
                        meta_data,
                        created_at
                    )
                    SELECT 
                        dgc.id AS context_id,  -- Map to dashboard_gpt_contexts
                        jsonb_build_object(
                            'text', COALESCE(gcs.summary, ''),
                            'key_points', CASE WHEN gcs.key_points IS NULL THEN '[]'::jsonb ELSE gcs.key_points::jsonb END,
                            'sentiment', gcs.sentiment,
                            'topics', CASE WHEN gcs.topics IS NULL THEN '[]'::jsonb ELSE gcs.topics::jsonb END,
                            'summary_type', COALESCE(gcs.summary_type, 'general'),
                            'confidence_score', gcs.confidence_score
                        ) AS summary,
                        jsonb_build_object(
                            'migrated_from', 'gpt_context_summaries',
                            'original_id', gcs.id,
                            'token_count', COALESCE(gcs.token_count, 0),
                            'summary_metadata', CASE WHEN gcs.summary_metadata IS NULL THEN '{}'::jsonb ELSE gcs.summary_metadata::jsonb END,
                            'user_id', gcs.user_id,
                            'project_id', gcs.project_id,
                            'organization_id', gcs.organization_id
                        ) AS meta_data,
                        COALESCE(gcs.created_at, NOW()) AS created_at
                    FROM gpt_context_summaries gcs
                    INNER JOIN gpt_interaction_contexts gic ON gcs.context_id = gic.id
                    LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                    INNER JOIN dashboard_gpt_contexts dgc ON (
                        dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                    )
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_context_summaries dcs
                        WHERE dcs.context_id = dgc.id
                        AND dcs.created_at = COALESCE(gcs.created_at, NOW())
                        AND dcs.meta_data::text LIKE '%migrated_from%gpt_context_summaries%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_context_summaries
                    WHERE meta_data::text LIKE '%migrated_from%gpt_context_summaries%'
                """)).scalar()
                
                results["context_summaries"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from gpt_context_summaries")
            else:
                print(f"  ℹ️  No records in gpt_context_summaries to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating gpt_context_summaries: {e}")
            logger.warning(f"Error migrating gpt_context_summaries: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE gpt_context_backups ====================
        print("\n📋 Migrating from gpt_context_backups...")
        print("-" * 60)
        try:
            total_backups = session.execute(text("""
                SELECT COUNT(*) FROM gpt_context_backups
            """)).scalar()
            
            if total_backups > 0:
                # Migrate gpt_context_backups to dashboard_context_backups
                # Convert backup_content to backup_data (JSON format)
                migrated_backups = session.execute(text("""
                    INSERT INTO dashboard_context_backups (
                        context_id,
                        backup_data,
                        created_at
                    )
                    SELECT 
                        dgc.id AS context_id,  -- Map to dashboard_gpt_contexts
                        jsonb_build_object(
                            'backup_content', CASE WHEN gcb.backup_content IS NULL THEN '{}'::jsonb ELSE gcb.backup_content::jsonb END,
                            'backup_type', COALESCE(gcb.backup_type, 'manual'),
                            'backup_reason', gcb.backup_reason,
                            'backup_metadata', CASE WHEN gcb.backup_metadata IS NULL THEN '{}'::jsonb ELSE gcb.backup_metadata::jsonb END,
                            'error_message', gcb.error_message,
                            'is_restored', COALESCE(gcb.is_restored, FALSE),
                            'restored_at', gcb.restored_at
                        ) AS backup_data,
                        NOW() AS created_at
                    FROM gpt_context_backups gcb
                    INNER JOIN gpt_interaction_contexts gic ON gcb.context_id = gic.id
                    LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                    INNER JOIN dashboard_gpt_contexts dgc ON (
                        dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                    )
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_context_backups dcb
                        WHERE dcb.context_id = dgc.id
                        AND dcb.created_at::date = NOW()::date
                        AND dcb.backup_data::text LIKE '%migrated_from%gpt_context_backups%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_context_backups
                    WHERE backup_data::text LIKE '%migrated_from%gpt_context_backups%'
                """)).scalar()
                
                results["context_backups"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from gpt_context_backups")
            else:
                print(f"  ℹ️  No records in gpt_context_backups to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating gpt_context_backups: {e}")
            logger.warning(f"Error migrating gpt_context_backups: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE gpt_context_metrics ====================
        print("\n📋 Migrating from gpt_context_metrics...")
        print("-" * 60)
        try:
            total_metrics = session.execute(text("""
                SELECT COUNT(*) FROM gpt_context_metrics
            """)).scalar()
            
            if total_metrics > 0:
                # Migrate gpt_context_metrics to dashboard_context_metrics
                # Convert value/metric_metadata to metric_data (JSON format)
                migrated_metrics = session.execute(text("""
                    INSERT INTO dashboard_context_metrics (
                        context_id,
                        metric_type,
                        metric_data,
                        timestamp
                    )
                    SELECT 
                        dgc.id AS context_id,  -- Map to dashboard_gpt_contexts
                        gcm.metric_type,
                        jsonb_build_object(
                            'value', gcm.value,
                            'metric_metadata', CASE WHEN gcm.metric_metadata IS NULL THEN '{}'::jsonb ELSE gcm.metric_metadata::jsonb END,
                            'migrated_from', 'gpt_context_metrics',
                            'original_id', gcm.id,
                            'created_at', gcm.created_at,
                            'updated_at', gcm.updated_at
                        ) AS metric_data,
                        COALESCE(gcm.timestamp, gcm.created_at, NOW()) AS timestamp
                    FROM gpt_context_metrics gcm
                    INNER JOIN gpt_interaction_contexts gic ON gcm.context_id = gic.id
                    LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                    INNER JOIN dashboard_gpt_contexts dgc ON (
                        dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                    )
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_context_metrics dcm
                        WHERE dcm.context_id = dgc.id
                        AND dcm.metric_type = gcm.metric_type
                        AND dcm.timestamp = COALESCE(gcm.timestamp, gcm.created_at, NOW())
                        AND dcm.metric_data::text LIKE '%migrated_from%gpt_context_metrics%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_context_metrics
                    WHERE metric_data::text LIKE '%migrated_from%gpt_context_metrics%'
                """)).scalar()
                
                results["context_metrics"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from gpt_context_metrics")
            else:
                print(f"  ℹ️  No records in gpt_context_metrics to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating gpt_context_metrics: {e}")
            logger.warning(f"Error migrating gpt_context_metrics: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== MIGRATE shared_contexts ====================
        print("\n📋 Migrating from shared_contexts...")
        print("-" * 60)
        try:
            total_shared = session.execute(text("""
                SELECT COUNT(*) FROM shared_contexts
            """)).scalar()
            
            if total_shared > 0:
                # Migrate shared_contexts to dashboard_shared_contexts
                # Map context_id and handle source_gpt_id/target_gpt_id appropriately
                migrated_shared = session.execute(text("""
                    INSERT INTO dashboard_shared_contexts (
                        context_id,
                        source_gpt_id,
                        target_gpt_id,
                        shared_data,
                        meta_data,
                        created_at
                    )
                    SELECT 
                        dgc.id AS context_id,  -- Map to dashboard_gpt_contexts
                        -- For source_gpt_id and target_gpt_id, use the context's primary_gpt_id
                        -- If shared_contexts has metadata about target GPT, extract it, otherwise use primary
                        dgc.primary_gpt_id AS source_gpt_id,
                        COALESCE(
                            (sc.metadata::jsonb->>'target_gpt_id')::int,
                            dgc.primary_gpt_id
                        ) AS target_gpt_id,
                        jsonb_build_object(
                            'sharing_type', COALESCE(sc.sharing_type::text, 'private'),
                            'sharing_permissions', CASE WHEN sc.sharing_permissions IS NULL THEN '{}'::jsonb ELSE sc.sharing_permissions::jsonb END,
                            'sharing_scope', COALESCE(sc.sharing_scope::text, 'private'),
                            'access_count', sc.access_count,
                            'last_accessed', sc.last_accessed,
                            'expires_at', sc.expires_at
                        ) AS shared_data,
                        jsonb_build_object(
                            'migrated_from', 'shared_contexts',
                            'original_id', sc.id,
                            'owner_id', sc.owner_id,
                            'shared_with_user_id', sc.shared_with_user_id,
                            'shared_with_project_id', sc.shared_with_project_id,
                            'shared_with_organization_id', sc.shared_with_organization_id
                        ) AS meta_data,
                        NOW() AS created_at
                    FROM shared_contexts sc
                    INNER JOIN gpt_interaction_contexts gic ON sc.context_id = gic.id
                    LEFT JOIN dashboard_users du ON du.core_user_id = gic.user_id
                    INNER JOIN dashboard_gpt_contexts dgc ON (
                        dgc.name = gic.name
                        AND dgc.user_id = COALESCE(du.id, gic.user_id)
                        AND dgc.primary_gpt_id = gic.primary_gpt_id
                    )
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dashboard_shared_contexts dsc
                        WHERE dsc.context_id = dgc.id
                        AND dsc.created_at::date = NOW()::date
                        AND dsc.meta_data::text LIKE '%migrated_from%shared_contexts%'
                    )
                """))
                
                session.commit()
                
                # Count migrated records
                migrated_count = session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_shared_contexts
                    WHERE meta_data::text LIKE '%migrated_from%shared_contexts%'
                """)).scalar()
                
                results["shared_contexts"] = migrated_count
                print(f"  ✅ Migrated {migrated_count} records from shared_contexts")
            else:
                print(f"  ℹ️  No records in shared_contexts to migrate")
                
        except Exception as e:
            session.rollback()
            print(f"  ⚠️ Error migrating shared_contexts: {e}")
            logger.warning(f"Error migrating shared_contexts: {e}")
            import traceback
            traceback.print_exc()
        
        results["total"] = sum([
            results["gpt_contexts"],
            results["context_interactions"],
            results["context_summaries"],
            results["context_backups"],
            results["context_metrics"],
            results["shared_contexts"]
        ])
        
        print(f"\n✅ Phase 5 Data Migration Complete! Total context records migrated: {results['total']}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        session.rollback()
        logger.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        raise

