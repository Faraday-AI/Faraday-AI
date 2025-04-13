import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.services.activity_adaptation_manager import ActivityAdaptationManager
from datetime import datetime, timedelta
import numpy as np

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_adaptation_model():
    with patch('app.models.activity_adaptation.ActivityAdaptationModel') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def adaptation_manager(mock_db, mock_activity_manager, mock_adaptation_model):
    return ActivityAdaptationManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_analyze_adaptation_needs(adaptation_manager, mock_adaptation_model):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    performance_data = {
        "completion_time": 45,
        "accuracy": 0.85,
        "difficulty_level": "moderate"
    }
    mock_adaptation_model.return_value.analyze.return_value = {
        "needs_adaptation": True,
        "adaptation_type": "simplification",
        "confidence": 0.85
    }
    
    # Test
    result = await adaptation_manager.analyze_adaptation_needs(activity_id, student_id, performance_data)
    
    # Verify
    assert result['needs_adaptation'] is True
    assert 'adaptation_type' in result
    assert 'confidence' in result
    mock_adaptation_model.return_value.analyze.assert_called_once()

@pytest.mark.asyncio
async def test_generate_adaptation_plan(adaptation_manager, mock_adaptation_model):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    adaptation_type = "simplification"
    mock_adaptation_model.return_value.generate_plan.return_value = {
        "plan_id": "plan123",
        "adaptations": [
            {"type": "simplify_instructions", "priority": "high"},
            {"type": "reduce_complexity", "priority": "medium"}
        ],
        "estimated_impact": 0.75
    }
    
    # Test
    result = await adaptation_manager.generate_adaptation_plan(activity_id, student_id, adaptation_type)
    
    # Verify
    assert 'plan_id' in result
    assert 'adaptations' in result
    assert 'estimated_impact' in result
    mock_adaptation_model.return_value.generate_plan.assert_called_once()

@pytest.mark.asyncio
async def test_apply_adaptations(adaptation_manager, mock_adaptation_model):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    adaptation_plan = {
        "adaptations": [
            {"type": "simplify_instructions", "priority": "high"},
            {"type": "reduce_complexity", "priority": "medium"}
        ]
    }
    mock_adaptation_model.return_value.apply.return_value = {
        "applied": True,
        "modified_activity": {
            "id": activity_id,
            "instructions": "simplified",
            "complexity": "reduced"
        }
    }
    
    # Test
    result = await adaptation_manager.apply_adaptations(activity_id, student_id, adaptation_plan)
    
    # Verify
    assert result['applied'] is True
    assert 'modified_activity' in result
    mock_adaptation_model.return_value.apply.assert_called_once()

@pytest.mark.asyncio
async def test_evaluate_adaptation_effectiveness(adaptation_manager, mock_adaptation_model):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    adaptation_id = "adapt123"
    post_adaptation_data = {
        "completion_time": 35,
        "accuracy": 0.92,
        "student_feedback": "positive"
    }
    mock_adaptation_model.return_value.evaluate.return_value = {
        "effectiveness_score": 0.85,
        "improvement_metrics": {
            "completion_time": -22.2,
            "accuracy": 8.2
        },
        "recommendations": ["maintain_current_adaptations"]
    }
    
    # Test
    result = await adaptation_manager.evaluate_adaptation_effectiveness(
        activity_id, student_id, adaptation_id, post_adaptation_data
    )
    
    # Verify
    assert 'effectiveness_score' in result
    assert 'improvement_metrics' in result
    assert 'recommendations' in result
    mock_adaptation_model.return_value.evaluate.assert_called_once()

@pytest.mark.asyncio
async def test_get_adaptation_history(adaptation_manager, mock_db):
    # Setup
    student_id = "test_student"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "adapt1",
            "activity_id": "test_activity",
            "adaptation_type": "simplification",
            "timestamp": datetime.now() - timedelta(days=1),
            "effectiveness": 0.85
        }
    ]
    
    # Test
    result = await adaptation_manager.get_adaptation_history(student_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('activity_id' in item for item in result)
    assert all('adaptation_type' in item for item in result)
    assert all('timestamp' in item for item in result)
    assert all('effectiveness' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_optimize_adaptations(adaptation_manager, mock_adaptation_model):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    historical_data = {
        "previous_adaptations": [
            {"type": "simplification", "effectiveness": 0.85},
            {"type": "complexity_reduction", "effectiveness": 0.75}
        ],
        "performance_trends": {
            "completion_time": "decreasing",
            "accuracy": "improving"
        }
    }
    mock_adaptation_model.return_value.optimize.return_value = {
        "optimized_plan": {
            "adaptations": [
                {"type": "simplification", "priority": "high"},
                {"type": "additional_support", "priority": "medium"}
            ]
        },
        "expected_improvement": 0.15
    }
    
    # Test
    result = await adaptation_manager.optimize_adaptations(activity_id, student_id, historical_data)
    
    # Verify
    assert 'optimized_plan' in result
    assert 'expected_improvement' in result
    mock_adaptation_model.return_value.optimize.assert_called_once() 