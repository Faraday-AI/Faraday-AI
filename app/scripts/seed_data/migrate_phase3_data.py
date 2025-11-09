"""
Migration script for Phase 3 data migration.

This script migrates data from:
- security_logs → security_events
- security_audits → security_events
- security_general_audit_logs → security_events

Runs after Phase 11 completes to ensure all parent tables are seeded.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def migrate_phase3_data(session: Session) -> dict:
    """
    Migrate Phase 3 data from existing security tables to security_events table.
    
    Phase 3 Migration:
    - security_logs → security_events
    - security_audits → security_events
    - security_general_audit_logs → security_events
    
    Args:
        session: Database session
        
    Returns:
        dict: Migration results with counts
    """
    results = {
        "security_logs": 0,
        "security_audits": 0,
        "security_general_audit_logs": 0,
        "total": 0
    }
    
    try:
        print("\n" + "=" * 60)
        print("🔒 PHASE 3 DATA MIGRATION")
        print("=" * 60)
        
        # Check if security_events table exists
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'security_events'
            )
        """)).scalar()
        
        if not table_exists:
            print("  ⚠️ security_events table does not exist. Creating it...")
            # Create table using raw SQL (will be created by model migration in production)
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(100) NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    ip_address VARCHAR(45),
                    details JSONB,
                    description TEXT,
                    severity VARCHAR(20) DEFAULT 'info',
                    resource_type VARCHAR(50),
                    resource_id VARCHAR(100),
                    action VARCHAR(50),
                    success VARCHAR(10) DEFAULT 'unknown',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            session.commit()
            print("  ✅ security_events table created")
        
        # ==================== MIGRATE security_logs ====================
        print("\n📋 Migrating security_logs to security_events")
        print("-" * 60)
        
        try:
            # Check if security_logs table exists and has data
            logs_exist = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'security_logs'
                )
            """)).scalar()
            
            if logs_exist:
                # Count existing security_logs
                total_logs = session.execute(text("""
                    SELECT COUNT(*) FROM security_logs
                """)).scalar()
                
                if total_logs > 0:
                    # Migrate security_logs to security_events
                    # Use raw SQL to migrate data with metadata tracking
                    migrated_logs = session.execute(text("""
                        INSERT INTO security_events (
                            event_type,
                            user_id,
                            ip_address,
                            details,
                            description,
                            severity,
                            created_at,
                            updated_at
                        )
                        SELECT 
                            sl.event_type,
                            sl.user_id,
                            sl.source_ip AS ip_address,
                            jsonb_build_object(
                                'migrated_from', 'security_logs',
                                'original_id', sl.id,
                                'original_severity', sl.severity,
                                'original_metadata', sl.security_metadata
                            ) AS details,
                            sl.description,
                            CASE 
                                WHEN sl.severity = 'HIGH' THEN 'error'
                                WHEN sl.severity = 'MEDIUM' THEN 'warning'
                                WHEN sl.severity = 'LOW' THEN 'info'
                                ELSE 'info'
                            END AS severity,
                            sl.created_at,
                            NOW() AS updated_at
                        FROM security_logs sl
                        WHERE NOT EXISTS (
                            SELECT 1 FROM security_events se
                            WHERE se.event_type = sl.event_type
                            AND COALESCE(se.user_id, -1) = COALESCE(sl.user_id, -1)
                            AND se.created_at = sl.created_at
                            AND se.description = sl.description
                            AND se.details::text LIKE '%migrated_from%security_logs%'
                        )
                    """))
                    
                    session.commit()
                    
                    # Count migrated records using metadata
                    migrated_count = session.execute(text("""
                        SELECT COUNT(*) FROM security_events
                        WHERE details::text LIKE '%migrated_from%security_logs%'
                    """)).scalar()
                    
                    results["security_logs"] = migrated_count
                    print(f"  ✅ Migrated {migrated_count} records from security_logs")
                else:
                    print(f"  ℹ️  No records in security_logs to migrate")
            else:
                print(f"  ℹ️  security_logs table does not exist")
                
        except Exception as e:
            print(f"  ⚠️ Error migrating security_logs: {e}")
            logger.warning(f"Error migrating security_logs: {e}")
            import traceback
            logger.warning(traceback.format_exc())
        
        # ==================== MIGRATE security_audits ====================
        print("\n📋 Migrating security_audits to security_events")
        print("-" * 60)
        
        try:
            # Check if security_audits table exists and has data
            audits_exist = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'security_audits'
                )
            """)).scalar()
            
            if audits_exist:
                # Count existing security_audits
                total_audits = session.execute(text("""
                    SELECT COUNT(*) FROM security_audits
                """)).scalar()
                
                if total_audits > 0:
                    # Migrate security_audits to security_events with metadata tracking
                    migrated_audits = session.execute(text("""
                        INSERT INTO security_events (
                            event_type,
                            user_id,
                            ip_address,
                            details,
                            description,
                            severity,
                            resource_type,
                            resource_id,
                            action,
                            created_at,
                            updated_at
                        )
                        SELECT 
                            'security_audit' AS event_type,
                            sa.user_id,
                            sa.ip_address,
                            jsonb_build_object(
                                'migrated_from', 'security_audits',
                                'original_id', sa.id,
                                'original_details', sa.details,
                                'user_agent', sa.user_agent
                            ) AS details,
                            COALESCE(sa.details::text, 'Security audit: ' || sa.action) AS description,
                            'info' AS severity,
                            sa.resource_type,
                            sa.resource_id,
                            sa.action,
                            sa.timestamp AS created_at,
                            NOW() AS updated_at
                        FROM security_audits sa
                        WHERE NOT EXISTS (
                            SELECT 1 FROM security_events se
                            WHERE se.event_type = 'security_audit'
                            AND COALESCE(se.user_id, -1) = COALESCE(sa.user_id, -1)
                            AND se.resource_type = sa.resource_type
                            AND se.resource_id = sa.resource_id
                            AND se.action = sa.action
                            AND se.created_at = sa.timestamp
                            AND se.details::text LIKE '%migrated_from%security_audits%'
                        )
                    """))
                    
                    session.commit()
                    
                    # Count migrated records using metadata
                    migrated_count = session.execute(text("""
                        SELECT COUNT(*) FROM security_events
                        WHERE details::text LIKE '%migrated_from%security_audits%'
                    """)).scalar()
                    
                    results["security_audits"] = migrated_count
                    print(f"  ✅ Migrated {migrated_count} records from security_audits")
                else:
                    print(f"  ℹ️  No records in security_audits to migrate")
            else:
                print(f"  ℹ️  security_audits table does not exist")
                
        except Exception as e:
            print(f"  ⚠️ Error migrating security_audits: {e}")
            logger.warning(f"Error migrating security_audits: {e}")
            import traceback
            logger.warning(traceback.format_exc())
        
        # ==================== MIGRATE security_general_audit_logs ====================
        print("\n📋 Migrating security_general_audit_logs to security_events")
        print("-" * 60)
        
        try:
            # Check if security_general_audit_logs table exists and has data
            general_audits_exist = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'security_general_audit_logs'
                )
            """)).scalar()
            
            if general_audits_exist:
                # Count existing security_general_audit_logs
                total_general_audits = session.execute(text("""
                    SELECT COUNT(*) FROM security_general_audit_logs
                """)).scalar()
                
                if total_general_audits > 0:
                    # Migrate security_general_audit_logs to security_events with metadata tracking
                    migrated_general_audits = session.execute(text("""
                        INSERT INTO security_events (
                            event_type,
                            user_id,
                            details,
                            description,
                            severity,
                            resource_type,
                            action,
                            created_at,
                            updated_at
                        )
                        SELECT 
                            'general_audit' AS event_type,
                            sgal.user_id,
                            jsonb_build_object(
                                'migrated_from', 'security_general_audit_logs',
                                'original_id', sgal.id,
                                'original_details', sgal.details,
                                'module', sgal.module
                            ) AS details,
                            COALESCE(sgal.details::text, 'General audit: ' || sgal.action || ' in ' || sgal.module) AS description,
                            'info' AS severity,
                            sgal.module AS resource_type,
                            sgal.action,
                            sgal.timestamp AS created_at,
                            NOW() AS updated_at
                        FROM security_general_audit_logs sgal
                        WHERE NOT EXISTS (
                            SELECT 1 FROM security_events se
                            WHERE se.event_type = 'general_audit'
                            AND COALESCE(se.user_id, -1) = COALESCE(sgal.user_id, -1)
                            AND se.resource_type = sgal.module
                            AND se.action = sgal.action
                            AND se.created_at = sgal.timestamp
                            AND se.details::text LIKE '%migrated_from%security_general_audit_logs%'
                        )
                    """))
                    
                    session.commit()
                    
                    # Count migrated records using metadata
                    migrated_count = session.execute(text("""
                        SELECT COUNT(*) FROM security_events
                        WHERE details::text LIKE '%migrated_from%security_general_audit_logs%'
                    """)).scalar()
                    
                    results["security_general_audit_logs"] = migrated_count
                    print(f"  ✅ Migrated {migrated_count} records from security_general_audit_logs")
                else:
                    print(f"  ℹ️  No records in security_general_audit_logs to migrate")
            else:
                print(f"  ℹ️  security_general_audit_logs table does not exist")
                
        except Exception as e:
            print(f"  ⚠️ Error migrating security_general_audit_logs: {e}")
            logger.warning(f"Error migrating security_general_audit_logs: {e}")
            import traceback
            logger.warning(traceback.format_exc())
        
        # Calculate total
        results["total"] = (
            results["security_logs"] +
            results["security_audits"] +
            results["security_general_audit_logs"]
        )
        
        print(f"\n  ✅ Phase 3 Migration Complete:")
        print(f"     - Security logs migrated: {results['security_logs']}")
        print(f"     - Security audits migrated: {results['security_audits']}")
        print(f"     - General audit logs migrated: {results['security_general_audit_logs']}")
        print(f"     - Total migrated: {results['total']}")
        
        # Commit all changes
        session.commit()
        
        return results
        
    except Exception as e:
        print(f"\n❌ Phase 3 migration error: {e}")
        session.rollback()
        logger.error(f"Phase 3 migration error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

