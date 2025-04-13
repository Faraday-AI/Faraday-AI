import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.services.activity_analytics_manager import ActivityAnalyticsManager
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_analytics_service():
    with patch('app.services.analytics.AnalyticsService') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def analytics_manager(mock_db, mock_activity_manager, mock_analytics_service):
    return ActivityAnalyticsManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_analyze_activity_performance(analytics_manager, mock_activity_manager):
    # Setup
    activity_id = "test_activity"
    performance_data = {
        "completion_times": [45, 40, 38],
        "accuracy_scores": [0.85, 0.88, 0.90],
        "participation_rates": [0.95, 0.92, 0.98]
    }
    mock_activity_manager.get_activity_performance.return_value = performance_data
    
    # Test
    result = await analytics_manager.analyze_activity_performance(activity_id)
    
    # Verify
    assert result['analysis_complete'] is True
    assert 'performance_metrics' in result
    assert 'trends' in result
    assert 'insights' in result
    mock_activity_manager.get_activity_performance.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_generate_performance_report(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    report_type = "weekly"
    mock_analytics_service.return_value.generate_report.return_value = {
        "report_id": "report123",
        "period": "2024-03-18 to 2024-03-24",
        "metrics": {
            "total_participants": 50,
            "average_score": 85,
            "improvement_rate": 15
        }
    }
    
    # Test
    result = await analytics_manager.generate_performance_report(activity_id, report_type)
    
    # Verify
    assert 'report_id' in result
    assert 'period' in result
    assert 'metrics' in result
    mock_analytics_service.return_value.generate_report.assert_called_once()

@pytest.mark.asyncio
async def test_identify_performance_patterns(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    historical_data = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(days=i) for i in range(3)],
        'completion_time': [45, 40, 38],
        'accuracy': [0.85, 0.88, 0.90]
    })
    mock_analytics_service.return_value.analyze.return_value = {
        "patterns": ["Decreasing completion time", "Increasing accuracy"],
        "correlations": {"completion_time_accuracy": -0.8}
    }
    
    # Test
    result = await analytics_manager.identify_performance_patterns(activity_id, historical_data)
    
    # Verify
    assert 'patterns' in result
    assert 'correlations' in result
    assert 'significance_levels' in result
    mock_analytics_service.return_value.analyze.assert_called_once()

@pytest.mark.asyncio
async def test_predict_future_performance(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    historical_data = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(days=i) for i in range(3)],
        'completion_time': [45, 40, 38],
        'accuracy': [0.85, 0.88, 0.90]
    })
    mock_analytics_service.return_value.predict.return_value = {
        "predicted_metrics": {"completion_time": 35, "accuracy": 0.92},
        "confidence_intervals": {"completion_time": [33, 37], "accuracy": [0.90, 0.94]}
    }
    
    # Test
    result = await analytics_manager.predict_future_performance(activity_id, historical_data)
    
    # Verify
    assert 'predicted_metrics' in result
    assert 'confidence_intervals' in result
    assert 'trend_projections' in result
    mock_analytics_service.return_value.predict.assert_called_once()

