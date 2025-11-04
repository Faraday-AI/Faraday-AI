"""
Resource Sharing Service

This module provides services for managing resource sharing between organizations
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import uuid
import time
from sqlalchemy.orm import Session
from fastapi import HTTPException
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
import asyncio
from functools import wraps
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from collections import deque
from statistics import mean, stdev
from dataclasses import dataclass

from ..models.organization_models import (
    Organization,
    OrganizationResource,
    OrganizationCollaboration
)
from ..schemas.collaboration import (
    SharedResource,
    ResourceSharingRequest,
    ResourceSharingMetrics
)
from .resource_sharing_cache_service import ResourceSharingCacheService
from .resource_sharing_performance_service import ResourceSharingPerformanceService

# Global flag to track metrics registration
_METRICS_REGISTERED = False

# Global metrics objects
RESOURCE_OPERATIONS = None
OPERATION_LATENCY = None
ACTIVE_OPERATIONS = None
CACHE_HITS = None
CACHE_MISSES = None
ERROR_COUNT = None
SYSTEM_LOAD = None
RESOURCE_TYPE_USAGE = None
COLLABORATION_METRICS = None
SECURITY_METRICS = None
OPTIMIZATION_METRICS = None
MEMORY_USAGE = None
DB_POOL_METRICS = None
CIRCUIT_STATE = None
ERROR_RATE = None
CLEANUP_METRICS = None
CONNECTION_POOL_METRICS = None
PERFORMANCE_METRICS = None
LOAD_BALANCE_METRICS = None

def register_metrics():
    """Register Prometheus metrics if not already registered."""
    global _METRICS_REGISTERED
    global RESOURCE_OPERATIONS, OPERATION_LATENCY, ACTIVE_OPERATIONS, CACHE_HITS, CACHE_MISSES
    global ERROR_COUNT, SYSTEM_LOAD, RESOURCE_TYPE_USAGE, COLLABORATION_METRICS
    global SECURITY_METRICS, OPTIMIZATION_METRICS, MEMORY_USAGE, DB_POOL_METRICS
    global CIRCUIT_STATE, ERROR_RATE, CLEANUP_METRICS, CONNECTION_POOL_METRICS
    global PERFORMANCE_METRICS, LOAD_BALANCE_METRICS

    if _METRICS_REGISTERED:
        return

    # Safely unregister any existing metrics with the same names
    metric_names = [
        'resource_sharing_operations',
        'resource_sharing_operation_latency',
        'resource_sharing_active_operations',
        'resource_sharing_cache_hits',
        'resource_sharing_cache_misses',
        'resource_sharing_errors',
        'resource_sharing_system_load',
        'resource_sharing_type_usage',
        'resource_sharing_collaboration_metrics',
        'resource_sharing_security_events',
        'resource_sharing_optimization_metrics',
        'resource_sharing_memory_usage',
        'resource_sharing_db_pool_metrics',
        'resource_sharing_circuit_state',
        'resource_sharing_error_rate',
        'resource_sharing_cleanup_operations',
        'resource_sharing_connection_pool',
        'resource_sharing_performance_metrics',
        'resource_sharing_load_balance'
    ]

    collectors_to_unregister = set()
    for collector in list(REGISTRY._collector_to_names.keys()):
        try:
            names = REGISTRY._collector_to_names.get(collector, set())
            if any(name.startswith(metric_name) for name in names for metric_name in metric_names):
                collectors_to_unregister.add(collector)
        except Exception:
            continue

    for collector in collectors_to_unregister:
        try:
            REGISTRY.unregister(collector)
        except KeyError:
            continue

    # Register new metrics
    RESOURCE_OPERATIONS = Counter(
        'resource_sharing_operations_total',
        'Total number of resource sharing operations',
        ['operation_type', 'status']
    )

    OPERATION_LATENCY = Histogram(
        'resource_sharing_operation_latency_seconds',
        'Resource sharing operation latency in seconds',
        ['operation_type']
    )

    ACTIVE_OPERATIONS = Gauge(
        'resource_sharing_active_operations',
        'Number of active resource sharing operations'
    )

    CACHE_HITS = Counter(
        'resource_sharing_cache_hits_total',
        'Total number of cache hits',
        ['operation_type']
    )

    CACHE_MISSES = Counter(
        'resource_sharing_cache_misses_total',
        'Total number of cache misses',
        ['operation_type']
    )

    ERROR_COUNT = Counter(
        'resource_sharing_errors_total',
        'Total number of errors in resource sharing operations',
        ['error_type']
    )

    SYSTEM_LOAD = Gauge(
        'resource_sharing_system_load',
        'Current system load for resource sharing service'
    )

    RESOURCE_TYPE_USAGE = Gauge(
        'resource_sharing_type_usage',
        'Usage by resource type',
        ['resource_type']
    )

    COLLABORATION_METRICS = Gauge(
        'resource_sharing_collaboration_metrics',
        'Collaboration-specific metrics',
        ['org_pair', 'metric_type']
    )

    SECURITY_METRICS = Counter(
        'resource_sharing_security_events',
        'Security-related events in resource sharing',
        ['event_type', 'severity']
    )

    OPTIMIZATION_METRICS = Gauge(
        'resource_sharing_optimization_metrics',
        'Resource optimization metrics',
        ['metric_type']
    )

    MEMORY_USAGE = Gauge(
        'resource_sharing_memory_usage_bytes',
        'Memory usage of resource sharing service'
    )

    DB_POOL_METRICS = Gauge(
        'resource_sharing_db_pool_metrics',
        'Database connection pool metrics',
        ['metric_type']
    )

    CIRCUIT_STATE = Gauge(
        'resource_sharing_circuit_state',
        'Circuit breaker state (0=open, 1=half-open, 2=closed)',
        ['operation_type']
    )

    ERROR_RATE = Gauge(
        'resource_sharing_error_rate',
        'Error rate for operations',
        ['operation_type']
    )

    CLEANUP_METRICS = Counter(
        'resource_sharing_cleanup_operations',
        'Resource cleanup operations',
        ['operation_type', 'status']
    )

    CONNECTION_POOL_METRICS = Gauge(
        'resource_sharing_connection_pool',
        'Connection pool metrics',
        ['pool_type', 'metric']
    )

    PERFORMANCE_METRICS = Gauge(
        'resource_sharing_performance_metrics',
        'Performance metrics for resource sharing',
        ['metric_type']
    )

    LOAD_BALANCE_METRICS = Gauge(
        'resource_sharing_load_balance',
        'Load balancing metrics',
        ['metric_type']
    )

    _METRICS_REGISTERED = True

# Call register_metrics at module import
register_metrics()

# Rate limiting settings
MAX_CONCURRENT_OPS = 50
MAX_BATCH_SIZE = 100
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_CALLS = 1000

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'memory_warning': 0.75,  # 75% memory usage
    'memory_critical': 0.90,  # 90% memory usage
    'db_pool_warning': 0.80,  # 80% pool usage
    'db_pool_critical': 0.95,  # 95% pool usage
    'latency_warning_ms': 500,  # 500ms
    'latency_critical_ms': 1000  # 1s
}

# Resource pool settings
POOL_CONFIG = {
    'max_connections': 50,
    'min_connections': 5,
    'max_idle_time': 300,  # 5 minutes
    'health_check_interval': 60  # 1 minute
}

@dataclass
class PerformanceWindow:
    """Rolling window of performance metrics."""
    window_size: int = 100
    latencies: List[float] = None
    errors: List[bool] = None
    timestamps: List[float] = None

    def __post_init__(self):
        self.latencies = []
        self.errors = []
        self.timestamps = []

    def add_metric(self, latency: float, error: bool = False):
        """Add a new metric to the window."""
        current_time = time.time()
        
        # Add new metrics
        self.latencies.append(latency)
        self.errors.append(error)
        self.timestamps.append(current_time)
        
        # Remove old metrics
        while len(self.latencies) > self.window_size:
            self.latencies.pop(0)
            self.errors.pop(0)
            self.timestamps.pop(0)

    def get_stats(self) -> Dict[str, float]:
        """Calculate performance statistics."""
        if not self.latencies:
            return {
                "avg_latency": 0,
                "std_dev": 0,
                "error_rate": 0,
                "throughput": 0
            }

        current_time = time.time()
        window_duration = current_time - self.timestamps[0] if self.timestamps else 1

        return {
            "avg_latency": mean(self.latencies),
            "std_dev": stdev(self.latencies) if len(self.latencies) > 1 else 0,
            "error_rate": sum(self.errors) / len(self.errors),
            "throughput": len(self.latencies) / window_duration
        }

class AdaptiveLoadBalancer:
    """Adaptive load balancing with performance optimization."""
    
    def __init__(self):
        self.performance_windows = {
            "share_resource": PerformanceWindow(),
            "share_resources_batch": PerformanceWindow(),
            "get_metrics": PerformanceWindow()
        }
        self.last_adjustment = time.time()
        self.adjustment_interval = 60  # seconds
        
        # Initialize metrics
        for metric in ["capacity", "throughput", "latency"]:
            LOAD_BALANCE_METRICS.labels(metric_type=metric).set(0)
    
    async def pre_operation(self, operation_type: str) -> bool:
        """Check if operation should proceed based on current load."""
        stats = self.performance_windows[operation_type].get_stats()
        
        # Update metrics
        LOAD_BALANCE_METRICS.labels(metric_type="throughput").set(stats["throughput"])
        LOAD_BALANCE_METRICS.labels(metric_type="latency").set(stats["avg_latency"])
        
        # Check if system is overloaded
        if (stats["error_rate"] > 0.1 or  # More than 10% errors
            stats["avg_latency"] > PERFORMANCE_THRESHOLDS["latency_critical_ms"] / 1000):
            return False
            
        return True
    
    async def post_operation(self, operation_type: str, latency: float, error: bool = False):
        """Record operation metrics and adjust if needed."""
        self.performance_windows[operation_type].add_metric(latency, error)
        
        current_time = time.time()
        if current_time - self.last_adjustment >= self.adjustment_interval:
            await self._adjust_capacity()
            self.last_adjustment = current_time
    
    async def _adjust_capacity(self):
        """Adjust system capacity based on performance metrics."""
        try:
            # Calculate overall system metrics
            all_stats = [
                window.get_stats()
                for window in self.performance_windows.values()
            ]
            
            avg_error_rate = mean(stats["error_rate"] for stats in all_stats)
            avg_latency = mean(stats["avg_latency"] for stats in all_stats)
            total_throughput = sum(stats["throughput"] for stats in all_stats)
            
            # Update capacity metric
            current_capacity = LOAD_BALANCE_METRICS.labels(
                metric_type="capacity"
            )._value.get()
            
            # Adjust capacity based on performance
            if avg_error_rate < 0.05 and avg_latency < PERFORMANCE_THRESHOLDS["latency_warning_ms"] / 1000:
                # System is healthy, can increase capacity
                new_capacity = min(1.0, current_capacity * 1.1)
            elif avg_error_rate > 0.1 or avg_latency > PERFORMANCE_THRESHOLDS["latency_critical_ms"] / 1000:
                # System is struggling, reduce capacity
                new_capacity = max(0.5, current_capacity * 0.9)
            else:
                # System is stable
                new_capacity = current_capacity
                
            LOAD_BALANCE_METRICS.labels(metric_type="capacity").set(new_capacity)
            
            # Record performance metrics
            PERFORMANCE_METRICS.labels(metric_type="error_rate").set(avg_error_rate)
            PERFORMANCE_METRICS.labels(metric_type="avg_latency").set(avg_latency)
            PERFORMANCE_METRICS.labels(metric_type="throughput").set(total_throughput)
            
        except Exception as e:
            ERROR_COUNT.labels(error_type="capacity_adjustment").inc()

# Enhanced rate limiting settings with adaptive thresholds
class AdaptiveRateLimiter:
    def __init__(self):
        self.base_limit = 1000
        self.current_limit = self.base_limit
        self.window_size = 60  # seconds
        self.operations = []
        self.last_adjustment = time.time()
        
    def adjust_limits(self, system_load: float):
        """Dynamically adjust rate limits based on system load."""
        current_time = time.time()
        if current_time - self.last_adjustment < 10:  # Adjust every 10 seconds
            return
            
        # Adjust limits based on system load
        if system_load > 0.8:  # High load
            self.current_limit = max(100, int(self.current_limit * 0.8))
        elif system_load < 0.3:  # Low load
            self.current_limit = min(self.base_limit, int(self.current_limit * 1.2))
            
        self.last_adjustment = current_time
        
    def check_limit(self, operation_type: str) -> bool:
        """Check if operation is within rate limits."""
        current_time = time.time()
        
        # Clean up old operations
        self.operations = [
            op for op in self.operations
            if current_time - op["timestamp"] <= self.window_size
        ]
        
        # Count operations of this type
        type_count = sum(1 for op in self.operations if op["type"] == operation_type)
        
        if len(self.operations) >= self.current_limit:
            return False
            
        self.operations.append({
            "timestamp": current_time,
            "type": operation_type
        })
        
        return True

def monitor_operation(operation_type: str):
    """Decorator for monitoring operation performance and load."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Check system load
            current_ops = ACTIVE_OPERATIONS._value.get()
            if current_ops >= MAX_CONCURRENT_OPS:
                ERROR_COUNT.labels(error_type="overload").inc()
                raise HTTPException(
                    status_code=503,
                    detail="System is currently overloaded. Please try again later."
                )

            try:
                # Update metrics
                ACTIVE_OPERATIONS.inc()
                SYSTEM_LOAD.set(current_ops / MAX_CONCURRENT_OPS)
                
                # Execute operation
                result = await func(*args, **kwargs)
                
                # Record success metrics
                RESOURCE_OPERATIONS.labels(
                    operation_type=operation_type,
                    status="success"
                ).inc()
                
                return result

            except Exception as e:
                # Record error metrics
                RESOURCE_OPERATIONS.labels(
                    operation_type=operation_type,
                    status="error"
                ).inc()
                ERROR_COUNT.labels(error_type=type(e).__name__).inc()
                raise

            finally:
                # Update timing metrics
                OPERATION_LATENCY.labels(
                    operation_type=operation_type
                ).observe(time.time() - start_time)
                ACTIVE_OPERATIONS.dec()

        return wrapper
    return decorator

