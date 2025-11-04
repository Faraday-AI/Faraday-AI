"""
Security components for the Faraday AI application.
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Tuple
from fastapi import HTTPException, status, Request, Response, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, constr, validator
import re
import logging
import base64
from io import BytesIO
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware
import redis
from app.core.config import settings
import uuid
from app.core.auth_models import User

# Try to import pyotp, but make it optional
try:
    import pyotp
    import qrcode
    MFA_AVAILABLE = True
except ImportError:
    MFA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("MFA functionality is disabled: pyotp package not available")

# Try to import authlib, but make it optional
try:
    from authlib.integrations.starlette_client import OAuth
    from authlib.oauth2.rfc6749 import OAuth2Token
    from authlib.oidc.core import UserInfo
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("OAuth functionality is disabled: authlib package not available")

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing
# Use bcrypt directly to avoid passlib's bug detection issues
try:
    import bcrypt
    _bcrypt_available = True
except ImportError:
    _bcrypt_available = False
    logger.warning("bcrypt not available, falling back to passlib with pbkdf2_sha256")

_pwd_context = None
_use_direct_bcrypt = False

def _initialize_password_context():
    """Initialize password context with lazy loading."""
    global _pwd_context, _use_direct_bcrypt
    
    # Check if already initialized (either direct bcrypt or passlib context)
    if _use_direct_bcrypt or (isinstance(_pwd_context, CryptContext)):
        return  # Already initialized
    
    if _bcrypt_available:
        try:
            # Try to use bcrypt directly first (bypasses passlib's bug detection)
            # Test with a short password
            test_hash = bcrypt.hashpw(b"test", bcrypt.gensalt(rounds=12))
            if bcrypt.checkpw(b"test", test_hash):
                _use_direct_bcrypt = True
                logger.info("Using direct bcrypt for password hashing")
                return
        except Exception as e:
            logger.warning(f"Direct bcrypt test failed: {e}. Trying passlib.")
    
    # Fall back to passlib
    try:
        _pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12,
            bcrypt__ident="2b"
        )
        # Test with a short password to trigger initialization
        _pwd_context.hash("test")
        _use_direct_bcrypt = False
        logger.info("Using passlib bcrypt for password hashing")
    except Exception as e:
        # If passlib bcrypt fails, use pbkdf2_sha256
        logger.warning(f"Bcrypt initialization failed: {e}. Using pbkdf2_sha256 fallback.")
        _pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        _use_direct_bcrypt = False

# For backwards compatibility, create a wrapper
class _PwdContextWrapper:
    """Wrapper that uses direct bcrypt when available, otherwise passlib."""
    def hash(self, password: str) -> str:
        _initialize_password_context()
        if _use_direct_bcrypt and _bcrypt_available:
            # Use bcrypt directly
            password_bytes = password.encode('utf-8')
            # Handle long passwords by pre-hashing
            if len(password_bytes) > 72:
                import hashlib
                password_bytes = hashlib.sha256(password_bytes).digest()
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password_bytes, salt)
            # Return in passlib-compatible format ($2b$...)
            return hashed.decode('utf-8')
        elif isinstance(_pwd_context, CryptContext):
            return _pwd_context.hash(password)
        else:
            raise RuntimeError("Password hashing not available")
    
    def verify(self, password: str, hash: str) -> bool:
        _initialize_password_context()
        if _use_direct_bcrypt and _bcrypt_available:
            # Use bcrypt directly
            password_bytes = password.encode('utf-8')
            # Handle long passwords by pre-hashing (match hashing logic)
            if len(password_bytes) > 72:
                import hashlib
                password_bytes = hashlib.sha256(password_bytes).digest()
            try:
                return bcrypt.checkpw(password_bytes, hash.encode('utf-8'))
            except Exception:
                return False
        elif isinstance(_pwd_context, CryptContext):
            return _pwd_context.verify(password, hash)
        else:
            return False

pwd_context = _PwdContextWrapper()

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# CORS settings
CORS_ORIGINS = settings.CORS_ORIGINS

# Security headers
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Resource-Policy": "same-origin",
}

# MFA Settings
MFA_ISSUER = "Faraday AI"
MFA_SECRET_LENGTH = 32
MFA_TOKEN_VALIDITY = 30  # seconds

# Session Settings
SESSION_EXPIRE_DAYS = 7
SESSION_CLEANUP_INTERVAL = 3600  # seconds
MAX_SESSIONS_PER_USER = 5

# API Key Settings
API_KEY_LENGTH = 32
API_KEY_PREFIX = "faraday_"
API_KEY_EXPIRE_DAYS = 365

# OAuth2 Settings
OAUTH2_CLIENTS = {}

# Add Google OAuth if credentials are available
if hasattr(settings, 'GOOGLE_CLIENT_ID') and hasattr(settings, 'GOOGLE_CLIENT_SECRET'):
    OAUTH2_CLIENTS["google"] = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
    }

# Add GitHub OAuth if credentials are available
if hasattr(settings, 'GITHUB_CLIENT_ID') and hasattr(settings, 'GITHUB_CLIENT_SECRET'):
    OAUTH2_CLIENTS["github"] = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
    }

# Password Policy
PASSWORD_POLICY = {
    "min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special": True,
    "max_age_days": 90,
    "history_size": 5,
}

# Rate Limiting
RATE_LIMITS = {
    "default": {"requests": 100, "window": 3600},
    "auth": {"requests": 5, "window": 300},
    "api": {"requests": 1000, "window": 3600},
}

# Audit Logging
AUDIT_EVENTS = {
    "AUTH": ["login", "logout", "password_change", "mfa_enable", "mfa_disable"],
    "USER": ["create", "update", "delete", "role_change"],
    "API": ["key_create", "key_revoke", "key_rotate"],
    "SESSION": ["create", "destroy", "expire"],
    "SECURITY": ["password_reset", "email_verify", "2fa_setup"],
}

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    STAFF = "staff"

class Permission(str, Enum):
    # User management
    VIEW_USERS = "view_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    
    # User profile management
    VIEW_USER_PROFILES = "view_user_profiles"
    EDIT_USER_PROFILES = "edit_user_profiles"
    CREATE_USER_PROFILES = "create_user_profiles"
    DELETE_USER_PROFILES = "delete_user_profiles"
    UPLOAD_PROFILE_PICTURES = "upload_profile_pictures"
    REMOVE_PROFILE_PICTURES = "remove_profile_pictures"
    
    # User preferences management
    VIEW_USER_PREFERENCES = "view_user_preferences"
    EDIT_USER_PREFERENCES = "edit_user_preferences"
    RESET_USER_PREFERENCES = "reset_user_preferences"
    EXPORT_USER_PREFERENCES = "export_user_preferences"
    IMPORT_USER_PREFERENCES = "import_user_preferences"
    
    # User privacy management
    VIEW_USER_PRIVACY = "view_user_privacy"
    EDIT_USER_PRIVACY = "edit_user_privacy"
    MANAGE_USER_PRIVACY = "manage_user_privacy"
    
    # Analytics permissions
    TRACK_ANALYTICS = "track_analytics"
    VIEW_USER_ANALYTICS = "view_user_analytics"
    VIEW_OTHER_USER_ANALYTICS = "view_other_user_analytics"
    VIEW_USER_BEHAVIOR = "view_user_behavior"
    VIEW_OTHER_USER_BEHAVIOR = "view_other_user_behavior"
    VIEW_USER_PERFORMANCE = "view_user_performance"
    VIEW_OTHER_USER_PERFORMANCE = "view_other_user_performance"
    VIEW_USER_ENGAGEMENT = "view_user_engagement"
    VIEW_OTHER_USER_ENGAGEMENT = "view_other_user_engagement"
    GENERATE_PREDICTIONS = "generate_predictions"
    VIEW_PREDICTIONS = "view_predictions"
    VIEW_OTHER_USER_PREDICTIONS = "view_other_user_predictions"
    GENERATE_RECOMMENDATIONS = "generate_recommendations"
    VIEW_RECOMMENDATIONS = "view_recommendations"
    VIEW_OTHER_USER_RECOMMENDATIONS = "view_other_user_recommendations"
    VIEW_USER_INSIGHTS = "view_user_insights"
    VIEW_OTHER_USER_INSIGHTS = "view_other_user_insights"
    VIEW_USER_TRENDS = "view_user_trends"
    VIEW_OTHER_USER_TRENDS = "view_other_user_trends"
    COMPARE_USERS = "compare_users"
    VIEW_ANALYTICS_SUMMARY = "view_analytics_summary"
    VIEW_OTHER_USER_ANALYTICS_SUMMARY = "view_other_user_analytics_summary"
    EXPORT_ANALYTICS = "export_analytics"
    VIEW_ANALYTICS_HEALTH = "view_analytics_health"
    VIEW_ANALYTICS_DASHBOARD = "view_analytics_dashboard"
    VIEW_OTHER_USER_ANALYTICS_DASHBOARD = "view_other_user_analytics_dashboard"
    BATCH_ANALYTICS_ANALYSIS = "batch_analytics_analysis"
    VIEW_REALTIME_ANALYTICS = "view_realtime_analytics"
    
    # Course management
    VIEW_COURSES = "view_courses"
    EDIT_COURSES = "edit_courses"
    CREATE_COURSES = "create_courses"
    DELETE_COURSES = "delete_courses"
    
    # Grade management
    VIEW_GRADES = "view_grades"
    EDIT_GRADES = "edit_grades"
    DELETE_GRADES = "delete_grades"
    
    # Assignment management
    VIEW_ASSIGNMENTS = "view_assignments"
    EDIT_ASSIGNMENTS = "edit_assignments"
    CREATE_ASSIGNMENTS = "create_assignments"
    DELETE_ASSIGNMENTS = "delete_assignments"
    
    # Rubric management
    VIEW_RUBRICS = "view_rubrics"
    EDIT_RUBRICS = "edit_rubrics"
    CREATE_RUBRICS = "create_rubrics"
    DELETE_RUBRICS = "delete_rubrics"
    
    # Communication
    SEND_MESSAGES = "send_messages"
    VIEW_MESSAGES = "view_messages"
    DELETE_MESSAGES = "delete_messages"
    
    # Message boards
    CREATE_BOARDS = "create_boards"
    EDIT_BOARDS = "edit_boards"
    DELETE_BOARDS = "delete_boards"
    POST_TO_BOARDS = "post_to_boards"
    VIEW_BOARDS = "view_boards"

# Role-Permission mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [
        Permission.VIEW_USERS,
        Permission.EDIT_USERS,
        Permission.DELETE_USERS,
        Permission.VIEW_USER_PROFILES,
        Permission.EDIT_USER_PROFILES,
        Permission.CREATE_USER_PROFILES,
        Permission.DELETE_USER_PROFILES,
        Permission.UPLOAD_PROFILE_PICTURES,
        Permission.REMOVE_PROFILE_PICTURES,
        Permission.VIEW_USER_PREFERENCES,
        Permission.EDIT_USER_PREFERENCES,
        Permission.RESET_USER_PREFERENCES,
        Permission.EXPORT_USER_PREFERENCES,
        Permission.IMPORT_USER_PREFERENCES,
        Permission.VIEW_USER_PRIVACY,
        Permission.EDIT_USER_PRIVACY,
        Permission.MANAGE_USER_PRIVACY,
        # Analytics permissions
        Permission.TRACK_ANALYTICS,
        Permission.VIEW_USER_ANALYTICS,
        Permission.VIEW_OTHER_USER_ANALYTICS,
        Permission.VIEW_USER_BEHAVIOR,
        Permission.VIEW_OTHER_USER_BEHAVIOR,
        Permission.VIEW_USER_PERFORMANCE,
        Permission.VIEW_OTHER_USER_PERFORMANCE,
        Permission.VIEW_USER_ENGAGEMENT,
        Permission.VIEW_OTHER_USER_ENGAGEMENT,
        Permission.GENERATE_PREDICTIONS,
        Permission.VIEW_PREDICTIONS,
        Permission.VIEW_OTHER_USER_PREDICTIONS,
        Permission.GENERATE_RECOMMENDATIONS,
        Permission.VIEW_RECOMMENDATIONS,
        Permission.VIEW_OTHER_USER_RECOMMENDATIONS,
        Permission.VIEW_USER_INSIGHTS,
        Permission.VIEW_OTHER_USER_INSIGHTS,
        Permission.VIEW_USER_TRENDS,
        Permission.VIEW_OTHER_USER_TRENDS,
        Permission.COMPARE_USERS,
        Permission.VIEW_ANALYTICS_SUMMARY,
        Permission.VIEW_OTHER_USER_ANALYTICS_SUMMARY,
        Permission.EXPORT_ANALYTICS,
        Permission.VIEW_ANALYTICS_HEALTH,
        Permission.VIEW_ANALYTICS_DASHBOARD,
        Permission.VIEW_OTHER_USER_ANALYTICS_DASHBOARD,
        Permission.BATCH_ANALYTICS_ANALYSIS,
        Permission.VIEW_REALTIME_ANALYTICS,
        # Course management
        Permission.VIEW_COURSES,
        Permission.EDIT_COURSES,
        Permission.CREATE_COURSES,
        Permission.DELETE_COURSES,
        Permission.VIEW_GRADES,
        Permission.EDIT_GRADES,
        Permission.DELETE_GRADES,
        Permission.VIEW_ASSIGNMENTS,
        Permission.EDIT_ASSIGNMENTS,
        Permission.CREATE_ASSIGNMENTS,
        Permission.DELETE_ASSIGNMENTS,
        Permission.VIEW_RUBRICS,
        Permission.EDIT_RUBRICS,
        Permission.CREATE_RUBRICS,
        Permission.DELETE_RUBRICS,
        Permission.SEND_MESSAGES,
        Permission.VIEW_MESSAGES,
        Permission.DELETE_MESSAGES,
        Permission.CREATE_BOARDS,
        Permission.EDIT_BOARDS,
        Permission.DELETE_BOARDS,
        Permission.POST_TO_BOARDS,
        Permission.VIEW_BOARDS
    ],
    UserRole.TEACHER: [
        Permission.VIEW_USER_PROFILES,
        Permission.EDIT_USER_PROFILES,
        Permission.VIEW_USER_PREFERENCES,
        Permission.EDIT_USER_PREFERENCES,
        Permission.VIEW_USER_PRIVACY,
        Permission.VIEW_COURSES,
        Permission.EDIT_COURSES,
        Permission.VIEW_GRADES,
        Permission.EDIT_GRADES,
        Permission.VIEW_ASSIGNMENTS,
        Permission.EDIT_ASSIGNMENTS,
        Permission.CREATE_ASSIGNMENTS,
        Permission.VIEW_RUBRICS,
        Permission.EDIT_RUBRICS,
        Permission.CREATE_RUBRICS,
        Permission.SEND_MESSAGES,
        Permission.VIEW_MESSAGES,
        Permission.VIEW_BOARDS,
        Permission.POST_TO_BOARDS
    ],
    UserRole.STUDENT: [
        Permission.VIEW_USER_PROFILES,
        Permission.EDIT_USER_PROFILES,
        Permission.VIEW_USER_PREFERENCES,
        Permission.EDIT_USER_PREFERENCES,
        Permission.VIEW_USER_PRIVACY,
        Permission.EDIT_USER_PRIVACY,
        Permission.VIEW_COURSES,
        Permission.VIEW_GRADES,
        Permission.VIEW_ASSIGNMENTS,
        Permission.VIEW_RUBRICS,
        Permission.SEND_MESSAGES,
        Permission.VIEW_MESSAGES,
        Permission.VIEW_BOARDS,
        Permission.POST_TO_BOARDS
    ],
    UserRole.PARENT: [
        Permission.VIEW_USER_PROFILES,
        Permission.VIEW_USER_PREFERENCES,
        Permission.VIEW_USER_PRIVACY,
        Permission.VIEW_COURSES,
        Permission.VIEW_GRADES,
        Permission.VIEW_ASSIGNMENTS,
        Permission.SEND_MESSAGES,
        Permission.VIEW_MESSAGES,
        Permission.VIEW_BOARDS
    ],
    UserRole.STAFF: [
        Permission.VIEW_USERS,
        Permission.VIEW_USER_PROFILES,
        Permission.VIEW_USER_PREFERENCES,
        Permission.VIEW_USER_PRIVACY,
        Permission.VIEW_COURSES,
        Permission.VIEW_GRADES,
        Permission.VIEW_ASSIGNMENTS,
        Permission.VIEW_RUBRICS,
        Permission.SEND_MESSAGES,
        Permission.VIEW_MESSAGES,
        Permission.VIEW_BOARDS,
        Permission.POST_TO_BOARDS
    ]
}

def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if user role has permission."""
    return permission in ROLE_PERMISSIONS.get(user_role, [])


