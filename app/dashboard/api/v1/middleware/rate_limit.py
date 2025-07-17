"""Rate limiting middleware for access control endpoints."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Rate limits for different endpoint types
RATE_LIMITS = {
    "read": "100/minute",      # Higher limit for read operations
    "write": "30/minute",      # Medium limit for write operations
    "admin": "10/minute",      # Lower limit for admin operations
    "check": "200/minute"      # Higher limit for permission checks
}

def get_rate_limit_key(request: Request) -> str:
    """Get the rate limit key based on the endpoint type."""
    path = request.url.path
    method = request.method
    
    # Admin operations
    if any(op in path for op in ["/roles", "/permissions"]) and method != "GET":
        return RATE_LIMITS["admin"]
    
    # Permission checks
    if "check" in path:
        return RATE_LIMITS["check"]
    
    # Write operations
    if method in ["POST", "PUT", "PATCH", "DELETE"]:
        return RATE_LIMITS["write"]
    
    # Read operations
    return RATE_LIMITS["read"]

def setup_rate_limiting(app):
    """Set up rate limiting for access control endpoints."""
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if "/api/v1/access-control" in request.url.path:
            rate_limit = get_rate_limit_key(request)
            limiter.limit(rate_limit)(lambda: None)()
        
        response = await call_next(request)
        return response 