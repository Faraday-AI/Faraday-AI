"""Analytics schemas for the dashboard."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class PerformanceTrends(BaseModel):
    """Performance trends data."""
    trends: Dict[str, List[float]]
    timestamps: List[datetime]
    metrics: Dict[str, Dict[str, float]]
    forecast: Optional[Dict[str, List[float]]] = None
    anomalies: Optional[Dict[str, List[Dict[str, float]]]] = None
    correlations: Optional[Dict[str, Dict[str, float]]] = None
    insights: Optional[Dict[str, str]] = None
    impact: Optional[Dict[str, Dict[str, float]]] = None

class ResourcePrediction(BaseModel):
    """Resource usage prediction data."""
    predictions: Dict[str, List[float]]
    timestamps: List[datetime]
    confidence: Optional[Dict[str, float]] = None
    impact: Optional[Dict[str, Dict[str, float]]] = None
    optimization: Optional[Dict[str, List[str]]] = None
    risk: Optional[Dict[str, Dict[str, float]]] = None
    mitigation: Optional[Dict[str, List[str]]] = None

class ComparativeAnalysis(BaseModel):
    """Comparative analysis data."""
    metrics: Dict[str, Dict[str, float]]
    benchmarks: Optional[Dict[str, Dict[str, float]]] = None
    rankings: Optional[Dict[str, int]] = None
    improvements: Optional[Dict[str, List[str]]] = None
    insights: Optional[Dict[str, str]] = None
    opportunities: Optional[Dict[str, List[str]]] = None

class AnalyticsDashboard(BaseModel):
    """Analytics dashboard data."""
    summary: Dict[str, Dict[str, float]]
    trends: Optional[Dict[str, List[float]]] = None
    alerts: Optional[Dict[str, Dict[str, str]]] = None
    optimization: Optional[Dict[str, List[str]]] = None
    insights: Optional[Dict[str, str]] = None
    forecast: Optional[Dict[str, List[float]]] = None

class UsagePatterns(BaseModel):
    """Usage patterns data."""
    patterns: Dict[str, Dict[str, float]]
    seasonality: Optional[Dict[str, Dict[str, float]]] = None
    correlation: Optional[Dict[str, Dict[str, float]]] = None
    forecast: Optional[Dict[str, List[float]]] = None
    insights: Optional[Dict[str, str]] = None
    optimization: Optional[Dict[str, List[str]]] = None

class PerformanceMetrics(BaseModel):
    """Performance metrics data."""
    metrics: Dict[str, Dict[str, float]]
    breakdown: Optional[Dict[str, Dict[str, float]]] = None
    trends: Optional[Dict[str, List[float]]] = None
    benchmarks: Optional[Dict[str, Dict[str, float]]] = None
    insights: Optional[Dict[str, str]] = None
    optimization: Optional[Dict[str, List[str]]] = None

class OptimizationOpportunities(BaseModel):
    """Optimization opportunities data."""
    opportunities: List[Dict[str, str]]
    impact: Optional[Dict[str, Dict[str, float]]] = None
    priority: Optional[Dict[str, int]] = None
    recommendations: Optional[Dict[str, List[str]]] = None
    insights: Optional[Dict[str, str]] = None
    forecast: Optional[Dict[str, List[float]]] = None

class AnalyticsInsights(BaseModel):
    """Analytics insights data."""
    insights: Dict[str, str]
    trends: Optional[Dict[str, str]] = None
    patterns: Optional[Dict[str, str]] = None
    opportunities: Optional[Dict[str, str]] = None

class AnalyticsForecast(BaseModel):
    """Analytics forecast data."""
    forecast: Dict[str, List[float]]
    timestamps: List[datetime]
    performance: Optional[Dict[str, List[float]]] = None
    usage: Optional[Dict[str, List[float]]] = None
    optimization: Optional[Dict[str, List[float]]] = None

class AnalyticsCorrelation(BaseModel):
    """Analytics correlation data."""
    correlations: Dict[str, Dict[str, float]]
    metrics: Optional[Dict[str, Dict[str, float]]] = None
    patterns: Optional[Dict[str, Dict[str, float]]] = None
    impact: Optional[Dict[str, Dict[str, float]]] = None

class AnalyticsAnomaly(BaseModel):
    """Analytics anomaly data."""
    anomalies: List[Dict[str, str]]
    detection: Optional[Dict[str, Dict[str, float]]] = None
    analysis: Optional[Dict[str, str]] = None
    mitigation: Optional[Dict[str, List[str]]] = None 