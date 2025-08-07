"""
Monitoring components for the Faraday AI application.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
import time
import logging
from typing import Dict, Any, Optional, List
from functools import wraps
import psutil
import os
import inspect
import socket
import threading
from datetime import datetime, timedelta
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# Request Metrics
REQUEST_COUNT = Counter('ai_analytics_requests_total', 'Total number of requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('ai_analytics_request_duration_seconds', 'Request duration in seconds', ['endpoint'])
REQUEST_SIZE = Histogram('ai_analytics_request_size_bytes', 'Request size in bytes', ['endpoint'])
RESPONSE_SIZE = Histogram('ai_analytics_response_size_bytes', 'Response size in bytes', ['endpoint'])

# Model Metrics
MODEL_PREDICTION_TIME = Histogram('ai_analytics_model_prediction_seconds', 'Model prediction time in seconds', ['model_name'])
MODEL_LOAD_TIME = Histogram('ai_analytics_model_load_seconds', 'Model load time in seconds', ['model_name'])
MODEL_MEMORY_USAGE = Gauge('ai_analytics_model_memory_bytes', 'Model memory usage in bytes', ['model_name'])
MODEL_GPU_USAGE = Gauge('ai_analytics_model_gpu_usage_percent', 'Model GPU usage percentage', ['model_name'])
MODEL_BATCH_SIZE = Histogram('ai_analytics_model_batch_size', 'Model batch size', ['model_name'])
MODEL_ERROR_RATE = Gauge('ai_analytics_model_error_rate', 'Model error rate', ['model_name'])

# Cache Metrics
CACHE_HITS = Counter('ai_analytics_cache_hits_total', 'Total number of cache hits', ['endpoint'])
CACHE_MISSES = Counter('ai_analytics_cache_misses_total', 'Total number of cache misses', ['endpoint'])
CACHE_SIZE = Gauge('ai_analytics_cache_size_bytes', 'Cache size in bytes')
CACHE_KEYS = Gauge('ai_analytics_cache_keys_total', 'Total number of cache keys')
CACHE_EVICTIONS = Counter('ai_analytics_cache_evictions_total', 'Total number of cache evictions')
CACHE_LATENCY = Histogram('ai_analytics_cache_latency_seconds', 'Cache operation latency in seconds')
CACHE_HIT_COUNT = CACHE_HITS  # Alias for backward compatibility

# Database Metrics
DB_CONNECTIONS = Gauge('ai_analytics_db_connections', 'Number of active database connections')
DB_QUERY_TIME = Histogram('ai_analytics_db_query_seconds', 'Database query time in seconds', ['query_type'])
DB_TRANSACTIONS = Counter('ai_analytics_db_transactions_total', 'Total number of database transactions', ['type'])
DB_ERRORS = Counter('ai_analytics_db_errors_total', 'Total number of database errors', ['error_type'])
DB_POOL_SIZE = Gauge('ai_analytics_db_pool_size', 'Database connection pool size')
DB_ACTIVE_CONNECTIONS = Gauge('ai_analytics_db_active_connections', 'Number of active database connections')

# System Metrics
CPU_USAGE = Gauge('ai_analytics_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('ai_analytics_memory_usage_bytes', 'Memory usage in bytes')
DISK_USAGE = Gauge('ai_analytics_disk_usage_bytes', 'Disk usage in bytes')
DISK_IO = Counter('ai_analytics_disk_io_bytes', 'Disk I/O in bytes', ['operation'])
NETWORK_IO = Counter('ai_analytics_network_io_bytes', 'Network I/O in bytes', ['operation'])
THREAD_COUNT = Gauge('ai_analytics_thread_count', 'Number of threads')
FILE_DESCRIPTORS = Gauge('ai_analytics_file_descriptors', 'Number of open file descriptors')

# Error Metrics
ERROR_COUNT = Counter('ai_analytics_errors_total', 'Total number of errors', ['endpoint', 'error_type'])
ERROR_RATE = Gauge('ai_analytics_error_rate', 'Error rate per minute')
EXCEPTION_COUNT = Counter('ai_analytics_exceptions_total', 'Total number of exceptions', ['type'])
VALIDATION_ERRORS = Counter('ai_analytics_validation_errors_total', 'Total number of validation errors', ['field'])

# API Metrics
API_CALLS = Counter('ai_analytics_api_calls_total', 'Total number of API calls', ['api_name'])
API_LATENCY = Histogram('ai_analytics_api_latency_seconds', 'API call latency in seconds', ['api_name'])
API_ERRORS = Counter('ai_analytics_api_errors_total', 'Total number of API errors', ['api_name', 'error_type'])
API_RATE_LIMIT = Counter('ai_analytics_api_rate_limit_total', 'Total number of API rate limit hits', ['api_name'])

# Performance Metrics
PERFORMANCE_SCORE = Gauge('ai_analytics_performance_score', 'Application performance score')
RESPONSE_TIME_P95 = Summary('ai_analytics_response_time_p95', '95th percentile of response time', ['endpoint'])
RESPONSE_TIME_P99 = Summary('ai_analytics_response_time_p99', '99th percentile of response time', ['endpoint'])
THROUGHPUT = Gauge('ai_analytics_throughput', 'Requests per second', ['endpoint'])

def track_metrics(endpoint: str = None):
    """Decorator to track request metrics."""
    def decorator(func):
        sig = inspect.signature(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                # Simply call the function with the provided arguments
                result = await func(*args, **kwargs)
                
                # Use function name as endpoint if none provided
                endpoint_name = endpoint or func.__name__
                duration = time.time() - start_time
                
                # Update metrics
                REQUEST_COUNT.labels(endpoint=endpoint_name, status='success').inc()
                REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(duration)
                RESPONSE_TIME_P95.labels(endpoint=endpoint_name).observe(duration)
                RESPONSE_TIME_P99.labels(endpoint=endpoint_name).observe(duration)
                THROUGHPUT.labels(endpoint=endpoint_name).inc()
                
                return result
            except Exception as e:
                endpoint_name = endpoint or func.__name__
                REQUEST_COUNT.labels(endpoint=endpoint_name, status='error').inc()
                ERROR_COUNT.labels(endpoint=endpoint_name, error_type=type(e).__name__).inc()
                EXCEPTION_COUNT.labels(type=type(e).__name__).inc()
                raise e
        return wrapper
    return decorator

def track_model_performance(model_name: str):
    """Decorator to track model performance metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Update metrics
                MODEL_PREDICTION_TIME.labels(model_name=model_name).observe(duration)
                MODEL_MEMORY_USAGE.labels(model_name=model_name).set(psutil.Process().memory_info().rss)
                MODEL_ERROR_RATE.labels(model_name=model_name).set(0)
                
                return result
            except Exception as e:
                MODEL_ERROR_RATE.labels(model_name=model_name).set(1)
                ERROR_COUNT.labels(endpoint=model_name, error_type=type(e).__name__).inc()
                raise
        return wrapper
    return decorator

