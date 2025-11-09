"""
Context Analytics Service for Phase 5

This service handles GPT context analytics operations including migration from Phase 5 tables
to dashboard_context_* tables, following the same pattern as Phase 1-4 migrations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import logging

from app.dashboard.models.context import (
    GPTContext,
    ContextInteraction,
    ContextSummary,
    ContextBackup,
    ContextMetrics,
    SharedContext
)

logger = logging.getLogger(__name__)


class ContextAnalyticsService:
    """Service for managing dashboard context analytics with migration support."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    # ==================== CONTEXT OPERATIONS ====================
    
    async def get_contexts(
        self,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get GPT context records."""
        try:
            query = self.db.query(GPTContext)
            
            if user_id:
                query = query.filter(GPTContext.user_id == user_id)
            
            if is_active is not None:
                query = query.filter(GPTContext.is_active == is_active)
            
            contexts = query.limit(limit).all()
            
            return [
                {
                    "id": ctx.id,
                    "user_id": ctx.user_id,
                    "primary_gpt_id": ctx.primary_gpt_id,
                    "name": ctx.name,
                    "description": ctx.description,
                    "context_data": ctx.context_data,
                    "is_active": ctx.is_active,
                    "created_at": ctx.created_at.isoformat() if ctx.created_at else None,
                    "updated_at": ctx.updated_at.isoformat() if ctx.updated_at else None
                }
                for ctx in contexts
            ]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving contexts: {str(e)}"
            )
    
    async def create_context(self, context_data: Dict) -> Dict:
        """Create a new GPT context."""
        try:
            context = GPTContext(
                user_id=context_data.get("user_id"),
                primary_gpt_id=context_data.get("primary_gpt_id"),
                name=context_data.get("name"),
                description=context_data.get("description"),
                context_data=context_data.get("context_data", {}),
                is_active=context_data.get("is_active", True)
            )
            
            self.db.add(context)
            self.db.flush()  # Flush to get ID before commit
            self.db.commit()  # Commit to ensure it's saved
            self.db.refresh(context)  # Refresh to get all fields
            
            return {
                "id": context.id,
                "user_id": context.user_id,
                "primary_gpt_id": context.primary_gpt_id,
                "name": context.name,
                "description": context.description,
                "context_data": context.context_data,
                "is_active": context.is_active,
                "created_at": context.created_at.isoformat() if context.created_at else None
            }
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating context: {str(e)}"
            )
    
    # ==================== CONTEXT INTERACTIONS ====================
    
    async def get_context_interactions(
        self,
        context_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get context interaction records."""
        try:
            query = self.db.query(ContextInteraction)
            
            if context_id:
                query = query.filter(ContextInteraction.context_id == context_id)
            
            interactions = query.order_by(ContextInteraction.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "id": inter.id,
                    "context_id": inter.context_id,
                    "gpt_id": inter.gpt_id,
                    "interaction_type": inter.interaction_type,
                    "content": inter.content,
                    "meta_data": inter.meta_data,
                    "timestamp": inter.timestamp.isoformat() if inter.timestamp else None
                }
                for inter in interactions
            ]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving context interactions: {str(e)}"
            )
    
    # ==================== CONTEXT METRICS ====================
    
    async def get_context_metrics(
        self,
        context_id: Optional[int] = None,
        metric_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get context metrics records."""
        try:
            query = self.db.query(ContextMetrics)
            
            if context_id:
                query = query.filter(ContextMetrics.context_id == context_id)
            
            if metric_type:
                query = query.filter(ContextMetrics.metric_type == metric_type)
            
            metrics = query.order_by(ContextMetrics.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "id": metric.id,
                    "context_id": metric.context_id,
                    "metric_type": metric.metric_type,
                    "metric_data": metric.metric_data,
                    "timestamp": metric.timestamp.isoformat() if metric.timestamp else None
                }
                for metric in metrics
            ]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving context metrics: {str(e)}"
            )
    
    # ==================== MIGRATION LOGIC ====================
    
    async def migrate_existing_context_data(self) -> Dict[str, int]:
        """
        Migrate existing context data from Phase 5 tables to dashboard_context_* tables.
        
        Returns:
            dict: Migration counts for each table type
        """
        migrated_counts = {
            "gpt_contexts": 0,
            "context_interactions": 0,
            "context_summaries": 0,
            "context_backups": 0,
            "context_metrics": 0,
            "shared_contexts": 0
        }
        
        try:
            # The actual migration is handled by migrate_phase5_data.py script
            # This method is just for checking migration status
            from app.scripts.seed_data.migrate_phase5_data import migrate_phase5_data
            
            results = migrate_phase5_data(self.db)
            migrated_counts.update(results)
            
            return migrated_counts
        except Exception as e:
            self.logger.error(f"Error migrating context data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error migrating context data: {str(e)}"
            )

