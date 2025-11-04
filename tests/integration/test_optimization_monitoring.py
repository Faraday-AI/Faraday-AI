import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from app.dashboard.services.optimization_monitoring_service import OptimizationMonitoringService
from app.dashboard.models import ResourceUsage, ResourceSharing, Organization

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def monitoring_service(mock_db):
    return OptimizationMonitoringService(mock_db)

@pytest.fixture
def sample_usage_data():
    now = datetime.utcnow()
    return [
        Mock(
            organization_id="test_org",
            timestamp=now - timedelta(hours=i),
            resource_type="compute",
            usage_amount=float(i)
        )
        for i in range(24)
    ]

@pytest.fixture
def sample_sharing_data():
    now = datetime.utcnow()
    return [
        Mock(
            source_org_id="test_org",
            target_org_id=f"org_{i}",
            timestamp=now - timedelta(hours=i),
            resource_type="compute"
        )
        for i in range(24)
    ]

@pytest.mark.asyncio
async def test_get_optimization_metrics(monitoring_service, mock_db, sample_usage_data, sample_sharing_data):
    """Test getting optimization metrics."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        sample_usage_data,
        sample_sharing_data
    ]

    # Act
    result = await monitoring_service.get_optimization_metrics("test_org", "24h")

    # Assert
    assert isinstance(result, dict)
    assert "utilization_rate" in result
    assert "sharing_efficiency" in result
    assert "optimization_score" in result
    assert "anomalies" in result
    assert "recommendations" in result
    assert "timestamp" in result
    assert 0 <= result["utilization_rate"] <= 1.0
    assert 0 <= result["sharing_efficiency"] <= 1.0
    assert 0 <= result["optimization_score"] <= 100
    assert isinstance(result["anomalies"], list)
    assert isinstance(result["recommendations"], list)
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_get_optimization_insights(monitoring_service, mock_db, sample_usage_data, sample_sharing_data):
    """Test getting optimization insights."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        sample_usage_data,
        sample_sharing_data
    ]

    # Act
    result = await monitoring_service.get_optimization_insights("test_org", "24h")

    # Assert
    assert isinstance(result, dict)
    assert "patterns" in result
    assert "trends" in result
    assert "opportunities" in result
    assert "risks" in result
    assert "timestamp" in result
    assert isinstance(result["patterns"], dict)
    assert isinstance(result["trends"], dict)
    assert isinstance(result["opportunities"], list)
    assert isinstance(result["risks"], list)
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_detect_anomalies(monitoring_service, sample_usage_data, sample_sharing_data):
    """Test anomaly detection."""
    # Act
    anomalies = await monitoring_service._detect_anomalies(
        usage_data=[{
            "timestamp": d.timestamp,
            "resource_type": d.resource_type,
            "usage_amount": d.usage_amount
        } for d in sample_usage_data],
        sharing_data=[{
            "timestamp": d.timestamp,
            "source_org": d.source_org_id,
            "target_org": d.target_org_id,
            "resource_type": d.resource_type
        } for d in sample_sharing_data]
    )

    # Assert
    assert isinstance(anomalies, list)
    for anomaly in anomalies:
        assert "timestamp" in anomaly
        assert "resource_type" in anomaly
        assert "usage_amount" in anomaly
        assert "severity" in anomaly
        assert anomaly["severity"] in ["high", "low"]

@pytest.mark.asyncio
async def test_analyze_patterns(monitoring_service, sample_usage_data, sample_sharing_data):
    """Test pattern analysis."""
    # Act
    patterns = await monitoring_service._analyze_patterns(
        usage_data=[{
            "timestamp": d.timestamp,
            "resource_type": d.resource_type,
            "usage_amount": d.usage_amount
        } for d in sample_usage_data],
        sharing_data=[{
            "timestamp": d.timestamp,
            "source_org": d.source_org_id,
            "target_org": d.target_org_id,
            "resource_type": d.resource_type
        } for d in sample_sharing_data]
    )

    # Assert
    assert isinstance(patterns, dict)
    assert "usage_patterns" in patterns
    assert "sharing_patterns" in patterns
    assert "peak_hours" in patterns["usage_patterns"]
    assert "resource_distribution" in patterns["usage_patterns"]
    assert "usage_trend" in patterns["usage_patterns"]
    assert "frequent_partners" in patterns["sharing_patterns"]
    assert "resource_preferences" in patterns["sharing_patterns"]
    assert "sharing_trend" in patterns["sharing_patterns"]

