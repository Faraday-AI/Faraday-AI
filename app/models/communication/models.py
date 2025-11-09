"""
Communication Models

This module defines the database models for communication records including
email, SMS, and translated messages for parent, student, teacher, and administrator communication.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean, Index
from sqlalchemy.orm import relationship
import enum

from app.models.shared_base import SharedBase


class CommunicationType(str, enum.Enum):
    """Types of communication."""
    PARENT = "parent"
    STUDENT = "student"
    TEACHER = "teacher"
    ADMINISTRATOR = "administrator"
    ASSIGNMENT = "assignment"
    BULK = "bulk"


class CommunicationChannel(str, enum.Enum):
    """Communication channels."""
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"


class CommunicationStatus(str, enum.Enum):
    """Communication delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"


class MessageType(str, enum.Enum):
    """Types of messages."""
    PROGRESS_UPDATE = "progress_update"
    ATTENDANCE_CONCERN = "attendance_concern"
    ACHIEVEMENT = "achievement"
    GENERAL = "general"
    ASSIGNMENT = "assignment"
    NOTIFICATION = "notification"


class CommunicationRecord(SharedBase):
    """Model for storing communication records."""
    __tablename__ = "communication_records"
    __table_args__ = (
        Index('idx_comm_student', 'student_id'),
        Index('idx_comm_teacher', 'teacher_id'),
        Index('idx_comm_type', 'communication_type'),
        Index('idx_comm_status', 'status'),
        Index('idx_comm_created', 'created_at'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Communication metadata
    communication_type = Column(Enum(CommunicationType, name='communication_type_enum'), nullable=False)
    message_type = Column(Enum(MessageType, name='message_type_enum'), nullable=True)
    channels = Column(JSON, nullable=False)  # List of channels used ["email", "sms", "both"]
    
    # Recipient information
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_name = Column(String(100), nullable=True)
    
    # Message content
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    original_message = Column(Text, nullable=True)  # Original before translation
    
    # Translation information
    source_language = Column(String(10), default="en")
    target_language = Column(String(10), nullable=True)
    translation_applied = Column(Boolean, default=False)
    
    # Delivery information
    status = Column(Enum(CommunicationStatus, name='communication_status_enum'), default=CommunicationStatus.PENDING)
    delivery_results = Column(JSON, nullable=True)  # Store delivery results per channel
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Sender information
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sender_email = Column(String(255), nullable=True)
    
    # Additional metadata
    communication_metadata = Column(JSON, nullable=True)  # Additional data like assignment_id, etc.
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps (SharedBase doesn't provide these automatically)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", foreign_keys=[student_id])
    teacher = relationship("app.models.core.user.User", foreign_keys=[teacher_id])
    sender = relationship("app.models.core.user.User", foreign_keys=[sender_id])


class AssignmentTranslation(SharedBase):
    """Model for storing assignment translations."""
    __tablename__ = "assignment_translations"
    __table_args__ = (
        Index('idx_assn_trans_assignment', 'assignment_id'),
        Index('idx_assn_trans_student', 'student_id'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Translation information
    source_language = Column(String(10), nullable=True)  # Auto-detected if not provided
    target_language = Column(String(10), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    
    # Delivery information
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    status = Column(Enum(CommunicationStatus, name='translation_status_enum'), default=CommunicationStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = relationship("app.models.educational.base.assignment.Assignment")
    student = relationship("app.models.physical_education.student.models.Student")


class SubmissionTranslation(SharedBase):
    """Model for storing student submission translations."""
    __tablename__ = "submission_translations"
    __table_args__ = (
        Index('idx_sub_trans_assignment', 'assignment_id'),
        Index('idx_sub_trans_student', 'student_id'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Translation information
    source_language = Column(String(10), nullable=False)  # Detected or provided
    target_language = Column(String(10), nullable=False, default="en")
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    
    # Translation metadata
    confidence = Column(String(20), nullable=True)  # Language detection confidence
    translated_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = relationship("app.models.educational.base.assignment.Assignment")
    student = relationship("app.models.physical_education.student.models.Student")

