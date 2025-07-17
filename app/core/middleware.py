"""
Middleware components for the Faraday AI application.
"""

import time
import uuid
import json
import logging
from typing import Callable, Optional, Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.responses import JSONResponse
from prometheus_client import Counter, Histogram
import redis
from app.core.security import (
    CORS_ORIGINS,
    SECURITY_HEADERS,
    add_security_headers,
    check_rate_limit,
    log_security_event,
    verify_token,
    get_current_user
)
from app.core.config import settings
from app.core.cache import get_cache
from app.core.monitoring import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ERROR_COUNT,
    CACHE_HITS,
    CACHE_MISSES
)

# Configure logging
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response details."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request started: {request_id} - {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
                "headers": dict(request.headers)
            }
        )
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {request_id} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request_id} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": process_time
                }
            )
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and formatting errors."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Log error
            logger.error(
                f"Error occurred: {str(e)}",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "error": str(e),
                    "path": request.url.path
                }
            )
            
            # Return formatted error response
            return Response(
                content=str(e),
                status_code=500,
                media_type="text/plain"
            )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        add_security_headers(response)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        check_rate_limit(request)
        return await call_next(request)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware for adding request ID to requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not exists
        if not hasattr(request.state, "request_id"):
            request.state.request_id = str(uuid.uuid4())
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request.state.request_id
        
        return response

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware for measuring request processing time."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add timing to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for public endpoints
        if request.url.path in settings.PUBLIC_PATHS:
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Verify token
        token = auth_header.split(" ")[1]
        try:
            user = await verify_token(token)
            request.state.user = user
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        
        return await call_next(request)

class CachingMiddleware(BaseHTTPMiddleware):
    """Middleware for caching responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip caching for non-GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        cache_key = f"{request.url.path}:{request.query_params}"
        
        # Try to get from cache
        cache = get_cache()
        cached_response = await cache.get(cache_key)
        
        if cached_response:
            CACHE_HITS.labels(endpoint=request.url.path).inc()
            return JSONResponse(content=json.loads(cached_response))
        
        CACHE_MISSES.labels(endpoint=request.url.path).inc()
        response = await call_next(request)
        
        # Cache response if successful
        if response.status_code == 200:
            await cache.set(cache_key, response.body, expire=settings.CACHE_TTL)
        
        return response

class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware for handling sessions."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get session from cookie
        session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
        
        if session_id:
            # Get session from store
            session = await get_session(session_id)
            if session:
                request.state.session = session
        
        response = await call_next(request)
        
        # Update session if modified
        if hasattr(request.state, "session") and request.state.session.modified:
            await save_session(request.state.session)
            response.set_cookie(
                settings.SESSION_COOKIE_NAME,
                request.state.session.id,
                max_age=settings.SESSION_TTL,
                httponly=True,
                secure=settings.SESSION_SECURE
            )
        
        return response

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring and metrics."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Increment request count
        REQUEST_COUNT.inc()
        
        # Start timing
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record latency
            REQUEST_LATENCY.observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Increment error count
            ERROR_COUNT.inc()
            raise

class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Validate request headers
        if not self._validate_headers(request.headers):
            raise HTTPException(status_code=400, detail="Invalid headers")
        
        # Validate request body for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.json()
                if not self._validate_body(body):
                    raise HTTPException(status_code=400, detail="Invalid request body")
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON")
        
        return await call_next(request)
    
    def _validate_headers(self, headers: Dict[str, str]) -> bool:
        """Validate request headers."""
        required_headers = ["Content-Type", "Accept"]
        return all(header in headers for header in required_headers)
    
    def _validate_body(self, body: Dict[str, Any]) -> bool:
        """Validate request body."""
        # Add your validation logic here
        return True

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get user from request state
        user = getattr(request.state, "user", None)
        
        # Log request
        await log_audit_event(
            action="request",
            user_id=user.id if user else None,
            resource_type=request.url.path,
            resource_id=None,
            details={
                "method": request.method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
        )
        
        response = await call_next(request)
        
        # Log response
        await log_audit_event(
            action="response",
            user_id=user.id if user else None,
            resource_type=request.url.path,
            resource_id=None,
            details={
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
        )
        
        return response

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance optimization."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add performance headers
        response = await call_next(request)
        
        # Add cache control headers
        response.headers["Cache-Control"] = "public, max-age=31536000"
        response.headers["Vary"] = "Accept-Encoding"
        
        # Add preload headers for critical resources
        if request.url.path == "/":
            response.headers["Link"] = "</static/css/main.css>; rel=preload; as=style"
        
        return response

class ServiceHealthMiddleware(BaseHTTPMiddleware):
    """Middleware for checking service health."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip health checks for health check endpoints
        if request.url.path.endswith("/health"):
            return await call_next(request)
        
        # Check service health
        try:
            service_id = request.headers.get("X-Service-ID")
            if service_id:
                cache = get_cache()
                health_key = f"service_health:{service_id}"
                health_data = await cache.get(health_key)
                
                if health_data:
                    health_data = json.loads(health_data)
                    if not health_data.get("is_healthy", True):
                        return JSONResponse(
                            status_code=503,
                            content={"detail": "Service is unhealthy"}
                        )
        except Exception as e:
            logger.error(f"Service health check failed: {str(e)}")
        
        return await call_next(request)

