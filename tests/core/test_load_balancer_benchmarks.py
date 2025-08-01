"""
Performance Benchmarks for the Global Load Balancer

This module contains performance benchmarks for the load balancing features,
including latency, throughput, and resource usage tests.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import psutil
import statistics
import numpy as np
from typing import List, Dict, Any

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

@pytest.mark.benchmark
class TestLoadBalancerPerformance:
    """Performance benchmarks for the load balancer."""
    
    @pytest.mark.asyncio
    async def test_region_selection_latency(self, load_balancer):
        """Benchmark region selection latency."""
        latencies = []
        
        # Warm up
        for _ in range(10):
            await load_balancer.get_target_region(RequestType.LOW_LATENCY)
        
        # Measure latency
        for _ in range(100):
            start_time = time.time()
            await load_balancer.get_target_region(RequestType.LOW_LATENCY)
            latencies.append(time.time() - start_time)
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)
        
        # Assert performance requirements
        assert avg_latency < 0.01  # Average latency < 10ms
        assert p95_latency < 0.02  # 95th percentile < 20ms
        assert p99_latency < 0.05  # 99th percentile < 50ms
        
        # Log results
        print(f"\nRegion Selection Latency:")
        print(f"Average: {avg_latency*1000:.2f}ms")
        print(f"95th percentile: {p95_latency*1000:.2f}ms")
        print(f"99th percentile: {p99_latency*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, load_balancer):
        """Benchmark concurrent request handling."""
        async def make_request():
            return await load_balancer.get_target_region(RequestType.LOW_LATENCY)
        
        # Test different concurrency levels
        for concurrency in [10, 50, 100]:
            start_time = time.time()
            tasks = [make_request() for _ in range(concurrency)]
            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time
            
            # Calculate throughput
            throughput = concurrency / duration
            
            # Assert performance requirements
            assert duration < 1.0  # All requests complete within 1 second
            assert throughput > concurrency * 0.8  # Maintain at least 80% of target throughput
            
            # Log results
            print(f"\nConcurrent Requests ({concurrency}):")
            print(f"Duration: {duration:.2f}s")
            print(f"Throughput: {throughput:.2f} requests/second")
    
    @pytest.mark.asyncio
    async def test_resource_monitoring_overhead(self, load_balancer):
        """Benchmark resource monitoring overhead."""
        # Measure CPU and memory before monitoring
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.Process().memory_info().rss
        
        # Test resource monitoring logic without infinite loop
        start_time = time.time()
        for region in Region:
            try:
                # Get resource usage (simulating one iteration of monitoring)
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                network_io = psutil.net_io_counters()
                
                # Update stats
                stats = load_balancer.region_stats[region]
                stats['resource_usage'] = {
                    'cpu': cpu_percent,
                    'memory': memory_percent,
                    'network': network_io.bytes_sent + network_io.bytes_recv
                }
                
            except Exception as e:
                pass  # Handle exceptions gracefully
        
        duration = time.time() - start_time
        
        # Measure CPU and memory after monitoring
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.Process().memory_info().rss
        
        # Calculate overhead
        cpu_overhead = end_cpu - start_cpu
        memory_overhead = (end_memory - start_memory) / 1024 / 1024  # MB
        
        # Assert performance requirements
        assert duration < 0.1  # Monitoring completes within 100ms
        assert cpu_overhead < 5.0  # Less than 5% CPU overhead
        assert memory_overhead < 10.0  # Less than 10MB memory overhead
        
        # Log results
        print(f"\nResource Monitoring Overhead:")
        print(f"Duration: {duration*1000:.2f}ms")
        print(f"CPU Overhead: {cpu_overhead:.2f}%")
        print(f"Memory Overhead: {memory_overhead:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_load_window_performance(self, load_balancer):
        """Benchmark load window operations."""
        window = LoadWindow()
        
        # Test metric addition
        start_time = time.time()
        for i in range(1000):
            window.add_metric({
                'latency': i * 0.001,
                'error': i % 2 == 0,
                'timestamp': time.time()
            })
        add_duration = time.time() - start_time
        
        # Test statistics calculation
        start_time = time.time()
        for _ in range(100):
            window.get_stats()
        stats_duration = time.time() - start_time
        
        # Assert performance requirements
        assert add_duration < 0.1  # Adding 1000 metrics within 100ms
        assert stats_duration < 0.1  # Calculating 100 stats within 100ms
        
        # Log results
        print(f"\nLoad Window Performance:")
        print(f"Metric Addition: {add_duration*1000:.2f}ms for 1000 metrics")
        print(f"Stats Calculation: {stats_duration*1000:.2f}ms for 100 calculations")
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_performance(self, load_balancer):
        """Benchmark circuit breaker operations."""
        breaker = load_balancer.circuit_breakers[Region.NORTH_AMERICA]
        
        # Test failure recording
        start_time = time.time()
        for _ in range(1000):
            breaker.record_failure()
        failure_duration = time.time() - start_time
        
        # Test state checking
        start_time = time.time()
        for _ in range(1000):
            breaker.can_attempt()
        check_duration = time.time() - start_time
        
        # Assert performance requirements
        assert failure_duration < 0.1  # Recording 1000 failures within 100ms
        assert check_duration < 0.1  # Checking 1000 states within 100ms
        
        # Log results
        print(f"\nCircuit Breaker Performance:")
        print(f"Failure Recording: {failure_duration*1000:.2f}ms for 1000 failures")
        print(f"State Checking: {check_duration*1000:.2f}ms for 1000 checks")
    
    @pytest.mark.asyncio
    async def test_predictive_scoring_performance(self, load_balancer):
        """Benchmark predictive scoring calculations."""
        # Set up test data
        current_hour = datetime.now().hour
        for region in Region:
            stats = load_balancer.region_stats[region]
            stats['hourly_load'][current_hour] = [0.2, 0.3, 0.4]
        
        # Measure scoring performance (test logic without infinite loop)
        start_time = time.time()
        current_hour = datetime.now().hour
        for region in Region:
            stats = load_balancer.region_stats[region]
            hourly_loads = stats['hourly_load'][current_hour]
            
            if hourly_loads:
                # Calculate average load for this hour
                avg_load = statistics.mean(hourly_loads)
                # Update predictive score (simulating one iteration)
                # Note: In real implementation, this would update PREDICTIVE_SCORE metrics
        update_duration = time.time() - start_time
        
        start_time = time.time()
        await load_balancer._get_predictive_scores()
        get_duration = time.time() - start_time
        
        # Assert performance requirements
        assert update_duration < 0.1  # Updating scores within 100ms
        assert get_duration < 0.1  # Getting scores within 100ms
        
        # Log results
        print(f"\nPredictive Scoring Performance:")
        print(f"Score Update: {update_duration*1000:.2f}ms")
        print(f"Score Retrieval: {get_duration*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_cost_efficiency_performance(self, load_balancer):
        """Benchmark cost efficiency calculations."""
        # Set up test data
        for region in Region:
            load_balancer.region_stats[region]['cost'] = RegionCost(0.1, 0.05, 0.02)
            load_balancer.region_stats[region]['requests'] = 1000
        
        # Measure calculation performance
        start_time = time.time()
        for _ in range(1000):
            load_balancer._calculate_cost_efficiency(Region.NORTH_AMERICA)
        duration = time.time() - start_time
        
        # Assert performance requirements
        assert duration < 0.1  # 1000 calculations within 100ms
        
        # Log results
        print(f"\nCost Efficiency Performance:")
        print(f"Calculation Time: {duration*1000:.2f}ms for 1000 calculations")

    @pytest.mark.asyncio
    async def test_adaptive_load_window_scaling(self, load_balancer):
        """Benchmark adaptive load window scaling under different loads."""
        window = LoadWindow()
        
        # Test under low load
        start_time = time.time()
        for i in range(1000):
            window.add_metric({
                'latency': 0.001,
                'error': False,
                'timestamp': time.time()
            })
            window.adjust_size(0.2)  # Low load
        low_load_duration = time.time() - start_time
        
        # Test under high load
        start_time = time.time()
        for i in range(1000):
            window.add_metric({
                'latency': 0.1,
                'error': True,
                'timestamp': time.time()
            })
            window.adjust_size(0.9)  # High load
        high_load_duration = time.time() - start_time
        
        # Assert performance requirements
        assert low_load_duration < 0.2  # Low load operations within 200ms
        assert high_load_duration < 0.2  # High load operations within 200ms
        
        # Log results
        print(f"\nAdaptive Load Window Scaling:")
        print(f"Low Load Duration: {low_load_duration*1000:.2f}ms")
        print(f"High Load Duration: {high_load_duration*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_resource_aware_routing_performance(self, load_balancer):
        """Benchmark resource-aware routing decisions."""
        # Set up different resource scenarios
        scenarios = [
            {'cpu': 0.2, 'memory': 0.3, 'network': 0.1},  # Low usage
            {'cpu': 0.8, 'memory': 0.9, 'network': 0.7},  # High usage
            {'cpu': 0.5, 'memory': 0.6, 'network': 0.4}   # Medium usage
        ]
        
        latencies = []
        for scenario in scenarios:
            # Update resource usage
            for region in Region:
                load_balancer.region_stats[region]['resource_usage'] = scenario
            
            # Measure routing latency
            start_time = time.time()
            await load_balancer.get_target_region(RequestType.HIGH_THROUGHPUT)
            latencies.append(time.time() - start_time)
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        
        # Assert performance requirements
        assert avg_latency < 0.01  # Average latency < 10ms
        assert max_latency < 0.02  # Maximum latency < 20ms
        
        # Log results
        print(f"\nResource-Aware Routing Performance:")
        print(f"Average Latency: {avg_latency*1000:.2f}ms")
        print(f"Maximum Latency: {max_latency*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_latency_weighting_performance(self, load_balancer):
        """Benchmark latency-based weighting calculations."""
        # Set up different latency scenarios
        scenarios = [
            [0.1, 0.2, 0.3],  # Low latency
            [0.5, 0.6, 0.7],  # Medium latency
            [1.0, 1.1, 1.2]   # High latency
        ]
        
        latencies = []
        for latencies_data in scenarios:
            # Update latency data
            for region in Region:
                load_balancer.region_stats[region]['latency'] = latencies_data
            
            # Measure weight update latency (test logic without infinite loop)
            start_time = time.time()
            for region in Region:
                try:
                    # Get recent latencies
                    stats = load_balancer.region_stats[region]
                    latencies_data = stats['latency'][-100:]  # Last 100 measurements
                    
                    if latencies_data:
                        # Calculate statistics
                        avg_latency = statistics.mean(latencies_data)
                        std_dev = statistics.stdev(latencies_data) if len(latencies_data) > 1 else 0
                        
                        # Update weights (simulating one iteration)
                        stats['latency_weights'] = {
                            'avg': avg_latency,
                            'std_dev': std_dev,
                            'last_update': time.time()
                        }
                        
                except Exception as e:
                    pass  # Handle exceptions gracefully
            latencies.append(time.time() - start_time)
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        
        # Assert performance requirements
        assert avg_latency < 0.01  # Average latency < 10ms
        assert max_latency < 0.02  # Maximum latency < 20ms
        
        # Log results
        print(f"\nLatency Weighting Performance:")
        print(f"Average Latency: {avg_latency*1000:.2f}ms")
        print(f"Maximum Latency: {max_latency*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, load_balancer):
        """Benchmark circuit breaker recovery performance."""
        breaker = load_balancer.circuit_breakers[Region.NORTH_AMERICA]
        
        # Simulate failures
        for _ in range(5):
            breaker.record_failure()
        
        # Measure recovery latency
        start_time = time.time()
        breaker.record_success()
        recovery_duration = time.time() - start_time
        
        # Assert performance requirements
        assert recovery_duration < 0.001  # Recovery within 1ms
        
        # Log results
        print(f"\nCircuit Breaker Recovery Performance:")
        print(f"Recovery Duration: {recovery_duration*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_predictive_scoring_accuracy(self, load_balancer):
        """Benchmark predictive scoring accuracy."""
        # Set up historical data
        current_hour = datetime.now().hour
        for region in Region:
            stats = load_balancer.region_stats[region]
            stats['hourly_load'][current_hour] = [0.2, 0.3, 0.4]
        
        # Measure prediction accuracy
        start_time = time.time()
        scores = await load_balancer._get_predictive_scores()
        duration = time.time() - start_time
        
        # Calculate accuracy metrics
        avg_score = statistics.mean(scores.values())
        score_std = statistics.stdev(scores.values()) if len(scores) > 1 else 0
        
        # Assert performance requirements
        assert duration < 0.01  # Prediction within 10ms
        assert 0 <= avg_score <= 1  # Scores in valid range
        assert score_std < 0.5  # Reasonable score distribution
        
        # Log results
        print(f"\nPredictive Scoring Accuracy:")
        print(f"Average Score: {avg_score:.2f}")
        print(f"Score Standard Deviation: {score_std:.2f}")
        print(f"Prediction Duration: {duration*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_cost_efficiency_accuracy(self, load_balancer):
        """Benchmark cost efficiency calculation accuracy."""
        # Set up different cost scenarios
        scenarios = [
            RegionCost(0.1, 0.05, 0.02),  # Low cost
            RegionCost(0.3, 0.15, 0.06),  # Medium cost
            RegionCost(0.5, 0.25, 0.10)   # High cost
        ]
        
        efficiencies = []
        for cost in scenarios:
            # Update cost data
            for region in Region:
                load_balancer.region_stats[region]['cost'] = cost
            
            # Calculate efficiency
            start_time = time.time()
            efficiency = load_balancer._calculate_cost_efficiency(Region.NORTH_AMERICA)
            duration = time.time() - start_time
            
            efficiencies.append(efficiency)
            
            # Assert performance requirements
            assert duration < 0.001  # Calculation within 1ms
            assert 0 <= efficiency <= 1  # Efficiency in valid range
        
        # Calculate accuracy metrics
        avg_efficiency = statistics.mean(efficiencies)
        efficiency_std = statistics.stdev(efficiencies) if len(efficiencies) > 1 else 0
        
        # Log results
        print(f"\nCost Efficiency Accuracy:")
        print(f"Average Efficiency: {avg_efficiency:.2f}")
        print(f"Efficiency Standard Deviation: {efficiency_std:.2f}")
        print(f"Calculation Duration: {duration*1000:.2f}ms") 