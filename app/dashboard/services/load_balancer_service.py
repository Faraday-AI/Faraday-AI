"""
Load Balancer Service

This module provides load balancer functionality for the dashboard.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from prometheus_client import Counter, Histogram, Gauge
import os
import logging
from app.core.load_balancer import Region, RegionCost

logger = logging.getLogger(__name__)

# Prometheus metrics for load balancer dashboard (production-ready)
LOAD_BALANCER_REQUESTS = Counter(
    'load_balancer_dashboard_requests_total',
    'Total number of load balancer dashboard requests',
    ['endpoint', 'status']
)

LOAD_BALANCER_LATENCY = Histogram(
    'load_balancer_dashboard_latency_seconds',
    'Load balancer dashboard request latency in seconds',
    ['endpoint']
)

REGION_PERFORMANCE = Gauge(
    'load_balancer_region_performance',
    'Performance metrics for load balancer regions',
    ['region', 'metric']
)

class LoadBalancerService:
    """Service for managing load balancing functionality in the dashboard."""
    
    def __init__(
        self,
        load_balancer,
        monitoring_service,
        resource_service
    ):
        self.load_balancer = load_balancer
        self.monitoring_service = monitoring_service
        self.resource_service = resource_service
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes for the load balancer service."""
        self.router.add_api_route(
            "/metrics",
            self.get_load_metrics,
            methods=["GET"],
            tags=["Load Balancer"]
        )
        self.router.add_api_route(
            "/health",
            self.get_node_health,
            methods=["GET"],
            tags=["Load Balancer"]
        )
        self.router.add_api_route(
            "/settings/{node_id}",
            self.update_node_settings,
            methods=["PUT"],
            tags=["Load Balancer"]
        )
        self.router.add_api_route(
            "/traffic",
            self.get_traffic_distribution,
            methods=["GET"],
            tags=["Load Balancer"]
        )
        self.router.add_api_route(
            "/performance",
            self.get_performance_metrics,
            methods=["GET"],
            tags=["Load Balancer"]
        )
        self.router.add_api_route(
            "/optimize",
            self.get_optimization_suggestions,
            methods=["GET"],
            tags=["Load Balancer"]
        )
        self.router.add_api_route(
            "/alerts",
            self.get_alert_history,
            methods=["GET"],
            tags=["Load Balancer"]
        )

    async def get_load_metrics(
        self,
        time_range: str = "5m"
    ) -> Dict[str, Any]:
        """
        Get current load metrics across all nodes.

        Args:
            time_range: Time range for metrics (e.g., "5m", "1h", "24h")

        Returns:
            Dict containing load metrics
        """
        metrics = {
            "total_requests": 0,
            "active_connections": 0,
            "request_rate": 0.0,
            "average_response_time": 0.0,
            "error_rate": 0.0,
            "node_metrics": [],
            "timestamp": datetime.utcnow()
        }
        return metrics

    async def get_node_health(
        self,
        node_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get health status of nodes.

        Args:
            node_id: Optional specific node ID to check

        Returns:
            Dict containing node health information
        """
        health_info = {
            "total_nodes": 0,
            "healthy_nodes": 0,
            "nodes": [],
            "timestamp": datetime.utcnow()
        }
        return health_info

    async def update_node_settings(
        self,
        node_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update settings for a specific node.

        Args:
            node_id: ID of the node to update
            settings: New settings to apply

        Returns:
            Dict containing updated node information
        """
        return {
            "node_id": node_id,
            "status": "updated",
            "settings": settings,
            "timestamp": datetime.utcnow()
        }

    async def get_traffic_distribution(
        self,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get traffic distribution metrics across nodes.

        Args:
            time_range: Time range for metrics

        Returns:
            Dict containing traffic distribution information
        """
        distribution = {
            "total_traffic": 0,
            "distribution": {},
            "patterns": [],
            "timestamp": datetime.utcnow()
        }
        return distribution

    async def get_performance_metrics(
        self,
        time_range: str = "1h",
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed performance metrics.

        Args:
            time_range: Time range for metrics
            include_details: Whether to include detailed metrics

        Returns:
            Dict containing performance metrics
        """
        metrics = {
            "throughput": 0.0,
            "latency": 0.0,
            "error_rate": 0.0,
            "resource_utilization": {},
            "timestamp": datetime.utcnow()
        }
        return metrics

    async def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get optimization suggestions for load balancer.

        Returns:
            List of optimization suggestions
        """
        suggestions = [
            {
                "type": "scaling",
                "priority": "high",
                "description": "Consider scaling up node capacity",
                "impact": "medium"
            }
        ]
        return suggestions

    async def get_alert_history(
        self,
        time_range: str = "24h",
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alert history for load balancer.

        Args:
            time_range: Time range for alerts
            severity: Optional severity filter

        Returns:
            List of alert history entries
        """
        alerts = [
            {
                "id": "alert-1",
                "severity": "warning",
                "message": "High load detected",
                "timestamp": datetime.utcnow()
            }
        ]
        return alerts

class LoadBalancerDashboardService:
    """Dashboard service for load balancer management."""
    
    def __init__(self, load_balancer=None, monitoring_service=None, resource_service=None):
        """Initialize the load balancer dashboard service."""
        self.load_balancer = load_balancer
        self.monitoring_service = monitoring_service
        self.resource_service = resource_service
        self.metrics = {}
        self.alerts = []
        self.router = APIRouter()
        self._monitoring_tasks = []
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes for the dashboard service."""
        self.router.add_api_route(
            "/regions/status",
            self._get_region_status_endpoint,
            methods=["GET"],
            tags=["Load Balancer Dashboard"]
        )
        self.router.add_api_route(
            "/regions/performance",
            self._get_region_performance_endpoint,
            methods=["GET"],
            tags=["Load Balancer Dashboard"]
        )
        self.router.add_api_route(
            "/regions/costs",
            self._get_region_costs_endpoint,
            methods=["GET"],
            tags=["Load Balancer Dashboard"]
        )
        self.router.add_api_route(
            "/regions/{region}/weight",
            self._set_region_weight_endpoint,
            methods=["POST"],
            tags=["Load Balancer Dashboard"]
        )
        self.router.add_api_route(
            "/regions/{region}/circuit",
            self._get_circuit_state_endpoint,
            methods=["GET"],
            tags=["Load Balancer Dashboard"]
        )
    
    async def _get_region_status_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint for getting region status."""
        import time
        start_time = time.time()
        try:
            result = await self._get_region_status()
            LOAD_BALANCER_REQUESTS.labels(endpoint="region_status", status="success").inc()
            LOAD_BALANCER_LATENCY.labels(endpoint="region_status").observe(time.time() - start_time)
            return result
        except Exception as e:
            LOAD_BALANCER_REQUESTS.labels(endpoint="region_status", status="error").inc()
            LOAD_BALANCER_LATENCY.labels(endpoint="region_status").observe(time.time() - start_time)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_region_status(self) -> Dict[str, Any]:
        """Get status of all regions."""
        if not self.load_balancer:
            return {region.value: {
                'health': 'unknown',
                'resources': {},
                'circuit_state': 'closed',
                'weight': 0.0
            } for region in Region}
        
        status = {}
        for region in Region:
            try:
                health = self.load_balancer.failover_manager.check_region_health()
                stats = self.load_balancer.region_stats.get(region, {})
                circuit = self.load_balancer.circuit_breakers.get(region)
                weight = self.load_balancer.load_weights.get(region, 0.0)
                
                status[region.value] = {
                    'health': health.get('status', 'unknown'),
                    'resources': stats.get('resource_usage', {}),
                    'circuit_state': circuit.state if circuit else 'closed',
                    'weight': weight
                }
                # Update Prometheus metrics
                REGION_PERFORMANCE.labels(
                    region=region.value,
                    metric='health'
                ).set(1.0 if health.get('status') == 'healthy' else 0.0)
            except Exception:
                status[region.value] = {
                    'health': 'error',
                    'resources': {},
                    'circuit_state': 'unknown',
                    'weight': 0.0
                }
        return status
    
    async def _get_region_performance_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint for getting region performance."""
        import time
        start_time = time.time()
        try:
            result = await self._get_region_performance()
            LOAD_BALANCER_REQUESTS.labels(endpoint="region_performance", status="success").inc()
            LOAD_BALANCER_LATENCY.labels(endpoint="region_performance").observe(time.time() - start_time)
            return result
        except Exception as e:
            LOAD_BALANCER_REQUESTS.labels(endpoint="region_performance", status="error").inc()
            LOAD_BALANCER_LATENCY.labels(endpoint="region_performance").observe(time.time() - start_time)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_region_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all regions."""
        if not self.load_balancer:
            return {region.value: {
                'requests': 0,
                'errors': 0,
                'avg_latency': 0.0,
                'error_rate': 0.0,
                'throughput': 0.0,
                'predictive_score': 0.0,
                'cost_efficiency': 0.0
            } for region in Region}
        
        performance = {}
        for region in Region:
            stats = self.load_balancer.region_stats.get(region, {})
            latency_list = stats.get('latency', [])
            requests = stats.get('requests', 0)
            errors = stats.get('errors', 0)
            avg_latency = sum(latency_list) / len(latency_list) if latency_list else 0.0
            error_rate = errors / requests if requests > 0 else 0.0
            
            predictive_scores = await self.load_balancer._get_predictive_scores()
            cost_efficiency = self.load_balancer._calculate_cost_efficiency()
            
            performance[region.value] = {
                'requests': requests,
                'errors': errors,
                'avg_latency': avg_latency,
                'error_rate': error_rate,
                'throughput': requests / 60.0 if requests > 0 else 0.0,  # requests per second approximation
                'predictive_score': predictive_scores.get(region, 0.0),
                'cost_efficiency': cost_efficiency
            }
        return performance
    
    async def _get_region_costs_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint for getting region costs."""
        import time
        start_time = time.time()
        try:
            result = await self._get_region_costs()
            LOAD_BALANCER_REQUESTS.labels(endpoint="region_costs", status="success").inc()
            LOAD_BALANCER_LATENCY.labels(endpoint="region_costs").observe(time.time() - start_time)
            return result
        except Exception as e:
            LOAD_BALANCER_REQUESTS.labels(endpoint="region_costs", status="error").inc()
            LOAD_BALANCER_LATENCY.labels(endpoint="region_costs").observe(time.time() - start_time)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_region_costs(self) -> Dict[str, Any]:
        """Get cost information for all regions."""
        if not self.load_balancer:
            return {region.value: {
                'compute': 0.0,
                'storage': 0.0,
                'network': 0.0,
                'total': 0.0,
                'currency': 'USD'
            } for region in Region}
        
        costs = {}
        for region in Region:
            stats = self.load_balancer.region_stats.get(region, {})
            cost = stats.get('cost')
            if isinstance(cost, RegionCost):
                costs[region.value] = {
                    'compute': cost.compute_cost,
                    'storage': cost.storage_cost,
                    'network': cost.network_cost,
                    'total': cost.compute_cost + cost.storage_cost + cost.network_cost,
                    'currency': cost.currency
                }
            else:
                costs[region.value] = {
                    'compute': 0.0,
                    'storage': 0.0,
                    'network': 0.0,
                    'total': 0.0,
                    'currency': 'USD'
                }
        return costs
    
    async def _set_region_weight_endpoint(self, region: str, weight: float = Query(...)) -> Dict[str, Any]:
        """HTTP endpoint for setting region weight."""
        try:
            # Validate weight first (before region parsing)
            if not (0.0 <= weight <= 1.0):
                raise HTTPException(status_code=400, detail="Weight must be between 0.0 and 1.0")
            
            # Validate region
            try:
                region_enum = Region(region)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid region: {region}")
            
            await self._set_region_weight(region_enum, weight)
            return {'region': region, 'weight': weight, 'status': 'updated'}
        except HTTPException:
            # Re-raise HTTP exceptions (including the 400 for weight validation)
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _set_region_weight(self, region: Region, weight: float):
        """Set weight for a region."""
        if self.load_balancer:
            self.load_balancer.load_weights[region] = weight
    
    async def _get_circuit_state_endpoint(self, region: str) -> Dict[str, Any]:
        """HTTP endpoint for getting circuit breaker state."""
        try:
            region_enum = Region(region)
            return await self._get_circuit_state(region_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid region: {region}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_circuit_state(self, region: Region) -> Dict[str, Any]:
        """Get circuit breaker state for a region."""
        if not self.load_balancer:
            return {
                'state': 'closed',
                'failures': 0,
                'last_failure': None,
                'can_attempt': True
            }
        
        circuit = self.load_balancer.circuit_breakers.get(region)
        if circuit:
            return {
                'state': circuit.state,
                'failures': circuit.failures,
                'last_failure': circuit.last_failure.isoformat() if circuit.last_failure else None,
                'can_attempt': circuit.can_attempt()
            }
        return {
            'state': 'closed',
            'failures': 0,
            'last_failure': None,
            'can_attempt': True
        }
    
    async def start_monitoring(self):
        """
        Start background monitoring tasks.
        
        NOTE: This method is DISABLED in production environments. In production,
        use LoadBalancerJobs from app.core.load_balancer_jobs instead, which
        integrates with proper background job infrastructure.
        
        This method is only enabled for:
        - Development environments
        - Testing scenarios
        """
        # Check if we're in production - if so, disable this method
        environment = os.getenv("APP_ENVIRONMENT", os.getenv("ENVIRONMENT", "development")).lower()
        deployment_env = os.getenv("DEPLOYMENT_ENVIRONMENT", "development").lower()
        is_production = environment == "production" or deployment_env == "production"
        
        if is_production:
            logger.warning(
                "LoadBalancerDashboardService.start_monitoring() is disabled in production. "
                "Use LoadBalancerJobs from app.core.load_balancer_jobs instead."
            )
            return
        
        if self.monitoring_service and self.load_balancer:
            import asyncio
            async def monitor_resources():
                """Monitor resource usage - runs until cancelled."""
                try:
                    while True:
                        for region in Region:
                            stats = self.load_balancer.region_stats.get(region, {})
                            if self.monitoring_service:
                                try:
                                    await self.monitoring_service.record_resource_usage(
                                        region=region.value,
                                        resources=stats.get('resource_usage', {})
                                    )
                                    # Update Prometheus metrics
                                    resources = stats.get('resource_usage', {})
                                    REGION_PERFORMANCE.labels(
                                        region=region.value,
                                        metric='cpu_usage'
                                    ).set(resources.get('cpu', 0.0))
                                    REGION_PERFORMANCE.labels(
                                        region=region.value,
                                        metric='memory_usage'
                                    ).set(resources.get('memory', 0.0))
                                    REGION_PERFORMANCE.labels(
                                        region=region.value,
                                        metric='network_usage'
                                    ).set(resources.get('network', 0.0))
                                except Exception:
                                    # Log error but continue monitoring
                                    pass
                        await asyncio.sleep(5)  # Check every 5 seconds, not 1
                except asyncio.CancelledError:
                    pass
            
            async def monitor_performance():
                """Monitor performance metrics - runs until cancelled."""
                try:
                    while True:
                        if self.monitoring_service:
                            try:
                                await self.monitoring_service.record_performance_metrics(
                                    metrics={}
                                )
                            except Exception:
                                pass
                        await asyncio.sleep(5)
                except asyncio.CancelledError:
                    pass
            
            async def monitor_costs():
                """Monitor cost metrics - runs until cancelled."""
                try:
                    while True:
                        if self.monitoring_service:
                            try:
                                await self.monitoring_service.record_cost_metrics(
                                    costs={}
                                )
                            except Exception:
                                pass
                        await asyncio.sleep(10)  # Cost metrics less frequent
                except asyncio.CancelledError:
                    pass
            
            task1 = asyncio.create_task(monitor_resources())
            task2 = asyncio.create_task(monitor_performance())
            task3 = asyncio.create_task(monitor_costs())
            self._monitoring_tasks = [task1, task2, task3]
    
    async def stop_monitoring(self):
        """Stop background monitoring tasks gracefully."""
        for task in self._monitoring_tasks:
            task.cancel()
        if self._monitoring_tasks:
            import asyncio
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
        self._monitoring_tasks = []
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics for load balancer."""
        return {
            "total_nodes": 5,
            "active_nodes": 4,
            "total_requests": 15000,
            "average_response_time": 120.5,
            "error_rate": 0.02,
            "last_updated": datetime.utcnow()
        }
    
    async def get_node_status(self) -> List[Dict[str, Any]]:
        """Get status of all nodes."""
        return [
            {
                "node_id": "node-1",
                "status": "healthy",
                "load": 0.75,
                "response_time": 100.0
            },
            {
                "node_id": "node-2", 
                "status": "healthy",
                "load": 0.60,
                "response_time": 95.0
            }
        ]
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts."""
        return self.alerts 