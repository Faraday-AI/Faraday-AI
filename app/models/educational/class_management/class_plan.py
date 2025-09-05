"""
Class Plan Model

This model represents class plans and lesson planning.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class ClassPlan(Base):
    """Model for class plans."""
    __tablename__ = "class_plans"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    plan_type = Column(String(50), nullable=False)  # Daily, Weekly, Monthly, Unit, Semester
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    educational_class = relationship("EducationalClass", back_populates="plans")

    def __repr__(self):
        return f"<ClassPlan(id={self.id}, class_id={self.class_id}, title={self.title})>"