class CircuitBreaker:
    """Circuit breaker for protecting system resources."""
    
    def __init__(self, operation_type: str):
        self.operation_type = operation_type
        self.state = "closed"  # closed, open, half-open
        self.failures = 0
        self.last_failure_time = 0
        self.half_open_time = 30  # seconds
        self.failure_threshold = 5
        self.success_threshold = 3
        self.successes = 0
        
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        current_time = time.time()
        
        # Update circuit state metric
        CIRCUIT_STATE.labels(operation_type=self.operation_type).set(
            2 if self.state == "closed" else 1 if self.state == "half-open" else 0
        )
        
        if self.state == "open":
            if current_time - self.last_failure_time > self.half_open_time:
                self.state = "half-open"
                self.successes = 0
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.successes += 1
                if self.successes >= self.success_threshold:
                    self.state = "closed"
                    self.failures = 0
                    
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = current_time
            
            # Update error rate metric
            ERROR_RATE.labels(operation_type=self.operation_type).set(
                self.failures / (self.failures + self.successes) if self.successes > 0 else 1
            )
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise

class ResourcePool:
    """Efficient resource connection pooling."""
    
    def __init__(self, pool_type: str):
        self.pool_type = pool_type
        self.active_connections = 0
        self.available_connections = deque()
        self.last_health_check = time.time()
        
        # Initialize metrics
        CONNECTION_POOL_METRICS.labels(
            pool_type=pool_type,
            metric="active"
        ).set(0)
        CONNECTION_POOL_METRICS.labels(
            pool_type=pool_type,
            metric="available"
        ).set(0)
        
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[Any, None]:
        """Acquire a connection from the pool."""
        try:
            # Try to get an available connection
            if self.available_connections:
                conn = self.available_connections.popleft()
            else:
                # Create new connection if under limit
                if self.active_connections < POOL_CONFIG['max_connections']:
                    conn = await self._create_connection()
                    self.active_connections += 1
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="Connection pool exhausted"
                    )
            
            # Update metrics
            CONNECTION_POOL_METRICS.labels(
                pool_type=self.pool_type,
                metric="active"
            ).set(self.active_connections)
            CONNECTION_POOL_METRICS.labels(
                pool_type=self.pool_type,
                metric="available"
            ).set(len(self.available_connections))
            
            yield conn
            
        finally:
            # Return connection to pool
            self.available_connections.append(conn)
            
            # Perform health check if needed
            current_time = time.time()
            if current_time - self.last_health_check > POOL_CONFIG['health_check_interval']:
                await self._health_check()
                self.last_health_check = current_time
    
    async def _create_connection(self) -> Any:
        """Create a new connection."""
        # Implementation depends on resource type
        pass
        
    async def _health_check(self):
        """Check and clean up idle connections."""
        current_time = time.time()
        active_conns = deque()
        
        while self.available_connections:
            conn = self.available_connections.popleft()
            if hasattr(conn, 'last_used'):
                idle_time = current_time - conn.last_used
                if idle_time > POOL_CONFIG['max_idle_time']:
                    self.active_connections -= 1
                    continue
            active_conns.append(conn)
            
        self.available_connections = active_conns
        
        # Ensure minimum connections
        while self.active_connections < POOL_CONFIG['min_connections']:
            try:
                conn = await self._create_connection()
                self.available_connections.append(conn)
                self.active_connections += 1
            except Exception as e:
                ERROR_COUNT.labels(error_type="pool_creation").inc()
                break

