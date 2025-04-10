import os
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
import json
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InjuryPreventionTrainer:
    def __init__(self):
        self.models_dir = Path('models')
        self.data_dir = Path('data')
        self.movement_data_dir = self.data_dir / 'movement_videos'
        self.health_metrics_dir = self.data_dir / 'health_metrics'
        
    def prepare_dataset(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare the dataset for training."""
        logger.info("Preparing dataset...")
        
        # Load and process movement data
        movement_features = []
        movement_labels = []
        
        for movement_type in ['jumping', 'running', 'squatting']:
            for video_file in (self.movement_data_dir / movement_type).glob('*.json'):
                with open(video_file) as f:
                    data = json.load(f)
                    
                    # Extract movement features
                    features = self._extract_movement_features(data)
                    movement_features.append(features)
                    
                    # Extract injury risk label
                    label = self._calculate_injury_risk(data)
                    movement_labels.append(label)
        
        # Load and process health metrics
        health_features = []
        health_labels = []
        
        for health_file in self.health_metrics_dir.glob('*.json'):
            with open(health_file) as f:
                data = json.load(f)
                
                # Extract health features
                features = self._extract_health_features(data)
                health_features.append(features)
                
                # Extract injury risk label
                label = self._calculate_health_risk(data)
                health_labels.append(label)
        
        # Combine features
        X_movement = np.array(movement_features)
        X_health = np.array(health_features)
        y_movement = np.array(movement_labels)
        y_health = np.array(health_labels)
        
        # Scale features
        scaler_movement = StandardScaler()
        scaler_health = StandardScaler()
        
        X_movement_scaled = scaler_movement.fit_transform(X_movement)
        X_health_scaled = scaler_health.fit_transform(X_health)
        
        # Combine scaled features
        X = np.concatenate([X_movement_scaled, X_health_scaled], axis=1)
        y = np.maximum(y_movement, y_health)  # Take the higher risk score
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Save scalers
        self.scaler_movement = scaler_movement
        self.scaler_health = scaler_health
        
        return X_train, X_test, y_train, y_test
    
    def _extract_movement_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract features from movement analysis data."""
        features = []
        
        # Key points features
        key_points = data.get('key_points', {})
        for point in ['shoulders', 'hips', 'knees', 'ankles']:
            if point in key_points:
                features.extend(key_points[point])
        
        # Angle features
        angles = data.get('angles', {})
        for angle in ['shoulder', 'hip', 'knee']:
            if angle in angles:
                features.append(angles[angle])
        
        # Analysis scores
        analysis = data.get('analysis', {})
        for score in ['form', 'alignment', 'stability', 'power']:
            if score in analysis:
                features.append(analysis[score])
        
        return np.array(features)
    
    def _extract_health_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract features from health metrics data."""
        features = []
        
        # Physical metrics
        physical = data.get('physical_metrics', {})
        for metric in ['bmi', 'body_fat_percentage', 'muscle_mass']:
            if metric in physical:
                features.append(physical[metric])
        
        # Vital signs
        vital = data.get('vital_signs', {})
        for sign in ['resting_heart_rate', 'blood_pressure_systolic', 
                    'blood_pressure_diastolic', 'oxygen_saturation']:
            if sign in vital:
                features.append(vital[sign])
        
        # Performance metrics
        performance = data.get('performance_metrics', {})
        for metric in ['strength_score', 'endurance_score', 'flexibility_score', 
                      'coordination_score', 'balance_score']:
            if metric in performance:
                features.append(performance[metric])
        
        # Health indicators
        health = data.get('health_indicators', {})
        for indicator in ['sleep_quality', 'nutrition_score', 'stress_level', 
                         'recovery_rate', 'immune_function']:
            if indicator in health:
                features.append(health[indicator])
        
        # Injury history
        injury = data.get('injury_history', {})
        for factor in ['total_injuries', 'recent_injuries', 'injury_severity', 
                      'recovery_status']:
            if factor in injury:
                features.append(injury[factor])
        
        return np.array(features)
    
    def _calculate_injury_risk(self, data: Dict[str, Any]) -> float:
        """Calculate injury risk from movement analysis."""
        risk_factors = []
        
        # Form and alignment issues
        analysis = data.get('analysis', {})
        if 'form' in analysis:
            risk_factors.append(1 - analysis['form'])
        if 'alignment' in analysis:
            risk_factors.append(1 - analysis['alignment'])
        
        # Stability issues
        if 'stability' in analysis:
            risk_factors.append(1 - analysis['stability'])
        
        # Joint angles outside safe ranges
        angles = data.get('angles', {})
        for joint, angle in angles.items():
            if joint == 'knee':
                if angle < 0 or angle > 180:  # Knee hyperextension/flexion
                    risk_factors.append(1.0)
            elif joint == 'shoulder':
                if angle < 0 or angle > 180:  # Shoulder hyperextension/flexion
                    risk_factors.append(1.0)
        
        # Calculate overall risk score
        if risk_factors:
            risk_score = np.mean(risk_factors)
        else:
            risk_score = 0.0
        
        return min(1.0, max(0.0, risk_score))
    
    def _calculate_health_risk(self, data: Dict[str, Any]) -> float:
        """Calculate injury risk from health metrics."""
        risk_factors = []
        
        # Physical condition
        physical = data.get('physical_metrics', {})
        if 'bmi' in physical:
            bmi = physical['bmi']
            if bmi < 18.5 or bmi > 25:  # Underweight or overweight
                risk_factors.append(0.5)
        
        # Performance metrics
        performance = data.get('performance_metrics', {})
        for metric in ['strength_score', 'flexibility_score', 'balance_score']:
            if metric in performance:
                risk_factors.append(1 - performance[metric])
        
        # Health indicators
        health = data.get('health_indicators', {})
        if 'stress_level' in health:
            risk_factors.append(health['stress_level'])
        if 'recovery_rate' in health:
            risk_factors.append(1 - health['recovery_rate'])
        
        # Injury history
        injury = data.get('injury_history', {})
        if 'total_injuries' in injury:
            risk_factors.append(min(1.0, injury['total_injuries'] / 5))
        if 'recent_injuries' in injury:
            risk_factors.append(min(1.0, injury['recent_injuries'] / 2))
        
        # Calculate overall risk score
        if risk_factors:
            risk_score = np.mean(risk_factors)
        else:
            risk_score = 0.0
        
        return min(1.0, max(0.0, risk_score))
    
    def create_model(self, input_shape: Tuple[int, ...]) -> tf.keras.Model:
        """Create the injury prevention model."""
        logger.info("Creating model...")
        
        model = models.Sequential([
            # Input layer
            layers.Dense(256, activation='relu', input_shape=input_shape),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Hidden layers
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        return model
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                   X_test: np.ndarray, y_test: np.ndarray,
                   epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """Train the injury prevention model."""
        logger.info("Training model...")
        
        # Create model
        model = self.create_model(input_shape=(X_train.shape[1],))
        
        # Define callbacks
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            callbacks.ModelCheckpoint(
                filepath=str(self.models_dir / 'injury_prevention_best.h5'),
                monitor='val_loss',
                save_best_only=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5
            )
        ]
        
        # Train model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks_list,
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_accuracy, test_auc = model.evaluate(X_test, y_test)
        
        return {
            'model': model,
            'history': history.history,
            'test_metrics': {
                'loss': test_loss,
                'accuracy': test_accuracy,
                'auc': test_auc
            }
        }
    
    def save_model(self, model: tf.keras.Model) -> None:
        """Save the trained model and scalers."""
        logger.info("Saving model...")
        
        # Create models directory if it doesn't exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model.save(str(self.models_dir / 'injury_prevention.h5'))
        
        # Save scalers
        joblib.dump(self.scaler_movement, str(self.models_dir / 'injury_prevention_movement_scaler.joblib'))
        joblib.dump(self.scaler_health, str(self.models_dir / 'injury_prevention_health_scaler.joblib'))
        
        logger.info("Model saved successfully")

def main():
    """Main function to train the injury prevention model."""
    try:
        # Initialize trainer
        trainer = InjuryPreventionTrainer()
        
        # Prepare dataset
        X_train, X_test, y_train, y_test = trainer.prepare_dataset()
        
        # Train model
        results = trainer.train_model(X_train, y_train, X_test, y_test)
        
        # Save model
        trainer.save_model(results['model'])
        
        # Log results
        logger.info("Training completed successfully")
        logger.info(f"Test Loss: {results['test_metrics']['loss']:.4f}")
        logger.info(f"Test Accuracy: {results['test_metrics']['accuracy']:.4f}")
        logger.info(f"Test AUC: {results['test_metrics']['auc']:.4f}")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    main() 