@pytest.mark.asyncio
async def test_get_analytics_history(analytics_manager, mock_db):
    # Setup
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "analytics1",
            "timestamp": datetime.now() - timedelta(days=1),
            "analysis_type": "performance",
            "results": {"average_completion_time": 41, "trend": "improving"}
        }
    ]
    
    # Test
    result = await analytics_manager.get_analytics_history(activity_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('timestamp' in item for item in result)
    assert all('analysis_type' in item for item in result)
    assert all('results' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_export_analytics_data(analytics_manager, mock_db):
    # Setup
    activity_id = "test_activity"
    analytics_data = {
        "performance_metrics": {"average_completion_time": 41, "average_accuracy": 0.88},
        "trends": {"completion_time": "decreasing", "accuracy": "improving"},
        "predictions": {"next_week_completion_time": 35, "next_week_accuracy": 0.92}
    }
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "id": activity_id,
        "analytics_history": [
            {"timestamp": datetime.now() - timedelta(days=1), "metrics": {"completion_time": 45}}
        ]
    }
    
    # Test
    result = await analytics_manager.export_analytics_data(activity_id, analytics_data)
    
    # Verify
    assert 'export_id' in result
    assert 'download_url' in result
    assert 'expires_at' in result
    assert 'data_format' in result
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_track_activity_metrics(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    metrics_data = {
        "duration": 45,
        "intensity": "moderate",
        "calories_burned": 300,
        "heart_rate": {"avg": 120, "max": 150},
        "steps": 5000
    }
    mock_analytics_service.return_value.track_metrics.return_value = {
        "tracked": True,
        "timestamp": datetime.now()
    }
    
    # Test
    result = await analytics_manager.track_activity_metrics(activity_id, metrics_data)
    
    # Verify
    assert result['tracked'] is True
    assert 'timestamp' in result
    mock_analytics_service.return_value.track_metrics.assert_called_once()

@pytest.mark.asyncio
async def test_get_activity_insights(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    time_range = {
        "start": datetime.now() - timedelta(days=7),
        "end": datetime.now()
    }
    mock_analytics_service.return_value.get_insights.return_value = {
        "insights": {
            "participation_rate": 85,
            "average_duration": 40,
            "popular_time_slots": ["morning", "afternoon"],
            "success_rate": 90
        }
    }
    
    # Test
    result = await analytics_manager.get_activity_insights(activity_id, time_range)
    
    # Verify
    assert 'insights' in result
    assert 'participation_rate' in result['insights']
    assert 'average_duration' in result['insights']
    assert 'popular_time_slots' in result['insights']
    assert 'success_rate' in result['insights']
    mock_analytics_service.return_value.get_insights.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_trends(analytics_manager, mock_analytics_service):
    # Setup
    activity_type = "cardio"
    time_range = {
        "start": datetime.now() - timedelta(days=30),
        "end": datetime.now()
    }
    mock_analytics_service.return_value.analyze_trends.return_value = {
        "trends": {
            "participation_growth": 10,
            "performance_trend": "improving",
            "peak_hours": ["09:00", "15:00"],
            "seasonal_patterns": ["weekday_morning", "weekend_afternoon"]
        }
    }
    
    # Test
    result = await analytics_manager.analyze_trends(activity_type, time_range)
    
    # Verify
    assert 'trends' in result
    assert 'participation_growth' in result['trends']
    assert 'performance_trend' in result['trends']
    assert 'peak_hours' in result['trends']
    assert 'seasonal_patterns' in result['trends']
    mock_analytics_service.return_value.analyze_trends.assert_called_once()

@pytest.mark.asyncio
async def test_get_engagement_metrics(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    mock_analytics_service.return_value.get_engagement_metrics.return_value = {
        "metrics": {
            "daily_active_users": 25,
            "session_duration": 45,
            "retention_rate": 80,
            "feedback_score": 4.5
        }
    }
    
    # Test
    result = await analytics_manager.get_engagement_metrics(activity_id)
    
    # Verify
    assert 'metrics' in result
    assert 'daily_active_users' in result['metrics']
    assert 'session_duration' in result['metrics']
    assert 'retention_rate' in result['metrics']
    assert 'feedback_score' in result['metrics']
    mock_analytics_service.return_value.get_engagement_metrics.assert_called_once()

@pytest.mark.asyncio
async def test_predict_activity_outcomes(analytics_manager, mock_analytics_service):
    # Setup
    activity_id = "test_activity"
    mock_analytics_service.return_value.predict_outcomes.return_value = {
        "predictions": {
            "expected_participation": 30,
            "success_probability": 85,
            "risk_factors": ["weather", "time_of_day"],
            "recommendations": ["increase_duration", "add_warmup"]
        }
    }
    
    # Test
    result = await analytics_manager.predict_activity_outcomes(activity_id)
    
    # Verify
    assert 'predictions' in result
    assert 'expected_participation' in result['predictions']
    assert 'success_probability' in result['predictions']
    assert 'risk_factors' in result['predictions']
    assert 'recommendations' in result['predictions']
    mock_analytics_service.return_value.predict_outcomes.assert_called_once() 