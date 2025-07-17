"""
Recommendation Service

This module provides sophisticated recommendation scoring for GPTs
based on user context, preferences, and usage patterns.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback
)
from ..models.context import ContextInteraction, GPTContext

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    async def calculate_gpt_score(
        self,
        gpt: GPTDefinition,
        user_id: str,
        current_subscriptions: List[DashboardGPTSubscription],
        context_data: Optional[Dict] = None
    ) -> Dict:
        """Calculate comprehensive recommendation score for a GPT."""
        try:
            # Get user's interaction history
            interactions = self._get_user_interactions(user_id)
            
            # Calculate base scores
            category_score = self._calculate_category_score(gpt, current_subscriptions)
            compatibility_score = self._calculate_compatibility_score(gpt, current_subscriptions)
            context_score = self._calculate_context_score(gpt, context_data) if context_data else 0.5
            usage_score = self._calculate_usage_score(gpt, interactions)
            performance_score = self._calculate_performance_score(gpt)

            # Calculate weighted final score
            weights = {
                'category': 0.25,
                'compatibility': 0.2,
                'context': 0.25,
                'usage': 0.15,
                'performance': 0.15
            }

            final_score = (
                category_score * weights['category'] +
                compatibility_score * weights['compatibility'] +
                context_score * weights['context'] +
                usage_score * weights['usage'] +
                performance_score * weights['performance']
            )

            # Generate explanation
            reasons = []
            if category_score > 0.7:
                reasons.append("Complements your current GPT categories")
            if compatibility_score > 0.7:
                reasons.append("High compatibility with your active GPTs")
            if context_score > 0.7:
                reasons.append("Relevant to your current context")
            if usage_score > 0.7:
                reasons.append("Matches your usage patterns")
            if performance_score > 0.7:
                reasons.append("Strong performance metrics")

            return {
                "score": final_score,
                "components": {
                    "category_score": category_score,
                    "compatibility_score": compatibility_score,
                    "context_score": context_score,
                    "usage_score": usage_score,
                    "performance_score": performance_score
                },
                "reasons": reasons
            }

        except Exception as e:
            # Log error and return default score
            print(f"Error calculating recommendation score: {str(e)}")
            return {
                "score": 0.5,
                "components": {},
                "reasons": ["Based on basic compatibility"]
            }

    def _get_user_interactions(self, user_id: str) -> List[Dict]:
        """Get user's recent interactions."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        return self.db.query(ContextInteraction).join(
            GPTContext
        ).filter(
            GPTContext.user_id == user_id,
            ContextInteraction.timestamp >= cutoff_date
        ).all()

    def _calculate_category_score(
        self,
        gpt: GPTDefinition,
        current_subscriptions: List[DashboardGPTSubscription]
    ) -> float:
        """Calculate score based on GPT category complementarity."""
        try:
            # Get current categories
            current_categories = {
                sub.gpt_definition.category for sub in current_subscriptions
            }

            # Higher score if category adds diversity
            if gpt.category not in current_categories:
                return 0.8 + (0.2 * (1 - len(current_categories) / 5))  # Max 5 categories
            
            # Lower score if category is well-represented
            category_count = sum(
                1 for sub in current_subscriptions
                if sub.gpt_definition.category == gpt.category
            )
            return max(0.3, 1 - (category_count * 0.2))

        except Exception:
            return 0.5

    def _calculate_compatibility_score(
        self,
        gpt: GPTDefinition,
        current_subscriptions: List[DashboardGPTSubscription]
    ) -> float:
        """Calculate score based on compatibility with current GPTs."""
        try:
            # Check requirements and capabilities
            requirements = gpt.requirements or {}
            capabilities = {
                sub.gpt_definition.capabilities for sub in current_subscriptions
            }

            # Calculate compatibility based on requirements met
            if not requirements:
                return 0.7  # Default for no special requirements

            req_count = len(requirements)
            met_count = sum(
                1 for cap in capabilities
                if any(req in cap for req in requirements)
            )

            return 0.4 + (0.6 * (met_count / req_count))

        except Exception:
            return 0.5

    def _calculate_context_score(
        self,
        gpt: GPTDefinition,
        context_data: Dict
    ) -> float:
        """Calculate score based on relevance to current context."""
        try:
            if not context_data:
                return 0.5

            # Extract key terms from context
            context_terms = set(
                term.lower()
                for term in context_data.get("keywords", [])
            )

            # Compare with GPT capabilities and description
            gpt_terms = set(
                term.lower()
                for term in (
                    gpt.capabilities.get("keywords", []) +
                    gpt.description.split()
                )
            )

            # Calculate term overlap
            if not context_terms or not gpt_terms:
                return 0.5

            overlap = len(context_terms & gpt_terms)
            return min(1.0, 0.4 + (0.6 * (overlap / len(context_terms))))

        except Exception:
            return 0.5

    def _calculate_usage_score(
        self,
        gpt: GPTDefinition,
        interactions: List[ContextInteraction]
    ) -> float:
        """Calculate score based on user's usage patterns."""
        try:
            if not interactions:
                return 0.5

            # Analyze interaction patterns
            interaction_types = [i.interaction_type for i in interactions]
            type_counts = {}
            for t in interaction_types:
                type_counts[t] = type_counts.get(t, 0) + 1

            # Compare with GPT's intended use cases
            use_cases = set(gpt.capabilities.get("use_cases", []))
            if not use_cases:
                return 0.5

            # Calculate match score
            matched_cases = sum(
                1 for case in use_cases
                if any(t.lower() in case.lower() for t in type_counts.keys())
            )
            return 0.4 + (0.6 * (matched_cases / len(use_cases)))

        except Exception:
            return 0.5

    def _calculate_performance_score(self, gpt: GPTDefinition) -> float:
        """Calculate score based on GPT's performance metrics."""
        try:
            # Get recent performance metrics
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            metrics = self.db.query(GPTPerformance).filter(
                GPTPerformance.subscription_id.in_(
                    self.db.query(DashboardGPTSubscription.id).filter(
                        DashboardGPTSubscription.gpt_definition_id == gpt.id
                    )
                ),
                GPTPerformance.timestamp >= cutoff_date
            ).all()

            if not metrics:
                return 0.5

            # Calculate average scores
            scores = []
            for metric in metrics:
                metric_data = metric.metrics or {}
                scores.extend([
                    metric_data.get("accuracy", 0.5),
                    metric_data.get("response_time_score", 0.5),
                    metric_data.get("user_satisfaction", 0.5)
                ])

            return sum(scores) / len(scores)

        except Exception:
            return 0.5 