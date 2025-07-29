"""Security package for compliance and data protection."""

import logging
from typing import Dict, Any, Optional
from functools import wraps
from fastapi import HTTPException, status
import hashlib
import secrets
import bcrypt

from .compliance_engine import ComplianceEngine, DataClassification

logger = logging.getLogger(__name__)

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://faraday-ai.com",
    "https://www.faraday-ai.com"
]

# Security headers configuration
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

class UserRole:
    """User role class for managing user roles."""
    
    def __init__(self, name: str, description: str = "", permissions: list = None):
        self.name = name
        self.description = description
        self.permissions = permissions or []
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"UserRole(name='{self.name}', description='{self.description}')"
    
    def __eq__(self, other):
        if isinstance(other, UserRole):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)

class Permission:
    """Permission class for managing user permissions."""
    
    def __init__(self, name: str, description: str = "", resource: str = ""):
        self.name = name
        self.description = description
        self.resource = resource
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Permission(name='{self.name}', description='{self.description}', resource='{self.resource}')"
    
    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)

# Add class-level permission constants after class definition
Permission.VIEW_USER_PROFILES = Permission("view_user_profiles", "View user profiles")
Permission.CREATE_USER_PROFILES = Permission("create_user_profiles", "Create user profiles")
Permission.EDIT_USER_PROFILES = Permission("edit_user_profiles", "Edit user profiles")
Permission.DELETE_USER_PROFILES = Permission("delete_user_profiles", "Delete user profiles")
Permission.UPLOAD_PROFILE_PICTURES = Permission("upload_profile_pictures", "Upload profile pictures")
Permission.REMOVE_PROFILE_PICTURES = Permission("remove_profile_pictures", "Remove profile pictures")
Permission.VIEW_USER_PRIVACY = Permission("view_user_privacy", "View user privacy settings")
Permission.EDIT_USER_PRIVACY = Permission("edit_user_privacy", "Edit user privacy settings")
Permission.VIEW_USER_PREFERENCES = Permission("view_user_preferences", "View user preferences")
Permission.EDIT_USER_PREFERENCES = Permission("edit_user_preferences", "Edit user preferences")
Permission.EDIT_USERS = Permission("edit_users", "Edit users")
Permission.VIEW_USERS = Permission("view_users", "View users")
Permission.MANAGE_USERS = Permission("manage_users", "Manage user accounts")
Permission.VIEW_ANALYTICS = Permission("view_analytics", "View analytics data")
Permission.MANAGE_SYSTEM = Permission("manage_system", "Manage system settings")
Permission.ACCESS_ADMIN = Permission("access_admin", "Access admin features")

# Common permission constants
class Permissions:
    """Common permission constants."""
    
    # User management permissions
    USER_READ = Permission("user:read", "Read user information")
    USER_WRITE = Permission("user:write", "Modify user information")
    USER_DELETE = Permission("user:delete", "Delete user accounts")
    
    # Profile permissions
    PROFILE_READ = Permission("profile:read", "Read user profiles")
    PROFILE_WRITE = Permission("profile:write", "Modify user profiles")
    VIEW_USER_PROFILES = Permission("view_user_profiles", "View user profiles")
    
    # Admin permissions
    ADMIN_ACCESS = Permission("admin:access", "Full administrative access")
    SYSTEM_CONFIG = Permission("system:config", "Configure system settings")
    
    # Data permissions
    DATA_READ = Permission("data:read", "Read data")
    DATA_WRITE = Permission("data:write", "Write data")
    DATA_DELETE = Permission("data:delete", "Delete data")
    
    # Analytics permissions
    ANALYTICS_READ = Permission("analytics:read", "Read analytics data")
    ANALYTICS_WRITE = Permission("analytics:write", "Write analytics data")
    
    # Additional permissions that might be referenced
    MANAGE_USERS = Permission("manage_users", "Manage user accounts")
    VIEW_ANALYTICS = Permission("view_analytics", "View analytics data")
    MANAGE_SYSTEM = Permission("manage_system", "Manage system settings")
    ACCESS_ADMIN = Permission("access_admin", "Access admin features")

