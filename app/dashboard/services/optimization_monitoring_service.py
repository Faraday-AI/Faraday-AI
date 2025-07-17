"""
Resource Optimization Monitoring Service

This module provides real-time monitoring and AI-driven insights for resource optimization
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..models import (
    DashboardResourceUsage,
    DashboardResourceSharing,
    Organization,
    DashboardOptimizationEvent
)

class OptimizationMonitoringService:
    """Service for monitoring resource optimization with AI insights."""

    def __init__(self, db: Session):
        self.db = db
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()

    async def get_optimization_metrics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        Get real-time optimization metrics.
        
        Args:
            org_id: Organization ID
            time_range: Time range for analysis (24h, 7d, 30d)
        """
        try:
            # Get usage and sharing data
            usage_data = await self._get_usage_data(org_id, time_range)
            sharing_data = await self._get_sharing_data(org_id, time_range)

            # Calculate metrics
            metrics = {
                "utilization_rate": self._calculate_utilization_rate(usage_data),
                "sharing_efficiency": self._calculate_sharing_efficiency(sharing_data),
                "optimization_score": self._calculate_optimization_score(usage_data, sharing_data),
                "anomalies": await self._detect_anomalies(usage_data, sharing_data),
                "recommendations": await self._generate_recommendations(usage_data, sharing_data),
                "timestamp": datetime.utcnow()
            }

            return metrics

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting optimization metrics: {str(e)}"
            )

    async def get_optimization_insights(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        Get AI-driven optimization insights.
        
        Args:
            org_id: Organization ID
            time_range: Time range for analysis (24h, 7d, 30d)
        """
        try:
            # Get historical data
            usage_data = await self._get_usage_data(org_id, time_range)
            sharing_data = await self._get_sharing_data(org_id, time_range)

            # Generate insights
            insights = {
                "patterns": await self._analyze_patterns(usage_data, sharing_data),
                "trends": await self._analyze_trends(usage_data, sharing_data),
                "opportunities": await self._identify_opportunities(usage_data, sharing_data),
                "risks": await self._assess_risks(usage_data, sharing_data),
                "timestamp": datetime.utcnow()
            }

            return insights

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting optimization insights: {str(e)}"
            )

    async def _get_usage_data(
        self,
        org_id: str,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get resource usage data."""
        end_time = datetime.utcnow()
        if time_range == "24h":
            start_time = end_time - timedelta(days=1)
        elif time_range == "7d":
            start_time = end_time - timedelta(days=7)
        else:  # 30d
            start_time = end_time - timedelta(days=30)

        usage_data = self.db.query(DashboardResourceUsage).filter(
            DashboardResourceUsage.organization_id == org_id,
            DashboardResourceUsage.timestamp >= start_time
        ).all()

        return [
            {
                "timestamp": u.timestamp,
                "resource_type": u.resource_type,
                "usage_amount": u.usage_amount
            }
            for u in usage_data
        ]

    async def _get_sharing_data(
        self,
        org_id: str,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get resource sharing data."""
        end_time = datetime.utcnow()
        if time_range == "24h":
            start_time = end_time - timedelta(days=1)
        elif time_range == "7d":
            start_time = end_time - timedelta(days=7)
        else:  # 30d
            start_time = end_time - timedelta(days=30)

        sharing_data = self.db.query(DashboardResourceSharing).filter(
            (DashboardResourceSharing.owner_id == org_id) |
            (DashboardResourceSharing.shared_with_user_id == org_id),
            DashboardResourceSharing.shared_at >= start_time
        ).all()

        return [
            {
                "timestamp": s.shared_at,
                "source_org": s.owner_id,
                "target_org": s.shared_with_user_id,
                "resource_type": s.resource_type
            }
            for s in sharing_data
        ]

    def _calculate_utilization_rate(self, usage_data: List[Dict[str, Any]]) -> float:
        """Calculate resource utilization rate."""
        if not usage_data:
            return 0.0

        df = pd.DataFrame(usage_data)
        total_usage = df["usage_amount"].sum()
        total_capacity = 100.0  # Example capacity
        return min(total_usage / total_capacity, 1.0)

    def _calculate_sharing_efficiency(self, sharing_data: List[Dict[str, Any]]) -> float:
        """Calculate resource sharing efficiency."""
        if not sharing_data:
            return 0.0

        df = pd.DataFrame(sharing_data)
        total_shares = len(df)
        max_potential_shares = 100.0  # Example maximum
        return min(total_shares / max_potential_shares, 1.0)

    def _calculate_optimization_score(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall optimization score."""
        utilization_rate = self._calculate_utilization_rate(usage_data)
        sharing_efficiency = self._calculate_sharing_efficiency(sharing_data)

        # Weighted average
        return (utilization_rate * 0.6 + sharing_efficiency * 0.4) * 100

    async def _detect_anomalies(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in resource usage and sharing patterns."""
        if not usage_data or not sharing_data:
            return []

        # Prepare data for anomaly detection
        df = pd.DataFrame(usage_data)
        features = df[["usage_amount"]].values
        features = self.scaler.fit_transform(features)

        # Detect anomalies
        anomalies = self.anomaly_detector.fit_predict(features)
        anomaly_indices = np.where(anomalies == -1)[0]

        return [
            {
                "timestamp": df.iloc[i]["timestamp"].isoformat(),
                "resource_type": df.iloc[i]["resource_type"],
                "usage_amount": float(df.iloc[i]["usage_amount"]),
                "severity": "high" if df.iloc[i]["usage_amount"] > df["usage_amount"].mean() else "low"
            }
            for i in anomaly_indices
        ]

    async def _generate_recommendations(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []

        # Analyze usage patterns
        utilization_rate = self._calculate_utilization_rate(usage_data)
        if utilization_rate < 0.6:
            recommendations.append({
                "type": "utilization",
                "priority": "high",
                "message": "Resource utilization is low. Consider optimizing resource allocation."
            })

        # Analyze sharing patterns
        sharing_efficiency = self._calculate_sharing_efficiency(sharing_data)
        if sharing_efficiency < 0.5:
            recommendations.append({
                "type": "sharing",
                "priority": "medium",
                "message": "Resource sharing efficiency is low. Consider increasing collaboration."
            })

        return recommendations

    async def _analyze_patterns(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze usage and sharing patterns."""
        if not usage_data or not sharing_data:
            return {}

        df_usage = pd.DataFrame(usage_data)
        df_sharing = pd.DataFrame(sharing_data)

        # Analyze usage patterns
        usage_patterns = {
            "peak_hours": self._find_peak_hours(df_usage),
            "resource_distribution": df_usage["resource_type"].value_counts().to_dict(),
            "usage_trend": self._calculate_usage_trend(df_usage)
        }

        # Analyze sharing patterns
        sharing_patterns = {
            "frequent_partners": df_sharing["target_org"].value_counts().head(5).to_dict(),
            "resource_preferences": df_sharing["resource_type"].value_counts().to_dict(),
            "sharing_trend": self._calculate_sharing_trend(df_sharing)
        }

        return {
            "usage_patterns": usage_patterns,
            "sharing_patterns": sharing_patterns
        }

    async def _analyze_trends(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze usage and sharing trends."""
        if not usage_data or not sharing_data:
            return {}

        df_usage = pd.DataFrame(usage_data)
        df_sharing = pd.DataFrame(sharing_data)

        # Calculate trends
        usage_trend = self._calculate_usage_trend(df_usage)
        sharing_trend = self._calculate_sharing_trend(df_sharing)

        return {
            "usage_trend": usage_trend,
            "sharing_trend": sharing_trend,
            "overall_trend": self._calculate_overall_trend(usage_trend, sharing_trend)
        }

    async def _identify_opportunities(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities = []

        # Analyze usage opportunities
        df_usage = pd.DataFrame(usage_data)
        if not df_usage.empty:
            underutilized_resources = df_usage[df_usage["usage_amount"] < df_usage["usage_amount"].mean()]
            if not underutilized_resources.empty:
                opportunities.append({
                    "type": "underutilized_resources",
                    "priority": "high",
                    "message": "Some resources are underutilized. Consider reallocating or sharing them."
                })

        # Analyze sharing opportunities
        df_sharing = pd.DataFrame(sharing_data)
        if not df_sharing.empty:
            potential_partners = self._identify_potential_partners(df_sharing)
            if potential_partners:
                opportunities.append({
                    "type": "potential_partners",
                    "priority": "medium",
                    "message": f"Potential new sharing partners identified: {', '.join(potential_partners)}"
                })

        return opportunities

    async def _assess_risks(
        self,
        usage_data: List[Dict[str, Any]],
        sharing_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Assess optimization risks."""
        risks = []

        # Analyze usage risks
        df_usage = pd.DataFrame(usage_data)
        if not df_usage.empty:
            overutilized_resources = df_usage[df_usage["usage_amount"] > df_usage["usage_amount"].mean() * 1.5]
            if not overutilized_resources.empty:
                risks.append({
                    "type": "overutilization",
                    "severity": "high",
                    "message": "Some resources are overutilized. Consider scaling up or optimizing usage."
                })

        # Analyze sharing risks
        df_sharing = pd.DataFrame(sharing_data)
        if not df_sharing.empty:
            sharing_anomalies = await self._detect_anomalies(usage_data, sharing_data)
            if sharing_anomalies:
                risks.append({
                    "type": "sharing_anomalies",
                    "severity": "medium",
                    "message": "Anomalies detected in sharing patterns. Review sharing policies."
                })

        return risks

    def _find_peak_hours(self, df: pd.DataFrame) -> List[int]:
        """Find peak usage hours."""
        df["hour"] = df["timestamp"].dt.hour
        hourly_usage = df.groupby("hour")["usage_amount"].mean()
        return hourly_usage.nlargest(3).index.tolist()

    def _calculate_usage_trend(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate usage trend."""
        if len(df) < 2:
            return {"direction": "stable", "rate": 0.0}

        x = np.arange(len(df))
        y = df["usage_amount"].values
        slope = np.polyfit(x, y, 1)[0]

        return {
            "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "rate": float(abs(slope))
        }

    def _calculate_sharing_trend(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate sharing trend."""
        if len(df) < 2:
            return {"direction": "stable", "rate": 0.0}

        df["date"] = df["timestamp"].dt.date
        daily_shares = df.groupby("date").size()
        x = np.arange(len(daily_shares))
        y = daily_shares.values
        slope = np.polyfit(x, y, 1)[0]

        return {
            "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "rate": float(abs(slope))
        }

    def _calculate_overall_trend(
        self,
        usage_trend: Dict[str, float],
        sharing_trend: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate overall optimization trend."""
        usage_score = 1.0 if usage_trend["direction"] == "increasing" else 0.5 if usage_trend["direction"] == "stable" else 0.0
        sharing_score = 1.0 if sharing_trend["direction"] == "increasing" else 0.5 if sharing_trend["direction"] == "stable" else 0.0

        overall_score = (usage_score * 0.6 + sharing_score * 0.4) * 100

        return {
            "score": overall_score,
            "direction": "improving" if overall_score > 50 else "degrading" if overall_score < 50 else "stable",
            "confidence": min(usage_trend["rate"] + sharing_trend["rate"], 1.0)
        }

    def _identify_potential_partners(self, df: pd.DataFrame) -> List[str]:
        """Identify potential new sharing partners."""
        if df.empty:
            return []

        # Get current partners
        current_partners = set(df["target_org"].unique())

        # Get all organizations
        all_orgs = set(org.id for org in self.db.query(Organization).all())

        # Find potential new partners
        potential_partners = all_orgs - current_partners

        return list(potential_partners)[:5]  # Return top 5 potential partners 