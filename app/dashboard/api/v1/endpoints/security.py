"""
Security API endpoints for the Faraday AI Dashboard.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....services.security_service import SecurityService
from ....dependencies import get_db
from ....schemas.security import (
    APIKeyInfo,
    PermissionInfo,
    RoleInfo,
    AccessLog,
    SecurityMetrics,
    SecurityAlert
)

router = APIRouter()

@router.post("/api-keys")
async def create_api_key(
    user_id: str,
    name: str,
    description: Optional[str] = None,
    permissions: Optional[List[str]] = None,
    expires_in: Optional[int] = None,
    db: Session = Depends(get_db)
) -> APIKeyInfo:
    """
    Create a new API key.
    
    Args:
        user_id: The ID of the user
        name: Name of the API key
        description: Optional description
        permissions: Optional list of permissions
        expires_in: Optional expiration in days
    """
    security_service = SecurityService(db)
    return await security_service.create_api_key(
        user_id=user_id,
        name=name,
        description=description,
        permissions=permissions,
        expires_in=expires_in
    )

@router.get("/api-keys/validate")
async def validate_api_key(
    key_id: str,
    secret: str,
    required_permissions: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """
    Validate an API key.
    
    Args:
        key_id: The API key ID
        secret: The API key secret
        required_permissions: Optional list of required permissions
    """
    security_service = SecurityService(db)
    is_valid = await security_service.validate_api_key(
        key_id=key_id,
        secret=secret,
        required_permissions=required_permissions
    )
    return {"valid": is_valid}

@router.get("/permissions/{user_id}")
async def get_user_permissions(
    user_id: str,
    include_roles: bool = Query(True, description="Include role-based permissions"),
    include_api_keys: bool = Query(True, description="Include API key permissions"),
    db: Session = Depends(get_db)
) -> Dict[str, List[str]]:
    """
    Get all permissions for a user.
    
    Args:
        user_id: The ID of the user
        include_roles: Whether to include role-based permissions
        include_api_keys: Whether to include API key permissions
    """
    security_service = SecurityService(db)
    return await security_service.get_user_permissions(
        user_id=user_id,
        include_roles=include_roles,
        include_api_keys=include_api_keys
    )

@router.post("/roles")
async def create_role(
    name: str,
    description: str,
    permissions: List[str],
    db: Session = Depends(get_db)
) -> RoleInfo:
    """
    Create a new role.
    
    Args:
        name: Name of the role
        description: Description of the role
        permissions: List of permissions
    """
    security_service = SecurityService(db)
    return await security_service.create_role(
        name=name,
        description=description,
        permissions=permissions
    )

@router.post("/roles/assign")
async def assign_role(
    user_id: str,
    role_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Assign a role to a user.
    
    Args:
        user_id: The ID of the user
        role_id: The ID of the role
    """
    security_service = SecurityService(db)
    return await security_service.assign_role(
        user_id=user_id,
        role_id=role_id
    )

@router.get("/metrics")
async def get_security_metrics(
    time_window: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_alerts: bool = Query(True, description="Include security alerts"),
    include_access_logs: bool = Query(True, description="Include access logs"),
    db: Session = Depends(get_db)
) -> SecurityMetrics:
    """
    Get security metrics and statistics.
    
    Args:
        time_window: Time window for metrics (24h, 7d, 30d)
        include_alerts: Whether to include security alerts
        include_access_logs: Whether to include access logs
    """
    security_service = SecurityService(db)
    return await security_service.get_security_metrics(
        time_window=time_window,
        include_alerts=include_alerts,
        include_access_logs=include_access_logs
    )

