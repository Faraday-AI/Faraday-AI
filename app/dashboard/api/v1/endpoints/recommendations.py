"""
Recommendations API

This module provides API endpoints for GPT recommendations based on
user context, preferences, and usage patterns.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....dependencies import get_db, get_current_user
from ....services.recommendation_service import RecommendationService
from ....schemas.recommendation_schemas import (
    GPTRecommendation,
    RecommendationScore,
    RecommendationContext,
    RecommendationMetrics,
    RecommendationAnalytics,
    RecommendationPerformance,
    RecommendationInsights,
    RecommendationOptimization
)

router = APIRouter()

@router.get("/gpts", response_model=List[GPTRecommendation])
async def get_gpt_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: Optional[str] = Query(None, description="Optional context ID for recommendations"),
    include_scores: bool = Query(True, description="Include recommendation scores"),
    include_metrics: bool = Query(True, description="Include recommendation metrics"),
    include_analytics: bool = Query(True, description="Include recommendation analytics"),
    include_performance: bool = Query(True, description="Include performance predictions"),
    include_insights: bool = Query(True, description="Include recommendation insights"),
    include_optimization: bool = Query(True, description="Include optimization opportunities")
):
    """Get GPT recommendations for the user."""
    service = RecommendationService(db)
    result = await service.get_gpt_recommendations(
        user_id=current_user["id"],
        context_id=context_id
    )
    
    if include_scores:
        result["scores"] = await service.get_recommendation_scores(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_metrics:
        result["metrics"] = await service.get_recommendation_metrics(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_analytics:
        result["analytics"] = await service.get_recommendation_analytics(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_performance:
        result["performance"] = await service.get_recommendation_performance(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_insights:
        result["insights"] = await service.get_recommendation_insights(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_optimization:
        result["optimization"] = await service.get_recommendation_optimization(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    return result

@router.get("/scores", response_model=RecommendationScore)
async def get_recommendation_scores(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Optional GPT ID to get scores for"),
    include_breakdown: bool = Query(True, description="Include score breakdown"),
    include_trends: bool = Query(True, description="Include score trends"),
    include_benchmarks: bool = Query(True, description="Include score benchmarks"),
    include_correlations: bool = Query(True, description="Include score correlations"),
    include_impact: bool = Query(True, description="Include score impact analysis")
):
    """Get detailed recommendation scores."""
    service = RecommendationService(db)
    return await service.get_recommendation_scores(
        user_id=current_user["id"],
        gpt_id=gpt_id,
        include_breakdown=include_breakdown,
        include_trends=include_trends,
        include_benchmarks=include_benchmarks,
        include_correlations=include_correlations,
        include_impact=include_impact
    )

@router.get("/context", response_model=RecommendationContext)
async def get_recommendation_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: Optional[str] = Query(None, description="Optional context ID"),
    include_history: bool = Query(True, description="Include context history"),
    include_patterns: bool = Query(True, description="Include usage patterns"),
    include_preferences: bool = Query(True, description="Include user preferences"),
    include_insights: bool = Query(True, description="Include context insights"),
    include_optimization: bool = Query(True, description="Include context optimization")
):
    """Get recommendation context details."""
    service = RecommendationService(db)
    return await service.get_recommendation_context(
        user_id=current_user["id"],
        context_id=context_id,
        include_history=include_history,
        include_patterns=include_patterns,
        include_preferences=include_preferences,
        include_insights=include_insights,
        include_optimization=include_optimization
    )

@router.get("/metrics", response_model=RecommendationMetrics)
async def get_recommendation_metrics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Optional GPT ID"),
    include_accuracy: bool = Query(True, description="Include accuracy metrics"),
    include_relevance: bool = Query(True, description="Include relevance metrics"),
    include_engagement: bool = Query(True, description="Include engagement metrics"),
    include_efficiency: bool = Query(True, description="Include efficiency metrics"),
    include_quality: bool = Query(True, description="Include quality metrics"),
    include_impact: bool = Query(True, description="Include impact metrics")
):
    """Get detailed recommendation metrics."""
    service = RecommendationService(db)
    return await service.get_recommendation_metrics(
        user_id=current_user["id"],
        gpt_id=gpt_id,
        include_accuracy=include_accuracy,
        include_relevance=include_relevance,
        include_engagement=include_engagement,
        include_efficiency=include_efficiency,
        include_quality=include_quality,
        include_impact=include_impact
    )

@router.get("/analytics", response_model=RecommendationAnalytics)
async def get_recommendation_analytics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Optional GPT ID"),
    include_trends: bool = Query(True, description="Include recommendation trends"),
    include_patterns: bool = Query(True, description="Include usage patterns"),
    include_forecasts: bool = Query(True, description="Include usage forecasts"),
    include_correlations: bool = Query(True, description="Include metric correlations"),
    include_anomalies: bool = Query(True, description="Include anomaly detection"),
    include_insights: bool = Query(True, description="Include analytics insights")
):
    """Get detailed recommendation analytics."""
    service = RecommendationService(db)
    return await service.get_recommendation_analytics(
        user_id=current_user["id"],
        gpt_id=gpt_id,
        include_trends=include_trends,
        include_patterns=include_patterns,
        include_forecasts=include_forecasts,
        include_correlations=include_correlations,
        include_anomalies=include_anomalies,
        include_insights=include_insights
    )

@router.get("/performance", response_model=RecommendationPerformance)
async def get_recommendation_performance(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Optional GPT ID"),
    include_benchmarks: bool = Query(True, description="Include performance benchmarks"),
    include_optimization: bool = Query(True, description="Include optimization opportunities"),
    include_recommendations: bool = Query(True, description="Include performance recommendations"),
    include_trends: bool = Query(True, description="Include performance trends"),
    include_impact: bool = Query(True, description="Include performance impact"),
    include_insights: bool = Query(True, description="Include performance insights")
):
    """Get detailed recommendation performance data."""
    service = RecommendationService(db)
    return await service.get_recommendation_performance(
        user_id=current_user["id"],
        gpt_id=gpt_id,
        include_benchmarks=include_benchmarks,
        include_optimization=include_optimization,
        include_recommendations=include_recommendations,
        include_trends=include_trends,
        include_impact=include_impact,
        include_insights=include_insights
    )

@router.get("/insights", response_model=RecommendationInsights)
async def get_recommendation_insights(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Optional GPT ID"),
    include_trends: bool = Query(True, description="Include insight trends"),
    include_patterns: bool = Query(True, description="Include usage patterns"),
    include_opportunities: bool = Query(True, description="Include optimization opportunities"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_forecasts: bool = Query(True, description="Include usage forecasts")
):
    """Get detailed recommendation insights."""
    service = RecommendationService(db)
    return await service.get_recommendation_insights(
        user_id=current_user["id"],
        gpt_id=gpt_id,
        include_trends=include_trends,
        include_patterns=include_patterns,
        include_opportunities=include_opportunities,
        include_impact=include_impact,
        include_forecasts=include_forecasts
    )

@router.get("/optimization", response_model=RecommendationOptimization)
async def get_recommendation_optimization(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Optional GPT ID"),
    include_opportunities: bool = Query(True, description="Include optimization opportunities"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_recommendations: bool = Query(True, description="Include optimization recommendations"),
    include_metrics: bool = Query(True, description="Include optimization metrics"),
    include_forecasts: bool = Query(True, description="Include optimization forecasts")
):
    """Get detailed recommendation optimization data."""
    service = RecommendationService(db)
    return await service.get_recommendation_optimization(
        user_id=current_user["id"],
        gpt_id=gpt_id,
        include_opportunities=include_opportunities,
        include_impact=include_impact,
        include_recommendations=include_recommendations,
        include_metrics=include_metrics,
        include_forecasts=include_forecasts
    ) 