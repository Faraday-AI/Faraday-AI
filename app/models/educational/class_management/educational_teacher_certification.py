"""
Educational Teacher Certification Model

This model tracks teacher certifications specifically for educational purposes.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class EducationalTeacherCertification(Base):
    """Model for educational teacher certifications."""
    __tablename__ = "educational_teacher_certifications"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    certification_type = Column(String(100), nullable=False)  # Teaching License, PE Certification, etc.
    certification_number = Column(String(100), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    issuing_authority = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="educational_certifications")

    def __repr__(self):
        return f"<EducationalTeacherCertification(id={self.id}, teacher_id={self.teacher_id}, type={self.certification_type})>"