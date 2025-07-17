"""
Video Processor Models

This module defines video processing models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

class Video(BaseModelMixin, TimestampMixin):
    """Model for videos."""
    __tablename__ = "videos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    video_date = Column(DateTime, nullable=False)
    video_type = Column(String(50), nullable=False)
    video_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    student = relationship("Student", back_populates="videos")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="videos")
    frames = relationship("VideoFrame", back_populates="video")

class VideoFrame(BaseModelMixin, TimestampMixin):
    """Model for video frames."""
    __tablename__ = "video_frames"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    frame_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    video = relationship("Video", back_populates="frames")
    keypoints = relationship("Keypoint", back_populates="frame")

class Keypoint(BaseModelMixin, TimestampMixin):
    """Model for keypoints."""
    __tablename__ = "keypoints"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    frame_id = Column(Integer, ForeignKey("video_frames.id"), nullable=False)
    keypoint_type = Column(String(50), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    confidence = Column(Float)
    keypoint_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    frame = relationship("VideoFrame", back_populates="keypoints")

class VideoAnalysis(BaseModelMixin, TimestampMixin):
    """Model for video analysis results."""
    
    __tablename__ = "video_analyses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    video_url = Column(String(255), nullable=False)
    analysis_type = Column(String(50), nullable=False)
    analysis_results = Column(JSON)
    status = Column(String(20), default="PENDING")
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="video_analyses")

class VideoAnalysisCreate(BaseModel):
    """Pydantic model for creating video analyses."""
    
    activity_id: int
    video_url: str
    analysis_type: str
    analysis_results: Optional[dict] = None
    status: str = "PENDING"
    error_message: Optional[str] = None

class VideoAnalysisUpdate(BaseModel):
    """Pydantic model for updating video analyses."""
    
    video_url: Optional[str] = None
    analysis_type: Optional[str] = None
    analysis_results: Optional[dict] = None
    status: Optional[str] = None
    error_message: Optional[str] = None

class VideoAnalysisResponse(BaseModel):
    """Pydantic model for video analysis responses."""
    
    id: int
    activity_id: int
    video_url: str
    analysis_type: str
    analysis_results: Optional[dict] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 