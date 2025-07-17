import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
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

class ActivityDifficultyTrainer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_dataset(self, data_dir: str = 'data/activity_difficulty') -> tuple:
        """Prepare training dataset from activity and performance data."""
        logger.info("Preparing dataset...")
        
        # Create data directory if it doesn't exist
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        # Load and process data
        X = []
        y = []
        
        # Process each activity file
        for activity_file in Path(data_dir).glob('*.json'):
            with open(activity_file, 'r') as f:
                activity_data = json.load(f)
                
                # Extract features
                features = self._extract_features(activity_data)
                
                X.append(features)
                y.append(activity_data['optimal_difficulty'])
        
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
    
    def _extract_features(self, activity_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from activity data."""
        features = []
        
        # Activity type (one-hot encoded)
        activity_type = self._one_hot_encode(activity_data['activity_type'])
        features.extend(activity_type)
        
        # Student performance metrics
        features.extend([
            activity_data['current_performance'],
            activity_data['skill_level'],
            activity_data['practice_frequency'],
            activity_data['physical_condition'],
            activity_data['motivation_level']
        ])
        
        # Environmental factors
        features.extend([
            activity_data['space_available'],
            activity_data['equipment_quality'],
            activity_data['group_size']
        ])
        
        return np.array(features)
    
    def _one_hot_encode(self, value: str) -> List[int]:
        """One-hot encode categorical values."""
        categories = [
            'strength', 'endurance', 'flexibility', 'coordination',
            'speed', 'agility', 'balance', 'power'
        ]
        
        encoding = [0] * len(categories)
        if value in categories:
            encoding[categories.index(value)] = 1
        
        return encoding
    
    def create_model(self, input_shape: tuple) -> Sequential:
        """Create neural network model for difficulty prediction."""
        logger.info("Creating model...")
        
        model = Sequential([
            Dense(128, activation='relu', input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.1),
            
            Dense(1, activation='sigmoid')  # Output: difficulty level (0-1)
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
        """Train the activity difficulty model."""
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
                '/app/models/activity_difficulty.h5',
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
        Path('/app/app/models').mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save('/app/app/models/activity_difficulty.keras', save_format='keras')
        
        # Save scaler
        joblib.dump(self.scaler, '/app/app/models/activity_difficulty_scaler.joblib')
        
        # Save metadata
        metadata = {
            'model_type': 'activity_difficulty',
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'model_path': '/app/app/models/activity_difficulty.keras'
        }
        
        with open('/app/app/models/activity_difficulty_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info("Model saved successfully")

def main():
    """Main function to train the activity difficulty model."""
    try:
        # Initialize trainer
        trainer = ActivityDifficultyTrainer()
        
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