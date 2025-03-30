from prometheus_client import Counter, Histogram, Gauge
import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
import psutil
import os

logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('ai_analytics_requests_total', 'Total number of requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('ai_analytics_request_duration_seconds', 'Request duration in seconds', ['endpoint'])
MODEL_PREDICTION_TIME = Histogram('ai_analytics_model_prediction_seconds', 'Model prediction time in seconds', ['model_name'])
CACHE_HITS = Counter('ai_analytics_cache_hits_total', 'Total number of cache hits', ['endpoint'])
CACHE_MISSES = Counter('ai_analytics_cache_misses_total', 'Total number of cache misses', ['endpoint'])
ERROR_COUNT = Counter('ai_analytics_errors_total', 'Total number of errors', ['endpoint', 'error_type'])
API_CALLS = Counter('ai_analytics_api_calls_total', 'Total number of API calls', ['api_name'])
RATE_LIMIT_HITS = Counter('ai_analytics_rate_limit_hits_total', 'Total number of rate limit hits', ['client_id'])

# System metrics
CPU_USAGE = Gauge('ai_analytics_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('ai_analytics_memory_usage_bytes', 'Memory usage in bytes')
DISK_USAGE = Gauge('ai_analytics_disk_usage_bytes', 'Disk usage in bytes')
MODEL_LOAD_TIME = Histogram('ai_analytics_model_load_seconds', 'Model load time in seconds', ['model_name'])

def track_metrics(endpoint: str):
    """Decorator to track request metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                REQUEST_COUNT.labels(endpoint=endpoint, status='success').inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start_time)
                return result
            except Exception as e:
                REQUEST_COUNT.labels(endpoint=endpoint, status='error').inc()
                ERROR_COUNT.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                raise
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
                MODEL_PREDICTION_TIME.labels(model_name=model_name).observe(time.time() - start_time)
                return result
            except Exception as e:
                ERROR_COUNT.labels(endpoint=model_name, error_type=type(e).__name__).inc()
                raise
        return wrapper
    return decorator

class SystemMonitor:
    def __init__(self):
        """Initialize system monitor."""
        self.process = psutil.Process(os.getpid())
        self._start_time = time.time()

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
                "connections": len(self.process.connections())
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

    def get_model_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all model metrics."""
        return self.model_metrics

# Initialize monitors
system_monitor = SystemMonitor()
model_monitor = ModelMonitor() 