"""
Generate AI Models Module

This module generates the necessary AI models for the physical education service.
"""

import os
import sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import tensorflow as tf

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

def generate_performance_prediction_model():
    """Generate the performance prediction model."""
    # Create sample data
    X = np.random.rand(100, 10)  # 100 samples, 10 features
    y = np.random.rand(100)  # Target values

    # Create and train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save model
    model_path = Path(project_root) / "models" / "performance_prediction.joblib"
    joblib.dump(model, model_path)
    print(f"Performance prediction model saved to {model_path}")

def generate_behavior_analysis_model():
    """Generate the behavior analysis model."""
    # Create sample data
    X = np.random.rand(100, 10)  # 100 samples, 10 features
    y = np.random.randint(0, 2, size=100)  # Binary classification

    # Create and train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save model
    model_path = Path(project_root) / "models" / "behavior_analysis.joblib"
    joblib.dump(model, model_path)
    print(f"Behavior analysis model saved to {model_path}")

def generate_audio_analysis_model():
    """Generate the audio analysis model."""
    # Create sample data
    X = np.random.rand(100, 50, 10)  # 100 samples, 50 time steps, 10 features
    y = np.random.randint(0, 2, size=100)  # Binary classification

    # Create and train model
    inputs = tf.keras.Input(shape=(50, 10))
    x = LSTM(64, return_sequences=True)(inputs)
    x = Dropout(0.2)(x)
    x = LSTM(32)(x)
    x = Dropout(0.2)(x)
    x = Dense(16, activation='relu')(x)
    outputs = Dense(1, activation='sigmoid')(x)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X, y, epochs=1, batch_size=32, verbose=0)

    # Save model in Keras format
    model_path = Path(project_root) / "models" / "audio_analysis.keras"
    model.save(model_path)  # Removed save_format parameter as it's inferred from extension
    print(f"Audio analysis model saved to {model_path}")

def generate_ai_models():
    """Generate all AI models."""
    try:
        # Create models directory if it doesn't exist
        models_dir = Path(project_root) / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        # Generate models
        generate_performance_prediction_model()
        generate_behavior_analysis_model()
        generate_audio_analysis_model()

        print("Successfully generated all AI models.")
    except Exception as e:
        print(f"Error generating AI models: {e}")
        # Don't exit with error code during build
        if not os.getenv('DOCKER_BUILD'):
            sys.exit(1)
        else:
            print("Continuing build process despite AI model generation errors...")

if __name__ == "__main__":
    generate_ai_models() 