"""
Core Sharing Service

This module provides essential resource sharing pattern analysis and recommendations
without heavy computational overhead.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.organization_models import (
    Organization,
    OrganizationResource,
    OrganizationCollaboration
)

class CoreSharingService:
    def __init__(self, db: Session):
        self.db = db

    async def analyze_basic_patterns(
        self,
        org_id: str,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """
        Analyze basic sharing patterns with minimal processing.
        Focuses on essential metrics and simple pattern recognition.
        """
        try:
            # Get recent sharing history
            history = await self._get_recent_history(org_id, time_range)
            
            # Calculate basic metrics
            metrics = self._calculate_basic_metrics(history)
            
            # Identify simple patterns
            patterns = self._identify_basic_patterns(history)
            
            # Generate straightforward recommendations
            recommendations = self._generate_basic_recommendations(metrics, patterns)

            return {
                "metrics": metrics,
                "patterns": patterns,
                "recommendations": recommendations
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing sharing patterns: {str(e)}"
            )

    async def monitor_security_basics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        Monitor basic security metrics and detect obvious anomalies.
        Uses simple threshold-based detection to minimize processing.
        """
        try:
            # Get recent access patterns
            access_patterns = await self._get_access_patterns(org_id, time_range)
            
            # Check for basic anomalies
            anomalies = self._detect_basic_anomalies(access_patterns)
            
            # Generate simple risk assessment
            risk_assessment = self._assess_basic_risks(anomalies)

            return {
                "anomalies": anomalies,
                "risk_level": risk_assessment["level"],
                "immediate_concerns": risk_assessment["concerns"]
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error monitoring security: {str(e)}"
            )

    async def get_optimization_basics(
        self,
        org_id: str
    ) -> Dict[str, Any]:
        """
        Get basic optimization insights with minimal processing.
        Focuses on obvious optimization opportunities.
        """
        try:
            # Get current resource state
            current_state = await self._get_resource_state(org_id)
            
            # Identify clear optimization opportunities
            opportunities = self._identify_basic_opportunities(current_state)
            
            # Generate simple recommendations
            recommendations = self._generate_basic_optimizations(opportunities)

            return {
                "current_state": current_state,
                "opportunities": opportunities,
                "recommendations": recommendations
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting optimization insights: {str(e)}"
            )

    async def _get_recent_history(
        self,
        org_id: str,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get recent sharing history with basic filtering."""
        try:
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            collaborations = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id),
                OrganizationCollaboration.created_at >= start_time
            ).all()

            history = []
            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        history.append({
                            "resource_type": resource["resource_type"],
                            "access_level": resource["access_level"],
                            "status": resource["status"],
                            "created_at": resource["created_at"]
                        })

            return history

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving history: {str(e)}"
            )

    def _calculate_basic_metrics(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate essential metrics only."""
        total_shares = len(history)
        if total_shares == 0:
            return {
                "success_rate": 0.0,
                "active_share_ratio": 0.0
            }

        active_shares = sum(1 for entry in history if entry["status"] == "active")

        return {
            "success_rate": active_shares / total_shares,
            "active_share_ratio": active_shares / total_shares
        }

    def _identify_basic_patterns(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify obvious patterns only."""
        patterns = {
            "resource_types": {},
            "access_levels": {},
            "status_distribution": {}
        }

        for entry in history:
            # Track resource types
            resource_type = entry["resource_type"]
            if resource_type not in patterns["resource_types"]:
                patterns["resource_types"][resource_type] = 0
            patterns["resource_types"][resource_type] += 1

            # Track access levels
            access_level = entry["access_level"]
            if access_level not in patterns["access_levels"]:
                patterns["access_levels"][access_level] = 0
            patterns["access_levels"][access_level] += 1

            # Track status distribution
            status = entry["status"]
            if status not in patterns["status_distribution"]:
                patterns["status_distribution"][status] = 0
            patterns["status_distribution"][status] += 1

        return patterns

    def _generate_basic_recommendations(
        self,
        metrics: Dict[str, float],
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate straightforward recommendations based on clear patterns."""
        recommendations = []

        # Check success rate
        if metrics["success_rate"] < 0.7:
            recommendations.append({
                "type": "success_rate",
                "recommendation": "Review sharing approval process",
                "importance": "high"
            })

        # Check resource type distribution
        if patterns["resource_types"]:
            most_shared = max(
                patterns["resource_types"].items(),
                key=lambda x: x[1]
            )[0]
            recommendations.append({
                "type": "resource_focus",
                "recommendation": f"Continue focusing on {most_shared} resources",
                "importance": "medium"
            })

        # Check access level distribution
        if patterns["access_levels"]:
            high_access = sum(
                count for level, count in patterns["access_levels"].items()
                if level in ["write", "admin"]
            )
            total_access = sum(patterns["access_levels"].values())
            if high_access / total_access > 0.7:
                recommendations.append({
                    "type": "access_levels",
                    "recommendation": "Review high-level access assignments",
                    "importance": "high"
                })

        return recommendations

    async def _get_access_patterns(
        self,
        org_id: str,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get basic access patterns for security monitoring."""
        try:
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            collaborations = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id),
                OrganizationCollaboration.created_at >= start_time
            ).all()

            patterns = []
            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        patterns.append({
                            "access_level": resource["access_level"],
                            "created_at": datetime.fromisoformat(resource["created_at"]),
                            "status": resource["status"]
                        })

            return patterns

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving access patterns: {str(e)}"
            )

    def _detect_basic_anomalies(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect obvious security anomalies using simple thresholds."""
        anomalies = []
        
        # Group by hour
        hourly_counts = {}
        for pattern in patterns:
            hour = pattern["created_at"].hour
            if hour not in hourly_counts:
                hourly_counts[hour] = 0
            hourly_counts[hour] += 1

        # Check for unusual spikes (simple threshold)
        avg_count = sum(hourly_counts.values()) / len(hourly_counts) if hourly_counts else 0
        for hour, count in hourly_counts.items():
            if count > avg_count * 2:  # Simple threshold: 2x average
                anomalies.append({
                    "type": "unusual_activity",
                    "hour": hour,
                    "count": count,
                    "average": avg_count,
                    "severity": "medium"
                })

        return anomalies

    def _assess_basic_risks(
        self,
        anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform basic risk assessment."""
        if not anomalies:
            return {
                "level": "low",
                "concerns": []
            }

        # Count medium and high severity anomalies
        medium_count = sum(1 for a in anomalies if a["severity"] == "medium")
        high_count = sum(1 for a in anomalies if a["severity"] == "high")

        # Simple risk level determination
        if high_count > 0:
            risk_level = "high"
        elif medium_count > 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Identify immediate concerns
        concerns = []
        if high_count > 0:
            concerns.append("Multiple high-severity anomalies detected")
        if medium_count > 2:
            concerns.append("Unusual pattern of access detected")

        return {
            "level": risk_level,
            "concerns": concerns
        }

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
            else:
                raise ValueError(f"Invalid time unit: {unit}")
        except Exception as e:
            raise ValueError(f"Invalid time range format: {time_range}") 