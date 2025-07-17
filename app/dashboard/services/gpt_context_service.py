"""
GPT Context Service for managing GPT context and history.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.context import GPTContext
from ..models.gpt_models import GPTDefinition
from ..models.user import DashboardUser
from ..schemas.context import (
    ContextHistory,
    ContextMetrics,
    ContextPatterns,
    ContextPreferences,
    ContextSharing
)

class GPTContextService:
    """Service for managing GPT context and history."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_context_history(
        self,
        gpt_id: str,
        user_id: str,
        time_window: str = "24h",
        include_metrics: bool = True,
        include_patterns: bool = True,
        include_preferences: bool = True
    ) -> Dict[str, Any]:
        """
        Get context history for a GPT and user.
        
        Args:
            gpt_id: The ID of the GPT
            user_id: The ID of the user
            time_window: Time window for history (24h, 7d, 30d)
            include_metrics: Whether to include context metrics
            include_patterns: Whether to include context patterns
            include_preferences: Whether to include context preferences
        """
        # Calculate time window
        window_map = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        time_delta = window_map.get(time_window, timedelta(hours=24))
        start_time = datetime.utcnow() - time_delta
        
        # Get context history
        history = self.db.query(GPTContext).filter(
            GPTContext.gpt_id == gpt_id,
            GPTContext.user_id == user_id,
            GPTContext.created_at >= start_time
        ).order_by(desc(GPTContext.created_at)).all()
        
        result = {
            "history": [ContextHistory.from_orm(ctx) for ctx in history]
        }
        
        if include_metrics:
            result["metrics"] = await self._get_context_metrics(history)
        
        if include_patterns:
            result["patterns"] = await self._get_context_patterns(history)
        
        if include_preferences:
            result["preferences"] = await self._get_context_preferences(gpt_id, user_id)
        
        return result
    
    async def _get_context_metrics(self, history: List[GPTContext]) -> ContextMetrics:
        """Calculate context metrics from history."""
        if not history:
            return ContextMetrics()
        
        total_contexts = len(history)
        avg_context_length = sum(len(ctx.content) for ctx in history) / total_contexts
        context_types = {}
        for ctx in history:
            context_types[ctx.context_type] = context_types.get(ctx.context_type, 0) + 1
        
        return ContextMetrics(
            total_contexts=total_contexts,
            avg_context_length=avg_context_length,
            context_types=context_types,
            last_updated=history[0].created_at
        )
    
    async def _get_context_patterns(self, history: List[GPTContext]) -> ContextPatterns:
        """Analyze context patterns from history."""
        if not history:
            return ContextPatterns()
        
        # Analyze temporal patterns
        time_patterns = {}
        for ctx in history:
            hour = ctx.created_at.hour
            time_patterns[hour] = time_patterns.get(hour, 0) + 1
        
        # Analyze content patterns
        content_patterns = {}
        for ctx in history:
            if ctx.context_type not in content_patterns:
                content_patterns[ctx.context_type] = {
                    "count": 0,
                    "avg_length": 0,
                    "last_used": None
                }
            pattern = content_patterns[ctx.context_type]
            pattern["count"] += 1
            pattern["avg_length"] = (pattern["avg_length"] * (pattern["count"] - 1) + len(ctx.content)) / pattern["count"]
            if not pattern["last_used"] or ctx.created_at > pattern["last_used"]:
                pattern["last_used"] = ctx.created_at
        
        return ContextPatterns(
            time_patterns=time_patterns,
            content_patterns=content_patterns
        )
    
    async def _get_context_preferences(self, gpt_id: str, user_id: str) -> ContextPreferences:
        """Get context preferences for a GPT and user."""
        # Get user preferences
        user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
        gpt = self.db.query(GPTDefinition).filter(GPTDefinition.id == gpt_id).first()
        
        if not user or not gpt:
            return ContextPreferences()
        
        return ContextPreferences(
            preferred_context_types=user.preferred_context_types or [],
            context_retention_days=user.context_retention_days or 30,
            auto_context_sharing=user.auto_context_sharing or False,
            context_sharing_scope=user.context_sharing_scope or "private",
            gpt_context_preferences=gpt.meta_data.get("context_preferences", {}) if gpt.meta_data else {}
        )
    
    async def share_context(
        self,
        source_gpt_id: str,
        target_gpt_id: str,
        context_id: str,
        include_history: bool = True,
        include_metrics: bool = True,
        include_patterns: bool = True
    ) -> ContextSharing:
        """
        Share context between GPTs.
        
        Args:
            source_gpt_id: The ID of the source GPT
            target_gpt_id: The ID of the target GPT
            context_id: The ID of the context to share
            include_history: Whether to include context history
            include_metrics: Whether to include context metrics
            include_patterns: Whether to include context patterns
        """
        # Get source context
        source_context = self.db.query(GPTContext).filter(
            GPTContext.id == context_id,
            GPTContext.gpt_id == source_gpt_id
        ).first()
        
        if not source_context:
            raise ValueError("Source context not found")
        
        # Create shared context
        shared_context = GPTContext(
            gpt_id=target_gpt_id,
            user_id=source_context.user_id,
            content=source_context.content,
            context_type=source_context.context_type,
            metadata={
                "shared_from": source_gpt_id,
                "original_context_id": context_id,
                "shared_at": datetime.utcnow().isoformat()
            }
        )
        
        self.db.add(shared_context)
        self.db.commit()
        
        result = {
            "shared_context": ContextHistory.from_orm(shared_context)
        }
        
        if include_history:
            result["history"] = await self.get_context_history(
                target_gpt_id,
                source_context.user_id,
                include_metrics=include_metrics,
                include_patterns=include_patterns
            )
        
        return ContextSharing(**result)
    
    async def update_context_preferences(
        self,
        gpt_id: str,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> ContextPreferences:
        """
        Update context preferences for a GPT and user.
        
        Args:
            gpt_id: The ID of the GPT
            user_id: The ID of the user
            preferences: The preferences to update
        """
        user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
        gpt = self.db.query(GPTDefinition).filter(GPTDefinition.id == gpt_id).first()
        
        if not user or not gpt:
            raise ValueError("User or GPT not found")
        
        # Update user preferences
        if "preferred_context_types" in preferences:
            user.preferred_context_types = preferences["preferred_context_types"]
        if "context_retention_days" in preferences:
            user.context_retention_days = preferences["context_retention_days"]
        if "auto_context_sharing" in preferences:
            user.auto_context_sharing = preferences["auto_context_sharing"]
        if "context_sharing_scope" in preferences:
            user.context_sharing_scope = preferences["context_sharing_scope"]
        
        # Update GPT preferences
        if "gpt_context_preferences" in preferences:
            gpt.meta_data = {
                **(gpt.meta_data or {}),
                "context_preferences": preferences["gpt_context_preferences"]
            }
        
        self.db.commit()
        
        return await self._get_context_preferences(gpt_id, user_id)
    
    async def cleanup_old_contexts(
        self,
        gpt_id: Optional[str] = None,
        user_id: Optional[str] = None,
        retention_days: int = 30
    ) -> Dict[str, int]:
        """
        Clean up old contexts based on retention policy.
        
        Args:
            gpt_id: Optional GPT ID to filter contexts
            user_id: Optional user ID to filter contexts
            retention_days: Number of days to retain contexts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        query = self.db.query(GPTContext).filter(
            GPTContext.created_at < cutoff_date
        )
        
        if gpt_id:
            query = query.filter(GPTContext.gpt_id == gpt_id)
        if user_id:
            query = query.filter(GPTContext.user_id == user_id)
        
        deleted_count = query.delete()
        self.db.commit()
        
        return {
            "deleted_contexts": deleted_count,
            "retention_days": retention_days
        } 