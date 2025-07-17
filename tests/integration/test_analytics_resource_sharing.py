import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from app.dashboard.services.analytics_service import AnalyticsService
from app.dashboard.models import ResourceUsage, ResourceSharing, Organization

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def analytics_service(mock_db):
    return AnalyticsService(mock_db)

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
async def test_get_resource_usage_metrics(analytics_service, mock_db, sample_usage_data):
    """Test getting resource usage metrics."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.return_value = sample_usage_data

    # Act
    result = await analytics_service.get_resource_usage_metrics("test_org", "24h")

    # Assert
    assert isinstance(result, dict)
    assert "total_usage" in result
    assert "average_usage" in result
    assert "peak_usage" in result
    assert "usage_by_type" in result
    assert "timestamp" in result
    assert result["total_usage"] > 0
    assert result["average_usage"] > 0
    assert result["peak_usage"] > 0
    assert isinstance(result["usage_by_type"], dict)
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_get_sharing_patterns(analytics_service, mock_db, sample_sharing_data):
    """Test analyzing sharing patterns."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.return_value = sample_sharing_data

    # Act
    result = await analytics_service.get_sharing_patterns("test_org", "24h")

    # Assert
    assert isinstance(result, dict)
    assert "frequent_pairs" in result
    assert "sharing_frequency" in result
    assert "resource_popularity" in result
    assert "timestamp" in result
    assert isinstance(result["frequent_pairs"], list)
    assert isinstance(result["sharing_frequency"], dict)
    assert isinstance(result["resource_popularity"], dict)
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_get_efficiency_metrics(analytics_service, mock_db, sample_usage_data, sample_sharing_data):
    """Test calculating efficiency metrics."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        sample_usage_data,
        sample_sharing_data
    ]

    # Act
    result = await analytics_service.get_efficiency_metrics("test_org", "24h")

    # Assert
    assert isinstance(result, dict)
    assert "utilization_rate" in result
    assert "sharing_efficiency" in result
    assert "cost_savings" in result
    assert "optimization_score" in result
    assert "timestamp" in result
    assert 0 <= result["utilization_rate"] <= 100
    assert 0 <= result["sharing_efficiency"] <= 100
    assert result["cost_savings"] >= 0
    assert 0 <= result["optimization_score"] <= 100
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_get_sharing_trends(analytics_service, mock_db, sample_usage_data, sample_sharing_data):
    """Test analyzing sharing trends."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        sample_usage_data,
        sample_sharing_data
    ]

    # Act
    result = await analytics_service.get_sharing_trends("test_org", "24h")

    # Assert
    assert isinstance(result, dict)
    assert "usage_trend" in result
    assert "sharing_trend" in result
    assert "efficiency_trend" in result
    assert "timestamp" in result
    assert isinstance(result["usage_trend"], list)
    assert isinstance(result["sharing_trend"], list)
    assert isinstance(result["efficiency_trend"], list)
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_empty_data_handling(analytics_service, mock_db):
    """Test handling of empty data."""
    # Arrange
    mock_db.query.return_value.filter.return_value.all.return_value = []

    # Act
    usage_result = await analytics_service.get_resource_usage_metrics("test_org", "24h")
    sharing_result = await analytics_service.get_sharing_patterns("test_org", "24h")
    trends_result = await analytics_service.get_sharing_trends("test_org", "24h")

    # Assert
    assert usage_result["total_usage"] == 0
    assert usage_result["average_usage"] == 0
    assert usage_result["peak_usage"] == 0
    assert sharing_result["frequent_pairs"] == []
    assert sharing_result["sharing_frequency"] == {}
    assert sharing_result["resource_popularity"] == {}
    assert trends_result["usage_trend"] == []
    assert trends_result["sharing_trend"] == []
    assert trends_result["efficiency_trend"] == []

@pytest.mark.asyncio
async def test_error_handling(analytics_service, mock_db):
    """Test error handling."""
    # Arrange
    mock_db.query.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await analytics_service.get_resource_usage_metrics("test_org", "24h")
    assert "Error getting resource usage metrics" in str(exc_info.value)

    with pytest.raises(Exception) as exc_info:
        await analytics_service.get_sharing_patterns("test_org", "24h")
    assert "Error analyzing sharing patterns" in str(exc_info.value)

    with pytest.raises(Exception) as exc_info:
        await analytics_service.get_sharing_trends("test_org", "24h")
    assert "Error analyzing sharing trends" in str(exc_info.value) 