"""
Dashboard Core Functionality

This module provides the core functionality for the Faraday AI Dashboard,
including user management, GPT model management, and project organization.
"""

from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json
import os
from .models.user import DashboardUser  # Import directly from user module
from .models.gpt_models import DashboardGPTSubscription, GPTPerformance
from .models.project import DashboardProject
from .models.feedback import Feedback
from .schemas import GPTSubscriptionResponse
from .services.cache_manager import CacheManager
from .services.query_optimizer import QueryOptimizer
from .services.monitoring import MonitoringService, monitor_request

class DashboardCore:
    def __init__(self, db: Session):
        self.db = db
        self.cache = CacheManager(
            redis_url=os.getenv('REDIS_URL'),
            default_ttl=300  # 5 minutes default TTL
        )
        self._metric_cache_ttl = 60  # 1 minute TTL for metrics
        
        # Initialize query optimizers for each model
        self.user_optimizer = QueryOptimizer(db, DashboardUser)
        self.project_optimizer = QueryOptimizer(db, DashboardProject)
        self.gpt_optimizer = QueryOptimizer(db, DashboardGPTSubscription)
        self.performance_optimizer = QueryOptimizer(db, GPTPerformance)
        self.feedback_optimizer = QueryOptimizer(db, Feedback)
        
        # Initialize monitoring service
        self.monitoring = MonitoringService()

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        return self.cache._get_cache_key(prefix, *args)

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if exists."""
        return self.cache.get(key)

    def _set_in_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with timestamp."""
        self.cache.set(key, value, ttl)

    def _invalidate_project_cache(self, project_id: str, user_id: str) -> None:
        """Invalidate project cache."""
        cache_key = self._get_cache_key('project', project_id, user_id)
        self.cache.delete(cache_key)

    def _invalidate_metrics_cache(self, subscription_id: str) -> None:
        """Invalidate metrics cache for a subscription."""
        for key in self.cache._memory_cache.keys():
            if key.startswith(self._get_cache_key('metrics', subscription_id)):
                self.cache.delete(key)

    @lru_cache(maxsize=128)
    def _get_user_cached(self, user_id: str) -> Optional[DashboardUser]:
        """Get user with caching."""
        return self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()

    async def _get_project_cached(self, project_id: str, user_id: str) -> Optional[DashboardProject]:
        """Get project with caching."""
        cache_key = self._get_cache_key('project', project_id, user_id)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        project = self.db.query(DashboardProject).filter(
            DashboardProject.id == project_id,
            DashboardProject.user_id == user_id
        ).first()
        
        if project:
            self._set_in_cache(cache_key, project)
        
        return project

    async def _get_performance_metrics_cached(
        self,
        subscription_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[GPTPerformance]:
        """Get performance metrics with caching."""
        cache_key = self._get_cache_key('metrics', subscription_id, start_date.isoformat(), end_date.isoformat())
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        metrics = self.db.query(GPTPerformance).filter(
            GPTPerformance.subscription_id == subscription_id,
            GPTPerformance.timestamp >= start_date,
            GPTPerformance.timestamp <= end_date
        ).all()

        self._set_in_cache(cache_key, metrics, self._metric_cache_ttl)
        return metrics

    async def get_user_gpt_subscriptions(self, user_id: str) -> List[Dict]:
        """
        Get all GPT subscriptions for a user.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            List of GPT subscriptions with their status and preferences
        """
        try:
            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get all active subscriptions for the user
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.is_active == True
            ).all()

            # Convert to response format
            return [
                GPTSubscriptionResponse.from_orm(sub).dict()
                for sub in subscriptions
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def switch_active_gpt(self, user_id: str, gpt_id: str) -> Dict:
        """
        Switch the active GPT for a user.
        
        Args:
            user_id: The unique identifier for the user
            gpt_id: The ID of the GPT to switch to
            
        Returns:
            Status of the switch operation
        """
        try:
            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the subscription to switch to
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_id == gpt_id
            ).first()

            if not subscription:
                raise HTTPException(status_code=404, detail="GPT subscription not found")

            # Deactivate all other subscriptions
            self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.is_active == True
            ).update({"is_active": False})

            # Activate the selected subscription
            subscription.is_active = True
            subscription.updated_at = datetime.utcnow()
            subscription.last_used = datetime.utcnow()

            self.db.commit()

            return {
                "status": "success",
                "active_gpt": gpt_id,
                "message": f"Successfully switched to GPT {gpt_id}"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def update_gpt_preferences(
        self,
        user_id: str,
        gpt_id: str,
        preferences: Dict
    ) -> Dict:
        """
        Update preferences for a specific GPT subscription.
        
        Args:
            user_id: The unique identifier for the user
            gpt_id: The ID of the GPT to update preferences for
            preferences: The new preferences to set
            
        Returns:
            Updated preferences
        """
        try:
            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the subscription
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_id == gpt_id
            ).first()

            if not subscription:
                raise HTTPException(status_code=404, detail="GPT subscription not found")

            # Update preferences
            subscription.preferences = preferences
            subscription.updated_at = datetime.utcnow()

            self.db.commit()

            return {
                "status": "success",
                "gpt_id": gpt_id,
                "preferences": preferences,
                "message": "Preferences updated successfully"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @monitor_request
    async def get_dashboard_analytics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get analytics data for the dashboard with performance tracking.
        
        Args:
            user_id: The unique identifier for the user
            start_date: Optional start date for analytics
            end_date: Optional end date for analytics
            
        Returns:
            Analytics data including usage statistics and performance metrics
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Set default date range if not provided
            if not start_date:
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = datetime.utcnow()

            # Get usage statistics with efficient queries
            usage_stats = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "request_trends": {},
                "error_distribution": {},
                "peak_usage_times": {}
            }

            # Get performance metrics with efficient aggregation
            performance_metrics = {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "network_usage": 0.0,
                "resource_trends": {},
                "bottleneck_analysis": {},
                "optimization_opportunities": []
            }

            # Get GPT activity with efficient joins
            gpt_activity = {}
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id
            ).all()

            for sub in subscriptions:
                # Get performance metrics for this GPT
                metrics = self.db.query(GPTPerformance).filter(
                    GPTPerformance.subscription_id == sub.id,
                    GPTPerformance.timestamp >= start_date,
                    GPTPerformance.timestamp <= end_date
                ).all()

                # Calculate aggregated metrics
                total_requests = sum(m.usage_count for m in metrics)
                success_rate = sum(1 for m in metrics if m.error_rate < 0.1) / len(metrics) if metrics else 0
                avg_response_time = sum(m.metrics.get("response_time", 0) for m in metrics) / len(metrics) if metrics else 0

                # Track performance metrics
                self.monitoring.track_performance(
                    'gpt_activity',
                    success_rate,
                    {'gpt_id': sub.gpt_id, 'metric': 'success_rate'}
                )
                self.monitoring.track_performance(
                    'gpt_activity',
                    avg_response_time,
                    {'gpt_id': sub.gpt_id, 'metric': 'response_time'}
                )

                gpt_activity[sub.gpt_id] = {
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "average_response_time": avg_response_time,
                    "last_used": sub.last_used,
                    "status": sub.status,
                    "performance_trends": {
                        "response_times": [m.metrics.get("response_time", 0) for m in metrics],
                        "error_rates": [m.error_rate for m in metrics],
                        "usage_patterns": [m.usage_count for m in metrics]
                    }
                }

            # Get project statistics
            projects = self.db.query(DashboardProject).filter(
                DashboardProject.user_id == user_id
            ).all()

            project_stats = {
                "total_projects": len(projects),
                "active_projects": sum(1 for p in projects if p.status == "active"),
                "project_distribution": {},
                "recent_activity": []
            }

            # Calculate project distribution by status
            for project in projects:
                if project.status not in project_stats["project_distribution"]:
                    project_stats["project_distribution"][project.status] = 0
                project_stats["project_distribution"][project.status] += 1

            # Track overall performance metrics
            self.monitoring.track_performance(
                'dashboard_analytics',
                len(projects),
                {'metric': 'total_projects'}
            )
            self.monitoring.track_performance(
                'dashboard_analytics',
                len(subscriptions),
                {'metric': 'total_subscriptions'}
            )

            return {
                "usage_stats": usage_stats,
                "performance_metrics": performance_metrics,
                "gpt_activity": gpt_activity,
                "project_stats": project_stats,
                "period": {
                    "start": start_date,
                    "end": end_date
                }
            }
        except Exception as e:
            self.monitoring.track_error(
                'dashboard_analytics_error',
                str(e),
                {'user_id': user_id, 'start_date': start_date, 'end_date': end_date}
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_projects(
        self,
        user_id: str,
        include_archived: bool = False,
        page: int = 1,
        per_page: int = 20,
        order_by: Optional[str] = None,
        desc_order: bool = False
    ) -> Dict[str, Any]:
        """
        Get all projects associated with a user with pagination.
        
        Args:
            user_id: The unique identifier for the user
            include_archived: Whether to include archived projects
            page: Page number (1-based)
            per_page: Items per page
            order_by: Column to order by
            desc_order: Whether to order in descending order
            
        Returns:
            Dictionary containing paginated projects and metadata
        """
        try:
            # Verify user exists using cache
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Try to get from cache
            cache_key = self._get_cache_key(
                'user_projects',
                user_id,
                str(include_archived),
                str(page),
                str(per_page),
                order_by or '',
                str(desc_order)
            )
            cached_projects = self._get_from_cache(cache_key)
            if cached_projects:
                return cached_projects

            # Build base query
            query = self.db.query(DashboardProject).filter(DashboardProject.user_id == user_id)
            if not include_archived:
                query = query.filter(DashboardProject.status != "archived")

            # Optimize query with joins and select_related
            query = self.project_optimizer.optimize_query(
                query,
                joins=['active_gpt'],
                select_related=['team']
            )

            # Get paginated results
            result = self.project_optimizer.paginate(
                query,
                page=page,
                per_page=per_page,
                order_by=order_by,
                desc_order=desc_order
            )

            # Convert items to response format
            result['items'] = [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "active_gpt_id": project.active_gpt_id,
                    "status": project.status,
                    "created_at": project.created_at,
                    "updated_at": project.updated_at,
                    "team_id": project.team_id,
                    "is_template": project.is_template
                }
                for project in result['items']
            ]

            # Cache the result
            self._set_in_cache(cache_key, result)

            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_project(
        self,
        user_id: str,
        project_data: Dict
    ) -> Dict:
        """
        Create a new project for a user.
        
        Args:
            user_id: The unique identifier for the user
            project_data: The project configuration data
            
        Returns:
            Created project details
        """
        try:
            # Verify user exists using cache
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create new project
            project = DashboardProject(
                user_id=user_id,
                name=project_data.get("name"),
                description=project_data.get("description"),
                active_gpt_id=project_data.get("active_gpt_id"),
                configuration=project_data.get("configuration", {}),
                status=project_data.get("status", "active"),
                team_id=project_data.get("team_id"),
                is_template=project_data.get("is_template", False)
            )

            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)

            # Cache the new project
            self._set_in_cache(
                self._get_cache_key('project', project.id, user_id),
                project
            )

            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "active_gpt_id": project.active_gpt_id,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "team_id": project.team_id,
                "is_template": project.is_template,
                "message": "Project created successfully"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def update_project(
        self,
        user_id: str,
        project_id: str,
        update_data: Dict
    ) -> Dict:
        """
        Update an existing project.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to update
            update_data: The updates to apply
            
        Returns:
            Updated project details
        """
        try:
            # Verify user exists using cache
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project using cache
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Update project fields
            for key, value in update_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)

            project.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(project)

            # Invalidate project cache
            self._invalidate_project_cache(project_id, user_id)

            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "active_gpt_id": project.active_gpt_id,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "team_id": project.team_id,
                "is_template": project.is_template,
                "message": "Project updated successfully"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_project(
        self,
        user_id: str,
        project_id: str
    ) -> Dict:
        """
        Delete a project.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to delete
            
        Returns:
            Status of the deletion operation
        """
        try:
            # Verify user exists using cache
            user = self._get_user_cached(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project using cache
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Delete the project
            self.db.delete(project)
            self.db.commit()

            # Invalidate project cache
            self._invalidate_project_cache(project_id, user_id)

            return {
                "status": "success",
                "project_id": project_id,
                "message": "Project deleted successfully"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_gpt_performance_metrics(
        self,
        user_id: str,
        gpt_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get performance metrics for a specific GPT.
        
        Args:
            user_id: The unique identifier for the user
            gpt_id: The ID of the GPT to get metrics for
            start_date: Optional start date for metrics
            end_date: Optional end date for metrics
            
        Returns:
            Performance metrics for the specified GPT
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the subscription
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_id == gpt_id
            ).first()

            if not subscription:
                raise HTTPException(status_code=404, detail="GPT subscription not found")

            # Set default date range if not provided
            if not start_date:
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = datetime.utcnow()

            # Get performance metrics
            metrics = self.db.query(GPTPerformance).filter(
                GPTPerformance.subscription_id == subscription.id,
                GPTPerformance.timestamp >= start_date,
                GPTPerformance.timestamp <= end_date
            ).all()

            # Calculate aggregated metrics
            response_times = {}
            accuracy_metrics = {}
            usage_patterns = {}
            total_usage = 0
            error_rate = 0.0

            for metric in metrics:
                total_usage += metric.usage_count
                error_rate += metric.error_rate
                if metric.metrics:
                    response_times.update(metric.metrics.get("response_times", {}))
                    accuracy_metrics.update(metric.metrics.get("accuracy_metrics", {}))
                    usage_patterns.update(metric.metrics.get("usage_patterns", {}))

            if metrics:
                error_rate /= len(metrics)

            return {
                "response_times": response_times,
                "accuracy_metrics": accuracy_metrics,
                "usage_patterns": usage_patterns,
                "error_rate": error_rate,
                "total_usage": total_usage,
                "period": {
                    "start": start_date,
                    "end": end_date
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_feedback(
        self,
        user_id: str,
        gpt_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get feedback provided by the user.
        
        Args:
            user_id: The unique identifier for the user
            gpt_id: Optional ID of the GPT to filter feedback by
            start_date: Optional start date for feedback
            end_date: Optional end date for feedback
            
        Returns:
            List of feedback entries
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Build base query
            query = self.db.query(Feedback).filter(
                Feedback.user_id == user_id
            )

            # Apply GPT filter if provided
            if gpt_id:
                query = query.filter(Feedback.gpt_id == gpt_id)

            # Apply date range if provided
            if start_date:
                query = query.filter(Feedback.created_at >= start_date)
            if end_date:
                query = query.filter(Feedback.created_at <= end_date)

            # Get feedback entries
            feedback_entries = query.order_by(Feedback.created_at.desc()).all()

            # Convert to response format
            return [
                {
                    "id": feedback.id,
                    "gpt_id": feedback.gpt_id,
                    "rating": feedback.rating,
                    "comment": feedback.comment,
                    "category": feedback.category,
                    "created_at": feedback.created_at,
                    "updated_at": feedback.updated_at,
                    "metadata": feedback.metadata
                }
                for feedback in feedback_entries
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def submit_feedback(
        self,
        user_id: str,
        gpt_id: str,
        feedback_data: Dict
    ) -> Dict:
        """
        Submit feedback for a GPT.
        
        Args:
            user_id: The unique identifier for the user
            gpt_id: The ID of the GPT to submit feedback for
            feedback_data: The feedback data containing rating, comment, and category
            
        Returns:
            Status of the feedback submission
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Verify GPT subscription exists
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_id == gpt_id
            ).first()
            if not subscription:
                raise HTTPException(status_code=404, detail="GPT subscription not found")

            # Validate feedback data
            required_fields = ["rating", "category"]
            for field in required_fields:
                if field not in feedback_data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required field: {field}"
                    )

            # Create new feedback entry
            feedback = Feedback(
                user_id=user_id,
                gpt_id=gpt_id,
                rating=feedback_data["rating"],
                comment=feedback_data.get("comment", ""),
                category=feedback_data["category"],
                metadata=feedback_data.get("metadata", {})
            )

            # Save to database
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)

            return {
                "status": "success",
                "feedback_id": feedback.id,
                "message": "Feedback submitted successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def archive_project(
        self,
        user_id: str,
        project_id: str,
        archive_reason: Optional[str] = None
    ) -> Dict:
        """
        Archive a project.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to archive
            archive_reason: Optional reason for archiving
            
        Returns:
            Status of the archiving operation
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = self.db.query(DashboardProject).filter(
                DashboardProject.id == project_id,
                DashboardProject.user_id == user_id
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Update project status and metadata
            project.status = "archived"
            project.updated_at = datetime.utcnow()
            
            # Store archiving metadata
            if not project.metadata:
                project.metadata = {}
            project.metadata["archived_at"] = datetime.utcnow().isoformat()
            if archive_reason:
                project.metadata["archive_reason"] = archive_reason

            self.db.commit()

            return {
                "status": "success",
                "project_id": project_id,
                "message": "Project archived successfully"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def create_project_template(
        self,
        user_id: str,
        template_data: Dict
    ) -> Dict:
        """
        Create a new project template.
        
        Args:
            user_id: The unique identifier for the user
            template_data: The template configuration data
            
        Returns:
            Created template details
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create new project template
            template = DashboardProject(
                user_id=user_id,
                name=template_data.get("name"),
                description=template_data.get("description"),
                configuration=template_data.get("configuration", {}),
                status="template",
                is_template=True,
                metadata={
                    "template_type": template_data.get("template_type", "custom"),
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            )

            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)

            return {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "template_type": template.metadata["template_type"],
                "version": template.metadata["version"],
                "created_at": template.created_at,
                "message": "Project template created successfully"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_project_templates(
        self,
        user_id: str,
        template_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get available project templates.
        
        Args:
            user_id: The unique identifier for the user
            template_type: Optional filter for template type
            
        Returns:
            List of available project templates
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Build base query
            query = self.db.query(DashboardProject).filter(
                DashboardProject.user_id == user_id,
                DashboardProject.is_template == True
            )

            # Apply template type filter if provided
            if template_type:
                query = query.filter(DashboardProject.metadata["template_type"].astext == template_type)

            # Get templates
            templates = query.all()

            # Convert to response format
            return [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "template_type": template.metadata.get("template_type", "custom"),
                    "version": template.metadata.get("version", "1.0"),
                    "created_at": template.created_at,
                    "updated_at": template.updated_at
                }
                for template in templates
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_project_sharing_settings(
        self,
        user_id: str,
        project_id: str,
        sharing_settings: Dict
    ) -> Dict:
        """
        Update project sharing settings.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to update
            sharing_settings: The new sharing settings
            
        Returns:
            Updated sharing settings
        """
        try:
            # Verify user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = self.db.query(DashboardProject).filter(
                DashboardProject.id == project_id,
                DashboardProject.user_id == user_id
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Validate sharing settings
            required_fields = ["visibility", "access_level"]
            for field in required_fields:
                if field not in sharing_settings:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required field: {field}"
                    )

            # Update project sharing settings
            if not project.metadata:
                project.metadata = {}
            project.metadata["sharing_settings"] = {
                "visibility": sharing_settings["visibility"],
                "access_level": sharing_settings["access_level"],
                "allowed_users": sharing_settings.get("allowed_users", []),
                "allowed_teams": sharing_settings.get("allowed_teams", []),
                "updated_at": datetime.utcnow().isoformat()
            }
            project.updated_at = datetime.utcnow()

            self.db.commit()

            return {
                "status": "success",
                "project_id": project_id,
                "sharing_settings": project.metadata["sharing_settings"],
                "message": "Project sharing settings updated successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_project_insights(
        self,
        user_id: str,
        project_id: str
    ) -> Dict:
        """
        Get insights and recommendations for a project.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to get insights for
            
        Returns:
            Project insights and recommendations
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Get project performance metrics
            performance_metrics = self.db.query(GPTPerformance).filter(
                GPTPerformance.subscription_id == project.active_gpt_id
            ).order_by(GPTPerformance.timestamp.desc()).limit(100).all()

            # Calculate insights
            insights = {
                "performance_insights": {
                    "average_response_time": 0.0,
                    "success_rate": 0.0,
                    "usage_trend": "stable",
                    "bottlenecks": []
                },
                "resource_insights": {
                    "cpu_utilization": 0.0,
                    "memory_utilization": 0.0,
                    "storage_utilization": 0.0,
                    "resource_trends": {}
                },
                "collaboration_insights": {
                    "team_activity": {},
                    "communication_patterns": {},
                    "collaboration_efficiency": 0.0
                },
                "recommendations": []
            }

            if performance_metrics:
                # Calculate performance metrics
                total_requests = sum(m.usage_count for m in performance_metrics)
                success_rate = sum(1 for m in performance_metrics if m.error_rate < 0.1) / len(performance_metrics)
                avg_response_time = sum(m.metrics.get("response_time", 0) for m in performance_metrics) / len(performance_metrics)

                insights["performance_insights"].update({
                    "average_response_time": avg_response_time,
                    "success_rate": success_rate,
                    "usage_trend": "increasing" if total_requests > 100 else "stable"
                })

                # Track performance metrics
                self.monitoring.track_performance(
                    'project_analytics',
                    success_rate,
                    {'project_id': project_id, 'metric': 'success_rate'}
                )
                self.monitoring.track_performance(
                    'project_analytics',
                    avg_response_time,
                    {'project_id': project_id, 'metric': 'response_time'}
                )

                # Generate recommendations based on metrics
                if success_rate < 0.8:
                    insights["recommendations"].append({
                        "type": "performance",
                        "priority": "high",
                        "message": "Consider optimizing GPT configuration for better success rate",
                        "action": "review_gpt_configuration"
                    })

                if avg_response_time > 2.0:
                    insights["recommendations"].append({
                        "type": "performance",
                        "priority": "medium",
                        "message": "Response times are above optimal levels",
                        "action": "optimize_queries"
                    })

            # Add project-specific insights
            if project.metadata:
                insights["project_insights"] = {
                    "creation_date": project.created_at,
                    "last_updated": project.updated_at,
                    "status": project.status,
                    "template_used": project.metadata.get("template_type", "custom"),
                    "version": project.metadata.get("version", "1.0")
                }

            return insights
        except Exception as e:
            self.monitoring.track_error(
                'project_insights_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id}
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def manage_project_dependencies(
        self,
        user_id: str,
        project_id: str,
        action: str,
        dependency_data: Optional[Dict] = None
    ) -> Dict:
        """
        Manage project dependencies and requirements.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to manage dependencies for
            action: The action to perform (add, remove, update, list)
            dependency_data: Optional data for the dependency operation
            
        Returns:
            Status of the dependency operation
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Initialize dependencies if not present
            if not project.metadata:
                project.metadata = {}
            if "dependencies" not in project.metadata:
                project.metadata["dependencies"] = {}

            # Perform the requested action
            if action == "list":
                return {
                    "status": "success",
                    "dependencies": project.metadata["dependencies"]
                }

            if action in ["add", "update"] and not dependency_data:
                raise HTTPException(
                    status_code=400,
                    detail="Dependency data required for add/update operations"
                )

            if action == "add":
                # Validate dependency data
                required_fields = ["name", "version", "type"]
                for field in required_fields:
                    if field not in dependency_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing required field: {field}"
                        )

                # Add new dependency
                project.metadata["dependencies"][dependency_data["name"]] = {
                    "version": dependency_data["version"],
                    "type": dependency_data["type"],
                    "added_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }

            elif action == "update":
                if dependency_data["name"] not in project.metadata["dependencies"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Dependency {dependency_data['name']} not found"
                    )

                # Update existing dependency
                project.metadata["dependencies"][dependency_data["name"]].update({
                    "version": dependency_data.get("version", project.metadata["dependencies"][dependency_data["name"]]["version"]),
                    "type": dependency_data.get("type", project.metadata["dependencies"][dependency_data["name"]]["type"]),
                    "updated_at": datetime.utcnow().isoformat()
                })

            elif action == "remove":
                if not dependency_data or "name" not in dependency_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Dependency name required for remove operation"
                    )

                if dependency_data["name"] not in project.metadata["dependencies"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Dependency {dependency_data['name']} not found"
                    )

                # Remove dependency
                del project.metadata["dependencies"][dependency_data["name"]]

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {action}"
                )

            # Update project
            project.updated_at = datetime.utcnow()
            self.db.commit()

            # Track dependency management
            self.monitoring.track_performance(
                'dependency_management',
                1,
                {'project_id': project_id, 'action': action}
            )

            return {
                "status": "success",
                "action": action,
                "dependencies": project.metadata["dependencies"],
                "message": f"Dependency {action}ed successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.monitoring.track_error(
                'dependency_management_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id, 'action': action}
            )
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def manage_project_backup(
        self,
        user_id: str,
        project_id: str,
        action: str,
        backup_data: Optional[Dict] = None
    ) -> Dict:
        """
        Manage project backups and versioning.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to manage backups for
            action: The action to perform (create, restore, list, delete)
            backup_data: Optional data for the backup operation
            
        Returns:
            Status of the backup operation
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Initialize backups if not present
            if not project.metadata:
                project.metadata = {}
            if "backups" not in project.metadata:
                project.metadata["backups"] = {}

            # Perform the requested action
            if action == "list":
                return {
                    "status": "success",
                    "backups": project.metadata["backups"]
                }

            if action == "create":
                # Generate backup ID
                backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                # Create backup
                project.metadata["backups"][backup_id] = {
                    "created_at": datetime.utcnow().isoformat(),
                    "version": project.metadata.get("version", "1.0"),
                    "configuration": project.configuration,
                    "status": "active",
                    "size": len(str(project.configuration)),
                    "description": backup_data.get("description", "Automatic backup")
                }

            elif action == "restore":
                if not backup_data or "backup_id" not in backup_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Backup ID required for restore operation"
                    )

                backup_id = backup_data["backup_id"]
                if backup_id not in project.metadata["backups"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Backup {backup_id} not found"
                    )

                # Restore from backup
                backup = project.metadata["backups"][backup_id]
                project.configuration = backup["configuration"]
                project.metadata["version"] = backup["version"]
                project.metadata["last_restored"] = {
                    "backup_id": backup_id,
                    "restored_at": datetime.utcnow().isoformat()
                }

            elif action == "delete":
                if not backup_data or "backup_id" not in backup_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Backup ID required for delete operation"
                    )

                backup_id = backup_data["backup_id"]
                if backup_id not in project.metadata["backups"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Backup {backup_id} not found"
                    )

                # Delete backup
                del project.metadata["backups"][backup_id]

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {action}"
                )

            # Update project
            project.updated_at = datetime.utcnow()
            self.db.commit()

            # Track backup management
            self.monitoring.track_performance(
                'backup_management',
                1,
                {'project_id': project_id, 'action': action}
            )

            return {
                "status": "success",
                "action": action,
                "backups": project.metadata["backups"],
                "message": f"Backup {action}d successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.monitoring.track_error(
                'backup_management_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id, 'action': action}
            )
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def manage_project_notifications(
        self,
        user_id: str,
        project_id: str,
        action: str,
        notification_data: Optional[Dict] = None
    ) -> Dict:
        """
        Manage project notifications and alerts.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to manage notifications for
            action: The action to perform (create, update, delete, list)
            notification_data: Optional data for the notification operation
            
        Returns:
            Status of the notification operation
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Initialize notifications if not present
            if not project.metadata:
                project.metadata = {}
            if "notifications" not in project.metadata:
                project.metadata["notifications"] = {}

            # Perform the requested action
            if action == "list":
                return {
                    "status": "success",
                    "notifications": project.metadata["notifications"]
                }

            if action in ["create", "update"] and not notification_data:
                raise HTTPException(
                    status_code=400,
                    detail="Notification data required for create/update operations"
                )

            if action == "create":
                # Validate notification data
                required_fields = ["type", "condition", "message"]
                for field in required_fields:
                    if field not in notification_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing required field: {field}"
                        )

                # Generate notification ID
                notification_id = f"notif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

                # Create notification
                project.metadata["notifications"][notification_id] = {
                    "type": notification_data["type"],
                    "condition": notification_data["condition"],
                    "message": notification_data["message"],
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "active",
                    "last_triggered": None,
                    "trigger_count": 0,
                    "settings": notification_data.get("settings", {})
                }

            elif action == "update":
                if "notification_id" not in notification_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Notification ID required for update operation"
                    )

                notification_id = notification_data["notification_id"]
                if notification_id not in project.metadata["notifications"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Notification {notification_id} not found"
                    )

                # Update notification
                project.metadata["notifications"][notification_id].update({
                    "type": notification_data.get("type", project.metadata["notifications"][notification_id]["type"]),
                    "condition": notification_data.get("condition", project.metadata["notifications"][notification_id]["condition"]),
                    "message": notification_data.get("message", project.metadata["notifications"][notification_id]["message"]),
                    "settings": notification_data.get("settings", project.metadata["notifications"][notification_id]["settings"]),
                    "updated_at": datetime.utcnow().isoformat()
                })

            elif action == "delete":
                if not notification_data or "notification_id" not in notification_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Notification ID required for delete operation"
                    )

                notification_id = notification_data["notification_id"]
                if notification_id not in project.metadata["notifications"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Notification {notification_id} not found"
                    )

                # Delete notification
                del project.metadata["notifications"][notification_id]

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {action}"
                )

            # Update project
            project.updated_at = datetime.utcnow()
            self.db.commit()

            # Track notification management
            self.monitoring.track_performance(
                'notification_management',
                1,
                {'project_id': project_id, 'action': action}
            )

            return {
                "status": "success",
                "action": action,
                "notifications": project.metadata["notifications"],
                "message": f"Notification {action}d successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.monitoring.track_error(
                'notification_management_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id, 'action': action}
            )
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def manage_project_integrations(
        self,
        user_id: str,
        project_id: str,
        action: str,
        integration_data: Optional[Dict] = None
    ) -> Dict:
        """
        Manage project integrations with external services.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to manage integrations for
            action: The action to perform (add, update, delete, list, test)
            integration_data: Optional data for the integration operation
            
        Returns:
            Status of the integration operation
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Initialize integrations if not present
            if not project.metadata:
                project.metadata = {}
            if "integrations" not in project.metadata:
                project.metadata["integrations"] = {}

            # Perform the requested action
            if action == "list":
                return {
                    "status": "success",
                    "integrations": project.metadata["integrations"]
                }

            if action in ["add", "update", "test"] and not integration_data:
                raise HTTPException(
                    status_code=400,
                    detail="Integration data required for add/update/test operations"
                )

            if action == "add":
                # Validate integration data
                required_fields = ["service", "type", "credentials"]
                for field in required_fields:
                    if field not in integration_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing required field: {field}"
                        )

                # Generate integration ID
                integration_id = f"int_{integration_data['service']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

                # Create integration
                project.metadata["integrations"][integration_id] = {
                    "service": integration_data["service"],
                    "type": integration_data["type"],
                    "credentials": integration_data["credentials"],
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "active",
                    "last_sync": None,
                    "sync_count": 0,
                    "settings": integration_data.get("settings", {})
                }

            elif action == "update":
                if "integration_id" not in integration_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Integration ID required for update operation"
                    )

                integration_id = integration_data["integration_id"]
                if integration_id not in project.metadata["integrations"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Integration {integration_id} not found"
                    )

                # Update integration
                project.metadata["integrations"][integration_id].update({
                    "service": integration_data.get("service", project.metadata["integrations"][integration_id]["service"]),
                    "type": integration_data.get("type", project.metadata["integrations"][integration_id]["type"]),
                    "credentials": integration_data.get("credentials", project.metadata["integrations"][integration_id]["credentials"]),
                    "settings": integration_data.get("settings", project.metadata["integrations"][integration_id]["settings"]),
                    "updated_at": datetime.utcnow().isoformat()
                })

            elif action == "delete":
                if not integration_data or "integration_id" not in integration_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Integration ID required for delete operation"
                    )

                integration_id = integration_data["integration_id"]
                if integration_id not in project.metadata["integrations"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Integration {integration_id} not found"
                    )

                # Delete integration
                del project.metadata["integrations"][integration_id]

            elif action == "test":
                if "integration_id" not in integration_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Integration ID required for test operation"
                    )

                integration_id = integration_data["integration_id"]
                if integration_id not in project.metadata["integrations"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Integration {integration_id} not found"
                    )

                # Test integration (placeholder for actual test logic)
                test_result = {
                    "status": "success",
                    "message": "Integration test successful",
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Update last test result
                project.metadata["integrations"][integration_id]["last_test"] = test_result

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {action}"
                )

            # Update project
            project.updated_at = datetime.utcnow()
            self.db.commit()

            # Track integration management
            self.monitoring.track_performance(
                'integration_management',
                1,
                {'project_id': project_id, 'action': action}
            )

            return {
                "status": "success",
                "action": action,
                "integrations": project.metadata["integrations"],
                "message": f"Integration {action}d successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.monitoring.track_error(
                'integration_management_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id, 'action': action}
            )
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def manage_project_collaboration(
        self,
        user_id: str,
        project_id: str,
        action: str,
        collaboration_data: Optional[Dict] = None
    ) -> Dict:
        """
        Manage project collaboration and team management.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to manage collaboration for
            action: The action to perform (add_member, remove_member, update_role, list_members)
            collaboration_data: Optional data for the collaboration operation
            
        Returns:
            Status of the collaboration operation
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Initialize collaboration settings if not present
            if not project.metadata:
                project.metadata = {}
            if "collaboration" not in project.metadata:
                project.metadata["collaboration"] = {
                    "members": {},
                    "roles": {},
                    "permissions": {},
                    "activity_log": []
                }

            # Perform the requested action
            if action == "list_members":
                return {
                    "status": "success",
                    "members": project.metadata["collaboration"]["members"],
                    "roles": project.metadata["collaboration"]["roles"]
                }

            if action in ["add_member", "update_role"] and not collaboration_data:
                raise HTTPException(
                    status_code=400,
                    detail="Collaboration data required for add_member/update_role operations"
                )

            if action == "add_member":
                # Validate member data
                required_fields = ["member_id", "role", "permissions"]
                for field in required_fields:
                    if field not in collaboration_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing required field: {field}"
                        )

                member_id = collaboration_data["member_id"]
                if member_id in project.metadata["collaboration"]["members"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Member {member_id} already exists"
                    )

                # Add new member
                project.metadata["collaboration"]["members"][member_id] = {
                    "role": collaboration_data["role"],
                    "permissions": collaboration_data["permissions"],
                    "joined_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }

                # Log activity
                project.metadata["collaboration"]["activity_log"].append({
                    "type": "member_added",
                    "member_id": member_id,
                    "role": collaboration_data["role"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_by": user_id
                })

            elif action == "update_role":
                if "member_id" not in collaboration_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Member ID required for update_role operation"
                    )

                member_id = collaboration_data["member_id"]
                if member_id not in project.metadata["collaboration"]["members"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Member {member_id} not found"
                    )

                # Update member role and permissions
                project.metadata["collaboration"]["members"][member_id].update({
                    "role": collaboration_data.get("role", project.metadata["collaboration"]["members"][member_id]["role"]),
                    "permissions": collaboration_data.get("permissions", project.metadata["collaboration"]["members"][member_id]["permissions"]),
                    "updated_at": datetime.utcnow().isoformat()
                })

                # Log activity
                project.metadata["collaboration"]["activity_log"].append({
                    "type": "role_updated",
                    "member_id": member_id,
                    "new_role": collaboration_data.get("role"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_by": user_id
                })

            elif action == "remove_member":
                if not collaboration_data or "member_id" not in collaboration_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Member ID required for remove_member operation"
                    )

                member_id = collaboration_data["member_id"]
                if member_id not in project.metadata["collaboration"]["members"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Member {member_id} not found"
                    )

                # Remove member
                del project.metadata["collaboration"]["members"][member_id]

                # Log activity
                project.metadata["collaboration"]["activity_log"].append({
                    "type": "member_removed",
                    "member_id": member_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_by": user_id
                })

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {action}"
                )

            # Update project
            project.updated_at = datetime.utcnow()
            self.db.commit()

            # Track collaboration management
            self.monitoring.track_performance(
                'collaboration_management',
                1,
                {'project_id': project_id, 'action': action}
            )

            return {
                "status": "success",
                "action": action,
                "collaboration": project.metadata["collaboration"],
                "message": f"Collaboration {action} completed successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            self.monitoring.track_error(
                'collaboration_management_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id, 'action': action}
            )
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_project_analytics(
        self,
        user_id: str,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """
        Get comprehensive project analytics and reports.
        
        Args:
            user_id: The unique identifier for the user
            project_id: The ID of the project to get analytics for
            start_date: Optional start date for analytics
            end_date: Optional end date for analytics
            metrics: Optional list of specific metrics to retrieve
            
        Returns:
            Project analytics and reports
        """
        try:
            # Track resource usage
            self.monitoring.track_resource_usage()

            # Verify user exists
            user = self._get_user_cached(user_id)
            if not user:
                self.monitoring.track_error(
                    'user_not_found',
                    f"User {user_id} not found",
                    {'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="User not found")

            # Get the project with caching
            project = await self._get_project_cached(project_id, user_id)
            if not project:
                self.monitoring.track_error(
                    'project_not_found',
                    f"Project {project_id} not found",
                    {'project_id': project_id, 'user_id': user_id}
                )
                raise HTTPException(status_code=404, detail="Project not found")

            # Set default date range if not provided
            if not start_date:
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = datetime.utcnow()

            # Try to get analytics from cache
            cache_key = self._get_cache_key(
                'analytics',
                project_id,
                start_date.isoformat(),
                end_date.isoformat(),
                '_'.join(metrics) if metrics else 'all'
            )
            cached_analytics = self._get_from_cache(cache_key)
            if cached_analytics:
                return cached_analytics

            # Initialize analytics data
            analytics = {
                "summary": {
                    "total_requests": 0,
                    "success_rate": 0.0,
                    "average_response_time": 0.0,
                    "active_users": 0,
                    "resource_utilization": 0.0
                },
                "performance_metrics": {
                    "response_times": [],
                    "error_rates": [],
                    "throughput": [],
                    "latency": []
                },
                "usage_patterns": {
                    "peak_hours": {},
                    "user_activity": {},
                    "feature_usage": {}
                },
                "collaboration_metrics": {
                    "team_activity": {},
                    "member_contributions": {},
                    "communication_stats": {}
                },
                "resource_metrics": {
                    "cpu_usage": [],
                    "memory_usage": [],
                    "storage_usage": [],
                    "network_usage": []
                },
                "trends": {
                    "daily": {},
                    "weekly": {},
                    "monthly": {}
                }
            }

            # Get performance metrics with caching
            performance_data = await self._get_performance_metrics_cached(
                project.active_gpt_id,
                start_date,
                end_date
            )

            if performance_data:
                # Calculate performance metrics
                total_requests = sum(p.usage_count for p in performance_data)
                success_rate = sum(1 for p in performance_data if p.error_rate < 0.1) / len(performance_data)
                avg_response_time = sum(p.metrics.get("response_time", 0) for p in performance_data) / len(performance_data)

                analytics["summary"].update({
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "average_response_time": avg_response_time
                })

                # Track performance metrics
                self.monitoring.track_performance(
                    'project_analytics',
                    success_rate,
                    {'project_id': project_id, 'metric': 'success_rate'}
                )
                self.monitoring.track_performance(
                    'project_analytics',
                    avg_response_time,
                    {'project_id': project_id, 'metric': 'response_time'}
                )

                # Collect detailed metrics
                for metric in performance_data:
                    timestamp = metric.timestamp.isoformat()
                    
                    # Response times
                    analytics["performance_metrics"]["response_times"].append({
                        "timestamp": timestamp,
                        "value": metric.metrics.get("response_time", 0)
                    })

                    # Error rates
                    analytics["performance_metrics"]["error_rates"].append({
                        "timestamp": timestamp,
                        "value": metric.error_rate
                    })

                    # Resource usage
                    if "resource_usage" in metric.metrics:
                        for resource, usage in metric.metrics["resource_usage"].items():
                            analytics["resource_metrics"][f"{resource}_usage"].append({
                                "timestamp": timestamp,
                                "value": usage
                            })

            # Get collaboration metrics if available
            if project.metadata and "collaboration" in project.metadata:
                members = project.metadata["collaboration"]["members"]
                activity_log = project.metadata["collaboration"]["activity_log"]

                # Calculate member activity
                for member_id, member_data in members.items():
                    member_activities = [
                        log for log in activity_log 
                        if log["member_id"] == member_id and 
                        start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date
                    ]

                    analytics["collaboration_metrics"]["member_contributions"][member_id] = {
                        "activity_count": len(member_activities),
                        "last_active": member_activities[-1]["timestamp"] if member_activities else None,
                        "role": member_data["role"]
                    }

            # Calculate trends
            if performance_data:
                # Group by day
                daily_data = {}
                for metric in performance_data:
                    day = metric.timestamp.date().isoformat()
                    if day not in daily_data:
                        daily_data[day] = []
                    daily_data[day].append(metric)

                # Calculate daily averages
                for day, metrics in daily_data.items():
                    analytics["trends"]["daily"][day] = {
                        "requests": sum(m.usage_count for m in metrics),
                        "error_rate": sum(m.error_rate for m in metrics) / len(metrics),
                        "response_time": sum(m.metrics.get("response_time", 0) for m in metrics) / len(metrics)
                    }

            # Cache the analytics
            self._set_in_cache(cache_key, analytics, self._metric_cache_ttl)

            return analytics
        except Exception as e:
            self.monitoring.track_error(
                'project_analytics_error',
                str(e),
                {'user_id': user_id, 'project_id': project_id}
            )
            raise HTTPException(status_code=500, detail=str(e)) 