@pytest.mark.asyncio
async def test_analyze_trends(monitoring_service, sample_usage_data, sample_sharing_data):
    """Test trend analysis."""
    # Act
    trends = await monitoring_service._analyze_trends(
        usage_data=[{
            "timestamp": d.timestamp,
            "resource_type": d.resource_type,
            "usage_amount": d.usage_amount
        } for d in sample_usage_data],
        sharing_data=[{
            "timestamp": d.timestamp,
            "source_org": d.source_org_id,
            "target_org": d.target_org_id,
            "resource_type": d.resource_type
        } for d in sample_sharing_data]
    )

    # Assert
    assert isinstance(trends, dict)
    assert "usage_trend" in trends
    assert "sharing_trend" in trends
    assert "overall_trend" in trends
    assert "direction" in trends["usage_trend"]
    assert "rate" in trends["usage_trend"]
    assert "direction" in trends["sharing_trend"]
    assert "rate" in trends["sharing_trend"]
    assert "score" in trends["overall_trend"]
    assert "direction" in trends["overall_trend"]
    assert "confidence" in trends["overall_trend"]

@pytest.mark.asyncio
async def test_empty_data_handling(monitoring_service):
    """Test handling of empty data."""
    # Act
    metrics = await monitoring_service.get_optimization_metrics("test_org", "24h")
    insights = await monitoring_service.get_optimization_insights("test_org", "24h")

    # Assert
    assert metrics["utilization_rate"] == 0.0
    assert metrics["sharing_efficiency"] == 0.0
    assert metrics["optimization_score"] == 0.0
    assert metrics["anomalies"] == []
    assert metrics["recommendations"] == []
    assert insights["patterns"] == {}
    assert insights["trends"] == {}
    assert insights["opportunities"] == []
    assert insights["risks"] == []

@pytest.mark.asyncio
async def test_error_handling(monitoring_service, mock_db):
    """Test error handling."""
    # Arrange - test that exceptions in data processing are handled gracefully
    # Since we now handle errors gracefully by returning default values, we verify that behavior
    from unittest.mock import patch
    
    # Test that processing errors in individual components are handled gracefully
    with patch.object(monitoring_service, '_calculate_utilization_rate', side_effect=Exception("Processing error")):
        # Should not raise, but return default values
        result = await monitoring_service.get_optimization_metrics("test_org", "24h")
        assert result["utilization_rate"] == 0.0  # Default fallback value
    
    # Test that exceptions in main processing still raise HTTPException
    # Patch a method that's called before the try-except for individual components
    with patch.object(monitoring_service, '_get_usage_data', side_effect=Exception("Database error")):
        with pytest.raises(Exception) as exc_info:
            await monitoring_service.get_optimization_metrics("test_org", "24h")
        assert "Error getting optimization metrics" in (str(exc_info.value.detail) if hasattr(exc_info.value, 'detail') else str(exc_info.value))
    
    with patch.object(monitoring_service, '_get_sharing_data', side_effect=Exception("Database error")):
        with pytest.raises(Exception) as exc_info:
            await monitoring_service.get_optimization_insights("test_org", "24h")
        assert "Error getting optimization insights" in (str(exc_info.value.detail) if hasattr(exc_info.value, 'detail') else str(exc_info.value))

@pytest.mark.asyncio
async def test_time_range_handling(monitoring_service, mock_db, sample_usage_data, sample_sharing_data):
    """Test handling of different time ranges."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        sample_usage_data,
        sample_sharing_data
    ]

    # Act
    result_24h = await monitoring_service.get_optimization_metrics("test_org", "24h")
    result_7d = await monitoring_service.get_optimization_metrics("test_org", "7d")
    result_30d = await monitoring_service.get_optimization_metrics("test_org", "30d")

    # Assert
    assert isinstance(result_24h["timestamp"], datetime)
    assert isinstance(result_7d["timestamp"], datetime)
    assert isinstance(result_30d["timestamp"], datetime)

@pytest.mark.asyncio
async def test_recommendation_generation(monitoring_service, sample_usage_data, sample_sharing_data):
    """Test recommendation generation."""
    # Act
    recommendations = await monitoring_service._generate_recommendations(
        usage_data=[{
            "timestamp": d.timestamp,
            "resource_type": d.resource_type,
            "usage_amount": d.usage_amount
        } for d in sample_usage_data],
        sharing_data=[{
            "timestamp": d.timestamp,
            "source_org": d.source_org_id,
            "target_org": d.target_org_id,
            "resource_type": d.resource_type
        } for d in sample_sharing_data]
    )

    # Assert
    assert isinstance(recommendations, list)
    for recommendation in recommendations:
        assert "type" in recommendation
        assert "priority" in recommendation
        assert "message" in recommendation
        assert recommendation["priority"] in ["high", "medium", "low"] 