class ResourceSharingService:
    def __init__(self, db: Session, redis_url: str = "redis://localhost:6379"):
        self.db = db
        self.cache_service = ResourceSharingCacheService(redis_url)
        self.performance_service = ResourceSharingPerformanceService()
        self.rate_limiter = AdaptiveRateLimiter()
        self.circuit_breakers = {
            "share_resource": CircuitBreaker("share_resource"),
            "share_resources_batch": CircuitBreaker("share_resources_batch"),
            "get_sharing_metrics": CircuitBreaker("get_sharing_metrics")
        }
        self.load_balancer = AdaptiveLoadBalancer()
        
        # Initialize resource pools
        self.db_pool = ResourcePool("database")
        self.cache_pool = ResourcePool("cache")
        
        # Initialize metrics and monitoring
        self._init_metrics()
        
        # Track background tasks for proper cleanup
        self._background_tasks = []
        self._shutdown_event = None  # Will be created when tasks start
        
        # Don't start background tasks in __init__ - let them be started lazily
        # This prevents issues in test environments where event loops are managed differently
        # Background tasks should be started explicitly via start_background_tasks() or
        # on first async method call if needed for production use
        
    def _init_metrics(self):
        """Initialize service metrics."""
        SYSTEM_LOAD.set(0)
        ACTIVE_OPERATIONS.set(0)
        MEMORY_USAGE.set(0)
        
        # Initialize DB pool metrics
        DB_POOL_METRICS.labels(metric_type="active_connections").set(0)
        DB_POOL_METRICS.labels(metric_type="available_connections").set(0)
        
    async def start_background_tasks(self):
        """Start background monitoring and cleanup tasks."""
        if self._shutdown_event is None:
            self._shutdown_event = asyncio.Event()
        
        if not self._background_tasks:
            try:
                loop = asyncio.get_running_loop()
                task1 = loop.create_task(self._monitor_service_health())
                task2 = loop.create_task(self._cleanup_resources())
                self._background_tasks = [task1, task2]
            except RuntimeError:
                # No event loop running - skip background tasks
                pass
    
    async def shutdown(self):
        """Gracefully shutdown background tasks."""
        # Signal shutdown
        if self._shutdown_event:
            self._shutdown_event.set()
        
        # Cancel all background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to finish cancellation
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self._background_tasks = []
    
    async def _monitor_service_health(self):
        """Background task to monitor service health."""
        try:
            while True:
                # Check for shutdown signal
                if self._shutdown_event and self._shutdown_event.is_set():
                    break
                
                try:
                    # Update memory usage metrics
                    import psutil
                    process = psutil.Process()
                    MEMORY_USAGE.set(process.memory_info().rss)
                    
                    # Update DB pool metrics
                    pool_metrics = await self._get_db_pool_metrics()
                    DB_POOL_METRICS.labels(metric_type="active_connections").set(
                        pool_metrics["active_connections"]
                    )
                    DB_POOL_METRICS.labels(metric_type="available_connections").set(
                        pool_metrics["available_connections"]
                    )
                    
                    # Adjust rate limits based on system load
                    current_load = SYSTEM_LOAD._value.get()
                    self.rate_limiter.adjust_limits(current_load)
                    
                    # Sleep with cancellation support
                    try:
                        await asyncio.sleep(10)  # Check every 10 seconds
                    except asyncio.CancelledError:
                        break
                    
                except Exception as e:
                    ERROR_COUNT.labels(error_type="health_monitor").inc()
                    # Log error but don't crash the monitor
                    print(f"Health monitor error: {str(e)}")
                    try:
                        await asyncio.sleep(30)  # Back off on error
                    except asyncio.CancelledError:
                        break
        except asyncio.CancelledError:
            # Task was cancelled - this is expected during shutdown
            pass
                
    async def _get_db_pool_metrics(self) -> Dict[str, int]:
        """Get database connection pool metrics."""
        try:
            # These metrics depend on your specific database engine
            return {
                "active_connections": self.db.bind.pool.size(),
                "available_connections": self.db.bind.pool.overflow()
            }
        except Exception:
            return {
                "active_connections": 0,
                "available_connections": 0
            }
            
    def _update_resource_metrics(self, resource_type: str, usage: float):
        """Update resource-specific metrics."""
        RESOURCE_TYPE_USAGE.labels(resource_type=resource_type).set(usage)
        
    def _update_collaboration_metrics(self, org_pair: str, metrics: Dict[str, float]):
        """Update collaboration-specific metrics."""
        for metric_type, value in metrics.items():
            COLLABORATION_METRICS.labels(
                org_pair=org_pair,
                metric_type=metric_type
            ).set(value)
            
    def _record_security_event(self, event_type: str, severity: str):
        """Record security-related events."""
        SECURITY_METRICS.labels(
            event_type=event_type,
            severity=severity
        ).inc()
        
    def _update_optimization_metrics(self, metrics: Dict[str, float]):
        """Update optimization-related metrics."""
        for metric_type, value in metrics.items():
            OPTIMIZATION_METRICS.labels(metric_type=metric_type).set(value)

    async def _cleanup_resources(self):
        """Background task for resource cleanup."""
        try:
            while True:
                # Check for shutdown signal
                if self._shutdown_event and self._shutdown_event.is_set():
                    break
                
                try:
                    # Clean up expired resources
                    await self._cleanup_expired_resources()
                    
                    # Clean up orphaned resources
                    await self._cleanup_orphaned_resources()
                    
                    # Clean up inactive collaborations
                    await self._cleanup_inactive_collaborations()
                    
                    # Sleep with cancellation support
                    try:
                        await asyncio.sleep(3600)  # Run every hour
                    except asyncio.CancelledError:
                        break
                    
                except Exception as e:
                    ERROR_COUNT.labels(error_type="cleanup").inc()
                    print(f"Cleanup error: {str(e)}")
                    try:
                        await asyncio.sleep(3600)  # Retry in an hour
                    except asyncio.CancelledError:
                        break
        except asyncio.CancelledError:
            # Task was cancelled - this is expected during shutdown
            pass
                
    async def _cleanup_expired_resources(self):
        """Clean up expired shared resources."""
        try:
            current_time = datetime.utcnow()
            
            # Find expired resources
            collaborations = self.db.query(OrganizationCollaboration).filter(
                OrganizationCollaboration.type == "resource-sharing"
            ).all()
            
            cleanup_count = 0
            for collab in collaborations:
                if "shared_resources" not in collab.settings:
                    continue
                    
                active_resources = []
                for resource in collab.settings["shared_resources"]:
                    # Check if resource has expired
                    if "expires_at" in resource and datetime.fromisoformat(resource["expires_at"]) <= current_time:
                        cleanup_count += 1
                        continue
                    active_resources.append(resource)
                
                if len(active_resources) != len(collab.settings["shared_resources"]):
                    collab.settings["shared_resources"] = active_resources
                    
            if cleanup_count > 0:
                self.db.commit()
                CLEANUP_METRICS.labels(
                    operation_type="expired_resources",
                    status="success"
                ).inc(cleanup_count)
                
        except Exception as e:
            CLEANUP_METRICS.labels(
                operation_type="expired_resources",
                status="error"
            ).inc()
            raise
            
    async def _cleanup_orphaned_resources(self):
        """Clean up orphaned resources."""
        try:
            cleanup_count = 0
            collaborations = self.db.query(OrganizationCollaboration).filter(
                OrganizationCollaboration.type == "resource-sharing"
            ).all()
            
            for collab in collaborations:
                if "shared_resources" not in collab.settings:
                    continue
                    
                active_resources = []
                for resource in collab.settings["shared_resources"]:
                    # Check if resource still exists
                    resource_exists = self.db.query(OrganizationResource).filter(
                        OrganizationResource.organization_id == collab.source_org_id,
                        OrganizationResource.resource_id == resource["resource_id"]
                    ).first() is not None
                    
                    if resource_exists:
                        active_resources.append(resource)
                    else:
                        cleanup_count += 1
                        
                if len(active_resources) != len(collab.settings["shared_resources"]):
                    collab.settings["shared_resources"] = active_resources
                    
            if cleanup_count > 0:
                self.db.commit()
                CLEANUP_METRICS.labels(
                    operation_type="orphaned_resources",
                    status="success"
                ).inc(cleanup_count)
                
        except Exception as e:
            CLEANUP_METRICS.labels(
                operation_type="orphaned_resources",
                status="error"
            ).inc()
            raise
            
    async def _cleanup_inactive_collaborations(self):
        """Clean up inactive collaborations."""
        try:
            current_time = datetime.utcnow()
            thirty_days_ago = current_time - timedelta(days=30)
            
            # Find inactive collaborations
            inactive_collaborations = self.db.query(OrganizationCollaboration).filter(
                OrganizationCollaboration.type == "resource-sharing",
                OrganizationCollaboration.updated_at <= thirty_days_ago,
                OrganizationCollaboration.status == "active"
            ).all()
            
            cleanup_count = 0
            for collab in inactive_collaborations:
                if "shared_resources" not in collab.settings or not collab.settings["shared_resources"]:
                    collab.status = "inactive"
                    cleanup_count += 1
                    
            if cleanup_count > 0:
                self.db.commit()
                CLEANUP_METRICS.labels(
                    operation_type="inactive_collaborations",
                    status="success"
                ).inc(cleanup_count)
                
        except Exception as e:
            CLEANUP_METRICS.labels(
                operation_type="inactive_collaborations",
                status="error"
            ).inc()
            raise

    @monitor_operation("share_resource")
    async def share_resource(
        self,
        source_org_id: str,
        target_org_id: str,
        resource_type: str,
        resource_id: str,
        access_level: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Share a resource between organizations."""
        if not self.rate_limiter.check_limit("share_resource"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
            
        # Check load balancer
        if not await self.load_balancer.pre_operation("share_resource"):
            raise HTTPException(
                status_code=503,
                detail="System is currently at capacity. Please try again later."
            )
            
        start_time = time.time()
        error = False
        
        try:
            result = await self.circuit_breakers["share_resource"].call(
                super().share_resource,
                source_org_id,
                target_org_id,
                resource_type,
                resource_id,
                access_level,
                settings
            )
            return result
        except Exception as e:
            error = True
            raise
        finally:
            latency = time.time() - start_time
            await self.load_balancer.post_operation("share_resource", latency, error)

    async def get_shared_resources(
        self,
        org_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get resources shared with an organization."""
        try:
            # Try to get from cache first
            cached_resources = await self.cache_service.get_shared_resources(org_id, status)
            if cached_resources is not None:
                return cached_resources

            # If not in cache, get from database
            collaborations = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id),
                OrganizationCollaboration.type == "resource-sharing"
            ).all()

            shared_resources = []
            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        if status is None or resource["status"] == status:
                            shared_resources.append(resource)

            # Cache the results
            await self.cache_service.set_shared_resources(org_id, shared_resources, status)

            return shared_resources

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving shared resources: {str(e)}"
            )

    async def update_shared_resource(
        self,
        share_id: str,
        status: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a shared resource's status or settings."""
        try:
            collaborations = self.db.query(OrganizationCollaboration).filter(
                OrganizationCollaboration.type == "resource-sharing"
            ).all()

            updated_resource = None
            affected_orgs = set()

            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        if resource["id"] == share_id:
                            resource["status"] = status
                            if settings:
                                resource["settings"].update(settings)
                            resource["updated_at"] = datetime.utcnow()
                            updated_resource = resource
                            affected_orgs.add(collab.source_org_id)
                            affected_orgs.add(collab.target_org_id)
                            break

            if updated_resource:
                self.db.commit()
                # Invalidate cache for affected organizations
                for org_id in affected_orgs:
                    await self.cache_service.invalidate_org_cache(org_id)
                return updated_resource

            raise HTTPException(
                status_code=404,
                detail="Shared resource not found"
            )

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating shared resource: {str(e)}"
            )

    @monitor_operation("get_sharing_metrics")
    async def get_sharing_metrics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get resource sharing metrics for an organization."""
        try:
            # Try to get from cache first
            cached_metrics = await self.cache_service.get_sharing_metrics(org_id, time_range)
            if cached_metrics is not None:
                CACHE_HITS.labels(operation_type="get_metrics").inc()
                return cached_metrics
            
            CACHE_MISSES.labels(operation_type="get_metrics").inc()
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            collaborations = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id),
                OrganizationCollaboration.type == "resource-sharing",
                OrganizationCollaboration.created_at >= start_time
            ).all()

            metrics = {
                "total_shared": 0,
                "active_shares": 0,
                "by_resource_type": {},
                "by_access_level": {},
                "usage_metrics": {},
                "performance_metrics": {},
                "cost_metrics": {},
                "security_metrics": {}
            }

            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        metrics["total_shared"] += 1
                        if resource["status"] == "active":
                            metrics["active_shares"] += 1

                        # Update resource type counts
                        resource_type = resource["resource_type"]
                        metrics["by_resource_type"][resource_type] = \
                            metrics["by_resource_type"].get(resource_type, 0) + 1

                        # Update access level counts
                        access_level = resource["access_level"]
                        metrics["by_access_level"][access_level] = \
                            metrics["by_access_level"].get(access_level, 0) + 1

                        # Update usage metrics
                        if "usage_metrics" in resource:
                            for key, value in resource["usage_metrics"].items():
                                if key not in metrics["usage_metrics"]:
                                    metrics["usage_metrics"][key] = 0
                                metrics["usage_metrics"][key] += value

            # Cache the metrics
            await self.cache_service.set_sharing_metrics(org_id, metrics, time_range)

            return metrics

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting sharing metrics: {str(e)}"
            )

    def _parse_time_range(self, time_range: str) -> timedelta:
        """Convert time range string to timedelta."""
        try:
            value = int(time_range[:-1])
            unit = time_range[-1].lower()
            
            if unit == "h":
                return timedelta(hours=value)
            elif unit == "d":
                return timedelta(days=value)
            elif unit == "w":
                return timedelta(weeks=value)
            elif unit == "m":
                return timedelta(days=value * 30)
            else:
                raise ValueError(f"Invalid time unit: {unit}")
        except Exception as e:
            raise ValueError(f"Invalid time range format: {time_range}")

    @monitor_operation("share_resources_batch")
    async def share_resources_batch(
        self,
        source_org_id: str,
        sharing_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Share multiple resources in a single transaction."""
        if not self.rate_limiter.check_limit("share_resources_batch"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        return await self.circuit_breakers["share_resources_batch"].call(
            super().share_resources_batch,
            source_org_id,
            sharing_requests
        )

    async def update_resources_batch(
        self,
        updates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update multiple shared resources in a single transaction."""
        correlation_id = str(uuid.uuid4())
        await self.performance_service.record_operation_start("update_resources_batch", correlation_id)

        try:
            share_ids = {update["share_id"] for update in updates}
            affected_orgs = set()
            results = []
            start_time = time.time()
            success_count = 0

            collaborations = self.db.query(OrganizationCollaboration).filter(
                OrganizationCollaboration.type == "resource-sharing"
            ).all()

            for update in updates:
                share_id = update["share_id"]
                status = update["status"]
                settings = update.get("settings")
                
                resource_found = False
                
                for collab in collaborations:
                    if "shared_resources" in collab.settings:
                        for resource in collab.settings["shared_resources"]:
                            if resource["id"] == share_id:
                                resource["status"] = status
                                if settings:
                                    resource["settings"].update(settings)
                                resource["updated_at"] = datetime.utcnow()
                                
                                affected_orgs.add(collab.source_org_id)
                                affected_orgs.add(collab.target_org_id)
                                
                                results.append(resource)
                                success_count += 1
                                resource_found = True
                                break
                
                if not resource_found:
                    results.append({
                        "error": "Resource not found",
                        "share_id": share_id
                    })

            self.db.commit()

            # Invalidate cache for affected organizations
            for org_id in affected_orgs:
                await self.cache_service.invalidate_org_cache(org_id)

            # Record performance metrics
            processing_time = time.time() - start_time
            success_rate = success_count / len(updates)
            await self.performance_service.record_batch_metrics(
                batch_size=len(updates),
                processing_time=processing_time,
                success_rate=success_rate
            )
            await self.performance_service.record_operation_end(correlation_id)

            return results

        except Exception as e:
            self.db.rollback()
            await self.performance_service.record_operation_end(correlation_id, "error")
            raise HTTPException(
                status_code=500,
                detail=f"Error in batch resource update: {str(e)}"
            )

    async def get_resources_batch(
        self,
        org_ids: List[str],
        status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get shared resources for multiple organizations."""
        correlation_id = str(uuid.uuid4())
        await self.performance_service.record_operation_start("get_resources_batch", correlation_id)

        try:
            results = {}
            cache_hits = 0
            start_time = time.time()

            for org_id in org_ids:
                # Try to get from cache first
                cached_resources = await self.cache_service.get_shared_resources(org_id, status)
                if cached_resources is not None:
                    results[org_id] = cached_resources
                    cache_hits += 1
                    continue

                # If not in cache, get from database
                collaborations = self.db.query(OrganizationCollaboration).filter(
                    (OrganizationCollaboration.source_org_id == org_id) |
                    (OrganizationCollaboration.target_org_id == org_id),
                    OrganizationCollaboration.type == "resource-sharing"
                ).all()

                shared_resources = []
                for collab in collaborations:
                    if "shared_resources" in collab.settings:
                        for resource in collab.settings["shared_resources"]:
                            if status is None or resource["status"] == status:
                                shared_resources.append(resource)

                # Cache the results
                await self.cache_service.set_shared_resources(org_id, shared_resources, status)
                results[org_id] = shared_resources

            # Record performance metrics
            processing_time = time.time() - start_time
            success_rate = 1.0  # All operations are read-only
            await self.performance_service.record_batch_metrics(
                batch_size=len(org_ids),
                processing_time=processing_time,
                success_rate=success_rate
            )
            await self.performance_service.record_operation_end(correlation_id)

            # Record cache operation metrics
            await self.performance_service.record_cache_operation(
                "get",
                "success" if cache_hits > 0 else "miss"
            )

            return results

        except Exception as e:
            await self.performance_service.record_operation_end(correlation_id, "error")
            raise HTTPException(
                status_code=500,
                detail=f"Error in batch resource retrieval: {str(e)}"
            )

    async def optimize_resource_allocation(
        self,
        org_id: str,
        resource_type: Optional[str] = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        AI-driven resource allocation optimization.
        Analyzes usage patterns and suggests optimal resource distribution.
        """
        try:
            # Get historical usage data
            metrics = await self.get_sharing_metrics(org_id, time_range)
            
            # Analyze resource utilization patterns
            utilization_patterns = await self._analyze_utilization_patterns(
                org_id,
                metrics,
                resource_type
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                utilization_patterns,
                metrics["by_resource_type"],
                metrics["usage_metrics"]
            )
            
            return {
                "current_allocation": metrics["by_resource_type"],
                "utilization_patterns": utilization_patterns,
                "recommendations": recommendations,
                "potential_savings": await self._calculate_potential_savings(
                    metrics,
                    recommendations
                )
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing resource allocation: {str(e)}"
            )

    async def predict_resource_needs(
        self,
        org_id: str,
        resource_type: Optional[str] = None,
        prediction_window: str = "7d"
    ) -> Dict[str, Any]:
        """
        Predictive scaling analysis for resource needs.
        Uses historical data to predict future resource requirements.
        """
        try:
            # Get historical data for prediction
            historical_data = await self._get_historical_usage_data(
                org_id,
                resource_type,
                prediction_window
            )
            
            # Generate usage predictions
            predictions = await self._generate_usage_predictions(
                historical_data,
                prediction_window
            )
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_prediction_confidence(
                predictions,
                historical_data
            )
            
            return {
                "predictions": predictions,
                "confidence_intervals": confidence_intervals,
                "recommended_scaling": await self._generate_scaling_recommendations(
                    predictions,
                    confidence_intervals
                )
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error predicting resource needs: {str(e)}"
            )

    async def analyze_cross_org_patterns(
        self,
        org_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Advanced analytics for cross-organization resource sharing patterns.
        Identifies optimization opportunities and collaboration patterns.
        """
        try:
            # Get collaboration data
            collaborations = await self._get_collaboration_data(org_id, time_range)
            
            # Analyze sharing patterns
            sharing_patterns = await self._analyze_sharing_patterns(collaborations)
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(
                sharing_patterns,
                collaborations
            )
            
            return {
                "sharing_patterns": sharing_patterns,
                "optimization_opportunities": optimization_opportunities,
                "collaboration_metrics": await self._calculate_collaboration_metrics(
                    collaborations
                )
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing cross-organization patterns: {str(e)}"
            )

    async def enhance_security_measures(
        self,
        org_id: str,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced security analysis and recommendations for resource sharing.
        Implements AI-driven security pattern recognition and risk assessment.
        """
        try:
            # Analyze security patterns
            security_patterns = await self._analyze_security_patterns(org_id, resource_type)
            
            # Assess risks
            risk_assessment = await self._assess_security_risks(
                org_id,
                security_patterns
            )
            
            # Generate security recommendations
            recommendations = await self._generate_security_recommendations(
                risk_assessment,
                security_patterns
            )
            
            return {
                "security_patterns": security_patterns,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "required_actions": await self._identify_required_security_actions(
                    risk_assessment
                )
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error enhancing security measures: {str(e)}"
            )

    # Helper methods for AI-driven features
    
    async def _analyze_utilization_patterns(
        self,
        org_id: str,
        metrics: Dict[str, Any],
        resource_type: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze resource utilization patterns."""
        try:
            patterns = {
                "usage_trends": {},
                "peak_periods": {},
                "underutilized_resources": [],
                "overutilized_resources": []
            }
            
            # Analyze resource-specific metrics if type specified
            resources_to_analyze = (
                {resource_type: metrics["by_resource_type"][resource_type]}
                if resource_type and resource_type in metrics["by_resource_type"]
                else metrics["by_resource_type"]
            )
            
            for res_type, count in resources_to_analyze.items():
                # Calculate basic usage metrics
                usage = metrics["usage_metrics"].get(res_type, 0)
                allocation = count
                utilization_rate = usage / allocation if allocation > 0 else 0
                
                # Record usage trends
                patterns["usage_trends"][res_type] = {
                    "allocation": allocation,
                    "usage": usage,
                    "utilization_rate": utilization_rate
                }
                
                # Identify peak periods (simple threshold-based)
                if utilization_rate > 0.8:  # 80% threshold
                    patterns["peak_periods"][res_type] = {
                        "utilization_rate": utilization_rate,
                        "frequency": "high"
                    }
                
                # Identify underutilized resources
                if utilization_rate < 0.3:  # 30% threshold
                    patterns["underutilized_resources"].append({
                        "resource_type": res_type,
                        "utilization_rate": utilization_rate,
                        "potential_savings": allocation - usage
                    })
                
                # Identify overutilized resources
                if utilization_rate > 0.9:  # 90% threshold
                    patterns["overutilized_resources"].append({
                        "resource_type": res_type,
                        "utilization_rate": utilization_rate,
                        "additional_needed": usage - allocation
                    })
            
            return patterns
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing utilization patterns: {str(e)}"
            )

    async def _generate_optimization_recommendations(
        self,
        patterns: Dict[str, Any],
        current_allocation: Dict[str, int],
        usage_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-driven optimization recommendations."""
        try:
            recommendations = []
            
            # Process underutilized resources
            for resource in patterns["underutilized_resources"]:
                res_type = resource["resource_type"]
                current = current_allocation.get(res_type, 0)
                
                # Calculate optimal allocation
                optimal = int(current * (resource["utilization_rate"] + 0.2))  # Add 20% buffer
                
                if optimal < current:
                    recommendations.append({
                        "resource_type": res_type,
                        "action": "reduce_allocation",
                        "current_allocation": current,
                        "recommended_allocation": optimal,
                        "potential_savings": current - optimal,
                        "priority": "high" if resource["utilization_rate"] < 0.2 else "medium",
                        "reason": "Resource significantly underutilized"
                    })
            
            # Process overutilized resources
            for resource in patterns["overutilized_resources"]:
                res_type = resource["resource_type"]
                current = current_allocation.get(res_type, 0)
                
                # Calculate optimal allocation with buffer
                optimal = int(current * 1.2)  # Add 20% buffer
                
                recommendations.append({
                    "resource_type": res_type,
                    "action": "increase_allocation",
                    "current_allocation": current,
                    "recommended_allocation": optimal,
                    "additional_needed": optimal - current,
                    "priority": "high",
                    "reason": "Resource consistently overutilized"
                })
            
            # Add peak period recommendations
            for res_type, peak_data in patterns["peak_periods"].items():
                if res_type not in [r["resource_type"] for r in recommendations]:
                    recommendations.append({
                        "resource_type": res_type,
                        "action": "monitor_usage",
                        "current_allocation": current_allocation.get(res_type, 0),
                        "priority": "medium",
                        "reason": "High utilization during peak periods"
                    })
            
            return recommendations
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating optimization recommendations: {str(e)}"
            )

    async def _calculate_potential_savings(
        self,
        metrics: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate potential savings from optimization recommendations."""
        try:
            savings = {
                "resource_units": 0,
                "percentage": 0.0,
                "by_resource_type": {}
            }
            
            total_current_allocation = 0
            total_recommended_allocation = 0
            
            for rec in recommendations:
                if rec["action"] == "reduce_allocation":
                    resource_type = rec["resource_type"]
                    current = rec["current_allocation"]
                    recommended = rec["recommended_allocation"]
                    
                    # Calculate savings
                    resource_savings = current - recommended
                    savings["resource_units"] += resource_savings
                    savings["by_resource_type"][resource_type] = {
                        "units": resource_savings,
                        "percentage": (resource_savings / current * 100) if current > 0 else 0
                    }
                    
                    total_current_allocation += current
                    total_recommended_allocation += recommended
            
            # Calculate overall percentage savings
            if total_current_allocation > 0:
                savings["percentage"] = (
                    (total_current_allocation - total_recommended_allocation)
                    / total_current_allocation * 100
                )
            
            return savings
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating potential savings: {str(e)}"
            )

    async def _get_historical_usage_data(
        self,
        org_id: str,
        resource_type: Optional[str],
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get historical usage data for predictions."""
        try:
            # Get metrics for different time ranges for trend analysis
            ranges = ["24h", "7d", "30d"]
            historical_data = []
            
            for range_str in ranges:
                metrics = await self.get_sharing_metrics(org_id, range_str)
                
                if resource_type:
                    if resource_type in metrics["by_resource_type"]:
                        historical_data.append({
                            "time_range": range_str,
                            "resource_type": resource_type,
                            "allocation": metrics["by_resource_type"][resource_type],
                            "usage": metrics["usage_metrics"].get(resource_type, 0)
                        })
                else:
                    for res_type, allocation in metrics["by_resource_type"].items():
                        historical_data.append({
                            "time_range": range_str,
                            "resource_type": res_type,
                            "allocation": allocation,
                            "usage": metrics["usage_metrics"].get(res_type, 0)
                        })
            
            return historical_data
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving historical usage data: {str(e)}"
            )

    async def _generate_usage_predictions(
        self,
        historical_data: List[Dict[str, Any]],
        prediction_window: str
    ) -> List[Dict[str, Any]]:
        """Generate usage predictions using AI models."""
        # Implementation details for usage predictions
        pass

    async def _calculate_prediction_confidence(
        self,
        predictions: List[Dict[str, Any]],
        historical_data: List[Dict[str, Any]]
    ) -> List[Dict[str, float]]:
        """Calculate confidence intervals for predictions."""
        # Implementation details for confidence calculation
        pass

    async def _generate_scaling_recommendations(
        self,
        predictions: List[Dict[str, Any]],
        confidence_intervals: List[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate scaling recommendations based on predictions."""
        # Implementation details for scaling recommendations
        pass

    async def _get_collaboration_data(
        self,
        org_id: str,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get collaboration data for pattern analysis."""
        # Implementation details for collaboration data retrieval
        pass

    async def _analyze_sharing_patterns(
        self,
        collaborations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze resource sharing patterns."""
        try:
            patterns = {
                "sharing_frequency": {},
                "common_resources": {},
                "collaboration_trends": {},
                "efficiency_metrics": {}
            }

            for collab in collaborations:
                if "shared_resources" not in collab.settings:
                    continue

                # Track sharing frequency by organization
                org_pair = f"{collab.source_org_id}-{collab.target_org_id}"
                if org_pair not in patterns["sharing_frequency"]:
                    patterns["sharing_frequency"][org_pair] = 0
                patterns["sharing_frequency"][org_pair] += len(collab.settings["shared_resources"])

                # Track commonly shared resources
                for resource in collab.settings["shared_resources"]:
                    res_type = resource["resource_type"]
                    if res_type not in patterns["common_resources"]:
                        patterns["common_resources"][res_type] = 0
                    patterns["common_resources"][res_type] += 1

                # Calculate basic efficiency metrics
                active_resources = sum(
                    1 for r in collab.settings["shared_resources"]
                    if r["status"] == "active"
                )
                total_resources = len(collab.settings["shared_resources"])
                
                patterns["efficiency_metrics"][org_pair] = {
                    "active_ratio": active_resources / total_resources if total_resources > 0 else 0,
                    "total_shared": total_resources
                }

            return patterns

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing sharing patterns: {str(e)}"
            )

    async def _identify_optimization_opportunities(
        self,
        patterns: Dict[str, Any],
        collaborations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities in sharing patterns."""
        try:
            opportunities = []

            # Identify low-efficiency collaborations
            for org_pair, metrics in patterns["efficiency_metrics"].items():
                if metrics["active_ratio"] < 0.5:  # Less than 50% active resources
                    opportunities.append({
                        "type": "low_efficiency",
                        "org_pair": org_pair,
                        "details": {
                            "active_ratio": metrics["active_ratio"],
                            "total_shared": metrics["total_shared"]
                        },
                        "recommendation": "Review and cleanup inactive shared resources",
                        "priority": "medium"
                    })

            # Identify resource consolidation opportunities
            for res_type, count in patterns["common_resources"].items():
                if count > 5:  # More than 5 instances of the same resource type
                    opportunities.append({
                        "type": "consolidation",
                        "resource_type": res_type,
                        "count": count,
                        "recommendation": "Consider consolidating shared resources",
                        "priority": "medium"
                    })

            # Sort opportunities by priority
            opportunities.sort(key=lambda x: 0 if x["priority"] == "high" else 1)

            return opportunities

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error identifying optimization opportunities: {str(e)}"
            )

    async def _calculate_collaboration_metrics(
        self,
        collaborations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate collaboration effectiveness metrics."""
        # Implementation details for collaboration metrics
        pass

    async def _analyze_security_patterns(
        self,
        org_id: str,
        resource_type: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze security patterns in resource sharing."""
        try:
            # Get recent collaborations
            collaborations = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id),
                OrganizationCollaboration.type == "resource-sharing"
            ).all()

            patterns = {
                "access_patterns": {},
                "unusual_activity": [],
                "security_incidents": [],
                "risk_factors": {}
            }

            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        if resource_type and resource["resource_type"] != resource_type:
                            continue

                        # Track access patterns
                        access_level = resource["access_level"]
                        if access_level not in patterns["access_patterns"]:
                            patterns["access_patterns"][access_level] = 0
                        patterns["access_patterns"][access_level] += 1

                        # Check for high-risk access levels
                        if access_level in ["admin", "write"]:
                            patterns["risk_factors"][resource["id"]] = {
                                "type": "high_access_level",
                                "details": f"High-privilege {access_level} access granted",
                                "severity": "high" if access_level == "admin" else "medium"
                            }

                        # Check for unusual activity (simple threshold-based)
                        if "usage_metrics" in resource:
                            avg_usage = sum(resource["usage_metrics"].values()) / len(resource["usage_metrics"])
                            for metric, value in resource["usage_metrics"].items():
                                if value > avg_usage * 2:  # Simple threshold: 2x average
                                    patterns["unusual_activity"].append({
                                        "resource_id": resource["id"],
                                        "metric": metric,
                                        "value": value,
                                        "average": avg_usage,
                                        "severity": "medium"
                                    })

            return patterns

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing security patterns: {str(e)}"
            )

    async def _assess_security_risks(
        self,
        org_id: str,
        patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess security risks based on patterns."""
        try:
            risk_assessment = {
                "overall_risk_level": "low",
                "risk_factors": [],
                "immediate_concerns": [],
                "recommendations": []
            }

            # Assess access pattern risks
            high_privilege_count = sum(
                count for level, count in patterns["access_patterns"].items()
                if level in ["admin", "write"]
            )
            total_access = sum(patterns["access_patterns"].values())
            
            if total_access > 0:
                high_privilege_ratio = high_privilege_count / total_access
                if high_privilege_ratio > 0.5:  # More than 50% high-privilege access
                    risk_assessment["risk_factors"].append({
                        "type": "excessive_privileges",
                        "severity": "high",
                        "details": f"{int(high_privilege_ratio * 100)}% of access is high-privilege"
                    })

            # Assess unusual activity
            if len(patterns["unusual_activity"]) > 0:
                risk_assessment["risk_factors"].append({
                    "type": "unusual_activity",
                    "severity": "medium",
                    "details": f"Detected {len(patterns['unusual_activity'])} instances of unusual activity"
                })

            # Set overall risk level
            high_risks = sum(1 for r in risk_assessment["risk_factors"] if r["severity"] == "high")
            medium_risks = sum(1 for r in risk_assessment["risk_factors"] if r["severity"] == "medium")
            
            if high_risks > 0:
                risk_assessment["overall_risk_level"] = "high"
            elif medium_risks > 2:
                risk_assessment["overall_risk_level"] = "medium"

            return risk_assessment

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error assessing security risks: {str(e)}"
            )

    async def _generate_security_recommendations(
        self,
        risk_assessment: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate security recommendations."""
        # Implementation details for security recommendations
        pass

    async def _identify_required_security_actions(
        self,
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify required security actions based on risk assessment."""
        # Implementation here
        pass 