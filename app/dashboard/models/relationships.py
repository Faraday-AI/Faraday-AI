"""
Relationship definitions for dashboard models.
This file helps break circular dependencies between models.
"""

from sqlalchemy.orm import relationship
from .context import GPTContext, ContextTemplate
from .gpt_models import GPTDefinition
from .user import DashboardUser
from .association_tables import dashboard_context_gpts

# Add relationships to DashboardUser model
DashboardUser.contexts = relationship("app.dashboard.models.context.GPTContext", back_populates="user")
DashboardUser.context_templates = relationship("app.dashboard.models.context.ContextTemplate", back_populates="created_by_user")

# Add relationships to GPTDefinition model
GPTDefinition.contexts = relationship("app.dashboard.models.context.GPTContext", secondary=dashboard_context_gpts, back_populates="active_gpts") 