def verify_access(user_id: str, resource: str, action: str, permissions: Dict[str, Any] = None) -> bool:
    """Verify if a user has access to perform an action on a resource."""
    try:
        # Mock access verification logic
        # In a real implementation, this would check user roles, permissions, etc.
        
        # Default to allowing access for now
        logger.info(f"Access verification: user={user_id}, resource={resource}, action={action}")
        
        # Basic permission checks
        if permissions:
            if resource in permissions.get("restricted_resources", []):
                return user_id in permissions.get("admin_users", [])
            
            if action in permissions.get("restricted_actions", []):
                return user_id in permissions.get("privileged_users", [])
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying access: {str(e)}")
        return False

def require_access(resource: str, action: str):
    """Decorator to require access verification for endpoints."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or request context
            user_id = kwargs.get("user_id") or "anonymous"
            
            if not verify_access(user_id, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied for {action} on {resource}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission: str):
    """Decorator to require specific permission for endpoints."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or request context
            user_id = kwargs.get("user_id") or "anonymous"
            
            # Mock permission check - in real implementation, check user permissions
            if not _has_permission(user_id, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def _has_permission(user_id: str, permission: str) -> bool:
    """Check if user has the specified permission."""
    # Mock permission check - in real implementation, check user roles/permissions
    logger.info(f"Permission check: user={user_id}, permission={permission}")
    
    # Default to allowing access for now
    return True

def has_permission(user_id: str, permission: str) -> bool:
    """Check if user has the specified permission (public interface)."""
    return _has_permission(user_id, permission)

def require_any_permission(*permissions: str):
    """Decorator to require any of the specified permissions for endpoints."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or request context
            user_id = kwargs.get("user_id") or "anonymous"
            
            # Check if user has any of the required permissions
            has_any_permission = any(_has_permission(user_id, perm) for perm in permissions)
            
            if not has_any_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of the following permissions required: {', '.join(permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt."""
    try:
        # Convert password to bytes if it's a string
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        # Fallback to simple hash if bcrypt fails
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        # Convert to bytes if needed
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        # Try bcrypt verification first
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        # Fallback to simple hash comparison
        try:
            expected_hash = hashlib.sha256(plain_password).hexdigest()
            return expected_hash == hashed_password.decode('utf-8')
        except:
            return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def hash_data(data: str) -> str:
    """Generate a hash for data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def get_current_user():
    """Get current user from request context."""
    # Mock implementation for now
    return None

def add_security_headers(response):
    """Add security headers to response."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

def check_rate_limit(user_id: str, action: str, limit: int = 100, window: int = 3600) -> bool:
    """Check if user has exceeded rate limit for an action."""
    # Mock implementation for now
    # In a real implementation, this would check Redis or database for rate limiting
    logger.info(f"Rate limit check: user={user_id}, action={action}, limit={limit}, window={window}")
    return True

def log_security_event(event_type: str, user_id: str = None, details: dict = None, severity: str = "INFO"):
    """Log security events for monitoring and auditing."""
    # Mock implementation for now
    # In a real implementation, this would log to a security event log or SIEM
    logger.info(f"Security event: type={event_type}, user={user_id}, severity={severity}, details={details}")
    return True

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    # Mock implementation for now
    # In a real implementation, this would verify the JWT signature and decode the payload
    logger.info(f"Token verification: {token[:10]}...")
    return {"user_id": "mock_user", "permissions": ["read", "write"]}

__all__ = [
    'ComplianceEngine', 
    'DataClassification', 
    'UserRole',
    'Permission',
    'Permissions',
    'CORS_ORIGINS',
    'SECURITY_HEADERS',
    'add_security_headers',
    'check_rate_limit',
    'log_security_event',
                'verify_token',
            'verify_access', 
            'require_access',
            'require_permission',
            'require_any_permission',
            'has_permission',
            'get_password_hash',
            'verify_password',
            'generate_secure_token',
            'hash_data',
            'get_current_user'
] 