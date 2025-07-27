"""
Tests for the analytics service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np

from app.dashboard.services.analytics_service import AnalyticsService
from app.dashboard.models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsageHistory,
    GPTCategory,
    GPTType
)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def analytics_service(mock_db):
    return AnalyticsService(mock_db)

@pytest.fixture
def sample_performance_data():
    now = datetime.utcnow()
    return [
        Mock(
            id=f"perf-{i}",
            subscription_id="sub-1",
            metrics={
                "response_time": 0.5 + i * 0.1,
                "accuracy": 0.8 + i * 0.02,
                "user_satisfaction": 0.85 + i * 0.01,
                "resource_usage": 0.4 + i * 0.05
            },
            timestamp=now - timedelta(hours=i)
        )
        for i in range(24)  # 24 hours of data
    ]

@pytest.fixture
def sample_usage_data():
    now = datetime.utcnow()
    return [
        Mock(
            id=f"usage-{i}",
            subscription_id="sub-1",
            interaction_type="api_call",
            details={
                "resource_usage": 0.4 + (i % 24) * 0.02,
                "duration": 0.5,
                "memory_used": 100 + i * 10
            },
            created_at=now - timedelta(hours=i)
        )
        for i in range(72)  # 3 days of data
    ]

@pytest.fixture
def sample_gpts():
    return [
        Mock(
            id="gpt-1",
            name="Math Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.MATH_TEACHER
        ),
        Mock(
            id="gpt-2",
            name="Science Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.SCIENCE_TEACHER
        )
    ]

async def test_get_performance_trends(
    analytics_service,
    mock_db,
    sample_performance_data
):
    """Test getting performance trends."""
    # Mock database query
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = (
        sample_performance_data
    )

    trends = await analytics_service.get_performance_trends("gpt-1")
    
    # Check that required fields are present
    assert "trends" in trends
    assert "timestamps" in trends
    assert "metrics" in trends
    
    # Verify trend data structure
    assert "response_time" in trends["trends"]
    assert "accuracy" in trends["trends"]
    assert "user_satisfaction" in trends["trends"]
    assert "resource_usage" in trends["trends"]
    
    # Verify metrics data structure
    assert "response_time" in trends["metrics"]
    assert "accuracy" in trends["metrics"]
    assert "user_satisfaction" in trends["metrics"]
    assert "resource_usage" in trends["metrics"]
    
    # Verify metrics have current and trend values
    for metric in trends["metrics"].values():
        assert "current" in metric
        assert "trend" in metric

async def test_predict_resource_usage(
    analytics_service,
    mock_db,
    sample_usage_data
):
    """Test resource usage prediction."""
    # Mock database query
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = (
        sample_usage_data
    )

    prediction = await analytics_service.predict_resource_usage("gpt-1")
    
    # Check that required fields are present (service doesn't return status)
    assert "predictions" in prediction
    assert "timestamps" in prediction
    assert "confidence" in prediction
    assert "impact" in prediction
    assert "optimization" in prediction
    assert "risk" in prediction
    assert "mitigation" in prediction
    
    # Verify predictions structure
    assert isinstance(prediction["predictions"], dict)
    assert isinstance(prediction["timestamps"], list)

async def test_get_comparative_analysis(
    analytics_service,
    mock_db,
    sample_gpts,
    sample_performance_data
):
    """Test comparative analysis."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_gpts[0]
    mock_db.query.return_value.filter.return_value.all.return_value = sample_gpts
    
    def mock_get_metrics(*args, **kwargs):
        return sample_performance_data[-1].metrics
    
    with patch.object(
        analytics_service,
        '_get_average_metrics',
        side_effect=mock_get_metrics
    ):
        analysis = await analytics_service.get_comparative_analysis("gpt-1")
        
        assert analysis["status"] == "success"
        assert "rankings" in analysis
        assert "comparative_metrics" in analysis
        assert "improvement_opportunities" in analysis

def test_analyze_metric_trend(analytics_service):
    """Test metric trend analysis."""
    # Create sample DataFrame
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=24, freq="H"),
        "response_time": np.linspace(0.5, 0.8, 24),  # Increasing trend
        "accuracy": np.linspace(0.9, 0.85, 24)  # Decreasing trend
    })
    
    # Test increasing trend
    response_trend = analytics_service._analyze_metric_trend(df, "response_time")
    assert response_trend["trend"] == "degrading"  # Higher response time is worse
    
    # Test decreasing trend
    accuracy_trend = analytics_service._analyze_metric_trend(df, "accuracy")
    assert accuracy_trend["trend"] == "degrading"

