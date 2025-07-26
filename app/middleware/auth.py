import os
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional
from app.core.config import settings

security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Skip auth in test mode
        if os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true":
            # Create a mock user for testing
            request.state.user = {
                "user_id": 1,
                "email": "test@example.com",
                "is_active": True
            }
            return await call_next(request)

        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Authorization header is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Extract the token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify the token
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )
            except JWTError:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check token expiration
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Add user info to request
            request.state.user = payload

            # Process the request
            response = await call_next(request)
            return response

        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            ) 