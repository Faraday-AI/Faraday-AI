from prometheus_client import Counter, Histogram, Gauge
import time
import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# Request metrics
request_count = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'status'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP request duration in seconds', ['method', 'endpoint'])

# Model metrics
model_prediction_time = Histogram('model_prediction_duration_seconds', 'Time spent in model predictions', ['model_name'])
model_prediction_count = Counter('model_predictions_total', 'Total number of model predictions', ['model_name', 'status'])

# System metrics
cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
disk_usage = Gauge('system_disk_usage_bytes', 'Disk usage in bytes')

# API metrics
api_call_count = Counter('api_calls_total', 'Total number of API calls', ['api_name', 'status'])
api_call_duration = Histogram('api_call_duration_seconds', 'Time spent in API calls', ['api_name'])

# Error metrics
error_count = Counter('errors_total', 'Total number of errors', ['type', 'component'])

def track_metrics(func: Callable) -> Callable:
    """Decorator to track metrics for a function."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            # Use function name and module as defaults, don't rely on kwargs
            method_name = func.__name__
            module_name = func.__module__.split('.')[-1] if func.__module__ else 'unknown'
            
            request_latency.labels(
                method=method_name,
                endpoint=module_name
            ).observe(duration)
            request_count.labels(
                method=method_name,
                endpoint=module_name,
                status='success'
            ).inc()
            return result
        except Exception as e:
            duration = time.time() - start_time
            # Use function name and module as defaults, don't rely on kwargs
            method_name = func.__name__
            module_name = func.__module__.split('.')[-1] if func.__module__ else 'unknown'
            
            request_latency.labels(
                method=method_name,
                endpoint=module_name
            ).observe(duration)
            request_count.labels(
                method=method_name,
                endpoint=module_name,
                status='error'
            ).inc()
            error_count.labels(
                type=type(e).__name__,
                component=func.__name__
            ).inc()
            raise
    return wrapper

def track_model_performance(model_name: str):
    """Decorator to track model performance metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                model_prediction_time.labels(model_name=model_name).observe(duration)
                model_prediction_count.labels(
                    model_name=model_name,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                duration = time.time() - start_time
                model_prediction_time.labels(model_name=model_name).observe(duration)
                model_prediction_count.labels(
                    model_name=model_name,
                    status='error'
                ).inc()
                error_count.labels(
                    type=type(e).__name__,
                    component=f"{model_name}_model"
                ).inc()
                raise
        return wrapper
    return decorator

class MetricsCollector:
    """Class for collecting and managing metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def update_system_metrics(self, cpu_percent: float, memory_bytes: int, disk_bytes: int):
        """Update system metrics."""
        try:
            cpu_usage.set(cpu_percent)
            memory_usage.set(memory_bytes)
            disk_usage.set(disk_bytes)
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {str(e)}")
    
    def track_api_call(self, api_name: str, duration: float, status: str = 'success'):
        """Track API call metrics."""
        try:
            api_call_count.labels(
                api_name=api_name,
                status=status
            ).inc()
            api_call_duration.labels(api_name=api_name).observe(duration)
        except Exception as e:
            self.logger.error(f"Error tracking API call: {str(e)}")
    
    def track_error(self, error_type: str, component: str):
        """Track error metrics."""
        try:
            error_count.labels(
                type=error_type,
                component=component
            ).inc()
        except Exception as e:
            self.logger.error(f"Error tracking error metrics: {str(e)}")

# Initialize global metrics collector
metrics_collector = MetricsCollector() 