class SystemMonitor:
    def __init__(self):
        """Initialize system monitor."""
        self.process = psutil.Process(os.getpid())
        self._start_time = time.time()
        self._last_network_io = psutil.net_io_counters()
        self._last_disk_io = psutil.disk_io_counters()

    def update_system_metrics(self):
        """Update system metrics."""
        try:
            # CPU usage
            CPU_USAGE.set(self.process.cpu_percent())
            
            # Memory usage
            memory_info = self.process.memory_info()
            MEMORY_USAGE.set(memory_info.rss)
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            DISK_USAGE.set(disk_usage.used)
            
            # Thread count
            THREAD_COUNT.set(self.process.num_threads())
            
            # File descriptors
            FILE_DESCRIPTORS.set(len(self.process.open_files()))
            
            # Network I/O
            current_network_io = psutil.net_io_counters()
            NETWORK_IO.labels(operation='bytes_sent').inc(current_network_io.bytes_sent - self._last_network_io.bytes_sent)
            NETWORK_IO.labels(operation='bytes_recv').inc(current_network_io.bytes_recv - self._last_network_io.bytes_recv)
            self._last_network_io = current_network_io
            
            # Disk I/O
            current_disk_io = psutil.disk_io_counters()
            DISK_IO.labels(operation='read_bytes').inc(current_disk_io.read_bytes - self._last_disk_io.read_bytes)
            DISK_IO.labels(operation='write_bytes').inc(current_disk_io.write_bytes - self._last_disk_io.write_bytes)
            self._last_disk_io = current_disk_io
            
            logger.debug("System metrics updated successfully")
        except Exception as e:
            logger.error(f"Error updating system metrics: {str(e)}", exc_info=True)

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            return {
                "uptime": time.time() - self._start_time,
                "cpu_usage": self.process.cpu_percent(),
                "memory_usage": self.process.memory_info().rss,
                "disk_usage": psutil.disk_usage('/').used,
                "thread_count": self.process.num_threads(),
                "open_files": len(self.process.open_files()),
                "connections": len(self.process.connections()),
                "network_io": psutil.net_io_counters()._asdict(),
                "disk_io": psutil.disk_io_counters()._asdict()
            }
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}", exc_info=True)
            return {}

