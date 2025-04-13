import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.services.activity_progress_manager import ActivityProgressManager
from datetime import datetime, timedelta
import numpy as np

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_progress_model():
    with patch('app.models.progress.ProgressModel') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def progress_manager(mock_db, mock_activity_manager, mock_progress_model):
    return ActivityProgressManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_track_activity_progress(progress_manager, mock_activity_manager):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    performance_data = {
        "completion_time": 45,
        "accuracy": 0.85,
        "effort_level": 0.7,
        "form_score": 0.8
    }
    mock_activity_manager.get_student_performance.return_value = performance_data
    
    # Test
    result = await progress_manager.track_activity_progress(student_id, activity_id)
    
    # Verify
    assert result['progress_tracked'] is True
    assert 'current_metrics' in result
    assert 'improvement' in result
    assert 'next_goals' in result
    mock_activity_manager.get_student_performance.assert_called_once_with(student_id, activity_id)

@pytest.mark.asyncio
async def test_calculate_improvement_metrics(progress_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "timestamp": datetime.now() - timedelta(days=2),
            "metrics": {"accuracy": 0.7, "speed": 0.6}
        },
        {
            "timestamp": datetime.now() - timedelta(days=1),
            "metrics": {"accuracy": 0.8, "speed": 0.7}
        }
    ]
    
    # Test
    result = await progress_manager.calculate_improvement_metrics(student_id, activity_id)
    
    # Verify
    assert 'improvement_percentage' in result
    assert 'trend' in result
    assert 'milestones' in result
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_generate_progress_report(progress_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    progress_data = {
        "current_metrics": {"accuracy": 0.85, "speed": 0.75},
        "improvement": {"percentage": 15, "trend": "positive"},
        "milestones": ["First goal achieved", "Second goal in progress"]
    }
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "id": activity_id,
        "student_id": student_id,
        "progress_history": [
            {"timestamp": datetime.now() - timedelta(days=1), "metrics": {"accuracy": 0.8}}
        ]
    }
    
    # Test
    result = await progress_manager.generate_progress_report(student_id, activity_id, progress_data)
    
    # Verify
    assert 'report_id' in result
    assert 'download_url' in result
    assert 'expires_at' in result
    assert 'summary' in result
    assert 'details' in result
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_set_progress_goals(progress_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    goals = {
        "short_term": {"target_accuracy": 0.9, "target_speed": 0.8},
        "long_term": {"target_accuracy": 0.95, "target_speed": 0.9}
    }
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "id": activity_id,
        "student_id": student_id
    }
    
    # Test
    result = await progress_manager.set_progress_goals(student_id, activity_id, goals)
    
    # Verify
    assert 'goals_set' in result
    assert 'short_term_goals' in result
    assert 'long_term_goals' in result
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_get_progress_history(progress_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "progress1",
            "timestamp": datetime.now() - timedelta(days=1),
            "metrics": {"accuracy": 0.8, "speed": 0.7},
            "goals_achieved": ["First milestone"]
        }
    ]
    
    # Test
    result = await progress_manager.get_progress_history(student_id, activity_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('timestamp' in item for item in result)
    assert all('metrics' in item for item in result)
    assert all('goals_achieved' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_predict_future_progress(progress_manager, mock_progress_model):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    historical_data = [
        {"timestamp": datetime.now() - timedelta(days=2), "metrics": {"accuracy": 0.7}},
        {"timestamp": datetime.now() - timedelta(days=1), "metrics": {"accuracy": 0.8}}
    ]
    mock_progress_model.return_value.predict.return_value = np.array([0.9])
    
    # Test
    result = await progress_manager.predict_future_progress(student_id, activity_id, historical_data)
    
    # Verify
    assert 'predicted_metrics' in result
    assert 'confidence_intervals' in result
    assert 'milestone_estimates' in result
    mock_progress_model.return_value.predict.assert_called_once() 