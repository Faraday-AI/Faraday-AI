"""
Core Enums

This module contains core enum definitions used across the Faraday AI application.
"""

import enum

class Region(str, enum.Enum):
    """Geographic regions."""
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA = "asia"
    AFRICA = "africa"
    AUSTRALIA = "australia"
    OCEANIA = "oceania"
    MIDDLE_EAST = "middle_east"
    GLOBAL = "global"

class ServiceStatus(str, enum.Enum):
    """Service status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"
    DEPLOYING = "deploying"
    ROLLING_BACK = "rolling_back"
    SCALING = "scaling"
    UPDATING = "updating"
    FAILED = "failed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated" 