import numpy as np
import librosa
import tensorflow as tf
import openai
from typing import Dict, Any, List
from app.core.config import get_settings
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)
settings = get_settings()

class AIVoiceAnalysis:
    def __init__(self):
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self._initialize_models()

    def _initialize_models(self):
        """Initialize voice analysis models."""
        self.voice_model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(128, 128, 1)),
            tf.keras.layers.Conv2D(32, 3, activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(5, activation='softmax')
        ])

    async def analyze_coaching_voice(
        self,
        audio_path: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze coaching voice for effectiveness and engagement."""
        try:
            # Extract audio features
            y, sr = librosa.load(audio_path)
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
            
            # Get AI coaching analysis
            prompt = f"""
            Analyze coaching voice characteristics considering:
            1. Clarity and articulation
            2. Tone and enthusiasm
            3. Pacing and timing
            4. Emphasis on key points
            5. Motivational elements
            
            Context: {context or 'General coaching session'}
            
            Provide:
            1. Voice effectiveness score
            2. Engagement analysis
            3. Improvement suggestions
            4. Best practices
            5. Student impact assessment
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "voice_metrics": self._analyze_voice_metrics(y, sr),
                "ai_feedback": response.choices[0].message.content,
                "effectiveness_score": self._calculate_effectiveness_score(mel_spec),
                "recommendations": self._generate_voice_recommendations(response),
                "visualizations": self._generate_voice_visualizations(y, sr)
            }
        except Exception as e:
            logger.error(f"Error analyzing coaching voice: {str(e)}")
            return {"error": str(e)}

    def _analyze_voice_metrics(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze various voice metrics."""
        return {
            "clarity": float(np.mean(librosa.feature.rms(y=y))),
            "pitch_variance": float(np.std(librosa.yin(y, fmin=75, fmax=300))),
            "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0]),
            "energy": float(np.mean(librosa.feature.spectral_contrast(y=y, sr=sr)))
        }

    def _calculate_effectiveness_score(self, mel_spec: np.ndarray) -> float:
        """Calculate overall voice effectiveness score."""
        features = np.expand_dims(
            librosa.power_to_db(mel_spec[:128, :128]), 
            axis=[0, -1]
        )
        predictions = self.voice_model.predict(features)
        return float(np.mean(predictions))

    def _generate_voice_recommendations(self, ai_response: Any) -> List[Dict[str, Any]]:
        """Generate voice-specific recommendations."""
        insights = ai_response.choices[0].message.content.split('\n')
        return [
            {
                "area": "voice_coaching",
                "recommendation": insight.strip(),
                "priority": self._calculate_priority(insight)
            }
            for insight in insights if insight.strip()
        ]

    def _generate_voice_visualizations(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """Generate visualizations for voice analysis."""
        return {
            "waveform": y.tolist(),
            "mel_spectrogram": librosa.feature.melspectrogram(y=y, sr=sr).tolist(),
            "pitch_contour": librosa.yin(y, fmin=75, fmax=300).tolist(),
            "tempo_curve": librosa.onset.onset_strength(y=y, sr=sr).tolist()
        }

    def _calculate_priority(self, insight: str) -> str:
        """Calculate priority level for voice recommendations."""
        if "immediate" in insight.lower() or "critical" in insight.lower():
            return "high"
        elif "consider" in insight.lower() or "might" in insight.lower():
            return "medium"
        return "low"

@lru_cache()
def get_ai_voice_service() -> AIVoiceAnalysis:
    """Get cached AI voice service instance."""
    return AIVoiceAnalysis() 