"""
Resource Optimization Monitoring Dashboard

This module provides monitoring dashboard configurations for resource optimization features
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

class ResourceOptimizationDashboard:
    """Dashboard configuration for resource optimization monitoring."""

    @staticmethod
    def get_dashboard_config() -> Dict[str, Any]:
        """Get the complete dashboard configuration."""
        return {
            "title": "Resource Optimization Monitoring",
            "refresh_rate": "1m",
            "layout": "grid",
            "panels": [
                # Smart Resource Sharing Patterns panels
                {
                    "title": "Sharing Pattern Analysis",
                    "type": "stats",
                    "metrics": [
                        "resource_sharing_success_rate",
                        "resource_sharing_effectiveness",
                        "collaboration_score"
                    ],
                    "thresholds": {
                        "success_rate": 0.8,
                        "effectiveness": 0.7,
                        "collaboration": 0.75
                    },
                    "position": {"x": 0, "y": 0, "w": 8, "h": 4}
                },
                {
                    "title": "Resource Type Distribution",
                    "type": "pie_chart",
                    "metric": "resource_type_distribution",
                    "refresh_rate": "5m",
                    "position": {"x": 8, "y": 0, "w": 4, "h": 4}
                },
                {
                    "title": "Sharing Pattern Trends",
                    "type": "time_series",
                    "metrics": [
                        "daily_shares",
                        "active_shares",
                        "sharing_success_rate"
                    ],
                    "timeRange": "7d",
                    "position": {"x": 0, "y": 4, "w": 12, "h": 6}
                },

                # Predictive Access Management panels
                {
                    "title": "Access Prediction Accuracy",
                    "type": "gauge",
                    "metric": "access_prediction_accuracy",
                    "thresholds": [
                        {"value": 0.7, "color": "red"},
                        {"value": 0.8, "color": "yellow"},
                        {"value": 0.9, "color": "green"}
                    ],
                    "position": {"x": 0, "y": 10, "w": 4, "h": 4}
                },
                {
                    "title": "Security Risk Overview",
                    "type": "status_panel",
                    "metrics": [
                        "active_anomalies",
                        "risk_level",
                        "security_incidents"
                    ],
                    "severity_mapping": {
                        "low": "green",
                        "medium": "yellow",
                        "high": "red"
                    },
                    "position": {"x": 4, "y": 10, "w": 8, "h": 4}
                },
                {
                    "title": "Access Pattern Anomalies",
                    "type": "timeline",
                    "metric": "access_anomalies",
                    "timeRange": "24h",
                    "severity_colors": {
                        "high": "red",
                        "medium": "yellow",
                        "low": "green"
                    },
                    "position": {"x": 0, "y": 14, "w": 12, "h": 6}
                },

                # Cross-Organization Optimization panels
                {
                    "title": "Resource Utilization Efficiency",
                    "type": "heatmap",
                    "metric": "resource_utilization",
                    "dimensions": ["org_id", "resource_type"],
                    "color_scheme": "YlOrRd",
                    "position": {"x": 0, "y": 20, "w": 6, "h": 6}
                },
                {
                    "title": "Sharing Schedule Compliance",
                    "type": "status_timeline",
                    "metrics": [
                        "schedule_adherence",
                        "window_utilization",
                        "blackout_violations"
                    ],
                    "timeRange": "7d",
                    "position": {"x": 6, "y": 20, "w": 6, "h": 6}
                },
                {
                    "title": "Optimization Impact",
                    "type": "stat_comparison",
                    "metrics": [
                        {
                            "name": "resource_utilization_improvement",
                            "format": "percent",
                            "comparison": "week_over_week"
                        },
                        {
                            "name": "cost_reduction",
                            "format": "currency",
                            "comparison": "week_over_week"
                        },
                        {
                            "name": "efficiency_gain",
                            "format": "percent",
                            "comparison": "week_over_week"
                        }
                    ],
                    "position": {"x": 0, "y": 26, "w": 12, "h": 4}
                }
            ],
            "alerts": [
                {
                    "name": "Low Sharing Success Rate",
                    "metric": "resource_sharing_success_rate",
                    "condition": "< 0.7",
                    "duration": "15m",
                    "severity": "warning"
                },
                {
                    "name": "High Risk Level",
                    "metric": "risk_level",
                    "condition": "== 'high'",
                    "duration": "5m",
                    "severity": "critical"
                },
                {
                    "name": "Schedule Violation",
                    "metric": "blackout_violations",
                    "condition": "> 0",
                    "duration": "5m",
                    "severity": "warning"
                },
                {
                    "name": "Low Resource Utilization",
                    "metric": "resource_utilization",
                    "condition": "< 0.6",
                    "duration": "1h",
                    "severity": "warning"
                }
            ],
            "data_sources": [
                {
                    "name": "prometheus",
                    "type": "prometheus",
                    "url": "${PROMETHEUS_URL}",
                    "access": "proxy"
                },
                {
                    "name": "elasticsearch",
                    "type": "elasticsearch",
                    "url": "${ELASTICSEARCH_URL}",
                    "index": "resource-optimization-*",
                    "access": "proxy"
                }
            ],
            "annotations": {
                "enabled": True,
                "list": [
                    {
                        "name": "Deployments",
                        "datasource": "prometheus",
                        "expr": "changes(deployment_status{job=\"resource-optimization\"}[1m]) > 0"
                    },
                    {
                        "name": "Configuration Changes",
                        "datasource": "elasticsearch",
                        "query": "type:configuration_change AND service:resource-optimization"
                    }
                ]
            },
            "variables": {
                "org_id": {
                    "type": "query",
                    "datasource": "prometheus",
                    "query": "label_values(resource_sharing_success_rate, org_id)"
                },
                "resource_type": {
                    "type": "query",
                    "datasource": "prometheus",
                    "query": "label_values(resource_type_distribution, type)"
                }
            }
        }

    @staticmethod
    def get_prometheus_rules() -> List[Dict[str, Any]]:
        """Get Prometheus alerting rules for the dashboard."""
        return [
            {
                "name": "ResourceOptimizationAlerts",
                "rules": [
                    {
                        "alert": "LowSharingSuccessRate",
                        "expr": "rate(resource_sharing_success_rate[15m]) < 0.7",
                        "for": "15m",
                        "labels": {
                            "severity": "warning",
                            "service": "resource-optimization"
                        },
                        "annotations": {
                            "summary": "Low resource sharing success rate",
                            "description": "Success rate has been below 70% for 15 minutes"
                        }
                    },
                    {
                        "alert": "HighRiskLevel",
                        "expr": "resource_risk_level == 3",
                        "for": "5m",
                        "labels": {
                            "severity": "critical",
                            "service": "resource-optimization"
                        },
                        "annotations": {
                            "summary": "High security risk level detected",
                            "description": "Security risk level has been high for 5 minutes"
                        }
                    },
                    {
                        "alert": "BlackoutViolation",
                        "expr": "sum(rate(blackout_violations_total[5m])) > 0",
                        "for": "5m",
                        "labels": {
                            "severity": "warning",
                            "service": "resource-optimization"
                        },
                        "annotations": {
                            "summary": "Sharing schedule blackout violation detected",
                            "description": "Resources are being shared during blackout periods"
                        }
                    }
                ]
            }
        ]

    @staticmethod
    def get_grafana_dashboard() -> Dict[str, Any]:
        """Get Grafana dashboard configuration."""
        return {
            "dashboard": ResourceOptimizationDashboard.get_dashboard_config(),
            "overwrite": True,
            "message": "Updated resource optimization dashboard",
            "folder": "Resource Optimization",
            "folderUid": "resource-opt",
            "refresh": "1m",
            "tags": ["resource-optimization", "monitoring", "analytics"],
            "timezone": "browser"
        } 