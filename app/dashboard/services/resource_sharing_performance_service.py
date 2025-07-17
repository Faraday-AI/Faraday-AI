"""
Resource Sharing Performance Service

This module provides performance monitoring and metrics collection for resource sharing
operations in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Prometheus metrics
RESOURCE_SHARING_OPS = Counter(
    'resource_sharing_operations_total',
    'Total number of resource sharing operations',
    ['operation_type', 'status']
)

RESOURCE_SHARING_LATENCY = Histogram(
    'resource_sharing_latency_seconds',
    'Latency of resource sharing operations',
    ['operation_type']
)

ACTIVE_SHARED_RESOURCES = Gauge(
    'active_shared_resources',
    'Number of active shared resources',
    ['org_id']
)

CACHE_OPERATIONS = Counter(
    'resource_sharing_cache_operations_total',
    'Total number of cache operations',
    ['operation_type', 'status']
)

class ResourceSharingPerformanceService:
    def __init__(self):
        """Initialize the performance monitoring service."""
        self.operation_times = {}
        self.batch_metrics = {
            "batch_sizes": [],
            "processing_times": [],
            "success_rates": []
        }

    async def record_operation_start(self, operation_type: str, correlation_id: str):
        """Record the start of an operation."""
        self.operation_times[correlation_id] = {
            "type": operation_type,
            "start_time": time.time()
        }

    async def record_operation_end(
        self,
        correlation_id: str,
        status: str = "success"
    ):
        """Record the end of an operation and calculate metrics."""
        if correlation_id in self.operation_times:
            start_time = self.operation_times[correlation_id]["start_time"]
            operation_type = self.operation_times[correlation_id]["type"]
            duration = time.time() - start_time

            # Record Prometheus metrics
            RESOURCE_SHARING_OPS.labels(
                operation_type=operation_type,
                status=status
            ).inc()
            
            RESOURCE_SHARING_LATENCY.labels(
                operation_type=operation_type
            ).observe(duration)

            del self.operation_times[correlation_id]
            return duration

    async def record_batch_metrics(
        self,
        batch_size: int,
        processing_time: float,
        success_rate: float
    ):
        """Record metrics for batch operations."""
        self.batch_metrics["batch_sizes"].append(batch_size)
        self.batch_metrics["processing_times"].append(processing_time)
        self.batch_metrics["success_rates"].append(success_rate)

        # Keep only last 1000 metrics
        max_metrics = 1000
        if len(self.batch_metrics["batch_sizes"]) > max_metrics:
            self.batch_metrics["batch_sizes"] = self.batch_metrics["batch_sizes"][-max_metrics:]
            self.batch_metrics["processing_times"] = self.batch_metrics["processing_times"][-max_metrics:]
            self.batch_metrics["success_rates"] = self.batch_metrics["success_rates"][-max_metrics:]

    async def record_cache_operation(
        self,
        operation_type: str,
        status: str = "success"
    ):
        """Record cache operation metrics."""
        CACHE_OPERATIONS.labels(
            operation_type=operation_type,
            status=status
        ).inc()

    async def update_active_resources(self, org_id: str, count: int):
        """Update the count of active shared resources for an organization."""
        ACTIVE_SHARED_RESOURCES.labels(org_id=org_id).set(count)

    async def get_performance_metrics(
        self,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """Get aggregated performance metrics."""
        try:
            # Calculate batch operation metrics
            avg_batch_size = sum(self.batch_metrics["batch_sizes"]) / len(self.batch_metrics["batch_sizes"]) \
                if self.batch_metrics["batch_sizes"] else 0
            avg_processing_time = sum(self.batch_metrics["processing_times"]) / len(self.batch_metrics["processing_times"]) \
                if self.batch_metrics["processing_times"] else 0
            avg_success_rate = sum(self.batch_metrics["success_rates"]) / len(self.batch_metrics["success_rates"]) \
                if self.batch_metrics["success_rates"] else 0

            return {
                "batch_operations": {
                    "average_batch_size": avg_batch_size,
                    "average_processing_time": avg_processing_time,
                    "average_success_rate": avg_success_rate,
                    "total_batches": len(self.batch_metrics["batch_sizes"])
                },
                "cache_operations": {
                    "hits": CACHE_OPERATIONS.labels(
                        operation_type="get",
                        status="success"
                    )._value.get(),
                    "misses": CACHE_OPERATIONS.labels(
                        operation_type="get",
                        status="miss"
                    )._value.get()
                },
                "latency": {
                    "share_resource": RESOURCE_SHARING_LATENCY.labels(
                        operation_type="share_resource"
                    )._value.get(),
                    "get_resources": RESOURCE_SHARING_LATENCY.labels(
                        operation_type="get_resources"
                    )._value.get(),
                    "update_resource": RESOURCE_SHARING_LATENCY.labels(
                        operation_type="update_resource"
                    )._value.get()
                }
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting performance metrics: {str(e)}"
            ) 