"""
Department Member Model

This model represents members of departments.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class DepartmentMember(Base):
    """Model for department members."""
    __tablename__ = "department_members"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    role = Column(String(100), nullable=False)  # Member, Senior Member, Lead, Coordinator
    join_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="members")
    teacher = relationship("Teacher", back_populates="department_memberships")

    def __repr__(self):
        return f"<DepartmentMember(id={self.id}, department_id={self.department_id}, teacher_id={self.teacher_id})>"