"""
Monitoring API endpoints for the Faraday AI Dashboard.
"""

from typing import Dict, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ....services.monitoring_service import MonitoringService
from ....dependencies import get_db

router = APIRouter()

@router.get("/metrics/{gpt_id}")
async def get_gpt_metrics(
    gpt_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    metrics: Optional[List[str]] = Query(None, description="Specific metrics to retrieve"),
    include_trends: bool = Query(False, description="Include trend analysis"),
    include_anomalies: bool = Query(False, description="Include anomaly detection"),
    include_correlations: bool = Query(False, description="Include metric correlations"),
    include_forecast: bool = Query(False, description="Include metric forecast"),
    include_insights: bool = Query(False, description="Include metric insights"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    include_impact: bool = Query(False, description="Include impact analysis"),
    include_benchmarks: bool = Query(False, description="Include performance benchmarks"),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for a specific GPT.
    
    Args:
        gpt_id: The ID of the GPT to monitor
        time_range: Time range for metrics (24h, 7d, 30d)
        metrics: Optional list of specific metrics to retrieve
        include_trends: Whether to include trend analysis
        include_anomalies: Whether to include anomaly detection
        include_correlations: Whether to include metric correlations
        include_forecast: Whether to include metric forecast
        include_insights: Whether to include metric insights
        include_optimization: Whether to include optimization suggestions
        include_impact: Whether to include impact analysis
        include_benchmarks: Whether to include performance benchmarks
    """
    monitoring_service = MonitoringService(db)
    result = await monitoring_service.get_performance_summary(
        gpt_id=gpt_id
    )
    
    if include_trends:
        result["trends"] = {
            "accuracy_trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="accuracy",
                time_range=time_range
            ),
            "response_time_trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="response_time",
                time_range=time_range
            ),
            "efficiency_trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="efficiency",
                time_range=time_range
            ),
            "quality_trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="quality",
                time_range=time_range
            )
        }
    
    if include_anomalies:
        result["anomalies"] = await monitoring_service.detect_anomalies(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_correlations:
        result["correlations"] = await monitoring_service.analyze_correlations(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_forecast:
        result["forecast"] = await monitoring_service.generate_forecast(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_insights:
        result["insights"] = await monitoring_service.get_metric_insights(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_optimization:
        result["optimization"] = await monitoring_service.get_optimization_suggestions(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_impact:
        result["impact"] = await monitoring_service.analyze_impact(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_benchmarks:
        result["benchmarks"] = await monitoring_service.get_performance_benchmarks(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    return result

@router.get("/contexts/{user_id}")
async def get_user_contexts(
    user_id: str,
    include_metrics: bool = Query(False, description="Include detailed context metrics"),
    include_history: bool = Query(False, description="Include context history"),
    include_patterns: bool = Query(False, description="Include context patterns"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get active contexts for a user.
    
    Args:
        user_id: The ID of the user to check
        include_metrics: Whether to include detailed context metrics
        include_history: Whether to include context history
        include_patterns: Whether to include context patterns
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    result = {
        "active_contexts": await monitoring_service.get_active_contexts_count(user_id)
    }
    
    if include_metrics:
        result["context_metrics"] = {
            "switches": monitoring_service.CONTEXT_SWITCHES._value.get(),
            "sharing_latency": monitoring_service.CONTEXT_SHARING_LATENCY._value.get(),
            "average_switch_time": await monitoring_service.get_average_switch_time(user_id),
            "context_utilization": await monitoring_service.get_context_utilization(user_id),
            "context_efficiency": await monitoring_service.get_context_efficiency(user_id)
        }
    
    if include_history:
        result["history"] = await monitoring_service.get_context_history(user_id)
    
    if include_patterns:
        result["patterns"] = await monitoring_service.get_context_patterns(user_id)
    
    if include_optimization:
        result["optimization"] = await monitoring_service.get_context_optimization(user_id)
    
    return result

@router.get("/sharing/{user_id}")
async def get_context_sharing_metrics(
    user_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_latency: bool = Query(True, description="Include latency metrics"),
    include_patterns: bool = Query(False, description="Include sharing patterns"),
    include_impact: bool = Query(False, description="Include impact analysis"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get context sharing metrics for a user.
    
    Args:
        user_id: The ID of the user to check
        time_range: Time range for metrics (24h, 7d, 30d)
        include_latency: Whether to include latency metrics
        include_patterns: Whether to include sharing patterns
        include_impact: Whether to include impact analysis
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    result = await monitoring_service.get_context_sharing_metrics(
        user_id=user_id,
        time_range=time_range
    )
    
    if include_latency:
        result["latency_metrics"] = {
            "average": monitoring_service.CONTEXT_SHARING_LATENCY._value.get(),
            "percentiles": await monitoring_service.get_latency_percentiles(user_id),
            "trends": await monitoring_service.get_latency_trends(user_id),
            "anomalies": await monitoring_service.detect_latency_anomalies(user_id)
        }
    
    if include_patterns:
        result["patterns"] = await monitoring_service.get_sharing_patterns(user_id)
    
    if include_impact:
        result["impact"] = await monitoring_service.analyze_sharing_impact(user_id)
    
    if include_optimization:
        result["optimization"] = await monitoring_service.get_sharing_optimization(user_id)
    
    return result

@router.get("/performance/{gpt_id}")
async def get_gpt_performance(
    gpt_id: str,
    metric_types: Optional[List[str]] = Query(None, description="Types of performance metrics to retrieve"),
    include_breakdown: bool = Query(False, description="Include metric breakdown by category"),
    include_trends: bool = Query(False, description="Include performance trends"),
    include_benchmarks: bool = Query(False, description="Include performance benchmarks"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get detailed performance metrics for a GPT.
    
    Args:
        gpt_id: The ID of the GPT to check
        metric_types: Optional list of metric types to retrieve
        include_breakdown: Whether to include metric breakdown by category
        include_trends: Whether to include performance trends
        include_benchmarks: Whether to include performance benchmarks
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    await monitoring_service.update_gpt_performance_metrics(gpt_id)
    
    metrics = {}
    if not metric_types or "accuracy" in metric_types:
        metrics["accuracy"] = {
            "value": monitoring_service.GPT_PERFORMANCE.labels(
                gpt_id=gpt_id,
                metric_type="accuracy"
            )._value.get(),
            "trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="accuracy"
            ),
            "anomalies": await monitoring_service.detect_metric_anomalies(
                gpt_id=gpt_id,
                metric_type="accuracy"
            )
        }
    
    if not metric_types or "response_time" in metric_types:
        metrics["response_time"] = {
            "value": monitoring_service.GPT_PERFORMANCE.labels(
                gpt_id=gpt_id,
                metric_type="response_time"
            )._value.get(),
            "trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="response_time"
            ),
            "anomalies": await monitoring_service.detect_metric_anomalies(
                gpt_id=gpt_id,
                metric_type="response_time"
            )
        }
    
    if not metric_types or "satisfaction" in metric_types:
        metrics["satisfaction"] = {
            "value": monitoring_service.GPT_PERFORMANCE.labels(
                gpt_id=gpt_id,
                metric_type="satisfaction"
            )._value.get(),
            "trend": await monitoring_service.get_metric_trend(
                gpt_id=gpt_id,
                metric_type="satisfaction"
            ),
            "anomalies": await monitoring_service.detect_metric_anomalies(
                gpt_id=gpt_id,
                metric_type="satisfaction"
            )
        }
    
    if include_breakdown:
        metrics["breakdown"] = await monitoring_service.get_performance_breakdown(gpt_id)
    
    if include_trends:
        metrics["trends"] = await monitoring_service.get_performance_trends(gpt_id)
    
    if include_benchmarks:
        metrics["benchmarks"] = await monitoring_service.get_performance_benchmarks(gpt_id)
    
    if include_optimization:
        metrics["optimization"] = await monitoring_service.get_performance_optimization(gpt_id)
    
    return metrics

@router.get("/recommendations")
async def get_recommendation_metrics(
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_latency: bool = Query(True, description="Include latency metrics"),
    include_categories: bool = Query(False, description="Include metrics by category"),
    include_accuracy: bool = Query(False, description="Include accuracy metrics"),
    include_impact: bool = Query(False, description="Include impact analysis"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get recommendation system metrics.
    
    Args:
        time_range: Time range for metrics (24h, 7d, 30d)
        include_latency: Whether to include latency metrics
        include_categories: Whether to include metrics by category
        include_accuracy: Whether to include accuracy metrics
        include_impact: Whether to include impact analysis
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    metrics = {
        "total_requests": monitoring_service.RECOMMENDATION_REQUESTS._value.get(),
        "success_rate": await monitoring_service.get_recommendation_success_rate(),
        "average_latency": monitoring_service.RECOMMENDATION_LATENCY._value.get()
    }
    
    if include_latency:
        metrics["latency"] = {
            "average": monitoring_service.RECOMMENDATION_LATENCY._value.get(),
            "percentiles": await monitoring_service.get_recommendation_latency_percentiles(),
            "trends": await monitoring_service.get_recommendation_latency_trends(),
            "anomalies": await monitoring_service.detect_recommendation_latency_anomalies()
        }
    
    if include_categories:
        metrics["categories"] = await monitoring_service.get_recommendation_category_metrics()
    
    if include_accuracy:
        metrics["accuracy"] = {
            "overall": await monitoring_service.get_recommendation_accuracy(),
            "by_category": await monitoring_service.get_recommendation_accuracy_by_category(),
            "trends": await monitoring_service.get_recommendation_accuracy_trends()
        }
    
    if include_impact:
        metrics["impact"] = await monitoring_service.analyze_recommendation_impact()
    
    if include_optimization:
        metrics["optimization"] = await monitoring_service.get_recommendation_optimization()
    
    return metrics

@router.get("/system/health")
async def get_system_health(
    include_details: bool = Query(False, description="Include detailed health metrics"),
    include_components: bool = Query(False, description="Include component health"),
    include_alerts: bool = Query(False, description="Include health alerts"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get system health metrics.
    
    Args:
        include_details: Whether to include detailed health metrics
        include_components: Whether to include component health
        include_alerts: Whether to include health alerts
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    health = {
        "status": await monitoring_service.get_system_status(),
        "uptime": await monitoring_service.get_system_uptime(),
        "load": await monitoring_service.get_system_load()
    }
    
    if include_details:
        health["details"] = {
            "cpu_usage": await monitoring_service.get_cpu_usage(),
            "memory_usage": await monitoring_service.get_memory_usage(),
            "disk_usage": await monitoring_service.get_disk_usage(),
            "network_usage": await monitoring_service.get_network_usage()
        }
    
    if include_components:
        health["components"] = await monitoring_service.get_component_health()
    
    if include_alerts:
        health["alerts"] = await monitoring_service.get_health_alerts()
    
    if include_optimization:
        health["optimization"] = await monitoring_service.get_health_optimization()
    
    return health

@router.get("/dashboard")
async def get_monitoring_dashboard(
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_detailed_metrics: bool = Query(False, description="Include detailed metrics"),
    include_health: bool = Query(True, description="Include system health"),
    include_trends: bool = Query(False, description="Include trend analysis"),
    include_alerts: bool = Query(False, description="Include alert status"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get monitoring dashboard data.
    
    Args:
        time_range: Time range for metrics (24h, 7d, 30d)
        include_detailed_metrics: Whether to include detailed metrics
        include_health: Whether to include system health
        include_trends: Whether to include trend analysis
        include_alerts: Whether to include alert status
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    dashboard = {
        "overview": await monitoring_service.get_dashboard_overview(),
        "metrics": await monitoring_service.get_dashboard_metrics(time_range)
    }
    
    if include_detailed_metrics:
        dashboard["detailed_metrics"] = await monitoring_service.get_detailed_metrics(time_range)
    
    if include_health:
        dashboard["health"] = await monitoring_service.get_system_health()
    
    if include_trends:
        dashboard["trends"] = await monitoring_service.get_dashboard_trends(time_range)
    
    if include_alerts:
        dashboard["alerts"] = await monitoring_service.get_dashboard_alerts()
    
    if include_optimization:
        dashboard["optimization"] = await monitoring_service.get_dashboard_optimization()
    
    return dashboard

@router.get("/alerts")
async def get_alerts(
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_details: bool = Query(True, description="Include alert details"),
    include_history: bool = Query(False, description="Include alert history"),
    include_impact: bool = Query(False, description="Include impact analysis"),
    include_mitigation: bool = Query(False, description="Include mitigation strategies"),
    db: Session = Depends(get_db)
):
    """
    Get system alerts.
    
    Args:
        time_range: Time range for alerts (24h, 7d, 30d)
        include_details: Whether to include alert details
        include_history: Whether to include alert history
        include_impact: Whether to include impact analysis
        include_mitigation: Whether to include mitigation strategies
    """
    monitoring_service = MonitoringService(db)
    alerts = {
        "active": await monitoring_service.get_active_alerts(),
        "count": await monitoring_service.get_alert_count(time_range)
    }
    
    if include_details:
        alerts["details"] = await monitoring_service.get_alert_details(time_range)
    
    if include_history:
        alerts["history"] = await monitoring_service.get_alert_history(time_range)
    
    if include_impact:
        alerts["impact"] = await monitoring_service.analyze_alert_impact(time_range)
    
    if include_mitigation:
        alerts["mitigation"] = await monitoring_service.get_alert_mitigation(time_range)
    
    return alerts

@router.get("/events")
async def get_events(
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_details: bool = Query(True, description="Include event details"),
    include_patterns: bool = Query(False, description="Include event patterns"),
    include_impact: bool = Query(False, description="Include impact analysis"),
    include_optimization: bool = Query(False, description="Include optimization suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get system events.
    
    Args:
        time_range: Time range for events (24h, 7d, 30d)
        include_details: Whether to include event details
        include_patterns: Whether to include event patterns
        include_impact: Whether to include impact analysis
        include_optimization: Whether to include optimization suggestions
    """
    monitoring_service = MonitoringService(db)
    events = {
        "recent": await monitoring_service.get_recent_events(time_range),
        "count": await monitoring_service.get_event_count(time_range)
    }
    
    if include_details:
        events["details"] = await monitoring_service.get_event_details(time_range)
    
    if include_patterns:
        events["patterns"] = await monitoring_service.get_event_patterns(time_range)
    
    if include_impact:
        events["impact"] = await monitoring_service.analyze_event_impact(time_range)
    
    if include_optimization:
        events["optimization"] = await monitoring_service.get_event_optimization(time_range)
    
    return events

@router.get("/insights/{gpt_id}")
async def get_gpt_insights(
    gpt_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_trends: bool = Query(True, description="Include insight trends"),
    include_patterns: bool = Query(True, description="Include usage patterns"),
    include_opportunities: bool = Query(True, description="Include optimization opportunities"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_forecasts: bool = Query(True, description="Include usage forecasts"),
    include_anomalies: bool = Query(True, description="Include anomaly detection"),
    include_correlations: bool = Query(True, description="Include metric correlations"),
    db: Session = Depends(get_db)
):
    """Get comprehensive insights for a specific GPT."""
    monitoring_service = MonitoringService(db)
    return await monitoring_service.get_gpt_insights(
        gpt_id=gpt_id,
        time_range=time_range,
        include_trends=include_trends,
        include_patterns=include_patterns,
        include_opportunities=include_opportunities,
        include_impact=include_impact,
        include_forecasts=include_forecasts,
        include_anomalies=include_anomalies,
        include_correlations=include_correlations
    )

@router.get("/optimization/{gpt_id}")
async def get_gpt_optimization(
    gpt_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_opportunities: bool = Query(True, description="Include optimization opportunities"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_recommendations: bool = Query(True, description="Include optimization recommendations"),
    include_metrics: bool = Query(True, description="Include optimization metrics"),
    include_forecasts: bool = Query(True, description="Include optimization forecasts"),
    include_benchmarks: bool = Query(True, description="Include performance benchmarks"),
    include_insights: bool = Query(True, description="Include optimization insights"),
    db: Session = Depends(get_db)
):
    """Get comprehensive optimization data for a specific GPT."""
    monitoring_service = MonitoringService(db)
    return await monitoring_service.get_gpt_optimization(
        gpt_id=gpt_id,
        time_range=time_range,
        include_opportunities=include_opportunities,
        include_impact=include_impact,
        include_recommendations=include_recommendations,
        include_metrics=include_metrics,
        include_forecasts=include_forecasts,
        include_benchmarks=include_benchmarks,
        include_insights=include_insights
    )

@router.get("/resources/{gpt_id}")
async def get_resource_utilization(
    gpt_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_cpu: bool = Query(True, description="Include CPU utilization metrics"),
    include_memory: bool = Query(True, description="Include memory utilization metrics"),
    include_network: bool = Query(True, description="Include network utilization metrics"),
    include_storage: bool = Query(True, description="Include storage utilization metrics"),
    include_trends: bool = Query(True, description="Include utilization trends"),
    include_forecast: bool = Query(True, description="Include resource forecast"),
    include_optimization: bool = Query(True, description="Include optimization suggestions"),
    include_alerts: bool = Query(True, description="Include resource alerts"),
    include_benchmarks: bool = Query(True, description="Include resource benchmarks"),
    db: Session = Depends(get_db)
):
    """
    Get resource utilization metrics for a GPT.
    
    Args:
        gpt_id: The ID of the GPT to monitor
        time_range: Time range for metrics (24h, 7d, 30d)
        include_cpu: Whether to include CPU utilization metrics
        include_memory: Whether to include memory utilization metrics
        include_network: Whether to include network utilization metrics
        include_storage: Whether to include storage utilization metrics
        include_trends: Whether to include utilization trends
        include_forecast: Whether to include resource forecast
        include_optimization: Whether to include optimization suggestions
        include_alerts: Whether to include resource alerts
        include_benchmarks: Whether to include resource benchmarks
    """
    monitoring_service = MonitoringService(db)
    result = {}
    
    if include_cpu:
        result["cpu"] = {
            "utilization": await monitoring_service.get_cpu_utilization(gpt_id, time_range),
            "cores": await monitoring_service.get_cpu_cores(gpt_id),
            "load": await monitoring_service.get_cpu_load(gpt_id, time_range),
            "threads": await monitoring_service.get_cpu_threads(gpt_id)
        }
    
    if include_memory:
        result["memory"] = {
            "utilization": await monitoring_service.get_memory_utilization(gpt_id, time_range),
            "total": await monitoring_service.get_memory_total(gpt_id),
            "used": await monitoring_service.get_memory_used(gpt_id),
            "free": await monitoring_service.get_memory_free(gpt_id),
            "swap": await monitoring_service.get_memory_swap(gpt_id)
        }
    
    if include_network:
        result["network"] = {
            "bandwidth": await monitoring_service.get_network_bandwidth(gpt_id, time_range),
            "connections": await monitoring_service.get_network_connections(gpt_id),
            "latency": await monitoring_service.get_network_latency(gpt_id, time_range),
            "errors": await monitoring_service.get_network_errors(gpt_id, time_range)
        }
    
    if include_storage:
        result["storage"] = {
            "utilization": await monitoring_service.get_storage_utilization(gpt_id, time_range),
            "total": await monitoring_service.get_storage_total(gpt_id),
            "used": await monitoring_service.get_storage_used(gpt_id),
            "free": await monitoring_service.get_storage_free(gpt_id),
            "iops": await monitoring_service.get_storage_iops(gpt_id, time_range)
        }
    
    if include_trends:
        result["trends"] = {
            "cpu_trend": await monitoring_service.get_resource_trend(gpt_id, "cpu", time_range),
            "memory_trend": await monitoring_service.get_resource_trend(gpt_id, "memory", time_range),
            "network_trend": await monitoring_service.get_resource_trend(gpt_id, "network", time_range),
            "storage_trend": await monitoring_service.get_resource_trend(gpt_id, "storage", time_range)
        }
    
    if include_forecast:
        result["forecast"] = {
            "cpu_forecast": await monitoring_service.get_resource_forecast(gpt_id, "cpu", time_range),
            "memory_forecast": await monitoring_service.get_resource_forecast(gpt_id, "memory", time_range),
            "network_forecast": await monitoring_service.get_resource_forecast(gpt_id, "network", time_range),
            "storage_forecast": await monitoring_service.get_resource_forecast(gpt_id, "storage", time_range)
        }
    
    if include_optimization:
        result["optimization"] = {
            "suggestions": await monitoring_service.get_resource_optimization(gpt_id, time_range),
            "impact": await monitoring_service.get_resource_optimization_impact(gpt_id, time_range),
            "recommendations": await monitoring_service.get_resource_recommendations(gpt_id, time_range)
        }
    
    if include_alerts:
        result["alerts"] = {
            "active": await monitoring_service.get_resource_alerts(gpt_id, time_range),
            "history": await monitoring_service.get_resource_alert_history(gpt_id, time_range),
            "thresholds": await monitoring_service.get_resource_alert_thresholds(gpt_id)
        }
    
    if include_benchmarks:
        result["benchmarks"] = {
            "cpu_benchmark": await monitoring_service.get_resource_benchmark(gpt_id, "cpu", time_range),
            "memory_benchmark": await monitoring_service.get_resource_benchmark(gpt_id, "memory", time_range),
            "network_benchmark": await monitoring_service.get_resource_benchmark(gpt_id, "network", time_range),
            "storage_benchmark": await monitoring_service.get_resource_benchmark(gpt_id, "storage", time_range)
        }
    
    return result 