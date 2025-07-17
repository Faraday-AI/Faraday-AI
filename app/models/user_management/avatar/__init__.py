"""
Avatar Models

This module provides models for managing user avatars and their customization.
"""

from .base import Avatar as BaseAvatar
from .models import UserAvatar, AvatarCustomization as ModelsAvatarCustomization, AvatarTemplate
from .customization import AvatarCustomization as BaseAvatarCustomization
from .voice import VoicePreference, Voice, VoiceTemplate
from .types import (
    AvatarType,
    AvatarStyle,
    AvatarMood,
    AvatarExpression,
    VoiceProvider,
    AvatarAccessory,
    AvatarBackground,
    AvatarAnimation
)

__all__ = [
    'BaseAvatar',
    'UserAvatar',
    'BaseAvatarCustomization',
    'ModelsAvatarCustomization',
    'AvatarTemplate',
    'VoicePreference',
    'Voice',
    'VoiceTemplate',
    'AvatarType',
    'AvatarStyle',
    'AvatarMood',
    'AvatarExpression',
    'VoiceProvider',
    'AvatarAccessory',
    'AvatarBackground',
    'AvatarAnimation'
] 