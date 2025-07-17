"""
Avatar schemas for the dashboard.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Union
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict

class AvatarType(str, Enum):
    STATIC = "static"
    ANIMATED = "animated"
    THREE_D = "3d"

class AvatarStyle(str, Enum):
    """Enumeration of possible avatar styles."""
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    ANIME = "anime"
    PIXEL = "pixel"
    MINIMAL = "minimal"
    CUSTOM = "custom"

class AvatarMood(str, Enum):
    """Enumeration of possible avatar moods."""
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

class AvatarExpression(str, Enum):
    """Enumeration of possible avatar expressions."""
    NEUTRAL = "neutral"
    SMILE = "smile"
    FROWN = "frown"
    SURPRISE = "surprise"
    THINKING = "thinking"
    WINK = "wink"
    BLUSH = "blush"
    ANGRY = "angry"
    WORRIED = "worried"
    DETERMINED = "determined"

class VoiceProvider(str, Enum):
    GOOGLE = "google"
    AMAZON = "amazon"
    MICROSOFT = "microsoft"
    ELEVENLABS = "elevenlabs"

class EmotionType(str, Enum):
    """Enumeration of possible avatar emotions."""
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
    """Enumeration of possible avatar gestures."""
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

class AvatarCustomizationResponse(AvatarCustomization):
    """Response schema for avatar customization."""
    id: str = Field(..., description="Unique identifier for the customization")
    created_at: datetime = Field(..., description="When the customization was created")
    updated_at: datetime = Field(..., description="When the customization was last updated")

class AvatarCustomizationCreate(AvatarCustomization):
    """Schema for creating avatar customization."""
    pass

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

class BehaviorType(str, Enum):
    """Enumeration of possible avatar behaviors."""
    IDLE = "idle"
    TEACHING = "teaching"
    LISTENING = "listening"
    RESPONDING = "responding"
    EXPLAINING = "explaining"
    ENCOURAGING = "encouraging"
    CORRECTING = "correcting"
    DEMONSTRATING = "demonstrating"
    INTERACTING = "interacting"
    CUSTOM = "custom"

class BehaviorTrigger(str, Enum):
    """Enumeration of behavior trigger types."""
    IMMEDIATE = "immediate"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    TIMED = "timed"
    CONDITIONAL = "conditional"

class BehaviorPriority(str, Enum):
    """Enumeration of behavior priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    OVERRIDE = "override"

class BehaviorTransition(BaseModel):
    """Configuration for behavior transitions."""
    blend_duration: float = Field(0.5, ge=0.0, le=5.0, description="Duration of transition blend in seconds")
    ease_type: str = Field("linear", description="Type of easing function for the transition")
    interrupt_current: bool = Field(False, description="Whether to interrupt current behavior")
    fade_audio: bool = Field(True, description="Whether to fade audio during transition")

class BehaviorConfig(BaseModel):
    """Configuration for a specific behavior."""
    emotion: Optional[EmotionType] = Field(None, description="Emotion to display during behavior")
    gesture: Optional[GestureType] = Field(None, description="Gesture to perform during behavior")
    voice_style: Optional[str] = Field(None, description="Voice style to use during behavior")
    duration: Optional[float] = Field(None, ge=0.0, description="Duration in seconds (None for indefinite)")
    loop: bool = Field(False, description="Whether to loop the behavior")
    intensity: float = Field(1.0, ge=0.0, le=1.0, description="Intensity of the behavior")
    custom_params: Optional[Dict] = Field(None, description="Additional behavior-specific parameters")

class AvatarBehaviorRequest(BaseModel):
    """Request schema for controlling avatar behavior."""
    behavior_type: BehaviorType = Field(..., description="Type of behavior to perform")
    trigger: BehaviorTrigger = Field(
        BehaviorTrigger.IMMEDIATE,
        description="What triggers this behavior"
    )
    priority: BehaviorPriority = Field(
        BehaviorPriority.NORMAL,
        description="Priority level of the behavior"
    )
    config: BehaviorConfig = Field(..., description="Configuration for the behavior")
    transition: Optional[BehaviorTransition] = Field(
        None,
        description="Configuration for behavior transition"
    )
    conditions: Optional[Dict] = Field(
        None,
        description="Conditions that must be met for conditional triggers"
    )
    callback_url: Optional[str] = Field(
        None,
        description="URL to call when behavior is complete"
    )

    @validator('callback_url')
    def validate_callback_url(cls, v):
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError("Callback URL must be a valid HTTP(S) URL")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "behavior_type": "teaching",
                "trigger": "immediate",
                "priority": "normal",
                "config": {
                    "emotion": "encouraging",
                    "gesture": "teach",
                    "voice_style": "instructional",
                    "duration": 10.0,
                    "loop": False,
                    "intensity": 0.8,
                    "custom_params": {
                        "teaching_style": "interactive",
                        "pace": "moderate"
                    }
                },
                "transition": {
                    "blend_duration": 0.5,
                    "ease_type": "ease-in-out",
                    "interrupt_current": False,
                    "fade_audio": True
                }
            }
        }

class AvatarBehaviorResponse(BaseModel):
    """Response schema for avatar behavior status."""
    behavior_type: BehaviorType = Field(..., description="Type of behavior performed")
    status: str = Field(..., description="Current status of the behavior (started, in_progress, completed, failed)")
    started_at: datetime = Field(..., description="When the behavior started")
    completed_at: Optional[datetime] = Field(None, description="When the behavior completed (if applicable)")
    duration: Optional[float] = Field(None, description="Duration of the behavior in seconds")
    error: Optional[str] = Field(None, description="Error message if behavior failed")
    current_state: AvatarState = Field(..., description="Current state of the avatar")
    metadata: Optional[Dict] = Field(None, description="Additional behavior-specific metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "behavior_type": "teaching",
                "status": "completed",
                "started_at": "2024-03-20T10:30:00Z",
                "completed_at": "2024-03-20T10:40:00Z",
                "duration": 10.0,
                "error": None,
                "current_state": {
                    "current_emotion": "encouraging",
                    "current_gesture": "teach",
                    "is_speaking": False,
                    "is_listening": False,
                    "is_thinking": False,
                    "custom_state": None
                },
                "metadata": {
                    "teaching_style": "interactive",
                    "pace": "moderate"
                }
            }
        } 