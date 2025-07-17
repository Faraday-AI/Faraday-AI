"""
Dashboard Services

This module provides the service layer for the Faraday AI Dashboard,
handling business logic and data operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
import uuid
import secrets
import json

from .models.user import DashboardUser
from .models.project import DashboardProject
from .models.gpt_models import (
    DashboardGPTSubscription,
    GPTVersion,
    GPTContext,
    GPTPerformance,
    GPTDefinition,
    GPTUsage,
    GPTIntegration,
    GPTAnalytics,
    GPTFeedback
)
from .schemas import (
    UserCreate,
    UserUpdate,
    GPTSubscriptionCreate,
    GPTSubscriptionUpdate,
    ProjectCreate,
    ProjectUpdate,
    FeedbackCreate,
    CategoryCreate,
    GPTVersionCreate,
    WebhookCreate,
    TeamCreate,
    TeamMemberCreate,
    CommentCreate
)

class DashboardServices:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            id=f"usr-{uuid.uuid4()}",
            email=user_data.email,
            subscription_status=user_data.subscription_status,
            role=user_data.role,
            api_key=secrets.token_urlsafe(32),
            last_api_key_rotation=datetime.utcnow()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def get_user(self, user_id: str) -> User:
        """Get a user by ID."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """Update an existing user."""
        user = await self.get_user(user_id)
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def rotate_api_key(self, user_id: str) -> User:
        """Rotate a user's API key."""
        user = await self.get_user(user_id)
        user.api_key = secrets.token_urlsafe(32)
        user.last_api_key_rotation = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    async def create_gpt_subscription(
        self,
        user_id: str,
        subscription_data: GPTSubscriptionCreate
    ) -> DashboardGPTSubscription:
        """Create a new GPT subscription for a user."""
        user = await self.get_user(user_id)
        
        # Check if subscription already exists
        existing = self.db.query(DashboardGPTSubscription).filter(
            DashboardGPTSubscription.user_id == user_id,
            DashboardGPTSubscription.gpt_id == subscription_data.gpt_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="GPT subscription already exists"
            )

        subscription = DashboardGPTSubscription(
            id=f"sub-{uuid.uuid4()}",
            user_id=user_id,
            gpt_id=subscription_data.gpt_id,
            status=subscription_data.status,
            preferences=subscription_data.preferences.dict(),
            version=subscription_data.version
        )
        
        # Add categories if provided
        if subscription_data.categories:
            categories = self.db.query(Category).filter(
                Category.id.in_(subscription_data.categories)
            ).all()
            subscription.categories = categories
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    async def update_gpt_subscription(
        self,
        user_id: str,
        subscription_id: str,
        subscription_data: GPTSubscriptionUpdate
    ) -> DashboardGPTSubscription:
        """Update an existing GPT subscription."""
        subscription = self.db.query(DashboardGPTSubscription).filter(
            DashboardGPTSubscription.id == subscription_id,
            DashboardGPTSubscription.user_id == user_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="GPT subscription not found"
            )

        for field, value in subscription_data.dict(exclude_unset=True).items():
            if field == "categories":
                categories = self.db.query(Category).filter(
                    Category.id.in_(value)
                ).all()
                subscription.categories = categories
            else:
                setattr(subscription, field, value)
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    async def share_gpt(
        self,
        user_id: str,
        subscription_id: str,
        shared_with_user_id: str,
        permissions: Dict[str, bool]
    ) -> Dict:
        """Share a GPT subscription with another user."""
        subscription = self.db.query(DashboardGPTSubscription).filter(
            DashboardGPTSubscription.id == subscription_id,
            DashboardGPTSubscription.user_id == user_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="GPT subscription not found"
            )

        # Add sharing relationship
        self.db.execute(
            gpt_sharing.insert().values(
                gpt_id=subscription_id,
                shared_with_user_id=shared_with_user_id,
                permissions=permissions
            )
        )
        self.db.commit()
        
        return {
            "status": "success",
            "message": f"GPT shared with user {shared_with_user_id}"
        }

    async def create_gpt_version(
        self,
        user_id: str,
        subscription_id: str,
        version_data: GPTVersionCreate
    ) -> GPTVersion:
        """Create a new version for a GPT subscription."""
        subscription = self.db.query(DashboardGPTSubscription).filter(
            DashboardGPTSubscription.id == subscription_id,
            DashboardGPTSubscription.user_id == user_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="GPT subscription not found"
            )

        # Deactivate current active version if exists
        if version_data.is_active:
            self.db.query(GPTVersion).filter(
                GPTVersion.subscription_id == subscription_id,
                GPTVersion.is_active == True
            ).update({"is_active": False})

        version = GPTVersion(
            id=f"ver-{uuid.uuid4()}",
            subscription_id=subscription_id,
            version_number=version_data.version_number,
            configuration=version_data.configuration,
            is_active=version_data.is_active
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    async def create_webhook(
        self,
        user_id: str,
        subscription_id: str,
        webhook_data: WebhookCreate
    ) -> Webhook:
        """Create a new webhook for a GPT subscription."""
        subscription = self.db.query(DashboardGPTSubscription).filter(
            DashboardGPTSubscription.id == subscription_id,
            DashboardGPTSubscription.user_id == user_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="GPT subscription not found"
            )

        webhook = Webhook(
            id=f"wh-{uuid.uuid4()}",
            subscription_id=subscription_id,
            url=webhook_data.url,
            events=webhook_data.events,
            is_active=webhook_data.is_active
        )
        
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        return webhook

    async def create_team(
        self,
        user_id: str,
        team_data: TeamCreate
    ) -> Team:
        """Create a new team."""
        team = Team(
            id=f"team-{uuid.uuid4()}",
            name=team_data.name,
            description=team_data.description
        )
        
        self.db.add(team)
        
        # Add creator as team owner
        team_member = TeamMember(
            id=f"tm-{uuid.uuid4()}",
            team_id=team.id,
            user_id=user_id,
            role="owner"
        )
        
        self.db.add(team_member)
        self.db.commit()
        self.db.refresh(team)
        return team

    async def add_team_member(
        self,
        team_id: str,
        member_data: TeamMemberCreate
    ) -> TeamMember:
        """Add a member to a team."""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Check if user is already a member
        existing = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == member_data.user_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User is already a team member"
            )

        member = TeamMember(
            id=f"tm-{uuid.uuid4()}",
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role
        )
        
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    async def create_project(
        self,
        user_id: str,
        project_data: ProjectCreate
    ) -> DashboardProject:
        """Create a new project."""
        project = DashboardProject(
            id=f"proj-{uuid.uuid4()}",
            user_id=user_id,
            name=project_data.name,
            description=project_data.description,
            active_gpt_id=project_data.active_gpt_id,
            configuration=project_data.configuration,
            status=project_data.status,
            team_id=project_data.team_id,
            is_template=project_data.is_template
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    async def add_project_comment(
        self,
        project_id: str,
        user_id: str,
        comment_data: CommentCreate
    ) -> Comment:
        """Add a comment to a project."""
        project = self.db.query(DashboardProject).filter(DashboardProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        comment = Comment(
            id=f"cmt-{uuid.uuid4()}",
            project_id=project_id,
            user_id=user_id,
            content=comment_data.content
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    async def record_gpt_performance(
        self,
        subscription_id: str,
        metrics: Dict
    ) -> GPTPerformance:
        """Record performance metrics for a GPT subscription."""
        performance = GPTPerformance(
            id=f"perf-{uuid.uuid4()}",
            subscription_id=subscription_id,
            metrics=metrics,
            timestamp=datetime.utcnow(),
            response_time=metrics.get("response_time", 0),
            error_rate=metrics.get("error_rate", 0),
            usage_count=metrics.get("usage_count", 0)
        )
        
        self.db.add(performance)
        self.db.commit()
        self.db.refresh(performance)
        return performance

    async def submit_feedback(
        self,
        user_id: str,
        feedback_data: FeedbackCreate
    ) -> Feedback:
        """Submit feedback for a GPT."""
        feedback = Feedback(
            id=f"fb-{uuid.uuid4()}",
            user_id=user_id,
            gpt_id=feedback_data.gpt_id,
            feedback_type=feedback_data.feedback_type,
            content=feedback_data.content,
            rating=feedback_data.rating
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    async def record_dashboard_analytics(
        self,
        user_id: str,
        metrics: Dict,
        period: str = "daily"
    ) -> DashboardAnalytics:
        """Record analytics data for the dashboard."""
        analytics = DashboardAnalytics(
            id=f"analytics-{uuid.uuid4()}",
            user_id=user_id,
            metrics=metrics,
            timestamp=datetime.utcnow(),
            period=period,
            gpt_usage=metrics.get("gpt_usage", {}),
            api_calls=metrics.get("api_calls", {}),
            error_logs=metrics.get("error_logs", [])
        )
        
        self.db.add(analytics)
        self.db.commit()
        self.db.refresh(analytics)
        return analytics

    async def get_dashboard_analytics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "daily"
    ) -> List[DashboardAnalytics]:
        """Get analytics data for the dashboard."""
        query = self.db.query(DashboardAnalytics).filter(
            DashboardAnalytics.user_id == user_id,
            DashboardAnalytics.period == period
        )
        
        if start_date:
            query = query.filter(DashboardAnalytics.timestamp >= start_date)
        if end_date:
            query = query.filter(DashboardAnalytics.timestamp <= end_date)
        
        return query.order_by(DashboardAnalytics.timestamp.desc()).all()

    async def log_audit_event(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict
    ) -> AuditLog:
        """Log an audit event."""
        log = AuditLog(
            id=f"audit-{uuid.uuid4()}",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    async def create_category(
        self,
        category_data: CategoryCreate
    ) -> Category:
        """Create a new GPT category."""
        category = Category(
            id=f"cat-{uuid.uuid4()}",
            name=category_data.name,
            description=category_data.description
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    async def get_category_gpts(
        self,
        category_id: str
    ) -> List[DashboardGPTSubscription]:
        """Get all GPTs in a category."""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return category.gpts 