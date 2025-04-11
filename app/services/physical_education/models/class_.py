from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

class Class(Base):
    """Model for physical education classes."""
    __tablename__ = "classes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    max_students = Column(Integer, nullable=False)
    schedule = Column(JSON, nullable=False)  # Contains day, time, duration
    location = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routines = relationship("Routine", back_populates="class_", cascade="all, delete-orphan")
    students = relationship("ClassStudent", back_populates="class_", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Class {self.name} - {self.grade_level}>"

class ClassStudent(Base):
    """Model for student enrollment in classes."""
    __tablename__ = "class_students"

    id = Column(String, primary_key=True)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("Class", back_populates="students")
    student = relationship("Student", back_populates="classes")

    def __repr__(self):
        return f"<ClassStudent {self.class_id} - {self.student_id}>" 