from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from app.dashboard.models.tool_registry import Tool, UserTool
from fastapi import HTTPException
import os
from pathlib import Path
import json
from functools import lru_cache
import hashlib
from datetime import datetime, timedelta
import mimetypes
from PIL import Image
import logging
from app.core.avatar_behavior import behavior_manager
from app.dashboard.schemas.avatar import EmotionType, GestureType

logger = logging.getLogger(__name__)

class AvatarService:
    def __init__(self, db: Session):
        self.db = db
        self.avatar_base_path = Path("static/avatars")
        self.avatar_base_path.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(minutes=5)
        self._setup_mime_types()

    def _setup_mime_types(self):
        """Setup additional MIME types for avatar files."""
        mimetypes.add_type('image/webp', '.webp')
        mimetypes.add_type('model/gltf-binary', '.glb')
        mimetypes.add_type('model/gltf+json', '.gltf')
        mimetypes.add_type('application/x-fbx', '.fbx')

    @lru_cache(maxsize=100)
    def get_tool_avatar(self, tool_id: str, user_id: Optional[str] = None) -> Dict:
        """Get avatar configuration for a tool, including user-specific customizations."""
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")

        avatar_config = {
            "type": tool.avatar_type,
            "url": tool.avatar_url,
            "config": tool.avatar_config or {},
            "voice_enabled": tool.voice_enabled,
            "voice_config": tool.voice_config or {},
            "last_updated": tool.updated_at
        }

        # Add user-specific customizations if user_id is provided
        if user_id:
            user_tool = self.db.query(UserTool).filter(
                UserTool.user_id == user_id,
                UserTool.tool_id == tool_id
            ).first()
            
            if user_tool:
                if user_tool.avatar_customization:
                    avatar_config["customization"] = user_tool.avatar_customization
                if user_tool.voice_preferences:
                    avatar_config["voice_preferences"] = user_tool.voice_preferences

        return avatar_config

    def update_tool_avatar(
        self,
        tool_id: str,
        avatar_type: str,
        avatar_url: str,
        avatar_config: Optional[Dict] = None,
        voice_enabled: bool = False,
        voice_config: Optional[Dict] = None
    ) -> Dict:
        """Update avatar configuration for a tool."""
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")

        # Validate the update
        self._validate_avatar_update(avatar_type, avatar_url, avatar_config)

        tool.avatar_type = avatar_type
        tool.avatar_url = avatar_url
        tool.avatar_config = avatar_config
        tool.voice_enabled = voice_enabled
        tool.voice_config = voice_config
        tool.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(tool)

        # Clear cache for this tool
        self.get_tool_avatar.cache_clear()

        return {
            "type": tool.avatar_type,
            "url": tool.avatar_url,
            "config": tool.avatar_config,
            "voice_enabled": tool.voice_enabled,
            "voice_config": tool.voice_config,
            "last_updated": tool.updated_at
        }

    def _validate_avatar_update(
        self,
        avatar_type: str,
        avatar_url: str,
        avatar_config: Optional[Dict]
    ) -> None:
        """Validate avatar update parameters."""
        if avatar_type not in self.get_available_avatar_types():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid avatar type: {avatar_type}"
            )

        if not avatar_url:
            raise HTTPException(
                status_code=400,
                detail="Avatar URL is required"
            )

        if avatar_config:
            self.validate_avatar_config(avatar_config)

    def update_user_avatar_preferences(
        self,
        user_id: str,
        tool_id: str,
        avatar_customization: Optional[Dict] = None,
        voice_preferences: Optional[Dict] = None
    ) -> Dict:
        """Update user-specific avatar preferences for a tool."""
        user_tool = self.db.query(UserTool).filter(
            UserTool.user_id == user_id,
            UserTool.tool_id == tool_id
        ).first()

        if not user_tool:
            raise HTTPException(status_code=404, detail="User tool settings not found")

        if avatar_customization is not None:
            self._validate_avatar_customization(avatar_customization)
            user_tool.avatar_customization = avatar_customization

        if voice_preferences is not None:
            self._validate_voice_preferences(voice_preferences)
            user_tool.voice_preferences = voice_preferences

        self.db.commit()
        self.db.refresh(user_tool)

        # Clear cache for this user's tool
        self.get_tool_avatar.cache_clear()

        return {
            "avatar_customization": user_tool.avatar_customization,
            "voice_preferences": user_tool.voice_preferences
        }

    def _validate_avatar_customization(self, customization: Dict) -> None:
        """Validate avatar customization settings."""
        if not isinstance(customization, dict):
            raise HTTPException(
                status_code=400,
                detail="Avatar customization must be a dictionary"
            )

    def _validate_voice_preferences(self, preferences: Dict) -> None:
        """Validate voice preferences."""
        if not isinstance(preferences, dict):
            raise HTTPException(
                status_code=400,
                detail="Voice preferences must be a dictionary"
            )

        required_fields = ["voice_id", "language", "speed"]
        for field in required_fields:
            if field not in preferences:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required voice preference: {field}"
                )

    def validate_avatar_config(self, config: Dict) -> bool:
        """Validate avatar configuration."""
        required_fields = {
            "static": ["url"],
            "animated": ["url", "animation_type", "fps"],
            "3d": ["model_url", "animations", "scale"]
        }

        avatar_type = config.get("type", "static")
        if avatar_type not in required_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid avatar type: {avatar_type}"
            )

        for field in required_fields[avatar_type]:
            if field not in config:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field for {avatar_type} avatar: {field}"
                )

        return True

    def get_available_avatar_types(self) -> Dict:
        """Get available avatar types and their configurations."""
        return {
            "static": {
                "description": "Static image avatar",
                "required_fields": ["url"],
                "supported_formats": ["png", "jpg", "gif", "webp"],
                "max_size": "5MB",
                "recommended_dimensions": "256x256"
            },
            "animated": {
                "description": "Animated 2D avatar",
                "required_fields": ["url", "animation_type", "fps"],
                "supported_formats": ["gif", "webp", "mp4"],
                "max_size": "10MB",
                "max_duration": "30s",
                "recommended_fps": 30
            },
            "3d": {
                "description": "3D model avatar",
                "required_fields": ["model_url", "animations", "scale"],
                "supported_formats": ["glb", "gltf", "fbx"],
                "max_size": "20MB",
                "max_polygons": "100k",
                "supported_animations": ["idle", "talking", "gestures"]
            }
        }

    def process_uploaded_file(
        self,
        file_path: Path,
        avatar_type: str,
        max_size: int = 20 * 1024 * 1024  # 20MB default
    ) -> Dict:
        """Process and validate an uploaded avatar file."""
        if not file_path.exists():
            raise HTTPException(status_code=400, detail="File not found")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size/1024/1024}MB"
            )

        # Get file metadata
        mime_type = mimetypes.guess_type(file_path)[0]
        if not mime_type:
            raise HTTPException(status_code=400, detail="Could not determine file type")

        # Validate file type
        allowed_types = self.get_available_avatar_types()[avatar_type]["supported_formats"]
        file_ext = file_path.suffix.lower()[1:]  # Remove the dot
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported for {avatar_type} avatar"
            )

        # Process image files
        if mime_type.startswith('image/'):
            try:
                with Image.open(file_path) as img:
                    # Generate thumbnail
                    thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
                    img.thumbnail((256, 256))
                    img.save(thumbnail_path)
                    
                    return {
                        "original_size": file_size,
                        "mime_type": mime_type,
                        "dimensions": img.size,
                        "thumbnail_path": str(thumbnail_path)
                    }
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error processing image file"
                )

        return {
            "original_size": file_size,
            "mime_type": mime_type
        }

    def get_avatar_behavior(
        self,
        tool_id: str,
        message: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Get avatar behavior configuration based on message content.
        
        Args:
            tool_id: Tool ID
            message: Message content to analyze
            user_id: Optional user ID for customization
            
        Returns:
            Dict containing behavior configuration
        """
        # Get current avatar state
        avatar_config = self.get_tool_avatar(tool_id, user_id)
        
        current_emotion = None
        if avatar_config.get('expression_config'):
            current_emotion = avatar_config['expression_config'].get('emotion')
            
        current_gesture = None
        if avatar_config.get('gesture_config'):
            current_gesture = avatar_config['gesture_config'].get('gesture')
        
        # Get behavior configuration
        behavior_config = behavior_manager.get_behavior_config(
            message=message,
            current_emotion=current_emotion,
            current_gesture=current_gesture
        )
        
        # Apply any user customizations
        if user_id and behavior_config:
            user_tool = self.db.query(UserTool).filter(
                UserTool.user_id == user_id,
                UserTool.tool_id == tool_id
            ).first()
            
            if user_tool and user_tool.avatar_customization:
                if 'expression_config' in behavior_config:
                    behavior_config['expression_config'].update(
                        user_tool.avatar_customization.get('expression_settings', {})
                    )
                if 'gesture_config' in behavior_config:
                    behavior_config['gesture_config'].update(
                        user_tool.avatar_customization.get('gesture_settings', {})
                    )
        
        return behavior_config
        
    def update_avatar_state(
        self,
        tool_id: str,
        behavior_config: Dict,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Update avatar state with new behavior configuration.
        
        Args:
            tool_id: Tool ID
            behavior_config: New behavior configuration
            user_id: Optional user ID for customization
            
        Returns:
            Updated avatar configuration
        """
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
            
        # Update tool's avatar configuration
        if 'expression_config' in behavior_config:
            tool.avatar_config = tool.avatar_config or {}
            tool.avatar_config['expression'] = behavior_config['expression_config']
            
        if 'gesture_config' in behavior_config:
            tool.avatar_config = tool.avatar_config or {}
            tool.avatar_config['gesture'] = behavior_config['gesture_config']
            
        tool.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Clear cache
        self.get_tool_avatar.cache_clear()
        
        # Return updated configuration
        return self.get_tool_avatar(tool_id, user_id) 