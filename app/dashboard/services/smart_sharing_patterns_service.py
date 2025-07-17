"""
Smart Sharing Patterns Service

This module provides AI-driven analysis of resource sharing patterns and recommendations
for optimal sharing configurations in the Faraday AI Dashboard.
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

class SmartSharingPatternsService:
    def __init__(self, db: Session):
        self.db = db
        self.scaler = StandardScaler()

    async def analyze_sharing_patterns(
        self,
        org_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Analyze resource sharing patterns for an organization."""
        try:
            # Get historical sharing data
            sharing_history = await self._get_sharing_history(org_id, time_range)
            
            # Analyze patterns
            patterns = await self._identify_sharing_patterns(sharing_history)
            
            # Generate success metrics
            success_metrics = await self._calculate_success_metrics(sharing_history)
            
            # Identify optimal configurations
            optimal_configs = await self._identify_optimal_configurations(
                sharing_history,
                success_metrics
            )

            return {
                "patterns": patterns,
                "success_metrics": success_metrics,
                "optimal_configurations": optimal_configs,
                "recommendations": await self._generate_pattern_recommendations(
                    patterns,
                    success_metrics,
                    optimal_configs
                )
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing sharing patterns: {str(e)}"
            )

    async def predict_collaboration_opportunities(
        self,
        org_id: str
    ) -> List[Dict[str, Any]]:
        """Predict potential collaboration opportunities."""
        try:
            # Get organization's resource profile
            org_profile = await self._get_organization_profile(org_id)
            
            # Find complementary organizations
            opportunities = await self._find_complementary_organizations(
                org_id,
                org_profile
            )
            
            # Score and rank opportunities
            ranked_opportunities = await self._rank_collaboration_opportunities(
                opportunities,
                org_profile
            )

            return ranked_opportunities

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error predicting collaboration opportunities: {str(e)}"
            )

    async def get_sharing_recommendations(
        self,
        org_id: str,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get AI-driven sharing recommendations."""
        try:
            # Get current sharing state
            current_state = await self._get_current_sharing_state(org_id)
            
            # Analyze sharing effectiveness
            effectiveness = await self._analyze_sharing_effectiveness(current_state)
            
            # Generate recommendations
            recommendations = await self._generate_sharing_recommendations(
                current_state,
                effectiveness,
                resource_type
            )

            return recommendations

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating sharing recommendations: {str(e)}"
            )

    async def _get_sharing_history(
        self,
        org_id: str,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get historical sharing data."""
        try:
            # Calculate time window
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            # Query collaborations
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
                            "collaboration_id": collab.id,
                            "resource_type": resource["resource_type"],
                            "access_level": resource["access_level"],
                            "status": resource["status"],
                            "created_at": resource["created_at"],
                            "usage_metrics": resource.get("usage_metrics", {}),
                            "is_source": collab.source_org_id == org_id
                        })

            return history

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving sharing history: {str(e)}"
            )

    async def _identify_sharing_patterns(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify patterns in sharing behavior."""
        patterns = {
            "resource_types": {},
            "access_levels": {},
            "temporal_patterns": {},
            "usage_patterns": {},
            "success_patterns": {}
        }

        for entry in history:
            # Resource type patterns
            resource_type = entry["resource_type"]
            if resource_type not in patterns["resource_types"]:
                patterns["resource_types"][resource_type] = 0
            patterns["resource_types"][resource_type] += 1

            # Access level patterns
            access_level = entry["access_level"]
            if access_level not in patterns["access_levels"]:
                patterns["access_levels"][access_level] = 0
            patterns["access_levels"][access_level] += 1

            # Temporal patterns (time of day, day of week)
            created_at = datetime.fromisoformat(entry["created_at"])
            hour = created_at.hour
            weekday = created_at.weekday()
            
            if hour not in patterns["temporal_patterns"]:
                patterns["temporal_patterns"][hour] = 0
            patterns["temporal_patterns"][hour] += 1

            # Usage patterns
            if entry["usage_metrics"]:
                for metric, value in entry["usage_metrics"].items():
                    if metric not in patterns["usage_patterns"]:
                        patterns["usage_patterns"][metric] = []
                    patterns["usage_patterns"][metric].append(value)

            # Success patterns (based on status)
            status = entry["status"]
            if status not in patterns["success_patterns"]:
                patterns["success_patterns"][status] = 0
            patterns["success_patterns"][status] += 1

        return patterns

    async def _calculate_success_metrics(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate success metrics for sharing patterns."""
        total_shares = len(history)
        if total_shares == 0:
            return {
                "success_rate": 0.0,
                "usage_effectiveness": 0.0,
                "collaboration_score": 0.0
            }

        successful_shares = sum(1 for entry in history if entry["status"] == "active")
        
        # Calculate usage effectiveness
        usage_effectiveness = 0.0
        shares_with_metrics = 0
        for entry in history:
            if entry["usage_metrics"]:
                usage_effectiveness += sum(entry["usage_metrics"].values()) / len(entry["usage_metrics"])
                shares_with_metrics += 1
        
        if shares_with_metrics > 0:
            usage_effectiveness /= shares_with_metrics

        # Calculate collaboration score
        collaboration_score = (successful_shares / total_shares) * usage_effectiveness

        return {
            "success_rate": successful_shares / total_shares,
            "usage_effectiveness": usage_effectiveness,
            "collaboration_score": collaboration_score
        }

    async def _identify_optimal_configurations(
        self,
        history: List[Dict[str, Any]],
        success_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify optimal sharing configurations."""
        if not history:
            return []

        # Prepare data for clustering
        features = []
        for entry in history:
            feature_vector = [
                hash(entry["resource_type"]) % 100,  # Hash resource type to numeric
                hash(entry["access_level"]) % 100,   # Hash access level to numeric
                float(entry["usage_metrics"].get("utilization", 0)),
                float(entry["usage_metrics"].get("efficiency", 0))
            ]
            features.append(feature_vector)

        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Cluster configurations
        n_clusters = min(len(features), 5)  # Maximum 5 clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)

        # Analyze clusters
        optimal_configs = []
        for i in range(n_clusters):
            cluster_entries = [entry for j, entry in enumerate(history) if clusters[j] == i]
            if not cluster_entries:
                continue

            # Calculate cluster success metrics
            cluster_metrics = await self._calculate_success_metrics(cluster_entries)
            
            if cluster_metrics["success_rate"] > 0.7:  # Only include successful configurations
                optimal_configs.append({
                    "resource_type": max(
                        set(entry["resource_type"] for entry in cluster_entries),
                        key=lambda x: sum(1 for e in cluster_entries if e["resource_type"] == x)
                    ),
                    "access_level": max(
                        set(entry["access_level"] for entry in cluster_entries),
                        key=lambda x: sum(1 for e in cluster_entries if e["access_level"] == x)
                    ),
                    "success_rate": cluster_metrics["success_rate"],
                    "usage_effectiveness": cluster_metrics["usage_effectiveness"],
                    "sample_size": len(cluster_entries)
                })

        return sorted(
            optimal_configs,
            key=lambda x: (x["success_rate"], x["usage_effectiveness"]),
            reverse=True
        )

    async def _generate_pattern_recommendations(
        self,
        patterns: Dict[str, Any],
        success_metrics: Dict[str, float],
        optimal_configs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on pattern analysis."""
        recommendations = []

        # Resource type recommendations
        if patterns["resource_types"]:
            most_successful_type = max(
                patterns["resource_types"].items(),
                key=lambda x: x[1]
            )[0]
            recommendations.append({
                "type": "resource_type",
                "recommendation": f"Focus on sharing {most_successful_type} resources",
                "confidence": 0.8,
                "impact": "high"
            })

        # Access level recommendations
        if patterns["access_levels"]:
            optimal_access = max(
                patterns["access_levels"].items(),
                key=lambda x: x[1]
            )[0]
            recommendations.append({
                "type": "access_level",
                "recommendation": f"Consider {optimal_access} access for new shares",
                "confidence": 0.75,
                "impact": "medium"
            })

        # Temporal recommendations
        if patterns["temporal_patterns"]:
            best_hour = max(
                patterns["temporal_patterns"].items(),
                key=lambda x: x[1]
            )[0]
            recommendations.append({
                "type": "timing",
                "recommendation": f"Optimal sharing time around {best_hour}:00",
                "confidence": 0.7,
                "impact": "medium"
            })

        # Configuration recommendations
        if optimal_configs:
            best_config = optimal_configs[0]
            recommendations.append({
                "type": "configuration",
                "recommendation": (
                    f"Use {best_config['access_level']} access for "
                    f"{best_config['resource_type']} resources"
                ),
                "confidence": best_config["success_rate"],
                "impact": "high"
            })

        return recommendations

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