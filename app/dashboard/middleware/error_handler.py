from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error
            logger.error(f"Error processing request: {str(e)}")
            logger.error(traceback.format_exc())

            # Create error response
            error_response = {
                "error": {
                    "message": str(e),
                    "type": type(e).__name__,
                    "status_code": getattr(e, "status_code", HTTP_500_INTERNAL_SERVER_ERROR)
                }
            }

            # Add additional context for specific error types
            if hasattr(e, "detail"):
                error_response["error"]["detail"] = e.detail
            if hasattr(e, "headers"):
                error_response["error"]["headers"] = e.headers

            return JSONResponse(
                status_code=error_response["error"]["status_code"],
                content=error_response
            )

class AccessControlErrorHandler:
    @staticmethod
    async def handle_permission_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle permission-related errors."""
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "message": "Permission denied",
                    "type": "PermissionError",
                    "detail": str(exc)
                }
            }
        )

    @staticmethod
    async def handle_authentication_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle authentication-related errors."""
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "message": "Authentication failed",
                    "type": "AuthenticationError",
                    "detail": str(exc)
                }
            }
        )

    @staticmethod
    async def handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle validation-related errors."""
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": "Validation error",
                    "type": "ValidationError",
                    "detail": str(exc)
                }
            }
        )

    @staticmethod
    async def handle_not_found_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle not found errors."""
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "message": "Resource not found",
                    "type": "NotFoundError",
                    "detail": str(exc)
                }
            }
        )

    @staticmethod
    async def handle_internal_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle internal server errors."""
        logger.error(f"Internal server error: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal server error",
                    "type": "InternalServerError",
                    "detail": "An unexpected error occurred"
                }
            }
        ) 