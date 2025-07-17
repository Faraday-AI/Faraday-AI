"""
Avatar Interaction System

This module provides adaptive interaction styles based on user engagement
and conversation patterns, helping create more personalized interactions.
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from app.dashboard.schemas.avatar import EmotionType, GestureType

class InteractionStyle:
    """Interaction style preferences."""
    FORMAL = "formal"           # Professional, structured interactions
    CASUAL = "casual"          # Relaxed, friendly interactions
    EMPATHETIC = "empathetic"  # Emotionally supportive interactions
    DIRECT = "direct"          # Straightforward, efficient interactions
    PLAYFUL = "playful"        # Light, entertaining interactions
    
    # Style modifiers for different aspects
    STYLE_MODIFIERS = {
        FORMAL: {
            'emotion_threshold': 1.2,      # Higher threshold for emotion changes
            'gesture_frequency': 0.7,      # Reduced gesture frequency
            'response_formality': 1.3,     # More formal language
            'emotion_intensity': 0.8       # More subdued emotions
        },
        CASUAL: {
            'emotion_threshold': 0.8,      # Lower threshold for emotion changes
            'gesture_frequency': 1.2,      # Increased gesture frequency
            'response_formality': 0.7,     # More casual language
            'emotion_intensity': 1.1       # More expressive emotions
        },
        EMPATHETIC: {
            'emotion_threshold': 0.7,      # Very responsive to emotional cues
            'gesture_frequency': 1.1,      # Slightly increased gestures
            'response_formality': 0.9,     # Balanced formality
            'emotion_intensity': 1.2       # More intense emotions
        },
        DIRECT: {
            'emotion_threshold': 1.3,      # Less emotional variation
            'gesture_frequency': 0.8,      # Fewer gestures
            'response_formality': 1.1,     # Slightly formal
            'emotion_intensity': 0.7       # More controlled emotions
        },
        PLAYFUL: {
            'emotion_threshold': 0.6,      # Very dynamic emotions
            'gesture_frequency': 1.4,      # Many gestures
            'response_formality': 0.5,     # Very casual
            'emotion_intensity': 1.3       # Very expressive
        }
    }

class UserEngagement:
    """Track and analyze user engagement patterns."""
    
    def __init__(self):
        self.message_lengths = []
        self.response_times = []
        self.emoji_usage = []
        self.question_frequency = []
        self.last_interaction = datetime.utcnow()
        
    def add_interaction(
        self,
        message: str,
        timestamp: Optional[datetime] = None
    ):
        """Record a user interaction."""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        # Calculate response time
        time_diff = (timestamp - self.last_interaction).total_seconds()
        self.response_times.append(min(time_diff, 300))  # Cap at 5 minutes
        
        # Analyze message
        self.message_lengths.append(len(message))
        self.emoji_usage.append(len([c for c in message if c in '😊😄😃😀😅']))
        self.question_frequency.append(message.count('?'))
        
        # Update last interaction time
        self.last_interaction = timestamp
        
        # Keep lists manageable
        max_history = 50
        self.message_lengths = self.message_lengths[-max_history:]
        self.response_times = self.response_times[-max_history:]
        self.emoji_usage = self.emoji_usage[-max_history:]
        self.question_frequency = self.question_frequency[-max_history:]
        
    def get_engagement_metrics(self) -> Dict[str, float]:
        """Calculate current engagement metrics."""
        if not self.message_lengths:
            return {
                'engagement_level': 0.5,
                'formality_level': 0.5,
                'emotional_level': 0.5,
                'interaction_speed': 0.5
            }
            
        # Calculate metrics
        avg_length = np.mean(self.message_lengths) / 100  # Normalize
        avg_response = np.mean(self.response_times) / 60  # Convert to minutes
        avg_emoji = np.mean(self.emoji_usage)
        avg_questions = np.mean(self.question_frequency)
        
        # Calculate engagement metrics
        engagement = min(1.0, (avg_length + avg_questions * 2) / 10)
        formality = max(0.1, min(1.0, 1.0 - (avg_emoji * 0.2)))
        emotional = min(1.0, avg_emoji * 0.3 + avg_length * 0.01)
        speed = max(0.1, min(1.0, 1.0 - (avg_response / 5)))
        
        return {
            'engagement_level': engagement,
            'formality_level': formality,
            'emotional_level': emotional,
            'interaction_speed': speed
        }
        
    def recommend_style(self) -> str:
        """Recommend interaction style based on engagement."""
        metrics = self.get_engagement_metrics()
        
        # Decision tree for style recommendation
        if metrics['emotional_level'] > 0.7:
            if metrics['formality_level'] < 0.4:
                return InteractionStyle.PLAYFUL
            return InteractionStyle.EMPATHETIC
            
        if metrics['formality_level'] > 0.7:
            if metrics['interaction_speed'] > 0.7:
                return InteractionStyle.DIRECT
            return InteractionStyle.FORMAL
            
        return InteractionStyle.CASUAL
        
    def clear(self):
        """Clear engagement history."""
        self.message_lengths.clear()
        self.response_times.clear()
        self.emoji_usage.clear()
        self.question_frequency.clear()
        self.last_interaction = datetime.utcnow()

class InteractionManager:
    """Manages adaptive interaction styles."""
    
    def __init__(self):
        self.engagement = UserEngagement()
        self.current_style = InteractionStyle.CASUAL
        self.style_duration = defaultdict(int)
        self.style_success = defaultdict(list)
        
    def process_interaction(
        self,
        message: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Process a user interaction and update style."""
        # Record interaction
        self.engagement.add_interaction(message, timestamp)
        
        # Get recommended style
        recommended_style = self.engagement.recommend_style()
        
        # Update style statistics
        self.style_duration[self.current_style] += 1
        
        # Get current metrics
        metrics = self.engagement.get_engagement_metrics()
        
        # Record success of current style
        self.style_success[self.current_style].append(metrics['engagement_level'])
        
        # Keep success history manageable
        max_history = 50
        self.style_success[self.current_style] = self.style_success[self.current_style][-max_history:]
        
        # Consider style change
        if self._should_change_style(recommended_style):
            self.current_style = recommended_style
            
        # Get style modifiers
        modifiers = InteractionStyle.STYLE_MODIFIERS[self.current_style]
        
        # Combine base metrics with style modifiers
        return {
            'emotion_threshold': modifiers['emotion_threshold'],
            'gesture_frequency': modifiers['gesture_frequency'],
            'response_formality': modifiers['response_formality'],
            'emotion_intensity': modifiers['emotion_intensity'] * metrics['emotional_level'],
            'interaction_speed': metrics['interaction_speed'],
            'current_style': self.current_style
        }
        
    def _should_change_style(self, recommended_style: str) -> bool:
        """Determine if style should change."""
        if self.current_style == recommended_style:
            return False
            
        # Get success rates
        current_success = np.mean(self.style_success[self.current_style][-5:])
        recommended_success = np.mean(self.style_success[recommended_style][-5:]) if self.style_success[recommended_style] else 0.5
        
        # Change if recommended style has better success rate
        return recommended_success > current_success
        
    def clear(self):
        """Clear interaction history."""
        self.engagement.clear()
        self.style_duration.clear()
        self.style_success.clear()
        self.current_style = InteractionStyle.CASUAL

# Initialize global interaction manager
interaction_manager = InteractionManager() 