def require_permission(permission: Permission):
    """Dependency to require a specific permission."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        # Handle both User objects and dictionaries (for test mode)
        if isinstance(current_user, dict):
            user_role = current_user.get('role')
        else:
            user_role = getattr(current_user, 'role', None)
        
        if not user_role:
            raise HTTPException(
                status_code=403,
                detail="User role not found"
            )
        
        # Convert string role to enum if needed
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid user role"
                )
        
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(*permissions: Permission):
    """Dependency to require any of the specified permissions."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        # Handle both User objects and dictionaries (for test mode)
        if isinstance(current_user, dict):
            user_role = current_user.get('role')
        else:
            user_role = getattr(current_user, 'role', None)
        
        if not user_role:
            raise HTTPException(
                status_code=403,
                detail="User role not found"
            )
        
        # Convert string role to enum if needed
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid user role"
                )
        
        # Check if user has any of the required permissions
        has_any_permission = any(has_permission(user_role, perm) for perm in permissions)
        
        if not has_any_permission:
            required_permissions = ", ".join([str(perm) for perm in permissions])
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required one of: {required_permissions}"
            )
        
        return current_user
    
    return permission_checker

class Token(BaseModel):
    """Token model."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    scopes: List[str] = []

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password.
    
    For long passwords (>72 bytes), we pre-hash with SHA256 before verification
    to match the hashing strategy in get_password_hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash.
    
    Bcrypt has a 72-byte limit. For longer passwords, we pre-hash with SHA256
    to ensure the input to bcrypt is always <= 64 bytes.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def validate_password(password: str) -> bool:
    """Validate password against policy."""
    if len(password) < PASSWORD_POLICY["min_length"]:
        return False
    if PASSWORD_POLICY["require_uppercase"] and not re.search(r"[A-Z]", password):
        return False
    if PASSWORD_POLICY["require_lowercase"] and not re.search(r"[a-z]", password):
        return False
    if PASSWORD_POLICY["require_numbers"] and not re.search(r"\d", password):
        return False
    if PASSWORD_POLICY["require_special"] and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(input_str: str) -> str:
    """Sanitize input string."""
    return re.sub(r'[<>]', '', input_str)

def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "INFO",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """Log security event."""
    logger.log(
        getattr(logging, severity.upper()),
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "severity": severity,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
    )

def add_security_headers(response: Response) -> None:
    """Add security headers to response."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value

