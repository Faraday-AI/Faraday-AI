"""
Team Models

This module defines the DashboardTeam and DashboardTeamMember models for team management functionality.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class DashboardTeam(Base):
    """Model for dashboard teams."""
    __tablename__ = "dashboard_teams"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON)

    # Relationships
    organization = relationship("Organization", back_populates="dashboard_teams")
    projects = relationship("DashboardProject", back_populates="team")
    members = relationship("DashboardTeamMember", back_populates="team")

dashboard_team_members = Table(
    "dashboard_team_members",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("dashboard_teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("dashboard_users.id"), primary_key=True),
    Column("role", String, default="member"),
    Column("joined_at", DateTime, default=datetime.utcnow),
    Column("last_active", DateTime),
    extend_existing=True
)

class DashboardTeamMember(Base):
    """Model for dashboard team members."""
    __tablename__ = "dashboard_team_members"
    __table_args__ = {'extend_existing': True}

    team_id = Column(Integer, ForeignKey("dashboard_teams.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), primary_key=True)
    role = Column(String, default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    status = Column(String, default="active")

    # Relationships
    team = relationship("DashboardTeam", back_populates="members")
    user = relationship("DashboardUser", back_populates="dashboard_team_memberships") 