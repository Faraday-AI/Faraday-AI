"""
Beta Resource Management Service
Provides resource management for beta teachers (usage, thresholds, optimizations)
Independent from district-level resource management.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.dashboard.services.resource_management_service import ResourceManagementService
from app.dashboard.models.resource_models import (
    DashboardResourceUsage,
    DashboardResourceThreshold,
    DashboardResourceOptimization
)
from app.models.teacher_registration import TeacherRegistration
from app.models.core.user import User


class BetaResourceManagementService(ResourceManagementService):
    """Resource management service for beta teachers - filters to teacher's context."""
    
    def __init__(self, db: Session, teacher_id: Union[str, int]):
        super().__init__(db)
        self.teacher_id = teacher_id
        self.logger = __import__('logging').getLogger("beta_resource_management_service")
    
    async def get_resource_usage(
        self,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get resource usage records for beta teacher."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Filter to only this teacher's resources
        if user_id and user_id != actual_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own resource usage"
            )
        
        return await super().get_resource_usage(
            user_id=actual_user_id,
            project_id=project_id,
            resource_type=resource_type,
            limit=limit
        )
    
    async def create_resource_usage(self, usage_data: Dict) -> Dict:
        """Create a new resource usage record for beta teacher."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Ensure beta teacher can only create usage for themselves
        if usage_data.get('user_id') and usage_data.get('user_id') != actual_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only create resource usage for themselves"
            )
        
        usage_data['user_id'] = actual_user_id
        
        # Add beta context to meta_data
        if usage_data.get('meta_data') is None:
            usage_data['meta_data'] = {}
        
        if isinstance(usage_data['meta_data'], dict):
            usage_data['meta_data']['beta_teacher_id'] = str(self.teacher_id)
            usage_data['meta_data']['beta_system'] = True
        
        return await super().create_resource_usage(usage_data)
    
    async def get_resource_thresholds(
        self,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict]:
        """Get resource thresholds for beta teacher."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Filter to only this teacher's thresholds
        if user_id and user_id != actual_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own resource thresholds"
            )
        
        return await super().get_resource_thresholds(
            user_id=actual_user_id,
            project_id=project_id,
            resource_type=resource_type
        )
    
    async def create_resource_threshold(self, threshold_data: Dict) -> Dict:
        """Create a new resource threshold for beta teacher."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Ensure beta teacher can only create thresholds for themselves
        if threshold_data.get('user_id') and threshold_data.get('user_id') != actual_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only create resource thresholds for themselves"
            )
        
        threshold_data['user_id'] = actual_user_id
        
        # Add beta context to meta_data
        if threshold_data.get('meta_data') is None:
            threshold_data['meta_data'] = {}
        
        if isinstance(threshold_data['meta_data'], dict):
            threshold_data['meta_data']['beta_teacher_id'] = str(self.teacher_id)
            threshold_data['meta_data']['beta_system'] = True
        
        return await super().create_resource_threshold(threshold_data)
    
    async def get_resource_optimizations(
        self,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get resource optimizations for beta teacher."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Filter to only this teacher's optimizations
        if user_id and user_id != actual_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own resource optimizations"
            )
        
        return await super().get_resource_optimizations(
            user_id=actual_user_id,
            project_id=project_id,
            status_filter=status_filter
        )
    
    async def create_resource_optimization(self, optimization_data: Dict) -> Dict:
        """Create a new resource optimization for beta teacher."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Ensure beta teacher can only create optimizations for themselves
        if optimization_data.get('user_id') and optimization_data.get('user_id') != actual_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only create resource optimizations for themselves"
            )
        
        optimization_data['user_id'] = actual_user_id
        
        # Add beta context to meta_data
        if optimization_data.get('meta_data') is None:
            optimization_data['meta_data'] = {}
        
        if isinstance(optimization_data['meta_data'], dict):
            optimization_data['meta_data']['beta_teacher_id'] = str(self.teacher_id)
            optimization_data['meta_data']['beta_system'] = True
        
        return await super().create_resource_optimization(optimization_data)
    
    async def migrate_existing_resource_data(self) -> Dict[str, int]:
        """Check migration status for beta teacher's resources."""
        # Get the actual user_id from User table using TeacherRegistration email
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        actual_user_id = None
        if teacher and teacher.email:
            user = self.db.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Get migration counts filtered by beta teacher
        from sqlalchemy import text
        
        migrated_usage = self.db.execute(text("""
            SELECT COUNT(*) FROM dashboard_resource_usage
            WHERE user_id = :user_id
            AND meta_data::text LIKE '%migrated_from%resource_management_usage%'
        """), {"user_id": actual_user_id}).scalar() if actual_user_id else 0
        
        migrated_thresholds = self.db.execute(text("""
            SELECT COUNT(*) FROM dashboard_resource_thresholds
            WHERE user_id = :user_id
            AND meta_data::text LIKE '%migrated_from%resource_thresholds%'
        """), {"user_id": actual_user_id}).scalar() if actual_user_id else 0
        
        migrated_optimizations = self.db.execute(text("""
            SELECT COUNT(*) FROM dashboard_resource_optimizations
            WHERE user_id = :user_id
            AND meta_data::text LIKE '%migrated_from%resource_optimizations%'
        """), {"user_id": actual_user_id}).scalar() if actual_user_id else 0
        
        return {
            "resource_usage": migrated_usage,
            "resource_thresholds": migrated_thresholds,
            "resource_optimizations": migrated_optimizations,
            "resource_sharing": 0,
            "optimization_events": 0
        }