def check_rate_limit(
    request: Request,
    endpoint: str = "default"
) -> None:
    """Check rate limit."""
    limit = RATE_LIMITS.get(endpoint, RATE_LIMITS["default"])
    if not limiter.check_rate_limit(request, limit["requests"], limit["window"]):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )

async def verify_access(
    user_id: str,
    resource_type: str,
    resource_id: str,
    required_access_level: str,
    org_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Verify user access to resource."""
    # Add your access control logic here
    return True

class MFASettings(BaseModel):
    """MFA settings model."""
    enabled: bool = False
    secret: Optional[str] = None
    backup_codes: List[str] = []
    last_used: Optional[datetime] = None

    @validator("backup_codes")
    def validate_backup_codes(cls, v):
        """Validate backup codes."""
        if len(v) != 10:
            raise ValueError("Must have exactly 10 backup codes")
        return v

class Session(BaseModel):
    """Session model."""
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

class APIKey(BaseModel):
    """API key model."""
    key: str
    user_id: str
    name: str
    created_at: datetime
    expires_at: datetime
    last_used: Optional[datetime]
    is_active: bool = True
    permissions: List[str] = []

class OAuth2User(BaseModel):
    """OAuth2 user model."""
    id: str
    email: str
    name: str
    provider: str
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    scope: List[str] = []

def generate_mfa_secret() -> str:
    """Generate a new MFA secret."""
    if not MFA_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="MFA functionality is not available: pyotp package not installed"
        )
    return pyotp.random_base32()

def generate_mfa_qr_code(secret: str, username: str) -> str:
    """Generate a QR code for MFA setup."""
    if not MFA_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="MFA functionality is not available: pyotp package not installed"
        )
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name=MFA_ISSUER
    )
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify an MFA code."""
    if not MFA_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="MFA functionality is not available: pyotp package not installed"
        )
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def generate_backup_codes() -> List[str]:
    """Generate backup codes."""
    return [pyotp.random_base32()[:8] for _ in range(10)]

