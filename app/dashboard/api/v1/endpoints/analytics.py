"""
Analytics API endpoints for the Faraday AI Dashboard.
"""

from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from ....services.analytics_service import AnalyticsService
from ....models.gpt_models import GPTCategory, GPTType
from ....schemas.analytics_schemas import (
    PerformanceTrends,
    ResourcePrediction,
    ComparativeAnalysis,
    AnalyticsDashboard,
    UsagePatterns,
    PerformanceMetrics,
    OptimizationOpportunities,
    AnalyticsInsights,
    AnalyticsForecast,
    AnalyticsCorrelation,
    AnalyticsAnomaly
)
from ....schemas.resource_sharing_analytics import ResourceSharingAnalytics

router = APIRouter()

@router.get("/performance/{gpt_id}/trends", response_model=PerformanceTrends)
async def get_performance_trends(
    gpt_id: str,
    time_range: str = Query("7d", regex="^(24h|7d|30d)$"),
    metrics: Optional[List[str]] = Query(None),
    include_forecast: bool = Query(False, description="Include trend forecast"),
    include_anomalies: bool = Query(True, description="Include anomaly detection"),
    include_correlation: bool = Query(True, description="Include metric correlations"),
    include_insights: bool = Query(True, description="Include trend insights"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    db: Session = Depends(get_db)
):
    """
    Get performance trends for a specific GPT.
    
    Args:
        gpt_id: The ID of the GPT to analyze
        time_range: Time range for analysis (24h, 7d, 30d)
        metrics: Optional list of specific metrics to analyze
        include_forecast: Whether to include trend forecast
        include_anomalies: Whether to include anomaly detection
        include_correlation: Whether to include metric correlations
        include_insights: Whether to include trend insights
        include_impact: Whether to include impact analysis
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_performance_trends(
        gpt_id=gpt_id,
        time_range=time_range,
        metrics=metrics
    )
    
    if include_forecast:
        result["forecast"] = await analytics_service.get_trend_forecast(
            gpt_id=gpt_id,
            time_range=time_range,
            metrics=metrics
        )
    
    if include_anomalies:
        result["anomalies"] = await analytics_service.detect_anomalies(
            gpt_id=gpt_id,
            time_range=time_range,
            metrics=metrics
        )
    
    if include_correlation:
        result["correlations"] = await analytics_service.analyze_correlations(
            gpt_id=gpt_id,
            time_range=time_range,
            metrics=metrics
        )
    
    if include_insights:
        result["insights"] = await analytics_service.get_trend_insights(
            gpt_id=gpt_id,
            time_range=time_range,
            metrics=metrics
        )
    
    if include_impact:
        result["impact"] = await analytics_service.analyze_trend_impact(
            gpt_id=gpt_id,
            time_range=time_range,
            metrics=metrics
        )
    
    return result

@router.get("/performance/{gpt_id}/resource-prediction", response_model=ResourcePrediction)
async def predict_resource_usage(
    gpt_id: str,
    prediction_window: str = Query("24h", regex="^(24h|7d)$"),
    include_confidence: bool = Query(True, description="Include confidence scores"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_optimization: bool = Query(True, description="Include optimization recommendations"),
    include_risk: bool = Query(True, description="Include risk assessment"),
    include_mitigation: bool = Query(True, description="Include mitigation strategies"),
    db: Session = Depends(get_db)
):
    """
    Predict resource usage for a specific GPT.
    
    Args:
        gpt_id: The ID of the GPT to analyze
        prediction_window: Time window for prediction (24h, 7d)
        include_confidence: Whether to include confidence scores
        include_impact: Whether to include impact analysis
        include_optimization: Whether to include optimization recommendations
        include_risk: Whether to include risk assessment
        include_mitigation: Whether to include mitigation strategies
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.predict_resource_usage(
        gpt_id=gpt_id,
        prediction_window=prediction_window
    )
    
    if include_confidence:
        result["confidence"] = await analytics_service.get_prediction_confidence(
            gpt_id=gpt_id,
            prediction_window=prediction_window
        )
    
    if include_impact:
        result["impact"] = await analytics_service.analyze_resource_impact(
            gpt_id=gpt_id,
            prediction_window=prediction_window
        )
    
    if include_optimization:
        result["optimization"] = await analytics_service.get_resource_optimization(
            gpt_id=gpt_id,
            prediction_window=prediction_window
        )
    
    if include_risk:
        result["risk"] = await analytics_service.assess_resource_risk(
            gpt_id=gpt_id,
            prediction_window=prediction_window
        )
    
    if include_mitigation:
        result["mitigation"] = await analytics_service.get_mitigation_strategies(
            gpt_id=gpt_id,
            prediction_window=prediction_window
        )
    
    return result

@router.get("/performance/{gpt_id}/comparative", response_model=ComparativeAnalysis)
async def get_comparative_analysis(
    gpt_id: str,
    category: Optional[GPTCategory] = None,
    include_benchmarks: bool = Query(True, description="Include industry benchmarks"),
    include_rankings: bool = Query(True, description="Include detailed rankings"),
    include_improvements: bool = Query(True, description="Include improvement recommendations"),
    include_insights: bool = Query(True, description="Include comparative insights"),
    include_opportunities: bool = Query(True, description="Include improvement opportunities"),
    db: Session = Depends(get_db)
):
    """
    Get comparative analysis for a specific GPT.
    
    Args:
        gpt_id: The ID of the GPT to analyze
        category: Optional category to filter comparisons
        include_benchmarks: Whether to include industry benchmarks
        include_rankings: Whether to include detailed rankings
        include_improvements: Whether to include improvement recommendations
        include_insights: Whether to include comparative insights
        include_opportunities: Whether to include improvement opportunities
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_comparative_analysis(
        gpt_id=gpt_id,
        category=category
    )
    
    if include_benchmarks:
        result["benchmarks"] = await analytics_service.get_industry_benchmarks(
            gpt_id=gpt_id,
            category=category
        )
    
    if include_rankings:
        result["rankings"] = await analytics_service.get_comparative_rankings(
            gpt_id=gpt_id,
            category=category
        )
    
    if include_improvements:
        result["improvements"] = await analytics_service.get_improvement_recommendations(
            gpt_id=gpt_id,
            category=category
        )
    
    if include_insights:
        result["insights"] = await analytics_service.get_comparative_insights(
            gpt_id=gpt_id,
            category=category
        )
    
    if include_opportunities:
        result["opportunities"] = await analytics_service.get_improvement_opportunities(
            gpt_id=gpt_id,
            category=category
        )
    
    return result

@router.get("/performance/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    category: Optional[GPTCategory] = None,
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_alerts: bool = Query(True, description="Include alert status"),
    include_optimization: bool = Query(True, description="Include optimization opportunities"),
    include_insights: bool = Query(True, description="Include dashboard insights"),
    include_forecast: bool = Query(True, description="Include performance forecast"),
    db: Session = Depends(get_db)
):
    """
    Get analytics dashboard data.
    
    Args:
        time_range: Time range for analysis (24h, 7d, 30d)
        category: Optional category to filter GPTs
        include_trends: Whether to include trend analysis
        include_alerts: Whether to include alert status
        include_optimization: Whether to include optimization opportunities
        include_insights: Whether to include dashboard insights
        include_forecast: Whether to include performance forecast
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_analytics_dashboard(
        time_range=time_range,
        category=category
    )
    
    if include_trends:
        result["trends"] = await analytics_service.get_dashboard_trends(
            time_range=time_range,
            category=category
        )
    
    if include_alerts:
        result["alerts"] = await analytics_service.get_dashboard_alerts(
            time_range=time_range,
            category=category
        )
    
    if include_optimization:
        result["optimization"] = await analytics_service.get_dashboard_optimization(
            time_range=time_range,
            category=category
        )
    
    if include_insights:
        result["insights"] = await analytics_service.get_dashboard_insights(
            time_range=time_range,
            category=category
        )
    
    if include_forecast:
        result["forecast"] = await analytics_service.get_dashboard_forecast(
            time_range=time_range,
            category=category
        )
    
    return result

@router.get("/usage/patterns", response_model=UsagePatterns)
async def get_usage_patterns(
    gpt_id: Optional[str] = None,
    time_range: str = Query("7d", regex="^(24h|7d|30d)$"),
    include_seasonality: bool = Query(True, description="Include seasonality analysis"),
    include_correlation: bool = Query(True, description="Include correlation analysis"),
    include_forecast: bool = Query(True, description="Include usage forecast"),
    include_insights: bool = Query(True, description="Include usage insights"),
    include_optimization: bool = Query(True, description="Include usage optimization"),
    db: Session = Depends(get_db)
):
    """
    Get usage patterns analysis.
    
    Args:
        gpt_id: Optional GPT ID to analyze
        time_range: Time range for analysis (24h, 7d, 30d)
        include_seasonality: Whether to include seasonality analysis
        include_correlation: Whether to include correlation analysis
        include_forecast: Whether to include usage forecast
        include_insights: Whether to include usage insights
        include_optimization: Whether to include usage optimization
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_usage_patterns(
        gpt_id=gpt_id,
        time_range=time_range
    )
    
    if include_seasonality:
        result["seasonality"] = await analytics_service.analyze_seasonality(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_correlation:
        result["correlation"] = await analytics_service.analyze_usage_correlation(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_forecast:
        result["forecast"] = await analytics_service.get_usage_forecast(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_insights:
        result["insights"] = await analytics_service.get_usage_insights(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_optimization:
        result["optimization"] = await analytics_service.get_usage_optimization(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    return result

@router.get("/performance/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(
    gpt_id: Optional[str] = None,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_breakdown: bool = Query(True, description="Include metric breakdown"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_benchmarks: bool = Query(True, description="Include benchmark comparison"),
    include_insights: bool = Query(True, description="Include performance insights"),
    include_optimization: bool = Query(True, description="Include performance optimization"),
    db: Session = Depends(get_db)
):
    """
    Get detailed performance metrics.
    
    Args:
        gpt_id: Optional GPT ID to analyze
        time_range: Time range for analysis (24h, 7d, 30d)
        include_breakdown: Whether to include metric breakdown
        include_trends: Whether to include trend analysis
        include_benchmarks: Whether to include benchmark comparison
        include_insights: Whether to include performance insights
        include_optimization: Whether to include performance optimization
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_performance_metrics(
        gpt_id=gpt_id,
        time_range=time_range
    )
    
    if include_breakdown:
        result["breakdown"] = await analytics_service.get_metric_breakdown(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_trends:
        result["trends"] = await analytics_service.get_metric_trends(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_benchmarks:
        result["benchmarks"] = await analytics_service.get_metric_benchmarks(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_insights:
        result["insights"] = await analytics_service.get_performance_insights(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_optimization:
        result["optimization"] = await analytics_service.get_performance_optimization(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    return result

@router.get("/optimization/opportunities", response_model=OptimizationOpportunities)
async def get_optimization_opportunities(
    gpt_id: Optional[str] = None,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_priority: bool = Query(True, description="Include priority ranking"),
    include_recommendations: bool = Query(True, description="Include optimization recommendations"),
    include_insights: bool = Query(True, description="Include optimization insights"),
    include_forecast: bool = Query(True, description="Include optimization forecast"),
    db: Session = Depends(get_db)
):
    """
    Get optimization opportunities.
    
    Args:
        gpt_id: Optional GPT ID to analyze
        time_range: Time range for analysis (24h, 7d, 30d)
        include_impact: Whether to include impact analysis
        include_priority: Whether to include priority ranking
        include_recommendations: Whether to include optimization recommendations
        include_insights: Whether to include optimization insights
        include_forecast: Whether to include optimization forecast
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_optimization_opportunities(
        gpt_id=gpt_id,
        time_range=time_range
    )
    
    if include_impact:
        result["impact"] = await analytics_service.analyze_optimization_impact(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_priority:
        result["priority"] = await analytics_service.get_optimization_priority(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_recommendations:
        result["recommendations"] = await analytics_service.get_optimization_recommendations(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_insights:
        result["insights"] = await analytics_service.get_optimization_insights(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    if include_forecast:
        result["forecast"] = await analytics_service.get_optimization_forecast(
            gpt_id=gpt_id,
            time_range=time_range
        )
    
    return result

@router.get("/insights", response_model=AnalyticsInsights)
async def get_analytics_insights(
    gpt_id: Optional[str] = None,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_trends: bool = Query(True, description="Include trend insights"),
    include_patterns: bool = Query(True, description="Include pattern insights"),
    include_opportunities: bool = Query(True, description="Include opportunity insights"),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics insights."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics_insights(
        gpt_id=gpt_id,
        time_range=time_range,
        include_trends=include_trends,
        include_patterns=include_patterns,
        include_opportunities=include_opportunities
    )

@router.get("/forecast", response_model=AnalyticsForecast)
async def get_analytics_forecast(
    gpt_id: Optional[str] = None,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_performance: bool = Query(True, description="Include performance forecast"),
    include_usage: bool = Query(True, description="Include usage forecast"),
    include_optimization: bool = Query(True, description="Include optimization forecast"),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics forecast."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics_forecast(
        gpt_id=gpt_id,
        time_range=time_range,
        include_performance=include_performance,
        include_usage=include_usage,
        include_optimization=include_optimization
    )

@router.get("/correlation", response_model=AnalyticsCorrelation)
async def get_analytics_correlation(
    gpt_id: Optional[str] = None,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_metrics: bool = Query(True, description="Include metric correlations"),
    include_patterns: bool = Query(True, description="Include pattern correlations"),
    include_impact: bool = Query(True, description="Include impact correlations"),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics correlations."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics_correlation(
        gpt_id=gpt_id,
        time_range=time_range,
        include_metrics=include_metrics,
        include_patterns=include_patterns,
        include_impact=include_impact
    )

@router.get("/anomaly", response_model=AnalyticsAnomaly)
async def get_analytics_anomaly(
    gpt_id: Optional[str] = None,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_detection: bool = Query(True, description="Include anomaly detection"),
    include_analysis: bool = Query(True, description="Include anomaly analysis"),
    include_mitigation: bool = Query(True, description="Include mitigation strategies"),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics anomaly detection."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics_anomaly(
        gpt_id=gpt_id,
        time_range=time_range,
        include_detection=include_detection,
        include_analysis=include_analysis,
        include_mitigation=include_mitigation
    )

@router.get("/resource-sharing/{org_id}", response_model=ResourceSharingAnalytics)
async def get_resource_sharing_analytics(
    org_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_patterns: bool = Query(True, description="Include sharing patterns analysis"),
    include_efficiency: bool = Query(True, description="Include efficiency metrics"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for resource sharing.
    
    Args:
        org_id: The ID of the organization to analyze
        time_range: Time range for analysis (24h, 7d, 30d)
        include_patterns: Whether to include sharing patterns analysis
        include_efficiency: Whether to include efficiency metrics
        include_trends: Whether to include trend analysis
    """
    analytics_service = AnalyticsService(db)
    result = {
        "usage_metrics": await analytics_service.get_resource_usage_metrics(
            org_id=org_id,
            time_range=time_range
        ),
        "timestamp": datetime.utcnow()
    }
    
    if include_patterns:
        result["sharing_patterns"] = await analytics_service.get_sharing_patterns(
            org_id=org_id,
            time_range=time_range
        )
    
    if include_efficiency:
        result["efficiency_metrics"] = await analytics_service.get_efficiency_metrics(
            org_id=org_id,
            time_range=time_range
        )
    
    if include_trends:
        result["trends"] = await analytics_service.get_sharing_trends(
            org_id=org_id,
            time_range=time_range
        )
    
    return result 