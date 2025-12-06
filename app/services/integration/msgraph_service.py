from msal import ConfidentialClientApplication
from typing import Optional, Dict, Any, List
import logging
from functools import lru_cache
import requests
import os
import base64
import json
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
    
    def send_email_via_outlook(
        self,
        token: str,
        recipients: List[str],
        subject: str,
        body: str,
        body_type: str = "Text",  # "Text" or "HTML"
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send email via Outlook using Microsoft Graph API.
        
        Args:
            token: Microsoft Graph access token
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content
            body_type: "Text" or "HTML"
            attachments: Optional list of attachment dicts with 'name', 'contentBytes' (base64), 'contentType'
            
        Returns:
            Dict with status and message details
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Build message payload
            message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": body_type,
                        "content": body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": recipient}}
                        for recipient in recipients
                    ]
                }
            }
            
            # Add attachments if provided
            if attachments:
                message["message"]["attachments"] = []
                for attachment in attachments:
                    message["message"]["attachments"].append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": attachment.get("name", "attachment"),
                        "contentType": attachment.get("contentType", "application/octet-stream"),
                        "contentBytes": attachment.get("contentBytes")  # Should be base64 encoded
                    })
            
            # Send email
            response = requests.post(
                "https://graph.microsoft.com/v1.0/me/sendMail",
                headers=headers,
                json=message
            )
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {len(recipients)} recipient(s)"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending email via Outlook: {str(e)}")
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("error", {}).get("message", str(e))
                except:
                    pass
            return {"status": "error", "error": error_detail}
    
    def upload_to_onedrive(
        self,
        token: str,
        file_bytes: bytes,
        filename: str,
        folder_path: str = "",
        conflict_behavior: str = "rename"  # "fail", "replace", "rename"
    ) -> Dict[str, Any]:
        """
        Upload file to OneDrive using Microsoft Graph API.
        
        Args:
            token: Microsoft Graph access token
            file_bytes: File content as bytes
            filename: Name of the file
            folder_path: Optional folder path in OneDrive (e.g., "Documents/Widgets")
            conflict_behavior: What to do if file exists ("fail", "replace", "rename")
            
        Returns:
            Dict with status and file details (webUrl, id, etc.)
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream"
            }
            
            # Build upload URL
            if folder_path:
                # Upload to specific folder
                folder_path_encoded = "/".join(folder_path.strip("/").split("/"))
                upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path_encoded}/{filename}:/content"
            else:
                # Upload to root
                upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filename}:/content"
            
            # Add conflict behavior query parameter
            upload_url += f"?@microsoft.graph.conflictBehavior={conflict_behavior}"
            
            # Upload file
            response = requests.put(
                upload_url,
                headers=headers,
                data=file_bytes
            )
            response.raise_for_status()
            
            file_data = response.json()
            
            return {
                "status": "success",
                "message": f"File uploaded successfully to OneDrive",
                "file_id": file_data.get("id"),
                "web_url": file_data.get("webUrl"),
                "filename": file_data.get("name"),
                "size": file_data.get("size")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading to OneDrive: {str(e)}")
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("error", {}).get("message", str(e))
                except:
                    pass
            return {"status": "error", "error": error_detail}
    
    def create_document_in_onedrive(
        self,
        token: str,
        document_type: str,  # "word", "excel", "powerpoint"
        filename: str,
        content: Optional[bytes] = None,
        folder_path: str = ""
    ) -> Dict[str, Any]:
        """
        Create a document in OneDrive (Word, Excel, or PowerPoint).
        
        Args:
            token: Microsoft Graph access token
            document_type: "word", "excel", or "powerpoint"
            filename: Name of the file (should include extension: .docx, .xlsx, .pptx)
            content: Optional file content as bytes (if None, creates empty document)
            folder_path: Optional folder path in OneDrive
            
        Returns:
            Dict with status and file details
        """
        try:
            # Map document type to MIME type
            mime_types = {
                "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "powerpoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            }
            
            content_type = mime_types.get(document_type.lower(), "application/octet-stream")
            
            # If no content provided, create empty document
            if content is None:
                # For now, return error - creating empty Office documents requires Graph API createUploadSession
                # which is more complex. Users should upload existing files instead.
                return {
                    "status": "error",
                    "error": "Creating empty Office documents requires file content. Use upload_to_onedrive() instead."
                }
            
            # Use upload_to_onedrive for actual file creation
            return self.upload_to_onedrive(
                token=token,
                file_bytes=content,
                filename=filename,
                folder_path=folder_path,
                conflict_behavior="rename"
            )
            
        except Exception as e:
            logger.error(f"Error creating document in OneDrive: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def share_document(
        self,
        token: str,
        file_id: str,
        recipients: List[str],
        permissions: str = "read",  # "read" or "write"
        send_notification: bool = True
    ) -> Dict[str, Any]:
        """
        Share a OneDrive document with recipients.
        
        Args:
            token: Microsoft Graph access token
            file_id: OneDrive file ID
            recipients: List of recipient email addresses
            permissions: "read" or "write"
            send_notification: Whether to send email notification to recipients
            
        Returns:
            Dict with status and sharing link
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Create sharing link
            permission_type = "write" if permissions == "write" else "read"
            
            share_payload = {
                "type": "view" if permission_type == "read" else "edit",
                "scope": "users",
                "recipients": [
                    {"email": recipient}
                    for recipient in recipients
                ],
                "sendNotification": send_notification
            }
            
            response = requests.post(
                f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/createLink",
                headers=headers,
                json=share_payload
            )
            response.raise_for_status()
            
            link_data = response.json()
            
            return {
                "status": "success",
                "message": f"Document shared with {len(recipients)} recipient(s)",
                "share_link": link_data.get("link", {}).get("webUrl"),
                "share_id": link_data.get("id")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sharing document: {str(e)}")
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("error", {}).get("message", str(e))
                except:
                    pass
            return {"status": "error", "error": error_detail}

@lru_cache()
def get_msgraph_service() -> MSGraphService:
    """Get cached Microsoft Graph service instance."""
    return MSGraphService() 