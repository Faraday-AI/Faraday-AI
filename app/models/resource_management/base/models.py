"""
Base Resource Management Models

This module defines the base models and enums for resource management.
"""

import enum
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.physical_education.base.base_class import Base
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class ResourceType(str, enum.Enum):
    """Types of resources that can be monitored."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"

class ResourceMetric(str, enum.Enum):
    """Types of metrics that can be collected."""
    USAGE = "usage"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    COST = "cost"
    EFFICIENCY = "efficiency" 