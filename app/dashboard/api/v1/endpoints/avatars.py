from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.dashboard.services.avatar_service import AvatarService
from app.dashboard.schemas.avatar import (
    AvatarConfig,
    AvatarUpdate,
    UserAvatarPreferences,
    AvatarResponse,
    AvatarUploadResponse,
    AvatarBehaviorRequest,
    AvatarBehaviorResponse
)
from app.dashboard.dependencies.auth import get_current_user
from app.dashboard.models.tool_registry import Tool
import os
from pathlib import Path
import shutil
import logging
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTasks
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/tools/{tool_id}/avatar", response_model=AvatarResponse)
async def get_tool_avatar(
    tool_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get avatar configuration for a tool."""
    try:
        avatar_service = AvatarService(db)
        return avatar_service.get_tool_avatar(tool_id, current_user["id"])
    except Exception as e:
        logger.error(f"Error getting tool avatar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving avatar configuration"
        )

@router.put("/tools/{tool_id}/avatar", response_model=AvatarResponse)
async def update_tool_avatar(
    tool_id: str,
    avatar_update: AvatarUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update avatar configuration for a tool."""
    try:
        avatar_service = AvatarService(db)
        return avatar_service.update_tool_avatar(
            tool_id=tool_id,
            avatar_type=avatar_update.avatar_type,
            avatar_url=avatar_update.avatar_url,
            avatar_config=avatar_update.avatar_config,
            voice_enabled=avatar_update.voice_enabled,
            voice_config=avatar_update.voice_config
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool avatar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error updating avatar configuration"
        )

@router.put("/tools/{tool_id}/avatar/preferences", response_model=UserAvatarPreferences)
async def update_user_avatar_preferences(
    tool_id: str,
    preferences: UserAvatarPreferences,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user-specific avatar preferences for a tool."""
    try:
        avatar_service = AvatarService(db)
        return avatar_service.update_user_avatar_preferences(
            user_id=current_user["id"],
            tool_id=tool_id,
            avatar_customization=preferences.avatar_customization,
            voice_preferences=preferences.voice_preferences
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user avatar preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error updating avatar preferences"
        )

@router.post("/tools/{tool_id}/avatar/upload", response_model=AvatarUploadResponse)
async def upload_avatar(
    tool_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload an avatar file for a tool."""
    try:
        avatar_service = AvatarService(db)
        
        # Get tool to determine avatar type
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Create upload directory
        upload_path = avatar_service.avatar_base_path / tool_id
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{tool_id}_{int(datetime.utcnow().timestamp())}{file_extension}"
        file_path = upload_path / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process file
        file_info = avatar_service.process_uploaded_file(
            file_path=file_path,
            avatar_type=tool.avatar_type
        )
        
        # Update tool with new avatar URL
        avatar_url = f"/static/avatars/{tool_id}/{unique_filename}"
        avatar_config = avatar_service.update_tool_avatar(
            tool_id=tool_id,
            avatar_type=tool.avatar_type,
            avatar_url=avatar_url,
            avatar_config=tool.avatar_config,
            voice_enabled=tool.voice_enabled,
            voice_config=tool.voice_config
        )
        
        # Clean up old files in background
        background_tasks.add_task(
            _cleanup_old_files,
            upload_path,
            unique_filename
        )
        
        return {
            "file_info": file_info,
            "avatar_config": avatar_config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error uploading avatar file"
        )

@router.get("/tools/{tool_id}/avatar/thumbnail")
async def get_avatar_thumbnail(
    tool_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the thumbnail version of an avatar."""
    try:
        avatar_service = AvatarService(db)
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        avatar_path = Path(tool.avatar_url.lstrip('/'))
        thumbnail_path = avatar_path.parent / f"thumb_{avatar_path.name}"
        
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        return FileResponse(
            thumbnail_path,
            media_type="image/jpeg",
            filename=f"thumb_{avatar_path.name}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting avatar thumbnail: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving avatar thumbnail"
        )

@router.get("/avatar-types")
async def get_available_avatar_types(db: Session = Depends(get_db)):
    """Get available avatar types and their configurations."""
    try:
        avatar_service = AvatarService(db)
        return avatar_service.get_available_avatar_types()
    except Exception as e:
        logger.error(f"Error getting avatar types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving avatar types"
        )

@router.post("/tools/{tool_id}/avatar/behavior", response_model=AvatarBehaviorResponse)
async def get_avatar_behavior(
    tool_id: str,
    request: AvatarBehaviorRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get avatar behavior configuration for a message."""
    try:
        avatar_service = AvatarService(db)
        behavior_config = avatar_service.get_avatar_behavior(
            tool_id=tool_id,
            message=request.message,
            user_id=current_user["id"]
        )
        
        if behavior_config:
            # Update avatar state
            updated_config = avatar_service.update_avatar_state(
                tool_id=tool_id,
                behavior_config=behavior_config,
                user_id=current_user["id"]
            )
            
            return {
                'behavior_config': behavior_config,
                'avatar_config': updated_config
            }
        else:
            return {
                'behavior_config': {},
                'avatar_config': avatar_service.get_tool_avatar(tool_id, current_user["id"])
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting avatar behavior: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error determining avatar behavior"
        )

async def _cleanup_old_files(upload_path: Path, current_filename: str):
    """Clean up old avatar files for a tool."""
    try:
        for file in upload_path.glob("*"):
            if file.name != current_filename and file.name != f"thumb_{current_filename}":
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Error deleting old file {file}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}") 