@router.get("/alerts")
async def get_security_alerts(
    time_window: str = Query("24h", regex="^(24h|7d|30d)$"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    status: Optional[str] = Query(None, regex="^(open|resolved|acknowledged)$"),
    db: Session = Depends(get_db)
) -> List[SecurityAlert]:
    """
    Get security alerts.
    
    Args:
        time_window: Time window for alerts (24h, 7d, 30d)
        severity: Optional severity filter
        status: Optional status filter
    """
    security_service = SecurityService(db)
    if time_window == "24h":
        start_time = datetime.utcnow() - timedelta(hours=24)
    elif time_window == "7d":
        start_time = datetime.utcnow() - timedelta(days=7)
    else:
        start_time = datetime.utcnow() - timedelta(days=30)
    
    alerts = await security_service._get_security_alerts(start_time)
    
    if severity:
        alerts = [alert for alert in alerts if alert.severity == severity]
    if status:
        alerts = [alert for alert in alerts if alert.status == status]
    
    return alerts

@router.get("/access-logs")
async def get_access_logs(
    time_window: str = Query("24h", regex="^(24h|7d|30d)$"),
    user_id: Optional[str] = None,
    api_key_id: Optional[str] = None,
    status: Optional[str] = Query(None, regex="^(success|failure)$"),
    db: Session = Depends(get_db)
) -> List[AccessLog]:
    """
    Get access logs.
    
    Args:
        time_window: Time window for logs (24h, 7d, 30d)
        user_id: Optional user ID filter
        api_key_id: Optional API key ID filter
        status: Optional status filter
    """
    security_service = SecurityService(db)
    return await security_service.get_access_logs(
        time_window=time_window,
        user_id=user_id,
        api_key_id=api_key_id,
        status=status
    )

@router.post("/rate-limits")
async def set_rate_limits(
    endpoint: str,
    requests_per_minute: int,
    burst_size: Optional[int] = None,
    user_id: Optional[str] = None,
    api_key_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Set rate limits for an endpoint.
    
    Args:
        endpoint: The API endpoint to rate limit
        requests_per_minute: Maximum requests per minute
        burst_size: Optional burst size for request spikes
        user_id: Optional user ID to apply limit to
        api_key_id: Optional API key ID to apply limit to
    """
    security_service = SecurityService(db)
    return await security_service.set_rate_limits(
        endpoint=endpoint,
        requests_per_minute=requests_per_minute,
        burst_size=burst_size,
        user_id=user_id,
        api_key_id=api_key_id
    )

@router.get("/rate-limits")
async def get_rate_limits(
    endpoint: Optional[str] = None,
    user_id: Optional[str] = None,
    api_key_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get rate limits.
    
    Args:
        endpoint: Optional endpoint to filter by
        user_id: Optional user ID to filter by
        api_key_id: Optional API key ID to filter by
    """
    security_service = SecurityService(db)
    return await security_service.get_rate_limits(
        endpoint=endpoint,
        user_id=user_id,
        api_key_id=api_key_id
    )

@router.post("/ip-allowlist")
async def add_ip_to_allowlist(
    ip_address: str,
    description: Optional[str] = None,
    expires_in: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add an IP address to the allowlist.
    
    Args:
        ip_address: The IP address to allow
        description: Optional description
        expires_in: Optional expiration in days
    """
    security_service = SecurityService(db)
    return await security_service.add_ip_to_allowlist(
        ip_address=ip_address,
        description=description,
        expires_in=expires_in
    )

@router.post("/ip-blocklist")
async def add_ip_to_blocklist(
    ip_address: str,
    reason: str,
    expires_in: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add an IP address to the blocklist.
    
    Args:
        ip_address: The IP address to block
        reason: Reason for blocking
        expires_in: Optional expiration in days
    """
    security_service = SecurityService(db)
    return await security_service.add_ip_to_blocklist(
        ip_address=ip_address,
        reason=reason,
        expires_in=expires_in
    )

@router.get("/ip-lists")
async def get_ip_lists(
    list_type: str = Query(..., regex="^(allowlist|blocklist)$"),
    include_expired: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get IP allowlist or blocklist.
    
    Args:
        list_type: Type of list to retrieve (allowlist or blocklist)
        include_expired: Whether to include expired entries
    """
    security_service = SecurityService(db)
    return await security_service.get_ip_lists(
        list_type=list_type,
        include_expired=include_expired
    )

@router.post("/audit-logs")
async def create_audit_log(
    action: str,
    resource_type: str,
    resource_id: str,
    user_id: str,
    details: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create an audit log entry.
    
    Args:
        action: The action performed
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        user_id: ID of user who performed the action
        details: Optional additional details
    """
    security_service = SecurityService(db)
    return await security_service.create_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details
    )

@router.get("/audit-logs")
async def get_audit_logs(
    time_window: str = Query("24h", regex="^(24h|7d|30d)$"),
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get audit logs with optional filters.
    
    Args:
        time_window: Time window for logs
        action: Optional action to filter by
        resource_type: Optional resource type to filter by
        resource_id: Optional resource ID to filter by
        user_id: Optional user ID to filter by
    """
    security_service = SecurityService(db)
    return await security_service.get_audit_logs(
        time_window=time_window,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id
    )

@router.post("/security-policies")
async def create_security_policy(
    name: str,
    policy_type: str,
    rules: List[Dict[str, Any]],
    description: Optional[str] = None,
    enabled: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a security policy.
    
    Args:
        name: Name of the policy
        policy_type: Type of policy
        rules: List of policy rules
        description: Optional description
        enabled: Whether the policy is enabled
    """
    security_service = SecurityService(db)
    return await security_service.create_security_policy(
        name=name,
        policy_type=policy_type,
        rules=rules,
        description=description,
        enabled=enabled
    )

@router.get("/security-policies")
async def get_security_policies(
    policy_type: Optional[str] = None,
    enabled_only: bool = True,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get security policies.
    
    Args:
        policy_type: Optional policy type to filter by
        enabled_only: Whether to return only enabled policies
    """
    security_service = SecurityService(db)
    return await security_service.get_security_policies(
        policy_type=policy_type,
        enabled_only=enabled_only
    )

@router.post("/sessions")
async def create_session(
    user_id: str,
    device_info: Dict[str, Any],
    ip_address: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new session.
    
    Args:
        user_id: The ID of the user
        device_info: Information about the device
        ip_address: IP address of the client
    """
    security_service = SecurityService(db)
    return await security_service.create_session(
        user_id=user_id,
        device_info=device_info,
        ip_address=ip_address
    )

@router.get("/sessions")
async def get_sessions(
    user_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get user sessions.
    
    Args:
        user_id: Optional user ID to filter by
        active_only: Whether to return only active sessions
    """
    security_service = SecurityService(db)
    return await security_service.get_sessions(
        user_id=user_id,
        active_only=active_only
    )

@router.post("/sessions/{session_id}/terminate")
async def terminate_session(
    session_id: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Terminate a session.
    
    Args:
        session_id: The ID of the session to terminate
        reason: Optional reason for termination
    """
    security_service = SecurityService(db)
    return await security_service.terminate_session(
        session_id=session_id,
        reason=reason
    )

@router.post("/2fa/enable")
async def enable_2fa(
    user_id: str,
    method: str = Query(..., regex="^(totp|sms|email)$"),
    phone_number: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Enable two-factor authentication for a user.
    
    Args:
        user_id: The ID of the user
        method: 2FA method (totp, sms, or email)
        phone_number: Required for SMS method
        email: Required for email method
    """
    security_service = SecurityService(db)
    return await security_service.enable_2fa(
        user_id=user_id,
        method=method,
        phone_number=phone_number,
        email=email
    )

@router.post("/2fa/verify")
async def verify_2fa(
    user_id: str,
    code: str,
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """
    Verify a 2FA code.
    
    Args:
        user_id: The ID of the user
        code: The 2FA code to verify
    """
    security_service = SecurityService(db)
    is_valid = await security_service.verify_2fa(
        user_id=user_id,
        code=code
    )
    return {"valid": is_valid}

@router.post("/2fa/disable")
async def disable_2fa(
    user_id: str,
    code: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Disable two-factor authentication for a user.
    
    Args:
        user_id: The ID of the user
        code: Current 2FA code for verification
    """
    security_service = SecurityService(db)
    return await security_service.disable_2fa(
        user_id=user_id,
        code=code
    ) 