"""
GPT Performance Models

This module defines models for tracking GPT performance metrics.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.core.base import CoreBase
from app.db.mixins import MetadataMixin

class CoreGPTPerformance(CoreBase, MetadataMixin):
    """Model for GPT performance metrics."""
    __tablename__ = "core_gpt_performance"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("core_gpt_definitions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    threshold_id = Column(Integer, ForeignKey("performance_thresholds.id"), nullable=True)
    metric_type = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    performance_metadata = Column(JSON, nullable=True)

    # Relationships
    model = relationship("app.models.gpt.base.gpt.CoreGPTDefinition", back_populates="performance_metrics")
    user = relationship("User", back_populates="gpt_performance_metrics")
    threshold = relationship("PerformanceThreshold", back_populates="performance_metrics")

class PerformanceThreshold(CoreBase, MetadataMixin):
    """Model for performance thresholds."""
    __tablename__ = "performance_thresholds"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_type = Column(String, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    threshold_metadata = Column(JSON, nullable=True)

    # Relationships
    performance_metrics = relationship("CoreGPTPerformance", back_populates="threshold")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "model_id": self.model_id,
            "user_id": self.user_id,
            "metric_type": self.metric_type,
            "metric_value": self.metric_value,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "performance_metadata": self.performance_metadata,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "threshold_metadata": self.threshold_metadata
        } 