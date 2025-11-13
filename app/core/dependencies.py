"""
Dependency injection functions for the Faraday AI application.
"""

import logging
from typing import AsyncGenerator, Callable, Dict, Generator, Optional, Type, TypeVar, Union, Any, List
from functools import lru_cache
import time
import json
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from redis import Redis
from prometheus_client import Counter, Histogram

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.core.cache import get_cache, Cache
from app.core.monitoring import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ERROR_COUNT,
    CACHE_HIT_COUNT,
    CACHE_MISS_COUNT
)
from app.models.user_management.user.user import User
from app.schemas.token import TokenPayload

# Type variables
T = TypeVar("T")
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Logger
logger = logging.getLogger(__name__)

# Note: get_current_user is defined in app.core.auth
# This async version is not currently used but kept for potential future use
async def get_current_user_async(
    db: AsyncSession = None,  # Will need get_async_db when implemented
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current user from token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await db.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user

async def get_current_active_user_async(
    current_user: User = Depends(get_current_user_async),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user

async def get_current_active_superuser_async(
    current_user: User = Depends(get_current_user_async),
) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

def get_db_session() -> Generator[Session, None, None]:
    """Get database session."""
    db = get_db()
    try:
        yield db
    finally:
        db.close()

# Note: get_async_db is not yet implemented in database.py
# This function is kept for potential future use
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    # TODO: Implement get_async_db in app.core.database
    raise NotImplementedError("Async database sessions are not yet implemented")
    # async with get_async_db() as db:
    #     try:
    #         yield db
    #     finally:
    #         await db.close()

def get_repository(
    model: Type[ModelType],
) -> Callable[[Session], Generator[ModelType, None, None]]:
    """Get repository for a model."""
    def _get_repo(
        db: Session = Depends(get_db_session),
    ) -> Generator[ModelType, None, None]:
        repo = model(db)
        try:
            yield repo
        finally:
            repo.close()
    return _get_repo

async def get_async_repository(
    model: Type[ModelType],
) -> Callable[[AsyncSession], AsyncGenerator[ModelType, None]]:
    """Get async repository for a model."""
    async def _get_repo(
        db: AsyncSession = Depends(get_async_db_session),
    ) -> AsyncGenerator[ModelType, None]:
        repo = model(db)
        try:
            yield repo
        finally:
            await repo.close()
    return _get_repo

def get_service(
    service_class: Type[T],
    **kwargs: Dict[str, Any],
) -> Callable[[Session], Generator[T, None, None]]:
    """Get service instance."""
    def _get_service(
        db: Session = Depends(get_db_session),
    ) -> Generator[T, None, None]:
        service = service_class(db, **kwargs)
        try:
            yield service
        finally:
            service.close()
    return _get_service

async def get_async_service(
    service_class: Type[T],
    **kwargs: Dict[str, Any],
) -> Callable[[AsyncSession], AsyncGenerator[T, None]]:
    """Get async service instance."""
    async def _get_service(
        db: AsyncSession = Depends(get_async_db_session),
    ) -> AsyncGenerator[T, None]:
        service = service_class(db, **kwargs)
        try:
            yield service
        finally:
            await service.close()
    return _get_service

def get_pagination_params(
    skip: int = 0,
    limit: int = 100,
) -> Dict[str, int]:
    """Get pagination parameters."""
    return {"skip": skip, "limit": limit}

def get_sort_params(
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """Get sort parameters."""
    return {"sort_by": sort_by, "sort_order": sort_order}

def get_filter_params(
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get filter parameters."""
    return {"filters": filters or {}}

def get_search_params(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get search parameters."""
    return {"query": query, "filters": filters or {}}

def get_export_params(
    format: str,
    fields: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get export parameters."""
    return {
        "format": format,
        "fields": fields or [],
        "filters": filters or {},
    }

def get_import_params(
    format: str,
    file: bytes,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get import parameters."""
    return {
        "format": format,
        "file": file,
        "options": options or {},
    }

def get_audit_params(
    user_id: int,
) -> Dict[str, int]:
    """Get audit parameters."""
    return {"user_id": user_id}

def get_version_params(
    version: int,
    is_latest: bool = True,
) -> Dict[str, Union[int, bool]]:
    """Get version parameters."""
    return {"version": version, "is_latest": is_latest}

def get_status_params(
    status: str,
    reason: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get status parameters."""
    return {
        "status": status,
        "reason": reason,
        "user_id": user_id,
    }

def get_priority_params(
    priority: int,
    reason: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get priority parameters."""
    return {
        "priority": priority,
        "reason": reason,
        "user_id": user_id,
    }

def get_order_params(
    order: int,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get order parameters."""
    return {
        "order": order,
        "user_id": user_id,
    }

def get_slug_params(
    slug: str,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get slug parameters."""
    return {
        "slug": slug,
        "user_id": user_id,
    }

def get_code_params(
    code: str,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get code parameters."""
    return {
        "code": code,
        "user_id": user_id,
    }

def get_external_id_params(
    external_id: str,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get external ID parameters."""
    return {
        "external_id": external_id,
        "user_id": user_id,
    }

def get_request_info(request: Request) -> Dict[str, Any]:
    """Get request information."""
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None,
    }

def get_error_response(
    status_code: int,
    detail: str,
    request_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get error response."""
    response = {
        "status_code": status_code,
        "detail": detail,
    }
    if request_info:
        response["request_info"] = request_info
    return response

def get_success_response(
    data: Any,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Get success response."""
    response = {
        "status": "success",
        "data": data,
    }
    if message:
        response["message"] = message
    return response

# Cache Dependencies
def get_cache_client() -> Generator[Redis, None, None]:
    """Get Redis cache client."""
    cache = get_cache()
    try:
        yield cache
    finally:
        cache.close()

async def get_async_cache_client() -> AsyncGenerator[Redis, None]:
    """Get async Redis cache client."""
    cache = get_cache()
    try:
        yield cache
    finally:
        await cache.close()

def get_cached_data(
    key: str,
    cache: Redis = Depends(get_cache_client),
) -> Optional[Any]:
    """Get cached data."""
    data = cache.get(key)
    if data:
        CACHE_HIT_COUNT.inc()
        return json.loads(data)
    CACHE_MISS_COUNT.inc()
    return None

# Session Dependencies
def get_session(
    request: Request,
) -> Dict[str, Any]:
    """Get session data."""
    session = request.session
    if not session:
        session = {}
    return session

def get_session_user(
    session: Dict[str, Any] = Depends(get_session),
) -> Optional[User]:
    """Get user from session."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.get(user_id)

# Monitoring Dependencies
def get_request_metrics(
    request: Request,
) -> Dict[str, Any]:
    """Get request metrics."""
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    def record_metrics(response: Response):
        process_time = time.time() - start_time
        REQUEST_LATENCY.observe(process_time)
        if response.status_code >= 400:
            ERROR_COUNT.inc()
    
    request.state.record_metrics = record_metrics
    return {"start_time": start_time}

# Validation Dependencies
def validate_request_body(
    request: Request,
    schema: Type[T],
) -> T:
    """Validate request body against schema."""
    try:
        body = request.json()
        return schema(**body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON",
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors(),
        )

def validate_query_params(
    request: Request,
    schema: Type[T],
) -> T:
    """Validate query parameters against schema."""
    try:
        params = dict(request.query_params)
        return schema(**params)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors(),
        )

# Audit Dependencies
def get_audit_context(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get audit context."""
    return {
        "user_id": current_user.id,
        "request_id": request.state.request_id,
        "timestamp": datetime.utcnow(),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }

def get_audit_logger(
    audit_context: Dict[str, Any] = Depends(get_audit_context),
) -> Callable:
    """Get audit logger."""
    def log_audit(
        action: str,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None,
    ):
        log_data = {
            **audit_context,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
        }
        logger.info("Audit log", extra=log_data)
    
    return log_audit

# Performance Dependencies
def get_performance_context(
    request: Request,
) -> Dict[str, Any]:
    """Get performance context."""
    return {
        "request_id": request.state.request_id,
        "start_time": time.time(),
        "path": request.url.path,
        "method": request.method,
    }

def get_performance_monitor(
    context: Dict[str, Any] = Depends(get_performance_context),
) -> Callable:
    """Get performance monitor."""
    def monitor_performance(response: Response):
        process_time = time.time() - context["start_time"]
        logger.info(
            "Request performance",
            extra={
                **context,
                "process_time": process_time,
                "status_code": response.status_code,
            }
        )
    
    return monitor_performance

# Security Dependencies
def get_security_context(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get security context."""
    return {
        "user_id": current_user.id,
        "user_role": current_user.role,
        "request_id": request.state.request_id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }

def get_security_checker(
    context: Dict[str, Any] = Depends(get_security_context),
) -> Callable:
    """Get security checker."""
    def check_security(
        required_role: Optional[str] = None,
        required_permission: Optional[str] = None,
    ):
        if required_role and context["user_role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        if required_permission:
            # Add permission checking logic here
            pass
    
    return check_security

# Rate Limiting Dependencies
def get_rate_limit_context(
    request: Request,
) -> Dict[str, Any]:
    """Get rate limit context."""
    return {
        "ip_address": request.client.host,
        "user_id": getattr(request.state, "user_id", None),
        "endpoint": request.url.path,
    }

def get_rate_limiter(
    context: Dict[str, Any] = Depends(get_rate_limit_context),
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get rate limiter."""
    def check_rate_limit(
        limit: int = 100,
        window: int = 3600,
    ):
        key = f"rate_limit:{context['ip_address']}:{context['endpoint']}"
        current = cache.get(key) or 0
        
        if current >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        
        cache.incr(key)
        if current == 0:
            cache.expire(key, window)
    
    return check_rate_limit

# Service Dependencies
def get_service_health_checker(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get service health checker."""
    def check_health(
        service_id: str,
        timeout: int = 5,
    ) -> Dict[str, Any]:
        """Check service health."""
        try:
            # Check cache first
            cache_key = f"service_health:{service_id}"
            cached_health = cache.get(cache_key)
            if cached_health:
                return json.loads(cached_health)
            
            # Perform health check
            # ... implementation ...
            
            # Cache result
            cache.setex(cache_key, 60, json.dumps(health_data))
            return health_data
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service health check failed"
            )
    return check_health

# Deployment Dependencies
def get_deployment_manager(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get deployment manager."""
    def manage_deployment(
        service_id: str,
        version: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Manage deployment."""
        try:
            # Check deployment status
            # ... implementation ...
            
            return deployment_data
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Deployment failed"
            )
    return manage_deployment

# Feature Flag Dependencies
def get_feature_flag_manager(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get feature flag manager."""
    def manage_feature_flag(
        flag_name: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Manage feature flag."""
        try:
            # Check cache first
            cache_key = f"feature_flag:{flag_name}"
            cached_flag = cache.get(cache_key)
            if cached_flag:
                return json.loads(cached_flag)
            
            # Evaluate feature flag
            # ... implementation ...
            
            # Cache result
            cache.setex(cache_key, 300, json.dumps(flag_value))
            return flag_value
        except Exception as e:
            logger.error(f"Feature flag check failed: {str(e)}")
            return False
    return manage_feature_flag

# A/B Testing Dependencies
def get_ab_test_manager(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get A/B test manager."""
    def manage_ab_test(
        test_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Manage A/B test."""
        try:
            # Check cache first
            cache_key = f"ab_test:{test_id}"
            cached_test = cache.get(cache_key)
            if cached_test:
                return json.loads(cached_test)
            
            # Get test variant
            # ... implementation ...
            
            # Cache result
            cache.setex(cache_key, 300, json.dumps(test_data))
            return test_data
        except Exception as e:
            logger.error(f"A/B test check failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A/B test check failed"
            )
    return manage_ab_test

# Analytics Dependencies
def get_analytics_manager(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get analytics manager."""
    def manage_analytics(
        event_type: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Manage analytics event."""
        try:
            # Track event
            # ... implementation ...
            
            # Cache event data
            cache_key = f"analytics:{event_type}:{user_id}"
            cache.setex(cache_key, 3600, json.dumps(event_data))
        except Exception as e:
            logger.error(f"Analytics tracking failed: {str(e)}")
    return manage_analytics

# Alert Dependencies
def get_alert_manager(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get alert manager."""
    def manage_alert(
        alert_type: str,
        severity: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Manage alert."""
        try:
            # Create alert
            # ... implementation ...
            
            # Cache alert data
            cache_key = f"alert:{alert_type}:{severity}"
            cache.setex(cache_key, 300, json.dumps(alert_data))
            return alert_data
        except Exception as e:
            logger.error(f"Alert creation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Alert creation failed"
            )
    return manage_alert

# Circuit Breaker Dependencies
def get_circuit_breaker_manager(
    cache: Redis = Depends(get_cache_client),
) -> Callable:
    """Get circuit breaker manager."""
    def manage_circuit_breaker(
        service_id: str,
        operation: str,
    ) -> Dict[str, Any]:
        """Manage circuit breaker."""
        try:
            # Check circuit breaker state
            cache_key = f"circuit_breaker:{service_id}:{operation}"
            cached_state = cache.get(cache_key)
            if cached_state:
                return json.loads(cached_state)
            
            # Get circuit breaker state
            # ... implementation ...
            
            # Cache state
            cache.setex(cache_key, 60, json.dumps(state_data))
            return state_data
        except Exception as e:
            logger.error(f"Circuit breaker check failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Circuit breaker check failed"
            )
    return manage_circuit_breaker 