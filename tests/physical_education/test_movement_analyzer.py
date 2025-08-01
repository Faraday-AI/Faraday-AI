import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from app.services.physical_education.movement_analyzer import MovementAnalyzer
from app.models.physical_education.movement_analysis.movement_models import MovementModels
from app.models.physical_education.skill_assessment.skill_assessment_models import SkillModels

@pytest.fixture
async def initialized_movement_analyzer():
    """Create and initialize MovementAnalyzer instance for testing."""
    analyzer = MovementAnalyzer()
    await analyzer.initialize()
    yield analyzer
    await analyzer.cleanup()

@pytest.fixture
def movement_analyzer():
    """Create MovementAnalyzer instance for testing."""
    return MovementAnalyzer()

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
    """Test initialization of MovementAnalyzer."""
    assert isinstance(initialized_movement_analyzer.movement_models, MovementModels)
    assert isinstance(initialized_movement_analyzer.skill_models, SkillModels)
    assert initialized_movement_analyzer.analysis_history == []
    assert isinstance(initialized_movement_analyzer.performance_benchmarks, dict)
    assert isinstance(initialized_movement_analyzer.injury_risk_factors, dict)

@pytest.mark.asyncio
async def test_cleanup(movement_analyzer):
    """Test cleanup of MovementAnalyzer."""
    mock_movement_models = AsyncMock(spec=MovementModels)
    mock_skill_models = AsyncMock(spec=SkillModels)
    
    # Ensure the mock objects have the cleanup method
    mock_movement_models.cleanup = AsyncMock()
    mock_skill_models.cleanup = AsyncMock()
    
    # Patch the _load methods to return our mocks
    with patch.object(movement_analyzer, '_load_movement_models', return_value=mock_movement_models), \
         patch.object(movement_analyzer, '_load_skill_models', return_value=mock_skill_models):

        await movement_analyzer.initialize()
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