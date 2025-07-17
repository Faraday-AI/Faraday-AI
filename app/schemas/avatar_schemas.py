"""
Avatar Schemas

This module defines the Pydantic schemas for avatar-related models.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Union
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict

class AvatarType(str, Enum):
    """Types of avatars supported by the system."""
    STATIC = "static"
    ANIMATED = "animated"
    THREE_D = "3d"

class EmotionType(str, Enum):
    """Possible avatar emotions."""
    HAPPY = "happy"
    SAD = "sad"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CONFUSED = "confused"
    THOUGHTFUL = "thoughtful"
    CONCERNED = "concerned"
    SURPRISED = "surprised"
    FOCUSED = "focused"
    ENCOURAGING = "encouraging"

class GestureType(str, Enum):
    """Possible avatar gestures."""
    WAVE = "wave"
    NOD = "nod"
    POINT = "point"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    SHRUG = "shrug"
    CLAP = "clap"
    THINK = "think"
    WRITE = "write"
    TEACH = "teach"

class VoiceProvider(str, Enum):
    """Supported voice providers."""
    GOOGLE = "google"
    AMAZON = "amazon"
    MICROSOFT = "microsoft"
    ELEVENLABS = "elevenlabs"

class ExpressionConfig(BaseModel):
    """Configuration for avatar expressions."""
    emotion: EmotionType = Field(EmotionType.NEUTRAL, description="Current emotion state")
    intensity: float = Field(1.0, ge=0.0, le=1.0, description="Intensity of the emotion")
    transition_speed: float = Field(1.0, ge=0.1, le=5.0, description="Speed of emotion transitions")
    auto_reset: bool = Field(True, description="Whether to reset to neutral after a delay")
    reset_delay: float = Field(3.0, ge=0.5, description="Seconds before resetting to neutral")

class GestureConfig(BaseModel):
    """Configuration for avatar gestures."""
    gesture: GestureType = Field(None, description="Current gesture")
    loop_count: int = Field(1, ge=1, description="Number of times to loop the gesture")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Gesture animation speed")
    blend_duration: float = Field(0.3, ge=0.1, le=1.0, description="Blend time between gestures")
    auto_complete: bool = Field(True, description="Whether to complete current gesture before new one")

class AvatarConfig(BaseModel):
    """Base configuration for avatars."""
    type: AvatarType = Field(..., description="Type of avatar")
    url: str = Field(..., description="URL to the avatar asset")
    config: Optional[Dict] = Field(None, description="Additional configuration for the avatar")
    voice_enabled: bool = Field(False, description="Whether voice is enabled for this avatar")
    voice_config: Optional[Dict] = Field(None, description="Voice configuration")
    expression_config: Optional[ExpressionConfig] = Field(
        None,
        description="Configuration for avatar expressions"
    )
    gesture_config: Optional[GestureConfig] = Field(
        None,
        description="Configuration for avatar gestures"
    )

    @validator('config')
    def validate_config(cls, v, values):
        if v is not None and 'type' in values:
            required_fields = {
                AvatarType.STATIC: ["url"],
                AvatarType.ANIMATED: ["url", "animation_type", "fps"],
                AvatarType.THREE_D: ["model_url", "animations", "scale"]
            }
            for field in required_fields[values['type']]:
                if field not in v:
                    raise ValueError(f"Missing required field for {values['type']} avatar: {field}")
        return v

    @validator('expression_config')
    def validate_expression_config(cls, v, values):
        if v is not None and values.get('type') == AvatarType.STATIC:
            raise ValueError("Expression config not supported for static avatars")
        return v

    @validator('gesture_config')
    def validate_gesture_config(cls, v, values):
        if v is not None and values.get('type') == AvatarType.STATIC:
            raise ValueError("Gesture config not supported for static avatars")
        return v

class VoicePreference(BaseModel):
    """Schema for voice preferences."""
    
    id: str
    avatar_id: str
    user_id: str
    voice_id: str
    language: str
    speed: int = 100
    pitch: int = 100
    provider: VoiceProvider
    style: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AvatarCustomization(BaseModel):
    """Schema for avatar customization."""
    scale: Optional[float] = Field(1.0, ge=0.1, le=5.0, description="Avatar scale")
    position: Optional[Dict[str, float]] = Field(
        None,
        description="Avatar position in 3D space (x, y, z)"
    )
    rotation: Optional[Dict[str, float]] = Field(
        None,
        description="Avatar rotation in 3D space (x, y, z)"
    )
    color: Optional[str] = Field(None, description="Avatar color (hex code)")
    opacity: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Avatar opacity")

class UserAvatarPreferences(BaseModel):
    """Schema for user-specific avatar preferences."""
    avatar_customization: Optional[AvatarCustomization] = Field(
        None,
        description="User-specific avatar customization settings"
    )
    voice_preferences: Optional[VoicePreference] = Field(
        None,
        description="User-specific voice preferences"
    )

class FileInfo(BaseModel):
    """Schema for uploaded file information."""
    original_size: int = Field(..., description="Original file size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    dimensions: Optional[Dict[str, int]] = Field(
        None,
        description="Image dimensions (width, height)"
    )
    thumbnail_path: Optional[str] = Field(
        None,
        description="Path to the generated thumbnail"
    )

class AvatarResponse(BaseModel):
    """Schema for avatar response."""
    
    id: str
    user_id: str
    type: AvatarType
    style: AvatarStyle
    mood: AvatarMood
    expression: AvatarExpression
    customizations: List[AvatarCustomizationResponse]
    voice_preferences: Optional[VoicePreference] = Field(
        default=None,
        description="Voice preferences for the avatar"
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AvatarCreate(BaseModel):
    """Schema for creating an avatar."""
    
    type: AvatarType
    style: AvatarStyle
    mood: AvatarMood = AvatarMood.NEUTRAL
    expression: AvatarExpression = AvatarExpression.NEUTRAL
    customizations: Optional[List[AvatarCustomizationCreate]] = None
    voice_preferences: Optional[VoicePreference] = Field(
        default=None,
        description="Voice preferences for the avatar"
    )

class AvatarUpdate(BaseModel):
    """Schema for updating avatar configuration."""
    avatar_type: AvatarType = Field(..., description="Type of avatar")
    avatar_url: str = Field(..., description="URL to the avatar asset")
    avatar_config: Optional[Dict] = Field(None, description="Additional configuration for the avatar")
    voice_enabled: bool = Field(False, description="Whether voice is enabled for this avatar")
    voice_config: Optional[Dict] = Field(None, description="Voice configuration")

class AvatarExpression(BaseModel):
    """Schema for avatar expressions combining emotion and gesture."""
    emotion: EmotionType
    gesture: Optional[GestureType] = None
    intensity: float = 1.0  # Scale from 0.0 to 1.0
    duration: float = 1.0  # Duration in seconds

class AvatarState(BaseModel):
    """Schema for current avatar state."""
    current_emotion: EmotionType = EmotionType.NEUTRAL
    current_gesture: Optional[GestureType] = None
    is_speaking: bool = False
    is_listening: bool = False
    is_thinking: bool = False
    custom_state: Optional[Dict] = None

class AvatarPreferences(BaseModel):
    """Schema for avatar customization preferences."""
    name: str
    appearance: Dict
    voice: Dict
    behavior_settings: Dict
    enabled_emotions: List[EmotionType]
    enabled_gestures: List[GestureType]
    interaction_style: Dict

class AvatarUploadResponse(BaseModel):
    """Response schema for avatar upload."""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    file_url: str = Field(..., description="URL where the file can be accessed")
    file_info: FileInfo = Field(..., description="Information about the uploaded file")
    avatar_config: Optional[AvatarConfig] = Field(None, description="Generated avatar configuration")
    thumbnail_url: Optional[str] = Field(None, description="URL of the generated thumbnail")
    processing_status: str = Field("completed", description="Status of file processing")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the file was uploaded")

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "avatar_123",
                "file_url": "https://storage.example.com/avatars/avatar_123.glb",
                "file_info": {
                    "original_size": 1024000,
                    "mime_type": "model/gltf-binary",
                    "dimensions": None,
                    "thumbnail_path": "/thumbnails/avatar_123.png"
                },
                "avatar_config": {
                    "type": "3d",
                    "url": "https://storage.example.com/avatars/avatar_123.glb",
                    "config": {
                        "model_url": "https://storage.example.com/avatars/avatar_123.glb",
                        "animations": ["idle", "talk", "gesture"],
                        "scale": 1.0
                    }
                },
                "thumbnail_url": "https://storage.example.com/thumbnails/avatar_123.png",
                "processing_status": "completed",
                "created_at": "2024-03-20T10:30:00Z"
            }
        } 