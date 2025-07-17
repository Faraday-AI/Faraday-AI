"""
Tests for the Global Load Balancer

This module contains tests for the load balancing features, including:
- Adaptive load window
- Resource-aware routing
- Latency-based weighting
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import psutil

from app.core.load_balancer import (
    GlobalLoadBalancer,
    LoadWindow,
    RequestType,
    Region,
    RegionCost
)
from app.core.regional_failover import RegionalFailoverManager

@pytest.fixture
def failover_manager():
    """Create a mock failover manager."""
    manager = Mock(spec=RegionalFailoverManager)
    manager.check_region_health.return_value = {
        'status': 'healthy',
        'latency': 0.1,
        'errors': 0
    }
    return manager

@pytest.fixture
def load_balancer(failover_manager):
    """Create a load balancer instance."""
    return GlobalLoadBalancer(failover_manager)

@pytest.fixture
def load_window():
    """Create a load window instance."""
    return LoadWindow()

@pytest.mark.asyncio
async def test_load_window_initialization(load_window):
    """Test load window initialization."""
    assert load_window.min_size == 10
    assert load_window.max_size == 1000
    assert load_window.current_size == 100
    assert len(load_window.metrics) == 0

@pytest.mark.asyncio
async def test_load_window_metrics(load_window):
    """Test adding metrics to the load window."""
    # Add metrics
    for i in range(5):
        load_window.add_metric({
            'latency': i * 0.1,
            'error': i % 2 == 0,
            'timestamp': time.time()
        })
    
    assert len(load_window.metrics) == 5
    
    # Test window size adjustment
    load_window.adjust_size(0.9)  # High load
    assert load_window.current_size == 50
    
    load_window.adjust_size(0.2)  # Low load
    assert load_window.current_size == 100

@pytest.mark.asyncio
async def test_load_window_stats(load_window):
    """Test calculating statistics from the load window."""
    # Add metrics
    for i in range(5):
        load_window.add_metric({
            'latency': i * 0.1,
            'error': i % 2 == 0,
            'timestamp': time.time()
        })
    
    stats = load_window.get_stats()
    assert 'avg_latency' in stats
    assert 'error_rate' in stats
    assert 'throughput' in stats

@pytest.mark.asyncio
async def test_resource_monitoring(load_balancer):
    """Test resource monitoring."""
    with patch('psutil.cpu_percent', return_value=50.0), \
         patch('psutil.virtual_memory') as mock_memory, \
         patch('psutil.net_io_counters') as mock_network:
        
        mock_memory.return_value.percent = 60.0
        mock_network.return_value.bytes_sent = 1000
        mock_network.return_value.bytes_recv = 2000
        
        # Run monitoring
        await load_balancer._monitor_resources()
        
        # Check stats
        for region in Region:
            stats = load_balancer.region_stats[region]
            assert stats['resource_usage']['cpu'] == 50.0
            assert stats['resource_usage']['memory'] == 60.0
            assert stats['resource_usage']['network'] == 3000

@pytest.mark.asyncio
async def test_latency_weighting(load_balancer):
    """Test latency-based weighting."""
    # Add some latency data
    for region in Region:
        stats = load_balancer.region_stats[region]
        stats['latency'] = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    # Run weight update
    await load_balancer._update_latency_weights()
    
    # Check weights
    for region in Region:
        stats = load_balancer.region_stats[region]
        assert 'latency_weights' in stats
        assert stats['latency_weights']['avg'] == 0.3
        assert stats['latency_weights']['std_dev'] > 0

@pytest.mark.asyncio
async def test_region_selection(load_balancer):
    """Test region selection based on request type."""
    # Set up test data
    for region in Region:
        stats = load_balancer.region_stats[region]
        stats['health_score'] = 1.0
        stats['resource_usage'] = {
            'cpu': 50.0,
            'memory': 60.0,
            'network': 3000
        }
        stats['latency_weights'] = {
            'avg': 0.1,
            'std_dev': 0.01,
            'last_update': time.time()
        }
    
    # Test different request types
    for request_type in RequestType:
        region = await load_balancer.get_target_region(request_type)
        assert region in Region
        assert isinstance(region, Region)

@pytest.mark.asyncio
async def test_circuit_breaker(load_balancer):
    """Test circuit breaker functionality."""
    # Simulate failures
    for _ in range(5):
        load_balancer.circuit_breakers[Region.NORTH_AMERICA].record_failure()
    
    # Check if circuit is open
    assert not load_balancer.circuit_breakers[Region.NORTH_AMERICA].can_attempt()
    
    # Wait for reset timeout
    await asyncio.sleep(61)  # Default timeout is 60 seconds
    
    # Check if circuit is half-open
    assert load_balancer.circuit_breakers[Region.NORTH_AMERICA].can_attempt()
    
    # Record success
    load_balancer.circuit_breakers[Region.NORTH_AMERICA].record_success()
    
    # Check if circuit is closed
    assert load_balancer.circuit_breakers[Region.NORTH_AMERICA].can_attempt()

@pytest.mark.asyncio
async def test_error_handling(load_balancer):
    """Test error handling in load balancer."""
    # Simulate monitoring error
    with patch('psutil.cpu_percent', side_effect=Exception("Test error")):
        await load_balancer._monitor_resources()
        # Should not raise exception
    
    # Simulate weight update error
    with patch('statistics.mean', side_effect=Exception("Test error")):
        await load_balancer._update_latency_weights()
        # Should not raise exception
    
    # Test region selection with no healthy regions
    for region in Region:
        load_balancer.circuit_breakers[region].record_failure()
    
    region = await load_balancer.get_target_region(RequestType.LOW_LATENCY)
    assert region == Region.NORTH_AMERICA  # Should fall back to primary

@pytest.mark.asyncio
async def test_performance_metrics(load_balancer):
    """Test performance metrics collection."""
    # Record some operations
    for _ in range(10):
        region = await load_balancer.get_target_region(RequestType.LOW_LATENCY)
        assert region in Region
    
    # Check metrics
    for region in Region:
        stats = load_balancer.region_stats[region]
        assert 'requests' in stats
        assert 'latency' in stats
        assert 'health_score' in stats

@pytest.mark.asyncio
async def test_adaptive_load_window(load_window):
    """Test adaptive load window behavior."""
    # Test window size adjustment under different loads
    load_window.adjust_size(0.9)  # High load
    assert load_window.current_size == 50
    
    load_window.adjust_size(0.2)  # Low load
    assert load_window.current_size == 100
    
    # Test window size limits
    for _ in range(10):
        load_window.adjust_size(0.9)  # Keep reducing
    assert load_window.current_size >= load_window.min_size
    
    for _ in range(10):
        load_window.adjust_size(0.2)  # Keep increasing
    assert load_window.current_size <= load_window.max_size

@pytest.mark.asyncio
async def test_resource_aware_routing(load_balancer):
    """Test resource-aware routing decisions."""
    # Set up different resource usage scenarios
    resource_scenarios = [
        {'cpu': 20.0, 'memory': 30.0, 'network': 1000},  # Low usage
        {'cpu': 80.0, 'memory': 90.0, 'network': 5000},  # High usage
        {'cpu': 50.0, 'memory': 60.0, 'network': 3000}   # Medium usage
    ]
    
    for region in Region:
        for scenario in resource_scenarios:
            # Update resource usage
            load_balancer.region_stats[region]['resource_usage'] = scenario
            
            # Test routing for different request types
            region = await load_balancer.get_target_region(RequestType.HIGH_THROUGHPUT)
            assert region in Region
            
            # Verify resource-aware routing
            if scenario['cpu'] < 30 and scenario['memory'] < 40:
                # Should prefer low-usage regions for high throughput
                assert load_balancer.region_stats[region]['resource_usage']['cpu'] < 50
                assert load_balancer.region_stats[region]['resource_usage']['memory'] < 60

@pytest.mark.asyncio
async def test_latency_based_weighting(load_balancer):
    """Test latency-based weighting calculations."""
    # Set up different latency scenarios
    latency_scenarios = [
        [0.1, 0.2, 0.3],  # Low latency
        [0.5, 0.6, 0.7],  # Medium latency
        [1.0, 1.1, 1.2]   # High latency
    ]
    
    for region in Region:
        for latencies in latency_scenarios:
            # Update latency data
            load_balancer.region_stats[region]['latency'] = latencies
            
            # Run weight update
            await load_balancer._update_latency_weights()
            
            # Check weights
            stats = load_balancer.region_stats[region]
            assert 'latency_weights' in stats
            
            # Verify weight calculation
            avg_latency = mean(latencies)
            weight = 1.0 / (1.0 + avg_latency)
            assert abs(stats['latency_weights']['avg'] - avg_latency) < 0.01
            
            # Test routing with different latencies
            region = await load_balancer.get_target_region(RequestType.LOW_LATENCY)
            assert region in Region
            
            if avg_latency < 0.3:
                # Should prefer low-latency regions
                assert load_balancer.region_stats[region]['latency_weights']['avg'] < 0.5

@pytest.mark.asyncio
async def test_predictive_scoring(load_balancer):
    """Test predictive scoring based on historical data."""
    # Set up historical load data
    current_hour = datetime.now().hour
    for region in Region:
        stats = load_balancer.region_stats[region]
        stats['hourly_load'][current_hour] = [0.2, 0.3, 0.4]  # Sample loads
    
    # Update predictive scores
    await load_balancer._update_predictive_scores()
    
    # Check scores
    scores = await load_balancer._get_predictive_scores()
    for region in Region:
        assert region in scores
        assert 0 <= scores[region] <= 1.0
        
        # Verify score calculation
        stats = load_balancer.region_stats[region]
        avg_load = mean(stats['hourly_load'][current_hour])
        expected_score = 1.0 - avg_load
        assert abs(scores[region] - expected_score) < 0.01

@pytest.mark.asyncio
async def test_cost_efficiency(load_balancer):
    """Test cost efficiency calculations."""
    # Set up different cost scenarios
    cost_scenarios = [
        RegionCost(0.1, 0.05, 0.02),  # Low cost
        RegionCost(0.3, 0.15, 0.06),  # Medium cost
        RegionCost(0.5, 0.25, 0.10)   # High cost
    ]
    
    for region in Region:
        for cost in cost_scenarios:
            # Update cost data
            load_balancer.region_stats[region]['cost'] = cost
            
            # Calculate efficiency
            efficiency = load_balancer._calculate_cost_efficiency(region)
            assert 0 <= efficiency <= 1.0
            
            # Verify efficiency calculation
            total_cost = cost.compute_cost + cost.storage_cost + cost.network_cost
            expected_efficiency = 1.0 / (1.0 + total_cost)
            assert abs(efficiency - expected_efficiency) < 0.01
            
            # Test routing for cost-sensitive requests
            region = await load_balancer.get_target_region(RequestType.COST_SENSITIVE)
            assert region in Region
            
            if total_cost < 0.2:
                # Should prefer low-cost regions
                assert load_balancer.region_stats[region]['cost'].compute_cost < 0.3 