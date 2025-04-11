import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.services.physical_education.services.movement_analyzer import MovementAnalyzer
from app.services.physical_education.models.movement_analysis.movement_models import MovementModels
from app.services.physical_education.models.skill_assessment.skill_models import SkillModels

@pytest.fixture
async def movement_analyzer():
    analyzer = MovementAnalyzer()
    await analyzer.initialize()
    yield analyzer
    await analyzer.cleanup()

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
async def test_initialization(movement_analyzer):
    """Test proper initialization of MovementAnalyzer."""
    assert isinstance(movement_analyzer.movement_models, MovementModels)
    assert isinstance(movement_analyzer.skill_models, SkillModels)
    assert movement_analyzer.analysis_history == []
    assert isinstance(movement_analyzer.performance_benchmarks, dict)
    assert isinstance(movement_analyzer.injury_risk_factors, dict)

@pytest.mark.asyncio
async def test_analyze_movement_patterns_ml(movement_analyzer, mock_movement_pattern):
    """Test ML-based movement pattern analysis."""
    patterns = [mock_movement_pattern]
    
    with patch.object(movement_analyzer.movement_models, 'identify_patterns', new_callable=AsyncMock) as mock_identify:
        mock_identify.return_value = {"pattern_type": "throwing"}
        
        result = await movement_analyzer.analyze_movement_patterns_ml(patterns)
        
        assert "pattern_recognition" in result
        assert "temporal_analysis" in result
        assert "biomechanical_analysis" in result

@pytest.mark.asyncio
async def test_generate_realtime_feedback(movement_analyzer, mock_movement_pattern):
    """Test real-time feedback generation."""
    result = await movement_analyzer.generate_realtime_feedback(mock_movement_pattern)
    
    assert "immediate_corrections" in result
    assert "safety_alerts" in result
    assert "performance_optimization" in result

@pytest.mark.asyncio
async def test_predict_injury_risk_ml(movement_analyzer, mock_movement_history):
    """Test ML-based injury risk prediction."""
    result = await movement_analyzer.predict_injury_risk_ml(mock_movement_history)
    
    assert "risk_assessment" in result
    assert "preventive_recommendations" in result
    assert "risk_factors" in result

@pytest.mark.asyncio
async def test_analyze_biomechanics(movement_analyzer, mock_movement_pattern):
    """Test biomechanical analysis."""
    patterns = [mock_movement_pattern]
    result = await movement_analyzer.analyze_biomechanics(patterns)
    
    assert isinstance(result, dict)
    assert "joint_angles" in result
    assert "force_analysis" in result

@pytest.mark.asyncio
async def test_analyze_energy_efficiency(movement_analyzer, mock_movement_pattern):
    """Test energy efficiency analysis."""
    patterns = [mock_movement_pattern]
    result = await movement_analyzer.analyze_energy_efficiency(patterns)
    
    assert isinstance(result, dict)
    assert "efficiency_score" in result
    assert "energy_expenditure" in result

@pytest.mark.asyncio
async def test_analyze_symmetry(movement_analyzer, mock_movement_pattern):
    """Test movement symmetry analysis."""
    patterns = [mock_movement_pattern]
    result = await movement_analyzer.analyze_symmetry(patterns)
    
    assert isinstance(result, dict)
    assert "symmetry_score" in result
    assert "imbalances" in result

@pytest.mark.asyncio
async def test_assess_skill_level(movement_analyzer, mock_movement_pattern):
    """Test skill level assessment."""
    patterns = [mock_movement_pattern]
    result = await movement_analyzer.assess_skill_level(patterns)
    
    assert isinstance(result, dict)
    assert "skill_level" in result
    assert "proficiency_metrics" in result

@pytest.mark.asyncio
async def test_analyze_recovery(movement_analyzer, mock_movement_pattern):
    """Test recovery analysis."""
    result = await movement_analyzer.analyze_recovery({"patterns": [mock_movement_pattern]})
    
    assert isinstance(result, dict)
    assert "fatigue_level" in result
    assert "recovery_recommendations" in result

@pytest.mark.asyncio
async def test_analyze_adaptation(movement_analyzer, mock_movement_pattern):
    """Test adaptation analysis."""
    result = await movement_analyzer.analyze_adaptation({"patterns": [mock_movement_pattern]})
    
    assert isinstance(result, dict)
    assert "adaptation_level" in result
    assert "training_recommendations" in result

@pytest.mark.asyncio
async def test_predict_performance(movement_analyzer, mock_movement_pattern):
    """Test performance prediction."""
    result = await movement_analyzer.predict_performance({"patterns": [mock_movement_pattern]})
    
    assert isinstance(result, dict)
    assert "performance_prediction" in result
    assert "confidence_score" in result

@pytest.mark.asyncio
async def test_environmental_analysis(movement_analyzer, mock_movement_pattern):
    """Test environmental factor analysis."""
    patterns = [mock_movement_pattern]
    result = await movement_analyzer.analyze_environmental_factors(patterns)
    
    assert isinstance(result, dict)
    assert "environmental_impact" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_equipment_analysis(movement_analyzer, mock_movement_pattern):
    """Test equipment usage analysis."""
    patterns = [mock_movement_pattern]
    result = await movement_analyzer.analyze_equipment_usage(patterns)
    
    assert isinstance(result, dict)
    assert "equipment_recommendations" in result
    assert "safety_guidelines" in result

@pytest.mark.asyncio
async def test_comprehensive_feedback(movement_analyzer, mock_movement_pattern):
    """Test comprehensive feedback generation."""
    analysis = {"patterns": [mock_movement_pattern]}
    metrics = {"performance_score": 0.8}
    
    result = await movement_analyzer.generate_comprehensive_feedback(analysis, metrics)
    
    assert isinstance(result, dict)
    assert "technical_feedback" in result
    assert "performance_feedback" in result
    assert "safety_feedback" in result

@pytest.mark.asyncio
async def test_error_handling(movement_analyzer):
    """Test error handling functionality."""
    with pytest.raises(Exception):
        await movement_analyzer.analyze_movement_patterns_ml(None)
    
    with pytest.raises(Exception):
        await movement_analyzer.generate_realtime_feedback(None)

@pytest.mark.asyncio
async def test_performance_tracking(movement_analyzer, mock_movement_history):
    """Test performance tracking functionality."""
    result = await movement_analyzer.track_progress(
        {"patterns": [mock_movement_history[0]["pattern"]]},
        {"performance_score": 0.8}
    )
    
    assert isinstance(result, dict)
    assert "progress_metrics" in result
    assert "improvement_areas" in result 