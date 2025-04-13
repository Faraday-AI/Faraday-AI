import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from typing import List, Dict, Any
from pathlib import Path

class ActivityAdaptationTrainer:
    def __init__(self):
        # Define activity categories
        self.activity_categories = {
            'strength': ['push-ups', 'pull-ups', 'squats', 'lunges'],
            'cardio': ['running', 'jumping', 'skipping', 'dancing'],
            'flexibility': ['stretching', 'yoga', 'pilates', 'gymnastics'],
            'coordination': ['dribbling', 'throwing', 'catching', 'balancing']
        }
        
        # Define adaptation levels
        self.adaptation_levels = ['beginner', 'intermediate', 'advanced']
        
        # Define student needs categories
        self.student_needs = {
            'physical': ['mobility_issues', 'strength_limitations', 'coordination_challenges'],
            'cognitive': ['attention_difficulties', 'memory_challenges', 'processing_speed'],
            'sensory': ['visual_impairment', 'auditory_impairment', 'sensory_sensitivity']
        }
        
        # Define environment factors
        self.environment_factors = {
            'space': ['limited', 'adequate', 'spacious'],
            'equipment': ['minimal', 'basic', 'full'],
            'surface': ['hard', 'soft', 'mixed']
        }

    def prepare_dataset(self, data_dir: str) -> tuple:
        """Prepare the dataset for training."""
        X = []
        y = []
        
        # Process each activity in the dataset
        for category, activities in self.activity_categories.items():
            for activity in activities:
                activity_dir = os.path.join(data_dir, category, activity)
                if not os.path.exists(activity_dir):
                    continue
                    
                for data_file in os.listdir(activity_dir):
                    if not data_file.endswith('.json'):
                        continue
                        
                    data_path = os.path.join(activity_dir, data_file)
                    with open(data_path, 'r') as f:
                        data = json.load(f)
                        
                    features = self._prepare_features(
                        activity=activity,
                        needs=data['needs'],
                        environment=data['environment']
                    )
                    
                    if features is not None:
                        X.append(features)
                        y.append(data['adaptation_level'])
        
        return np.array(X), np.array(y)

    def _prepare_features(self, activity: str, needs: Dict[str, List[str]], environment: Dict[str, str]) -> np.ndarray:
        """Prepare features for the model."""
        features = []
        
        # Activity category
        category = self._get_activity_category(activity)
        features.extend(self._one_hot_encode(category, list(self.activity_categories.keys())))
        
        # Activity type
        features.extend(self._one_hot_encode(activity, self._get_all_activities()))
        
        # Student needs
        for need_category, need_types in self.student_needs.items():
            category_needs = needs.get(need_category, [])
            features.extend(self._one_hot_encode_multiple(category_needs, need_types))
        
        # Environment factors
        for factor, levels in self.environment_factors.items():
            level = environment.get(factor, 'adequate')
            features.extend(self._one_hot_encode(level, levels))
        
        return np.array(features)

    def _get_activity_category(self, activity: str) -> str:
        """Determine the category of an activity."""
        for category, activities in self.activity_categories.items():
            if activity in activities:
                return category
        return 'general'

    def _get_all_activities(self) -> List[str]:
        """Get all activity types."""
        activities = []
        for category_activities in self.activity_categories.values():
            activities.extend(category_activities)
        return activities

    def _one_hot_encode(self, value: str, categories: List[str]) -> List[int]:
        """One-hot encode a categorical value."""
        return [1 if value == cat else 0 for cat in categories]

    def _one_hot_encode_multiple(self, values: List[str], categories: List[str]) -> List[int]:
        """One-hot encode multiple categorical values."""
        return [1 if cat in values else 0 for cat in categories]

    def create_model(self) -> RandomForestClassifier:
        """Create the random forest classifier."""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    def train(self, data_dir: str):
        """Train the activity adaptation model."""
        # Prepare dataset
        X, y = self.prepare_dataset(data_dir)
        
        # Encode target variable
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        
        # Create and train model
        model = self.create_model()
        model.fit(X, y_encoded)
        
        # Save model
        joblib.dump(model, 'models/activity_adaptation.joblib')
        
        # Save model metadata
        metadata = {
            'activity_categories': self.activity_categories,
            'adaptation_levels': self.adaptation_levels,
            'student_needs': self.student_needs,
            'environment_factors': self.environment_factors,
            'label_encoder_classes': label_encoder.classes_.tolist()
        }
        
        with open('models/activity_adaptation_metadata.json', 'w') as f:
            json.dump(metadata, f)

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    Path('models').mkdir(exist_ok=True)
    
    # Initialize trainer
    trainer = ActivityAdaptationTrainer()
    
    # Train model
    trainer.train(data_dir='data/activity_adaptations') 