"""
Avatar Types

This module defines the enums used for avatar management.
"""

import enum

class AvatarType(str, enum.Enum):
    """Types of avatars supported by the system."""
    STATIC = "static"
    ANIMATED = "animated"
    THREE_D = "3d"

class AvatarStyle(str, enum.Enum):
    """Styles of avatars supported by the system."""
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    ANIME = "anime"
    PIXEL = "pixel"
    MINIMAL = "minimal"
    CUSTOM = "custom"

class AvatarMood(str, enum.Enum):
    """Moods that avatars can express."""
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

class AvatarExpression(str, enum.Enum):
    """Expressions that avatars can make."""
    SMILE = "smile"
    FROWN = "frown"
    NEUTRAL = "neutral"
    SURPRISED = "surprised"
    THINKING = "thinking"
    WINK = "wink"
    LAUGH = "laugh"
    WORRIED = "worried"
    DETERMINED = "determined"
    ENCOURAGING = "encouraging"

class EmotionType(str, enum.Enum):
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

class GestureType(str, enum.Enum):
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

class VoiceProvider(str, enum.Enum):
    """Supported voice providers."""
    GOOGLE = "google"
    AMAZON = "amazon"
    MICROSOFT = "microsoft"
    ELEVENLABS = "elevenlabs"

class AvatarAccessory(str, enum.Enum):
    """Accessories that can be added to avatars."""
    GLASSES = "glasses"
    HAT = "hat"
    SCARF = "scarf"
    JEWELRY = "jewelry"
    BADGE = "badge"
    MASK = "mask"
    CUSTOM = "custom"

class AvatarBackground(str, enum.Enum):
    """Background styles for avatars."""
    SOLID = "solid"
    GRADIENT = "gradient"
    PATTERN = "pattern"
    SCENE = "scene"
    BLUR = "blur"
    CUSTOM = "custom"

class AvatarAnimation(str, enum.Enum):
    """Animation types for avatars."""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    DANCE = "dance"
    WAVE = "wave"
    TALK = "talk"
    THINK = "think"
    CUSTOM = "custom"

class CustomizationType(str, enum.Enum):
    """Types of avatar customizations supported by the system."""
    APPEARANCE = "appearance"
    VOICE = "voice"
    EXPRESSION = "expression"
    GESTURE = "gesture"
    ACCESSORY = "accessory"
    BACKGROUND = "background"
    ANIMATION = "animation"
    CUSTOM = "custom" 