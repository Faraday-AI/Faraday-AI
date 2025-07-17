"""Compatibility schemas for the dashboard."""

from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

class CompatibilityCheck(BaseModel):
    """Compatibility check results."""
    is_compatible: bool
    compatibility_score: float
    details: Optional[Dict[str, Dict[str, str]]] = None
    impact: Optional[Dict[str, Dict[str, float]]] = None
    recommendations: Optional[List[str]] = None

class CompatibleGPTs(BaseModel):
    """Compatible GPTs data."""
    compatible_gpts: List[Dict[str, str]]
    metrics: Optional[Dict[str, Dict[str, float]]] = None
    rankings: Optional[Dict[str, int]] = None
    improvements: Optional[List[str]] = None

class IntegrationValidation(BaseModel):
    """Integration validation results."""
    is_valid: bool
    validation_score: float
    requirements: Optional[Dict[str, Dict[str, str]]] = None
    validation: Optional[Dict[str, Dict[str, bool]]] = None
    recommendations: Optional[List[str]] = None

class CompatibilityDashboard(BaseModel):
    """Compatibility dashboard data."""
    overall_stats: Dict[str, Dict[str, float]]
    gpt_metrics: Dict[str, Dict[str, float]]
    compatibility_issues: List[Dict[str, str]]
    recommendations: List[str]

class DependencyAnalysis(BaseModel):
    """Dependency analysis results."""
    dependencies: List[Dict[str, str]]
    impact: Optional[Dict[str, Dict[str, float]]] = None
    conflicts: Optional[List[Dict[str, str]]] = None
    recommendations: Optional[List[str]] = None

class VersionCompatibility(BaseModel):
    """Version compatibility data."""
    is_compatible: bool
    current_version: str
    latest_version: str
    updates: Optional[List[Dict[str, str]]] = None
    impact: Optional[Dict[str, Dict[str, float]]] = None
    recommendations: Optional[List[str]] = None

class ResourceRequirements(BaseModel):
    """Resource requirements data."""
    requirements: Dict[str, Dict[str, float]]
    analysis: Optional[Dict[str, Dict[str, float]]] = None
    optimization: Optional[Dict[str, List[str]]] = None
    recommendations: Optional[List[str]] = None 