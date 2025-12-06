"""
Widget Export API Endpoints

Provides endpoints for exporting widget data to various formats:
- PDF
- Word (DOCX)
- Excel (XLSX)
- PowerPoint (PPTX)
- Email
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging
import io
import base64
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.widget_export_service import WidgetExportService
from app.services.email.email_service import EmailService
from app.services.integration.twilio_service import get_twilio_service
from app.services.integration.msgraph_service import get_msgraph_service
from app.models.integration.microsoft_token import MicrosoftOAuthToken
from app.services.integration.token_encryption import get_token_encryption_service
from app.models.core.user import User as UserModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/widgets", tags=["widget-export"])


@router.post("/{widget_id}/export/pdf")
async def export_widget_to_pdf(
    widget_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request,
    upload_to_onedrive: bool = Body(False, description="Upload to OneDrive instead of downloading"),
    onedrive_folder: Optional[str] = Body(None, description="Optional OneDrive folder path")
):
    """Export widget data to PDF format. Optionally upload to OneDrive."""
    try:
        widget_data = await _get_widget_data(db, current_user["id"], widget_id)
        
        if not widget_data:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        export_service = WidgetExportService()
        pdf_bytes = export_service.export_to_pdf(
            widget_data=widget_data.get("data", {}),
            widget_type=widget_data.get("type", "unknown"),
            widget_title=widget_data.get("title", f"Widget {widget_id}")
        )
        
        filename = f"widget_{widget_id}_{widget_data.get('type', 'export')}.pdf"
        
        # If upload to OneDrive is requested
        if upload_to_onedrive:
            token = _get_microsoft_token_for_user(current_user, db, request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                )
            
            msgraph_service = get_msgraph_service()
            upload_result = msgraph_service.upload_to_onedrive(
                token=token,
                file_bytes=pdf_bytes,
                filename=filename,
                folder_path=onedrive_folder or "",
                conflict_behavior="rename"
            )
            
            if upload_result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "File uploaded to OneDrive successfully",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename")
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to OneDrive: {upload_result.get('error')}"
                )
        
        # Default: download file
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting widget to PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting widget: {str(e)}")


@router.post("/{widget_id}/export/word")
async def export_widget_to_word(
    widget_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request,
    upload_to_onedrive: bool = Body(False, description="Upload to OneDrive instead of downloading"),
    onedrive_folder: Optional[str] = Body(None, description="Optional OneDrive folder path")
):
    """Export widget data to Word (DOCX) format. Optionally upload to OneDrive."""
    try:
        widget_data = await _get_widget_data(db, current_user["id"], widget_id)
        
        if not widget_data:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        export_service = WidgetExportService()
        word_bytes = export_service.export_to_word(
            widget_data=widget_data.get("data", {}),
            widget_type=widget_data.get("type", "unknown"),
            widget_title=widget_data.get("title", f"Widget {widget_id}")
        )
        
        filename = f"widget_{widget_id}_{widget_data.get('type', 'export')}.docx"
        
        # If upload to OneDrive is requested
        if upload_to_onedrive:
            token = _get_microsoft_token_for_user(current_user, db, request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                )
            
            msgraph_service = get_msgraph_service()
            upload_result = msgraph_service.upload_to_onedrive(
                token=token,
                file_bytes=word_bytes,
                filename=filename,
                folder_path=onedrive_folder or "",
                conflict_behavior="rename"
            )
            
            if upload_result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "File uploaded to OneDrive successfully",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename")
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to OneDrive: {upload_result.get('error')}"
                )
        
        # Default: download file
        return StreamingResponse(
            io.BytesIO(word_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting widget to Word: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting widget: {str(e)}")


@router.post("/{widget_id}/export/excel")
async def export_widget_to_excel(
    widget_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request,
    upload_to_onedrive: bool = Body(False, description="Upload to OneDrive instead of downloading"),
    onedrive_folder: Optional[str] = Body(None, description="Optional OneDrive folder path")
):
    """Export widget data to Excel (XLSX) format. Optionally upload to OneDrive."""
    try:
        widget_data = await _get_widget_data(db, current_user["id"], widget_id)
        
        if not widget_data:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        export_service = WidgetExportService()
        excel_bytes = export_service.export_to_excel(
            widget_data=widget_data.get("data", {}),
            widget_type=widget_data.get("type", "unknown"),
            widget_title=widget_data.get("title", f"Widget {widget_id}")
        )
        
        filename = f"widget_{widget_id}_{widget_data.get('type', 'export')}.xlsx"
        
        # If upload to OneDrive is requested
        if upload_to_onedrive:
            token = _get_microsoft_token_for_user(current_user, db, request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                )
            
            msgraph_service = get_msgraph_service()
            upload_result = msgraph_service.upload_to_onedrive(
                token=token,
                file_bytes=excel_bytes,
                filename=filename,
                folder_path=onedrive_folder or "",
                conflict_behavior="rename"
            )
            
            if upload_result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "File uploaded to OneDrive successfully",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename")
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to OneDrive: {upload_result.get('error')}"
                )
        
        # Default: download file
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting widget to Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting widget: {str(e)}")


@router.post("/{widget_id}/export/powerpoint")
async def export_widget_to_powerpoint(
    widget_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request,
    upload_to_onedrive: bool = Body(False, description="Upload to OneDrive instead of downloading"),
    onedrive_folder: Optional[str] = Body(None, description="Optional OneDrive folder path")
):
    """Export widget data to PowerPoint (PPTX) format. Optionally upload to OneDrive."""
    try:
        widget_data = await _get_widget_data(db, current_user["id"], widget_id)
        
        if not widget_data:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        export_service = WidgetExportService()
        pptx_bytes = export_service.export_to_powerpoint(
            widget_data=widget_data.get("data", {}),
            widget_type=widget_data.get("type", "unknown"),
            widget_title=widget_data.get("title", f"Widget {widget_id}")
        )
        
        filename = f"widget_{widget_id}_{widget_data.get('type', 'export')}.pptx"
        
        # If upload to OneDrive is requested
        if upload_to_onedrive:
            token = _get_microsoft_token_for_user(current_user, db, request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                )
            
            msgraph_service = get_msgraph_service()
            upload_result = msgraph_service.upload_to_onedrive(
                token=token,
                file_bytes=pptx_bytes,
                filename=filename,
                folder_path=onedrive_folder or "",
                conflict_behavior="rename"
            )
            
            if upload_result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "File uploaded to OneDrive successfully",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename")
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to OneDrive: {upload_result.get('error')}"
                )
        
        # Default: download file
        return StreamingResponse(
            io.BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting widget to PowerPoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting widget: {str(e)}")


@router.post("/{widget_id}/export/email")
async def email_widget_export(
    widget_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request,
    recipients: List[str] = Body(..., description="List of email recipients"),
    format: str = Body("pdf", regex="^(pdf|word|excel|powerpoint)$", description="Export format"),
    subject: Optional[str] = Body(None, description="Email subject"),
    message: Optional[str] = Body(None, description="Email message body"),
    use_outlook_email: bool = Body(False, description="Use Outlook email instead of SMTP")
):
    """Email widget export to specified recipients. Optionally use Outlook email."""
    try:
        widget_data = await _get_widget_data(db, current_user["id"], widget_id)
        
        if not widget_data:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        export_service = WidgetExportService()
        widget_title = widget_data.get("title", f"Widget {widget_id}")
        widget_type = widget_data.get("type", "unknown")
        
        # Generate export file
        if format == "pdf":
            file_bytes = export_service.export_to_pdf(
                widget_data=widget_data.get("data", {}),
                widget_type=widget_type,
                widget_title=widget_title
            )
            filename = f"{widget_title.replace(' ', '_')}.pdf"
            content_type = "application/pdf"
        elif format == "word":
            file_bytes = export_service.export_to_word(
                widget_data=widget_data.get("data", {}),
                widget_type=widget_type,
                widget_title=widget_title
            )
            filename = f"{widget_title.replace(' ', '_')}.docx"
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif format == "excel":
            file_bytes = export_service.export_to_excel(
                widget_data=widget_data.get("data", {}),
                widget_type=widget_type,
                widget_title=widget_title
            )
            filename = f"{widget_title.replace(' ', '_')}.xlsx"
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif format == "powerpoint":
            file_bytes = export_service.export_to_powerpoint(
                widget_data=widget_data.get("data", {}),
                widget_type=widget_type,
                widget_title=widget_title
            )
            filename = f"{widget_title.replace(' ', '_')}.pptx"
            content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        email_subject = subject or f"{widget_title} - Widget Export"
        email_body = message or f"Please find attached the {widget_title} widget export in {format.upper()} format."
        
        # Use Outlook email if requested
        if use_outlook_email:
            token = _get_microsoft_token_for_user(current_user, db, request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Microsoft account not connected. Please connect your Microsoft account to use Outlook email."
                )
            
            msgraph_service = get_msgraph_service()
            
            # Prepare attachment for Outlook
            attachment_content = base64.b64encode(file_bytes).decode('utf-8')
            attachments = [{
                "name": filename,
                "content_bytes": attachment_content,
                "content_type": content_type
            }]
            
            # Send via Outlook
            result = msgraph_service.send_email_via_outlook(
                token=token,
                recipients=recipients,
                subject=email_subject,
                body=email_body,
                body_type="Text",
                attachments=attachments
            )
            
            if result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": f"Widget export sent via Outlook to {len(recipients)} recipient(s)",
                        "format": format,
                        "filename": filename,
                        "email_provider": "outlook"
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to send email via Outlook: {result.get('error')}"
                )
        
        # Default: Use SMTP email
        email_service = EmailService()
        success = await email_service.send_email_with_attachment(
            recipients=recipients,
            subject=email_subject,
            body=email_body,
            attachment_bytes=file_bytes,
            attachment_filename=filename,
            attachment_content_type=content_type
        )
        
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Widget export sent to {len(recipients)} recipient(s)",
                    "format": format,
                    "filename": filename,
                    "email_provider": "smtp"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error emailing widget export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error emailing widget: {str(e)}")


@router.post("/{widget_id}/export/sms")
async def sms_widget_export(
    widget_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    phone_number: str = Body(..., description="Recipient phone number (E.164 format)"),
    message: Optional[str] = Body(None, description="Optional custom message prefix")
):
    """Send widget data via SMS."""
    try:
        widget_data = await _get_widget_data(db, current_user["id"], widget_id)
        
        if not widget_data:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        # Get widget title
        widget_title = widget_data.get("title", f"Widget {widget_id}")
        widget_type = widget_data.get("type", "unknown")
        
        # Format widget data for SMS (concise format due to SMS character limits)
        sms_body = _format_widget_data_for_sms(
            widget_data.get("data", {}),
            widget_type,
            widget_title
        )
        
        # Add custom message prefix if provided
        if message:
            sms_body = f"{message}\n\n{sms_body}"
        
        # Send SMS via Twilio
        twilio_service = get_twilio_service()
        sms_result = await twilio_service.send_sms(phone_number, sms_body)
        
        if sms_result.get("status") in ["success", "pending"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Widget data sent via SMS to {phone_number}",
                    "message_sid": sms_result.get("message_sid"),
                    "twilio_status": sms_result.get("twilio_status")
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send SMS: {sms_result.get('message', 'Unknown error')}"
            )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending SMS widget export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending SMS: {str(e)}")


def _format_widget_data_for_sms(data: Dict[str, Any], widget_type: str, widget_title: str) -> str:
    """Format widget data for SMS (concise format)."""
    sms_text = f"{widget_title}\n"
    
    if not data or not isinstance(data, dict):
        return f"{sms_text}No data available."
    
    # Special handling for lesson plans
    if widget_type == 'lesson-planning' or 'lesson' in widget_type.lower():
        if data.get('title'):
            sms_text += f"Title: {data['title']}\n"
        if data.get('description'):
            desc = data['description'][:100] + "..." if len(data['description']) > 100 else data['description']
            sms_text += f"{desc}\n"
        if data.get('objectives'):
            objectives = data['objectives'] if isinstance(data['objectives'], list) else [data['objectives']]
            sms_text += f"Objectives: {len(objectives)} items\n"
        if data.get('activities'):
            activities = data['activities'] if isinstance(data['activities'], list) else [data['activities']]
            sms_text += f"Activities: {len(activities)} items\n"
    
    # Generic formatting (keep it short for SMS)
    elif isinstance(data, dict):
        # Limit to first 3-4 key items to keep SMS concise
        items = list(data.items())[:4]
        for key, value in items:
            if key not in ['id', 'widget_id', 'created_at', 'updated_at']:
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                sms_text += f"{key}: {value_str}\n"
    
    # Truncate to SMS-friendly length (SMS can be up to 1600 chars with concatenation, but keep it reasonable)
    if len(sms_text) > 500:
        sms_text = sms_text[:497] + "..."
    
    return sms_text


def _get_microsoft_token_for_user(
    current_user: dict,
    db: Session,
    request: Request
) -> Optional[str]:
    """Get Microsoft access token for user, refreshing if necessary."""
    try:
        from jose import jwt
        import os
        
        # Get encryption service for decrypting tokens
        encryption_service = get_token_encryption_service()
        
        # Get user ID from current_user dict
        user_id = current_user.get("id")
        if not user_id:
            # Try to get from JWT token if available
            try:
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
                    if SECRET_KEY:
                        ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
                        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        user_id = payload.get("sub")
                        if user_id:
                            try:
                                user_id = int(user_id)
                            except (ValueError, TypeError):
                                pass
            except Exception:
                pass
        
        if not user_id:
            logger.warning("Could not determine user ID for Microsoft token")
            return None
        
        # Convert to int if needed
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = int(user_id)
        
        # Get stored token from database
        oauth_token = db.query(MicrosoftOAuthToken).filter(
            MicrosoftOAuthToken.user_id == user_id,
            MicrosoftOAuthToken.is_active == True
        ).first()
        
        if not oauth_token:
            logger.warning(f"No active Microsoft token found for user {user_id}")
            return None
        
        # Check if token is expired or will expire soon (within 5 minutes)
        if oauth_token.expires_at and oauth_token.expires_at <= datetime.utcnow() + timedelta(minutes=5):
            # Token expired or expiring soon, try to refresh
            if oauth_token.refresh_token:
                msgraph_service = get_msgraph_service()
                decrypted_refresh_token = encryption_service.decrypt(oauth_token.refresh_token)
                refresh_result = msgraph_service.refresh_token(decrypted_refresh_token)
                
                if refresh_result.get("status") == "success":
                    token_data = refresh_result.get("token", {})
                    # Note: In a full implementation, you'd update the token in the database here
                    return token_data.get("access_token")
                else:
                    logger.error(f"Failed to refresh token: {refresh_result.get('error')}")
                    return None
        
        # Decrypt and return access token
        if oauth_token.encrypted_access_token:
            try:
                access_token = encryption_service.decrypt(oauth_token.encrypted_access_token)
                return access_token
            except Exception as e:
                logger.error(f"Error decrypting access token: {str(e)}")
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting Microsoft token: {str(e)}")
        return None


@router.post("/presentations/create")
async def create_presentation(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request,
    presentation_title: str = Body(..., description="Title of the presentation"),
    topic: str = Body(..., description="Topic of the presentation"),
    num_slides: int = Body(..., description="Number of slides"),
    slides: List[Dict[str, Any]] = Body(..., description="List of slide data"),
    subtitle: Optional[str] = Body(None, description="Optional subtitle"),
    upload_to_onedrive: bool = Body(False, description="Upload to OneDrive"),
    onedrive_folder: Optional[str] = Body(None, description="OneDrive folder path")
):
    """Create a PowerPoint presentation from scratch."""
    try:
        from app.services.widget_export_service import WidgetExportService
        
        export_service = WidgetExportService()
        ppt_bytes = export_service.create_presentation_from_slides(
            presentation_title=presentation_title,
            slides=slides,
            subtitle=subtitle
        )
        
        filename = f"{presentation_title.replace(' ', '_')}.pptx"
        
        # If upload to OneDrive is requested
        if upload_to_onedrive:
            token = _get_microsoft_token_for_user(current_user, db, request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                )
            
            msgraph_service = get_msgraph_service()
            upload_result = msgraph_service.upload_to_onedrive(
                token=token,
                file_bytes=ppt_bytes,
                filename=filename,
                folder_path=onedrive_folder or "",
                conflict_behavior="rename"
            )
            
            if upload_result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Presentation created and uploaded to OneDrive successfully",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename"),
                        "num_slides": len(slides) + 1
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to OneDrive: {upload_result.get('error')}"
                )
        
        # Default: download file
        return StreamingResponse(
            io.BytesIO(ppt_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating presentation: {str(e)}")


async def _get_widget_data(db: Session, user_id: str, widget_id: str) -> Optional[Dict[str, Any]]:
    """Get widget data by ID."""
    try:
        from app.dashboard.services.dashboard_service import DashboardService
        
        service = DashboardService(db)
        widgets = await service.get_dashboard_widgets(
            user_id=user_id,
            include_data=True,
            include_config=False
        )
        
        # Find the widget by ID
        for widget in widgets:
            if str(widget.get("id")) == str(widget_id) or str(widget.get("widget_id")) == str(widget_id):
                return widget
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting widget data: {str(e)}")
        return None

