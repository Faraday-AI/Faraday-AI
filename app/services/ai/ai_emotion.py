import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50V2
import openai
from typing import Dict, Any, List, Optional
from app.core.config import get_settings
import logging
from functools import lru_cache
from datetime import datetime
import json

logger = logging.getLogger(__name__)
settings = get_settings()

class AIEmotionAnalysis:
    def __init__(self):
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self._initialize_models()

    def _initialize_models(self):
        """Initialize emotion recognition models."""
        base_model = ResNet50V2(weights='imagenet', include_top=False)
        x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        output = tf.keras.layers.Dense(7, activation='softmax')(x)  # 7 basic emotions
        self.emotion_model = tf.keras.Model(inputs=base_model.input, outputs=output)

    async def analyze_student_emotions(
        self,
        video_path: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze student emotions during physical activities."""
        try:
            # Process video frames
            frames = self._extract_frames(video_path)
            emotions = self._detect_emotions(frames)
            
            # Get AI emotion analysis
            prompt = f"""
            Analyze student emotional engagement considering:
            1. Emotional states detected
            2. Engagement patterns
            3. Motivation levels
            4. Social interactions
            5. Activity enjoyment
            
            Context: {context or 'General PE activity'}
            
            Provide:
            1. Emotional analysis
            2. Engagement insights
            3. Motivation assessment
            4. Support recommendations
            5. Activity adjustments
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "emotion_metrics": self._analyze_emotion_metrics(emotions),
                "ai_insights": response.choices[0].message.content,
                "engagement_score": self._calculate_engagement_score(emotions),
                "recommendations": self._generate_emotion_recommendations(response),
                "visualizations": self._generate_emotion_visualizations(frames, emotions)
            }
        except Exception as e:
            logger.error(f"Error analyzing student emotions: {str(e)}")
            return {"error": str(e)}

    def _extract_frames(self, video_path: str) -> List[np.ndarray]:
        """Extract frames from video file."""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            
        cap.release()
        return frames

    def _detect_emotions(self, frames: List[np.ndarray]) -> List[Dict[str, float]]:
        """Detect emotions in video frames."""
        emotions = []
        for frame in frames:
            # Preprocess frame
            resized = cv2.resize(frame, (224, 224))
            normalized = resized / 255.0
            batch = np.expand_dims(normalized, axis=0)
            
            # Get emotion predictions
            predictions = self.emotion_model.predict(batch)
            emotions.append({
                "happy": float(predictions[0][0]),
                "sad": float(predictions[0][1]),
                "angry": float(predictions[0][2]),
                "fearful": float(predictions[0][3]),
                "surprised": float(predictions[0][4]),
                "neutral": float(predictions[0][5]),
                "excited": float(predictions[0][6])
            })
        
        return emotions

    def _analyze_emotion_metrics(
        self,
        emotions: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Analyze emotion metrics over time."""
        metrics = {}
        for emotion in ["happy", "sad", "angry", "fearful", "surprised", "neutral", "excited"]:
            values = [e[emotion] for e in emotions]
            metrics[emotion] = {
                "mean": float(np.mean(values)),
                "max": float(np.max(values)),
                "variance": float(np.var(values))
            }
        return metrics

    def _calculate_engagement_score(
        self,
        emotions: List[Dict[str, float]]
    ) -> float:
        """Calculate overall engagement score based on emotions."""
        positive_emotions = ["happy", "excited", "surprised"]
        negative_emotions = ["sad", "angry", "fearful"]
        
        positive_score = np.mean([
            np.mean([e[emotion] for e in emotions])
            for emotion in positive_emotions
        ])
        negative_score = np.mean([
            np.mean([e[emotion] for e in emotions])
            for emotion in negative_emotions
        ])
        
        return float(positive_score - negative_score + 0.5)  # Normalize to 0-1

    def _generate_emotion_recommendations(
        self,
        ai_response: Any
    ) -> List[Dict[str, Any]]:
        """Generate emotion-based recommendations."""
        insights = ai_response.choices[0].message.content.split('\n')
        return [
            {
                "area": "emotional_engagement",
                "recommendation": insight.strip(),
                "priority": self._calculate_priority(insight)
            }
            for insight in insights if insight.strip()
        ]

    def _generate_emotion_visualizations(
        self,
        frames: List[np.ndarray],
        emotions: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Generate visualizations for emotion analysis."""
        return {
            "emotion_timeline": self._create_emotion_timeline(emotions),
            "engagement_curve": self._create_engagement_curve(emotions),
            "emotion_heatmap": self._create_emotion_heatmap(emotions),
            "key_moments": self._identify_key_moments(frames, emotions)
        }

    def _calculate_priority(self, insight: str) -> str:
        """Calculate priority level for emotion recommendations."""
        if "immediate" in insight.lower() or "critical" in insight.lower():
            return "high"
        elif "consider" in insight.lower() or "might" in insight.lower():
            return "medium"
        return "low"

    def _create_emotion_timeline(
        self,
        emotions: List[Dict[str, float]]
    ) -> Dict[str, List[float]]:
        """Create timeline of emotional states."""
        return {
            emotion: [e[emotion] for e in emotions]
            for emotion in emotions[0].keys()
        }

    def _create_engagement_curve(
        self,
        emotions: List[Dict[str, float]]
    ) -> List[float]:
        """Create engagement level curve over time."""
        return [self._calculate_engagement_score([e]) for e in emotions]

    def _create_emotion_heatmap(
        self,
        emotions: List[Dict[str, float]]
    ) -> List[List[float]]:
        """Create emotion intensity heatmap."""
        return [[e[emotion] for emotion in e.keys()] for e in emotions]

    def _identify_key_moments(
        self,
        frames: List[np.ndarray],
        emotions: List[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Identify key emotional moments in the video."""
        key_moments = []
        engagement_scores = self._create_engagement_curve(emotions)
        
        # Find peaks in engagement
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(engagement_scores, height=0.7)
        
        for peak in peaks:
            key_moments.append({
                "timestamp": peak,
                "frame_index": peak,
                "emotions": emotions[peak],
                "engagement_score": engagement_scores[peak]
            })
        
        return key_moments

@lru_cache()
def get_ai_emotion_service() -> AIEmotionAnalysis:
    """Get cached AI emotion service instance."""
    return AIEmotionAnalysis() 