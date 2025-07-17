"""
Cross-Organization Resource Optimization Service

This module provides AI-driven optimization for resource sharing across organizations
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from ..models.organization_models import (
    Organization,
    OrganizationResource,
    OrganizationCollaboration
)
from .smart_sharing_patterns_service import SmartSharingPatternsService
from .predictive_access_service import PredictiveAccessService

class CrossOrgOptimizationService:
    def __init__(self, db: Session):
        self.db = db
        self.scaler = StandardScaler()
        self.patterns_service = SmartSharingPatternsService(db)
        self.access_service = PredictiveAccessService(db)

    async def analyze_sharing_efficiency(
        self,
        org_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Analyze resource sharing efficiency across organizations."""
        try:
            # Get sharing patterns
            patterns = await self.patterns_service.analyze_sharing_patterns(
                org_id,
                time_range
            )
            
            # Get access predictions
            access_predictions = await self._get_access_predictions(org_id)
            
            # Calculate efficiency metrics
            efficiency_metrics = await self._calculate_efficiency_metrics(
                patterns,
                access_predictions
            )

            return {
                "current_efficiency": efficiency_metrics,
                "optimization_opportunities": await self._identify_optimization_opportunities(
                    patterns,
                    efficiency_metrics
                ),
                "recommendations": await self._generate_efficiency_recommendations(
                    patterns,
                    efficiency_metrics
                )
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing sharing efficiency: {str(e)}"
            )

    async def suggest_sharing_schedule(
        self,
        org_id: str,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Suggest optimal sharing schedule based on usage patterns."""
        try:
            # Get usage patterns
            usage_patterns = await self._get_usage_patterns(org_id, resource_type)
            
            # Analyze temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(usage_patterns)
            
            # Generate schedule suggestions
            schedule = await self._generate_sharing_schedule(
                usage_patterns,
                temporal_patterns
            )

            return {
                "suggested_schedule": schedule,
                "optimization_impact": await self._calculate_schedule_impact(schedule),
                "implementation_plan": await self._create_implementation_plan(schedule)
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating sharing schedule: {str(e)}"
            )

    async def find_complementary_patterns(
        self,
        org_id: str
    ) -> List[Dict[str, Any]]:
        """Find complementary resource usage patterns across organizations."""
        try:
            # Get organization's usage patterns
            org_patterns = await self._get_usage_patterns(org_id)
            
            # Find complementary organizations
            complementary_orgs = await self._find_complementary_organizations(
                org_id,
                org_patterns
            )
            
            # Generate collaboration suggestions
            suggestions = await self._generate_collaboration_suggestions(
                org_patterns,
                complementary_orgs
            )

            return suggestions

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error finding complementary patterns: {str(e)}"
            )

    async def _calculate_efficiency_metrics(
        self,
        patterns: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate efficiency metrics for resource sharing."""
        metrics = {
            "resource_utilization": 0.0,
            "access_optimization": 0.0,
            "sharing_effectiveness": 0.0,
            "cost_efficiency": 0.0
        }

        if patterns["success_metrics"]:
            metrics["resource_utilization"] = patterns["success_metrics"]["usage_effectiveness"]
            metrics["sharing_effectiveness"] = patterns["success_metrics"]["success_rate"]

        if predictions:
            metrics["access_optimization"] = sum(
                pred["confidence_score"] for pred in predictions.values()
            ) / len(predictions) if predictions else 0.0

        # Calculate cost efficiency
        total_resources = len(patterns.get("resource_types", {}))
        active_shares = patterns.get("success_patterns", {}).get("active", 0)
        metrics["cost_efficiency"] = active_shares / total_resources if total_resources > 0 else 0.0

        return metrics

    async def _identify_optimization_opportunities(
        self,
        patterns: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities for optimization."""
        opportunities = []

        # Check resource utilization
        if metrics["resource_utilization"] < 0.7:
            opportunities.append({
                "type": "resource_utilization",
                "current_value": metrics["resource_utilization"],
                "target_value": 0.8,
                "impact": "high",
                "difficulty": "medium"
            })

        # Check access optimization
        if metrics["access_optimization"] < 0.8:
            opportunities.append({
                "type": "access_optimization",
                "current_value": metrics["access_optimization"],
                "target_value": 0.9,
                "impact": "medium",
                "difficulty": "low"
            })

        # Check sharing effectiveness
        if metrics["sharing_effectiveness"] < 0.75:
            opportunities.append({
                "type": "sharing_effectiveness",
                "current_value": metrics["sharing_effectiveness"],
                "target_value": 0.85,
                "impact": "high",
                "difficulty": "medium"
            })

        return opportunities

    async def _analyze_temporal_patterns(
        self,
        usage_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze temporal patterns in resource usage."""
        patterns = {
            "hourly": {},
            "daily": {},
            "weekly": {},
            "monthly": {}
        }

        for pattern in usage_patterns:
            timestamp = pattern["timestamp"]
            
            # Hourly patterns
            hour = timestamp.hour
            if hour not in patterns["hourly"]:
                patterns["hourly"][hour] = 0
            patterns["hourly"][hour] += 1

            # Daily patterns
            day = timestamp.weekday()
            if day not in patterns["daily"]:
                patterns["daily"][day] = 0
            patterns["daily"][day] += 1

            # Weekly patterns
            week = timestamp.isocalendar()[1]
            if week not in patterns["weekly"]:
                patterns["weekly"][week] = 0
            patterns["weekly"][week] += 1

            # Monthly patterns
            month = timestamp.month
            if month not in patterns["monthly"]:
                patterns["monthly"][month] = 0
            patterns["monthly"][month] += 1

        return patterns

    async def _generate_sharing_schedule(
        self,
        usage_patterns: List[Dict[str, Any]],
        temporal_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimal sharing schedule."""
        schedule = {
            "peak_hours": [],
            "off_peak_hours": [],
            "recommended_windows": [],
            "blackout_periods": []
        }

        # Identify peak hours
        hourly_usage = temporal_patterns["hourly"]
        avg_hourly = sum(hourly_usage.values()) / len(hourly_usage) if hourly_usage else 0
        
        for hour, count in hourly_usage.items():
            if count > avg_hourly * 1.2:  # 20% above average
                schedule["peak_hours"].append(hour)
            elif count < avg_hourly * 0.8:  # 20% below average
                schedule["off_peak_hours"].append(hour)

        # Generate recommended windows
        for i in range(24):
            if i in schedule["off_peak_hours"]:
                window_start = i
                window_end = i
                
                # Extend window if next hour is also off-peak
                while (window_end + 1) % 24 in schedule["off_peak_hours"]:
                    window_end += 1
                    if window_end - window_start >= 3:  # Minimum 4-hour window
                        schedule["recommended_windows"].append({
                            "start": window_start,
                            "end": window_end,
                            "duration": window_end - window_start + 1
                        })

        # Identify blackout periods
        for i in range(24):
            if i in schedule["peak_hours"]:
                window_start = i
                window_end = i
                
                # Extend window if next hour is also peak
                while (window_end + 1) % 24 in schedule["peak_hours"]:
                    window_end += 1
                    if window_end - window_start >= 1:  # Minimum 2-hour window
                        schedule["blackout_periods"].append({
                            "start": window_start,
                            "end": window_end,
                            "duration": window_end - window_start + 1
                        })

        return schedule

    async def _calculate_schedule_impact(
        self,
        schedule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate potential impact of the suggested schedule."""
        total_recommended_hours = sum(
            window["duration"] for window in schedule["recommended_windows"]
        )
        total_blackout_hours = sum(
            period["duration"] for period in schedule["blackout_periods"]
        )

        return {
            "resource_utilization_improvement": 0.2 if total_recommended_hours > 8 else 0.1,
            "cost_reduction": 0.15 if total_blackout_hours > 4 else 0.05,
            "performance_impact": "minimal" if total_blackout_hours < 6 else "moderate",
            "implementation_complexity": "low" if len(schedule["recommended_windows"]) <= 3 else "medium"
        }

    async def _create_implementation_plan(
        self,
        schedule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create a plan for implementing the sharing schedule."""
        plan = []

        # Add recommended windows implementation
        if schedule["recommended_windows"]:
            plan.append({
                "phase": "setup_sharing_windows",
                "actions": [
                    {
                        "type": "configure_window",
                        "window": window,
                        "priority": "high" if window["duration"] >= 6 else "medium"
                    }
                    for window in schedule["recommended_windows"]
                ],
                "timeline": "immediate"
            })

        # Add blackout periods implementation
        if schedule["blackout_periods"]:
            plan.append({
                "phase": "setup_blackout_periods",
                "actions": [
                    {
                        "type": "configure_blackout",
                        "period": period,
                        "priority": "high" if period["duration"] >= 4 else "medium"
                    }
                    for period in schedule["blackout_periods"]
                ],
                "timeline": "immediate"
            })

        # Add monitoring setup
        plan.append({
            "phase": "setup_monitoring",
            "actions": [
                {
                    "type": "configure_alerts",
                    "metric": "utilization",
                    "threshold": 0.8,
                    "priority": "high"
                },
                {
                    "type": "configure_alerts",
                    "metric": "violations",
                    "threshold": 0,
                    "priority": "high"
                }
            ],
            "timeline": "week_1"
        })

        return plan 