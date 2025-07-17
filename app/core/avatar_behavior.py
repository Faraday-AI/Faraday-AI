"""
Avatar Behavior System

This module provides context-aware behavior management for avatars,
automatically selecting appropriate expressions and gestures based on
conversation context and message content.
"""

from typing import Dict, Optional, Tuple, List
import re
from app.dashboard.schemas.avatar import EmotionType, GestureType
import numpy as np
from app.core.avatar_memory import memory_manager
from app.core.avatar_interaction import interaction_manager
from datetime import datetime
from app.dashboard.schemas.interaction_style import InteractionStyle

class EmotionIntensity:
    """Emotion intensity analysis."""
    
    # Intensity modifiers
    INTENSITY_MODIFIERS = {
        'very': 1.5,
        'extremely': 2.0,
        'somewhat': 0.7,
        'slightly': 0.5,
        'really': 1.3,
        'absolutely': 1.8,
        'totally': 1.6,
        'completely': 1.7,
        'barely': 0.3,
        'hardly': 0.4
    }
    
    # Punctuation intensity modifiers
    PUNCTUATION_MODIFIERS = {
        '!': 1.2,
        '!!': 1.4,
        '!!!': 1.6,
        '?!': 1.3,
        '...': 0.8
    }
    
    @classmethod
    def calculate_intensity(cls, message: str) -> float:
        """Calculate emotion intensity from message content."""
        base_intensity = 1.0
        words = message.lower().split()
        
        # Check for intensity modifiers
        for word in words:
            if word in cls.INTENSITY_MODIFIERS:
                base_intensity *= cls.INTENSITY_MODIFIERS[word]
        
        # Check for punctuation
        for punct, modifier in cls.PUNCTUATION_MODIFIERS.items():
            if punct in message:
                base_intensity *= modifier
        
        # Normalize between 0 and 1
        return min(max(base_intensity, 0.1), 1.0)

class EmotionBlending:
    """Handles smooth transitions between emotions."""
    
    # Emotion compatibility matrix (which emotions can blend)
    BLEND_MATRIX = {
        EmotionType.HAPPY: [EmotionType.EXCITED, EmotionType.SURPRISED],
        EmotionType.EXCITED: [EmotionType.HAPPY, EmotionType.SURPRISED],
        EmotionType.THOUGHTFUL: [EmotionType.CONCERNED, EmotionType.SURPRISED],
        EmotionType.SURPRISED: [EmotionType.HAPPY, EmotionType.EXCITED, EmotionType.CONCERNED],
        EmotionType.CONCERNED: [EmotionType.THOUGHTFUL, EmotionType.SURPRISED],
        EmotionType.NEUTRAL: list(EmotionType)  # Can blend with any
    }
    
    @classmethod
    def can_blend(cls, emotion1: EmotionType, emotion2: EmotionType) -> bool:
        """Check if two emotions can blend together."""
        return emotion2 in cls.BLEND_MATRIX.get(emotion1, [])
    
    @classmethod
    def get_transition_time(cls, emotion1: EmotionType, emotion2: EmotionType) -> float:
        """Get appropriate transition time between emotions."""
        if emotion1 == emotion2:
            return 0.0
        if cls.can_blend(emotion1, emotion2):
            return 0.5  # Fast transition for compatible emotions
        return 1.0  # Slower transition for incompatible emotions

