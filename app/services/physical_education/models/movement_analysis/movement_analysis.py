import tensorflow as tf
import numpy as np
import mediapipe as mp
from typing import Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)

class MovementAnalysisModel:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Get the base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.models_dir = '/app/services/physical_education/models/movement_analysis'
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Movement analysis model
        model_path = os.path.join(self.models_dir, 'movement_analysis_model.h5')
        logger.info(f"Loading movement model from: {model_path}")
        
        try:
            if not os.path.exists(model_path):
                # Create a simple model if it doesn't exist
                inputs = tf.keras.layers.Input(shape=(10,))
                x = tf.keras.layers.Dense(10, activation='relu')(inputs)
                outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
                model = tf.keras.Model(inputs=inputs, outputs=outputs)
                # Use new Keras format
                tf.keras.models.save_model(model, model_path.replace('.h5', '.keras'), save_format='keras')
            
            self.model = tf.keras.models.load_model(model_path.replace('.h5', '.keras'))
        except Exception as e:
            print(f"Error loading movement model: {str(e)}")
            raise
        
        # Define key points for analysis
        self.key_points = {
            'shoulder': [11, 12],  # Left and right shoulder
            'hip': [23, 24],       # Left and right hip
            'knee': [25, 26],      # Left and right knee
            'ankle': [27, 28]      # Left and right ankle
        }

    def process_video_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a single video frame for movement analysis."""
        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        results = self.pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return None
            
        # Extract key points
        landmarks = results.pose_landmarks.landmark
        key_points_data = {}
        
        for point_name, indices in self.key_points.items():
            points = []
            for idx in indices:
                landmark = landmarks[idx]
                points.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            key_points_data[point_name] = points
            
        return key_points_data

    def analyze_movement(self, key_points_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze movement patterns from key points data."""
        # Prepare features for the model
        features = self._prepare_features(key_points_data)
        
        # Get model predictions
        predictions = self.model.predict(features)
        
        # Generate analysis results
        analysis = {
            'form_score': float(predictions[0][0]),
            'alignment_score': float(predictions[0][1]),
            'stability_score': float(predictions[0][2]),
            'recommendations': self._generate_recommendations(predictions)
        }
        
        return analysis

    def _prepare_features(self, key_points_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for the model."""
        features = []
        
        # Calculate angles between key points
        for point_name, points in key_points_data.items():
            if len(points) == 2:  # For pairs of points
                angle = self._calculate_angle(points[0], points[1])
                features.append(angle)
                
        # Calculate distances between key points
        for i, (point_name1, points1) in enumerate(key_points_data.items()):
            for point_name2, points2 in list(key_points_data.items())[i+1:]:
                distance = self._calculate_distance(points1[0], points2[0])
                features.append(distance)
                
        return np.array([features])

    def _calculate_angle(self, point1: Dict[str, float], point2: Dict[str, float]) -> float:
        """Calculate the angle between two points."""
        dx = point2['x'] - point1['x']
        dy = point2['y'] - point1['y']
        return np.arctan2(dy, dx) * 180 / np.pi

    def _calculate_distance(self, point1: Dict[str, float], point2: Dict[str, float]) -> float:
        """Calculate the distance between two points."""
        dx = point2['x'] - point1['x']
        dy = point2['y'] - point1['y']
        dz = point2['z'] - point1['z']
        return np.sqrt(dx*dx + dy*dy + dz*dz)

    def _generate_recommendations(self, predictions: np.ndarray) -> List[str]:
        """Generate movement recommendations based on model predictions."""
        recommendations = []
        
        # Form recommendations
        if predictions[0][0] < 0.7:
            recommendations.append("Focus on maintaining proper form throughout the movement")
            
        # Alignment recommendations
        if predictions[0][1] < 0.7:
            recommendations.append("Pay attention to body alignment and posture")
            
        # Stability recommendations
        if predictions[0][2] < 0.7:
            recommendations.append("Work on improving stability and balance")
            
        return recommendations 