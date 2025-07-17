"""
User Preferences Types

This module defines the types and enums used for user preferences.
"""

from enum import Enum

class PreferenceType(Enum):
    """Enum for user preference types."""
    THEME = "theme"
    LANGUAGE = "language"
    NOTIFICATIONS = "notifications"
    PRIVACY = "privacy"
    ACCESSIBILITY = "accessibility"
    DASHBOARD = "dashboard"
    TOOLS = "tools"
    AVATAR = "avatar"
    VOICE = "voice"
    GENERAL = "general" 