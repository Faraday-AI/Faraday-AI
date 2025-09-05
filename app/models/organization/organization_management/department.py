"""
Department Model

This model represents departments within an organization.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Department(Base):
    """Model for departments."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    department_type = Column(String(50), nullable=False)  # Academic, Administrative, Support, Research, Student Services
    head_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    head_teacher = relationship("Teacher", back_populates="departments_headed")
    members = relationship("DepartmentMember", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, type={self.department_type})>"