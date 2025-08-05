"""
Security package for Faraday AI.

This package contains security-related modules including compliance engine,
regional compliance, and digital barrier implementations.
"""

import sys
import importlib.util
import os

# Cache for the security module
_security_module = None

def _get_security_module():
    """Get the security module lazily to avoid circular imports."""
    global _security_module
    if _security_module is None:
        # Get the path to the actual security.py file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        security_py_path = os.path.join(os.path.dirname(current_dir), 'security.py')
        
        # Load the module from the file path
        spec = importlib.util.spec_from_file_location("app.core.security_module", security_py_path)
        if spec and spec.loader:
            _security_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_security_module)
        else:
            raise ImportError("Could not load security.py module")
    return _security_module

def __getattr__(name):
    """Dynamically import attributes from the security module."""
    module = _get_security_module()
    if hasattr(module, name):
        return getattr(module, name)
    raise AttributeError(f"module 'app.core.security' has no attribute '{name}'")

# Define __all__ for what should be available
__all__ = [
    'UserRole',
    'Permission',
    'has_permission',
    'require_permission',
    'require_any_permission',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'validate_password',
    'validate_email',
    'sanitize_input',
    'log_security_event',
    'add_security_headers',
    'check_rate_limit',
    'verify_access',
    'generate_mfa_secret',
    'generate_mfa_qr_code',
    'verify_mfa_code',
    'generate_backup_codes',
    'create_session',
    'validate_session',
    'generate_api_key',
    'validate_api_key',
    'validate_password_strength',
    'check_password_history',
    'get_current_user',
    'Token',
    'TokenData',
    'MFASettings',
    'Session',
    'APIKey',
    'OAuth2User',
    'TestOAuth2PasswordBearer',
    'pwd_context',
    'SECRET_KEY',
    'ALGORITHM',
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    'REFRESH_TOKEN_EXPIRE_DAYS',
    'limiter',
    'CORS_ORIGINS',
    'SECURITY_HEADERS',
    'MFA_ISSUER',
    'MFA_SECRET_LENGTH',
    'MFA_TOKEN_VALIDITY',
    'SESSION_EXPIRE_DAYS',
    'SESSION_CLEANUP_INTERVAL',
    'MAX_SESSIONS_PER_USER',
    'API_KEY_LENGTH',
    'API_KEY_PREFIX',
    'API_KEY_EXPIRE_DAYS',
    'OAUTH2_CLIENTS',
    'MFA_AVAILABLE',
    'OAUTH_AVAILABLE',
] 