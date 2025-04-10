import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LSTM
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthMetricsTrainer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_dataset(self, data_dir: str = 'data/health_metrics') -> tuple:
        """Prepare training dataset from health metrics data."""
        logger.info("Preparing dataset...")
        
        # Create data directory if it doesn't exist
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        # Load and process data
        X = []
        y = []
        
        # Process each student file
        for student_file in Path(data_dir).glob('*.json'):
            with open(student_file, 'r') as f:
                student_data = json.load(f)
                
                # Extract features
                features = self._extract_features(student_data)
                
                X.append(features)
                y.append(student_data['health_score'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def _extract_features(self, student_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from student data."""
        features = []
        
        # Physical metrics
        features.extend([
            student_data['height'],
            student_data['weight'],
            student_data['bmi'],
            student_data['resting_heart_rate'],
            student_data['blood_pressure_systolic'],
            student_data['blood_pressure_diastolic']
        ])
        
        # Activity metrics
        features.extend([
            student_data['activity_level'],
            student_data['exercise_frequency'],
            student_data['exercise_duration'],
            student_data['exercise_intensity']
        ])
        
        # Performance metrics
        features.extend([
            student_data['strength_score'],
            student_data['endurance_score'],
            student_data['flexibility_score'],
            student_data['coordination_score']
        ])
        
        # Health indicators
        features.extend([
            student_data['sleep_quality'],
            student_data['nutrition_score'],
            student_data['stress_level'],
            student_data['recovery_rate']
        ])
        
        return np.array(features)
    
    def create_model(self, input_shape: tuple) -> Sequential:
        """Create neural network model for health metrics prediction."""
        logger.info("Creating model...")
        
        model = Sequential([
            Dense(256, activation='relu', input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.1),
            
            Dense(1, activation='sigmoid')  # Output: health score (0-1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        return model
    
    def train_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32
    ) -> dict:
        """Train the health metrics model."""
        logger.info("Training model...")
        
        # Create model
        self.model = self.create_model(input_shape=(X_train.shape[1],))
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            ModelCheckpoint(
                'models/health_metrics.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_mae, test_mse = self.model.evaluate(X_test, y_test)
        
        return {
            'test_loss': test_loss,
            'test_mae': test_mae,
            'test_mse': test_mse,
            'history': history.history
        }
    
    def save_model(self):
        """Save the trained model and scaler."""
        logger.info("Saving model...")
        
        # Create models directory if it doesn't exist
        Path('models').mkdir(exist_ok=True)
        
        # Save model
        self.model.save('models/health_metrics.h5')
        
        # Save scaler
        joblib.dump(self.scaler, 'models/health_metrics_scaler.joblib')
        
        # Save metadata
        metadata = {
            'model_type': 'health_metrics',
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape
        }
        
        with open('models/health_metrics_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info("Model saved successfully")

def main():
    """Main function to train the health metrics model."""
    try:
        # Initialize trainer
        trainer = HealthMetricsTrainer()
        
        # Prepare dataset
        X_train, X_test, y_train, y_test = trainer.prepare_dataset()
        
        # Train model
        results = trainer.train_model(X_train, y_train, X_test, y_test)
        
        # Save model
        trainer.save_model()
        
        # Log results
        logger.info(f"Training completed with results: {results}")
        
    except Exception as e:
        logger.error(f"Error in training: {str(e)}")
        raise

if __name__ == "__main__":
    main() 