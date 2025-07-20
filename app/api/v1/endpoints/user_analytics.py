"""
User Analytics API Endpoints

This module provides API endpoints for user analytics.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.services.user.user_analytics_service import UserAnalyticsService, get_user_analytics_service
from app.schemas.user_analytics import (
    UserActivityMetrics,
    UserUsageAnalytics,
    UserPerformanceMetrics,
    UserEngagementData,
    UserGrowthMetrics,
    UserAnalyticsFilter,
    UserAnalyticsComparison
)

router = APIRouter()


@router.get("/users/{user_id}/analytics/activity", response_model=UserActivityMetrics)
async def get_user_activity_metrics(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user activity metrics."""
    # Users can view their own analytics, admins can view any user's analytics
    if user_id != current_user.id and not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_user_activity_metrics(user_id, days)


@router.get("/users/{user_id}/analytics/usage", response_model=UserUsageAnalytics)
async def get_user_usage_analytics(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user usage analytics."""
    # Users can view their own analytics, admins can view any user's analytics
    if user_id != current_user.id and not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_user_usage_analytics(user_id, days)


@router.get("/users/{user_id}/analytics/performance", response_model=UserPerformanceMetrics)
async def get_user_performance_metrics(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user performance metrics."""
    # Users can view their own analytics, admins can view any user's analytics
    if user_id != current_user.id and not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_user_performance_metrics(user_id, days)


@router.get("/users/{user_id}/analytics/engagement", response_model=UserEngagementData)
async def get_user_engagement_data(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user engagement data."""
    # Users can view their own analytics, admins can view any user's analytics
    if user_id != current_user.id and not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_user_engagement_data(user_id, days)


@router.get("/users/{user_id}/analytics/growth", response_model=UserGrowthMetrics)
async def get_user_growth_metrics(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user growth metrics."""
    # Users can view their own analytics, admins can view any user's analytics
    if user_id != current_user.id and not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_user_growth_metrics(user_id, days)


@router.get("/users/{user_id}/analytics/comprehensive")
async def get_comprehensive_user_analytics(
    user_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get comprehensive user analytics combining all metrics."""
    # Users can view their own analytics, admins can view any user's analytics
    if user_id != current_user.id and not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_comprehensive_user_analytics(user_id, days)


@router.post("/users/analytics/comparison")
async def compare_user_analytics(
    user_ids: List[int],
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Compare analytics between multiple users."""
    # Check if user has permission to view user analytics
    if not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return analytics_service.get_user_comparison_analytics(user_ids, days)


@router.post("/users/analytics/filter")
async def filter_user_analytics(
    filter_data: UserAnalyticsFilter,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Filter user analytics based on criteria."""
    # Check if user has permission to view user analytics
    if not analytics_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # This would implement filtering logic based on the filter criteria
    # For now, return a placeholder response
    return {
        "message": "Filter functionality to be implemented",
        "filter_criteria": filter_data.dict(),
        "results": []
    }


@router.get("/users/analytics/dashboard")
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get analytics dashboard data for current user."""
    # Get comprehensive analytics for current user
    user_analytics = analytics_service.get_comprehensive_user_analytics(current_user.id, 30)
    
    # Add dashboard-specific data
    dashboard_data = {
        "user_analytics": user_analytics,
        "quick_stats": {
            "total_sessions": user_analytics["activity_metrics"]["total_sessions"],
            "engagement_rate": user_analytics["engagement_data"]["engagement_rate"],
            "overall_score": user_analytics["summary"]["overall_score"],
            "growth_score": user_analytics["growth_metrics"]["overall_growth"]
        },
        "recent_activity": user_analytics["engagement_data"]["recent_activity"][:5],
        "recommendations": [
            "Complete your profile to improve your analytics score",
            "Join more teams to increase engagement",
            "Try new features to boost your growth metrics"
        ]
    }
    
    return dashboard_data


@router.get("/users/analytics/trends")
async def get_user_analytics_trends(
    days: int = 90,
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get user analytics trends over time."""
    # Get analytics for different time periods to show trends
    periods = [7, 30, 90]
    trends_data = {}
    
    for period in periods:
        if period <= days:
            try:
                analytics = analytics_service.get_comprehensive_user_analytics(current_user.id, period)
                trends_data[f"{period}_days"] = {
                    "overall_score": analytics["summary"]["overall_score"],
                    "engagement_rate": analytics["engagement_data"]["engagement_rate"],
                    "total_sessions": analytics["activity_metrics"]["total_sessions"],
                    "growth_score": analytics["growth_metrics"]["overall_growth"]
                }
            except Exception as e:
                trends_data[f"{period}_days"] = {"error": str(e)}
    
    return {
        "user_id": current_user.id,
        "trends_data": trends_data,
        "analysis_period": days
    }


@router.get("/users/analytics/insights")
async def get_user_analytics_insights(
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Get insights and recommendations based on user analytics."""
    # Get comprehensive analytics
    analytics = analytics_service.get_comprehensive_user_analytics(current_user.id, 30)
    
    # Generate insights based on analytics data
    insights = []
    
    # Activity insights
    if analytics["activity_metrics"]["total_sessions"] < 10:
        insights.append("Low activity detected. Consider logging in more frequently.")
    elif analytics["activity_metrics"]["total_sessions"] > 50:
        insights.append("High activity level! You're very engaged with the platform.")
    
    # Engagement insights
    if analytics["engagement_data"]["engagement_rate"] < 0.3:
        insights.append("Low engagement rate. Try exploring new features.")
    elif analytics["engagement_data"]["engagement_rate"] > 0.8:
        insights.append("Excellent engagement! You're making the most of the platform.")
    
    # Performance insights
    if analytics["performance_metrics"]["overall_score"] < 0.6:
        insights.append("Performance could be improved. Complete more tasks to boost your score.")
    elif analytics["performance_metrics"]["overall_score"] > 0.9:
        insights.append("Outstanding performance! You're excelling in all areas.")
    
    # Growth insights
    if analytics["growth_metrics"]["overall_growth"] < 0.5:
        insights.append("Growth opportunities available. Try new features and join more teams.")
    elif analytics["growth_metrics"]["overall_growth"] > 0.8:
        insights.append("Strong growth trajectory! Keep up the great work.")
    
    return {
        "user_id": current_user.id,
        "insights": insights,
        "key_metrics": {
            "activity_level": analytics["summary"]["activity_level"],
            "engagement_level": analytics["summary"]["engagement_level"],
            "growth_potential": analytics["summary"]["growth_potential"]
        },
        "recommendations": [
            "Complete your profile to improve analytics accuracy",
            "Join more teams to increase engagement",
            "Explore new features to boost growth metrics",
            "Maintain consistent activity for better performance"
        ]
    }


@router.get("/users/analytics/export")
async def export_user_analytics(
    export_type: str = "comprehensive",
    days: int = 30,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    analytics_service: UserAnalyticsService = Depends(get_user_analytics_service)
):
    """Export user analytics data."""
    # Validate export type
    valid_types = ["activity", "usage", "performance", "engagement", "growth", "comprehensive"]
    if export_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid export type. Must be one of: {valid_types}")
    
    # Validate format
    valid_formats = ["json", "csv", "excel"]
    if format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {valid_formats}")
    
    # Get analytics data
    if export_type == "comprehensive":
        data = analytics_service.get_comprehensive_user_analytics(current_user.id, days)
    elif export_type == "activity":
        data = analytics_service.get_user_activity_metrics(current_user.id, days).dict()
    elif export_type == "usage":
        data = analytics_service.get_user_usage_analytics(current_user.id, days).dict()
    elif export_type == "performance":
        data = analytics_service.get_user_performance_metrics(current_user.id, days).dict()
    elif export_type == "engagement":
        data = analytics_service.get_user_engagement_data(current_user.id, days).dict()
    elif export_type == "growth":
        data = analytics_service.get_user_growth_metrics(current_user.id, days).dict()
    
    return {
        "user_id": current_user.id,
        "export_type": export_type,
        "period_days": days,
        "format": format,
        "data": data,
        "exported_at": datetime.utcnow().isoformat()
    } 