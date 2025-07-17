"""
Teacher Enums

This module defines enums for teacher-related models.
"""

from enum import Enum

class CertificationType(str, Enum):
    """Enum for teacher certification types."""
    
    CPR = "CPR"
    FIRST_AID = "FIRST_AID"
    PHYSICAL_EDUCATION = "PHYSICAL_EDUCATION"
    COACHING = "COACHING"
    SPORTS_SPECIFIC = "SPORTS_SPECIFIC"
    FITNESS = "FITNESS"
    NUTRITION = "NUTRITION"
    OTHER = "OTHER"

class SpecializationType(str, Enum):
    """Enum for teacher specialization types."""
    
    GENERAL_PE = "GENERAL_PE"
    SPORTS_COACHING = "SPORTS_COACHING"
    FITNESS_TRAINING = "FITNESS_TRAINING"
    ADAPTIVE_PE = "ADAPTIVE_PE"
    ATHLETICS = "ATHLETICS"
    RECREATION = "RECREATION"
    WELLNESS = "WELLNESS"
    OTHER = "OTHER" 