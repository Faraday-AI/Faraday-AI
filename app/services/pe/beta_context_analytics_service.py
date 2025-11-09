"""
Beta Context Analytics Service
Provides context analytics for beta teachers (contexts, interactions, metrics)
Independent from district-level context analytics.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.dashboard.services.context_analytics_service import ContextAnalyticsService
from app.dashboard.models.context import (
    GPTContext,
    ContextInteraction,
    ContextMetrics
)
from app.models.teacher_registration import TeacherRegistration
from app.models.core.user import User
from app.dashboard.models.user import DashboardUser


class BetaContextAnalyticsService(ContextAnalyticsService):
    """Context analytics service for beta teachers - filters to teacher's context."""
    
    def __init__(self, db: Session, teacher_id: Union[str, int]):
        super().__init__(db)
        self.teacher_id = teacher_id
        self.logger = __import__('logging').getLogger("beta_context_analytics_service")
    
    def _get_teacher_user_id(self) -> Optional[int]:
        """Get the dashboard_user.id for this beta teacher."""
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        if not teacher or not teacher.email:
            return None
        
        # Get User from core.users table
        user = self.db.query(User).filter(User.email == teacher.email).first()
        if not user:
            return None
        
        # Get DashboardUser from dashboard_users table using core_user_id
        dashboard_user = self.db.query(DashboardUser).filter(
            DashboardUser.core_user_id == user.id
        ).first()
        
        if dashboard_user:
            return dashboard_user.id
        
        return None
    
    async def get_contexts(
        self,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get GPT context records for beta teacher."""
        # Get the dashboard_user.id for this teacher
        teacher_user_id = self._get_teacher_user_id()
        
        if not teacher_user_id:
            return []
        
        # Override user_id to ensure only this teacher's contexts are returned
        if user_id and user_id != teacher_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own contexts"
            )
        
        return await super().get_contexts(
            user_id=teacher_user_id,
            is_active=is_active,
            limit=limit
        )
    
    async def create_context(self, context_data: Dict) -> Dict:
        """Create a new GPT context for beta teacher."""
        # Get the dashboard_user.id for this teacher
        teacher_user_id = self._get_teacher_user_id()
        
        if not teacher_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta teacher dashboard user not found"
            )
        
        # Ensure beta teacher can only create contexts for themselves
        if context_data.get('user_id') and context_data.get('user_id') != teacher_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only create contexts for themselves"
            )
        
        # Set user_id to teacher's dashboard_user.id
        context_data['user_id'] = teacher_user_id
        
        # Add beta context metadata
        if 'context_data' not in context_data:
            context_data['context_data'] = {}
        
        context_data['context_data']['beta_teacher_id'] = str(self.teacher_id)
        context_data['context_data']['beta_system'] = True
        
        result = await super().create_context(context_data)
        
        # Add beta metadata to result
        result['beta_teacher_id'] = str(self.teacher_id)
        result['beta_system'] = True
        
        return result
    
    async def get_context_interactions(
        self,
        context_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get context interaction records for beta teacher."""
        # Verify context belongs to this teacher
        if context_id:
            teacher_user_id = self._get_teacher_user_id()
            if teacher_user_id:
                context = self.db.query(GPTContext).filter(
                    GPTContext.id == context_id,
                    GPTContext.user_id == teacher_user_id
                ).first()
                
                if not context:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Beta teachers can only access interactions for their own contexts"
                    )
        
        return await super().get_context_interactions(
            context_id=context_id,
            limit=limit
        )
    
    async def get_context_metrics(
        self,
        context_id: Optional[int] = None,
        metric_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get context metrics records for beta teacher."""
        # Verify context belongs to this teacher
        if context_id:
            teacher_user_id = self._get_teacher_user_id()
            if teacher_user_id:
                context = self.db.query(GPTContext).filter(
                    GPTContext.id == context_id,
                    GPTContext.user_id == teacher_user_id
                ).first()
                
                if not context:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Beta teachers can only access metrics for their own contexts"
                    )
        
        return await super().get_context_metrics(
            context_id=context_id,
            metric_type=metric_type,
            limit=limit
        )
    
    async def migrate_existing_context_data(self) -> Dict[str, int]:
        """Get migration status for beta teacher's context data."""
        # Beta system shares the same tables, so migration is handled at the system level
        # This method just returns status for this teacher's contexts
        teacher_user_id = self._get_teacher_user_id()
        
        if not teacher_user_id:
            return {
                "gpt_contexts": 0,
                "context_interactions": 0,
                "context_summaries": 0,
                "context_backups": 0,
                "context_metrics": 0,
                "shared_contexts": 0,
                "total": 0
            }
        
        # Count migrated contexts for this teacher
        contexts = self.db.query(GPTContext).filter(
            GPTContext.user_id == teacher_user_id
        ).count()
        
        return {
            "gpt_contexts": contexts,
            "context_interactions": 0,  # Would need to count separately
            "context_summaries": 0,
            "context_backups": 0,
            "context_metrics": 0,
            "shared_contexts": 0,
            "total": contexts
        }