def test_calculate_performance_score(analytics_service):
    """Test performance score calculation."""
    trends = {
        "response_time": {
            "status": "success",
            "current_value": 0.5
        },
        "accuracy": {
            "status": "success",
            "current_value": 0.9
        },
        "user_satisfaction": {
            "status": "success",
            "current_value": 0.85
        },
        "resource_usage": {
            "status": "success",
            "current_value": 0.6
        }
    }
    
    score = analytics_service._calculate_performance_score(trends)
    assert 0 <= score <= 1
    
    # Test with missing metrics
    incomplete_trends = {
        "response_time": {
            "status": "success",
            "current_value": 0.5
        }
    }
    partial_score = analytics_service._calculate_performance_score(incomplete_trends)
    assert 0 <= partial_score <= 1

def test_generate_recommendations(analytics_service):
    """Test recommendation generation."""
    trends = {
        "response_time": {
            "trend": "degrading",
            "current_value": 0.8
        },
        "accuracy": {
            "trend": "stable",
            "current_value": 0.75
        },
        "resource_usage": {
            "trend": "improving",
            "current_value": 0.5
        }
    }
    
    recommendations = analytics_service._generate_recommendations(trends)
    assert len(recommendations) > 0
    
    # Verify recommendation structure
    for rec in recommendations:
        assert "category" in rec
        assert "priority" in rec
        assert "message" in rec

def test_analyze_usage_patterns(analytics_service):
    """Test usage pattern analysis."""
    # Create sample DataFrame
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=72, freq="H"),
        "resource_usage": np.concatenate([
            np.random.normal(0.5, 0.1, 24),  # Day 1
            np.random.normal(0.6, 0.1, 24),  # Day 2
            np.random.normal(0.7, 0.1, 24)   # Day 3
        ])
    })
    
    predictions = analytics_service._analyze_usage_patterns(df, "24h")
    assert "peak_hours" in predictions
    assert "growth_trend" in predictions
    assert "predicted_peak_usage" in predictions
    
    # Verify peak hours
    assert len(predictions["peak_hours"]) == 3
    assert all(0 <= hour <= 23 for hour in predictions["peak_hours"])

def test_calculate_confidence_score(analytics_service):
    """Test confidence score calculation."""
    # Create sample DataFrame with consistent patterns
    df_consistent = pd.DataFrame({
        "resource_usage": np.random.normal(0.5, 0.05, 1000)  # Low variance
    })
    consistent_score = analytics_service._calculate_confidence_score(df_consistent)
    
    # Create sample DataFrame with inconsistent patterns
    df_inconsistent = pd.DataFrame({
        "resource_usage": np.random.normal(0.5, 0.25, 1000)  # High variance
    })
    inconsistent_score = analytics_service._calculate_confidence_score(df_inconsistent)
    
    assert consistent_score > inconsistent_score
    assert 0 <= consistent_score <= 1
    assert 0 <= inconsistent_score <= 1

def test_identify_bottlenecks(analytics_service):
    """Test bottleneck identification."""
    predictions = {
        "predicted_peak_usage": 0.85,  # Above 80% threshold
        "growth_trend": 0.15  # Above 10% threshold
    }
    
    bottlenecks = analytics_service._identify_bottlenecks(predictions)
    assert len(bottlenecks) == 2  # Should identify both issues
    
    # Verify bottleneck structure
    for bottleneck in bottlenecks:
        assert "type" in bottleneck
        assert "severity" in bottleneck
        assert "description" in bottleneck
        assert "mitigation" in bottleneck

def test_calculate_rankings(analytics_service):
    """Test ranking calculation."""
    comparative_metrics = {
        "gpt-1": {
            "accuracy": 0.9,
            "response_time": 0.5
        },
        "gpt-2": {
            "accuracy": 0.85,
            "response_time": 0.6
        },
        "gpt-3": {
            "accuracy": 0.95,
            "response_time": 0.4
        }
    }
    
    rankings = analytics_service._calculate_rankings("gpt-1", comparative_metrics)
    
    # Verify ranking structure
    for metric in ["accuracy", "response_time"]:
        assert metric in rankings
        assert "value" in rankings[metric]
        assert "percentile" in rankings[metric]
        assert "rank" in rankings[metric]
        assert "total" in rankings[metric]
        assert rankings[metric]["total"] == 3

def test_identify_improvements(analytics_service):
    """Test improvement identification."""
    comparative_metrics = {
        "gpt-1": {
            "accuracy": 0.8,
            "response_time": 0.6
        },
        "gpt-2": {
            "accuracy": 0.95,  # Significantly better
            "response_time": 0.4  # Significantly better
        }
    }
    
    improvements = analytics_service._identify_improvements("gpt-1", comparative_metrics)
    assert len(improvements) == 2  # Should identify both metrics
    
    # Verify improvement structure
    for improvement in improvements:
        assert "metric" in improvement
        assert "current_value" in improvement
        assert "top_value" in improvement
        assert "gap" in improvement
        assert "priority" in improvement 