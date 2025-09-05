"""
Team Model

This model represents teams within organizations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Team(Base):
    """Model for teams."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    team_type = Column(String(50), nullable=False)  # Department, Project, Committee, Working Group, Advisory
    leader_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    max_members = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leader = relationship("Teacher", back_populates="teams_led")
    members = relationship("TeamMember", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.team_name}, type={self.team_type})>"