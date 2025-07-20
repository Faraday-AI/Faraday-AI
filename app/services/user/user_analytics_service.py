"""
User Analytics Service

This module provides comprehensive user analytics functionality
including activity tracking, usage analytics, and performance metrics.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from fastapi import HTTPException

from app.models.core.user import User
from app.models.user_management.user.user_management import UserSession, UserProfile
from app.models.organization.base.organization_management import OrganizationMember
from app.models.organization.team import TeamMember
from app.schemas.user_analytics import (
    UserActivityMetrics,
    UserUsageAnalytics,
    UserPerformanceMetrics,
    UserEngagementData,
    UserGrowthMetrics
)


class UserAnalyticsService:
    """Service for user analytics and metrics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_activity_metrics(self, user_id: int, days: int = 30) -> UserActivityMetrics:
        """Get user activity metrics for the specified period."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get login sessions
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.created_at >= start_date,
                UserSession.created_at <= end_date
            )
        ).all()
        
        # Calculate metrics
        total_sessions = len(sessions)
        total_duration = sum(
            (session.last_activity - session.created_at).total_seconds() 
            for session in sessions 
            if session.last_activity and session.created_at
        )
        avg_session_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # Get daily activity
        daily_activity = {}
        for session in sessions:
            date = session.created_at.date()
            daily_activity[date] = daily_activity.get(date, 0) + 1
        
        return UserActivityMetrics(
            user_id=user_id,
            period_days=days,
            total_sessions=total_sessions,
            total_duration_hours=total_duration / 3600,
            avg_session_duration_minutes=avg_session_duration / 60,
            daily_activity=daily_activity,
            last_activity=user.last_login
        )
    
    def get_user_usage_analytics(self, user_id: int, days: int = 30) -> UserUsageAnalytics:
        """Get user usage analytics for the specified period."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get organization memberships
        org_memberships = self.db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id
        ).all()
        
        # Get team memberships
        team_memberships = self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id
        ).all()
        
        # Calculate usage metrics
        total_organizations = len(org_memberships)
        total_teams = len(team_memberships)
        
        # Get role distribution
        org_roles = {}
        team_roles = {}
        
        for membership in org_memberships:
            role = membership.role.name if membership.role else "member"
            org_roles[role] = org_roles.get(role, 0) + 1
        
        for membership in team_memberships:
            role = membership.role
            team_roles[role] = team_roles.get(role, 0) + 1
        
        return UserUsageAnalytics(
            user_id=user_id,
            period_days=days,
            total_organizations=total_organizations,
            total_teams=total_teams,
            organization_roles=org_roles,
            team_roles=team_roles,
            subscription_status=user.subscription_status,
            user_type=user.user_type,
            billing_tier=user.billing_tier
        )
    
    def get_user_performance_metrics(self, user_id: int, days: int = 30) -> UserPerformanceMetrics:
        """Get user performance metrics for the specified period."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user profile
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        # Calculate performance metrics
        # This would typically include metrics from various activities
        # For now, we'll use placeholder data
        completion_rate = 0.85  # Placeholder
        accuracy_score = 0.92   # Placeholder
        efficiency_score = 0.78 # Placeholder
        
        return UserPerformanceMetrics(
            user_id=user_id,
            period_days=days,
            completion_rate=completion_rate,
            accuracy_score=accuracy_score,
            efficiency_score=efficiency_score,
            overall_score=(completion_rate + accuracy_score + efficiency_score) / 3,
            profile_completeness=self._calculate_profile_completeness(profile),
            last_updated=user.updated_at
        )
    
    def get_user_engagement_data(self, user_id: int, days: int = 30) -> UserEngagementData:
        """Get user engagement data for the specified period."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get sessions for engagement calculation
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.created_at >= start_date,
                UserSession.created_at <= end_date
            )
        ).all()
        
        # Calculate engagement metrics
        total_days_active = len(set(session.created_at.date() for session in sessions))
        engagement_rate = total_days_active / days if days > 0 else 0
        
        # Calculate session frequency
        session_frequency = len(sessions) / days if days > 0 else 0
        
        # Get recent activity
        recent_activity = []
        for session in sessions[-10:]:  # Last 10 sessions
            recent_activity.append({
                "session_id": session.id,
                "started_at": session.created_at,
                "ended_at": session.last_activity,
                "duration_minutes": (session.last_activity - session.created_at).total_seconds() / 60 if session.last_activity else 0
            })
        
        return UserEngagementData(
            user_id=user_id,
            period_days=days,
            total_days_active=total_days_active,
            engagement_rate=engagement_rate,
            session_frequency=session_frequency,
            recent_activity=recent_activity,
            is_active=user.is_active
        )
    
    def get_user_growth_metrics(self, user_id: int, days: int = 30) -> UserGrowthMetrics:
        """Get user growth metrics for the specified period."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user creation date
        created_date = user.created_at
        
        # Calculate growth metrics
        days_since_creation = (end_date - created_date).days
        account_age_days = days_since_creation
        
        # Get progression data (placeholder)
        skill_progression = 0.75  # Placeholder
        feature_adoption = 0.60   # Placeholder
        community_participation = 0.45  # Placeholder
        
        return UserGrowthMetrics(
            user_id=user_id,
            period_days=days,
            account_age_days=account_age_days,
            skill_progression=skill_progression,
            feature_adoption=feature_adoption,
            community_participation=community_participation,
            overall_growth=(skill_progression + feature_adoption + community_participation) / 3,
            created_at=created_date
        )
    
    def get_comprehensive_user_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive user analytics combining all metrics."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all analytics
        activity_metrics = self.get_user_activity_metrics(user_id, days)
        usage_analytics = self.get_user_usage_analytics(user_id, days)
        performance_metrics = self.get_user_performance_metrics(user_id, days)
        engagement_data = self.get_user_engagement_data(user_id, days)
        growth_metrics = self.get_user_growth_metrics(user_id, days)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "user_info": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "subscription_status": user.subscription_status,
                "user_type": user.user_type,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "activity_metrics": activity_metrics.dict(),
            "usage_analytics": usage_analytics.dict(),
            "performance_metrics": performance_metrics.dict(),
            "engagement_data": engagement_data.dict(),
            "growth_metrics": growth_metrics.dict(),
            "summary": {
                "overall_score": (performance_metrics.overall_score + engagement_data.engagement_rate + growth_metrics.overall_growth) / 3,
                "activity_level": "high" if activity_metrics.total_sessions > 20 else "medium" if activity_metrics.total_sessions > 10 else "low",
                "engagement_level": "high" if engagement_data.engagement_rate > 0.7 else "medium" if engagement_data.engagement_rate > 0.4 else "low",
                "growth_potential": "high" if growth_metrics.overall_growth > 0.7 else "medium" if growth_metrics.overall_growth > 0.4 else "low"
            }
        }
    
    def get_user_comparison_analytics(self, user_ids: List[int], days: int = 30) -> Dict[str, Any]:
        """Compare analytics between multiple users."""
        if not user_ids:
            raise HTTPException(status_code=400, detail="No user IDs provided")
        
        comparison_data = {}
        
        for user_id in user_ids:
            try:
                user_analytics = self.get_comprehensive_user_analytics(user_id, days)
                comparison_data[user_id] = user_analytics
            except Exception as e:
                comparison_data[user_id] = {"error": str(e)}
        
        # Calculate comparative metrics
        if len(comparison_data) > 1:
            scores = []
            engagement_rates = []
            activity_sessions = []
            
            for user_data in comparison_data.values():
                if "error" not in user_data:
                    scores.append(user_data["summary"]["overall_score"])
                    engagement_rates.append(user_data["engagement_data"]["engagement_rate"])
                    activity_sessions.append(user_data["activity_metrics"]["total_sessions"])
            
            if scores:
                comparison_data["comparative_metrics"] = {
                    "average_overall_score": sum(scores) / len(scores),
                    "highest_score": max(scores),
                    "lowest_score": min(scores),
                    "average_engagement_rate": sum(engagement_rates) / len(engagement_rates),
                    "average_activity_sessions": sum(activity_sessions) / len(activity_sessions)
                }
        
        return comparison_data
    
    def _calculate_profile_completeness(self, profile: Optional[UserProfile]) -> float:
        """Calculate profile completeness percentage."""
        if not profile:
            return 0.0
        
        fields = [
            profile.bio,
            profile.timezone,
            profile.language,
            profile.notification_preferences,
            profile.custom_settings
        ]
        
        completed_fields = sum(1 for field in fields if field is not None)
        return completed_fields / len(fields) if fields else 0.0


def get_user_analytics_service(db: Session) -> UserAnalyticsService:
    """Dependency to get user analytics service."""
    return UserAnalyticsService(db) 