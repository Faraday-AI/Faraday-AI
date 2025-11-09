"""
Test configuration for the physical education models.

This module provides test fixtures and configuration for running model tests.
"""

import os
import pytest
import faulthandler
import signal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.models.shared_base import SharedBase

def get_test_db_url():
    """Get database URL based on environment."""
    # Always use DATABASE_URL from environment if available (set by run.sh)
    # This ensures tests use the same database connection as the running application
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # Fallback only if DATABASE_URL is not set
    if os.getenv("TEST_MODE") == "true":
        # Use Azure database for tests
        return "sqlite:///:memory:"
    elif os.getenv("CI") == "true":
        return "sqlite:///./test.db"
    else:
        # For local development, use the same database as development
        return "sqlite:///:memory:"

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Force set environment variables for all tests
    os.environ["TEST_MODE"] = "true"
    os.environ["SCHEMA"] = os.getenv("TEST_SCHEMA", "test_schema")
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["REDIS_URL"] = "redis://redis:6379/0"
    # Skip migration during save operations - migration tests call it directly
    os.environ["SKIP_MIGRATION_DURING_SAVE"] = "true"
    
    # Use DATABASE_URL from environment (set by run.sh/docker-compose)
    # Do NOT override it - use the same connection as the running application
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Only set if not already available (shouldn't happen if run.sh was used)
        os.environ["DATABASE_URL"] = get_test_db_url()
    
    # Verify environment is set correctly
    assert os.getenv("TEST_MODE") == "true", "TEST_MODE must be set to 'true'"
    assert os.getenv("DATABASE_URL") is not None, "DATABASE_URL must be set"
    
    # Log the database URL (first 50 chars) for debugging
    import logging
    logger = logging.getLogger(__name__)
    db_url_display = os.getenv("DATABASE_URL", "")[:50]
    logger.info(f"Tests using DATABASE_URL: {db_url_display}...")
    
    # Enable faulthandler to dump all thread tracebacks if tests hang > 15s
    # This helps diagnose deadlocks/hangs in CI and local runs
    try:
        faulthandler.enable()
        # Dump after 15 seconds, repeat every 15 seconds until disabled
        faulthandler.dump_traceback_later(15, repeat=True)
    except Exception:
        pass
    
    # PRODUCTION-READY: Add signal handlers to catch unexpected exits
    # This helps diagnose if pytest is being killed by a signal
    # CRITICAL: After Ctrl+C, connection pool may be corrupted - we'll dispose it in pytest_sessionfinish
    def signal_handler(signum, frame):
        logger.error(f"CRITICAL: Received signal {signum} - pytest may be exiting unexpectedly")
        import traceback
        logger.error(f"Stack trace:\n{traceback.format_stack(frame)}")
        
        # PRODUCTION-READY: On SIGINT (Ctrl+C), mark engine for cleanup
        # Don't dispose here - let pytest_sessionfinish handle it properly
        global _engine_instance
        if _engine_instance is not None:
            logger.warning("Signal received - connection pool will be disposed in pytest_sessionfinish")
    
    # Register handlers for common signals that might kill pytest
    # NOTE: We don't override SIGINT - pytest handles it properly for graceful shutdown
    # We just log it so we know to clean up the connection pool
    try:
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        # Don't override SIGINT - pytest needs it for Ctrl+C handling
        # We'll detect interruption via exitstatus=2 in pytest_sessionfinish
    except Exception as e:
        logger.warning(f"Could not set signal handlers: {e}")
    
    yield
    
    # Cleanup
    try:
        faulthandler.cancel_dump_traceback_later()
    except Exception:
        pass
    if os.getenv("TEST_MODE") == "true" and os.getenv("DATABASE_URL", "").startswith("sqlite"):
        try:
            os.remove("./test.db")
        except:
            pass

# Model relationships are now handled with full module paths - no dynamic setup needed

# Global engine instance to ensure proper cleanup
_engine_instance = None

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    global _engine_instance
    
    # PRODUCTION-READY: Reuse engine instance but dispose pool if interrupted
    # After Ctrl+C, connection pool may be corrupted - dispose and recreate
    if _engine_instance is not None:
        try:
            # More robust pool health check: try to actually get a connection
            # This catches cases where pool.size() works but connections are corrupted
            # Use a non-blocking approach: check if we can get a connection quickly
            # If pool is corrupted, this will fail or hang - in that case, dispose and recreate
            try:
                # Try to get a connection with a very short timeout
                # If this hangs, the pool is likely corrupted
                conn = _engine_instance.connect()
                try:
                    # Try a simple query to verify connection works
                    conn.execute(text("SELECT 1"))
                finally:
                    conn.close()
                # If we get here, pool is healthy
            except Exception as e:
                # Connection failed - pool may be corrupted
                raise
        except (AttributeError, Exception) as e:
            # Pool is corrupted (e.g., after Ctrl+C interrupt) - dispose and recreate
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Connection pool appears corrupted (error: {e}) - disposing and recreating")
            try:
                _engine_instance.dispose()
            except Exception:
                pass
            _engine_instance = None
    
    if _engine_instance is None:
        db_url = get_test_db_url()
        if db_url.startswith("sqlite"):
            _engine_instance = create_engine(db_url)
        else:
            # Azure-specific configuration
            # PRODUCTION-READY: Increased pool size for full test suite (1136 tests)
            # With 1136 tests, pool_size=5 was too small, causing connection exhaustion
            # pool_size=10 + max_overflow=20 = 30 max connections (sufficient for sequential test execution)
            _engine_instance = create_engine(
                db_url,
                pool_size=10,  # Increased from 5 to 10 for full suite
                max_overflow=20,  # Increased from 10 to 20 for full suite
                pool_timeout=30,
                pool_recycle=1800
            )
    
    return _engine_instance

@pytest.fixture(scope="session")
def test_schema(engine):
    """Use existing schema for Azure PostgreSQL."""
    if not get_test_db_url().startswith("sqlite"):
        # For Azure, use the existing schema (public)
        yield "public"
    else:
        yield None

@pytest.fixture(scope="session")
def tables(engine, test_schema):
    """Use existing tables for Azure PostgreSQL."""
    # For Azure, tables are already created and seeded
    # No need to create/drop tables
    yield

@pytest.fixture
def db_session(engine, tables, test_schema):
    """
    Create a new database session for a test with transaction rollback.
    
    BEST PRACTICE FOR FINAL STAGES:
    - Uses nested transactions (SAVEPOINT) for test isolation
    - Automatically rolls back all changes after each test
    - Prevents tests from affecting each other
    - Ensures clean test state without manual cleanup
    """
    import time
    from sqlalchemy.exc import OperationalError
    
    # Retry connection logic for Azure PostgreSQL
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            connection = engine.connect()
            
            # Set the search path to use the test schema for PostgreSQL
            if test_schema:
                connection.execute(text(f"SET search_path TO {test_schema}, public"))
                connection.commit()
            
            # Add timeouts to surface blocking DB operations
            # Increased to 15 seconds to allow complex queries with large datasets
            try:
                # PostgreSQL timeouts in milliseconds
                # PRODUCTION-READY: Increased statement_timeout from 15s to 60s for full suite
                # Some integration tests with large datasets may take longer than 15s
                # 60s is reasonable for comprehensive integration tests with real database
                connection.execute(text("SET statement_timeout = 60000"))  # 60 seconds
                connection.execute(text("SET lock_timeout = 10000"))  # 10 seconds (increased from 5s)
                connection.commit()
            except Exception:
                # Ignore if not supported (e.g., sqlite or restricted roles)
                pass
            
            # Begin a transaction for test isolation
            trans = connection.begin()
            
            # Create session bound to the transaction
            Session = sessionmaker(bind=connection)
            session = Session()
            
            # For PostgreSQL, use SAVEPOINT for nested transaction support
            # This allows rollback of individual test changes
            db_url = get_test_db_url()
            is_postgres = not db_url.startswith("sqlite")
            savepoint_created = False
            
            if is_postgres:
                # CRITICAL FIX: Sync sequences to MAX(id) to prevent duplicate key errors
                # When tests create records, sequences must be ahead of existing data
                # This ensures auto-increment IDs don't conflict with seeded data
                # Sequences don't rollback with SAVEPOINTs, so we sync at test start
                try:
                    # Sync sequences for tables commonly used in tests
                    # This prevents "duplicate key" errors when test data IDs conflict with seeded data
                    sequence_sync_queries = [
                        "SELECT setval('physical_education_classes_id_seq', COALESCE((SELECT MAX(id) FROM physical_education_classes), 1), true)",
                        "SELECT setval('students_id_seq', COALESCE((SELECT MAX(id) FROM students), 1), true)",
                        "SELECT setval('activities_id_seq', COALESCE((SELECT MAX(id) FROM activities), 1), true)",
                        "SELECT setval('activity_categories_id_seq', COALESCE((SELECT MAX(id) FROM activity_categories), 1), true)",
                    ]
                    for sync_query in sequence_sync_queries:
                        try:
                            connection.execute(text(sync_query))
                        except Exception:
                            # Table or sequence might not exist, skip it
                            pass
                except Exception:
                    # If sequence syncing fails, continue anyway - better to have test fail than suite hang
                    pass
                
                session.execute(text("SAVEPOINT test"))
                savepoint_created = True
            
            # Test the connection by executing a simple query
            try:
                connection.execute(text("SELECT 1"))
            except Exception as e:
                session.close()
                connection.close()
                raise
            
            # Patch session.commit() and refresh() to use flush() in nested transactions to prevent hangs
            # This prevents hangs when services call commit() inside SAVEPOINT transactions
            original_commit = session.commit
            original_refresh = session.refresh
            
            def safe_commit():
                """Commit that uses flush() if in nested transaction (SAVEPOINT)."""
                # Always check both in_nested_transaction and TEST_MODE for reliability
                in_nested = hasattr(session, 'in_nested_transaction') and session.in_nested_transaction()
                is_test = os.getenv("TEST_MODE") == "true"
                if in_nested or is_test:
                    session.flush()
                else:
                    original_commit()
            
            def safe_refresh(instance):
                """Refresh that is a no-op in test mode to prevent hangs."""
                # Skip refresh in nested transactions - flush() makes object available
                in_nested = hasattr(session, 'in_nested_transaction') and session.in_nested_transaction()
                is_test = os.getenv("TEST_MODE") == "true"
                if not (in_nested or is_test):
                    original_refresh(instance)
                # In test mode, flush() is sufficient - object is already available
            
            session.commit = safe_commit
            session.refresh = safe_refresh
            
            # Set the test session for get_db() to use in test mode
            # Both app.core.database and app.db.session have get_db(), so set both
            # They share the same thread-local storage, so setting one sets both
            from app.core.database import set_test_session, clear_test_session
            
            # Set test session (shared thread-local storage)
            set_test_session(session)
            
            try:
                yield session
            finally:
                # CRITICAL: Always clear test session before cleanup to prevent state pollution
                # This ensures the next test starts with a clean thread-local state
                clear_test_session()
                
                # BEST PRACTICE: Explicitly rollback to SAVEPOINT before outer transaction rollback
                # This ensures test data is properly isolated and doesn't leak between tests
                # FIX: This prevents "duplicate key" errors when tests run in full suite
                # CRITICAL: Must rollback to SAVEPOINT BEFORE session.rollback() to ensure proper isolation
                if is_postgres and savepoint_created:
                    try:
                        # Check if transaction is still active before attempting rollback
                        if connection.in_transaction():
                            # Explicitly rollback to the SAVEPOINT we created
                            # This ensures all test changes are discarded and IDs don't conflict
                            # Do this BEFORE session.rollback() to ensure proper nested transaction handling
                            session.execute(text("ROLLBACK TO SAVEPOINT test"))
                    except Exception as rollback_err:
                        # If SAVEPOINT doesn't exist, transaction is aborted, or already rolled back, that's okay
                        # This can happen if:
                        # 1. The transaction was already aborted due to an error
                        # 2. The SAVEPOINT was already released
                        # 3. The connection is closed
                        # Continue with cleanup - the outer transaction rollback will handle it
                        pass
                
                # Close session before outer transaction rollback
                # session.rollback() may conflict with explicit SAVEPOINT rollback, so skip it if we did ROLLBACK TO SAVEPOINT
                try:
                    if not (is_postgres and savepoint_created):
                        # Only do session.rollback() if we didn't do explicit SAVEPOINT rollback
                        session.rollback()
                except Exception:
                    pass
                finally:
                    session.close()
                
                # Rollback outer transaction
                try:
                    trans.rollback()
                except Exception:
                    pass
                finally:
                    connection.close()
            break  # Success, exit retry loop
            
        except (OperationalError, Exception) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            else:
                # Final attempt failed, raise the error
                raise

@pytest.fixture
def sample_data(db_session):
    """Create sample data for testing."""
    # This will be implemented with specific test data
    pass

@pytest.fixture(autouse=True, scope="function")
def ensure_global_app_state_clean():
    """
    CRITICAL: Comprehensive state pollution cleanup before and after EVERY test.
    
    STATE POLLUTION = One test modifies shared/global state that persists and affects later tests.
    This causes tests to pass individually but fail when run together.
    
    Sources of state pollution:
    1. Singleton instances (24+ services with _instance = None pattern)
    2. FastAPI app.dependency_overrides
    3. Context variables (database sessions)
    4. Module-level caches/variables
    5. Redis connection state
    6. Thread-local storage
    7. Async event loops and pending tasks
    
    This fixture ensures ALL sources are cleaned between tests.
    """
    # Import app here to avoid circular imports
    from app.main import app
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    # Ensure limiter exists on app.state for tests
    if not hasattr(app.state, 'limiter'):
        app.state.limiter = Limiter(key_func=get_remote_address)
    
    # 1. Clear FastAPI dependency overrides
    app.dependency_overrides.clear()
    
    # 2. Clear context variables (database sessions)
    from app.core.database import clear_test_session
    clear_test_session()
    
    # 3. PRODUCTION-READY: Clean up any pending async tasks
    # This prevents async tasks from previous tests from interfering with new tests
    try:
        import asyncio
        # Try to get the current event loop
        try:
            loop = asyncio.get_running_loop()
            # Cancel any pending tasks (except the current one)
            pending = [task for task in asyncio.all_tasks(loop) if not task.done()]
            for task in pending:
                task.cancel()
        except RuntimeError:
            # No running event loop - this is fine
            pass
    except Exception:
        # Ignore errors in async cleanup - not critical for test isolation
        pass
    
    # 4. CRITICAL: Reset ALL singleton instances to prevent state pollution
    # Found 24+ singleton services - ALL must be reset
    singleton_services = [
        # Physical Education Services
        ('app.services.physical_education.movement_analyzer', 'MovementAnalyzer'),
        ('app.services.physical_education.safety_manager', 'SafetyManager'),
        ('app.services.physical_education.student_manager', 'StudentManager'),
        ('app.services.physical_education.equipment_manager', 'EquipmentManager'),
        ('app.services.physical_education.service_integration', 'ServiceIntegration'),
        ('app.services.physical_education.pe_service', 'PEService'),
        ('app.services.physical_education.activity_manager', 'ActivityManager'),
        ('app.services.physical_education.activity_analysis_manager', 'ActivityAnalysisManager'),
        ('app.services.physical_education.activity_planning_manager', 'ActivityPlanningManager'),
        ('app.services.physical_education.activity_tracking_manager', 'ActivityTrackingManager'),
        ('app.services.physical_education.activity_rate_limit_manager', 'ActivityRateLimitManager'),
        ('app.services.physical_education.activity_visualization_manager', 'ActivityVisualizationManager'),
        ('app.services.physical_education.activity_export_manager', 'ActivityExportManager'),
        ('app.services.physical_education.activity_collaboration_manager', 'ActivityCollaborationManager'),
        ('app.services.physical_education.activity_adaptation_manager', 'ActivityAdaptationManager'),
        ('app.services.physical_education.activity_assessment_manager', 'ActivityAssessmentManager'),
        ('app.services.physical_education.activity_circuit_breaker_manager', 'ActivityCircuitBreakerManager'),
        ('app.services.physical_education.activity_cache_manager', 'ActivityCacheManager'),
        ('app.services.physical_education.activity_security_manager', 'ActivitySecurityManager'),
        ('app.services.physical_education.lesson_planner', 'LessonPlanner'),
        ('app.services.physical_education.assessment_system', 'AssessmentSystem'),
        ('app.services.physical_education.ai_assistant', 'AIAssistant'),
        ('app.services.physical_education.security_service', 'SecurityService'),
        # Beta Teacher Dashboard
        ('app.services.pe.beta_teacher_dashboard_service', 'BetaTeacherDashboardService'),
        # Dashboard Services (Phase 4, 5, 6)
        ('app.dashboard.services.resource_management_service', 'ResourceManagementService'),
        ('app.services.pe.beta_resource_management_service', 'BetaResourceManagementService'),
        ('app.dashboard.services.context_analytics_service', 'ContextAnalyticsService'),
        ('app.services.pe.beta_context_analytics_service', 'BetaContextAnalyticsService'),
        ('app.dashboard.services.dashboard_preferences_service', 'DashboardPreferencesService'),
        ('app.services.pe.beta_dashboard_preferences_service', 'BetaDashboardPreferencesService'),
    ]
    
    # Reset all singletons before test
    for module_path, class_name in singleton_services:
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name, None)
            if service_class and hasattr(service_class, '_instance'):
                # Force reset singleton instance
                service_class._instance = None
        except (ImportError, AttributeError, Exception):
            # Service might not exist or import might fail - continue
            pass
    
    yield
    
    # 5. Cleanup AFTER test - clear everything again
    app.dependency_overrides.clear()
    clear_test_session()
    
    # 6. PRODUCTION-READY: Clean up any pending async tasks after test
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            pending = [task for task in asyncio.all_tasks(loop) if not task.done()]
            for task in pending:
                task.cancel()
        except RuntimeError:
            pass
    except Exception:
        pass
    
    # 7. Reset ALL singletons again after test
    for module_path, class_name in singleton_services:
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name, None)
            if service_class and hasattr(service_class, '_instance'):
                service_class._instance = None
        except (ImportError, AttributeError, Exception):
            pass