def create_session(
    user_id: str,
    request: Request,
    expire_days: int = SESSION_EXPIRE_DAYS
) -> Session:
    """Create session."""
    now = datetime.utcnow()
    return Session(
        id=str(uuid.uuid4()),
        user_id=user_id,
        created_at=now,
        expires_at=now + timedelta(days=expire_days),
        last_activity=now,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )

def validate_session(session: Session) -> bool:
    """Validate session."""
    now = datetime.utcnow()
    return (
        session.is_active and
        session.expires_at > now and
        session.last_activity > now - timedelta(days=1)
    )

def generate_api_key(
    user_id: str,
    name: str,
    permissions: List[str] = None,
    expire_days: int = API_KEY_EXPIRE_DAYS
) -> APIKey:
    """Generate API key."""
    now = datetime.utcnow()
    return APIKey(
        key=f"{API_KEY_PREFIX}{uuid.uuid4().hex}",
        user_id=user_id,
        name=name,
        created_at=now,
        expires_at=now + timedelta(days=expire_days),
        permissions=permissions or []
    )

def validate_api_key(key: str) -> bool:
    """Validate API key."""
    if not key.startswith(API_KEY_PREFIX):
        return False
    return len(key) == len(API_KEY_PREFIX) + 32

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password strength."""
    errors = []
    if len(password) < PASSWORD_POLICY["min_length"]:
        errors.append(f"Password must be at least {PASSWORD_POLICY['min_length']} characters")
    if PASSWORD_POLICY["require_uppercase"] and not re.search(r"[A-Z]", password):
        errors.append("Password must contain uppercase letters")
    if PASSWORD_POLICY["require_lowercase"] and not re.search(r"[a-z]", password):
        errors.append("Password must contain lowercase letters")
    if PASSWORD_POLICY["require_numbers"] and not re.search(r"\d", password):
        errors.append("Password must contain numbers")
    if PASSWORD_POLICY["require_special"] and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain special characters")
    return len(errors) == 0, errors

def check_password_history(
    user_id: str,
    new_password: str,
    history_size: int = PASSWORD_POLICY["history_size"]
) -> bool:
    """Check password history."""
    # Add your password history check logic here
    return True

# OAuth2 scheme for token authentication
class TestOAuth2PasswordBearer(OAuth2PasswordBearer):
    """Custom OAuth2 scheme that bypasses authentication in test mode."""
    
    async def __call__(self, request=None):
        # Skip authentication in test mode
        if os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true":
            return "test_token"
        
        # Use the parent class implementation for normal operation
        return await super().__call__(request)

oauth2_scheme = TestOAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from the JWT token.
    
    Args:
        token: The JWT token from the request
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    # Skip authentication in test mode
    if os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true":
        # Create a mock User object for testing
        from app.models.core.user import User
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
            role="admin",
            password_hash="hashed_password_for_testing"
        )
        return mock_user
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    return {
        "username": token_data.username,
        "scopes": token_data.scopes
    } 