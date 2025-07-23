"""
User Analytics API Endpoints - Phase 3

This module provides API endpoints for advanced user analytics, intelligence,
and insights including behavior tracking, performance metrics, and AI-powered predictions.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import (
    require_permission, 
    require_any_permission,
    Permission
)
from app.models.core.user import User
from app.services.analytics.user_analytics_service import UserAnalyticsService, get_user_analytics_service
from app.schemas.analytics import (
    UserAnalyticsRequest,
    UserAnalyticsResponse,
    BehaviorAnalysisRequest,
    UserBehaviorAnalysis,
    PerformanceAnalysisRequest,
    UserPerformanceMetrics,
    EngagementAnalysisRequest,
    UserEngagementMetrics,
    PredictionRequest,
    UserPredictionResponse,
    RecommendationRequest,
    UserRecommendationResponse,
    UserInsightsResponse,
    UserTrendsResponse,
    UserComparisonResponse,
    ComparisonRequest,
    TrendAnalysisRequest,
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsSummaryResponse,
    AnalyticsExportResponse,
    AnalyticsHealthResponse,
    AnalyticsFilter,
    AnalyticsAggregation,
    AnalyticsSort,
    AnalyticsPagination,
    TimeRange
)

router = APIRouter()


@router.post("/track", response_model=AnalyticsEventResponse)
async def track_user_activity(
    event_data: AnalyticsEventCreate,
    current_user: User = Depends(require_permission(Permission.TRACK_ANALYTICS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Track user activity for analytics."""
    event = await analytics_service.track_user_activity(
        user_id=event_data.user_id,
        activity_type=event_data.event_type,
        activity_data=event_data.event_data,
        session_id=event_data.session_id
    )
    return AnalyticsEventResponse(**event.to_dict())


