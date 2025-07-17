"""
Avatar Memory System

This module provides short-term memory for avatar behavior,
helping maintain contextual awareness and behavior consistency.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque, Counter
import numpy as np
from app.dashboard.schemas.avatar import EmotionType, GestureType

class PersonalityTrait:
    """Personality traits that influence behavior."""
    EXPRESSIVENESS = "expressiveness"  # How readily emotions are shown
    ADAPTABILITY = "adaptability"      # How quickly behavior changes
    PERSISTENCE = "persistence"        # How long states are maintained
    REACTIVITY = "reactivity"         # How strongly events affect behavior
    
    # Default personality configuration
    DEFAULT_TRAITS = {
        EXPRESSIVENESS: 0.7,  # 0 = reserved, 1 = very expressive
        ADAPTABILITY: 0.6,    # 0 = rigid, 1 = highly adaptable
        PERSISTENCE: 0.5,     # 0 = fleeting, 1 = very persistent
        REACTIVITY: 0.6       # 0 = steady, 1 = highly reactive
    }

class BehaviorPattern:
    """Recognizable behavior patterns."""
    
    def __init__(self):
        self.emotion_transitions = Counter()  # Track emotion changes
        self.gesture_sequences = Counter()    # Track gesture sequences
        self.context_patterns = Counter()     # Track context patterns
        
    def add_transition(self, from_emotion: EmotionType, to_emotion: EmotionType):
        """Record an emotion transition."""
        self.emotion_transitions[(from_emotion, to_emotion)] += 1
        
    def add_gesture_sequence(self, gestures: Tuple[GestureType, ...]):
        """Record a gesture sequence."""
        if len(gestures) >= 2:  # Only track sequences of 2 or more
            self.gesture_sequences[gestures] += 1
            
    def add_context_pattern(self, context_key: str, context_value: str):
        """Record a context pattern."""
        self.context_patterns[(context_key, context_value)] += 1
        
    def get_likely_next_emotion(
        self,
        current_emotion: EmotionType,
        threshold: int = 3
    ) -> Optional[EmotionType]:
        """Predict next likely emotion based on patterns."""
        transitions = [
            (emotion_pair, count) for emotion_pair, count in self.emotion_transitions.items()
            if emotion_pair[0] == current_emotion and count >= threshold
        ]
        if transitions:
            return max(transitions, key=lambda x: x[1])[0][1]
        return None
        
    def get_likely_next_gesture(
        self,
        current_sequence: Tuple[GestureType, ...],
        threshold: int = 2
    ) -> Optional[GestureType]:
        """Predict next likely gesture based on patterns."""
        if len(current_sequence) < 1:
            return None
            
        matching_sequences = [
            (seq, count) for seq, count in self.gesture_sequences.items()
            if seq[:-1] == current_sequence and count >= threshold
        ]
        if matching_sequences:
            return max(matching_sequences, key=lambda x: x[1])[0][-1]
        return None
        
    def clear(self):
        """Clear all pattern data."""
        self.emotion_transitions.clear()
        self.gesture_sequences.clear()
        self.context_patterns.clear()

class BehaviorMemory:
    """Short-term memory for avatar behavior."""
    
    def __init__(
        self,
        max_size: int = 10,
        personality_traits: Optional[Dict[str, float]] = None
    ):
        self.max_size = max_size
        self.emotion_history = deque(maxlen=max_size)
        self.gesture_history = deque(maxlen=max_size)
        self.context_history = deque(maxlen=max_size)
        self.last_reset = datetime.utcnow()
        self.patterns = BehaviorPattern()
        self.personality = personality_traits or PersonalityTrait.DEFAULT_TRAITS
        
    def add_behavior(
        self,
        emotion: Optional[EmotionType],
        gesture: Optional[GestureType],
        context: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ):
        """Add behavior to memory."""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        # Record emotion with pattern tracking
        if emotion:
            if self.emotion_history:
                self.patterns.add_transition(
                    self.emotion_history[-1]['emotion'],
                    emotion
                )
            self.emotion_history.append({
                'emotion': emotion,
                'timestamp': timestamp
            })
            
        # Record gesture with pattern tracking
        if gesture:
            recent_gestures = tuple(
                g['gesture'] for g in list(self.gesture_history)[-2:]
            )
            if recent_gestures:
                self.patterns.add_gesture_sequence(
                    recent_gestures + (gesture,)
                )
            self.gesture_history.append({
                'gesture': gesture,
                'timestamp': timestamp
            })
            
        # Record context with pattern tracking
        if context:
            for key, value in context.items():
                if isinstance(value, str):
                    self.patterns.add_context_pattern(key, value)
            self.context_history.append({
                'context': context,
                'timestamp': timestamp
            })
            
    def get_dominant_emotion(
        self,
        window_seconds: int = 30
    ) -> Optional[EmotionType]:
        """Get the dominant emotion in recent history."""
        if not self.emotion_history:
            return None
            
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        recent_emotions = [
            e['emotion'] for e in self.emotion_history
            if e['timestamp'] > cutoff
        ]
        
        if not recent_emotions:
            return None
            
        # Count occurrences of each emotion
        emotion_counts = {}
        for emotion in recent_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
        # Return most frequent emotion
        return max(emotion_counts.items(), key=lambda x: x[1])[0]
        
    def should_maintain_emotion(
        self,
        current_emotion: EmotionType,
        threshold_seconds: Optional[int] = None
    ) -> bool:
        """Check if current emotion should be maintained."""
        if not self.emotion_history:
            return False
            
        # Adjust threshold based on personality
        if threshold_seconds is None:
            base_threshold = 5
            persistence = self.personality[PersonalityTrait.PERSISTENCE]
            threshold_seconds = int(base_threshold * (1 + persistence))
            
        # Check recent emotion consistency
        cutoff = datetime.utcnow() - timedelta(seconds=threshold_seconds)
        recent_emotions = [
            e['emotion'] for e in self.emotion_history
            if e['timestamp'] > cutoff
        ]
        
        if not recent_emotions:
            return False
            
        # If current emotion has been consistent, maintain it
        return all(e == current_emotion for e in recent_emotions)
        
    def get_context_summary(
        self,
        window_seconds: int = 60
    ) -> Dict:
        """Get summary of recent context."""
        if not self.context_history:
            return {}
            
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        recent_contexts = [
            c['context'] for c in self.context_history
            if c['timestamp'] > cutoff
        ]
        
        if not recent_contexts:
            return {}
            
        # Merge recent contexts
        summary = {}
        for context in recent_contexts:
            for key, value in context.items():
                if key not in summary:
                    summary[key] = []
                if value not in summary[key]:
                    summary[key].append(value)
                    
        return summary
        
    def should_reset_state(self, idle_threshold: Optional[int] = None) -> bool:
        """Check if avatar state should reset due to inactivity."""
        if not self.emotion_history and not self.gesture_history:
            return True
            
        # Adjust threshold based on personality
        if idle_threshold is None:
            base_threshold = 300
            persistence = self.personality[PersonalityTrait.PERSISTENCE]
            idle_threshold = int(base_threshold * (1 + persistence))
            
        last_activity = max(
            self.emotion_history[-1]['timestamp'] if self.emotion_history else datetime.min,
            self.gesture_history[-1]['timestamp'] if self.gesture_history else datetime.min
        )
        
        idle_time = (datetime.utcnow() - last_activity).total_seconds()
        return idle_time >= idle_threshold
        
    def predict_next_behavior(
        self,
        current_emotion: Optional[EmotionType] = None,
        current_gesture: Optional[GestureType] = None
    ) -> Tuple[Optional[EmotionType], Optional[GestureType]]:
        """Predict next likely behavior based on patterns."""
        next_emotion = None
        next_gesture = None
        
        # Predict next emotion if we have current
        if current_emotion:
            next_emotion = self.patterns.get_likely_next_emotion(current_emotion)
            
        # Predict next gesture if we have recent history
        if self.gesture_history:
            recent_gestures = tuple(
                g['gesture'] for g in list(self.gesture_history)[-2:]
            )
            if recent_gestures:
                next_gesture = self.patterns.get_likely_next_gesture(recent_gestures)
                
        return next_emotion, next_gesture
        
    def get_behavior_influence(self) -> Dict[str, float]:
        """Get personality influence on behavior."""
        return {
            'emotion_intensity': self.personality[PersonalityTrait.EXPRESSIVENESS],
            'transition_speed': self.personality[PersonalityTrait.ADAPTABILITY],
            'state_persistence': self.personality[PersonalityTrait.PERSISTENCE],
            'response_intensity': self.personality[PersonalityTrait.REACTIVITY]
        }
        
    def clear(self):
        """Clear all memory."""
        self.emotion_history.clear()
        self.gesture_history.clear()
        self.context_history.clear()
        self.patterns.clear()
        self.last_reset = datetime.utcnow()

# Initialize global memory manager
memory_manager = BehaviorMemory() 