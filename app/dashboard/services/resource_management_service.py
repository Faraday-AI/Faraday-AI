"""
Resource Management Service for Phase 4

This service handles resource management operations including migration from Phase 11 tables
to dashboard_resource_* tables, following the same pattern as Phase 1-3 migrations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import logging
import json

from app.dashboard.models.resource_models import (
    DashboardResourceUsage,
    DashboardResourceThreshold,
    DashboardResourceOptimization,
    DashboardResourceSharing,
    DashboardOptimizationEvent,
    ResourceType,
    ResourceMetric
)

logger = logging.getLogger(__name__)


class ResourceManagementService:
    """Service for managing dashboard resources with migration support."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    # ==================== RESOURCE USAGE ====================
    
    async def get_resource_usage(
        self,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get resource usage records."""
        try:
            query = self.db.query(DashboardResourceUsage)
            
            if user_id:
                query = query.filter(DashboardResourceUsage.user_id == user_id)
            if project_id:
                query = query.filter(DashboardResourceUsage.project_id == project_id)
            if resource_type:
                query = query.filter(DashboardResourceUsage.resource_type == resource_type)
            
            records = query.order_by(DashboardResourceUsage.timestamp.desc()).limit(limit).all()
            return [self._usage_to_dict(r) for r in records]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving resource usage: {str(e)}"
            )
    
    async def create_resource_usage(self, usage_data: Dict) -> Dict:
        """Create a new resource usage record."""
        try:
            required_fields = ['resource_id', 'resource_type', 'metric_type', 'value', 'unit']
            missing_fields = [field for field in required_fields if field not in usage_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            new_usage = DashboardResourceUsage(
                resource_id=usage_data['resource_id'],
                resource_type=ResourceType(usage_data['resource_type']),
                metric_type=ResourceMetric(usage_data['metric_type']),
                value=usage_data['value'],
                unit=usage_data['unit'],
                timestamp=usage_data.get('timestamp', datetime.utcnow()),
                meta_data=usage_data.get('meta_data'),
                user_id=usage_data.get('user_id'),
                project_id=usage_data.get('project_id'),
                organization_id=usage_data.get('organization_id')
            )
            
            self.db.add(new_usage)
            self.db.commit()
            self.db.refresh(new_usage)
            
            return self._usage_to_dict(new_usage)
        except HTTPException:
            raise
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
                detail=f"Error creating resource usage: {str(e)}"
            )
    
    # ==================== RESOURCE THRESHOLDS ====================
    
    async def get_resource_thresholds(
        self,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict]:
        """Get resource thresholds."""
        try:
            query = self.db.query(DashboardResourceThreshold)
            
            if user_id:
                query = query.filter(DashboardResourceThreshold.user_id == user_id)
            if project_id:
                query = query.filter(DashboardResourceThreshold.project_id == project_id)
            if resource_type:
                query = query.filter(DashboardResourceThreshold.resource_type == resource_type)
            
            records = query.all()
            return [self._threshold_to_dict(r) for r in records]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving resource thresholds: {str(e)}"
            )
    
    async def create_resource_threshold(self, threshold_data: Dict) -> Dict:
        """Create a new resource threshold."""
        try:
            required_fields = ['resource_type', 'metric_type', 'threshold_value', 'threshold_type', 'action']
            missing_fields = [field for field in required_fields if field not in threshold_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            new_threshold = DashboardResourceThreshold(
                resource_type=ResourceType(threshold_data['resource_type']),
                metric_type=ResourceMetric(threshold_data['metric_type']),
                threshold_value=threshold_data['threshold_value'],
                threshold_type=threshold_data['threshold_type'],
                action=threshold_data['action'],
                meta_data=threshold_data.get('meta_data'),
                user_id=threshold_data.get('user_id'),
                project_id=threshold_data.get('project_id'),
                organization_id=threshold_data.get('organization_id')
            )
            
            self.db.add(new_threshold)
            self.db.commit()
            self.db.refresh(new_threshold)
            
            return self._threshold_to_dict(new_threshold)
        except HTTPException:
            raise
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
                detail=f"Error creating resource threshold: {str(e)}"
            )
    
    # ==================== RESOURCE OPTIMIZATIONS ====================
    
    async def get_resource_optimizations(
        self,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get resource optimizations."""
        try:
            query = self.db.query(DashboardResourceOptimization)
            
            if user_id:
                query = query.filter(DashboardResourceOptimization.user_id == user_id)
            if project_id:
                query = query.filter(DashboardResourceOptimization.project_id == project_id)
            if status_filter:
                query = query.filter(DashboardResourceOptimization.status == status_filter)
            
            records = query.order_by(DashboardResourceOptimization.created_at.desc()).all()
            return [self._optimization_to_dict(r) for r in records]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving resource optimizations: {str(e)}"
            )
    
    async def create_resource_optimization(self, optimization_data: Dict) -> Dict:
        """Create a new resource optimization."""
        try:
            required_fields = ['resource_type', 'metric_type', 'current_value', 'recommended_value', 'recommendation']
            missing_fields = [field for field in required_fields if field not in optimization_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            new_optimization = DashboardResourceOptimization(
                resource_type=ResourceType(optimization_data['resource_type']),
                metric_type=ResourceMetric(optimization_data['metric_type']),
                current_value=optimization_data['current_value'],
                recommended_value=optimization_data['recommended_value'],
                potential_savings=optimization_data.get('potential_savings'),
                confidence_score=optimization_data.get('confidence_score'),
                recommendation=optimization_data['recommendation'],
                status=optimization_data.get('status', 'pending'),
                created_at=optimization_data.get('created_at', datetime.utcnow()),
                applied_at=optimization_data.get('applied_at'),
                meta_data=optimization_data.get('meta_data'),
                user_id=optimization_data.get('user_id'),
                project_id=optimization_data.get('project_id'),
                organization_id=optimization_data.get('organization_id')
            )
            
            self.db.add(new_optimization)
            self.db.commit()
            self.db.refresh(new_optimization)
            
            return self._optimization_to_dict(new_optimization)
        except HTTPException:
            raise
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
                detail=f"Error creating resource optimization: {str(e)}"
            )
    
    # ==================== MIGRATION LOGIC ====================
    
    async def migrate_existing_resource_data(self) -> Dict[str, int]:
        """
        Migrate existing resource data from Phase 11 tables to dashboard_resource_* tables.
        
        Returns:
            dict: Migration counts for each table type
        """
        migrated_counts = {
            "resource_usage": 0,
            "resource_thresholds": 0,
            "resource_optimizations": 0,
            "resource_sharing": 0,
            "optimization_events": 0
        }
        
        try:
            # The actual migration is handled by migrate_phase4_data.py script
            # This method is here for consistency with Phase 1-3 pattern
            # and can be called to trigger migration if needed
            
            # Check if migration already completed
            migrated_usage = self.db.execute(text("""
                SELECT COUNT(*) FROM dashboard_resource_usage
                WHERE meta_data::text LIKE '%migrated_from%resource_management_usage%'
            """)).scalar()
            
            migrated_thresholds = self.db.execute(text("""
                SELECT COUNT(*) FROM dashboard_resource_thresholds
                WHERE meta_data::text LIKE '%migrated_from%resource_thresholds%'
            """)).scalar()
            
            migrated_optimizations = self.db.execute(text("""
                SELECT COUNT(*) FROM dashboard_resource_optimizations
                WHERE meta_data::text LIKE '%migrated_from%resource_optimizations%'
            """)).scalar()
            
            migrated_sharing = self.db.execute(text("""
                SELECT COUNT(*) FROM dashboard_resource_sharing
                WHERE meta_data::text LIKE '%migrated_from%resource_management_sharing%'
            """)).scalar()
            
            migrated_events = self.db.execute(text("""
                SELECT COUNT(*) FROM dashboard_optimization_events
                WHERE meta_data::text LIKE '%migrated_from%optimization_events%'
            """)).scalar()
            
            migrated_counts["resource_usage"] = migrated_usage
            migrated_counts["resource_thresholds"] = migrated_thresholds
            migrated_counts["resource_optimizations"] = migrated_optimizations
            migrated_counts["resource_sharing"] = migrated_sharing
            migrated_counts["optimization_events"] = migrated_events
            
            return migrated_counts
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error checking migration status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking migration status: {str(e)}"
            )
    
    # ==================== HELPER METHODS ====================
    
    def _usage_to_dict(self, usage: DashboardResourceUsage) -> Dict:
        """Convert DashboardResourceUsage to dictionary."""
        return {
            "id": usage.id,
            "resource_id": usage.resource_id,
            "resource_type": usage.resource_type.value if hasattr(usage.resource_type, 'value') else str(usage.resource_type),
            "metric_type": usage.metric_type.value if hasattr(usage.metric_type, 'value') else str(usage.metric_type),
            "value": usage.value,
            "unit": usage.unit,
            "timestamp": usage.timestamp.isoformat() if usage.timestamp else None,
            "meta_data": usage.meta_data,
            "user_id": usage.user_id,
            "project_id": usage.project_id,
            "organization_id": usage.organization_id
        }
    
    def _threshold_to_dict(self, threshold: DashboardResourceThreshold) -> Dict:
        """Convert DashboardResourceThreshold to dictionary."""
        return {
            "id": threshold.id,
            "resource_type": threshold.resource_type.value if hasattr(threshold.resource_type, 'value') else str(threshold.resource_type),
            "metric_type": threshold.metric_type.value if hasattr(threshold.metric_type, 'value') else str(threshold.metric_type),
            "threshold_value": threshold.threshold_value,
            "threshold_type": threshold.threshold_type,
            "action": threshold.action,
            "meta_data": threshold.meta_data,
            "user_id": threshold.user_id,
            "project_id": threshold.project_id,
            "organization_id": threshold.organization_id
        }
    
    def _optimization_to_dict(self, optimization: DashboardResourceOptimization) -> Dict:
        """Convert DashboardResourceOptimization to dictionary."""
        return {
            "id": optimization.id,
            "resource_type": optimization.resource_type.value if hasattr(optimization.resource_type, 'value') else str(optimization.resource_type),
            "metric_type": optimization.metric_type.value if hasattr(optimization.metric_type, 'value') else str(optimization.metric_type),
            "current_value": optimization.current_value,
            "recommended_value": optimization.recommended_value,
            "potential_savings": optimization.potential_savings,
            "confidence_score": optimization.confidence_score,
            "recommendation": optimization.recommendation,
            "status": optimization.status,
            "created_at": optimization.created_at.isoformat() if optimization.created_at else None,
            "applied_at": optimization.applied_at.isoformat() if optimization.applied_at else None,
            "meta_data": optimization.meta_data,
            "user_id": optimization.user_id,
            "project_id": optimization.project_id,
            "organization_id": optimization.organization_id
        }