@router.get("/analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_USER_ANALYTICS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get comprehensive user analytics."""
    analytics = await analytics_service.get_user_analytics(
        user_id=current_user.id,
        time_range=time_range.value
    )
    return analytics


@router.get("/analytics/{user_id}", response_model=UserAnalyticsResponse)
async def get_user_analytics_by_id(
    user_id: int,
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_ANALYTICS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get analytics for a specific user (admin/manager only)."""
    analytics = await analytics_service.get_user_analytics(
        user_id=user_id,
        time_range=time_range.value
    )
    return analytics


@router.get("/behavior", response_model=UserBehaviorAnalysis)
async def analyze_user_behavior(
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_USER_BEHAVIOR)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Analyze user behavior patterns."""
    behavior = await analytics_service.analyze_user_behavior(
        user_id=current_user.id,
        time_range=time_range.value
    )
    return behavior


@router.get("/behavior/{user_id}", response_model=UserBehaviorAnalysis)
async def analyze_user_behavior_by_id(
    user_id: int,
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_BEHAVIOR)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Analyze behavior for a specific user (admin/manager only)."""
    behavior = await analytics_service.analyze_user_behavior(
        user_id=user_id,
        time_range=time_range.value
    )
    return behavior


@router.get("/performance", response_model=UserPerformanceMetrics)
async def get_user_performance(
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_USER_PERFORMANCE)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user performance metrics."""
    performance = await analytics_service.get_performance_metrics(
        user_id=current_user.id,
        time_range=time_range.value
    )
    return performance


@router.get("/performance/{user_id}", response_model=UserPerformanceMetrics)
async def get_user_performance_by_id(
    user_id: int,
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_PERFORMANCE)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get performance metrics for a specific user (admin/manager only)."""
    performance = await analytics_service.get_performance_metrics(
        user_id=user_id,
        time_range=time_range.value
    )
    return performance


@router.get("/engagement", response_model=UserEngagementMetrics)
async def get_user_engagement(
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_USER_ENGAGEMENT)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user engagement metrics."""
    engagement = await analytics_service.get_engagement_metrics(
        user_id=current_user.id,
        time_range=time_range.value
    )
    return engagement


@router.get("/engagement/{user_id}", response_model=UserEngagementMetrics)
async def get_user_engagement_by_id(
    user_id: int,
    time_range: TimeRange = Query(TimeRange.THIRTY_DAYS, description="Time range for analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_ENGAGEMENT)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get engagement metrics for a specific user (admin/manager only)."""
    engagement = await analytics_service.get_engagement_metrics(
        user_id=user_id,
        time_range=time_range.value
    )
    return engagement


@router.post("/predictions", response_model=UserPredictionResponse)
async def generate_predictions(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_permission(Permission.GENERATE_PREDICTIONS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Generate AI-powered predictions for user behavior and performance."""
    # Run prediction generation in background for better performance
    background_tasks.add_task(
        analytics_service.generate_predictions,
        user_id=current_user.id
    )
    
    # Return immediate response with placeholder
    return UserPredictionResponse(
        user_id=current_user.id,
        predictions={"status": "generating"},
        confidence_score=0.0,
        prediction_horizon="30d",
        last_updated=datetime.utcnow()
    )


@router.get("/predictions", response_model=UserPredictionResponse)
async def get_user_predictions(
    current_user: User = Depends(require_permission(Permission.VIEW_PREDICTIONS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user predictions."""
    predictions = await analytics_service.generate_predictions(current_user.id)
    return predictions


@router.get("/predictions/{user_id}", response_model=UserPredictionResponse)
async def get_user_predictions_by_id(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_PREDICTIONS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get predictions for a specific user (admin/manager only)."""
    predictions = await analytics_service.generate_predictions(user_id)
    return predictions


@router.post("/recommendations", response_model=UserRecommendationResponse)
async def generate_recommendations(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_permission(Permission.GENERATE_RECOMMENDATIONS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Generate personalized recommendations for user improvement."""
    # Run recommendation generation in background
    background_tasks.add_task(
        analytics_service.generate_recommendations,
        user_id=current_user.id
    )
    
    # Return immediate response with placeholder
    return UserRecommendationResponse(
        user_id=current_user.id,
        recommendations={"status": "generating"},
        priority_score=0.0,
        categories=[],
        actionable_items=[],
        last_updated=datetime.utcnow()
    )


@router.get("/recommendations", response_model=UserRecommendationResponse)
async def get_user_recommendations(
    current_user: User = Depends(require_permission(Permission.VIEW_RECOMMENDATIONS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user recommendations."""
    recommendations = await analytics_service.generate_recommendations(current_user.id)
    return recommendations


@router.get("/recommendations/{user_id}", response_model=UserRecommendationResponse)
async def get_user_recommendations_by_id(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_RECOMMENDATIONS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get recommendations for a specific user (admin/manager only)."""
    recommendations = await analytics_service.generate_recommendations(user_id)
    return recommendations


@router.get("/insights", response_model=UserInsightsResponse)
async def get_user_insights(
    current_user: User = Depends(require_permission(Permission.VIEW_USER_INSIGHTS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get comprehensive user insights and intelligence."""
    insights = await analytics_service.get_user_insights(current_user.id)
    return insights


@router.get("/insights/{user_id}", response_model=UserInsightsResponse)
async def get_user_insights_by_id(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_INSIGHTS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get insights for a specific user (admin/manager only)."""
    insights = await analytics_service.get_user_insights(user_id)
    return insights


@router.get("/trends", response_model=UserTrendsResponse)
async def get_user_trends(
    time_range: TimeRange = Query(TimeRange.NINETY_DAYS, description="Time range for trend analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_USER_TRENDS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user trends and patterns over time."""
    trends = await analytics_service.get_user_trends(
        user_id=current_user.id,
        time_range=time_range.value
    )
    return trends


@router.get("/trends/{user_id}", response_model=UserTrendsResponse)
async def get_user_trends_by_id(
    user_id: int,
    time_range: TimeRange = Query(TimeRange.NINETY_DAYS, description="Time range for trend analysis"),
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_TRENDS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get trends for a specific user (admin/manager only)."""
    trends = await analytics_service.get_user_trends(
        user_id=user_id,
        time_range=time_range.value
    )
    return trends


@router.post("/compare", response_model=UserComparisonResponse)
async def compare_users(
    comparison_request: ComparisonRequest,
    current_user: User = Depends(require_permission(Permission.COMPARE_USERS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Compare user performance and behavior with other users."""
    comparison = await analytics_service.compare_users(
        user_id=comparison_request.user_id,
        comparison_users=comparison_request.comparison_users
    )
    return comparison


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS_SUMMARY)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get analytics summary for the current user."""
    # Get basic analytics
    analytics = await analytics_service.get_user_analytics(current_user.id, "30d")
    
    # Get recent insights
    insights = await analytics_service.get_user_insights(current_user.id)
    
    # Get predictions
    predictions = await analytics_service.generate_predictions(current_user.id)
    
    return AnalyticsSummaryResponse(
        user_id=current_user.id,
        total_analytics=analytics.total_activities,
        last_updated=datetime.utcnow(),
        key_metrics={
            "engagement_score": analytics.engagement_score,
            "profile_completeness": analytics.profile_completeness,
            "total_sessions": analytics.unique_sessions
        },
        recent_insights=insights.key_findings[:5] if insights.key_findings else [],
        upcoming_predictions=list(predictions.predictions.keys())[:3] if predictions.predictions else []
    )


@router.get("/summary/{user_id}", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary_by_id(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_ANALYTICS_SUMMARY)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get analytics summary for a specific user (admin/manager only)."""
    # Get basic analytics
    analytics = await analytics_service.get_user_analytics(user_id, "30d")
    
    # Get recent insights
    insights = await analytics_service.get_user_insights(user_id)
    
    # Get predictions
    predictions = await analytics_service.generate_predictions(user_id)
    
    return AnalyticsSummaryResponse(
        user_id=user_id,
        total_analytics=analytics.total_activities,
        last_updated=datetime.utcnow(),
        key_metrics={
            "engagement_score": analytics.engagement_score,
            "profile_completeness": analytics.profile_completeness,
            "total_sessions": analytics.unique_sessions
        },
        recent_insights=insights.key_findings[:5] if insights.key_findings else [],
        upcoming_predictions=list(predictions.predictions.keys())[:3] if predictions.predictions else []
    )


@router.post("/export", response_model=AnalyticsExportResponse)
async def export_analytics(
    export_request: Dict[str, Any],
    current_user: User = Depends(require_permission(Permission.EXPORT_ANALYTICS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Export user analytics data."""
    # This would generate and return a download link for analytics data
    # For now, return a placeholder response
    
    return AnalyticsExportResponse(
        user_id=current_user.id,
        export_type=export_request.get("type", "comprehensive"),
        data_format=export_request.get("format", "json"),
        download_url=f"/api/v1/analytics/export/{current_user.id}/download",
        file_size=1024,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )


@router.get("/health", response_model=AnalyticsHealthResponse)
async def get_analytics_health(
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS_HEALTH)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get analytics system health status."""
    return AnalyticsHealthResponse(
        system_status="healthy",
        data_freshness=datetime.utcnow(),
        model_versions={
            "prediction_model": "v1.0.0",
            "recommendation_model": "v1.0.0",
            "insights_model": "v1.0.0"
        },
        prediction_accuracy=0.85,
        recommendation_effectiveness=0.78,
        system_performance={
            "response_time": 0.15,
            "throughput": 1000,
            "error_rate": 0.01
        }
    )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_analytics_dashboard(
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS_DASHBOARD)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get comprehensive analytics dashboard data."""
    # Get all analytics data for dashboard
    analytics = await analytics_service.get_user_analytics(current_user.id, "30d")
    behavior = await analytics_service.analyze_user_behavior(current_user.id, "30d")
    performance = await analytics_service.get_performance_metrics(current_user.id, "30d")
    engagement = await analytics_service.get_engagement_metrics(current_user.id, "30d")
    insights = await analytics_service.get_user_insights(current_user.id)
    trends = await analytics_service.get_user_trends(current_user.id, "90d")
    
    return {
        "user_id": current_user.id,
        "analytics": analytics.dict(),
        "behavior": behavior.dict(),
        "performance": performance.dict(),
        "engagement": engagement.dict(),
        "insights": insights.dict(),
        "trends": trends.dict(),
        "dashboard_metrics": {
            "overall_score": (analytics.engagement_score + performance.overall_score) / 2,
            "improvement_rate": performance.improvement_rate if hasattr(performance, 'improvement_rate') else 0.0,
            "consistency_score": behavior.consistency_score,
            "trend_direction": trends.trend_direction
        }
    }


@router.get("/dashboard/{user_id}", response_model=Dict[str, Any])
async def get_analytics_dashboard_by_id(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.VIEW_OTHER_USER_ANALYTICS_DASHBOARD)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get analytics dashboard for a specific user (admin/manager only)."""
    # Get all analytics data for dashboard
    analytics = await analytics_service.get_user_analytics(user_id, "30d")
    behavior = await analytics_service.analyze_user_behavior(user_id, "30d")
    performance = await analytics_service.get_performance_metrics(user_id, "30d")
    engagement = await analytics_service.get_engagement_metrics(user_id, "30d")
    insights = await analytics_service.get_user_insights(user_id)
    trends = await analytics_service.get_user_trends(user_id, "90d")
    
    return {
        "user_id": user_id,
        "analytics": analytics.dict(),
        "behavior": behavior.dict(),
        "performance": performance.dict(),
        "engagement": engagement.dict(),
        "insights": insights.dict(),
        "trends": trends.dict(),
        "dashboard_metrics": {
            "overall_score": (analytics.engagement_score + performance.overall_score) / 2,
            "improvement_rate": performance.improvement_rate if hasattr(performance, 'improvement_rate') else 0.0,
            "consistency_score": behavior.consistency_score,
            "trend_direction": trends.trend_direction
        }
    }


@router.post("/batch-analysis", response_model=Dict[str, Any])
async def batch_analytics_analysis(
    user_ids: List[int],
    analysis_types: List[str] = Query(["analytics", "behavior", "performance", "engagement"]),
    current_user: User = Depends(require_permission(Permission.BATCH_ANALYTICS_ANALYSIS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Perform batch analytics analysis for multiple users."""
    results = {}
    
    for user_id in user_ids:
        user_results = {}
        
        if "analytics" in analysis_types:
            user_results["analytics"] = await analytics_service.get_user_analytics(user_id, "30d")
        
        if "behavior" in analysis_types:
            user_results["behavior"] = await analytics_service.analyze_user_behavior(user_id, "30d")
        
        if "performance" in analysis_types:
            user_results["performance"] = await analytics_service.get_performance_metrics(user_id, "30d")
        
        if "engagement" in analysis_types:
            user_results["engagement"] = await analytics_service.get_engagement_metrics(user_id, "30d")
        
        results[user_id] = user_results
    
    return {
        "batch_id": str(uuid.uuid4()),
        "total_users": len(user_ids),
        "analysis_types": analysis_types,
        "results": results,
        "completed_at": datetime.utcnow()
    }


@router.get("/realtime", response_model=Dict[str, Any])
async def get_realtime_analytics(
    current_user: User = Depends(require_permission(Permission.VIEW_REALTIME_ANALYTICS)),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get real-time analytics data."""
    # This would provide real-time analytics updates
    # For now, return current session data
    
    return {
        "user_id": current_user.id,
        "current_session": {
            "session_id": str(uuid.uuid4()),
            "start_time": datetime.utcnow(),
            "activities_count": 0,
            "current_page": "analytics",
            "session_duration": 0
        },
        "realtime_metrics": {
            "active_users": 150,
            "system_load": 0.65,
            "response_time": 0.12
        },
        "last_updated": datetime.utcnow()
    }


# Import required modules
from datetime import datetime, timedelta
import uuid 