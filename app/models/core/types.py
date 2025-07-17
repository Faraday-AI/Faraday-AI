"""
Core Types

This module defines core enums and types used throughout the application.
"""

from enum import Enum

class Subject(str, Enum):
    """Standard, built-in subjects."""
    
    PHYSICAL_EDUCATION = "physical_education"
    MATH = "math"
    SCIENCE = "science"
    ENGLISH = "english"
    HISTORY = "history"
    ART = "art"
    MUSIC = "music"
    COMPUTER_SCIENCE = "computer_science"
    FOREIGN_LANGUAGE = "foreign_language"
    SOCIAL_STUDIES = "social_studies"
    HEALTH = "health"
    OTHER = "other" 