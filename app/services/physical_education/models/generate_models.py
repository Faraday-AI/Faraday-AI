import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

def generate_sample_data(num_students: int = 100, num_activities: int = 20) -> Dict[str, pd.DataFrame]:
    """Generate sample data for model training."""
    # Create directories if they don't exist
    os.makedirs('/app/services/physical_education/models', exist_ok=True)
    os.makedirs('/app/models', exist_ok=True)
    
    # Generate student data
    students = pd.DataFrame({
        'id': range(1, num_students + 1),
        'name': [f'Student {i}' for i in range(1, num_students + 1)],
        'age': np.random.randint(10, 18, num_students),
        'gender': np.random.choice(['M', 'F'], num_students),
        'fitness_level': np.random.choice(['Beginner', 'Intermediate', 'Advanced'], num_students),
        'medical_conditions': np.random.choice(['None', 'Asthma', 'Allergies', 'None'], num_students),
        'created_at': [datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(num_students)]
    })
    
    # Generate activity data
    activities = pd.DataFrame({
        'id': [f'ACT{i:03d}' for i in range(1, num_activities + 1)],
        'name': [f'Activity {i}' for i in range(1, num_activities + 1)],
        'description': [f'Description for Activity {i}' for i in range(1, num_activities + 1)],
        'type': np.random.choice(['Cardio', 'Strength', 'Flexibility', 'Balance'], num_activities),
        'difficulty_level': np.random.choice(['Easy', 'Medium', 'Hard'], num_activities),
        'duration_minutes': np.random.randint(10, 60, num_activities),
        'equipment_requirements': np.random.choice(['None', 'Basic', 'Advanced'], num_activities),
        'created_at': [datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(num_activities)]
    })
    
    # Generate performance data
    performance_data = []
    for student_id in students['id']:
        for activity_id in activities['id']:
            performance_data.append({
                'student_id': student_id,
                'activity_id': activity_id,
                'score': np.random.randint(1, 100),
                'duration_minutes': np.random.randint(10, 60),
                'calories_burned': np.random.randint(50, 500),
                'heart_rate': np.random.randint(60, 180),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            })
    performance = pd.DataFrame(performance_data)
    
    return {
        'students': students,
        'activities': activities,
        'performance': performance
    }

def generate_models():
    """Generate and save all required models."""
    # Generate sample data
    data = generate_sample_data()
    
    # Train performance prediction model
    X = data['performance'][['student_id', 'duration_minutes', 'heart_rate']].copy()
    
    # Handle activity_id separately with LabelEncoder
    le = LabelEncoder()
    activity_encoded = le.fit_transform(data['performance']['activity_id'])
    X.loc[:, 'activity_id_encoded'] = activity_encoded
    
    y = data['performance']['score']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    # Save models in both locations
    for model_dir in ['/app/services/physical_education/models', '/app/models']:
        joblib.dump(model, os.path.join(model_dir, 'performance_prediction.h5'))
        joblib.dump(scaler, os.path.join(model_dir, 'performance_scaler.joblib'))
        joblib.dump(le, os.path.join(model_dir, 'activity_encoder.joblib'))
    
    # Train behavior analysis model
    X_behavior = data['performance'][['score', 'duration_minutes', 'calories_burned']].copy()
    y_behavior = np.random.choice(['Good', 'Average', 'Poor'], len(X_behavior))
    
    behavior_model = RandomForestClassifier(n_estimators=100, random_state=42)
    behavior_model.fit(X_behavior, y_behavior)
    
    for model_dir in ['/app/services/physical_education/models', '/app/models']:
        joblib.dump(behavior_model, os.path.join(model_dir, 'behavior_analysis.joblib'))
    
    # Train audio analysis model
    model = Sequential([
        LSTM(64, input_shape=(100, 13), return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001),
                 loss='binary_crossentropy',
                 metrics=['accuracy'])
    
    for model_dir in ['/app/services/physical_education/models', '/app/models']:
        model.save(os.path.join(model_dir, 'audio_analysis.h5'))

if __name__ == '__main__':
    generate_models() 