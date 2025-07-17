"""
Organization Analytics Service

This module provides advanced analytics and reporting capabilities for organizations
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.organization_models import (
    Organization,
    OrganizationMember,
    OrganizationCollaboration,
    OrganizationResource
)

class OrganizationAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_organization_metrics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get comprehensive organization metrics."""
        try:
            # Convert time range to timedelta
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            # Get organization
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise HTTPException(status_code=404, detail="Organization not found")

            # Collect metrics
            metrics = {
                "organization": self._get_org_summary(org),
                "members": await self._get_member_metrics(org_id, start_time),
                "collaborations": await self._get_collaboration_metrics(org_id, start_time),
                "resources": await self._get_resource_metrics(org_id, start_time),
                "performance": await self._get_performance_metrics(org_id, start_time),
                "engagement": await self._get_engagement_metrics(org_id, start_time),
                "trends": await self._get_trend_analysis(org_id, start_time)
            }

            return metrics
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting organization metrics: {str(e)}"
            )

    async def get_collaboration_analytics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get detailed collaboration analytics."""
        try:
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            analytics = {
                "overview": await self._get_collaboration_overview(org_id, start_time),
                "patterns": await self._analyze_collaboration_patterns(org_id, start_time),
                "effectiveness": await self._measure_collaboration_effectiveness(org_id, start_time),
                "resource_sharing": await self._analyze_resource_sharing(org_id, start_time),
                "communication": await self._analyze_communication_patterns(org_id, start_time),
                "recommendations": await self._generate_collaboration_recommendations(org_id)
            }

            return analytics
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting collaboration analytics: {str(e)}"
            )

    async def get_resource_analytics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get detailed resource usage analytics."""
        try:
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            analytics = {
                "usage": await self._analyze_resource_usage(org_id, start_time),
                "allocation": await self._analyze_resource_allocation(org_id, start_time),
                "efficiency": await self._measure_resource_efficiency(org_id, start_time),
                "optimization": await self._generate_optimization_suggestions(org_id),
                "predictions": await self._predict_resource_needs(org_id)
            }

            return analytics
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting resource analytics: {str(e)}"
            )

    async def get_performance_report(
        self,
        org_id: str,
        time_range: str = "24h",
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        try:
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            report = {
                "summary": await self._generate_performance_summary(org_id, start_time),
                "metrics": await self._collect_performance_metrics(org_id, start_time),
                "analysis": await self._analyze_performance_trends(org_id, start_time),
                "benchmarks": await self._compare_with_benchmarks(org_id),
                "recommendations": await self._generate_performance_recommendations(org_id)
            }

            if include_predictions:
                report["predictions"] = await self._generate_performance_predictions(org_id)

            return report
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating performance report: {str(e)}"
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

    def _get_org_summary(self, org: Organization) -> Dict[str, Any]:
        """Get organization summary."""
        return {
            "id": org.id,
            "name": org.name,
            "type": org.type,
            "subscription_tier": org.subscription_tier,
            "member_count": len(org.members),
            "department_count": len(org.departments),
            "resource_count": len(org.resources)
        }

    async def _get_member_metrics(
        self,
        org_id: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Get member-related metrics."""
        members = self.db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.created_at >= start_time
        ).all()

        return {
            "total": len(members),
            "active": sum(1 for m in members if m.status == "active"),
            "by_role": self._group_by_attribute(members, "role"),
            "growth_rate": self._calculate_growth_rate(members, start_time),
            "engagement_rate": await self._calculate_engagement_rate(members)
        }

    async def _get_collaboration_metrics(
        self,
        org_id: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Get collaboration-related metrics."""
        collaborations = self.db.query(OrganizationCollaboration).filter(
            (OrganizationCollaboration.source_org_id == org_id) |
            (OrganizationCollaboration.target_org_id == org_id),
            OrganizationCollaboration.created_at >= start_time
        ).all()

        return {
            "total": len(collaborations),
            "active": sum(1 for c in collaborations if c.status == "active"),
            "by_type": self._group_by_attribute(collaborations, "type"),
            "success_rate": self._calculate_success_rate(collaborations),
            "avg_duration": self._calculate_avg_duration(collaborations)
        }

    async def _get_resource_metrics(
        self,
        org_id: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Get resource-related metrics."""
        resources = self.db.query(OrganizationResource).filter(
            OrganizationResource.organization_id == org_id,
            OrganizationResource.created_at >= start_time
        ).all()

        return {
            "total": len(resources),
            "active": sum(1 for r in resources if r.status == "active"),
            "by_type": self._group_by_attribute(resources, "resource_type"),
            "utilization_rate": await self._calculate_utilization_rate(resources),
            "efficiency_score": await self._calculate_efficiency_score(resources)
        }

    def _group_by_attribute(self, items: List[Any], attribute: str) -> Dict[str, int]:
        """Group items by attribute and count."""
        groups = {}
        for item in items:
            value = getattr(item, attribute)
            groups[value] = groups.get(value, 0) + 1
        return groups

    def _calculate_growth_rate(
        self,
        items: List[Any],
        start_time: datetime
    ) -> float:
        """Calculate growth rate over time period."""
        if not items:
            return 0.0

        time_periods = []
        current_time = datetime.utcnow()
        while current_time >= start_time:
            period_items = [i for i in items if i.created_at.date() == current_time.date()]
            time_periods.append(len(period_items))
            current_time -= timedelta(days=1)

        if len(time_periods) < 2:
            return 0.0

        return (time_periods[0] - time_periods[-1]) / len(time_periods)

    async def _calculate_engagement_rate(self, members: List[OrganizationMember]) -> float:
        """Calculate member engagement rate."""
        if not members:
            return 0.0

        # This would typically involve analyzing member activity logs
        # For now, we'll return a simulated value
        return len([m for m in members if m.status == "active"]) / len(members)

    def _calculate_success_rate(self, collaborations: List[OrganizationCollaboration]) -> float:
        """Calculate collaboration success rate."""
        if not collaborations:
            return 0.0

        successful = sum(1 for c in collaborations if c.status == "completed")
        return successful / len(collaborations)

    def _calculate_avg_duration(self, collaborations: List[OrganizationCollaboration]) -> float:
        """Calculate average collaboration duration in days."""
        if not collaborations:
            return 0.0

        completed = [c for c in collaborations if c.status == "completed"]
        if not completed:
            return 0.0

        durations = [(c.updated_at - c.created_at).days for c in completed]
        return sum(durations) / len(durations)

    async def _calculate_utilization_rate(self, resources: List[OrganizationResource]) -> float:
        """Calculate resource utilization rate."""
        if not resources:
            return 0.0

        # This would typically involve analyzing resource usage logs
        # For now, we'll return a simulated value
        return len([r for r in resources if r.status == "active"]) / len(resources)

    async def _calculate_efficiency_score(self, resources: List[OrganizationResource]) -> float:
        """Calculate resource efficiency score."""
        if not resources:
            return 0.0

        # This would typically involve analyzing resource performance metrics
        # For now, we'll return a simulated value
        active_resources = [r for r in resources if r.status == "active"]
        return len(active_resources) / len(resources) if resources else 0.0 