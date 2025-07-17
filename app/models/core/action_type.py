"""
Action Type Enum

This module defines the different types of actions that can be performed on resources.
"""

from enum import Enum

class ActionType(str, Enum):
    """Enum for different types of actions."""
    
    # Read Actions
    VIEW = "view"
    READ = "read"
    LIST = "list"
    SEARCH = "search"
    
    # Write Actions
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MODIFY = "modify"
    
    # Execute Actions
    EXECUTE = "execute"
    RUN = "run"
    START = "start"
    STOP = "stop"
    
    # Manage Actions
    MANAGE = "manage"
    ADMINISTER = "administer"
    CONFIGURE = "configure"
    DEPLOY = "deploy"
    
    # Share Actions
    SHARE = "share"
    GRANT = "grant"
    REVOKE = "revoke"
    TRANSFER = "transfer"
    
    # Special Actions
    APPROVE = "approve"
    REJECT = "reject"
    VERIFY = "verify"
    VALIDATE = "validate" 