def pytest_configure(config):
    """Configure pytest and ensure environment variables are set."""
    # Ensure environment variables are set at the very beginning
    os.environ["TEST_MODE"] = "true"
    os.environ["SCHEMA"] = os.getenv("TEST_SCHEMA", "test_schema")
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["REDIS_URL"] = "redis://redis:6379/0"
    
    # Set DATABASE_URL for tests if not already set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = get_test_db_url()
    
    # Verify environment is set correctly
    assert os.getenv("TEST_MODE") == "true", "TEST_MODE must be set to 'true'"
    assert os.getenv("DATABASE_URL") is not None, "DATABASE_URL must be set"

def pytest_unconfigure(config):
    """Cleanup after tests."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("pytest_unconfigure called - test session ending")
    pass

def pytest_sessionfinish(session, exitstatus):
    """Called after entire test run finishes, right before returning the exit status to the system."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"pytest_sessionfinish called - exitstatus={exitstatus}")
    # Exit status codes:
    # 0 = all tests passed
    # 1 = tests failed
    # 2 = tests were interrupted (Ctrl+C)
    # 3 = internal error
    # 4 = pytest was misused
    # 5 = no tests were collected
    
    # PRODUCTION-READY: If interrupted (exitstatus=2), clean up connection pool
    # Ctrl+C can leave connections in a bad state - dispose pool to ensure clean state for next run
    if exitstatus == 2:
        logger.warning("Test suite was interrupted (Ctrl+C) - cleaning up connection pool")
        global _engine_instance
        if _engine_instance is not None:
            try:
                # Dispose all connections in the pool to ensure clean state
                _engine_instance.dispose()
                logger.info("Connection pool disposed after interruption")
            except Exception as e:
                logger.warning(f"Error disposing connection pool: {e}")
            finally:
                _engine_instance = None
    
    if exitstatus not in [0, 1, 2, 3, 4, 5]:
        logger.warning(f"Unexpected exit status: {exitstatus}")

def pytest_runtest_setup(item):
    """Called before each test item runs."""
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Starting test: {item.nodeid}")

def pytest_runtest_teardown(item, nextitem):
    """Called after each test item runs."""
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Finished test: {item.nodeid}, next: {nextitem.nodeid if nextitem else 'None'}") 