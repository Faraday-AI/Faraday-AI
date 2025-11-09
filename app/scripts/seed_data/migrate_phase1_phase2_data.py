"""
Migration script for Phase 1 and Phase 2 data migration.

This script migrates data from:
- Phase 1: skill_assessment_safety_* tables → safety_protocols, safety_incidents, risk_assessments, emergency_procedures
- Phase 2: general_* tables → skill_assessment_* tables

Runs after Phase 10 completes to ensure all parent tables are seeded.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def migrate_phase1_phase2_data(session: Session) -> dict:
    """
    Migrate Phase 1 and Phase 2 data from source tables to target tables.
    
    Phase 1 Migration:
    - skill_assessment_safety_protocols → safety_protocols
    - skill_assessment_safety_incidents → safety_incidents
    - skill_assessment_risk_assessments → risk_assessments
    
    Phase 2 Migration:
    - general_assessments → skill_assessment_skill_assessments
    - general_skill_assessments → AssessmentResult records
    - general_assessment_criteria → skill_assessment_assessment_criteria
    - general_assessment_history → skill_assessment_assessment_history
    - general_skill_progress → skill_progress
    
    Args:
        session: Database session
        
    Returns:
        dict: Migration results with counts
    """
    results = {
        "phase1": {
            "protocols": 0,
            "incidents": 0,
            "risk_assessments": 0
        },
        "phase2": {
            "assessments": 0,
            "results": 0,
            "criteria": 0,
            "history": 0,
            "progress": 0
        }
    }
    
    try:
        print("\n" + "=" * 60)
        print("🔄 PHASE 1 & PHASE 2 DATA MIGRATION")
        print("=" * 60)
        
        # ==================== PHASE 1 MIGRATION ====================
        print("\n📋 Phase 1: Safety Service Migration")
        print("-" * 60)
        
        # Import services
        from app.dashboard.services.safety_service import SafetyService
        
        # Create safety service and run migration
        safety_service = SafetyService(session)
        
        # Run migration (async method)
        import asyncio
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async migration
            if loop.is_running():
                # If loop is already running, use asyncio.run in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, safety_service.migrate_existing_safety_data())
                    migration_result = future.result(timeout=120)
            else:
                migration_result = loop.run_until_complete(safety_service.migrate_existing_safety_data())
            
            results["phase1"] = migration_result
            print(f"  ✅ Phase 1 Migration Complete:")
            print(f"     - Protocols migrated: {migration_result.get('protocols', 0)}")
            print(f"     - Incidents migrated: {migration_result.get('incidents', 0)}")
            print(f"     - Risk assessments migrated: {migration_result.get('risk_assessments', 0)}")
            
            # Verify migrated records exist (count total migrated records)
            try:
                migrated_protocols_count = session.execute(text("""
                    SELECT COUNT(*) FROM safety_protocols 
                    WHERE name LIKE 'Migrated:%'
                """)).scalar()
                if migrated_protocols_count > 0:
                    print(f"     ℹ️  Total migrated protocols in database: {migrated_protocols_count}")
            except:
                pass
            
        except Exception as e:
            error_msg = str(e) if e else "Unknown error"
            print(f"  ⚠️ Phase 1 migration error: {error_msg}")
            logger.warning(f"Phase 1 migration error: {error_msg}")
            import traceback
            logger.warning(traceback.format_exc())
        
        # ==================== PHASE 2 MIGRATION ====================
        print("\n📊 Phase 2: Assessment System Migration")
        print("-" * 60)
        
        # Import assessment system
        from app.services.physical_education.assessment_system import AssessmentSystem
        
        # Create assessment system instance
        assessment_system = AssessmentSystem()
        assessment_system.db = session
        
        # Run Phase 2 migration
        try:
            # Migrate existing assessments
            assessment_system._migrate_existing_assessments()
            
            # Commit migration changes to make them visible for counting
            session.commit()
            
            # Count migrated records (now that data is committed)
            from app.models.skill_assessment.assessment.assessment import (
                SkillAssessment, AssessmentResult, AssessmentHistory, SkillProgress
            )
            from app.models.assessment import GeneralAssessment
            
            # Count migrated assessments (use JSON text cast for PostgreSQL)
            migrated_assessments = session.execute(text("""
                SELECT COUNT(*) FROM skill_assessment_skill_assessments 
                WHERE assessment_metadata::text LIKE '%migrated_from%'
            """)).scalar()
            results["phase2"]["assessments"] = migrated_assessments or 0
            
            # Count migrated results (use JSON text cast for PostgreSQL)
            migrated_results = session.execute(text("""
                SELECT COUNT(*) FROM skill_assessment_assessment_results 
                WHERE evidence::text LIKE '%migrated_from%'
            """)).scalar()
            results["phase2"]["results"] = migrated_results or 0
            
            # Count migrated history (use JSON text cast for PostgreSQL)
            migrated_history = session.execute(text("""
                SELECT COUNT(*) FROM skill_assessment_assessment_history 
                WHERE new_state::text LIKE '%migrated_from%'
            """)).scalar()
            results["phase2"]["history"] = migrated_history or 0
            
            # Count migrated progress (use JSON text cast for PostgreSQL)
            migrated_progress = session.execute(text("""
                SELECT COUNT(*) FROM skill_progress 
                WHERE progress_data::text LIKE '%migrated_from%'
            """)).scalar()
            results["phase2"]["progress"] = migrated_progress or 0
            
            # Load skill benchmarks (triggers criteria migration)
            try:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, assessment_system.load_skill_benchmarks())
                        future.result(timeout=120)
                else:
                    loop.run_until_complete(assessment_system.load_skill_benchmarks())
                
                # Count total criteria (both migrated and new)
                from app.models.skill_assessment.assessment.assessment import AssessmentCriteria
                total_criteria = session.query(AssessmentCriteria).count()
                results["phase2"]["criteria"] = total_criteria
                
            except Exception as e:
                print(f"  ⚠️ Criteria migration error: {e}")
                logger.warning(f"Criteria migration error: {e}")
            
            print(f"  ✅ Phase 2 Migration Complete:")
            print(f"     - Assessments migrated: {results['phase2']['assessments']}")
            print(f"     - Results migrated: {results['phase2']['results']}")
            print(f"     - Criteria migrated: {results['phase2']['criteria']}")
            print(f"     - History migrated: {results['phase2']['history']}")
            print(f"     - Progress migrated: {results['phase2']['progress']}")
            
        except Exception as e:
            print(f"  ⚠️ Phase 2 migration error: {e}")
            logger.warning(f"Phase 2 migration error: {e}")
            import traceback
            traceback.print_exc()
        
        # Commit migration
        session.commit()
        # Note: Completion message is handled by seed_database.py in the final summary
        
        return results
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        session.rollback()
        logger.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        raise

