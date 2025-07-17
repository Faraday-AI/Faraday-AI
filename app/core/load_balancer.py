"""
Global Load Balancer

This module provides global load balancing capabilities for the Faraday AI system,
integrating with regional failover and existing load balancing components.
"""

from typing import Dict, List, Optional, Any, Set
import asyncio
import time
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from prometheus_client import Counter, Histogram, Gauge
import subprocess
from statistics import mean, stdev
from dataclasses import dataclass
from enum import Enum
import psutil
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from app.core.config import get_settings
from app.core.health_checks import check_redis, check_minio, check_database
from sqlalchemy import create_engine
from app.core.enums import Region
from .regional_failover import RegionalFailoverManager

logger = logging.getLogger(__name__)

# Load balancing metrics
LOAD_BALANCE_REQUESTS = Counter(
    'global_load_balance_requests_total',
    'Total number of load balanced requests',
    ['region', 'status']
)

LOAD_BALANCE_LATENCY = Histogram(
    'global_load_balance_latency_seconds',
    'Load balancing operation latency in seconds',
    ['region']
)

REGION_LOAD = Gauge(
    'global_region_load',
    'Current load for each region',
    ['region']
)

REGION_HEALTH = Gauge(
    'global_region_health',
    'Health status for each region',
    ['region']
)

# New metrics for enhanced features
PREDICTIVE_SCORE = Gauge(
    'global_predictive_score',
    'Predictive load score for each region',
    ['region']
)

COST_EFFICIENCY = Gauge(
    'global_cost_efficiency',
    'Cost efficiency score for each region',
    ['region']
)

CIRCUIT_STATE = Gauge(
    'global_circuit_state',
    'Circuit breaker state for each region',
    ['region']
)

RESOURCE_USAGE = Gauge(
    'global_resource_usage',
    'Resource usage metrics',
    ['region', 'resource_type']
)

LATENCY_WEIGHT = Gauge(
    'global_latency_weight',
    'Latency-based weight for each region',
    ['region']
)

class RequestType(Enum):
    """Types of requests for routing."""
    LOW_LATENCY = "low_latency"
    HIGH_THROUGHPUT = "high_throughput"
    COST_SENSITIVE = "cost_sensitive"
    DATA_LOCAL = "data_local"

@dataclass
class RegionCost:
    """Cost information for a region."""
    compute_cost: float
    storage_cost: float
    network_cost: float
    currency: str = "USD"

class CircuitBreaker:
    """Circuit breaker for region health monitoring."""
    
    def __init__(self, region: Region):
        self.region = region
        self.failures = 0
        self.last_failure = None
        self.state = "closed"  # closed, open, half-open
        self.threshold = 5  # number of failures before opening
        self.reset_timeout = 60  # seconds to wait before half-open
        
    def record_failure(self):
        """Record a failure and update circuit state."""
        self.failures += 1
        self.last_failure = time.time()
        
        if self.failures >= self.threshold:
            self.state = "open"
            CIRCUIT_STATE.labels(region=self.region.value).set(0)  # 0 = open
            
    def record_success(self):
        """Record a success and update circuit state."""
        self.failures = 0
        self.state = "closed"
        CIRCUIT_STATE.labels(region=self.region.value).set(2)  # 2 = closed
        
    def can_attempt(self) -> bool:
        """Check if requests can be sent to this region."""
        if self.state == "closed":
            return True
            
        if self.state == "open":
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = "half-open"
                CIRCUIT_STATE.labels(region=self.region.value).set(1)  # 1 = half-open
                return True
            return False
            
        return True  # half-open state allows attempts