class DeploymentMiddleware(BaseHTTPMiddleware):
    """Middleware for handling deployments."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check deployment status
        try:
            service_id = request.headers.get("X-Service-ID")
            if service_id:
                cache = get_cache()
                deploy_key = f"deployment:{service_id}"
                deploy_data = await cache.get(deploy_key)
                
                if deploy_data:
                    deploy_data = json.loads(deploy_data)
                    if deploy_data.get("status") == "in_progress":
                        return JSONResponse(
                            status_code=503,
                            content={"detail": "Service is being deployed"}
                        )
        except Exception as e:
            logger.error(f"Deployment check failed: {str(e)}")
        
        return await call_next(request)

class FeatureFlagMiddleware(BaseHTTPMiddleware):
    """Middleware for handling feature flags."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check feature flags
        try:
            user_id = getattr(request.state, "user_id", None)
            if user_id:
                cache = get_cache()
                flags_key = f"user_flags:{user_id}"
                flags_data = await cache.get(flags_key)
                
                if flags_data:
                    flags_data = json.loads(flags_data)
                    request.state.feature_flags = flags_data
        except Exception as e:
            logger.error(f"Feature flag check failed: {str(e)}")
        
        return await call_next(request)

class ABTestingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling A/B testing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check A/B test assignments
        try:
            user_id = getattr(request.state, "user_id", None)
            if user_id:
                cache = get_cache()
                tests_key = f"user_tests:{user_id}"
                tests_data = await cache.get(tests_key)
                
                if tests_data:
                    tests_data = json.loads(tests_data)
                    request.state.ab_tests = tests_data
        except Exception as e:
            logger.error(f"A/B test check failed: {str(e)}")
        
        return await call_next(request)

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking analytics events."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Track request as analytics event
        try:
            user_id = getattr(request.state, "user_id", None)
            event_data = {
                "type": "request",
                "path": request.url.path,
                "method": request.method,
                "user_id": user_id,
                "timestamp": time.time()
            }
            
            cache = get_cache()
            events_key = f"analytics_events:{int(time.time() / 60)}"
            await cache.rpush(events_key, json.dumps(event_data))
        except Exception as e:
            logger.error(f"Analytics tracking failed: {str(e)}")
        
        return await call_next(request)

class AlertMiddleware(BaseHTTPMiddleware):
    """Middleware for handling alerts."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check for alerts
        try:
            service_id = request.headers.get("X-Service-ID")
            if service_id:
                cache = get_cache()
                alerts_key = f"service_alerts:{service_id}"
                alerts_data = await cache.get(alerts_key)
                
                if alerts_data:
                    alerts_data = json.loads(alerts_data)
                    if alerts_data.get("has_active_alerts", False):
                        logger.warning(f"Active alerts for service {service_id}")
        except Exception as e:
            logger.error(f"Alert check failed: {str(e)}")
        
        return await call_next(request)

class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling circuit breakers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check circuit breaker state
        try:
            service_id = request.headers.get("X-Service-ID")
            if service_id:
                cache = get_cache()
                breaker_key = f"circuit_breaker:{service_id}"
                breaker_data = await cache.get(breaker_key)
                
                if breaker_data:
                    breaker_data = json.loads(breaker_data)
                    if breaker_data.get("state") == "open":
                        return JSONResponse(
                            status_code=503,
                            content={"detail": "Circuit breaker is open"}
                        )
        except Exception as e:
            logger.error(f"Circuit breaker check failed: {str(e)}")
        
        return await call_next(request)

def setup_middleware(app: FastAPI) -> None:
    """Set up all middleware components."""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET,
        session_cookie=settings.SESSION_COOKIE_NAME,
        max_age=settings.SESSION_TTL,
        same_site="lax",
        https_only=settings.SESSION_SECURE
    )
    
    # Add custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(CachingMiddleware)
    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(ValidationMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(PerformanceMiddleware)
    
    # Add new middleware
    app.add_middleware(ServiceHealthMiddleware)
    app.add_middleware(DeploymentMiddleware)
    app.add_middleware(FeatureFlagMiddleware)
    app.add_middleware(ABTestingMiddleware)
    app.add_middleware(AnalyticsMiddleware)
    app.add_middleware(AlertMiddleware)
    app.add_middleware(CircuitBreakerMiddleware)
    
    # Log middleware setup
    logger.info("Middleware setup completed") 