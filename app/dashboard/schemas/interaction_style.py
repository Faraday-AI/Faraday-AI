"""
Interaction style schemas for the dashboard.
"""

from enum import Enum

class InteractionStyle(str, Enum):
    """Enumeration of possible interaction styles."""
    FORMAL = "formal"  # Professional, structured interactions
    CASUAL = "casual"  # Relaxed, friendly interactions
    EMPATHETIC = "empathetic"  # Emotionally attuned interactions
    DIRECT = "direct"  # Clear, straightforward interactions
    PLAYFUL = "playful"  # Fun, engaging interactions

    @classmethod
    def get_default_style(cls) -> "InteractionStyle":
        """Get the default interaction style."""
        return cls.CASUAL

    @classmethod
    def get_style_description(cls, style: "InteractionStyle") -> str:
        """Get a description of the interaction style."""
        descriptions = {
            cls.FORMAL: "Professional and structured communication style",
            cls.CASUAL: "Relaxed and friendly communication style",
            cls.EMPATHETIC: "Emotionally attuned and supportive communication style",
            cls.DIRECT: "Clear and straightforward communication style",
            cls.PLAYFUL: "Fun and engaging communication style"
        }
        return descriptions.get(style, "Unknown interaction style")

    @classmethod
    def get_style_characteristics(cls, style: "InteractionStyle") -> dict:
        """Get characteristics of the interaction style."""
        characteristics = {
            cls.FORMAL: {
                "formality_level": 0.9,
                "response_length": "medium",
                "emotion_range": "limited",
                "gesture_frequency": "low",
                "vocabulary_level": "advanced"
            },
            cls.CASUAL: {
                "formality_level": 0.4,
                "response_length": "variable",
                "emotion_range": "moderate",
                "gesture_frequency": "moderate",
                "vocabulary_level": "conversational"
            },
            cls.EMPATHETIC: {
                "formality_level": 0.6,
                "response_length": "medium",
                "emotion_range": "wide",
                "gesture_frequency": "moderate",
                "vocabulary_level": "supportive"
            },
            cls.DIRECT: {
                "formality_level": 0.7,
                "response_length": "short",
                "emotion_range": "limited",
                "gesture_frequency": "low",
                "vocabulary_level": "precise"
            },
            cls.PLAYFUL: {
                "formality_level": 0.2,
                "response_length": "variable",
                "emotion_range": "wide",
                "gesture_frequency": "high",
                "vocabulary_level": "casual"
            }
        }
        return characteristics.get(style, {}) 