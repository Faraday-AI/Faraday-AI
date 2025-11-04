import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from app.services.physical_education.movement_analyzer import MovementAnalyzer
from app.models.physical_education.movement_analysis.movement_models import MovementModels
from app.models.physical_education.skill_assessment.skill_assessment_models import SkillModels

# Note: Singleton reset is handled by global autouse fixture in conftest.py
# No need for module-level reset - ensure_global_app_state_clean handles it

@pytest.fixture
async def initialized_movement_analyzer(db_session):
    """
    Create and initialize MovementAnalyzer instance for testing with real Azure DB.
    
    Best practice: Reset singleton instance before creating new analyzer to ensure clean state.
    Uses real Azure PostgreSQL via db_session fixture.
    
    CRITICAL: Handle cleanup errors gracefully to prevent hangs in full suite.
    If cleanup hangs, force reset singleton to ensure next test starts clean.
    
    PRODUCTION-READY: Uses timeout wrapper AND mocks MediaPipe to prevent indefinite hangs.
    MediaPipe initialization can hang synchronously in full suite due to resource contention.
    """
    # Singleton reset is handled by global autouse fixture (ensure_global_app_state_clean)
    # This ensures clean state even if previous tests polluted the singleton
    
    # CRITICAL: Create analyzer AFTER ensuring TEST_MODE is set
    # This prevents any MediaPipe imports during MovementAnalyzer.__init__
    import os
    os.environ["TEST_MODE"] = "true"
    analyzer = MovementAnalyzer()
    
    # PRODUCTION-READY: MovementAnalyzer._load_movement_models() now checks TEST_MODE
    # and automatically uses mock MediaPipe in test mode. No manual mocking needed.
    # This ensures:
    # 1. Tests run fast without MediaPipe hangs
    # 2. Production code uses real MediaPipe
    # 3. Graceful fallback if MediaPipe fails in production
    
    # CRITICAL: Wrap initialization in timeout to prevent indefinite hangs
    # Even with MediaPipe mocked (via TEST_MODE), synchronous operations might block
    # Use threading timeout for synchronous blocking, then asyncio timeout for async
    import asyncio
    import concurrent.futures
    import threading
    import logging
    import signal
    logger = logging.getLogger("test_movement_analyzer")
    
    # Set up a timeout signal as backup (Unix only)
    def timeout_handler(signum, frame):
        logger.error("CRITICAL: Signal timeout during initialization - forcing exit")
        raise TimeoutError("Initialization timed out (signal)")
    
    # Run initialization in a separate thread to handle synchronous blocks
    # This prevents the entire event loop from being blocked by sync operations
    init_done = threading.Event()
    init_error = []
    
    def run_init():
        """Run initialization in a thread to prevent blocking the event loop."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(analyzer.initialize(db_session=db_session))
                init_done.set()
                return result
            finally:
                loop.close()
        except Exception as e:
            init_error.append(e)
            init_done.set()
            raise
    
    try:
        # Set signal timeout as backup (15 seconds)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)
        
        # Use ThreadPoolExecutor with timeout to catch synchronous blocks
        # This will timeout even if a sync operation blocks
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_init)
            # 10 second timeout - should complete in <1 second with mocks
            result = future.result(timeout=10.0)
            logger.info("MovementAnalyzer initialized successfully")
            
        # Cancel signal timeout
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
            
    except concurrent.futures.TimeoutError:
        # CRITICAL: Timeout occurred - log and fail fast
        logger.error("CRITICAL: MovementAnalyzer initialization timed out after 10 seconds")
        logger.error("This indicates a blocking synchronous operation that needs investigation")
        # Cancel signal timeout
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        # Global cleanup fixture will reset singleton - no need to do it here
        raise TimeoutError("MovementAnalyzer initialization timed out after 10 seconds - check for blocking operations")
    except Exception as e:
        # Cancel signal timeout
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        # Check if error was captured in thread
        if init_error:
            raise init_error[0]
        # Any other exception during initialization - log and re-raise
        logger.error(f"Error during MovementAnalyzer initialization: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    
    try:
        yield analyzer
    finally:
        # Cleanup with error handling to prevent hangs
        # If cleanup hangs, we'll just reset singleton and continue
        try:
            # Also timeout cleanup to prevent hangs
            import asyncio
            await asyncio.wait_for(analyzer.cleanup(), timeout=5.0)
        except (asyncio.TimeoutError, Exception) as e:
            # Log but don't fail - singleton reset is more important
            import logging
            logger = logging.getLogger("test_movement_analyzer")
            logger.warning(f"Cleanup failed or timed out (non-fatal): {e}")
        finally:
            # Global autouse fixture (ensure_global_app_state_clean) handles singleton reset
            # No need to reset here - global cleanup ensures clean state for next test
            pass

@pytest.fixture
def movement_analyzer():
    """
    Create MovementAnalyzer instance for testing.
    
    Best practice: Reset singleton instance to ensure clean state.
    """
    # Reset singleton instance to ensure clean state between tests
    original_instance = MovementAnalyzer._instance
    MovementAnalyzer._instance = None
    
    analyzer = MovementAnalyzer()
    
    yield analyzer
    
    # Restore original instance to avoid affecting other tests
    MovementAnalyzer._instance = original_instance

@pytest.fixture
def mock_movement_models():
    """Create a mock MovementModels."""
    return MagicMock(spec=MovementModels)

@pytest.fixture
def mock_skill_models():
    """Create a mock SkillModels."""
    return MagicMock(spec=SkillModels)

@pytest.fixture
def sample_processed_video():
    """Create sample processed video data."""
    return {
        "frames": [np.zeros((1080, 1920, 3)) for _ in range(10)],
        "key_points": [{"x": 0, "y": 0} for _ in range(10)],
        "motion_vectors": [{"dx": 0, "dy": 0} for _ in range(10)],
        "quality_metrics": {"brightness": 0.5, "contrast": 0.5, "sharpness": 0.5}
    }

@pytest.fixture
def sample_movement_patterns():
    """Create sample movement patterns."""
    return [
        {
            "type": "throwing",
            "key_points": [{"x": 0, "y": 0}],
            "motion_vectors": [{"dx": 0, "dy": 0}],
            "timestamps": [0.0]
        }
    ]

@pytest.fixture
def mock_movement_pattern():
    return {
        "key_points": {
            "shoulder": [0.5, 0.5],
            "elbow": [0.6, 0.6],
            "wrist": [0.7, 0.7]
        },
        "features": {
            "angle": 45.0,
            "velocity": 2.0,
            "acceleration": 1.0
        },
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def mock_movement_history():
    return [
        {
            "pattern": {
                "key_points": {"shoulder": [0.5, 0.5]},
                "features": {"angle": 45.0}
            },
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "pattern": {
                "key_points": {"shoulder": [0.6, 0.6]},
                "features": {"angle": 50.0}
            },
            "timestamp": datetime.now().isoformat()
        }
    ]

@pytest.mark.asyncio
async def test_initialization(initialized_movement_analyzer):
    """
    Test initialization of MovementAnalyzer.
    
    PRODUCTION-READY: This test verifies MovementAnalyzer initializes correctly.
    Timeout protection is handled in the fixture via ThreadPoolExecutor with 10s timeout.
    In test mode, MediaPipe is automatically skipped to prevent hangs.
    """
    # Verify initialization completed successfully (fixture handles timeout)
    # If we reach here, initialization completed within timeout
    assert initialized_movement_analyzer.movement_models is not None, "Movement models not initialized"
    assert initialized_movement_analyzer.skill_models is not None, "Skill models not initialized"
    assert initialized_movement_analyzer.analysis_history == []
    assert isinstance(initialized_movement_analyzer.performance_benchmarks, dict)
    assert isinstance(initialized_movement_analyzer.injury_risk_factors, dict)
    
    # Verify models are correct type (will be mock instances in TEST_MODE)
    # This is production-ready: gracefully handles MediaPipe initialization failures
    assert hasattr(initialized_movement_analyzer.movement_models, 'extract_patterns'), "MovementModels missing extract_patterns method"
    assert hasattr(initialized_movement_analyzer.skill_models, 'cleanup'), "SkillModels missing cleanup method"

@pytest.mark.asyncio
async def test_cleanup(movement_analyzer, db_session):
    """Test cleanup of MovementAnalyzer with real Azure DB."""
    mock_movement_models = AsyncMock(spec=MovementModels)
    mock_skill_models = AsyncMock(spec=SkillModels)
    
    # Ensure the mock objects have the cleanup method
    mock_movement_models.cleanup = AsyncMock()
    mock_skill_models.cleanup = AsyncMock()
    
    # Patch the _load methods to return our mocks
    with patch.object(movement_analyzer, '_load_movement_models', return_value=mock_movement_models), \
         patch.object(movement_analyzer, '_load_skill_models', return_value=mock_skill_models):

        # Use real db_session instead of get_db()
        await movement_analyzer.initialize(db_session=db_session)
        await movement_analyzer.cleanup()

        mock_movement_models.cleanup.assert_called_once()
        mock_skill_models.cleanup.assert_called_once()
        assert movement_analyzer.analysis_history == []
        assert movement_analyzer.analysis_cache == {}

@pytest.mark.asyncio
async def test_analyze(movement_analyzer, sample_processed_video):
    """Test movement analysis."""
    with patch.object(movement_analyzer, 'extract_movement_patterns', return_value=[{"pattern": "test"}]), \
         patch.object(movement_analyzer, 'analyze_movement_patterns', return_value={"analysis": "results"}):
        
        result = await movement_analyzer.analyze(sample_processed_video)
        
        assert "analysis" in result
        assert result["analysis"] == "results"
        assert movement_analyzer.total_analyses > 0

@pytest.mark.asyncio
async def test_extract_movement_patterns(movement_analyzer, sample_processed_video):
    """Test extracting movement patterns."""
    patterns = await movement_analyzer.extract_movement_patterns(sample_processed_video)
    
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    assert all("key_points" in pattern for pattern in patterns)

@pytest.mark.asyncio
async def test_analyze_movement_patterns(movement_analyzer, sample_movement_patterns):
    """Test analyzing movement patterns."""
    with patch.object(movement_analyzer, 'analyze_patterns_batch', return_value=[{"analysis": "results"}]):
        result = await movement_analyzer.analyze_movement_patterns(sample_movement_patterns)
        
        assert "analysis" in result
        assert result["analysis"] == "results"

@pytest.mark.asyncio
async def test_analyze_patterns_batch(movement_analyzer, sample_movement_patterns):
    """Test batch analysis of movement patterns."""
    with patch.object(movement_analyzer, 'analyze_single_pattern', return_value={"analysis": "results"}):
        results = await movement_analyzer.analyze_patterns_batch(sample_movement_patterns)
        
        assert len(results) == len(sample_movement_patterns)
        assert all("analysis" in result for result in results)

@pytest.mark.asyncio
async def test_analyze_single_pattern(movement_analyzer):
    """Test analyzing a single movement pattern."""
    pattern = {
        "type": "throwing",
        "key_points": [{"x": 0, "y": 0}],
        "motion_vectors": [{"dx": 0, "dy": 0}],
        "timestamps": [0.0]
    }
    
    with patch.object(movement_analyzer, 'analyze_posture_realtime', return_value={"posture": "good"}), \
         patch.object(movement_analyzer, 'analyze_form_realtime', return_value={"form": "good"}), \
         patch.object(movement_analyzer, 'analyze_alignment_realtime', return_value={"alignment": "good"}), \
         patch.object(movement_analyzer, 'analyze_joint_stress_realtime', return_value={"stress": "low"}), \
         patch.object(movement_analyzer, 'analyze_balance_realtime', return_value={"balance": "good"}):
        
        result = await movement_analyzer.analyze_single_pattern(pattern)
        
        assert "posture" in result
        assert "form" in result
        assert "alignment" in result
        assert "stress" in result
        assert "balance" in result

@pytest.mark.asyncio
async def test_manage_analysis_cache(movement_analyzer):
    """Test managing analysis cache."""
    movement_analyzer.analysis_cache["test"] = {"data": "test", "timestamp": datetime.now()}
    await movement_analyzer.manage_analysis_cache()
    
    assert "test" in movement_analyzer.analysis_cache
    assert movement_analyzer.cache_stats["hits"] >= 0

@pytest.mark.asyncio
async def test_manage_batch_cache(movement_analyzer):
    """Test managing batch cache."""
    movement_analyzer.batch_cache["test"] = {"data": "test", "timestamp": datetime.now()}
    await movement_analyzer.manage_batch_cache()
    
    assert "test" in movement_analyzer.batch_cache
    assert movement_analyzer.cache_stats["hits"] >= 0

def test_get_cache_stats(movement_analyzer):
    """Test getting cache statistics."""
    stats = movement_analyzer.get_cache_stats()
    
    assert "hits" in stats
    assert "misses" in stats
    assert "evictions" in stats

def test_optimize_memory_usage(movement_analyzer):
    """Test optimizing memory usage."""
    movement_analyzer.analysis_cache["test"] = {"data": "test", "timestamp": datetime.now()}
    movement_analyzer.batch_cache["test"] = {"data": "test", "timestamp": datetime.now()}
    
    movement_analyzer.optimize_memory_usage()
    
    assert movement_analyzer.analysis_cache == {}
    assert movement_analyzer.batch_cache == {}

def test_get_performance_report(movement_analyzer):
    """Test getting performance report."""
    report = movement_analyzer.get_performance_report()
    
    assert "processing_times" in report
    assert "memory_usage" in report
    assert "cache_efficiency" in report

def test_clear_caches(movement_analyzer):
    """Test clearing caches."""
    movement_analyzer.analysis_cache["test"] = {"data": "test"}
    movement_analyzer.batch_cache["test"] = {"data": "test"}
    
    movement_analyzer.clear_caches()
    
    assert movement_analyzer.analysis_cache == {}
    assert movement_analyzer.batch_cache == {}

def test_initialize_adaptive_learning(movement_analyzer):
    """Test initializing adaptive learning."""
    movement_analyzer.initialize_adaptive_learning()
    
    assert "pattern_recognition" in movement_analyzer.adaptive_learning
    assert "performance_trends" in movement_analyzer.adaptive_learning
    assert "error_recovery" in movement_analyzer.adaptive_learning

def test_initialize_real_time_monitoring(movement_analyzer):
    """Test initializing real-time monitoring."""
    movement_analyzer.initialize_real_time_monitoring()
    
    assert "active_sessions" in movement_analyzer.real_time_monitoring
    assert "resource_usage" in movement_analyzer.real_time_monitoring
    assert "error_rates" in movement_analyzer.real_time_monitoring

@pytest.mark.asyncio
async def test_analyze_movement_patterns_ml(initialized_movement_analyzer, mock_movement_pattern):
    """Test ML-based movement pattern analysis."""
    patterns = [mock_movement_pattern]

    with patch.object(initialized_movement_analyzer.movement_models, 'identify_patterns', new_callable=AsyncMock) as mock_identify:
        mock_identify.return_value = {"pattern_type": "throwing"}

        result = await initialized_movement_analyzer.analyze_movement_patterns_ml(patterns)

        assert "pattern_recognition" in result
        assert "temporal_analysis" in result
        assert "biomechanical_analysis" in result

@pytest.mark.asyncio
async def test_generate_realtime_feedback(initialized_movement_analyzer, mock_movement_pattern):
    """Test real-time feedback generation."""
    result = await initialized_movement_analyzer.generate_realtime_feedback(mock_movement_pattern)

    assert "immediate_corrections" in result
    assert "safety_alerts" in result
    assert "performance_optimization" in result

@pytest.mark.asyncio
async def test_predict_injury_risk_ml(initialized_movement_analyzer, mock_movement_history):
    """Test ML-based injury risk prediction."""
    result = await initialized_movement_analyzer.predict_injury_risk_ml(mock_movement_history)

    assert "risk_assessment" in result
    assert "preventive_recommendations" in result
    assert "risk_factors" in result

@pytest.mark.asyncio
async def test_analyze_biomechanics(initialized_movement_analyzer, mock_movement_pattern):
    """Test biomechanical analysis."""
    patterns = [mock_movement_pattern]
    result = await initialized_movement_analyzer.analyze_biomechanics(patterns)

    assert isinstance(result, dict)
    assert "joint_angles" in result
    assert "force_analysis" in result

@pytest.mark.asyncio
async def test_analyze_energy_efficiency(initialized_movement_analyzer, mock_movement_pattern):
    """Test energy efficiency analysis."""
    patterns = [mock_movement_pattern]
    result = await initialized_movement_analyzer.analyze_energy_efficiency(patterns)

    assert isinstance(result, dict)
    assert "efficiency_score" in result
    assert "energy_expenditure" in result

@pytest.mark.asyncio
async def test_analyze_symmetry(initialized_movement_analyzer, mock_movement_pattern):
    """Test movement symmetry analysis."""
    patterns = [mock_movement_pattern]
    result = await initialized_movement_analyzer.analyze_symmetry(patterns)

    assert isinstance(result, dict)
    assert "symmetry_score" in result
    assert "imbalances" in result

@pytest.mark.asyncio
async def test_assess_skill_level(initialized_movement_analyzer, mock_movement_pattern):
    """Test skill level assessment."""
    patterns = [mock_movement_pattern]
    result = await initialized_movement_analyzer.assess_skill_level(patterns)

    assert isinstance(result, dict)
    assert "skill_level" in result
    assert "proficiency_metrics" in result

@pytest.mark.asyncio
async def test_analyze_recovery(initialized_movement_analyzer, mock_movement_pattern):
    """Test recovery analysis."""
    result = await initialized_movement_analyzer.analyze_recovery({"patterns": [mock_movement_pattern]})

    assert isinstance(result, dict)
    assert "fatigue_level" in result
    assert "recovery_recommendations" in result

@pytest.mark.asyncio
async def test_analyze_adaptation(initialized_movement_analyzer, mock_movement_pattern):
    """Test adaptation analysis."""
    result = await initialized_movement_analyzer.analyze_adaptation({"patterns": [mock_movement_pattern]})

    assert isinstance(result, dict)
    assert "adaptation_level" in result
    assert "training_recommendations" in result

@pytest.mark.asyncio
async def test_predict_performance(initialized_movement_analyzer, mock_movement_pattern):
    """Test performance prediction."""
    result = await initialized_movement_analyzer.predict_performance({"patterns": [mock_movement_pattern]})

    assert isinstance(result, dict)
    assert "performance_prediction" in result
    assert "confidence_score" in result

@pytest.mark.asyncio
async def test_environmental_analysis(initialized_movement_analyzer, mock_movement_pattern):
    """Test environmental factor analysis."""
    patterns = [mock_movement_pattern]
    result = await initialized_movement_analyzer.analyze_environmental_factors(patterns)

    assert isinstance(result, dict)
    assert "environmental_impact" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_equipment_analysis(initialized_movement_analyzer, mock_movement_pattern):
    """Test equipment usage analysis."""
    patterns = [mock_movement_pattern]
    result = await initialized_movement_analyzer.analyze_equipment_usage(patterns)

    assert isinstance(result, dict)
    assert "equipment_recommendations" in result
    assert "safety_guidelines" in result

@pytest.mark.asyncio
async def test_comprehensive_feedback(initialized_movement_analyzer, mock_movement_pattern):
    """Test comprehensive feedback generation."""
    analysis = {"patterns": [mock_movement_pattern]}
    metrics = {"performance_score": 0.8}
    result = await initialized_movement_analyzer.generate_comprehensive_feedback(analysis, metrics)

    assert isinstance(result, dict)
    assert "technical_feedback" in result
    assert "performance_feedback" in result
    assert "safety_feedback" in result

@pytest.mark.asyncio
async def test_error_handling(initialized_movement_analyzer):
    """Test error handling functionality."""
    with pytest.raises(Exception):
        await initialized_movement_analyzer.analyze_movement_patterns_ml(None)

    with pytest.raises(Exception):
        await initialized_movement_analyzer.generate_realtime_feedback(None)

@pytest.mark.asyncio
async def test_performance_tracking(initialized_movement_analyzer, mock_movement_history):
    """Test performance tracking functionality."""
    result = await initialized_movement_analyzer.track_progress(
        {"patterns": [mock_movement_history[0]["pattern"]]},
        {"performance_score": 0.8}
    )

    assert isinstance(result, dict)
    assert "progress_metrics" in result
    assert "improvement_areas" in result 