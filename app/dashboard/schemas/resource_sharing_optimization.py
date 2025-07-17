"""
Resource Sharing Optimization Schemas

This module provides Pydantic models for resource sharing optimization features
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SharingPatternResponse(BaseModel):
    """Response schema for sharing pattern analysis."""
    patterns: Dict[str, Any] = Field(..., description="Identified sharing patterns")
    success_metrics: Dict[str, float] = Field(..., description="Success metrics")
    optimal_configurations: List[Dict[str, Any]] = Field(..., description="Optimal configurations")
    recommendations: List[Dict[str, Any]] = Field(..., description="Pattern-based recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "patterns": {
                    "resource_types": {"gpt": 10, "dataset": 5},
                    "access_levels": {"read": 8, "write": 7},
                    "temporal_patterns": {"9": 5, "14": 8},
                    "usage_patterns": {"frequency": [10, 15, 20]},
                    "success_patterns": {"active": 12, "pending": 3}
                },
                "success_metrics": {
                    "success_rate": 0.85,
                    "usage_effectiveness": 0.78,
                    "collaboration_score": 0.82
                },
                "optimal_configurations": [
                    {
                        "resource_type": "gpt",
                        "access_level": "write",
                        "success_rate": 0.9,
                        "usage_effectiveness": 0.85,
                        "sample_size": 10
                    }
                ],
                "recommendations": [
                    {
                        "type": "resource_type",
                        "recommendation": "Focus on sharing gpt resources",
                        "confidence": 0.8,
                        "impact": "high"
                    }
                ]
            }
        }

class AccessPredictionResponse(BaseModel):
    """Response schema for access need predictions."""
    current_access: Optional[Dict[str, Any]] = Field(None, description="Current access state")
    predictions: Dict[str, Any] = Field(..., description="Access level predictions")
    confidence_score: float = Field(..., description="Prediction confidence score")
    recommendations: List[Dict[str, Any]] = Field(..., description="Access recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "current_access": {
                    "level": "read",
                    "usage_metrics": {"frequency": 100, "volume": 500}
                },
                "predictions": {
                    "predicted_access_level": "write",
                    "prediction_factors": {
                        "usage_trend": "increasing",
                        "growth_rate": 0.25
                    },
                    "timeline": "within_week"
                },
                "confidence_score": 0.85,
                "recommendations": [
                    {
                        "type": "access_upgrade",
                        "recommendation": "Upgrade to write access within 7 days",
                        "confidence": 0.85,
                        "impact": "medium"
                    }
                ]
            }
        }

class SecurityRiskResponse(BaseModel):
    """Response schema for security risk detection."""
    anomalies: List[Dict[str, Any]] = Field(..., description="Detected anomalies")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Identified risk factors")
    risk_assessment: Dict[str, Any] = Field(..., description="Overall risk assessment")
    mitigation_suggestions: List[Dict[str, Any]] = Field(..., description="Risk mitigation suggestions")

    class Config:
        json_schema_extra = {
            "example": {
                "anomalies": [
                    {
                        "type": "high_frequency_access",
                        "severity": "high",
                        "details": {
                            "frequency": 150,
                            "normal_range": [0, 100]
                        }
                    }
                ],
                "risk_factors": [
                    {
                        "factor": "unusual_access_pattern",
                        "severity": "medium",
                        "context": "Off-hours access spike"
                    }
                ],
                "risk_assessment": {
                    "overall_risk": "medium",
                    "risk_score": 0.65,
                    "confidence": 0.8
                },
                "mitigation_suggestions": [
                    {
                        "action": "implement_rate_limiting",
                        "priority": "high",
                        "impact": "immediate"
                    }
                ]
            }
        }

class SharingScheduleResponse(BaseModel):
    """Response schema for sharing schedule suggestions."""
    suggested_schedule: Dict[str, Any] = Field(..., description="Suggested sharing schedule")
    optimization_impact: Dict[str, Any] = Field(..., description="Schedule impact analysis")
    implementation_plan: List[Dict[str, Any]] = Field(..., description="Implementation steps")

    class Config:
        json_schema_extra = {
            "example": {
                "suggested_schedule": {
                    "peak_hours": [9, 10, 11, 14, 15, 16],
                    "off_peak_hours": [0, 1, 2, 3, 4, 5],
                    "recommended_windows": [
                        {
                            "start": 1,
                            "end": 4,
                            "duration": 4
                        }
                    ],
                    "blackout_periods": [
                        {
                            "start": 14,
                            "end": 16,
                            "duration": 3
                        }
                    ]
                },
                "optimization_impact": {
                    "resource_utilization_improvement": 0.2,
                    "cost_reduction": 0.15,
                    "performance_impact": "minimal",
                    "implementation_complexity": "low"
                },
                "implementation_plan": [
                    {
                        "phase": "setup_sharing_windows",
                        "actions": [
                            {
                                "type": "configure_window",
                                "window": {"start": 1, "end": 4},
                                "priority": "high"
                            }
                        ],
                        "timeline": "immediate"
                    }
                ]
            }
        }

class CrossOrgOptimizationResponse(BaseModel):
    """Response schema for cross-organization optimization."""
    current_efficiency: Dict[str, float] = Field(..., description="Current efficiency metrics")
    optimization_opportunities: List[Dict[str, Any]] = Field(..., description="Identified opportunities")
    recommendations: List[Dict[str, Any]] = Field(..., description="Optimization recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "current_efficiency": {
                    "resource_utilization": 0.65,
                    "access_optimization": 0.75,
                    "sharing_effectiveness": 0.70,
                    "cost_efficiency": 0.80
                },
                "optimization_opportunities": [
                    {
                        "type": "resource_utilization",
                        "current_value": 0.65,
                        "target_value": 0.8,
                        "impact": "high",
                        "difficulty": "medium"
                    }
                ],
                "recommendations": [
                    {
                        "type": "resource_consolidation",
                        "recommendation": "Consolidate similar resources",
                        "impact": "high",
                        "timeline": "2_weeks"
                    }
                ]
            }
        } 