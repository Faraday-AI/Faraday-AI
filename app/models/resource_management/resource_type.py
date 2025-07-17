"""
Resource Type Enum

This module defines the different types of resources that can be accessed in the system.
"""

from enum import Enum

class ResourceType(str, Enum):
    """Enum for different types of resources."""
    
    # GPT Resources
    GPT = "gpt"
    GPT_DEFINITION = "gpt_definition"
    GPT_SUBSCRIPTION = "gpt_subscription"
    GPT_INTEGRATION = "gpt_integration"
    
    # User Resources
    USER = "user"
    USER_PROFILE = "user_profile"
    USER_SETTINGS = "user_settings"
    
    # Content Resources
    CONTENT = "content"
    DOCUMENT = "document"
    FILE = "file"
    
    # System Resources
    SYSTEM = "system"
    CONFIGURATION = "configuration"
    METRICS = "metrics"
    
    # Educational Resources
    COURSE = "course"
    LESSON = "lesson"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    
    # Collaboration Resources
    COLLABORATION = "collaboration"
    SESSION = "session"
    TEAM = "team"
    
    # Analytics Resources
    ANALYTICS = "analytics"
    REPORT = "report"
    DASHBOARD = "dashboard" 