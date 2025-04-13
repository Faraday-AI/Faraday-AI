from typing import List, Dict, Any, Optional
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import openai
from app.core.config import get_settings
import logging
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)
settings = get_settings()

class AIVisionAnalysis:
    def __init__(self):
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self._initialize_models()

    def _initialize_models(self):
        """Initialize vision models for movement analysis."""
        # Movement classification model
        base_model = MobileNetV2(weights='imagenet', include_top=False)
        x = GlobalAveragePooling2D()(base_model.output)
        x = Dense(1024, activation='relu')(x)
        output = Dense(len(self.movement_classes), activation='softmax')(x)
        self.movement_model = tf.keras.Model(inputs=base_model.input, outputs=output)

        # Pose estimation
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    async def analyze_movement(
        self,
        video_path: str,
        movement_type: str
    ) -> Dict[str, Any]:
        """Analyze physical movement from video."""
        try:
            # Process video frames
            frames = self._extract_frames(video_path)
            pose_landmarks = self._extract_pose_landmarks(frames)
            
            # Get AI movement analysis
            prompt = f"""
            Analyze {movement_type} movement technique considering:
            1. Body alignment and posture
            2. Movement efficiency
            3. Form correctness
            4. Safety considerations
            5. Performance improvements
            
            Provide:
            1. Technique analysis
            2. Form corrections
            3. Safety recommendations
            4. Performance tips
            5. Progressive improvements
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "movement_analysis": self._analyze_pose_sequence(pose_landmarks),
                "ai_feedback": response.choices[0].message.content,
                "form_score": self._calculate_form_score(pose_landmarks),
                "recommendations": self._generate_movement_recommendations(response),
                "visualizations": self._generate_movement_visualizations(frames, pose_landmarks)
            }
        except Exception as e:
            logger.error(f"Error analyzing movement: {str(e)}")
            return {"error": str(e)}

    async def generate_form_feedback(
        self,
        video_path: str,
        exercise_type: str
    ) -> Dict[str, Any]:
        """Generate real-time form feedback for physical exercises."""
        try:
            # Process exercise video
            frames = self._extract_frames(video_path)
            pose_landmarks = self._extract_pose_landmarks(frames)
            
            # Analyze form with AI
            prompt = f"""
            Provide detailed form feedback for {exercise_type} considering:
            1. Joint angles and alignment
            2. Movement patterns
            3. Common errors
            4. Safety concerns
            5. Progression options
            
            Include:
            1. Form corrections
            2. Safety tips
            3. Modification options
            4. Advanced variations
            5. Training progressions
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "form_analysis": self._analyze_exercise_form(pose_landmarks),
                "ai_feedback": response.choices[0].message.content,
                "safety_score": self._calculate_safety_score(pose_landmarks),
                "recommendations": self._generate_form_recommendations(response),
                "visualizations": self._generate_form_visualizations(frames, pose_landmarks)
            }
        except Exception as e:
            logger.error(f"Error generating form feedback: {str(e)}")
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

    def _extract_pose_landmarks(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Extract pose landmarks from video frames."""
        landmarks = []
        
        for frame in frames:
            results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                landmarks.append({
                    'landmarks': results.pose_landmarks,
                    'world_landmarks': results.pose_world_landmarks
                })
                
        return landmarks

    def _analyze_pose_sequence(self, landmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sequence of pose landmarks for movement patterns."""
        analysis = {
            'joint_angles': self._calculate_joint_angles(landmarks),
            'movement_smoothness': self._calculate_movement_smoothness(landmarks),
            'balance_stability': self._calculate_balance_stability(landmarks),
            'movement_efficiency': self._calculate_movement_efficiency(landmarks)
        }
        
        return analysis

    def _analyze_exercise_form(self, landmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze exercise form from pose landmarks."""
        return {
            'form_quality': self._assess_form_quality(landmarks),
            'alignment': self._assess_alignment(landmarks),
            'range_of_motion': self._assess_range_of_motion(landmarks),
            'symmetry': self._assess_movement_symmetry(landmarks)
        }

    def _calculate_form_score(self, landmarks: List[Dict[str, Any]]) -> float:
        """Calculate overall form score based on multiple metrics."""
        scores = []
        
        for metric in ['alignment', 'smoothness', 'range_of_motion', 'balance']:
            score = self._calculate_metric_score(landmarks, metric)
            scores.append(score)
            
        return float(np.mean(scores))

    def _calculate_safety_score(self, landmarks: List[Dict[str, Any]]) -> float:
        """Calculate safety score based on form and alignment."""
        safety_metrics = []
        
        for metric in ['joint_stress', 'posture', 'movement_control']:
            score = self._calculate_safety_metric(landmarks, metric)
            safety_metrics.append(score)
            
        return float(np.mean(safety_metrics))

    def _generate_movement_recommendations(self, ai_response: Any) -> List[Dict[str, Any]]:
        """Generate movement-specific recommendations."""
        insights = ai_response.choices[0].message.content.split('\n')
        return [
            {
                "area": "movement",
                "recommendation": insight.strip(),
                "priority": self._calculate_recommendation_priority(insight)
            }
            for insight in insights if insight.strip()
        ]

    def _generate_form_recommendations(self, ai_response: Any) -> List[Dict[str, Any]]:
        """Generate form-specific recommendations."""
        insights = ai_response.choices[0].message.content.split('\n')
        return [
            {
                "area": "form",
                "recommendation": insight.strip(),
                "implementation": self._generate_form_corrections(insight)
            }
            for insight in insights if insight.strip()
        ]

    def _generate_movement_visualizations(
        self,
        frames: List[np.ndarray],
        landmarks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate visualizations for movement analysis."""
        visualizations = {
            "annotated_frames": self._draw_pose_annotations(frames, landmarks),
            "movement_trajectory": self._generate_movement_trajectory(landmarks),
            "joint_angle_plots": self._generate_joint_angle_plots(landmarks),
            "form_analysis_overlay": self._generate_form_analysis_overlay(frames, landmarks)
        }
        return visualizations

    def _generate_form_visualizations(
        self,
        frames: List[np.ndarray],
        landmarks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate visualizations for form analysis."""
        return {
            "form_breakdown": self._generate_form_breakdown(frames, landmarks),
            "alignment_analysis": self._generate_alignment_analysis(landmarks),
            "range_of_motion_plots": self._generate_rom_plots(landmarks),
            "comparison_overlay": self._generate_comparison_overlay(frames, landmarks)
        }

    def _calculate_metric_score(
        self,
        landmarks: List[Dict[str, Any]],
        metric: str
    ) -> float:
        """Calculate score for specific movement metric."""
        if metric == 'alignment':
            return self._calculate_alignment_score(landmarks)
        elif metric == 'smoothness':
            return self._calculate_smoothness_score(landmarks)
        elif metric == 'range_of_motion':
            return self._calculate_rom_score(landmarks)
        else:
            return self._calculate_balance_score(landmarks)

    def _calculate_safety_metric(
        self,
        landmarks: List[Dict[str, Any]],
        metric: str
    ) -> float:
        """Calculate safety metric score."""
        if metric == 'joint_stress':
            return self._calculate_joint_stress(landmarks)
        elif metric == 'posture':
            return self._calculate_posture_score(landmarks)
        else:
            return self._calculate_movement_control(landmarks)

    def _calculate_recommendation_priority(self, insight: str) -> str:
        """Calculate priority for movement recommendations."""
        if "immediate" in insight.lower() or "critical" in insight.lower():
            return "high"
        elif "consider" in insight.lower() or "might" in insight.lower():
            return "medium"
        return "low"

    def _generate_form_corrections(self, insight: str) -> List[str]:
        """Generate specific form correction steps."""
        return [
            f"Correction: {insight.split(':')[0] if ':' in insight else insight}",
            "Practice with reduced load/intensity",
            "Focus on proper form and technique",
            "Gradually increase difficulty"
        ]

@lru_cache()
def get_ai_vision_service() -> AIVisionAnalysis:
    """Get cached AI vision service instance."""
    return AIVisionAnalysis() 