"""
Microsoft OAuth Token Storage Model

This module defines the model for storing Microsoft OAuth tokens for users.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin

class MicrosoftOAuthToken(SharedBase, TimestampedMixin):
    """Model for storing Microsoft OAuth tokens for users."""
    
    __tablename__ = "microsoft_oauth_tokens"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Token fields
    access_token = Column(Text, nullable=False)  # Encrypted access token
    refresh_token = Column(Text, nullable=True)  # Encrypted refresh token
    id_token = Column(Text, nullable=True)  # ID token if available
    
    # Token metadata
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime, nullable=False)  # When the access token expires
    scope = Column(Text, nullable=True)  # Granted scopes
    
    # Microsoft user info
    microsoft_id = Column(String(255), nullable=True, index=True)  # Microsoft user ID
    microsoft_email = Column(String(255), nullable=True, index=True)  # Microsoft email
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)  # Last time token was used
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("app.models.core.user.User", backref="microsoft_oauth_token", foreign_keys=[user_id])

class BetaMicrosoftOAuthToken(SharedBase, TimestampedMixin):
    """Model for storing Microsoft OAuth tokens for beta teachers."""
    
    __tablename__ = "beta_microsoft_oauth_tokens"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id"), nullable=False, unique=True, index=True)
    
    # Token fields
    access_token = Column(Text, nullable=False)  # Encrypted access token
    refresh_token = Column(Text, nullable=True)  # Encrypted refresh token
    id_token = Column(Text, nullable=True)  # ID token if available
    
    # Token metadata
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime, nullable=False)  # When the access token expires
    scope = Column(Text, nullable=True)  # Granted scopes
    
    # Microsoft user info
    microsoft_id = Column(String(255), nullable=True, index=True)  # Microsoft user ID
    microsoft_email = Column(String(255), nullable=True, index=True)  # Microsoft email
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)  # Last time token was used
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", backref="microsoft_oauth_token", foreign_keys=[teacher_id])

