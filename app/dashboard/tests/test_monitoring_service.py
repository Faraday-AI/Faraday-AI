"""
Tests for the monitoring service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import prometheus_client as prom
import redis
from redis.exceptions import ConnectionError, TimeoutError
import asyncio

from ...models import (
    GPTContext,
    ContextInteraction,
    SharedContext,
    GPTPerformance,
    GPTDefinition
)
from ...services.monitoring_service import MonitoringService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_redis():
    mock = MagicMock(spec=redis.Redis)
    mock.get.return_value = None  # Default to cache miss
    return mock

@pytest.fixture
def monitoring_service(mock_db):
    with patch('redis.from_url') as mock_redis_client:
        mock_redis_client.return_value = Mock(spec=redis.Redis)
        return MonitoringService(mock_db)

@pytest.fixture
def sample_metrics():
    return [
        GPTPerformance(
            id="perf-1",
            gpt_definition_id="gpt-1",
            metrics={
                "accuracy": 0.85,
                "response_time_score": 0.75,
                "user_satisfaction": 0.90
            },
            timestamp=datetime.utcnow() - timedelta(hours=1)
        ),
        GPTPerformance(
            id="perf-2",
            gpt_definition_id="gpt-1",
            metrics={
                "accuracy": 0.80,
                "response_time_score": 0.70,
                "user_satisfaction": 0.85
            },
            timestamp=datetime.utcnow() - timedelta(hours=2)
        )
    ]

@pytest.fixture
def sample_contexts():
    return [
        GPTContext(
            id="ctx-1",
            user_id="user-1",
            is_active=True
        ),
        GPTContext(
            id="ctx-2",
            user_id="user-1",
            is_active=True
        )
    ]

@pytest.fixture
def sample_shared_contexts():
    source_gpt = GPTDefinition(id="gpt-1", category="TEACHER")
    target_gpt = GPTDefinition(id="gpt-2", category="STUDENT")
    
    return [
        SharedContext(
            id="sh-1",
            context_id="ctx-1",
            source_gpt=source_gpt,
            target_gpt=target_gpt,
            shared_data={"key": "value"},
            created_at=datetime.utcnow() - timedelta(hours=1)
        ),
        SharedContext(
            id="sh-2",
            context_id="ctx-1",
            source_gpt=target_gpt,
            target_gpt=source_gpt,
            shared_data={"key": "value2"},
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
    ]

async def test_record_recommendation_request(monitoring_service):
    """Test recording recommendation request metrics."""
    # Reset counters
    prom.REGISTRY.unregister(prom.REGISTRY._names_to_collectors['gpt_recommendation_requests_total'])
    prom.REGISTRY.unregister(prom.REGISTRY._names_to_collectors['gpt_recommendation_latency_seconds'])

    await monitoring_service.record_recommendation_request(
        user_id="user-1",
        category="TEACHER",
        duration=0.5
    )

    # Verify metrics were recorded
    counter = prom.REGISTRY._names_to_collectors['gpt_recommendation_requests_total']
    assert counter._value.get() == 1

    histogram = prom.REGISTRY._names_to_collectors['gpt_recommendation_latency_seconds']
    assert histogram._sum.get() > 0

async def test_record_context_switch(monitoring_service, mock_db, sample_contexts):
    """Test recording context switch metrics."""
    # Mock database query
    mock_db.query.return_value.filter.return_value.count.return_value = len(sample_contexts)

    await monitoring_service.record_context_switch(
        user_id="user-1",
        source_category="TEACHER",
        target_category="STUDENT"
    )

    # Verify metrics
    counter = prom.REGISTRY._names_to_collectors['gpt_context_switches_total']
    assert counter._value.get() == 1

    gauge = prom.REGISTRY._names_to_collectors['gpt_active_contexts']
    assert gauge._value.get() == len(sample_contexts)

async def test_update_gpt_performance_metrics(
    monitoring_service,
    mock_db,
    sample_metrics
):
    """Test updating GPT performance metrics."""
    # Mock database query
    mock_db.query.return_value.filter.return_value.all.return_value = sample_metrics

    await monitoring_service.update_gpt_performance_metrics("gpt-1")

    # Verify metrics
    gauge = prom.REGISTRY._names_to_collectors['gpt_performance_score']
    accuracy_value = gauge.labels(gpt_id="gpt-1", metric_type="accuracy")._value.get()
    assert 0.8 <= accuracy_value <= 0.85

async def test_get_active_contexts_count_cached(monitoring_service, mock_redis):
    """Test getting active contexts count from cache."""
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Set up cache hit
        mock_redis.get.return_value = b"2"
        
        count = await monitoring_service.get_active_contexts_count("user-1")
        assert count == 2
        mock_redis.get.assert_called_once()
        mock_redis.setex.assert_not_called()

async def test_get_active_contexts_count_uncached(
    monitoring_service,
    mock_db,
    mock_redis,
    sample_contexts
):
    """Test getting active contexts count from database."""
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Set up cache miss
        mock_redis.get.return_value = None
        mock_db.query.return_value.filter.return_value.count.return_value = len(sample_contexts)
        
        count = await monitoring_service.get_active_contexts_count("user-1")
        assert count == len(sample_contexts)
        mock_redis.setex.assert_called_once()

async def test_get_performance_summary(
    monitoring_service,
    mock_db,
    sample_metrics
):
    """Test getting performance summary."""
    # Mock database query
    mock_db.query.return_value.filter.return_value.all.return_value = sample_metrics

    summary = await monitoring_service.get_performance_summary("gpt-1")
    
    assert "accuracy" in summary
    assert "response_time" in summary
    assert "satisfaction" in summary
    assert summary["total_interactions"] == len(sample_metrics)
    assert 0.8 <= summary["accuracy"] <= 0.85

@pytest.mark.parametrize("time_range,delta", [
    ("24h", timedelta(days=1)),
    ("7d", timedelta(days=7)),
    ("30d", timedelta(days=30))
])
async def test_get_context_sharing_metrics_time_ranges(
    monitoring_service,
    mock_db,
    mock_redis,
    sample_shared_contexts,
    time_range,
    delta
):
    """Test getting context sharing metrics for different time ranges."""
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Set up cache miss
        mock_redis.get.return_value = None
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = sample_shared_contexts
        
        metrics = await monitoring_service.get_context_sharing_metrics(
            user_id="user-1",
            time_range=time_range
        )
        
        # Verify time range was properly applied
        assert metrics["total_shares"] == len(sample_shared_contexts)
        # Verify cache was set
        mock_redis.setex.assert_called_once()
        # Verify average frequency calculation
        expected_frequency = len(sample_shared_contexts) / delta.days
        assert abs(metrics["average_sharing_frequency"] - expected_frequency) < 0.01

async def test_get_context_sharing_metrics_cached(
    monitoring_service,
    mock_redis
):
    """Test getting context sharing metrics from cache."""
    cached_metrics = {
        "total_shares": 2,
        "category_pairs": {"TEACHER->STUDENT": 1, "STUDENT->TEACHER": 1},
        "most_shared_gpts": {"gpt-1": 2, "gpt-2": 2},
        "average_sharing_frequency": 2.0
    }
    
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Set up cache hit
        mock_redis.get.return_value = str(cached_metrics).encode()
        
        metrics = await monitoring_service.get_context_sharing_metrics(
            user_id="user-1",
            time_range="24h"
        )
        
        assert metrics == cached_metrics
        mock_redis.get.assert_called_once()
        mock_redis.setex.assert_not_called()

async def test_record_context_sharing(monitoring_service):
    """Test recording context sharing latency metrics."""
    # Reset histogram
    prom.REGISTRY.unregister(prom.REGISTRY._names_to_collectors['gpt_context_sharing_latency_seconds'])

    # Test recording sharing latency
    await monitoring_service.record_context_sharing(
        source_category="TEACHER",
        target_category="STUDENT",
        duration=0.75
    )

    # Verify metrics were recorded
    histogram = prom.REGISTRY._names_to_collectors['gpt_context_sharing_latency_seconds']
    assert histogram._sum.get() > 0
    
    # Verify labels
    labels = {'source_category': 'TEACHER', 'target_category': 'STUDENT'}
    assert histogram.labels(**labels)._sum.get() == 0.75

async def test_get_performance_summary_cached(monitoring_service, mock_redis, sample_metrics):
    """Test getting performance summary from cache."""
    cached_summary = {
        "accuracy": 0.825,
        "response_time": 0.725,
        "satisfaction": 0.875,
        "total_interactions": 2
    }
    
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Set up cache hit
        mock_redis.get.return_value = str(cached_summary).encode()
        
        summary = await monitoring_service.get_performance_summary("gpt-1")
        
        assert summary == cached_summary
        mock_redis.get.assert_called_once()
        mock_redis.setex.assert_not_called()

async def test_get_performance_summary_cache_miss(
    monitoring_service,
    mock_db,
    mock_redis,
    sample_metrics
):
    """Test getting performance summary with cache miss."""
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Set up cache miss
        mock_redis.get.return_value = None
        mock_db.query.return_value.filter.return_value.all.return_value = sample_metrics
        
        summary = await monitoring_service.get_performance_summary("gpt-1")
        
        assert summary["total_interactions"] == len(sample_metrics)
        mock_redis.setex.assert_called_once()
        # Verify the cached data matches computed summary
        cached_data = eval(mock_redis.setex.call_args[0][2])
        assert cached_data == summary

@pytest.mark.parametrize("redis_error", [
    ConnectionError("Connection refused"),
    TimeoutError("Connection timeout"),
    Exception("Unknown Redis error")
])
async def test_redis_connection_failures(
    monitoring_service,
    mock_db,
    mock_redis,
    sample_metrics,
    redis_error
):
    """Test handling of Redis connection failures."""
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Simulate Redis failure
        mock_redis.get.side_effect = redis_error
        mock_redis.setex.side_effect = redis_error
        
        # Mock database response for fallback
        mock_db.query.return_value.filter.return_value.all.return_value = sample_metrics
        
        # Test performance summary fallback
        summary = await monitoring_service.get_performance_summary("gpt-1")
        assert summary["total_interactions"] == len(sample_metrics)
        
        # Test active contexts count fallback
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        count = await monitoring_service.get_active_contexts_count("user-1")
        assert count == 2
        
        # Verify Redis was attempted but failed
        mock_redis.get.assert_called()
        mock_redis.setex.assert_not_called()  # Should not try to cache when Redis fails

async def test_concurrent_cache_access(
    monitoring_service,
    mock_db,
    mock_redis,
    sample_metrics
):
    """Test concurrent access to cached data."""
    with patch.object(monitoring_service, 'redis', mock_redis):
        # Simulate slow database query
        async def slow_db_query(*args, **kwargs):
            await asyncio.sleep(0.1)
            return sample_metrics
        
        mock_db.query.return_value.filter.return_value.all.side_effect = slow_db_query
        
        # First access - cache miss
        mock_redis.get.return_value = None
        
        # Launch multiple concurrent requests
        tasks = []
        for _ in range(5):
            tasks.append(
                monitoring_service.get_performance_summary("gpt-1")
            )
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks)
        
        # Verify all requests got the same result
        expected_summary = results[0]
        assert all(result == expected_summary for result in results)
        
        # Verify cache was only set once
        assert mock_redis.setex.call_count == 1
        
        # Verify database was only queried once
        assert mock_db.query.call_count == 1

async def test_concurrent_metric_updates(monitoring_service):
    """Test concurrent updates to Prometheus metrics."""
    # Reset counters
    prom.REGISTRY.unregister(prom.REGISTRY._names_to_collectors['gpt_recommendation_requests_total'])
    prom.REGISTRY.unregister(prom.REGISTRY._names_to_collectors['gpt_recommendation_latency_seconds'])
    
    # Launch multiple concurrent metric updates
    tasks = []
    for i in range(5):
        tasks.append(
            monitoring_service.record_recommendation_request(
                user_id=f"user-{i}",
                category="TEACHER",
                duration=0.5
            )
        )
    
    await asyncio.gather(*tasks)
    
    # Verify metrics were recorded correctly
    counter = prom.REGISTRY._names_to_collectors['gpt_recommendation_requests_total']
    assert counter._value.get() == 5
    
    histogram = prom.REGISTRY._names_to_collectors['gpt_recommendation_latency_seconds']
    assert histogram._sum.get() == 2.5  # 5 requests * 0.5 duration

def test_error_handling(monitoring_service, mock_db):
    """Test error handling in monitoring service."""
    # Mock database error
    mock_db.query.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc:
        monitoring_service.get_performance_summary("gpt-1")
    assert "Error getting performance summary" in str(exc.value) 