class BehaviorTrigger:
    """Trigger patterns for avatar behaviors."""
    
    # Enhanced emotion triggers with context
    EMOTION_PATTERNS = {
        EmotionType.HAPPY: [
            r"great|excellent|perfect|well done|congratulations|amazing",
            r"😊|😄|👍|🎉",
            r"success|achieved|completed|solved|fixed",
            r"proud|pleased|delighted|glad"
        ],
        EmotionType.THOUGHTFUL: [
            r"hmm|let me think|analyzing|processing|calculating",
            r"🤔|💭",
            r"consider|evaluate|assess|examine|investigate",
            r"perhaps|maybe|possibly|potentially"
        ],
        EmotionType.SURPRISED: [
            r"wow|oh|unexpected|surprising|interesting",
            r"😮|😯|😲",
            r"incredible|unbelievable|amazing|astonishing",
            r"didn't expect|couldn't believe|never thought"
        ],
        EmotionType.CONCERNED: [
            r"error|warning|caution|careful|issue|problem",
            r"⚠️|❗|😟",
            r"worried|concerned|troubled|unsure",
            r"might not|could fail|risk|danger"
        ],
        EmotionType.EXCITED: [
            r"awesome|fantastic|incredible|amazing|wonderful",
            r"🎉|✨|🌟",
            r"can't wait|looking forward|excited to|thrilled",
            r"brilliant|outstanding|exceptional|remarkable"
        ]
    }
    
    # Enhanced gesture triggers with context
    GESTURE_PATTERNS = {
        GestureType.WAVE: [
            r"hello|hi|hey|welcome|goodbye|bye",
            r"👋|🤚",
            r"greetings|farewell|see you|catch you later",
            r"morning|evening|good day"
        ],
        GestureType.POINT: [
            r"look at|notice|see|here|there|this",
            r"👉|👆",
            r"observe|check|examine|view",
            r"specifically|particularly|notably"
        ],
        GestureType.NOD: [
            r"yes|correct|right|agree|exactly",
            r"👍|✅",
            r"indeed|precisely|absolutely|definitely",
            r"that's right|you got it|spot on"
        ],
        GestureType.THUMBS_UP: [
            r"good job|well done|great work|excellent",
            r"👍|🆙",
            r"impressive|outstanding|superb|terrific",
            r"keep it up|nice work|brilliant"
        ],
        GestureType.THINK: [
            r"analyzing|processing|calculating|considering",
            r"🤔|💭",
            r"evaluating|assessing|reviewing|studying",
            r"let me check|need to verify"
        ],
        GestureType.WRITE: [
            r"writing|noting|recording|documenting",
            r"✍️|📝",
            r"taking notes|making a note|jotting down",
            r"let me write|will record"
        ]
    }

