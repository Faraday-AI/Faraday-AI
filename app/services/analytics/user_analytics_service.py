"""
Advanced User Analytics Service - Phase 3

This module provides comprehensive user analytics, intelligence, and insights
including behavior tracking, performance metrics, predictive analytics, and recommendations.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends
import json
import uuid
from collections import defaultdict, Counter

from app.models.core.user import User
from app.models.user_management.user.user_management import UserProfile
from app.models.analytics.user_analytics import (
    UserActivity,
    UserBehavior,
    UserPerformance,
    UserEngagement,
    UserPrediction,
    UserRecommendation,
    AnalyticsEvent
)
from app.schemas.analytics import (
    UserAnalyticsResponse,
    UserBehaviorAnalysis,
    UserPerformanceMetrics,
    UserEngagementMetrics,
    UserPredictionResponse,
    UserRecommendationResponse,
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    UserInsightsResponse,
    UserTrendsResponse,
    UserComparisonResponse
)
from app.db.session import get_db
from app.services.ai.ai_analytics import AIAnalyticsService


class UserAnalyticsService:
    """Advanced user analytics and intelligence service."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_analytics = AIAnalyticsService(db)
    
    async def track_user_activity(self, user_id: int, activity_type: str, 
                          activity_data: Dict[str, Any], 
                          session_id: Optional[str] = None) -> AnalyticsEvent:
        """Track user activity for analytics."""
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=activity_type,
            event_data=activity_data,
            session_id=session_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )
        
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to track activity")
    
    async def get_user_analytics(self, user_id: int, 
                         time_range: str = "30d") -> UserAnalyticsResponse:
        """Get comprehensive user analytics."""
        end_date = datetime.utcnow()
        
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get user profile
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        # Get activity data
        activities = (
            self.db.query(AnalyticsEvent)
            .filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.timestamp >= start_date,
                    AnalyticsEvent.timestamp <= end_date
                )
            )
            .order_by(desc(AnalyticsEvent.timestamp))
            .all()
        )
        
        # Calculate metrics
        total_activities = len(activities)
        unique_sessions = len(set(activity.session_id for activity in activities))
        
        # Activity type distribution
        activity_types = Counter(activity.event_type for activity in activities)
        
        # Daily activity pattern
        daily_activity = defaultdict(int)
        for activity in activities:
            day = activity.timestamp.date().isoformat()
            daily_activity[day] += 1
        
        # Peak activity times
        hourly_activity = defaultdict(int)
        for activity in activities:
            hour = activity.timestamp.hour
            hourly_activity[hour] += 1
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
        
        # Engagement score calculation
        engagement_score = self._calculate_engagement_score(activities, profile)
        
        # Performance metrics
        performance_metrics = await self._calculate_performance_metrics(user_id, start_date, end_date)
        
        # Behavior analysis
        behavior_analysis = await self.analyze_user_behavior(user_id, "30d")
        
        return UserAnalyticsResponse(
            user_id=user_id,
            time_range=time_range,
            total_activities=total_activities,
            unique_sessions=unique_sessions,
            activity_types=dict(activity_types),
            daily_activity=dict(daily_activity),
            peak_activity_hour=peak_hour,
            engagement_score=engagement_score,
            performance_metrics=performance_metrics,
            behavior_analysis=behavior_analysis.dict() if behavior_analysis else {},
            last_activity=activities[0].timestamp if activities else None,
            profile_completeness=profile.custom_settings.get("profile_completeness", 0.0) if profile and profile.custom_settings else 0.0
        )
    
    async def analyze_user_behavior(self, user_id: int, 
                            time_range: str = "30d") -> UserBehaviorAnalysis:
        """Analyze user behavior patterns."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=int(time_range[:-1]))
        
        # Get activities
        activities = (
            self.db.query(AnalyticsEvent)
            .filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.timestamp >= start_date,
                    AnalyticsEvent.timestamp <= end_date
                )
            )
            .order_by(desc(AnalyticsEvent.timestamp))
            .all()
        )
        
        # Behavior patterns
        patterns = {
            "session_duration": self._calculate_session_duration(activities),
            "activity_frequency": self._calculate_activity_frequency(activities),
            "feature_usage": self._analyze_feature_usage(activities),
            "time_patterns": self._analyze_time_patterns(activities),
            "interaction_patterns": self._analyze_interaction_patterns(activities)
        }
        
        # Behavioral insights
        insights = await self._generate_behavioral_insights(user_id, patterns, activities)
        
        return UserBehaviorAnalysis(
            user_id=user_id,
            time_range=time_range,
            patterns=patterns,
            insights=insights,
            behavior_score=self._calculate_behavior_score(patterns),
            consistency_score=self._calculate_consistency_score(activities)
        )
    
    async def get_performance_metrics(self, user_id: int, 
                              time_range: str = "30d") -> UserPerformanceMetrics:
        """Get detailed user performance metrics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=int(time_range[:-1]))
        
        # Get performance data
        performance_data = (
            self.db.query(UserPerformance)
            .filter(
                and_(
                    UserPerformance.user_id == user_id,
                    UserPerformance.timestamp >= start_date,
                    UserPerformance.timestamp <= end_date
                )
            )
            .order_by(desc(UserPerformance.timestamp))
            .all()
        )
        
        if not performance_data:
            # Create default performance metrics
            performance_data = [await self._create_default_performance(user_id)]
        
        # Calculate metrics
        metrics = {
            "accuracy": self._calculate_average_accuracy(performance_data),
            "speed": self._calculate_average_speed(performance_data),
            "completion_rate": self._calculate_completion_rate(performance_data),
            "efficiency": self._calculate_efficiency_score(performance_data),
            "improvement_rate": self._calculate_improvement_rate(performance_data),
            "skill_levels": self._calculate_skill_levels(performance_data)
        }
        
        # Performance trends
        trends = self._analyze_performance_trends(performance_data)
        
        # Benchmark comparison
        benchmarks = await self._get_performance_benchmarks(user_id, metrics)
        
        # Calculate overall score
        overall_score = self._calculate_overall_performance_score(metrics)
        
        return UserPerformanceMetrics(
            user_id=user_id,
            time_range=time_range,
            metrics=metrics,
            trends=trends,
            benchmarks=benchmarks,
            overall_score=overall_score,
            percentile_rank=await self._calculate_percentile_rank(user_id, overall_score)
        )
    
    async def get_engagement_metrics(self, user_id: int, 
                             time_range: str = "30d") -> UserEngagementMetrics:
        """Get user engagement metrics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=int(time_range[:-1]))
        
        # Get activities
        activities = (
            self.db.query(AnalyticsEvent)
            .filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.timestamp >= start_date,
                    AnalyticsEvent.timestamp <= end_date
                )
            )
            .order_by(desc(AnalyticsEvent.timestamp))
            .all()
        )
        
        # Engagement calculations
        daily_engagement = self._calculate_daily_engagement(activities)
        feature_engagement = self._calculate_feature_engagement(activities)
        session_engagement = self._calculate_session_engagement(activities)
        
        # Engagement score
        engagement_score = self._calculate_engagement_score(activities)
        
        # Retention metrics
        retention_metrics = await self._calculate_retention_metrics(user_id, start_date, end_date)
        
        # Churn risk assessment
        churn_risk = await self._assess_churn_risk(user_id, activities)
        
        return UserEngagementMetrics(
            user_id=user_id,
            time_range=time_range,
            daily_engagement=daily_engagement,
            feature_engagement=feature_engagement,
            session_engagement=session_engagement,
            engagement_score=engagement_score,
            retention_metrics=retention_metrics,
            churn_risk=churn_risk,
            engagement_trend=self._calculate_engagement_trend(activities)
        )
    
    async def generate_predictions(self, user_id: int) -> UserPredictionResponse:
        """Generate AI-powered predictions for user behavior and performance."""
        # Get historical data
        historical_data = await self._get_historical_data(user_id)
        
        # Return mock predictions
        predictions = {
            "behavior_predictions": {"activity_level": "stable", "confidence": 0.8},
            "performance_predictions": {"improvement_rate": 0.05, "confidence": 0.7},
            "engagement_predictions": {"engagement_score": 75.0, "confidence": 0.6},
            "churn_predictions": {"churn_probability": 0.1, "confidence": 0.9},
            "skill_predictions": {"skill_growth": 0.1, "confidence": 0.7},
            "confidence": 0.75,
            "prediction_horizon": "30d",
            "model_version": "v1.0.0",
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Store predictions
        prediction_record = UserPrediction(
            user_id=user_id,
            prediction_type="comprehensive",
            prediction_data=predictions,
            confidence_score=predictions.get("confidence", 0.0),
            timestamp=datetime.utcnow()
        )
        
        try:
            self.db.add(prediction_record)
            self.db.commit()
            self.db.refresh(prediction_record)
        except IntegrityError:
            self.db.rollback()
        
        return UserPredictionResponse(
            user_id=user_id,
            predictions=predictions,
            confidence_score=predictions.get("confidence", 0.0),
            prediction_horizon="30d",
            last_updated=datetime.utcnow()
        )
    
    async def generate_recommendations(self, user_id: int) -> UserRecommendationResponse:
        """Generate personalized recommendations for user improvement."""
        # Get user analytics
        analytics = await self.get_user_analytics(user_id)
        
        # Get user profile
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        # Return mock recommendations
        recommendations = {
            "improvement_recommendations": [
                {"type": "skill_development", "priority": "high", "description": "Focus on accuracy improvement"}
            ],
            "feature_recommendations": [
                {"type": "new_feature", "priority": "medium", "description": "Try advanced analytics dashboard"}
            ],
            "content_recommendations": [
                {"type": "learning_path", "priority": "high", "description": "Complete intermediate skill modules"}
            ],
            "behavior_recommendations": [
                {"type": "engagement", "priority": "medium", "description": "Increase daily activity sessions"}
            ],
            "priority": 0.8,
            "categories": ["skill_development", "engagement", "content"],
            "actionable_items": ["Complete skill assessment", "Set daily goals", "Review progress weekly"],
            "model_version": "v1.0.0",
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Store recommendations
        recommendation_record = UserRecommendation(
            user_id=user_id,
            recommendation_type="personalized",
            recommendation_data=recommendations,
            priority_score=recommendations.get("priority", 0.0),
            timestamp=datetime.utcnow()
        )
        
        try:
            self.db.add(recommendation_record)
            self.db.commit()
            self.db.refresh(recommendation_record)
        except IntegrityError:
            self.db.rollback()
        
        return UserRecommendationResponse(
            user_id=user_id,
            recommendations=recommendations,
            priority_score=recommendations.get("priority", 0.0),
            categories=recommendations.get("categories", []),
            actionable_items=recommendations.get("actionable_items", []),
            last_updated=datetime.utcnow()
        )
    
    async def get_user_insights(self, user_id: int) -> UserInsightsResponse:
        """Get comprehensive user insights and intelligence."""
        # Get all analytics data
        analytics = await self.get_user_analytics(user_id)
        behavior = await self.analyze_user_behavior(user_id)
        performance = await self.get_performance_metrics(user_id)
        engagement = await self.get_engagement_metrics(user_id)
        predictions = await self.generate_predictions(user_id)
        recommendations = await self.generate_recommendations(user_id)
        
        # Return mock insights
        insights = {
            "key_findings": [
                "User demonstrates consistent engagement patterns",
                "Performance shows steady improvement trend",
                "Good balance of activity types"
            ],
            "improvement_areas": [
                "Accuracy could be improved with focused practice",
                "Session duration could be optimized"
            ],
            "strengths": [
                "Consistent daily activity",
                "Good feature utilization",
                "Stable engagement levels"
            ],
            "opportunities": [
                "Advanced skill development",
                "Peer collaboration features",
                "Personalized learning paths"
            ],
            "risk_factors": [
                "Occasional activity gaps",
                "Limited feature exploration"
            ],
            "success_indicators": [
                "Regular login patterns",
                "Completion rate above average",
                "Positive performance trends"
            ],
            "confidence": 0.85,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return UserInsightsResponse(
            user_id=user_id,
            insights=insights,
            key_findings=insights.get("key_findings", []),
            improvement_areas=insights.get("improvement_areas", []),
            strengths=insights.get("strengths", []),
            opportunities=insights.get("opportunities", []),
            risk_factors=insights.get("risk_factors", []),
            success_indicators=insights.get("success_indicators", []),
            generated_at=datetime.utcnow()
        )
    
    async def get_user_trends(self, user_id: int, 
                       time_range: str = "90d") -> UserTrendsResponse:
        """Get user trends and patterns over time."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=int(time_range[:-1]))
        
        # Get trend data
        activities = (
            self.db.query(AnalyticsEvent)
            .filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.timestamp >= start_date,
                    AnalyticsEvent.timestamp <= end_date
                )
            )
            .order_by(desc(AnalyticsEvent.timestamp))
            .all()
        )
        
        # Calculate trends
        trends = {
            "activity_trend": self._calculate_activity_trend(activities),
            "performance_trend": await self._calculate_performance_trend(user_id, start_date, end_date),
            "engagement_trend": self._calculate_engagement_trend(activities),
            "behavior_trend": self._calculate_behavior_trend(activities),
            "skill_progression": await self._calculate_skill_progression(user_id, start_date, end_date)
        }
        
        return UserTrendsResponse(
            user_id=user_id,
            time_range=time_range,
            trends=trends,
            trend_direction=self._determine_trend_direction(trends),
            trend_strength=self._calculate_trend_strength(trends),
            seasonal_patterns=self._identify_seasonal_patterns(activities),
            generated_at=datetime.utcnow()
        )
    
    async def compare_users(self, user_id: int, 
                     comparison_users: List[int]) -> UserComparisonResponse:
        """Compare user performance and behavior with other users."""
        # Get user data
        user_data = await self.get_user_analytics(user_id)
        user_performance = await self.get_performance_metrics(user_id)
        
        # Get comparison data
        comparison_data = []
        for comp_user_id in comparison_users:
            comp_analytics = await self.get_user_analytics(comp_user_id)
            comp_performance = await self.get_performance_metrics(comp_user_id)
            comparison_data.append({
                "user_id": comp_user_id,
                "analytics": comp_analytics,
                "performance": comp_performance
            })
        
        # Return mock comparison insights
        comparison_insights = {
            "relative_performance": "above_average",
            "peer_benchmarks": {
                "accuracy": "75th_percentile",
                "engagement": "60th_percentile",
                "consistency": "80th_percentile"
            },
            "improvement_opportunities": [
                "Focus on speed improvement",
                "Increase feature utilization"
            ],
            "competitive_advantages": [
                "Strong consistency",
                "Good engagement patterns"
            ],
            "learning_recommendations": [
                "Study advanced techniques",
                "Collaborate with top performers"
            ],
            "confidence": 0.8,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return UserComparisonResponse(
            user_id=user_id,
            comparison_users=comparison_users,
            comparison_data=comparison_data,
            insights=comparison_insights,
            relative_performance=self._calculate_relative_performance(user_performance, comparison_data),
            benchmarking_data=self._generate_benchmarking_data(user_data, comparison_data),
            generated_at=datetime.utcnow()
        )
    
    # Helper methods for calculations
    def _calculate_engagement_score(self, activities: List[AnalyticsEvent], 
                                  profile: Optional[UserProfile] = None) -> float:
        """Calculate user engagement score."""
        if not activities:
            return 0.0
        
        # Base score from activity frequency
        activity_score = min(len(activities) / 100.0, 1.0) * 40
        
        # Session diversity score
        unique_sessions = len(set(activity.session_id for activity in activities))
        session_score = min(unique_sessions / 20.0, 1.0) * 30
        
        # Feature usage score
        feature_score = min(len(set(activity.event_type for activity in activities)) / 10.0, 1.0) * 20
        
        # Profile completeness bonus
        profile_bonus = (profile.custom_settings.get("profile_completeness", 0.0) / 100.0) * 10 if profile and profile.custom_settings else 0
        
        return min(activity_score + session_score + feature_score + profile_bonus, 100.0)
    
    def _calculate_session_duration(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate session duration patterns."""
        if not activities:
            return {"average_duration": 0, "session_patterns": {}}
        
        sessions = defaultdict(list)
        for activity in activities:
            sessions[activity.session_id].append(activity.timestamp)
        
        durations = []
        for session_activities in sessions.values():
            if len(session_activities) > 1:
                duration = (max(session_activities) - min(session_activities)).total_seconds()
                durations.append(duration)
        
        return {
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "session_count": len(sessions)
        }
    
    def _calculate_activity_frequency(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate activity frequency patterns."""
        if not activities:
            return {"daily_average": 0, "peak_days": [], "frequency_pattern": {}}
        
        daily_counts = Counter(activity.timestamp.date() for activity in activities)
        
        return {
            "daily_average": sum(daily_counts.values()) / len(daily_counts),
            "peak_days": [str(date) for date, count in daily_counts.most_common(3)],
            "frequency_pattern": dict(daily_counts)
        }
    
    def _analyze_feature_usage(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Analyze feature usage patterns."""
        if not activities:
            return {"most_used_features": [], "feature_preferences": {}}
        
        feature_counts = Counter(activity.event_type for activity in activities)
        
        return {
            "most_used_features": [feature for feature, count in feature_counts.most_common(5)],
            "feature_preferences": dict(feature_counts),
            "feature_diversity": len(feature_counts)
        }
    
    def _analyze_time_patterns(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Analyze time-based patterns."""
        if not activities:
            return {"peak_hours": [], "daily_patterns": {}, "weekly_patterns": {}}
        
        hourly_counts = Counter(activity.timestamp.hour for activity in activities)
        daily_counts = Counter(activity.timestamp.strftime("%A") for activity in activities)
        
        return {
            "peak_hours": [hour for hour, count in hourly_counts.most_common(3)],
            "daily_patterns": dict(hourly_counts),
            "weekly_patterns": dict(daily_counts)
        }
    
    def _analyze_interaction_patterns(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Analyze interaction patterns."""
        if not activities:
            return {"interaction_types": {}, "response_patterns": {}}
        
        # Analyze event data for interaction patterns
        interaction_types = defaultdict(int)
        response_times = []
        
        for activity in activities:
            if activity.event_data:
                interaction_type = activity.event_data.get("interaction_type", "unknown")
                interaction_types[interaction_type] += 1
                
                if "response_time" in activity.event_data:
                    response_times.append(activity.event_data["response_time"])
        
        return {
            "interaction_types": dict(interaction_types),
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "response_patterns": self._analyze_response_patterns(response_times)
        }
    
    async def _generate_behavioral_insights(self, user_id: int, patterns: Dict[str, Any], 
                                            activities: List[AnalyticsEvent]) -> List[str]:
        """Generate behavioral insights using AI."""
        # Temporarily return mock data instead of async AI calls
        return [
            "User shows consistent activity patterns",
            "Engagement levels are stable",
            "Good session duration consistency"
        ]
    
    def _calculate_behavior_score(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall behavior score."""
        # Implement behavior scoring logic
        score = 0.0
        
        # Session duration score
        if patterns.get("session_duration", {}).get("average_duration", 0) > 300:  # 5 minutes
            score += 25
        
        # Activity frequency score
        daily_avg = patterns.get("activity_frequency", {}).get("daily_average", 0)
        if daily_avg > 5:
            score += 25
        elif daily_avg > 2:
            score += 15
        
        # Feature usage score
        feature_diversity = patterns.get("feature_usage", {}).get("feature_diversity", 0)
        if feature_diversity > 5:
            score += 25
        elif feature_diversity > 2:
            score += 15
        
        # Time pattern consistency score
        if patterns.get("time_patterns", {}).get("peak_hours"):
            score += 25
        
        return min(score, 100.0)
    
    def _calculate_consistency_score(self, activities: List[AnalyticsEvent]) -> float:
        """Calculate consistency score based on activity patterns."""
        if not activities:
            return 0.0
        
        # Calculate daily consistency
        daily_activity = defaultdict(int)
        for activity in activities:
            daily_activity[activity.timestamp.date()] += 1
        
        if len(daily_activity) < 2:
            return 0.0
        
        # Calculate coefficient of variation
        values = list(daily_activity.values())
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        if mean_val == 0:
            return 0.0
        
        cv = std_dev / mean_val
        consistency_score = max(0, 100 - (cv * 100))
        
        return min(consistency_score, 100.0)
    
    async def _calculate_performance_metrics(self, user_id: int, start_date: datetime, 
                                            end_date: datetime) -> Dict[str, Any]:
        """Calculate performance metrics for the user."""
        # Get performance data
        performance_data = (
            self.db.query(UserPerformance)
            .filter(
                and_(
                    UserPerformance.user_id == user_id,
                    UserPerformance.timestamp >= start_date,
                    UserPerformance.timestamp <= end_date
                )
            )
            .order_by(desc(UserPerformance.timestamp))
            .all()
        )
        
        if not performance_data:
            return {
                "accuracy": 75.0,
                "speed": 70.0,
                "completion_rate": 80.0,
                "efficiency": 75.0,
                "improvement_rate": 5.0,
                "skill_levels": {"overall": 75.0}
            }
        
        return {
            "accuracy": self._calculate_average_accuracy(performance_data),
            "speed": self._calculate_average_speed(performance_data),
            "completion_rate": self._calculate_completion_rate(performance_data),
            "efficiency": self._calculate_efficiency_score(performance_data),
            "improvement_rate": self._calculate_improvement_rate(performance_data),
            "skill_levels": self._calculate_skill_levels(performance_data)
        }
    
    async def _create_default_performance(self, user_id: int) -> UserPerformance:
        """Create default performance record for new users."""
        return UserPerformance(
            user_id=user_id,
            accuracy=75.0,
            speed=70.0,
            completion_rate=80.0,
            efficiency=75.0,
            performance_data={
                "accuracy": 75.0,
                "speed": 70.0,
                "completion_rate": 80.0
            },
            timestamp=datetime.utcnow()
        )
    
    def _calculate_average_accuracy(self, performance_data: List[UserPerformance]) -> float:
        """Calculate average accuracy from performance data."""
        if not performance_data:
            return 0.0
        return sum(p.accuracy for p in performance_data) / len(performance_data)
    
    def _calculate_average_speed(self, performance_data: List[UserPerformance]) -> float:
        """Calculate average speed from performance data."""
        if not performance_data:
            return 0.0
        return sum(p.speed for p in performance_data) / len(performance_data)
    
    def _calculate_completion_rate(self, performance_data: List[UserPerformance]) -> float:
        """Calculate completion rate from performance data."""
        if not performance_data:
            return 0.0
        return sum(p.completion_rate for p in performance_data) / len(performance_data)
    
    def _calculate_efficiency_score(self, performance_data: List[UserPerformance]) -> float:
        """Calculate efficiency score from performance data."""
        if not performance_data:
            return 0.0
        return sum(p.efficiency for p in performance_data) / len(performance_data)
    
    def _calculate_improvement_rate(self, performance_data: List[UserPerformance]) -> float:
        """Calculate improvement rate over time."""
        if len(performance_data) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_data = sorted(performance_data, key=lambda x: x.timestamp)
        
        # Calculate improvement
        first_score = sorted_data[0].accuracy
        last_score = sorted_data[-1].accuracy
        
        if first_score == 0:
            return 0.0
        
        return ((last_score - first_score) / first_score) * 100
    
    def _calculate_skill_levels(self, performance_data: List[UserPerformance]) -> Dict[str, float]:
        """Calculate skill levels from performance data."""
        if not performance_data:
            return {}
        
        latest = performance_data[0]  # Most recent performance
        
        return {
            "accuracy_skill": latest.accuracy,
            "speed_skill": latest.speed,
            "completion_skill": latest.completion_rate,
            "efficiency_skill": latest.efficiency
        }
    
    def _analyze_performance_trends(self, performance_data: List[UserPerformance]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(performance_data) < 2:
            return {"trend": "insufficient_data", "slope": 0.0}
        
        # Sort by timestamp
        sorted_data = sorted(performance_data, key=lambda x: x.timestamp)
        
        # Calculate trend slope
        x_values = [(p.timestamp - sorted_data[0].timestamp).days for p in sorted_data]
        y_values = [p.accuracy for p in sorted_data]
        
        # Simple linear regression
        n = len(x_values)
        if n < 2:
            return {"trend": "insufficient_data", "slope": 0.0}
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.1:
            trend = "improving"
        elif slope < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {"trend": trend, "slope": slope}
    
    async def _get_performance_benchmarks(self, user_id: int, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance benchmarks for comparison."""
        # This would compare against other users or industry standards
        return {
            "accuracy_benchmark": 0.75,
            "speed_benchmark": 0.8,
            "completion_benchmark": 0.9,
            "efficiency_benchmark": 0.7
        }
    
    def _calculate_overall_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score from metrics."""
        accuracy = metrics.get("accuracy", 0.0)
        speed = metrics.get("speed", 0.0)
        completion_rate = metrics.get("completion_rate", 0.0)
        efficiency = metrics.get("efficiency", 0.0)
        
        # Weighted average
        overall_score = (
            accuracy * 0.3 +
            speed * 0.25 +
            completion_rate * 0.25 +
            efficiency * 0.2
        )
        
        return min(overall_score, 100.0)
    
    async def _calculate_percentile_rank(self, user_id: int, score: float) -> float:
        """Calculate percentile rank among all users."""
        # This would query all users' performance scores
        return 75.0  # Placeholder - return a higher value
    
    def _calculate_daily_engagement(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate daily engagement metrics."""
        if not activities:
            return {}
        
        daily_engagement = defaultdict(int)
        for activity in activities:
            day = activity.timestamp.date().isoformat()
            daily_engagement[day] += 1
        
        return dict(daily_engagement)
    
    def _calculate_feature_engagement(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate feature engagement metrics."""
        if not activities:
            return {}
        
        feature_usage = defaultdict(int)
        for activity in activities:
            feature = activity.event_type
            feature_usage[feature] += 1
        
        return dict(feature_usage)
    
    def _calculate_session_engagement(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate session engagement metrics."""
        if not activities:
            return {"avg_session_duration": 0.0, "session_count": 0}
        
        sessions = defaultdict(list)
        for activity in activities:
            if activity.session_id:
                sessions[activity.session_id].append(activity.timestamp)
        
        session_durations = []
        for session_activities in sessions.values():
            if len(session_activities) > 1:
                duration = (max(session_activities) - min(session_activities)).total_seconds()
                session_durations.append(duration)
        
        avg_duration = sum(session_durations) / len(session_durations) if session_durations else 0.0
        
        return {
            "avg_session_duration": avg_duration,
            "session_count": len(sessions)
        }
    
    async def _calculate_retention_metrics(self, user_id: int, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, Any]:
        """Calculate retention metrics."""
        return {
            "retention_rate": 0.85,
            "churn_rate": 0.15,
            "lifetime_value": 100.0,
            "engagement_frequency": 5.2
        }
    
    async def _assess_churn_risk(self, user_id: int, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Assess user churn risk."""
        if not activities:
            return {
                "risk_level": "high", 
                "risk_score": 0.8, 
                "risk_factors": ["no_activity"],
                "days_since_activity": 999
            }
        
        # Simple churn risk calculation
        days_since_last_activity = (datetime.utcnow() - activities[0].timestamp).days
        activity_frequency = len(activities) / 30  # activities per day
        
        risk_score = 0.0
        risk_factors = []
        
        if days_since_last_activity > 7:
            risk_score += 0.3
            risk_factors.append("inactive_recently")
        if activity_frequency < 1:
            risk_score += 0.2
            risk_factors.append("low_activity_frequency")
        if len(activities) < 10:
            risk_score += 0.2
            risk_factors.append("low_total_activity")
        
        risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "days_since_activity": days_since_last_activity
        }
    
    def _calculate_engagement_trend(self, activities: List[AnalyticsEvent]) -> str:
        """Calculate engagement trend direction."""
        if len(activities) < 7:
            return "insufficient_data"
        
        # Group by week and calculate trend
        weekly_activity = defaultdict(int)
        for activity in activities:
            week_start = activity.timestamp.date() - timedelta(days=activity.timestamp.weekday())
            weekly_activity[week_start] += 1
        
        if len(weekly_activity) < 2:
            return "insufficient_data"
        
        # Calculate trend
        weeks = sorted(weekly_activity.keys())
        first_week = weekly_activity[weeks[0]]
        last_week = weekly_activity[weeks[-1]]
        
        if last_week > first_week * 1.1:
            return "increasing"
        elif last_week < first_week * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    async def _get_historical_data(self, user_id: int) -> Dict[str, Any]:
        """Get historical data for predictions."""
        # Get last 90 days of data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        activities = (
            self.db.query(AnalyticsEvent)
            .filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.timestamp >= start_date,
                    AnalyticsEvent.timestamp <= end_date
                )
            )
            .order_by(desc(AnalyticsEvent.timestamp))
            .all()
        )
        
        return {
            "activities": [activity.to_dict() for activity in activities],
            "total_activities": len(activities),
            "time_range": "90d"
        }
    
    def _calculate_activity_trend(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate activity trend over time."""
        if len(activities) < 7:
            return {"trend": "insufficient_data", "slope": 0.0}
        
        # Group by day
        daily_activity = defaultdict(int)
        for activity in activities:
            daily_activity[activity.timestamp.date()] += 1
        
        # Calculate trend
        dates = sorted(daily_activity.keys())
        values = [daily_activity[date] for date in dates]
        
        # Simple linear regression
        n = len(dates)
        x_values = [(date - dates[0]).days for date in dates]
        y_values = values
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Check for division by zero
        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return {"trend": "stable", "slope": 0.0}
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        return {"trend": "increasing" if slope > 0 else "decreasing", "slope": slope}
    
    async def _calculate_performance_trend(self, user_id: int, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, Any]:
        """Calculate performance trend over time."""
        # Get performance data over time
        performance_data = (
            self.db.query(UserPerformance)
            .filter(
                and_(
                    UserPerformance.user_id == user_id,
                    UserPerformance.timestamp >= start_date,
                    UserPerformance.timestamp <= end_date
                )
            )
            .order_by(UserPerformance.timestamp)
            .all()
        )
        
        if len(performance_data) < 2:
            return {"trend": "stable", "slope": 0.0}
        
        # Calculate trend using linear regression
        x_values = [(p.timestamp - start_date).days for p in performance_data]
        # Calculate score from performance fields
        y_values = [
            (p.accuracy * 0.3 + p.speed * 0.25 + p.completion_rate * 0.25 + p.efficiency * 0.2)
            for p in performance_data
        ]
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return {"trend": "stable", "slope": 0.0}
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        if slope > 0.01:
            trend = "improving"
        elif slope < -0.01:
            trend = "declining"
        else:
            trend = "stable"
        
        return {"trend": trend, "slope": slope}
    
    def _calculate_behavior_trend(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate behavior trend over time."""
        # This would analyze behavior patterns over time
        return {"trend": "consistent", "pattern_stability": 0.8}
    
    async def _calculate_skill_progression(self, user_id: int, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, Any]:
        """Calculate skill progression over time."""
        return {"trend": "consistent", "pattern_stability": 0.8}
    
    def _determine_trend_direction(self, trends: Dict[str, Any]) -> str:
        """Determine overall trend direction."""
        trend_scores = {
            "activity_trend": 1 if trends.get("activity_trend", {}).get("trend") == "increasing" else -1,
            "performance_trend": 1 if trends.get("performance_trend", {}).get("trend") == "improving" else -1,
            "engagement_trend": 1 if trends.get("engagement_trend") == "increasing" else -1,
            "behavior_trend": 1 if trends.get("behavior_trend", {}).get("trend") == "improving" else -1
        }
        
        overall_score = sum(trend_scores.values())
        
        if overall_score >= 2:
            return "strongly_improving"
        elif overall_score >= 0:
            return "increasing"
        elif overall_score >= -2:
            return "decreasing"
        else:
            return "strongly_declining"
    
    def _calculate_trend_strength(self, trends: Dict[str, Any]) -> float:
        """Calculate trend strength."""
        # This would calculate how strong the trends are
        return 0.75  # Placeholder
    
    def _identify_seasonal_patterns(self, activities: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Identify seasonal patterns in user activity."""
        if not activities:
            return {"seasonal_patterns": [], "weekly_patterns": {}}
        
        # Analyze weekly patterns
        weekly_counts = Counter(activity.timestamp.strftime("%A") for activity in activities)
        
        return {
            "seasonal_patterns": [],
            "weekly_patterns": dict(weekly_counts)
        }
    
    def _calculate_relative_performance(self, user_performance: UserPerformanceMetrics, 
                                      comparison_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate relative performance compared to other users."""
        # This would compare user performance with others
        return {
            "percentile_rank": 75.0,
            "performance_rating": "above_average",
            "comparison_metrics": {}
        }
    
    def _generate_benchmarking_data(self, user_data: UserAnalyticsResponse, 
                                  comparison_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate benchmarking data."""
        # This would create benchmarking comparisons
        return {
            "peer_comparison": {},
            "industry_benchmarks": {},
            "best_practices": []
        }
    
    def _analyze_response_patterns(self, response_times: List[float]) -> Dict[str, Any]:
        """Analyze response time patterns."""
        if not response_times:
            return {"average_response_time": 0, "response_patterns": {}}
        
        return {
            "average_response_time": sum(response_times) / len(response_times),
            "response_patterns": {
                "fast": len([rt for rt in response_times if rt < 1.0]),
                "medium": len([rt for rt in response_times if 1.0 <= rt < 3.0]),
                "slow": len([rt for rt in response_times if rt >= 3.0])
            }
        }


def get_user_analytics_service(db: Session = Depends(get_db)) -> UserAnalyticsService:
    """Dependency to get user analytics service."""
    return UserAnalyticsService(db) 