import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import mediapipe as mp
import cv2
from typing import List, Dict, Any
import json
from pathlib import Path
import logging
from app.core.monitoring import track_metrics
from app.services.physical_education.models.movement_analysis.movement_models import MovementModels
from datetime import datetime

class MovementAnalysisTrainer:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Define key points for analysis
        self.key_points = {
            'shoulders': [11, 12],  # Left and right shoulders
            'hips': [23, 24],       # Left and right hips
            'knees': [25, 26],      # Left and right knees
            'ankles': [27, 28]      # Left and right ankles
        }
        
        # Define movement categories
        self.movement_categories = {
            'jumping': ['vertical_jump', 'broad_jump'],
            'running': ['sprint', 'jog'],
            'throwing': ['overhead_throw', 'underhand_throw'],
            'catching': ['two_hand_catch', 'one_hand_catch']
        }

    def prepare_dataset(self, data_dir: str) -> tuple:
        """Prepare the dataset for training."""
        X = []
        y = []
        
        # Process each video in the dataset
        for category, movements in self.movement_categories.items():
            for movement in movements:
                video_dir = os.path.join(data_dir, category, movement)
                if not os.path.exists(video_dir):
                    continue
                    
                for video_file in os.listdir(video_dir):
                    if not video_file.endswith(('.mp4', '.avi')):
                        continue
                        
                    video_path = os.path.join(video_dir, video_file)
                    features = self._extract_features_from_video(video_path)
                    
                    if features is not None:
                        X.append(features)
                        y.append(self._one_hot_encode(movement, self._get_all_movements()))
        
        return np.array(X), np.array(y)

    def _extract_features_from_video(self, video_path: str) -> np.ndarray:
        """Extract features from a video file."""
        cap = cv2.VideoCapture(video_path)
        features = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame
            frame_features = self._process_frame(frame)
            if frame_features is not None:
                features.append(frame_features)
        
        cap.release()
        
        if not features:
            return None
            
        # Average features across frames
        return np.mean(features, axis=0)

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame and extract features."""
        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return None
            
        # Extract key points
        key_points_data = []
        for point_group in self.key_points.values():
            for point_idx in point_group:
                landmark = results.pose_landmarks.landmark[point_idx]
                key_points_data.extend([landmark.x, landmark.y, landmark.z])
        
        # Calculate angles and distances
        angles = self._calculate_angles(results.pose_landmarks)
        distances = self._calculate_distances(results.pose_landmarks)
        
        # Combine all features
        features = np.concatenate([
            np.array(key_points_data),
            np.array(angles),
            np.array(distances)
        ])
        
        return features

    def _calculate_angles(self, landmarks: Any) -> List[float]:
        """Calculate angles between key points."""
        angles = []
        
        # Calculate shoulder angles
        left_shoulder = landmarks.landmark[11]
        right_shoulder = landmarks.landmark[12]
        left_hip = landmarks.landmark[23]
        right_hip = landmarks.landmark[24]
        
        angles.append(self._calculate_angle(
            [left_shoulder.x, left_shoulder.y],
            [right_shoulder.x, right_shoulder.y],
            [left_hip.x, left_hip.y]
        ))
        
        angles.append(self._calculate_angle(
            [right_shoulder.x, right_shoulder.y],
            [left_shoulder.x, left_shoulder.y],
            [right_hip.x, right_hip.y]
        ))
        
        return angles

    def _calculate_distances(self, landmarks: Any) -> List[float]:
        """Calculate distances between key points."""
        distances = []
        
        # Calculate shoulder width
        left_shoulder = landmarks.landmark[11]
        right_shoulder = landmarks.landmark[12]
        distances.append(self._calculate_distance(
            [left_shoulder.x, left_shoulder.y],
            [right_shoulder.x, right_shoulder.y]
        ))
        
        # Calculate hip width
        left_hip = landmarks.landmark[23]
        right_hip = landmarks.landmark[24]
        distances.append(self._calculate_distance(
            [left_hip.x, left_hip.y],
            [right_hip.x, right_hip.y]
        ))
        
        return distances

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """Calculate the angle between three points."""
        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)

    def _calculate_distance(self, a: List[float], b: List[float]) -> float:
        """Calculate the distance between two points."""
        return np.linalg.norm(np.array(a) - np.array(b))

    def _get_all_movements(self) -> List[str]:
        """Get all movement types."""
        movements = []
        for category_movements in self.movement_categories.values():
            movements.extend(category_movements)
        return movements

    def _one_hot_encode(self, movement: str, all_movements: List[str]) -> List[int]:
        """One-hot encode a movement type."""
        return [1 if m == movement else 0 for m in all_movements]

    def create_model(self, input_shape: tuple) -> tf.keras.Model:
        """Create the neural network model."""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=input_shape),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(len(self._get_all_movements()), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model

    def train(self, data_dir: str, epochs: int = 50, batch_size: int = 32):
        """Train the movement analysis model."""
        # Prepare dataset
        X, y = self.prepare_dataset(data_dir)
        
        # Create and train model
        model = self.create_model((X.shape[1],))
        model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ]
        )
        
        # Save the model
        model.save('models/movement_analysis_model.h5')
        
        # Save model metadata
        metadata = {
            'input_shape': X.shape[1:],
            'num_classes': len(self._get_all_movements()),
            'model_type': 'movement_analysis',
            'version': '1.0.0',
            'created_at': datetime.now().isoformat()
        }
        
        with open('models/movement_analysis_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    Path('models').mkdir(exist_ok=True)
    
    # Initialize trainer
    trainer = MovementAnalysisTrainer()
    
    # Train model
    trainer.train(
        data_dir='data/movement_videos',
        epochs=50,
        batch_size=32
    ) 