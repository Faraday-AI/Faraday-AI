"""Movement models for physical education."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from ...core.base import BaseModel
from ...physical_education.activity.models import Activity

class MovementType(str, Enum):
    RUNNING = "running"
    JUMPING = "jumping"
    THROWING = "throwing"
    CATCHING = "catching"
    KICKING = "kicking"
    BALANCING = "balancing"
    CLIMBING = "climbing"
    ROLLING = "rolling"
    OTHER = "other"

class MovementQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"

# Removed duplicate MovementAnalysis and MovementPattern classes 