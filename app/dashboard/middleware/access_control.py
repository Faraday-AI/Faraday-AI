from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from app.dashboard.services.access_control_service import AccessControlService
from app.dashboard.schemas.access_control import ResourceType, ActionType
from app.dashboard.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class AccessControlMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        db: Session,
        skip_paths: Optional[list] = None,
        skip_methods: Optional[list] = None
    ):
        super().__init__(app)
        self.db = db
        self.skip_paths = skip_paths or []
        self.skip_methods = skip_methods or ["OPTIONS"]
        self.service = AccessControlService(db)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip middleware for certain paths and methods
        if request.url.path in self.skip_paths or request.method in self.skip_methods:
            return await call_next(request)

        try:
            # Get user ID from request (assuming it's in the Authorization header)
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID not provided"
                )

            # Map HTTP methods to action types
            action_map = {
                "GET": ActionType.READ,
                "POST": ActionType.CREATE,
                "PUT": ActionType.UPDATE,
                "DELETE": ActionType.DELETE,
                "PATCH": ActionType.UPDATE
            }
            action = action_map.get(request.method)
            if not action:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail=f"Method {request.method} not allowed"
                )

            # Map URL paths to resource types
            resource_map = {
                "/api/v1/users": ResourceType.USER,
                "/api/v1/roles": ResourceType.ROLE,
                "/api/v1/permissions": ResourceType.PERMISSION,
                "/api/v1/tools": ResourceType.TOOL,
                "/api/v1/gpt": ResourceType.GPT,
                "/api/v1/avatars": ResourceType.AVATAR,
                "/api/v1/preferences": ResourceType.PREFERENCE,
                "/api/v1/analytics": ResourceType.ANALYTICS,
                "/api/v1/monitoring": ResourceType.MONITORING,
                "/api/v1/notifications": ResourceType.NOTIFICATION
            }

            # Find the matching resource type
            resource_type = None
            resource_id = None
            for path_prefix, rtype in resource_map.items():
                if request.url.path.startswith(path_prefix):
                    resource_type = rtype
                    # Extract resource ID if present
                    path_parts = request.url.path.split("/")
                    if len(path_parts) > 4 and path_parts[4].isalnum():
                        resource_id = path_parts[4]
                    break

            if not resource_type:
                # If no specific resource type is found, use a default
                resource_type = ResourceType.API

            # Check permission
            has_permission = await self.service.check_permission(
                user_id=user_id,
                resource_type=resource_type,
                action=action,
                resource_id=resource_id
            )

            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )

            # If permission check passes, proceed with the request
            response = await call_next(request)
            return response

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Access control error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

class AccessControlRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = get_db()

    async def get_route_handler(self) -> Callable:
        original_route_handler = await super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Get user ID from request
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID not provided"
                )

            # Check if the route requires specific permissions
            if hasattr(self.endpoint, "required_permissions"):
                service = AccessControlService(self.db)
                for permission in self.endpoint.required_permissions:
                    has_permission = await service.check_permission(
                        user_id=user_id,
                        resource_type=permission["resource_type"],
                        action=permission["action"],
                        resource_id=permission.get("resource_id")
                    )
                    if not has_permission:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Permission denied: {permission['action']} on {permission['resource_type']}"
                        )

            # Proceed with the original route handler
            return await original_route_handler(request)

        return custom_route_handler 