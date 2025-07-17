"""
Performance benchmark tests for the load balancer.

This module contains tests to measure and verify the performance
characteristics of the load balancer under various conditions.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import numpy as np

from app.core.load_balancer import (
    GlobalLoadBalancer,
    RequestType,
    Region,
    RoutingStrategy
)
from app.core.regional_failover import RegionalFailoverManager

@pytest.fixture
async def load_balancer():
    """Create and initialize a load balancer instance."""
    failover_manager = RegionalFailoverManager()
    lb = GlobalLoadBalancer(failover_manager)
    await lb.initialize()
    return lb

class TestLoadBalancerPerformance:
    """Performance tests for the load balancer."""
    
    @pytest.mark.asyncio
    async def test_routing_latency(self, load_balancer):
        """Test routing decision latency."""
        latencies = []
        
        for _ in range(1000):
            start_time = time.perf_counter()
            await load_balancer.get_target_region(RequestType.LOW_LATENCY)
            latency = time.perf_counter() - start_time
            latencies.append(latency)
            
        avg_latency = statistics.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)
        
        # Verify performance meets requirements
        assert avg_latency < 0.001  # Average under 1ms
        assert p95_latency < 0.002  # 95th percentile under 2ms
        assert p99_latency < 0.005  # 99th percentile under 5ms
        
    @pytest.mark.asyncio
    async def test_concurrent_routing(self, load_balancer):
        """Test performance under concurrent load."""
        async def make_request():
            start_time = time.perf_counter()
            region = await load_balancer.get_target_region(RequestType.HIGH_THROUGHPUT)
            latency = time.perf_counter() - start_time
            return region, latency
            
        # Simulate 1000 concurrent requests
        tasks = [make_request() for _ in range(1000)]
        results = await asyncio.gather(*tasks)
        
        latencies = [lat for _, lat in results]
        regions = [reg for reg, _ in results]
        
        # Verify latency under load
        avg_latency = statistics.mean(latencies)
        assert avg_latency < 0.002  # Average under 2ms under load
        
        # Verify load distribution
        region_counts = {region: regions.count(region) for region in set(regions)}
        total_requests = len(regions)
        distribution = {r: count/total_requests for r, count in region_counts.items()}
        
        # No region should handle more than 40% of requests
        assert all(ratio < 0.4 for ratio in distribution.values())
        
    @pytest.mark.asyncio
    async def test_adaptive_routing_performance(self, load_balancer):
        """Test performance of adaptive routing strategy."""
        load_balancer.routing_strategy = RoutingStrategy.ADAPTIVE
        
        # Simulate varying load conditions
        for region in Region:
            load_balancer.region_stats[region]['resource_usage'] = {
                'cpu': np.random.uniform(0.3, 0.8),
                'memory': np.random.uniform(0.4, 0.7),
                'network': np.random.uniform(0.2, 0.6)
            }
            
        latencies = []
        regions = []
        
        # Make 1000 routing decisions
        for _ in range(1000):
            start_time = time.perf_counter()
            region = await load_balancer.get_target_region(RequestType.ADAPTIVE)
            latency = time.perf_counter() - start_time
            
            latencies.append(latency)
            regions.append(region)
            
            # Randomly vary resource usage
            for r in Region:
                load_balancer.region_stats[r]['resource_usage']['cpu'] += np.random.uniform(-0.1, 0.1)
                load_balancer.region_stats[r]['resource_usage']['cpu'] = max(0.1, min(0.9, load_balancer.region_stats[r]['resource_usage']['cpu']))
                
        # Verify performance
        avg_latency = statistics.mean(latencies)
        assert avg_latency < 0.002  # Adaptive routing under 2ms
        
        # Verify load distribution adapts to resource usage
        region_counts = {region: regions.count(region) for region in set(regions)}
        high_load_regions = [r for r in Region if load_balancer.region_stats[r]['resource_usage']['cpu'] > 0.7]
        
        # Regions under high load should receive fewer requests
        for region in high_load_regions:
            assert region_counts.get(region, 0) < total_requests * 0.3
            
    @pytest.mark.asyncio
    async def test_geographic_routing_performance(self, load_balancer):
        """Test performance of geographic routing."""
        load_balancer.routing_strategy = RoutingStrategy.GEOGRAPHIC
        
        # Test IPs from different regions
        test_ips = {
            Region.NORTH_AMERICA: "72.229.28.185",  # US
            Region.EUROPE: "88.156.136.38",         # EU
            Region.ASIA: "202.51.76.154",           # Asia
            Region.SOUTH_AMERICA: "200.55.108.142"  # South America
        }
        
        latencies = []
        correct_regions = 0
        total_tests = len(test_ips) * 100
        
        for expected_region, ip in test_ips.items():
            for _ in range(100):
                start_time = time.perf_counter()
                region = await load_balancer.get_target_region(
                    RequestType.LOW_LATENCY,
                    ip_address=ip
                )
                latency = time.perf_counter() - start_time
                
                latencies.append(latency)
                if region == expected_region:
                    correct_regions += 1
                    
        # Verify performance
        avg_latency = statistics.mean(latencies)
        assert avg_latency < 0.005  # Geographic routing under 5ms
        
        # Verify accuracy
        accuracy = correct_regions / total_tests
        assert accuracy > 0.9  # Over 90% accuracy
        
    @pytest.mark.asyncio
    async def test_failover_performance(self, load_balancer):
        """Test performance during failover scenarios."""
        # Simulate region failure
        failed_region = Region.EUROPE
        load_balancer.circuit_breakers[failed_region].record_failure()
        load_balancer.circuit_breakers[failed_region].record_failure()
        load_balancer.circuit_breakers[failed_region].record_failure()
        
        latencies = []
        regions = []
        
        # Test routing during failure
        for _ in range(1000):
            start_time = time.perf_counter()
            region = await load_balancer.get_target_region(RequestType.LOW_LATENCY)
            latency = time.perf_counter() - start_time
            
            latencies.append(latency)
            regions.append(region)
            
        # Verify performance during failover
        avg_latency = statistics.mean(latencies)
        assert avg_latency < 0.002  # Failover routing under 2ms
        
        # Verify failed region is not used
        assert failed_region not in regions
        
        # Verify load is redistributed
        remaining_regions = len(Region) - 1
        expected_requests = len(regions) / remaining_regions
        region_counts = {region: regions.count(region) for region in set(regions)}
        
        # Each remaining region should handle approximately equal load
        for region, count in region_counts.items():
            assert abs(count - expected_requests) < expected_requests * 0.2
            
    @pytest.mark.asyncio
    async def test_resource_monitoring_performance(self, load_balancer):
        """Test performance of resource monitoring."""
        start_time = time.perf_counter()
        
        # Monitor resources for 10 seconds
        monitoring_latencies = []
        for _ in range(10):
            monitor_start = time.perf_counter()
            await load_balancer._monitor_resources()
            latency = time.perf_counter() - monitor_start
            monitoring_latencies.append(latency)
            await asyncio.sleep(1)
            
        # Verify monitoring performance
        avg_monitoring_latency = statistics.mean(monitoring_latencies)
        assert avg_monitoring_latency < 0.1  # Resource monitoring under 100ms
        
        # Verify monitoring doesn't impact routing
        routing_latencies = []
        for _ in range(100):
            route_start = time.perf_counter()
            await load_balancer.get_target_region(RequestType.LOW_LATENCY)
            latency = time.perf_counter() - route_start
            routing_latencies.append(latency)
            
        avg_routing_latency = statistics.mean(routing_latencies)
        assert avg_routing_latency < 0.002  # Routing still under 2ms 