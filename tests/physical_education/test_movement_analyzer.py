import pytest
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.services.movement_analyzer import MovementAnalyzer
from app.services.physical_education.models.movement_analysis.movement_models import MovementModels
from app.services.physical_education.models.skill_assessment.skill_models import SkillModels

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

@pytest.mark.asyncio
async def test_initialization(movement_analyzer, mock_movement_models, mock_skill_models):
    """Test initialization of MovementAnalyzer."""
    with patch.object(movement_analyzer, 'movement_models', mock_movement_models), \
         patch.object(movement_analyzer, 'skill_models', mock_skill_models):
        
        await movement_analyzer.initialize()
        
        mock_movement_models.initialize.assert_called_once()
        mock_skill_models.initialize.assert_called_once()
        assert movement_analyzer.optimization_config["max_cache_size"] == 1000
        assert movement_analyzer.optimization_config["max_batch_size"] == 50

@pytest.mark.asyncio
async def test_cleanup(movement_analyzer, mock_movement_models, mock_skill_models):
    """Test cleanup of MovementAnalyzer."""
    with patch.object(movement_analyzer, 'movement_models', mock_movement_models), \
         patch.object(movement_analyzer, 'skill_models', mock_skill_models):
        
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