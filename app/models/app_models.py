"""
Core Types

This module contains core type definitions used across the application.
"""

import enum
from typing import Optional
from datetime import datetime

class SecurityLevel(str, enum.Enum):
    """Security levels for access control."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityStatus(str, enum.Enum):
    """Status options for security events."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    PENDING = "pending"
    INVESTIGATING = "investigating"
    CLOSED = "closed"

class SecurityAction(str, enum.Enum):
    """Types of security actions."""
    MONITOR = "monitor"
    ALERT = "alert"
    BLOCK = "block"
    RESTRICT = "restrict"
    AUDIT = "audit"
    REPORT = "report"

class SecurityTrigger(str, enum.Enum):
    """Triggers for security events."""
    MANUAL = "manual"
    AUTOMATED = "automated"
    SCHEDULED = "scheduled"
    INCIDENT = "incident"
    VIOLATION = "violation"
    THRESHOLD = "threshold"

class SecurityType(str, enum.Enum):
    """Types of security measures."""
    ACCESS_CONTROL = "access_control"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    AUDIT = "audit"
    MONITORING = "monitoring"
    COMPLIANCE = "compliance"
    PRIVACY = "privacy"
    DATA_PROTECTION = "data_protection"
    NETWORK = "network"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"

class ExportFormat(str, enum.Enum):
    """Export formats for activity data."""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    HTML = "html"

class FileType(str, enum.Enum):
    """File types for exported data."""
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    MARKDOWN = "md"

class GradeLevel(str, enum.Enum):
    """Grade levels for students."""
    KINDERGARTEN = "kindergarten"
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"
    FIFTH = "5th"
    SIXTH = "6th"
    SEVENTH = "7th"
    EIGHTH = "8th"
    NINTH = "9th"
    TENTH = "10th"
    ELEVENTH = "11th"
    TWELFTH = "12th"

class Subject(str, enum.Enum):
    """Academic subjects."""
    PHYSICAL_EDUCATION = "physical_education"
    HEALTH = "health"
    SPORTS = "sports"
    FITNESS = "fitness"
    WELLNESS = "wellness"
    ATHLETICS = "athletics"
    RECREATION = "recreation"
    DANCE = "dance"
    YOGA = "yoga"
    MARTIAL_ARTS = "martial_arts"
    AQUATICS = "aquatics"
    OUTDOOR_EDUCATION = "outdoor_education"

__all__ = [
    'SecurityLevel',
    'SecurityStatus',
    'SecurityAction',
    'SecurityTrigger',
    'SecurityType',
    'ExportFormat',
    'FileType',
    'GradeLevel',
    'Subject'
] 