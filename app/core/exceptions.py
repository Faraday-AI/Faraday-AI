"""
Exceptions Module

This module provides comprehensive exception handling for the Faraday AI Dashboard.
"""

from typing import Any, Dict, Optional, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

class ErrorResponse(BaseModel):
    """Base error response model."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

class BaseAppException(Exception):
    """Base exception for all application exceptions."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

# HTTP Exceptions
class HTTPException(BaseAppException):
    """Base HTTP exception."""
    def __init__(
        self,
        message: str,
        code: str = "HTTP_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status_code, details)

class NotFoundException(HTTPException):
    """Resource not found exception."""
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_404_NOT_FOUND, details)

class BadRequestException(HTTPException):
    """Bad request exception."""
    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_400_BAD_REQUEST, details)

class UnauthorizedException(HTTPException):
    """Unauthorized exception."""
    def __init__(
        self,
        message: str = "Unauthorized",
        code: str = "UNAUTHORIZED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_401_UNAUTHORIZED, details)

class ForbiddenException(HTTPException):
    """Forbidden exception."""
    def __init__(
        self,
        message: str = "Forbidden",
        code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_403_FORBIDDEN, details)

class ConflictException(HTTPException):
    """Conflict exception."""
    def __init__(
        self,
        message: str = "Conflict",
        code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_409_CONFLICT, details)

# Database Exceptions
class DatabaseException(BaseAppException):
    """Base database exception."""
    def __init__(
        self,
        message: str,
        code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class IntegrityError(DatabaseException):
    """Database integrity error."""
    def __init__(
        self,
        message: str = "Database integrity error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "INTEGRITY_ERROR", details)

class ConnectionError(DatabaseException):
    """Database connection error."""
    def __init__(
        self,
        message: str = "Database connection error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "CONNECTION_ERROR", details)

# Validation Exceptions
class ValidationException(BaseAppException):
    """Base validation exception."""
    def __init__(
        self,
        message: str,
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_422_UNPROCESSABLE_ENTITY, details)

class SchemaValidationError(ValidationException):
    """Schema validation error."""
    def __init__(
        self,
        message: str = "Schema validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "SCHEMA_VALIDATION_ERROR", details)

class DataValidationError(ValidationException):
    """Data validation error."""
    def __init__(
        self,
        message: str = "Data validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "DATA_VALIDATION_ERROR", details)

# Authentication Exceptions
class AuthenticationException(BaseAppException):
    """Base authentication exception."""
    def __init__(
        self,
        message: str,
        code: str = "AUTHENTICATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_401_UNAUTHORIZED, details)

class InvalidCredentialsError(AuthenticationException):
    """Invalid credentials error."""
    def __init__(
        self,
        message: str = "Invalid credentials",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "INVALID_CREDENTIALS", details)

class TokenError(AuthenticationException):
    """Token error."""
    def __init__(
        self,
        message: str = "Invalid or expired token",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "TOKEN_ERROR", details)

# Security Exceptions
class SecurityException(BaseAppException):
    """Base security exception."""
    def __init__(
        self,
        message: str,
        code: str = "SECURITY_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_403_FORBIDDEN, details)

class AuthenticationError(SecurityException):
    """Authentication error."""
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class AuthorizationError(SecurityException):
    """Authorization error."""
    def __init__(
        self,
        message: str = "Not authorized",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AUTHORIZATION_ERROR", details)

class RateLimitExceeded(SecurityException):
    """Rate limit exceeded error."""
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)

class IPBlockedError(SecurityException):
    """IP blocked error."""
    def __init__(
        self,
        message: str = "IP address is blocked",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "IP_BLOCKED", details)

# Business Logic Exceptions
class BusinessLogicException(BaseAppException):
    """Base business logic exception."""
    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_400_BAD_REQUEST, details)

class ResourceStateError(BusinessLogicException):
    """Resource state error."""
    def __init__(
        self,
        message: str = "Invalid resource state",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "RESOURCE_STATE_ERROR", details)

class OperationNotAllowedError(BusinessLogicException):
    """Operation not allowed error."""
    def __init__(
        self,
        message: str = "Operation not allowed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "OPERATION_NOT_ALLOWED", details)

# Service Exceptions
class ServiceException(BaseAppException):
    """Base service exception."""
    def __init__(
        self,
        message: str,
        code: str = "SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_503_SERVICE_UNAVAILABLE, details)

class ServiceUnavailableError(ServiceException):
    """Service unavailable error."""
    def __init__(
        self,
        message: str = "Service unavailable",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "SERVICE_UNAVAILABLE", details)

class ServiceTimeoutError(ServiceException):
    """Service timeout error."""
    def __init__(
        self,
        message: str = "Service timeout",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "SERVICE_TIMEOUT", details)

class ServiceDiscoveryError(ServiceException):
    """Service discovery error."""
    def __init__(
        self,
        message: str = "Service discovery error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "SERVICE_DISCOVERY_ERROR", details)

# Deployment Exceptions
class DeploymentException(BaseAppException):
    """Base deployment exception."""
    def __init__(
        self,
        message: str,
        code: str = "DEPLOYMENT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class DeploymentFailedError(DeploymentException):
    """Deployment failed error."""
    def __init__(
        self,
        message: str = "Deployment failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "DEPLOYMENT_FAILED", details)

class RollbackFailedError(DeploymentException):
    """Rollback failed error."""
    def __init__(
        self,
        message: str = "Rollback failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "ROLLBACK_FAILED", details)

class VersionConflictError(DeploymentException):
    """Version conflict error."""
    def __init__(
        self,
        message: str = "Version conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "VERSION_CONFLICT", details)

# Feature Flag Exceptions
class FeatureFlagException(BaseAppException):
    """Base feature flag exception."""
    def __init__(
        self,
        message: str,
        code: str = "FEATURE_FLAG_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_400_BAD_REQUEST, details)

class FeatureFlagNotFoundError(FeatureFlagException):
    """Feature flag not found error."""
    def __init__(
        self,
        message: str = "Feature flag not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "FEATURE_FLAG_NOT_FOUND", details)

class FeatureFlagValidationError(FeatureFlagException):
    """Feature flag validation error."""
    def __init__(
        self,
        message: str = "Feature flag validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "FEATURE_FLAG_VALIDATION_ERROR", details)

# A/B Testing Exceptions
class ABTestException(BaseAppException):
    """Base A/B test exception."""
    def __init__(
        self,
        message: str,
        code: str = "AB_TEST_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_400_BAD_REQUEST, details)

class ABTestNotFoundError(ABTestException):
    """A/B test not found error."""
    def __init__(
        self,
        message: str = "A/B test not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AB_TEST_NOT_FOUND", details)

class ABTestValidationError(ABTestException):
    """A/B test validation error."""
    def __init__(
        self,
        message: str = "A/B test validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AB_TEST_VALIDATION_ERROR", details)

# Analytics Exceptions
class AnalyticsException(BaseAppException):
    """Base analytics exception."""
    def __init__(
        self,
        message: str,
        code: str = "ANALYTICS_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class AnalyticsProcessingError(AnalyticsException):
    """Analytics processing error."""
    def __init__(
        self,
        message: str = "Analytics processing error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "ANALYTICS_PROCESSING_ERROR", details)

class AnalyticsStorageError(AnalyticsException):
    """Analytics storage error."""
    def __init__(
        self,
        message: str = "Analytics storage error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "ANALYTICS_STORAGE_ERROR", details)

# Metrics Exceptions
class MetricsException(BaseAppException):
    """Base metrics exception."""
    def __init__(
        self,
        message: str,
        code: str = "METRICS_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class MetricsCollectionError(MetricsException):
    """Metrics collection error."""
    def __init__(
        self,
        message: str = "Metrics collection error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "METRICS_COLLECTION_ERROR", details)

class MetricsStorageError(MetricsException):
    """Metrics storage error."""
    def __init__(
        self,
        message: str = "Metrics storage error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "METRICS_STORAGE_ERROR", details)

# Alert Exceptions
class AlertException(BaseAppException):
    """Base alert exception."""
    def __init__(
        self,
        message: str,
        code: str = "ALERT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class AlertCreationError(AlertException):
    """Alert creation error."""
    def __init__(
        self,
        message: str = "Alert creation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "ALERT_CREATION_ERROR", details)

class AlertDeliveryError(AlertException):
    """Alert delivery error."""
    def __init__(
        self,
        message: str = "Alert delivery error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "ALERT_DELIVERY_ERROR", details)

# Circuit Breaker Exceptions
class CircuitBreakerException(BaseAppException):
    """Base circuit breaker exception."""
    def __init__(
        self,
        message: str,
        code: str = "CIRCUIT_BREAKER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status.HTTP_503_SERVICE_UNAVAILABLE, details)

class CircuitBreakerOpenError(CircuitBreakerException):
    """Circuit breaker open error."""
    def __init__(
        self,
        message: str = "Circuit breaker is open",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "CIRCUIT_BREAKER_OPEN", details)

class CircuitBreakerHalfOpenError(CircuitBreakerException):
    """Circuit breaker half-open error."""
    def __init__(
        self,
        message: str = "Circuit breaker is half-open",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "CIRCUIT_BREAKER_HALF_OPEN", details)

# Exception Handlers
async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handle application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id if hasattr(request.state, "request_id") else None
        ).dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id if hasattr(request.state, "request_id") else None
        ).dict()
    )

async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id if hasattr(request.state, "request_id") else None
        ).dict()
    )

async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """Handle database exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id if hasattr(request.state, "request_id") else None
        ).dict()
    )

async def authentication_exception_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
    """Handle authentication exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id if hasattr(request.state, "request_id") else None
        ).dict()
    )

async def business_logic_exception_handler(request: Request, exc: BusinessLogicException) -> JSONResponse:
    """Handle business logic exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id if hasattr(request.state, "request_id") else None
        ).dict()
    )

async def service_exception_handler(request: Request, exc: ServiceException) -> JSONResponse:
    """Handle service exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def deployment_exception_handler(request: Request, exc: DeploymentException) -> JSONResponse:
    """Handle deployment exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def feature_flag_exception_handler(request: Request, exc: FeatureFlagException) -> JSONResponse:
    """Handle feature flag exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def ab_test_exception_handler(request: Request, exc: ABTestException) -> JSONResponse:
    """Handle A/B test exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def analytics_exception_handler(request: Request, exc: AnalyticsException) -> JSONResponse:
    """Handle analytics exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def metrics_exception_handler(request: Request, exc: MetricsException) -> JSONResponse:
    """Handle metrics exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def alert_exception_handler(request: Request, exc: AlertException) -> JSONResponse:
    """Handle alert exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

async def circuit_breaker_exception_handler(request: Request, exc: CircuitBreakerException) -> JSONResponse:
    """Handle circuit breaker exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).dict()
    )

# Register exception handlers
def register_exception_handlers(app):
    """Register all exception handlers."""
    app.add_exception_handler(BaseAppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)
    app.add_exception_handler(BusinessLogicException, business_logic_exception_handler)
    app.add_exception_handler(ServiceException, service_exception_handler)
    app.add_exception_handler(DeploymentException, deployment_exception_handler)
    app.add_exception_handler(FeatureFlagException, feature_flag_exception_handler)
    app.add_exception_handler(ABTestException, ab_test_exception_handler)
    app.add_exception_handler(AnalyticsException, analytics_exception_handler)
    app.add_exception_handler(MetricsException, metrics_exception_handler)
    app.add_exception_handler(AlertException, alert_exception_handler)
    app.add_exception_handler(CircuitBreakerException, circuit_breaker_exception_handler)
    app.add_exception_handler(SQLAlchemyError, lambda request, exc: database_exception_handler(
        request, DatabaseException(str(exc))
    )) 