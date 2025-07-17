"""
Project models for the dashboard.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.shared_base import SharedBase as Base

class DashboardProject(Base):
    """Model for dashboard projects."""
    __tablename__ = "dashboard_projects"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    active_gpt_id = Column(String)
    configuration = Column(JSON)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    team_id = Column(Integer, ForeignKey("dashboard_teams.id"))
    is_template = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Relationships
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="projects")
    team = relationship("app.dashboard.models.team.DashboardTeam", back_populates="projects")
    organization = relationship("Organization", back_populates="projects")
    comments = relationship("Comment", back_populates="project")
    gpt_definitions = relationship("app.dashboard.models.gpt_models.GPTDefinition", back_populates="project")
    dashboard_widgets = relationship("app.dashboard.models.dashboard_models.DashboardWidget", back_populates="project")
    dashboards = relationship("app.dashboard.models.dashboard_models.Dashboard", back_populates="project")
    dashboard_shares = relationship("app.dashboard.models.dashboard_models.DashboardShare", back_populates="project")
    dashboard_filters = relationship("app.dashboard.models.dashboard_models.DashboardFilter", back_populates="project")
    context_interactions = relationship("app.models.gpt.context.models.ContextInteraction", back_populates="project")
    shared_contexts = relationship("app.models.gpt.context.models.SharedContext", back_populates="shared_with_project")
    context_summaries = relationship("app.models.gpt.context.models.ContextSummary", back_populates="project")
    context_backups = relationship("app.models.gpt.context.models.ContextBackup", back_populates="project") 