class ModelMonitor:
    def __init__(self):
        """Initialize model monitor."""
        self.model_metrics: Dict[str, Dict[str, Any]] = {}

    def track_model_load(self, model_name: str, load_time: float):
        """Track model load time."""
        MODEL_LOAD_TIME.labels(model_name=model_name).observe(load_time)
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = {}
        self.model_metrics[model_name]['load_time'] = load_time

    def track_model_prediction(self, model_name: str, prediction_time: float, success: bool):
        """Track model prediction metrics."""
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = {}
        
        metrics = self.model_metrics[model_name]
        metrics['last_prediction_time'] = prediction_time
        metrics['total_predictions'] = metrics.get('total_predictions', 0) + 1
        metrics['successful_predictions'] = metrics.get('successful_predictions', 0) + (1 if success else 0)
        metrics['success_rate'] = metrics['successful_predictions'] / metrics['total_predictions']
        
        # Update Prometheus metrics
        MODEL_PREDICTION_TIME.labels(model_name=model_name).observe(prediction_time)
        MODEL_ERROR_RATE.labels(model_name=model_name).set(0 if success else 1)

    def get_model_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all model metrics."""
        return self.model_metrics

class CacheMonitor:
    def __init__(self, redis_client: redis.Redis):
        """Initialize cache monitor."""
        self.redis_client = redis_client

    def update_cache_metrics(self):
        """Update cache metrics."""
        try:
            info = self.redis_client.info()
            CACHE_SIZE.set(info['used_memory'])
            CACHE_KEYS.set(info['db0']['keys'])
            CACHE_EVICTIONS.inc(info['evicted_keys'])
        except Exception as e:
            logger.error(f"Error updating cache metrics: {str(e)}", exc_info=True)

class DatabaseMonitor:
    def __init__(self, engine):
        """Initialize database monitor."""
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def update_database_metrics(self):
        """Update database metrics."""
        try:
            with self.engine.connect() as conn:
                # Get connection pool metrics
                pool = self.engine.pool
                DB_POOL_SIZE.set(pool.size())
                DB_ACTIVE_CONNECTIONS.set(pool.checkedin())
                DB_CONNECTIONS.set(pool.checkedout())
        except Exception as e:
            logger.error(f"Error updating database metrics: {str(e)}", exc_info=True)

class NetworkMonitor:
    def __init__(self):
        """Initialize network monitor."""
        self.hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(self.hostname)

    def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        try:
            return {
                "hostname": self.hostname,
                "ip_address": self.ip_address,
                "connections": psutil.net_connections(),
                "interfaces": psutil.net_if_addrs(),
                "stats": psutil.net_if_stats()
            }
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}", exc_info=True)
            return {}

class ErrorMonitor:
    def __init__(self):
        """Initialize error monitor."""
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: List[datetime] = []

    def track_error(self, error_type: str):
        """Track error occurrence."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.error_timestamps.append(datetime.utcnow())
        self._cleanup_old_errors()

    def _cleanup_old_errors(self):
        """Clean up old error timestamps."""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        self.error_timestamps = [ts for ts in self.error_timestamps if ts > one_hour_ago]

    def get_error_rate(self) -> float:
        """Get error rate per minute."""
        if not self.error_timestamps:
            return 0.0
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_errors = len([ts for ts in self.error_timestamps if ts > one_minute_ago])
        return recent_errors / 60.0

class PerformanceMonitor:
    def __init__(self):
        """Initialize performance monitor."""
        self.response_times: Dict[str, List[float]] = {}

    def track_response_time(self, endpoint: str, response_time: float):
        """Track response time."""
        if endpoint not in self.response_times:
            self.response_times[endpoint] = []
        self.response_times[endpoint].append(response_time)
        self._cleanup_old_metrics()

    def _cleanup_old_metrics(self):
        """Clean up old metrics."""
        for endpoint in self.response_times:
            if len(self.response_times[endpoint]) > 1000:
                self.response_times[endpoint] = self.response_times[endpoint][-1000:]

    def calculate_performance_score(self) -> float:
        """Calculate performance score."""
        if not self.response_times:
            return 100.0
        
        total_score = 0
        count = 0
        
        for endpoint, times in self.response_times.items():
            if times:
                avg_time = sum(times) / len(times)
                score = 100.0 * (1.0 / (1.0 + avg_time))
                total_score += score
                count += 1
        
        return total_score / count if count > 0 else 100.0

# Initialize monitors
system_monitor = SystemMonitor()
model_monitor = ModelMonitor()
cache_monitor = CacheMonitor(redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
))
database_monitor = DatabaseMonitor(create_engine(settings.DATABASE_URL))
network_monitor = NetworkMonitor()
error_monitor = ErrorMonitor()
performance_monitor = PerformanceMonitor() 