class AvatarBehavior:
    """Manages context-aware avatar behavior."""
    
    def __init__(self):
        self._compile_patterns()
        self.style_adaptation = {
            InteractionStyle.FORMAL: {
                'gesture_duration': 0.8,
                'emotion_transition': 0.7,
                'gesture_frequency': 0.6,
                'emotion_intensity': 0.8,
                'preferred_emotions': [EmotionType.NEUTRAL, EmotionType.THOUGHTFUL, EmotionType.CONCERNED],
                'preferred_gestures': [GestureType.NOD, GestureType.THINK, GestureType.WRITE],
                'transition_style': 'smooth'
            },
            InteractionStyle.CASUAL: {
                'gesture_duration': 1.2,
                'emotion_transition': 1.3,
                'gesture_frequency': 1.4,
                'emotion_intensity': 1.2,
                'preferred_emotions': [EmotionType.HAPPY, EmotionType.NEUTRAL, EmotionType.SURPRISED],
                'preferred_gestures': [GestureType.WAVE, GestureType.THUMBS_UP, GestureType.POINT],
                'transition_style': 'bounce'
            },
            InteractionStyle.EMPATHETIC: {
                'gesture_duration': 1.1,
                'emotion_transition': 1.2,
                'gesture_frequency': 1.1,
                'emotion_intensity': 1.3,
                'preferred_emotions': [EmotionType.CONCERNED, EmotionType.HAPPY, EmotionType.THOUGHTFUL],
                'preferred_gestures': [GestureType.NOD, GestureType.WRITE, GestureType.THINK],
                'transition_style': 'gentle'
            },
            InteractionStyle.DIRECT: {
                'gesture_duration': 0.7,
                'emotion_transition': 0.8,
                'gesture_frequency': 0.7,
                'emotion_intensity': 0.9,
                'preferred_emotions': [EmotionType.NEUTRAL, EmotionType.THOUGHTFUL, EmotionType.CONCERNED],
                'preferred_gestures': [GestureType.POINT, GestureType.NOD, GestureType.WRITE],
                'transition_style': 'sharp'
            },
            InteractionStyle.PLAYFUL: {
                'gesture_duration': 1.4,
                'emotion_transition': 1.5,
                'gesture_frequency': 1.6,
                'emotion_intensity': 1.4,
                'preferred_emotions': [EmotionType.HAPPY, EmotionType.EXCITED, EmotionType.SURPRISED],
                'preferred_gestures': [GestureType.WAVE, GestureType.THUMBS_UP, GestureType.WRITE],
                'transition_style': 'bounce'
            }
        }
        
        # Define transition animations
        self.transition_animations = {
            'smooth': {
                'easing': 'easeInOutQuad',
                'duration_multiplier': 1.0,
                'blend_factor': 0.5
            },
            'bounce': {
                'easing': 'easeOutBounce',
                'duration_multiplier': 1.2,
                'blend_factor': 0.7
            },
            'gentle': {
                'easing': 'easeInOutSine',
                'duration_multiplier': 1.1,
                'blend_factor': 0.6
            },
            'sharp': {
                'easing': 'easeInOutCubic',
                'duration_multiplier': 0.9,
                'blend_factor': 0.4
            }
        }
        
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.emotion_patterns = {
            emotion: [re.compile(p, re.IGNORECASE) for p in patterns]
            for emotion, patterns in BehaviorTrigger.EMOTION_PATTERNS.items()
        }
        self.gesture_patterns = {
            gesture: [re.compile(p, re.IGNORECASE) for p in patterns]
            for gesture, patterns in BehaviorTrigger.GESTURE_PATTERNS.items()
        }
        
    def _get_style_aware_emotion(
        self,
        message: str,
        current_emotion: Optional[EmotionType],
        style: str
    ) -> Optional[EmotionType]:
        """Get emotion that aligns with current interaction style."""
        # Get style preferences
        style_prefs = self.style_adaptation[style]
        preferred_emotions = style_prefs['preferred_emotions']
        
        # First try to detect emotion from message
        detected_emotion = self._detect_emotion(message, current_emotion)
        
        if detected_emotion:
            # If detected emotion is in preferred list, use it
            if detected_emotion in preferred_emotions:
                return detected_emotion
            # Otherwise, try to find a compatible preferred emotion
            for pref_emotion in preferred_emotions:
                if EmotionBlending.can_blend(detected_emotion, pref_emotion):
                    return pref_emotion
        
        # If no emotion detected or compatible, use most appropriate preferred emotion
        if current_emotion and current_emotion in preferred_emotions:
            return current_emotion
        return preferred_emotions[0]
        
    def _get_style_aware_gesture(
        self,
        message: str,
        current_gesture: Optional[GestureType],
        style: str
    ) -> Optional[GestureType]:
        """Get gesture that aligns with current interaction style."""
        # Get style preferences
        style_prefs = self.style_adaptation[style]
        preferred_gestures = style_prefs['preferred_gestures']
        
        # First try to detect gesture from message
        detected_gesture = self._detect_gesture(message, current_gesture)
        
        if detected_gesture:
            # If detected gesture is in preferred list, use it
            if detected_gesture in preferred_gestures:
                return detected_gesture
            # Otherwise, use first preferred gesture
            return preferred_gestures[0]
        
        # If no gesture detected, use most appropriate preferred gesture
        if current_gesture and current_gesture in preferred_gestures:
            return current_gesture
        return preferred_gestures[0]
        
    def analyze_message(
        self,
        message: str,
        current_emotion: Optional[EmotionType] = None,
        current_gesture: Optional[GestureType] = None,
        context: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ) -> Tuple[Optional[EmotionType], Optional[GestureType], float]:
        """Analyze message content to determine appropriate emotion and gesture."""
        # Process interaction and get style modifiers
        style_modifiers = interaction_manager.process_interaction(message, timestamp)
        current_style = style_modifiers['current_style']
        
        # Get style-aware behavior
        new_emotion = self._get_style_aware_emotion(message, current_emotion, current_style)
        new_gesture = self._get_style_aware_gesture(message, current_gesture, current_style)
        
        # Calculate base intensity
        base_intensity = EmotionIntensity.calculate_intensity(message)
        
        # Adjust intensity based on style
        style_intensity = self.style_adaptation[current_style]['emotion_intensity']
        intensity = min(1.0, base_intensity * style_intensity)
        
        return new_emotion, new_gesture, intensity
        
    def _detect_emotion(
        self,
        message: str,
        current_emotion: Optional[EmotionType]
    ) -> Optional[EmotionType]:
        """Detect appropriate emotion from message content."""
        matched_emotions = []
        for emotion, patterns in self.emotion_patterns.items():
            if any(p.search(message) for p in patterns):
                matched_emotions.append(emotion)
        
        if not matched_emotions:
            return None
            
        # If current emotion can blend with any matched emotion, prefer that one
        if current_emotion:
            for emotion in matched_emotions:
                if EmotionBlending.can_blend(current_emotion, emotion):
                    return emotion
        
        return matched_emotions[0]
        
    def _detect_gesture(
        self,
        message: str,
        current_gesture: Optional[GestureType]
    ) -> Optional[GestureType]:
        """Detect appropriate gesture from message content."""
        for gesture, patterns in self.gesture_patterns.items():
            if any(p.search(message) for p in patterns):
                if gesture != current_gesture:
                    return gesture
        return None
        
    def get_behavior_config(
        self,
        message: str,
        current_emotion: Optional[EmotionType] = None,
        current_gesture: Optional[GestureType] = None,
        context: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """Get complete behavior configuration for a message."""
        # Get behavior influence from personality
        influence = memory_manager.get_behavior_influence()
        
        # Get interaction style modifiers
        style_modifiers = interaction_manager.process_interaction(message, timestamp)
        current_style = style_modifiers['current_style']
        style_adaptation = self.style_adaptation[current_style]
        transition_style = self.transition_animations[style_adaptation['transition_style']]
        
        # Combine influences with style adaptation
        combined_influence = {
            'emotion_intensity': influence['emotion_intensity'] * 
                               style_modifiers['emotion_intensity'] * 
                               style_adaptation['emotion_intensity'],
            'transition_speed': influence['transition_speed'] * 
                              style_modifiers['interaction_speed'] * 
                              style_adaptation['emotion_transition'],
            'state_persistence': influence['state_persistence'],
            'response_intensity': influence['response_intensity'] * 
                                style_modifiers['gesture_frequency'] * 
                                style_adaptation['gesture_frequency']
        }
        
        # Check for inactivity reset
        if memory_manager.should_reset_state():
            current_emotion = None
            current_gesture = None
            memory_manager.clear()
            interaction_manager.clear()
        
        new_emotion, new_gesture, intensity = self.analyze_message(
            message,
            current_emotion,
            current_gesture,
            context,
            timestamp
        )
        
        config = {}
        
        if new_emotion:
            # Base transition speed on combined influence and transition style
            base_speed = 1.0
            if current_emotion:
                base_speed = EmotionBlending.get_transition_time(
                    current_emotion,
                    new_emotion
                )
            transition_speed = base_speed * combined_influence['transition_speed'] * transition_style['duration_multiplier']
            
            config['expression_config'] = {
                'emotion': new_emotion,
                'intensity': intensity,
                'transition_speed': transition_speed,
                'auto_reset': True,
                'reset_delay': 3.0 * combined_influence['state_persistence'],
                'transition_style': transition_style['easing'],
                'blend_factor': transition_style['blend_factor']
            }
            
        if new_gesture:
            config['gesture_config'] = {
                'gesture': new_gesture,
                'loop_count': 1,
                'speed': min(1.5, intensity * combined_influence['response_intensity']),
                'blend_duration': 0.3 * combined_influence['transition_speed'] * transition_style['duration_multiplier'],
                'auto_complete': True,
                'duration': style_adaptation['gesture_duration'],
                'transition_style': transition_style['easing']
            }
            
        # Add context summary to config
        context_summary = memory_manager.get_context_summary()
        if context_summary:
            config['context'] = context_summary
            
        # Add interaction style info
        config['interaction_style'] = {
            'current_style': current_style,
            'formality_level': style_modifiers['response_formality'],
            'adaptation': style_adaptation,
            'transition_style': transition_style
        }
            
        return config

# Initialize global behavior manager
behavior_manager = AvatarBehavior() 