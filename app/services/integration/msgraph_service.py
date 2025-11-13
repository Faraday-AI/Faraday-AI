from msal import ConfidentialClientApplication
from typing import Optional, Dict, Any
import logging
from functools import lru_cache
import requests
import os
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class MSGraphService:
    def __init__(self):
        self.settings = get_settings()
        try:
            # Verify required environment variables
            if not all([
                os.getenv('MSCLIENTID'),
                os.getenv('MSCLIENTSECRET'),
                os.getenv('MSTENANTID')
            ]):
                raise ValueError("Missing required Microsoft Graph environment variables")
                
            self.client = ConfidentialClientApplication(
                client_id=self.settings.CLIENT_ID,
                client_credential=self.settings.CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/{self.settings.TENANT_ID}"
            )
            self.scope = self.settings.SCOPE.split()
            logger.info("Microsoft Graph Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Microsoft Graph Service: {str(e)}")
            self.client = None
            self.scope = []

    def get_auth_url(self) -> str:
        """Generate authorization URL for Microsoft Graph."""
        if not self.client:
            raise ValueError("Microsoft Graph Service not properly initialized")
        return self.client.get_authorization_request_url(
            scopes=self.scope,
            redirect_uri=self.settings.REDIRECT_URI
        )

    def get_token(self, auth_code: str) -> Dict[str, Any]:
        """Get access token from authorization code."""
        if not self.client:
            return {"status": "error", "error": "Microsoft Graph Service not properly initialized"}
        try:
            # MSAL acquire_token_by_authorization_code is synchronous
            result = self.client.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=self.scope,
                redirect_uri=self.settings.REDIRECT_URI
            )
            if "access_token" in result:
                return {"status": "success", "token": result}
            return {"status": "error", "error": result.get("error_description", "Unknown error")}
        except Exception as e:
            logger.error(f"Error getting token: {str(e)}")
            return {"status": "error", "error": str(e)}

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information from Microsoft Graph."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            # requests.get is synchronous, but we can make it async-compatible by running in executor if needed
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers
            )
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user info: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Microsoft access token using refresh token."""
        if not self.client:
            return {"status": "error", "error": "Microsoft Graph Service not properly initialized"}
        try:
            # MSAL acquire_token_by_refresh_token is synchronous
            result = self.client.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=self.scope
            )
            if "access_token" in result:
                return {"status": "success", "token": result}
            return {"status": "error", "error": result.get("error_description", "Unknown error")}
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return {"status": "error", "error": str(e)}

@lru_cache()
def get_msgraph_service() -> MSGraphService:
    """Get cached Microsoft Graph service instance."""
    return MSGraphService() 