@dataclass
class LoadWindow:
    """Adaptive load window for performance tracking."""
    min_size: int = 10
    max_size: int = 1000
    current_size: int = 100
    metrics: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        self.metrics = []
        
    def add_metric(self, metric: Dict[str, Any]):
        """Add a new metric to the window."""
        self.metrics.append(metric)
        
        # Adjust window size based on system load
        if len(self.metrics) > self.current_size:
            self.metrics = self.metrics[-self.current_size:]
            
    def adjust_size(self, system_load: float):
        """Adjust window size based on system load."""
        if system_load > 0.8:  # High load
            self.current_size = max(self.min_size, self.current_size // 2)
        elif system_load < 0.3:  # Low load
            self.current_size = min(self.max_size, self.current_size * 2)
            
    def get_stats(self) -> Dict[str, float]:
        """Calculate statistics from the window."""
        if not self.metrics:
            return {
                "avg_latency": 0,
                "error_rate": 0,
                "throughput": 0
            }
            
        latencies = [m["latency"] for m in self.metrics]
        errors = [m["error"] for m in self.metrics]
        
        return {
            "avg_latency": mean(latencies) if latencies else 0,
            "error_rate": sum(errors) / len(errors) if errors else 0,
            "throughput": len(self.metrics) / (time.time() - self.metrics[0]["timestamp"])
        }

class RoutingStrategy(Enum):
    GEOGRAPHIC = "geographic"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    ADAPTIVE = "adaptive"

class GeographicRouter:
    def __init__(self):
        # TODO: Set up GeoLite2 database properly
        # 1. Create MaxMind account
        # 2. Download GeoLite2-City.mmdb
        # 3. Place in /app/data/geoip/GeoLite2-City.mmdb
        # For now, using default region
        self.reader = None
        
    def get_nearest_region(self, ip_address: str) -> Region:
        # TODO: Implement proper geolocation once GeoLite2 is set up
        return Region.NORTH_AMERICA  # Default to North America for now
        
    def _find_nearest_region(self, lat: float, lon: float) -> Region:
        # TODO: Implement proper region finding once GeoLite2 is set up
        return Region.NORTH_AMERICA  # Default to North America for now

class AdaptiveLoadBalancer:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.weights = {}
        
    def update_weights(self, metrics: Dict[str, Dict[str, float]]):
        features = []
        for region in metrics:
            region_metrics = metrics[region]
            features.append([
                1 - region_metrics['cpu_usage'],
                1 - region_metrics['memory_usage'],
                1 - region_metrics['error_rate'],
                region_metrics['throughput']
            ])
            
        if features:
            normalized = self.scaler.fit_transform(features)
            weights = np.mean(normalized, axis=1)
            
            for i, region in enumerate(metrics.keys()):
                self.weights[region] = float(weights[i])
                
    def get_target_region(self, regions: List[Region]) -> Region:
        valid_regions = [r for r in regions if r in self.weights]
        if not valid_regions:
            return regions[0]
            
        weights = [self.weights.get(r, 0) for r in valid_regions]
        return np.random.choice(valid_regions, p=weights/np.sum(weights))

class GlobalLoadBalancer:
    """Manages global load balancing across regions."""
    
    def __init__(self, failover_manager: RegionalFailoverManager):
        self.failover_manager = failover_manager
        self.settings = get_settings()
        self.region_stats = defaultdict(lambda: {
            'requests': 0,
            'errors': 0,
            'latency': [],
            'last_check': None,
            'health_score': 1.0,
            'hourly_load': defaultdict(list),
            'cost': RegionCost(0.1, 0.05, 0.02),  # Default costs
            'load_window': LoadWindow(),
            'resource_usage': {
                'cpu': 0.0,
                'memory': 0.0,
                'network': 0.0
            },
            'latency_weights': {
                'avg': 0.0,
                'std_dev': 0.0,
                'last_update': time.time()
            }
        })
        self.load_weights = {region: 1.0 for region in Region}
        self.rebalancing = False
        self.last_rebalance = time.time()
        self.rebalance_interval = 300  # 5 minutes
        
        # Initialize circuit breakers
        self.circuit_breakers = {
            region: CircuitBreaker(region)
            for region in Region
        }
        
        # Start monitoring
        asyncio.create_task(self._monitor_regions())
        asyncio.create_task(self._auto_rebalance())
        asyncio.create_task(self._update_predictive_scores())
        asyncio.create_task(self._monitor_resources())
        asyncio.create_task(self._update_latency_weights())
        
        self.geographic_router = GeographicRouter()
        self.adaptive_balancer = AdaptiveLoadBalancer()
        self.routing_strategy = RoutingStrategy.ADAPTIVE
        
    async def _monitor_resources(self):
        """Monitor resource usage across regions."""
        while True:
            try:
                for region in Region:
                    try:
                        # Get resource usage
                        cpu_percent = psutil.cpu_percent()
                        memory_percent = psutil.virtual_memory().percent
                        network_io = psutil.net_io_counters()
                        
                        # Update metrics
                        RESOURCE_USAGE.labels(
                            region=region.value,
                            resource_type='cpu'
                        ).set(cpu_percent)
                        RESOURCE_USAGE.labels(
                            region=region.value,
                            resource_type='memory'
                        ).set(memory_percent)
                        RESOURCE_USAGE.labels(
                            region=region.value,
                            resource_type='network'
                        ).set(network_io.bytes_sent + network_io.bytes_recv)
                        
                        # Update stats
                        stats = self.region_stats[region]
                        stats['resource_usage'] = {
                            'cpu': cpu_percent,
                            'memory': memory_percent,
                            'network': network_io.bytes_sent + network_io.bytes_recv
                        }
                        
                    except Exception as e:
                        logger.error(f"Error monitoring resources for {region}: {e}")
                        
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(30)  # Back off on error
                
    async def _update_latency_weights(self):
        """Update latency-based weights for regions."""
        while True:
            try:
                for region in Region:
                    try:
                        # Get recent latencies
                        stats = self.region_stats[region]
                        latencies = stats['latency'][-100:]  # Last 100 measurements
                        
                        if latencies:
                            # Calculate statistics
                            avg_latency = mean(latencies)
                            std_dev = stdev(latencies) if len(latencies) > 1 else 0
                            
                            # Update weights
                            stats['latency_weights'] = {
                                'avg': avg_latency,
                                'std_dev': std_dev,
                                'last_update': time.time()
                            }
                            
                            # Update metric
                            LATENCY_WEIGHT.labels(region=region.value).set(
                                1.0 / (1.0 + avg_latency)  # Lower latency = higher weight
                            )
                            
                    except Exception as e:
                        logger.error(f"Error updating latency weights for {region}: {e}")
                        
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in latency weight update: {e}")
                await asyncio.sleep(120)  # Back off on error
                
    async def get_target_region(
        self,
        request_type: RequestType = RequestType.LOW_LATENCY,
        ip_address: Optional[str] = None
    ) -> Region:
        """Get the optimal region for a request based on type."""
        try:
            if self.routing_strategy == RoutingStrategy.GEOGRAPHIC and ip_address:
                return self.geographic_router.get_nearest_region(ip_address)
            
            elif self.routing_strategy == RoutingStrategy.ADAPTIVE:
                metrics = {
                    region: {
                        'cpu_usage': stats['resource_usage']['cpu'],
                        'memory_usage': stats['resource_usage']['memory'],
                        'error_rate': stats['errors'] / max(1, stats['requests']),
                        'throughput': len(stats['latency']) / 60
                    }
                    for region, stats in self.region_stats.items()
                }
                self.adaptive_balancer.update_weights(metrics)
                return self.adaptive_balancer.get_target_region(list(Region))
            
            # Get current region health and load
            region_health = await self._get_region_health()
            region_load = await self._get_region_load()
            predictive_scores = await self._get_predictive_scores()
            
            # Calculate scores for each region
            region_scores = {}
            for region in Region:
                if not self.circuit_breakers[region].can_attempt():
                    continue
                    
                health = region_health.get(region, 0)
                load = region_load.get(region, 0)
                weight = self.load_weights[region]
                predictive = predictive_scores.get(region, 0.5)
                cost_efficiency = self._calculate_cost_efficiency(region)
                
                # Get resource usage
                resource_usage = self.region_stats[region]['resource_usage']
                resource_score = (
                    (1 - resource_usage['cpu'] / 100) * 0.4 +
                    (1 - resource_usage['memory'] / 100) * 0.3 +
                    (1 - resource_usage['network'] / 1000000) * 0.3  # Normalize network usage
                )
                
                # Get latency weight
                latency_weight = LATENCY_WEIGHT.labels(region=region.value)._value.get() or 0.5
                
                # Base score components
                base_score = (
                    (health * 0.2) +
                    ((1 - load) * 0.2) +
                    (weight * 0.2) +
                    (resource_score * 0.2) +
                    (latency_weight * 0.2)
                )
                
                # Adjust score based on request type
                if request_type == RequestType.LOW_LATENCY:
                    score = base_score + (latency_weight * 0.2)
                elif request_type == RequestType.HIGH_THROUGHPUT:
                    score = base_score + (resource_score * 0.2)
                elif request_type == RequestType.COST_SENSITIVE:
                    score = base_score + (cost_efficiency * 0.2)
                else:  # DATA_LOCAL
                    score = base_score + (health * 0.2)
                    
                region_scores[region] = score
            
            if not region_scores:
                # All regions are unhealthy, fall back to primary
                return Region.NORTH_AMERICA
                
            # Select region with highest score
            target_region = max(region_scores.items(), key=lambda x: x[1])[0]
            
            # Update metrics
            LOAD_BALANCE_REQUESTS.labels(
                region=target_region.value,
                status="success"
            ).inc()
            
            return target_region
            
        except Exception as e:
            logger.error(f"Error selecting target region: {e}")
            return Region.NORTH_AMERICA
            
    def _calculate_cost_efficiency(self, region: Region) -> float:
        """Calculate cost efficiency score for a region."""
        try:
            stats = self.region_stats[region]
            cost = stats['cost']
            
            # Calculate cost per request
            if stats['requests'] > 0:
                cost_per_request = (
                    cost.compute_cost +
                    cost.storage_cost +
                    cost.network_cost
                ) / stats['requests']
            else:
                cost_per_request = 1.0
                
            # Normalize to 0-1 range (lower is better)
            return 1.0 / (1.0 + cost_per_request)
            
        except Exception as e:
            logger.error(f"Error calculating cost efficiency: {e}")
            return 0.5
            
    async def _update_predictive_scores(self):
        """Update predictive scores based on historical data."""
        while True:
            try:
                current_hour = datetime.now().hour
                
                for region in Region:
                    stats = self.region_stats[region]
                    hourly_loads = stats['hourly_load'][current_hour]
                    
                    if hourly_loads:
                        # Calculate average load for this hour
                        avg_load = mean(hourly_loads)
                        # Update predictive score
                        PREDICTIVE_SCORE.labels(region=region.value).set(1.0 - avg_load)
                        
                await asyncio.sleep(3600)  # Update hourly
                
            except Exception as e:
                logger.error(f"Error updating predictive scores: {e}")
                await asyncio.sleep(3600)
                
    async def _get_predictive_scores(self) -> Dict[Region, float]:
        """Get current predictive scores for all regions."""
        scores = {}
        for region in Region:
            try:
                score = PREDICTIVE_SCORE.labels(region=region.value)._value.get()
                scores[region] = score if score is not None else 0.5
            except Exception:
                scores[region] = 0.5
        return scores
        
    async def _get_region_health(self) -> Dict[Region, float]:
        """Get health scores for all regions."""
        health_scores = {}
        for region in Region:
            try:
                # Check region health
                health_data = await self.failover_manager.check_region_health(region)
                health_score = self._calculate_health_score(health_data)
                
                # Update metrics
                REGION_HEALTH.labels(region=region.value).set(health_score)
                health_scores[region] = health_score
                
            except Exception as e:
                logger.error(f"Error checking region health: {e}")
                health_scores[region] = 0.0
                
        return health_scores
        
    async def _get_region_load(self) -> Dict[Region, float]:
        """Get load scores for all regions."""
        load_scores = {}
        for region in Region:
            try:
                # Calculate load based on stats
                stats = self.region_stats[region]
                if stats['requests'] > 0:
                    error_rate = stats['errors'] / stats['requests']
                    avg_latency = mean(stats['latency']) if stats['latency'] else 0
                    load_score = (error_rate * 0.3) + (avg_latency * 0.7)
                else:
                    load_score = 0.0
                    
                # Update metrics
                REGION_LOAD.labels(region=region.value).set(load_score)
                load_scores[region] = load_score
                
            except Exception as e:
                logger.error(f"Error calculating region load: {e}")
                load_scores[region] = 1.0
                
        return load_scores
        
    def _calculate_health_score(self, health_data: Dict[str, Any]) -> float:
        """Calculate health score from health data."""
        try:
            # Extract health metrics
            system_health = health_data.get('system', {})
            redis_health = health_data.get('redis', {})
            db_health = health_data.get('database', {})
            
            # Calculate component scores
            system_score = system_health.get('status') == 'healthy'
            redis_score = redis_health.get('status') == 'healthy'
            db_score = db_health.get('status') == 'healthy'
            
            # Combined health score
            health_score = (
                (system_score * 0.4) +
                (redis_score * 0.3) +
                (db_score * 0.3)
            )
            
            return health_score
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0.0
            
    async def _monitor_regions(self):
        """Monitor region health and performance."""
        while True:
            try:
                # Check all regions
                for region in Region:
                    try:
                        # Get health data
                        health_data = await self.failover_manager.check_region_health(region)
                        health_score = self._calculate_health_score(health_data)
                        
                        # Update stats
                        stats = self.region_stats[region]
                        stats['health_score'] = health_score
                        stats['last_check'] = time.time()
                        
                    except Exception as e:
                        logger.error(f"Error monitoring region {region}: {e}")
                        self.region_stats[region]['health_score'] = 0.0
                        
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in region monitoring: {e}")
                await asyncio.sleep(300)  # Back off on error
                
    async def _auto_rebalance(self):
        """Automatically rebalance load across regions."""
        while True:
            try:
                if not self.rebalancing:
                    # Get current load distribution
                    region_load = await self._get_region_load()
                    
                    # Check if rebalancing is needed
                    if region_load:
                        min_load = min(region_load.values())
                        max_load = max(region_load.values())
                        
                        if max_load > min_load * 1.5:  # 50% difference triggers rebalancing
                            await self._rebalance_load(region_load)
                            
                await asyncio.sleep(self.rebalance_interval)
                
            except Exception as e:
                logger.error(f"Error in auto-rebalancing: {e}")
                await asyncio.sleep(self.rebalance_interval * 2)
                
    async def _rebalance_load(self, region_load: Dict[Region, float]):
        """Rebalance load across regions."""
        try:
            self.rebalancing = True
            
            # Sort regions by load
            sorted_regions = sorted(
                region_load.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Adjust weights
            for region, load in sorted_regions:
                # Reduce weight for high-load regions
                if load > 0.8:  # 80% load
                    self.load_weights[region] *= 0.9
                # Increase weight for low-load regions
                elif load < 0.3:  # 30% load
                    self.load_weights[region] *= 1.1
                    
            # Normalize weights
            total_weight = sum(self.load_weights.values())
            for region in Region:
                self.load_weights[region] /= total_weight
                
        except Exception as e:
            logger.error(f"Error rebalancing load: {e}")
            self.rebalancing = False 