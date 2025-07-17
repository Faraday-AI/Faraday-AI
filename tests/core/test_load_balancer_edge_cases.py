"""
Edge Case Tests for the Global Load Balancer

This module contains tests for edge cases and boundary conditions
in the load balancing features.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np
from typing import List, Dict, Any

from app.core.load_balancer import (
    GlobalLoadBalancer,
    LoadWindow,
    RequestType,
    Region,
    RegionCost,
    CircuitBreaker
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

class TestLoadBalancerEdgeCases:
    """Edge case tests for the load balancer."""
    
    @pytest.mark.asyncio
    async def test_empty_region_selection(self, load_balancer):
        """Test region selection with no available regions."""
        # Remove all regions
        load_balancer.region_stats = {}
        
        # Attempt to get target region
        with pytest.raises(ValueError, match="No regions available"):
            await load_balancer.get_target_region(RequestType.LOW_LATENCY)
    
    @pytest.mark.asyncio
    async def test_all_regions_unhealthy(self, load_balancer):
        """Test when all regions are unhealthy."""
        # Mark all regions as unhealthy
        for region in Region:
            load_balancer.region_stats[region]['health'] = 'unhealthy'
            load_balancer.circuit_breakers[region].state = CircuitBreaker.State.OPEN
        
        # Attempt to get target region
        with pytest.raises(ValueError, match="No healthy regions available"):
            await load_balancer.get_target_region(RequestType.LOW_LATENCY)
    
    @pytest.mark.asyncio
    async def test_extreme_resource_usage(self, load_balancer):
        """Test routing with extreme resource usage values."""
        # Set extreme resource usage
        for region in Region:
            load_balancer.region_stats[region]['resource_usage'] = {
                'cpu': 1.5,  # Over 100%
                'memory': -0.1,  # Negative usage
                'network': 2.0  # Over 100%
            }
        
        # Verify routing still works
        region = await load_balancer.get_target_region(RequestType.HIGH_THROUGHPUT)
        assert region in Region
    
    @pytest.mark.asyncio
    async def test_load_window_boundaries(self, load_balancer):
        """Test load window behavior at size boundaries."""
        window = LoadWindow()
        
        # Test minimum size
        for _ in range(100):
            window.adjust_size(0.0)  # Minimum load
        assert window.size == window.MIN_SIZE
        
        # Test maximum size
        for _ in range(100):
            window.adjust_size(1.0)  # Maximum load
        assert window.size == window.MAX_SIZE
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_extreme_failures(self, load_balancer):
        """Test circuit breaker with extreme failure patterns."""
        breaker = load_balancer.circuit_breakers[Region.NORTH_AMERICA]
        
        # Rapid failures
        for _ in range(1000):
            breaker.record_failure()
        assert breaker.state == CircuitBreaker.State.OPEN
        
        # Rapid successes
        for _ in range(1000):
            breaker.record_success()
        assert breaker.state == CircuitBreaker.State.CLOSED
    
    @pytest.mark.asyncio
    async def test_predictive_scoring_edge_cases(self, load_balancer):
        """Test predictive scoring with edge case data."""
        # Empty historical data
        for region in Region:
            load_balancer.region_stats[region]['hourly_load'] = {}
        
        scores = await load_balancer._get_predictive_scores()
        assert all(0 <= score <= 1 for score in scores.values())
        
        # Extreme historical data
        for region in Region:
            load_balancer.region_stats[region]['hourly_load'] = {
                hour: [2.0] * 24 for hour in range(24)  # All hours at 200% load
            }
        
        scores = await load_balancer._get_predictive_scores()
        assert all(0 <= score <= 1 for score in scores.values())
    
    @pytest.mark.asyncio
    async def test_cost_efficiency_edge_cases(self, load_balancer):
        """Test cost efficiency calculations with edge cases."""
        # Zero costs
        for region in Region:
            load_balancer.region_stats[region]['cost'] = RegionCost(0.0, 0.0, 0.0)
        
        efficiency = load_balancer._calculate_cost_efficiency(Region.NORTH_AMERICA)
        assert 0 <= efficiency <= 1
        
        # Extreme costs
        for region in Region:
            load_balancer.region_stats[region]['cost'] = RegionCost(1000.0, 1000.0, 1000.0)
        
        efficiency = load_balancer._calculate_cost_efficiency(Region.NORTH_AMERICA)
        assert 0 <= efficiency <= 1
    
    @pytest.mark.asyncio
    async def test_concurrent_edge_cases(self, load_balancer):
        """Test concurrent operations with edge cases."""
        async def make_request():
            return await load_balancer.get_target_region(RequestType.LOW_LATENCY)
        
        # Test with extreme concurrency
        tasks = [make_request() for _ in range(1000)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all results are either valid regions or expected errors
        for result in results:
            if isinstance(result, Exception):
                assert isinstance(result, ValueError)
            else:
                assert result in Region
    
    @pytest.mark.asyncio
    async def test_resource_monitoring_edge_cases(self, load_balancer):
        """Test resource monitoring with edge cases."""
        # Simulate monitoring failure
        with patch('psutil.cpu_percent', side_effect=Exception("CPU monitoring failed")):
            await load_balancer._monitor_resources()
            # Verify system continues to function
            assert await load_balancer.get_target_region(RequestType.LOW_LATENCY) in Region
    
    @pytest.mark.asyncio
    async def test_latency_weighting_edge_cases(self, load_balancer):
        """Test latency weighting with edge cases."""
        # Zero latencies
        for region in Region:
            load_balancer.region_stats[region]['latency'] = [0.0] * 10
        
        await load_balancer._update_latency_weights()
        assert all(0 <= w <= 1 for w in load_balancer.region_weights.values())
        
        # Extreme latencies
        for region in Region:
            load_balancer.region_stats[region]['latency'] = [1000.0] * 10
        
        await load_balancer._update_latency_weights()
        assert all(0 <= w <= 1 for w in load_balancer.region_weights.values())
    
    @pytest.mark.asyncio
    async def test_request_type_edge_cases(self, load_balancer):
        """Test request type handling with edge cases."""
        # Test with invalid request type
        with pytest.raises(ValueError, match="Invalid request type"):
            await load_balancer.get_target_region("INVALID_TYPE")
        
        # Test with None request type
        with pytest.raises(ValueError, match="Request type cannot be None"):
            await load_balancer.get_target_region(None)
    
    @pytest.mark.asyncio
    async def test_region_stats_edge_cases(self, load_balancer):
        """Test region stats handling with edge cases."""
        # Test with missing stats
        for region in Region:
            load_balancer.region_stats[region] = {}
        
        # Verify system handles missing stats gracefully
        region = await load_balancer.get_target_region(RequestType.LOW_LATENCY)
        assert region in Region
        
        # Test with invalid stats
        for region in Region:
            load_balancer.region_stats[region] = {
                'health': 'invalid',
                'latency': 'not a number',
                'requests': -1
            }
        
        # Verify system handles invalid stats gracefully
        region = await load_balancer.get_target_region(RequestType.LOW_LATENCY)
        assert region in Region 