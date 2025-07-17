"""
Analytics Service

This module provides advanced analytics capabilities for the Faraday AI Dashboard,
including performance tracking, trend analysis, and predictive analytics.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from fastapi import HTTPException

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback
)
from ..models.context import GPTContext

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_performance_trends(
        self,
        gpt_id: str,
        time_range: str = "7d",
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze performance trends for a specific GPT.
        
        Args:
            gpt_id: The ID of the GPT to analyze
            time_range: Time range for analysis (24h, 7d, 30d)
            metrics: Specific metrics to analyze (default: all)
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:  # 30d
                start_time = end_time - timedelta(days=30)

            # Get performance data
            performance_data = self.db.query(GPTPerformance).join(
                DashboardGPTSubscription
            ).filter(
                DashboardGPTSubscription.gpt_definition_id == gpt_id,
                GPTPerformance.timestamp >= start_time
            ).all()

            if not performance_data:
                return {
                    "status": "no_data",
                    "message": "No performance data available for the specified period"
                }

            # Convert to pandas DataFrame for analysis
            df = pd.DataFrame([
                {
                    "timestamp": p.timestamp,
                    **p.metrics
                } for p in performance_data
            ])

            # Calculate trends
            trends = {
                "response_time": self._analyze_metric_trend(df, "response_time"),
                "accuracy": self._analyze_metric_trend(df, "accuracy"),
                "user_satisfaction": self._analyze_metric_trend(df, "user_satisfaction"),
                "resource_usage": self._analyze_metric_trend(df, "resource_usage")
            }

            # Calculate performance score
            performance_score = self._calculate_performance_score(trends)

            return {
                "status": "success",
                "trends": trends,
                "performance_score": performance_score,
                "recommendations": self._generate_recommendations(trends)
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing performance trends: {str(e)}"
            )

    async def predict_resource_usage(
        self,
        gpt_id: str,
        prediction_window: str = "24h"
    ) -> Dict:
        """
        Predict future resource usage based on historical patterns.
        
        Args:
            gpt_id: The ID of the GPT to analyze
            prediction_window: Time window for prediction
        """
        try:
            # Get historical usage data
            usage_data = self.db.query(GPTUsage).join(
                DashboardGPTSubscription
            ).filter(
                DashboardGPTSubscription.gpt_definition_id == gpt_id,
                GPTUsage.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).all()

            if not usage_data:
                return {
                    "status": "no_data",
                    "message": "Insufficient historical data for prediction"
                }

            # Convert to pandas DataFrame
            df = pd.DataFrame([
                {
                    "timestamp": u.timestamp,
                    **u.details
                } for u in usage_data
            ])

            # Perform time series analysis
            predictions = self._analyze_usage_patterns(df, prediction_window)

            return {
                "status": "success",
                "predictions": predictions,
                "confidence_score": self._calculate_confidence_score(df),
                "potential_bottlenecks": self._identify_bottlenecks(predictions)
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error predicting resource usage: {str(e)}"
            )

    async def get_comparative_analysis(
        self,
        gpt_id: str,
        category: Optional[GPTAnalytics] = None
    ) -> Dict:
        """
        Perform comparative analysis against similar GPTs.
        
        Args:
            gpt_id: The ID of the GPT to analyze
            category: Optional category to limit comparison
        """
        try:
            # Get GPT details
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.id == gpt_id
            ).first()

            if not gpt:
                raise HTTPException(status_code=404, detail="GPT not found")

            # Get comparison group
            comparison_query = self.db.query(GPTDefinition)
            if category:
                comparison_query = comparison_query.filter(GPTDefinition.category == category)
            else:
                comparison_query = comparison_query.filter(GPTDefinition.type == gpt.type)
            
            comparison_group = comparison_query.all()

            # Collect performance metrics for comparison
            comparative_metrics = {}
            for comparison_gpt in comparison_group:
                metrics = self._get_average_metrics(comparison_gpt.id)
                comparative_metrics[comparison_gpt.id] = metrics

            # Calculate percentiles and rankings
            rankings = self._calculate_rankings(gpt_id, comparative_metrics)

            return {
                "status": "success",
                "rankings": rankings,
                "comparative_metrics": comparative_metrics,
                "improvement_opportunities": self._identify_improvements(
                    gpt_id,
                    comparative_metrics
                )
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error performing comparative analysis: {str(e)}"
            )

    def _analyze_metric_trend(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> Dict:
        """Analyze trend for a specific metric."""
        if metric not in df.columns:
            return {"status": "no_data"}

        values = df[metric].values
        timestamps = df["timestamp"].values

        # Calculate basic statistics
        mean_value = np.mean(values)
        std_dev = np.std(values)
        trend_direction = "stable"
        
        if len(values) > 1:
            # Calculate trend direction
            slope = np.polyfit(range(len(values)), values, 1)[0]
            if slope > 0.05:
                trend_direction = "improving"
            elif slope < -0.05:
                trend_direction = "degrading"

        return {
            "current_value": float(values[-1]),
            "mean": float(mean_value),
            "std_dev": float(std_dev),
            "trend": trend_direction,
            "stability_score": float(1 - (std_dev / mean_value)) if mean_value != 0 else 0
        }

    def _calculate_performance_score(self, trends: Dict) -> float:
        """Calculate overall performance score."""
        weights = {
            "response_time": 0.3,
            "accuracy": 0.3,
            "user_satisfaction": 0.25,
            "resource_usage": 0.15
        }

        score = 0
        for metric, weight in weights.items():
            if metric in trends and trends[metric]["status"] != "no_data":
                normalized_value = trends[metric]["current_value"]
                if metric == "response_time":
                    # Lower is better for response time
                    normalized_value = 1 - (normalized_value / 10)  # Assuming 10s is max
                score += normalized_value * weight

        return min(max(score, 0), 1)  # Ensure score is between 0 and 1

    def _generate_recommendations(self, trends: Dict) -> List[Dict]:
        """Generate improvement recommendations based on trends."""
        recommendations = []

        # Check response time
        if (
            "response_time" in trends and
            trends["response_time"]["trend"] == "degrading"
        ):
            recommendations.append({
                "category": "performance",
                "priority": "high",
                "message": "Response time is degrading. Consider optimizing resource allocation."
            })

        # Check accuracy
        if (
            "accuracy" in trends and
            trends["accuracy"]["current_value"] < 0.8
        ):
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "message": "Accuracy is below target. Review training data and model parameters."
            })

        # Check resource usage
        if (
            "resource_usage" in trends and
            trends["resource_usage"]["trend"] == "improving"
        ):
            recommendations.append({
                "category": "efficiency",
                "priority": "medium",
                "message": "Resource usage is optimizing well. Consider increasing workload capacity."
            })

        return recommendations

    def _analyze_usage_patterns(
        self,
        df: pd.DataFrame,
        prediction_window: str
    ) -> Dict:
        """Analyze usage patterns and make predictions."""
        # Group by hour to get usage patterns
        df["hour"] = df["timestamp"].dt.hour
        hourly_usage = df.groupby("hour").mean()

        # Identify peak usage hours
        peak_hours = hourly_usage.nlargest(3, "resource_usage").index.tolist()

        # Calculate growth trend
        usage_trend = np.polyfit(range(len(df)), df["resource_usage"].values, 1)[0]

        return {
            "peak_hours": peak_hours,
            "growth_trend": float(usage_trend),
            "predicted_peak_usage": float(hourly_usage.max()["resource_usage"] * (1 + usage_trend))
        }

    def _calculate_confidence_score(self, df: pd.DataFrame) -> float:
        """Calculate confidence score for predictions."""
        # More data points = higher confidence
        data_points_score = min(len(df) / 1000, 0.5)  # Max 0.5 from data points

        # Consistency in patterns increases confidence
        std_dev = df["resource_usage"].std()
        mean = df["resource_usage"].mean()
        consistency_score = 0.5 * (1 - (std_dev / mean)) if mean != 0 else 0

        return data_points_score + consistency_score

    def _identify_bottlenecks(self, predictions: Dict) -> List[Dict]:
        """Identify potential bottlenecks based on predictions."""
        bottlenecks = []

        # Check for high resource usage during peak hours
        if predictions["predicted_peak_usage"] > 0.8:  # 80% capacity
            bottlenecks.append({
                "type": "resource_capacity",
                "severity": "high",
                "description": "Predicted peak usage exceeds 80% capacity",
                "mitigation": "Consider scaling resources during peak hours"
            })

        # Check for rapid growth trend
        if predictions["growth_trend"] > 0.1:  # 10% growth
            bottlenecks.append({
                "type": "growth_rate",
                "severity": "medium",
                "description": "Usage growing rapidly",
                "mitigation": "Plan for capacity expansion"
            })

        return bottlenecks

    def _get_average_metrics(self, gpt_id: str) -> Dict:
        """Get average performance metrics for a GPT."""
        recent_metrics = self.db.query(GPTPerformance).join(
            DashboardGPTSubscription
        ).filter(
            DashboardGPTSubscription.gpt_definition_id == gpt_id,
            GPTPerformance.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).all()

        if not recent_metrics:
            return {}

        # Calculate averages
        metrics_sum = {}
        for metric in recent_metrics:
            for key, value in metric.metrics.items():
                metrics_sum[key] = metrics_sum.get(key, 0) + value

        return {
            key: value / len(recent_metrics)
            for key, value in metrics_sum.items()
        }

    def _calculate_rankings(
        self,
        gpt_id: str,
        comparative_metrics: Dict
    ) -> Dict:
        """Calculate rankings and percentiles."""
        rankings = {}
        
        # Get metrics for the target GPT
        target_metrics = comparative_metrics.get(gpt_id, {})
        if not target_metrics:
            return {}

        # Calculate rankings for each metric
        for metric in target_metrics.keys():
            values = [m.get(metric, 0) for m in comparative_metrics.values()]
            values.sort()
            
            target_value = target_metrics[metric]
            percentile = sum(1 for v in values if v <= target_value) / len(values)
            
            rankings[metric] = {
                "value": target_value,
                "percentile": percentile,
                "rank": sum(1 for v in values if v > target_value) + 1,
                "total": len(values)
            }

        return rankings

    def _identify_improvements(
        self,
        gpt_id: str,
        comparative_metrics: Dict
    ) -> List[Dict]:
        """Identify improvement opportunities based on comparative analysis."""
        improvements = []
        target_metrics = comparative_metrics.get(gpt_id, {})
        
        if not target_metrics:
            return []

        # Find top performer for each metric
        for metric in target_metrics.keys():
            top_performer_id = max(
                comparative_metrics.keys(),
                key=lambda k: comparative_metrics[k].get(metric, 0)
            )
            
            if top_performer_id != gpt_id:
                gap = (
                    comparative_metrics[top_performer_id][metric] -
                    target_metrics[metric]
                )
                
                if gap > 0.1:  # Significant gap
                    improvements.append({
                        "metric": metric,
                        "current_value": target_metrics[metric],
                        "top_value": comparative_metrics[top_performer_id][metric],
                        "gap": gap,
                        "priority": "high" if gap > 0.3 else "medium"
                    })

        return improvements

    async def get_resource_usage_metrics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict:
        """
        Get resource usage metrics for an organization.
        
        Args:
            org_id: The ID of the organization to analyze
            time_range: Time range for analysis (24h, 7d, 30d)
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:  # 30d
                start_time = end_time - timedelta(days=30)

            # Get usage data
            usage_data = self.db.query(ResourceUsage).filter(
                ResourceUsage.organization_id == org_id,
                ResourceUsage.timestamp >= start_time
            ).all()

            if not usage_data:
                return {
                    "total_usage": 0.0,
                    "average_usage": 0.0,
                    "peak_usage": 0.0,
                    "usage_by_type": {},
                    "timestamp": datetime.utcnow()
                }

            # Convert to DataFrame for analysis
            df = pd.DataFrame([
                {
                    "timestamp": u.timestamp,
                    "resource_type": u.resource_type,
                    "usage": u.usage_amount
                } for u in usage_data
            ])

            # Calculate metrics
            total_usage = df["usage"].sum()
            average_usage = df["usage"].mean()
            peak_usage = df["usage"].max()
            usage_by_type = df.groupby("resource_type")["usage"].sum().to_dict()

            return {
                "total_usage": float(total_usage),
                "average_usage": float(average_usage),
                "peak_usage": float(peak_usage),
                "usage_by_type": usage_by_type,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting resource usage metrics: {str(e)}"
            )

    async def get_sharing_patterns(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict:
        """
        Analyze resource sharing patterns.
        
        Args:
            org_id: The ID of the organization to analyze
            time_range: Time range for analysis (24h, 7d, 30d)
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:  # 30d
                start_time = end_time - timedelta(days=30)

            # Get sharing data
            sharing_data = self.db.query(ResourceSharing).filter(
                (ResourceSharing.source_org_id == org_id) | 
                (ResourceSharing.target_org_id == org_id),
                ResourceSharing.timestamp >= start_time
            ).all()

            if not sharing_data:
                return {
                    "frequent_pairs": [],
                    "sharing_frequency": {},
                    "resource_popularity": {},
                    "timestamp": datetime.utcnow()
                }

            # Analyze patterns
            df = pd.DataFrame([
                {
                    "timestamp": s.timestamp,
                    "source_org": s.source_org_id,
                    "target_org": s.target_org_id,
                    "resource_type": s.resource_type
                } for s in sharing_data
            ])

            # Find frequent pairs
            pairs = []
            for _, row in df.iterrows():
                if row["source_org"] == org_id:
                    pairs.append({"org_id": row["target_org"], "role": "receiver"})
                else:
                    pairs.append({"org_id": row["source_org"], "role": "provider"})

            # Calculate frequencies
            sharing_frequency = {}
            for pair in pairs:
                org = pair["org_id"]
                if org not in sharing_frequency:
                    sharing_frequency[org] = 1
                else:
                    sharing_frequency[org] += 1

            # Calculate resource popularity
            resource_popularity = df["resource_type"].value_counts().to_dict()

            return {
                "frequent_pairs": pairs[:10],  # Top 10 pairs
                "sharing_frequency": sharing_frequency,
                "resource_popularity": resource_popularity,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing sharing patterns: {str(e)}"
            )

    async def get_efficiency_metrics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict:
        """
        Calculate resource sharing efficiency metrics.
        
        Args:
            org_id: The ID of the organization to analyze
            time_range: Time range for analysis (24h, 7d, 30d)
        """
        try:
            # Get usage and sharing data
            usage_metrics = await self.get_resource_usage_metrics(org_id, time_range)
            sharing_patterns = await self.get_sharing_patterns(org_id, time_range)

            # Calculate utilization rate
            total_capacity = 100.0  # Example capacity
            utilization_rate = (usage_metrics["average_usage"] / total_capacity) * 100

            # Calculate sharing efficiency
            total_shares = sum(sharing_patterns["sharing_frequency"].values())
            sharing_efficiency = min(total_shares / 10.0, 1.0) * 100  # Example calculation

            # Calculate cost savings (example)
            cost_per_unit = 10.0  # Example cost
            cost_savings = total_shares * cost_per_unit * 0.3  # 30% savings

            # Calculate optimization score
            optimization_factors = [
                utilization_rate / 100.0,
                sharing_efficiency / 100.0,
                min(cost_savings / 1000.0, 1.0)  # Normalize to 0-1
            ]
            optimization_score = sum(optimization_factors) / len(optimization_factors) * 100

            return {
                "utilization_rate": float(utilization_rate),
                "sharing_efficiency": float(sharing_efficiency),
                "cost_savings": float(cost_savings),
                "optimization_score": float(optimization_score),
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating efficiency metrics: {str(e)}"
            )

    async def get_sharing_trends(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Dict:
        """
        Analyze resource sharing trends over time.
        
        Args:
            org_id: The ID of the organization to analyze
            time_range: Time range for analysis (24h, 7d, 30d)
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_range == "24h":
                start_time = end_time - timedelta(days=1)
                interval = "1H"
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
                interval = "1D"
            else:  # 30d
                start_time = end_time - timedelta(days=30)
                interval = "1D"

            # Get historical data
            usage_data = self.db.query(ResourceUsage).filter(
                ResourceUsage.organization_id == org_id,
                ResourceUsage.timestamp >= start_time
            ).all()

            sharing_data = self.db.query(ResourceSharing).filter(
                (ResourceSharing.source_org_id == org_id) | 
                (ResourceSharing.target_org_id == org_id),
                ResourceSharing.timestamp >= start_time
            ).all()

            # Convert to DataFrames
            usage_df = pd.DataFrame([
                {
                    "timestamp": u.timestamp,
                    "usage": u.usage_amount
                } for u in usage_data
            ])

            sharing_df = pd.DataFrame([
                {
                    "timestamp": s.timestamp,
                    "sharing": 1
                } for s in sharing_data
            ])

            # Resample data
            if not usage_df.empty:
                usage_trend = usage_df.set_index("timestamp").resample(interval)["usage"].mean().fillna(0).to_dict()
            else:
                usage_trend = {}

            if not sharing_df.empty:
                sharing_trend = sharing_df.set_index("timestamp").resample(interval)["sharing"].sum().fillna(0).to_dict()
            else:
                sharing_trend = {}

            # Calculate efficiency trend
            efficiency_trend = {}
            for timestamp in usage_trend.keys():
                usage = usage_trend.get(timestamp, 0)
                sharing = sharing_trend.get(timestamp, 0)
                if usage > 0:
                    efficiency = (sharing / usage) * 100
                else:
                    efficiency = 0
                efficiency_trend[timestamp.isoformat()] = float(efficiency)

            return {
                "usage_trend": [{
                    "timestamp": ts.isoformat(),
                    "value": float(val)
                } for ts, val in usage_trend.items()],
                "sharing_trend": [{
                    "timestamp": ts.isoformat(),
                    "value": float(val)
                } for ts, val in sharing_trend.items()],
                "efficiency_trend": [{
                    "timestamp": ts,
                    "value": val
                } for ts, val in efficiency_trend.items()],
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing sharing trends: {str(e)}"
            ) 