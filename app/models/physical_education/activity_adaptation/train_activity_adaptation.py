import os
import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import joblib
from datetime import datetime

class ActivityAdaptationTrainer:
    def __init__(self):
        self.activity_categories = ['strength', 'flexibility', 'endurance', 'coordination']
        self.adaptation_levels = ['beginner', 'intermediate', 'advanced']
        self.student_needs = {
            'physical': ['mobility_issues', 'strength_limitations', 'limited_flexibility'],
            'cognitive': ['attention_difficulties', 'memory_challenges'],
            'sensory': ['visual_impairment', 'hearing_impairment']
        }
        self.environmental_factors = {
            'space': ['limited', 'adequate', 'spacious'],
            'equipment': ['none', 'minimal', 'full'],
            'surface': ['hard', 'soft', 'uneven']
        }
    
    def prepare_dataset(self, data_dir):
        """Prepare dataset from JSON files."""
        features = []
        labels = []
        
        for category in self.activity_categories:
            category_dir = Path(data_dir) / category
            if not category_dir.exists():
                continue
                
            for activity_dir in category_dir.iterdir():
                if not activity_dir.is_dir():
                    continue
                    
                for json_file in activity_dir.glob('*.json'):
                    with open(json_file) as f:
                        data = json.load(f)
                        
                        # Extract features
                        feature_vector = []
                        
                        # Activity category (one-hot encoded)
                        category_vector = [0] * len(self.activity_categories)
                        category_vector[self.activity_categories.index(category)] = 1
                        feature_vector.extend(category_vector)
                        
                        # Student needs (one-hot encoded)
                        for need_type, needs in self.student_needs.items():
                            need_vector = [0] * len(needs)
                            for need in data['needs'].get(need_type, []):
                                if need in needs:
                                    need_vector[needs.index(need)] = 1
                            feature_vector.extend(need_vector)
                        
                        # Environmental factors (one-hot encoded)
                        for factor_type, factors in self.environmental_factors.items():
                            factor_vector = [0] * len(factors)
                            factor = data['environment'].get(factor_type, '')
                            if factor in factors:
                                factor_vector[factors.index(factor)] = 1
                            feature_vector.extend(factor_vector)
                        
                        # Performance metrics
                        performance = data['performance']
                        feature_vector.extend([
                            performance['alignment'],
                            performance['technique'],
                            performance['control'],
                            performance['speed'],
                            performance['accuracy'],
                            performance['consistency']
                        ])
                        
                        # Previous performance
                        if data['previous']:
                            prev = data['previous'][0]
                            feature_vector.extend([
                                prev['improvement'],
                                prev['consistency'],
                                prev['effort']
                            ])
                        else:
                            feature_vector.extend([0, 0, 0])
                        
                        features.append(feature_vector)
                        labels.append(self.adaptation_levels.index(data['adaptation_level']))
        
        return np.array(features), np.array(labels)
    
    def train(self, data_dir):
        """Train the model and save it."""
        # Prepare dataset
        X, y = self.prepare_dataset(data_dir)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Save model
        model_dir = Path('app/services/physical_education/models/activity_adaptation')
        model_dir.mkdir(exist_ok=True)
        joblib.dump(model, model_dir / 'activity_adaptation.joblib')
        
        # Save metadata
        metadata = {
            'input_features': X.shape[1],
            'output_features': len(self.adaptation_levels),  # Number of possible adaptation levels
            'model_type': 'activity_adaptation',
            'training_date': datetime.now().isoformat()
        }
        
        with open(model_dir / 'activity_adaptation_metadata.json', 'w') as f:
            json.dump(metadata, f)

if __name__ == '__main__':
    # Initialize trainer
    trainer = ActivityAdaptationTrainer()
    
    # Train model
    trainer.train(data_dir='/app/data/activity_adaptations') 