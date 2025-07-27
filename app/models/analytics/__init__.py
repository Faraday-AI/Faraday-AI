"""
Analytics models module.

This module contains analytics-related database models.
"""

from .user_analytics import (
    UserActivity,
    UserBehavior,
    UserPerformance,
    UserEngagement,
    UserPrediction,
    UserRecommendation,
    AnalyticsEvent,
    UserInsight,
    UserTrend,
    UserComparison
)

__all__ = [
    'UserActivity',
    'UserBehavior',
    'UserPerformance',
    'UserEngagement',
    'UserPrediction',
    'UserRecommendation',
    'AnalyticsEvent',
    'UserInsight',
    'UserTrend',
    'UserComparison'
] 