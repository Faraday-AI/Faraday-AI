"""
Predictive Access Management Service

This module provides predictive access management capabilities for resource sharing
in the Faraday AI Dashboard, using AI to predict access needs and security risks.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..models.organization_models import (
    Organization,
    OrganizationResource,
    OrganizationCollaboration
)
from .smart_sharing_patterns_service import SmartSharingPatternsService

class PredictiveAccessService:
    def __init__(self, db: Session):
        self.db = db
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.patterns_service = SmartSharingPatternsService(db)

    async def predict_access_needs(
        self,
        org_id: str,
        resource_id: str,
        prediction_window: str = "7d"
    ) -> Dict[str, Any]:
        """Predict future access level needs for a resource."""
        try:
            # Get historical access patterns
            access_history = await self._get_access_history(org_id, resource_id)
            
            # Analyze usage trends
            usage_trends = await self._analyze_usage_trends(access_history)
            
            # Generate predictions
            predictions = await self._generate_access_predictions(
                access_history,
                usage_trends,
                prediction_window
            )

            return {
                "current_access": access_history[-1] if access_history else None,
                "predictions": predictions,
                "confidence_score": await self._calculate_prediction_confidence(
                    access_history,
                    predictions
                ),
                "recommendations": await self._generate_access_recommendations(
                    access_history,
                    predictions
                )
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error predicting access needs: {str(e)}"
            )

    async def detect_security_risks(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> List[Dict[str, Any]]:
        """Detect potential security risks in resource sharing."""
        try:
            # Get recent access patterns
            access_patterns = await self._get_recent_access_patterns(org_id, time_range)
            
            # Detect anomalies
            anomalies = await self._detect_access_anomalies(access_patterns)
            
            # Analyze risk factors
            risk_factors = await self._analyze_risk_factors(access_patterns)
            
            # Generate risk assessments
            risks = await self._generate_risk_assessments(
                anomalies,
                risk_factors
            )

            return risks

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error detecting security risks: {str(e)}"
            )

    async def get_access_optimization_suggestions(
        self,
        org_id: str
    ) -> List[Dict[str, Any]]:
        """Get suggestions for optimizing access levels."""
        try:
            # Get current access configurations
            current_configs = await self._get_access_configurations(org_id)
            
            # Get sharing patterns
            sharing_patterns = await self.patterns_service.analyze_sharing_patterns(org_id)
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(
                current_configs,
                sharing_patterns
            )

            return suggestions

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating optimization suggestions: {str(e)}"
            )

    async def _get_access_history(
        self,
        org_id: str,
        resource_id: str
    ) -> List[Dict[str, Any]]:
        """Get historical access data for a resource."""
        try:
            collaborations = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id)
            ).all()

            history = []
            for collab in collaborations:
                if "shared_resources" in collab.settings:
                    for resource in collab.settings["shared_resources"]:
                        if resource["resource_id"] == resource_id:
                            history.append({
                                "timestamp": datetime.fromisoformat(resource["created_at"]),
                                "access_level": resource["access_level"],
                                "usage_metrics": resource.get("usage_metrics", {}),
                                "status": resource["status"]
                            })

            return sorted(history, key=lambda x: x["timestamp"])

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving access history: {str(e)}"
            )

    async def _analyze_usage_trends(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze usage trends from historical data."""
        if not history:
            return {
                "trend": "stable",
                "growth_rate": 0.0,
                "volatility": 0.0
            }

        usage_values = []
        for entry in history:
            if entry["usage_metrics"]:
                avg_usage = sum(entry["usage_metrics"].values()) / len(entry["usage_metrics"])
                usage_values.append(avg_usage)

        if not usage_values:
            return {
                "trend": "stable",
                "growth_rate": 0.0,
                "volatility": 0.0
            }

        # Calculate trend
        growth_rate = (usage_values[-1] - usage_values[0]) / usage_values[0] \
            if len(usage_values) > 1 else 0.0
        
        # Calculate volatility
        volatility = np.std(usage_values) / np.mean(usage_values) \
            if len(usage_values) > 1 else 0.0

        return {
            "trend": "increasing" if growth_rate > 0.1 else "decreasing" if growth_rate < -0.1 else "stable",
            "growth_rate": growth_rate,
            "volatility": volatility
        }

    async def _generate_access_predictions(
        self,
        history: List[Dict[str, Any]],
        trends: Dict[str, Any],
        prediction_window: str
    ) -> Dict[str, Any]:
        """Generate access level predictions."""
        if not history:
            return {
                "predicted_access_level": None,
                "prediction_factors": {},
                "timeline": None
            }

        current_access = history[-1]["access_level"]
        usage_trend = trends["trend"]
        growth_rate = trends["growth_rate"]

        # Predict access level needs
        if usage_trend == "increasing" and growth_rate > 0.2:
            predicted_access = self._get_next_access_level(current_access)
            timeline = "within_week" if growth_rate > 0.5 else "within_month"
        else:
            predicted_access = current_access
            timeline = "stable"

        return {
            "predicted_access_level": predicted_access,
            "prediction_factors": {
                "usage_trend": usage_trend,
                "growth_rate": growth_rate,
                "current_access": current_access
            },
            "timeline": timeline
        }

    async def _detect_access_anomalies(
        self,
        access_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in access patterns."""
        if not access_patterns:
            return []

        # Prepare features for anomaly detection
        features = []
        for pattern in access_patterns:
            feature_vector = [
                hash(pattern["access_level"]) % 100,
                float(pattern["usage_metrics"].get("frequency", 0)),
                float(pattern["usage_metrics"].get("duration", 0)),
                float(pattern["usage_metrics"].get("volume", 0))
            ]
            features.append(feature_vector)

        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Detect anomalies
        anomaly_scores = self.anomaly_detector.fit_predict(features_scaled)

        # Collect anomalies
        anomalies = []
        for i, score in enumerate(anomaly_scores):
            if score == -1:  # Anomaly detected
                anomalies.append({
                    "pattern": access_patterns[i],
                    "anomaly_type": self._classify_anomaly(access_patterns[i]),
                    "severity": "high" if self._calculate_anomaly_severity(access_patterns[i]) > 0.8 else "medium",
                    "timestamp": access_patterns[i]["timestamp"]
                })

        return anomalies

    def _get_next_access_level(self, current_access: str) -> str:
        """Get the next higher access level."""
        access_levels = {
            "read": "write",
            "write": "admin",
            "admin": "admin"  # No higher level
        }
        return access_levels.get(current_access, current_access)

    def _classify_anomaly(self, pattern: Dict[str, Any]) -> str:
        """Classify the type of access anomaly."""
        metrics = pattern["usage_metrics"]
        
        if metrics.get("frequency", 0) > 100:
            return "high_frequency_access"
        elif metrics.get("volume", 0) > 1000:
            return "high_volume_access"
        elif metrics.get("duration", 0) > 3600:
            return "extended_duration"
        else:
            return "unusual_pattern"

    def _calculate_anomaly_severity(self, pattern: Dict[str, Any]) -> float:
        """Calculate the severity score of an anomaly."""
        metrics = pattern["usage_metrics"]
        
        # Calculate normalized scores for each metric
        frequency_score = min(metrics.get("frequency", 0) / 100, 1.0)
        volume_score = min(metrics.get("volume", 0) / 1000, 1.0)
        duration_score = min(metrics.get("duration", 0) / 3600, 1.0)
        
        # Weight the scores
        return (frequency_score * 0.4 + volume_score * 0.3 + duration_score * 0.3) 