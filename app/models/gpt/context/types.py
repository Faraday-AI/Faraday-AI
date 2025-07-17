"""
Context Types

This module defines context-related enumerations and types.
"""

import enum

class ContextType(str, enum.Enum):
    """Types of GPT contexts."""
    CONVERSATION = "conversation"
    TASK = "task"
    SESSION = "session"
    WORKFLOW = "workflow"
    PROJECT = "project"

class InteractionType(str, enum.Enum):
    """Types of context interactions."""
    MESSAGE = "message"
    COMMAND = "command"
    ACTION = "action"
    QUERY = "query"
    RESPONSE = "response"

class SharingType(str, enum.Enum):
    """Types of context sharing."""
    USER = "user"
    PROJECT = "project"
    ORGANIZATION = "organization"

class SharingScope(str, enum.Enum):
    """Scopes of context sharing."""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted" 