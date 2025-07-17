import os
import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
import joblib

class SkillAssessmentTrainer:
    def __init__(self):
        self.skill_categories = ['strength', 'flexibility', 'endurance', 'coordination']
        self.performance_metrics = ['alignment', 'technique', 'control', 'speed', 'accuracy', 'consistency']
    
    def prepare_dataset(self, data_dir):
        """Prepare dataset from JSON files."""
        features = []
        labels = []
        
        for category in self.skill_categories:
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
                        category_vector = [0] * len(self.skill_categories)
                        category_vector[self.skill_categories.index(category)] = 1
                        feature_vector.extend(category_vector)
                        
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
                        labels.append(data['skill_score'])
        
        return np.array(features), np.array(labels)
    
    def train(self, data_dir):
        """Train the model and save it."""
        # Prepare dataset
        X, y = self.prepare_dataset(data_dir)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Save model
        model_dir = Path('app/services/physical_education/models/skill_assessment')
        model_dir.mkdir(exist_ok=True)
        joblib.dump(model, model_dir / 'skill_assessment.joblib')
        
        # Save metadata
        metadata = {
            'skill_categories': self.skill_categories,
            'performance_metrics': self.performance_metrics,
            'feature_names': [
                'skill_category_' + cat for cat in self.skill_categories
            ] + [
                'alignment', 'technique', 'control', 'speed', 'accuracy', 'consistency',
                'prev_improvement', 'prev_consistency', 'prev_effort'
            ]
        }
        
        with open(model_dir / 'skill_assessment_metadata.json', 'w') as f:
            json.dump(metadata, f)

if __name__ == '__main__':
    # Initialize trainer
    trainer = SkillAssessmentTrainer()
    
    # Train model
    trainer.train(data_dir='/app/data/skill_assessments') 