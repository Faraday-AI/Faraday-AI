"""
Team Management Models

This module defines the database models for team management and collaboration.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base
from app.models.mixins import StatusMixin, MetadataMixin, AuditableModel

class Team(Base, StatusMixin, MetadataMixin):
    """Model for team collaboration."""
    __tablename__ = "teams"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    projects = relationship("OrganizationProject", back_populates="team")
    organization_projects = relationship("OrganizationProject", back_populates="team", overlaps="projects")
    members = relationship("TeamMember", back_populates="team")
    feedback_projects = relationship("FeedbackProject", back_populates="team")

class TeamMember(Base, StatusMixin, MetadataMixin):
    """Model for team membership."""
    __tablename__ = "team_members"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    permissions = Column(JSON, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships") 