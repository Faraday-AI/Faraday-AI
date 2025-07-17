"""
Pydantic schemas for security models.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class RateLimitBase(BaseModel):
    """Base schema for rate limit configuration."""
    endpoint: str = Field(..., description="The API endpoint to rate limit")
    requests_per_minute: int = Field(..., description="Maximum requests per minute")
    burst_size: Optional[int] = Field(None, description="Optional burst size for request spikes")
    user_id: Optional[str] = Field(None, description="Optional user ID to apply limit to")
    api_key_id: Optional[str] = Field(None, description="Optional API key ID to apply limit to")

class RateLimit(RateLimitBase):
    """Complete rate limit configuration with system fields."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IPAllowlistBase(BaseModel):
    """Base schema for IP allowlist entries."""
    ip_address: str = Field(..., description="The IP address to allow")
    description: Optional[str] = Field(None, description="Optional description")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")

class IPAllowlist(IPAllowlistBase):
    """Complete IP allowlist entry with system fields."""
    id: str
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class IPBlocklistBase(BaseModel):
    """Base schema for IP blocklist entries."""
    ip_address: str = Field(..., description="The IP address to block")
    reason: str = Field(..., description="Reason for blocking")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")

class IPBlocklist(IPBlocklistBase):
    """Complete IP blocklist entry with system fields."""
    id: str
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    """Base schema for audit log entries."""
    action: str = Field(..., description="The action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: str = Field(..., description="ID of resource affected")
    user_id: str = Field(..., description="ID of user who performed the action")
    details: Optional[Dict[str, Any]] = Field(default={}, description="Additional details")

class AuditLog(AuditLogBase):
    """Complete audit log entry with system fields."""
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class SecurityPolicyBase(BaseModel):
    """Base schema for security policies."""
    name: str = Field(..., description="Name of the policy")
    policy_type: str = Field(..., description="Type of policy")
    description: Optional[str] = Field(None, description="Optional description")
    rules: List[Dict[str, Any]] = Field(..., description="List of policy rules")
    enabled: bool = Field(True, description="Whether the policy is enabled")

class SecurityPolicy(SecurityPolicyBase):
    """Complete security policy with system fields."""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    """Base schema for user sessions."""
    user_id: str = Field(..., description="The ID of the user")
    device_info: Dict[str, Any] = Field(..., description="Information about the device")
    ip_address: str = Field(..., description="IP address of the client")

class Session(SessionBase):
    """Complete user session with system fields."""
    id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    termination_reason: Optional[str] = None

    class Config:
        from_attributes = True

class SecurityMetrics(BaseModel):
    """Security metrics and statistics."""
    total_active_sessions: int = Field(..., description="Total number of active sessions")
    total_audit_logs: int = Field(..., description="Total number of audit log entries")
    active_security_policies: int = Field(..., description="Number of active security policies")
    recent_security_alerts: List[Dict[str, Any]] = Field(..., description="Recent security alerts")
    ip_allowlist_count: int = Field(..., description="Number of IP allowlist entries")
    ip_blocklist_count: int = Field(..., description="Number of IP blocklist entries")
    rate_limit_violations: int = Field(..., description="Number of rate limit violations")
    failed_login_attempts: int = Field(..., description="Number of failed login attempts")
    two_factor_usage: float = Field(..., description="Percentage of users with 2FA enabled")

class SecurityAlert(BaseModel):
    """Security alert information."""
    id: str = Field(..., description="Alert ID")
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    category: str = Field(..., description="Alert category")
    message: str = Field(..., description="Alert message")
    details: Dict[str, Any] = Field(..., description="Alert details")
    timestamp: datetime = Field(..., description="Alert timestamp")
    status: str = Field(..., description="Alert status (open, resolved, acknowledged)")
    assigned_to: Optional[str] = Field(None, description="User assigned to the alert")
    resolution: Optional[str] = Field(None, description="Resolution details if resolved")

class AccessLog(BaseModel):
    """Access log information."""
    id: str = Field(..., description="Log ID")
    timestamp: datetime = Field(..., description="Access timestamp")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    api_key_id: Optional[str] = Field(None, description="API key ID if used")
    ip_address: str = Field(..., description="Client IP address")
    endpoint: str = Field(..., description="Accessed endpoint")
    method: str = Field(..., description="HTTP method")
    status_code: int = Field(..., description="Response status code")
    response_time: float = Field(..., description="Response time in seconds")
    user_agent: str = Field(..., description="Client user agent")
    request_id: str = Field(..., description="Unique request ID")
    error_details: Optional[str] = Field(None, description="Error details if any")

class TwoFactorConfig(BaseModel):
    """Two-factor authentication configuration."""
    method: str = Field(..., description="2FA method (totp, sms, email)")
    enabled: bool = Field(..., description="Whether 2FA is enabled")
    phone_number: Optional[str] = Field(None, description="Phone number for SMS method")
    email: Optional[str] = Field(None, description="Email for email method")
    backup_codes: Optional[List[str]] = Field(None, description="List of backup codes")
    last_verified: Optional[datetime] = Field(None, description="Last successful verification")

class APIKeyInfo(BaseModel):
    """API key information."""
    key_id: str = Field(..., description="API key ID")
    secret: Optional[str] = Field(None, description="API key secret (only returned once)")
    name: str = Field(..., description="Name of the API key")
    description: Optional[str] = Field(None, description="Optional description")
    permissions: List[str] = Field(default=[], description="List of permissions")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")

class PermissionInfo(BaseModel):
    """Permission information."""
    name: str = Field(..., description="Permission name")
    description: str = Field(..., description="Permission description")
    resource_type: str = Field(..., description="Type of resource")
    actions: List[str] = Field(..., description="Allowed actions")

class RoleInfo(BaseModel):
    """Role information."""
    id: str = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    permissions: List[str] = Field(..., description="List of permissions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp") 