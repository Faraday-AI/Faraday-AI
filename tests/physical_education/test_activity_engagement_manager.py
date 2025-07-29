import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.activity_engagement_manager import ActivityEngagementManager
from datetime import datetime, timedelta
import numpy as np

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_engagement_model():
    with patch('app.models.engagement.EngagementModel') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def engagement_manager(mock_db, mock_activity_manager, mock_engagement_model):
    return ActivityEngagementManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_measure_engagement(engagement_manager, mock_activity_manager):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    engagement_data = {
        "participation_level": 0.85,
        "focus_duration": 45,
        "interaction_count": 10,
        "feedback_quality": 0.8
    }
    mock_activity_manager.get_student_engagement.return_value = engagement_data
    
    # Test
    result = await engagement_manager.measure_engagement(student_id, activity_id)
    
    # Verify
    assert result['engagement_measured'] is True
    assert 'engagement_score' in result
    assert 'engagement_level' in result
    assert 'improvement_areas' in result
    mock_activity_manager.get_student_engagement.assert_called_once_with(student_id, activity_id)

@pytest.mark.asyncio
async def test_analyze_engagement_patterns(engagement_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "timestamp": datetime.now() - timedelta(days=2),
            "engagement_metrics": {"participation": 0.7, "focus": 0.6}
        },
        {
            "timestamp": datetime.now() - timedelta(days=1),
            "engagement_metrics": {"participation": 0.8, "focus": 0.7}
        }
    ]
    
    # Test
    result = await engagement_manager.analyze_engagement_patterns(student_id, activity_id)
    
    # Verify
    assert 'patterns' in result
    assert 'trends' in result
    assert 'peak_times' in result
    assert 'low_engagement_periods' in result
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_generate_engagement_report(engagement_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    engagement_data = {
        "current_engagement": {"score": 0.85, "level": "high"},
        "patterns": {"trend": "improving", "consistency": 0.8},
        "recommendations": ["Increase interactive elements", "Add more challenges"]
    }
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "id": activity_id,
        "student_id": student_id,
        "engagement_history": [
            {"timestamp": datetime.now() - timedelta(days=1), "score": 0.8}
        ]
    }
    
    # Test
    result = await engagement_manager.generate_engagement_report(student_id, activity_id, engagement_data)
    
    # Verify
    assert 'report_id' in result
    assert 'download_url' in result
    assert 'expires_at' in result
    assert 'summary' in result
    assert 'details' in result
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_suggest_engagement_improvements(engagement_manager, mock_engagement_model):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    current_engagement = {
        "participation": 0.7,
        "focus": 0.6,
        "interaction": 0.5
    }
    mock_engagement_model.return_value.predict.return_value = np.array([0.8])
    
    # Test
    result = await engagement_manager.suggest_engagement_improvements(student_id, activity_id, current_engagement)
    
    # Verify
    assert 'suggestions' in result
    assert 'expected_improvement' in result
    assert 'implementation_guidelines' in result
    mock_engagement_model.return_value.predict.assert_called_once()

@pytest.mark.asyncio
async def test_get_engagement_history(engagement_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "engage1",
            "timestamp": datetime.now() - timedelta(days=1),
            "engagement_metrics": {"participation": 0.8, "focus": 0.7},
            "improvements_made": ["Added interactive elements"]
        }
    ]
    
    # Test
    result = await engagement_manager.get_engagement_history(student_id, activity_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('timestamp' in item for item in result)
    assert all('engagement_metrics' in item for item in result)
    assert all('improvements_made' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_predict_engagement_trends(engagement_manager, mock_engagement_model):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    historical_data = [
        {"timestamp": datetime.now() - timedelta(days=2), "engagement_score": 0.7},
        {"timestamp": datetime.now() - timedelta(days=1), "engagement_score": 0.8}
    ]
    mock_engagement_model.return_value.predict.return_value = np.array([0.9])
    
    # Test
    result = await engagement_manager.predict_engagement_trends(student_id, activity_id, historical_data)
    
    # Verify
    assert 'predicted_scores' in result
    assert 'trend_direction' in result
    assert 'confidence_level' in result
    mock_engagement_model.return_value.predict.assert_called_once() 