"""
Monitoring Service

This module provides monitoring and metrics collection for the dashboard,
integrating with Prometheus and Grafana for visualization.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy.orm import Session
from fastapi import HTTPException
import redis

from ..models import (
    ContextInteraction,
    SharedContext,
    GPTPerformance
)
from ..models.context import GPTContext

# Prometheus metrics
RECOMMENDATION_REQUESTS = Counter(
    'gpt_recommendation_requests_total',
    'Total number of GPT recommendation requests',
    ['user_id', 'category']
)

RECOMMENDATION_LATENCY = Histogram(
    'gpt_recommendation_latency_seconds',
    'Latency of GPT recommendation calculations',
    ['category']
)

CONTEXT_SWITCHES = Counter(
    'gpt_context_switches_total',
    'Total number of GPT context switches',
    ['source_category', 'target_category']
)

ACTIVE_CONTEXTS = Gauge(
    'gpt_active_contexts',
    'Number of active GPT contexts',
    ['user_id']
)

CONTEXT_SHARING_LATENCY = Histogram(
    'gpt_context_sharing_latency_seconds',
    'Latency of context sharing operations',
    ['source_category', 'target_category']
)

GPT_PERFORMANCE = Gauge(
    'gpt_performance_score',
    'Performance score of GPTs',
    ['gpt_id', 'metric_type']
)

class MonitoringService:
    def __init__(self, db: Session, redis_url: str = "redis://localhost:6379"):
        self.db = db
        self.redis = redis.from_url(redis_url)
        self.cache_ttl = 300  # 5 minutes

    async def record_recommendation_request(
        self,
        user_id: str,
        category: str,
        duration: float
    ):
        """Record metrics for a recommendation request."""
        RECOMMENDATION_REQUESTS.labels(user_id=user_id, category=category).inc()
        RECOMMENDATION_LATENCY.labels(category=category).observe(duration)

    async def record_context_switch(
        self,
        user_id: str,
        source_category: str,
        target_category: str
    ):
        """Record metrics for a context switch."""
        CONTEXT_SWITCHES.labels(
            source_category=source_category,
            target_category=target_category
        ).inc()

        # Update active contexts gauge
        active_count = await self.get_active_contexts_count(user_id)
        ACTIVE_CONTEXTS.labels(user_id=user_id).set(active_count)

    async def record_context_sharing(
        self,
        source_category: str,
        target_category: str,
        duration: float
    ):
        """Record metrics for context sharing."""
        CONTEXT_SHARING_LATENCY.labels(
            source_category=source_category,
            target_category=target_category
        ).observe(duration)

    async def update_gpt_performance_metrics(self, gpt_id: str):
        """Update performance metrics for a GPT."""
        try:
            # Get recent performance metrics
            metrics = self.db.query(GPTPerformance).filter(
                GPTPerformance.gpt_definition_id == gpt_id,
                GPTPerformance.timestamp >= datetime.utcnow() - timedelta(days=1)
            ).all()

            if not metrics:
                return

            # Calculate average scores
            accuracy_scores = []
            response_times = []
            satisfaction_scores = []

            for metric in metrics:
                data = metric.metrics or {}
                accuracy_scores.append(data.get("accuracy", 0))
                response_times.append(data.get("response_time_score", 0))
                satisfaction_scores.append(data.get("user_satisfaction", 0))

            # Update Prometheus metrics
            if accuracy_scores:
                GPT_PERFORMANCE.labels(
                    gpt_id=gpt_id,
                    metric_type="accuracy"
                ).set(sum(accuracy_scores) / len(accuracy_scores))

            if response_times:
                GPT_PERFORMANCE.labels(
                    gpt_id=gpt_id,
                    metric_type="response_time"
                ).set(sum(response_times) / len(response_times))

            if satisfaction_scores:
                GPT_PERFORMANCE.labels(
                    gpt_id=gpt_id,
                    metric_type="satisfaction"
                ).set(sum(satisfaction_scores) / len(satisfaction_scores))

        except Exception as e:
            print(f"Error updating GPT performance metrics: {str(e)}")

    async def get_active_contexts_count(self, user_id: str) -> int:
        """Get count of active contexts for a user."""
        cache_key = f"active_contexts:{user_id}"
        
        # Try to get from cache
        cached_count = self.redis.get(cache_key)
        if cached_count is not None:
            return int(cached_count)

        # Query database
        count = self.db.query(GPTContext).filter(
            GPTContext.user_id == user_id,
            GPTContext.is_active == True
        ).count()

        # Cache the result
        self.redis.setex(cache_key, self.cache_ttl, str(count))
        
        return count

    async def get_performance_summary(self, gpt_id: str) -> Dict:
        """Get performance summary for a GPT."""
        cache_key = f"performance_summary:{gpt_id}"
        
        # Try to get from cache
        cached_summary = self.redis.get(cache_key)
        if cached_summary is not None:
            return eval(cached_summary)  # Safe as we control the cached data

        # Calculate summary
        try:
            metrics = self.db.query(GPTPerformance).filter(
                GPTPerformance.gpt_definition_id == gpt_id,
                GPTPerformance.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).all()

            summary = {
                "accuracy": 0,
                "response_time": 0,
                "satisfaction": 0,
                "total_interactions": len(metrics)
            }

            if metrics:
                for metric in metrics:
                    data = metric.metrics or {}
                    summary["accuracy"] += data.get("accuracy", 0)
                    summary["response_time"] += data.get("response_time_score", 0)
                    summary["satisfaction"] += data.get("user_satisfaction", 0)

                count = len(metrics)
                summary["accuracy"] /= count
                summary["response_time"] /= count
                summary["satisfaction"] /= count

            # Cache the summary
            self.redis.setex(cache_key, self.cache_ttl, str(summary))
            
            return summary

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting performance summary: {str(e)}"
            )

    async def get_context_sharing_metrics(
        self,
        user_id: str,
        time_range: str = "24h"
    ) -> Dict:
        """Get metrics about context sharing patterns."""
        cache_key = f"context_sharing:{user_id}:{time_range}"
        
        # Try to get from cache
        cached_metrics = self.redis.get(cache_key)
        if cached_metrics is not None:
            return eval(cached_metrics)  # Safe as we control the cached data

        try:
            # Calculate time range
            if time_range == "24h":
                start_time = datetime.utcnow() - timedelta(days=1)
            elif time_range == "7d":
                start_time = datetime.utcnow() - timedelta(days=7)
            else:
                start_time = datetime.utcnow() - timedelta(days=30)

            # Get shared contexts
            shared_contexts = self.db.query(SharedContext).join(
                GPTContext
            ).filter(
                GPTContext.user_id == user_id,
                SharedContext.created_at >= start_time
            ).all()

            metrics = {
                "total_shares": len(shared_contexts),
                "category_pairs": {},
                "most_shared_gpts": {},
                "average_sharing_frequency": 0
            }

            if shared_contexts:
                # Analyze sharing patterns
                for context in shared_contexts:
                    pair = f"{context.source_gpt.category}->{context.target_gpt.category}"
                    metrics["category_pairs"][pair] = metrics["category_pairs"].get(pair, 0) + 1
                    
                    metrics["most_shared_gpts"][context.source_gpt_id] = \
                        metrics["most_shared_gpts"].get(context.source_gpt_id, 0) + 1
                    metrics["most_shared_gpts"][context.target_gpt_id] = \
                        metrics["most_shared_gpts"].get(context.target_gpt_id, 0) + 1

                # Calculate sharing frequency (shares per day)
                time_diff = datetime.utcnow() - start_time
                metrics["average_sharing_frequency"] = len(shared_contexts) / time_diff.days

            # Cache the metrics
            self.redis.setex(cache_key, self.cache_ttl, str(metrics))
            
            return metrics

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting context sharing metrics: {str(e)}"
            )

    async def get_cpu_utilization(self, gpt_id: str, time_range: str) -> Dict:
        """Get CPU utilization metrics for a GPT."""
        cache_key = f"cpu_utilization:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query CPU metrics from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        utilization = {
            "average": 0,
            "max": 0,
            "min": 0,
            "percentiles": {}
        }
        
        if metrics:
            cpu_values = [m.metrics.get("cpu_utilization", 0) for m in metrics]
            utilization["average"] = sum(cpu_values) / len(cpu_values)
            utilization["max"] = max(cpu_values)
            utilization["min"] = min(cpu_values)
            utilization["percentiles"] = {
                "50th": self._calculate_percentile(cpu_values, 50),
                "90th": self._calculate_percentile(cpu_values, 90),
                "95th": self._calculate_percentile(cpu_values, 95)
            }
        
        self.redis.setex(cache_key, self.cache_ttl, str(utilization))
        return utilization

    async def get_cpu_cores(self, gpt_id: str) -> int:
        """Get number of CPU cores allocated to a GPT."""
        cache_key = f"cpu_cores:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query CPU cores from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        cores = gpt.resource_allocation.get("cpu_cores", 1) if gpt else 1
        
        self.redis.setex(cache_key, self.cache_ttl, str(cores))
        return cores

    async def get_cpu_load(self, gpt_id: str, time_range: str) -> Dict:
        """Get CPU load metrics for a GPT."""
        cache_key = f"cpu_load:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query CPU load from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        load = {
            "1min": 0,
            "5min": 0,
            "15min": 0
        }
        
        if metrics:
            load_values = [m.metrics.get("cpu_load", {}) for m in metrics]
            load["1min"] = sum(l.get("1min", 0) for l in load_values) / len(load_values)
            load["5min"] = sum(l.get("5min", 0) for l in load_values) / len(load_values)
            load["15min"] = sum(l.get("15min", 0) for l in load_values) / len(load_values)
        
        self.redis.setex(cache_key, self.cache_ttl, str(load))
        return load

    async def get_cpu_threads(self, gpt_id: str) -> int:
        """Get number of CPU threads used by a GPT."""
        cache_key = f"cpu_threads:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query CPU threads from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        threads = gpt.resource_allocation.get("cpu_threads", 1) if gpt else 1
        
        self.redis.setex(cache_key, self.cache_ttl, str(threads))
        return threads

    async def get_memory_utilization(self, gpt_id: str, time_range: str) -> Dict:
        """Get memory utilization metrics for a GPT."""
        cache_key = f"memory_utilization:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query memory metrics from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        utilization = {
            "average": 0,
            "max": 0,
            "min": 0,
            "percentiles": {}
        }
        
        if metrics:
            memory_values = [m.metrics.get("memory_utilization", 0) for m in metrics]
            utilization["average"] = sum(memory_values) / len(memory_values)
            utilization["max"] = max(memory_values)
            utilization["min"] = min(memory_values)
            utilization["percentiles"] = {
                "50th": self._calculate_percentile(memory_values, 50),
                "90th": self._calculate_percentile(memory_values, 90),
                "95th": self._calculate_percentile(memory_values, 95)
            }
        
        self.redis.setex(cache_key, self.cache_ttl, str(utilization))
        return utilization

    async def get_memory_total(self, gpt_id: str) -> int:
        """Get total memory allocated to a GPT."""
        cache_key = f"memory_total:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query total memory from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        total = gpt.resource_allocation.get("memory_total", 1024) if gpt else 1024
        
        self.redis.setex(cache_key, self.cache_ttl, str(total))
        return total

    async def get_memory_used(self, gpt_id: str) -> int:
        """Get used memory by a GPT."""
        cache_key = f"memory_used:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query used memory from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        used = gpt.resource_allocation.get("memory_used", 0) if gpt else 0
        
        self.redis.setex(cache_key, self.cache_ttl, str(used))
        return used

    async def get_memory_free(self, gpt_id: str) -> int:
        """Get free memory available to a GPT."""
        total = await self.get_memory_total(gpt_id)
        used = await self.get_memory_used(gpt_id)
        return total - used

    async def get_memory_swap(self, gpt_id: str) -> Dict:
        """Get swap memory usage for a GPT."""
        cache_key = f"memory_swap:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query swap memory from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        swap = gpt.resource_allocation.get("memory_swap", {}) if gpt else {}
        
        self.redis.setex(cache_key, self.cache_ttl, str(swap))
        return swap

    async def get_network_bandwidth(self, gpt_id: str, time_range: str) -> Dict:
        """Get network bandwidth metrics for a GPT."""
        cache_key = f"network_bandwidth:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query network metrics from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        bandwidth = {
            "in": 0,
            "out": 0,
            "total": 0
        }
        
        if metrics:
            network_values = [m.metrics.get("network_bandwidth", {}) for m in metrics]
            bandwidth["in"] = sum(n.get("in", 0) for n in network_values) / len(network_values)
            bandwidth["out"] = sum(n.get("out", 0) for n in network_values) / len(network_values)
            bandwidth["total"] = bandwidth["in"] + bandwidth["out"]
        
        self.redis.setex(cache_key, self.cache_ttl, str(bandwidth))
        return bandwidth

    async def get_network_connections(self, gpt_id: str) -> int:
        """Get number of active network connections for a GPT."""
        cache_key = f"network_connections:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query network connections from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        connections = gpt.resource_allocation.get("network_connections", 0) if gpt else 0
        
        self.redis.setex(cache_key, self.cache_ttl, str(connections))
        return connections

    async def get_network_latency(self, gpt_id: str, time_range: str) -> Dict:
        """Get network latency metrics for a GPT."""
        cache_key = f"network_latency:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query network latency from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        latency = {
            "average": 0,
            "max": 0,
            "min": 0,
            "percentiles": {}
        }
        
        if metrics:
            latency_values = [m.metrics.get("network_latency", 0) for m in metrics]
            latency["average"] = sum(latency_values) / len(latency_values)
            latency["max"] = max(latency_values)
            latency["min"] = min(latency_values)
            latency["percentiles"] = {
                "50th": self._calculate_percentile(latency_values, 50),
                "90th": self._calculate_percentile(latency_values, 90),
                "95th": self._calculate_percentile(latency_values, 95)
            }
        
        self.redis.setex(cache_key, self.cache_ttl, str(latency))
        return latency

    async def get_network_errors(self, gpt_id: str, time_range: str) -> Dict:
        """Get network error metrics for a GPT."""
        cache_key = f"network_errors:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query network errors from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        errors = {
            "total": 0,
            "by_type": {},
            "rate": 0
        }
        
        if metrics:
            error_values = [m.metrics.get("network_errors", {}) for m in metrics]
            errors["total"] = sum(e.get("total", 0) for e in error_values)
            errors["by_type"] = self._aggregate_error_types(error_values)
            errors["rate"] = errors["total"] / len(metrics)
        
        self.redis.setex(cache_key, self.cache_ttl, str(errors))
        return errors

    async def get_storage_utilization(self, gpt_id: str, time_range: str) -> Dict:
        """Get storage utilization metrics for a GPT."""
        cache_key = f"storage_utilization:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query storage metrics from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        utilization = {
            "average": 0,
            "max": 0,
            "min": 0,
            "percentiles": {}
        }
        
        if metrics:
            storage_values = [m.metrics.get("storage_utilization", 0) for m in metrics]
            utilization["average"] = sum(storage_values) / len(storage_values)
            utilization["max"] = max(storage_values)
            utilization["min"] = min(storage_values)
            utilization["percentiles"] = {
                "50th": self._calculate_percentile(storage_values, 50),
                "90th": self._calculate_percentile(storage_values, 90),
                "95th": self._calculate_percentile(storage_values, 95)
            }
        
        self.redis.setex(cache_key, self.cache_ttl, str(utilization))
        return utilization

    async def get_storage_total(self, gpt_id: str) -> int:
        """Get total storage allocated to a GPT."""
        cache_key = f"storage_total:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query total storage from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        total = gpt.resource_allocation.get("storage_total", 1024) if gpt else 1024
        
        self.redis.setex(cache_key, self.cache_ttl, str(total))
        return total

    async def get_storage_used(self, gpt_id: str) -> int:
        """Get used storage by a GPT."""
        cache_key = f"storage_used:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return int(cached_data)
        
        # Query used storage from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        used = gpt.resource_allocation.get("storage_used", 0) if gpt else 0
        
        self.redis.setex(cache_key, self.cache_ttl, str(used))
        return used

    async def get_storage_free(self, gpt_id: str) -> int:
        """Get free storage available to a GPT."""
        total = await self.get_storage_total(gpt_id)
        used = await self.get_storage_used(gpt_id)
        return total - used

    async def get_storage_iops(self, gpt_id: str, time_range: str) -> Dict:
        """Get storage IOPS metrics for a GPT."""
        cache_key = f"storage_iops:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query storage IOPS from database
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).all()
        
        iops = {
            "read": 0,
            "write": 0,
            "total": 0
        }
        
        if metrics:
            iops_values = [m.metrics.get("storage_iops", {}) for m in metrics]
            iops["read"] = sum(i.get("read", 0) for i in iops_values) / len(iops_values)
            iops["write"] = sum(i.get("write", 0) for i in iops_values) / len(iops_values)
            iops["total"] = iops["read"] + iops["write"]
        
        self.redis.setex(cache_key, self.cache_ttl, str(iops))
        return iops

    async def get_resource_trend(self, gpt_id: str, resource_type: str, time_range: str) -> Dict:
        """Get trend analysis for a resource type."""
        cache_key = f"resource_trend:{gpt_id}:{resource_type}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Get historical data
        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= self._get_time_range_start(time_range)
        ).order_by(GPTPerformance.timestamp).all()
        
        trend = {
            "values": [],
            "timestamps": [],
            "slope": 0,
            "direction": "stable"
        }
        
        if metrics:
            for metric in metrics:
                trend["values"].append(metric.metrics.get(f"{resource_type}_utilization", 0))
                trend["timestamps"].append(metric.timestamp.isoformat())
            
            # Calculate trend slope
            if len(trend["values"]) > 1:
                x = list(range(len(trend["values"])))
                y = trend["values"]
                slope = self._calculate_slope(x, y)
                trend["slope"] = slope
                trend["direction"] = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        
        self.redis.setex(cache_key, self.cache_ttl, str(trend))
        return trend

    async def get_resource_forecast(self, gpt_id: str, resource_type: str, time_range: str) -> Dict:
        """Get forecast for a resource type."""
        cache_key = f"resource_forecast:{gpt_id}:{resource_type}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Get historical data
        trend = await self.get_resource_trend(gpt_id, resource_type, time_range)
        
        forecast = {
            "next_hour": 0,
            "next_day": 0,
            "next_week": 0,
            "confidence": 0
        }
        
        if trend["values"]:
            # Simple linear extrapolation
            last_value = trend["values"][-1]
            slope = trend["slope"]
            
            forecast["next_hour"] = last_value + slope
            forecast["next_day"] = last_value + slope * 24
            forecast["next_week"] = last_value + slope * 24 * 7
            
            # Calculate confidence based on trend stability
            forecast["confidence"] = self._calculate_forecast_confidence(trend["values"])
        
        self.redis.setex(cache_key, self.cache_ttl, str(forecast))
        return forecast

    async def get_resource_optimization(self, gpt_id: str, time_range: str) -> List[Dict]:
        """Get optimization suggestions for resources."""
        cache_key = f"resource_optimization:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        suggestions = []
        
        # Check CPU optimization
        cpu_utilization = await self.get_cpu_utilization(gpt_id, time_range)
        if cpu_utilization["average"] > 80:
            suggestions.append({
                "resource": "cpu",
                "issue": "High CPU utilization",
                "suggestion": "Consider scaling up CPU resources",
                "impact": "High",
                "priority": "Critical"
            })
        
        # Check memory optimization
        memory_utilization = await self.get_memory_utilization(gpt_id, time_range)
        if memory_utilization["average"] > 80:
            suggestions.append({
                "resource": "memory",
                "issue": "High memory utilization",
                "suggestion": "Consider scaling up memory resources",
                "impact": "High",
                "priority": "Critical"
            })
        
        # Check storage optimization
        storage_utilization = await self.get_storage_utilization(gpt_id, time_range)
        if storage_utilization["average"] > 80:
            suggestions.append({
                "resource": "storage",
                "issue": "High storage utilization",
                "suggestion": "Consider scaling up storage resources",
                "impact": "Medium",
                "priority": "High"
            })
        
        self.redis.setex(cache_key, self.cache_ttl, str(suggestions))
        return suggestions

    async def get_resource_optimization_impact(self, gpt_id: str, time_range: str) -> Dict:
        """Get impact analysis for resource optimization."""
        cache_key = f"resource_optimization_impact:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        impact = {
            "performance": 0,
            "cost": 0,
            "reliability": 0,
            "recommendations": []
        }
        
        # Get current resource usage
        cpu_utilization = await self.get_cpu_utilization(gpt_id, time_range)
        memory_utilization = await self.get_memory_utilization(gpt_id, time_range)
        storage_utilization = await self.get_storage_utilization(gpt_id, time_range)
        
        # Calculate impact scores
        impact["performance"] = self._calculate_performance_impact(
            cpu_utilization, memory_utilization, storage_utilization
        )
        impact["cost"] = self._calculate_cost_impact(
            cpu_utilization, memory_utilization, storage_utilization
        )
        impact["reliability"] = self._calculate_reliability_impact(
            cpu_utilization, memory_utilization, storage_utilization
        )
        
        # Generate recommendations
        impact["recommendations"] = self._generate_resource_recommendations(
            cpu_utilization, memory_utilization, storage_utilization
        )
        
        self.redis.setex(cache_key, self.cache_ttl, str(impact))
        return impact

    async def get_resource_recommendations(self, gpt_id: str, time_range: str) -> List[Dict]:
        """Get resource optimization recommendations."""
        cache_key = f"resource_recommendations:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        recommendations = []
        
        # Get current resource usage
        cpu_utilization = await self.get_cpu_utilization(gpt_id, time_range)
        memory_utilization = await self.get_memory_utilization(gpt_id, time_range)
        storage_utilization = await self.get_storage_utilization(gpt_id, time_range)
        
        # Generate recommendations based on utilization
        if cpu_utilization["average"] > 80:
            recommendations.append({
                "resource": "cpu",
                "action": "scale_up",
                "reason": "High CPU utilization",
                "priority": "high",
                "estimated_impact": "Improved performance"
            })
        elif cpu_utilization["average"] < 20:
            recommendations.append({
                "resource": "cpu",
                "action": "scale_down",
                "reason": "Low CPU utilization",
                "priority": "medium",
                "estimated_impact": "Cost optimization"
            })
        
        if memory_utilization["average"] > 80:
            recommendations.append({
                "resource": "memory",
                "action": "scale_up",
                "reason": "High memory utilization",
                "priority": "high",
                "estimated_impact": "Improved performance"
            })
        elif memory_utilization["average"] < 20:
            recommendations.append({
                "resource": "memory",
                "action": "scale_down",
                "reason": "Low memory utilization",
                "priority": "medium",
                "estimated_impact": "Cost optimization"
            })
        
        if storage_utilization["average"] > 80:
            recommendations.append({
                "resource": "storage",
                "action": "scale_up",
                "reason": "High storage utilization",
                "priority": "medium",
                "estimated_impact": "Prevent storage issues"
            })
        
        self.redis.setex(cache_key, self.cache_ttl, str(recommendations))
        return recommendations

    async def get_resource_alerts(self, gpt_id: str, time_range: str) -> List[Dict]:
        """Get active resource alerts for a GPT."""
        cache_key = f"resource_alerts:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        alerts = []
        
        # Check CPU alerts
        cpu_utilization = await self.get_cpu_utilization(gpt_id, time_range)
        if cpu_utilization["average"] > 90:
            alerts.append({
                "resource": "cpu",
                "severity": "critical",
                "message": "Critical CPU utilization",
                "threshold": 90,
                "current": cpu_utilization["average"]
            })
        elif cpu_utilization["average"] > 80:
            alerts.append({
                "resource": "cpu",
                "severity": "warning",
                "message": "High CPU utilization",
                "threshold": 80,
                "current": cpu_utilization["average"]
            })
        
        # Check memory alerts
        memory_utilization = await self.get_memory_utilization(gpt_id, time_range)
        if memory_utilization["average"] > 90:
            alerts.append({
                "resource": "memory",
                "severity": "critical",
                "message": "Critical memory utilization",
                "threshold": 90,
                "current": memory_utilization["average"]
            })
        elif memory_utilization["average"] > 80:
            alerts.append({
                "resource": "memory",
                "severity": "warning",
                "message": "High memory utilization",
                "threshold": 80,
                "current": memory_utilization["average"]
            })
        
        # Check storage alerts
        storage_utilization = await self.get_storage_utilization(gpt_id, time_range)
        if storage_utilization["average"] > 90:
            alerts.append({
                "resource": "storage",
                "severity": "critical",
                "message": "Critical storage utilization",
                "threshold": 90,
                "current": storage_utilization["average"]
            })
        elif storage_utilization["average"] > 80:
            alerts.append({
                "resource": "storage",
                "severity": "warning",
                "message": "High storage utilization",
                "threshold": 80,
                "current": storage_utilization["average"]
            })
        
        self.redis.setex(cache_key, self.cache_ttl, str(alerts))
        return alerts

    async def get_resource_alert_history(self, gpt_id: str, time_range: str) -> List[Dict]:
        """Get historical resource alerts for a GPT."""
        cache_key = f"resource_alert_history:{gpt_id}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Query alert history from database
        alerts = self.db.query(Alert).filter(
            Alert.gpt_id == gpt_id,
            Alert.timestamp >= self._get_time_range_start(time_range),
            Alert.alert_type.in_(["cpu", "memory", "storage"])
        ).order_by(Alert.timestamp.desc()).all()
        
        history = []
        for alert in alerts:
            history.append({
                "resource": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "threshold": alert.threshold,
                "value": alert.value,
                "timestamp": alert.timestamp.isoformat()
            })
        
        self.redis.setex(cache_key, self.cache_ttl, str(history))
        return history

    async def get_resource_alert_thresholds(self, gpt_id: str) -> Dict:
        """Get resource alert thresholds for a GPT."""
        cache_key = f"resource_alert_thresholds:{gpt_id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Get thresholds from database
        gpt = self.db.query(GPTContext).filter(GPTContext.id == gpt_id).first()
        thresholds = gpt.alert_thresholds if gpt else {}
        
        # Set default thresholds if not configured
        if not thresholds:
            thresholds = {
                "cpu": {
                    "warning": 80,
                    "critical": 90
                },
                "memory": {
                    "warning": 80,
                    "critical": 90
                },
                "storage": {
                    "warning": 80,
                    "critical": 90
                }
            }
        
        self.redis.setex(cache_key, self.cache_ttl, str(thresholds))
        return thresholds

    async def get_resource_benchmark(self, gpt_id: str, resource_type: str, time_range: str) -> Dict:
        """Get performance benchmarks for a resource type."""
        cache_key = f"resource_benchmark:{gpt_id}:{resource_type}:{time_range}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return eval(cached_data)
        
        # Get current metrics
        if resource_type == "cpu":
            metrics = await self.get_cpu_utilization(gpt_id, time_range)
        elif resource_type == "memory":
            metrics = await self.get_memory_utilization(gpt_id, time_range)
        elif resource_type == "network":
            metrics = await self.get_network_bandwidth(gpt_id, time_range)
        elif resource_type == "storage":
            metrics = await self.get_storage_utilization(gpt_id, time_range)
        else:
            metrics = {}
        
        # Get industry benchmarks
        benchmarks = self._get_industry_benchmarks(resource_type)
        
        benchmark = {
            "current": metrics,
            "industry_average": benchmarks.get("average", 0),
            "industry_best": benchmarks.get("best", 0),
            "industry_worst": benchmarks.get("worst", 0),
            "percentile": self._calculate_percentile_rank(metrics.get("average", 0), benchmarks)
        }
        
        self.redis.setex(cache_key, self.cache_ttl, str(benchmark))
        return benchmark

    def _get_time_range_start(self, time_range: str) -> datetime:
        """Get start time for a time range."""
        now = datetime.utcnow()
        if time_range == "24h":
            return now - timedelta(hours=24)
        elif time_range == "7d":
            return now - timedelta(days=7)
        elif time_range == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate a percentile value from a list of values."""
        if not values:
            return 0
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * (percentile / 100)
        f = int(k)
        c = int(k) + 1
        if c >= len(sorted_values):
            return sorted_values[f]
        d0 = sorted_values[f] * (c - k)
        d1 = sorted_values[c] * (k - f)
        return d0 + d1

    def _calculate_slope(self, x: List[int], y: List[float]) -> float:
        """Calculate the slope of a trend line."""
        if len(x) != len(y) or len(x) < 2:
            return 0
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

    def _calculate_forecast_confidence(self, values: List[float]) -> float:
        """Calculate confidence score for a forecast."""
        if len(values) < 2:
            return 0
        # Calculate variance
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        # Convert variance to confidence (0-1)
        max_variance = max(values) - min(values)
        if max_variance == 0:
            return 1
        confidence = 1 - (variance / max_variance)
        return max(0, min(1, confidence))

    def _aggregate_error_types(self, error_values: List[Dict]) -> Dict:
        """Aggregate error types from multiple error values."""
        error_types = {}
        for errors in error_values:
            for error_type, count in errors.get("by_type", {}).items():
                error_types[error_type] = error_types.get(error_type, 0) + count
        return error_types

    def _calculate_performance_impact(
        self,
        cpu_utilization: Dict,
        memory_utilization: Dict,
        storage_utilization: Dict
    ) -> float:
        """Calculate performance impact score."""
        scores = [
            cpu_utilization.get("average", 0),
            memory_utilization.get("average", 0),
            storage_utilization.get("average", 0)
        ]
        return sum(scores) / len(scores)

    def _calculate_cost_impact(
        self,
        cpu_utilization: Dict,
        memory_utilization: Dict,
        storage_utilization: Dict
    ) -> float:
        """Calculate cost impact score."""
        # Lower utilization means higher cost impact (underutilization)
        scores = [
            100 - cpu_utilization.get("average", 0),
            100 - memory_utilization.get("average", 0),
            100 - storage_utilization.get("average", 0)
        ]
        return sum(scores) / len(scores)

    def _calculate_reliability_impact(
        self,
        cpu_utilization: Dict,
        memory_utilization: Dict,
        storage_utilization: Dict
    ) -> float:
        """Calculate reliability impact score."""
        # Higher utilization means higher reliability impact
        scores = [
            cpu_utilization.get("average", 0),
            memory_utilization.get("average", 0),
            storage_utilization.get("average", 0)
        ]
        return sum(scores) / len(scores)

    def _generate_resource_recommendations(
        self,
        cpu_utilization: Dict,
        memory_utilization: Dict,
        storage_utilization: Dict
    ) -> List[Dict]:
        """Generate resource optimization recommendations."""
        recommendations = []
        
        # CPU recommendations
        if cpu_utilization.get("average", 0) > 80:
            recommendations.append({
                "resource": "cpu",
                "action": "scale_up",
                "reason": "High CPU utilization",
                "priority": "high"
            })
        elif cpu_utilization.get("average", 0) < 20:
            recommendations.append({
                "resource": "cpu",
                "action": "scale_down",
                "reason": "Low CPU utilization",
                "priority": "medium"
            })
        
        # Memory recommendations
        if memory_utilization.get("average", 0) > 80:
            recommendations.append({
                "resource": "memory",
                "action": "scale_up",
                "reason": "High memory utilization",
                "priority": "high"
            })
        elif memory_utilization.get("average", 0) < 20:
            recommendations.append({
                "resource": "memory",
                "action": "scale_down",
                "reason": "Low memory utilization",
                "priority": "medium"
            })
        
        # Storage recommendations
        if storage_utilization.get("average", 0) > 80:
            recommendations.append({
                "resource": "storage",
                "action": "scale_up",
                "reason": "High storage utilization",
                "priority": "medium"
            })
        
        return recommendations

    def _get_industry_benchmarks(self, resource_type: str) -> Dict:
        """Get industry benchmarks for a resource type."""
        # This is a placeholder - in a real implementation, these would come from
        # a database or external service
        benchmarks = {
            "cpu": {
                "average": 50,
                "best": 30,
                "worst": 80
            },
            "memory": {
                "average": 60,
                "best": 40,
                "worst": 90
            },
            "network": {
                "average": 40,
                "best": 20,
                "worst": 70
            },
            "storage": {
                "average": 70,
                "best": 50,
                "worst": 95
            }
        }
        return benchmarks.get(resource_type, {})

    def _calculate_percentile_rank(self, value: float, benchmarks: Dict) -> float:
        """Calculate percentile rank against industry benchmarks."""
        if not benchmarks:
            return 0
        best = benchmarks.get("best", 0)
        worst = benchmarks.get("worst", 0)
        if best == worst:
            return 0
        percentile = ((value - best) / (worst - best)) * 100
        return max(0, min(100, percentile)) 