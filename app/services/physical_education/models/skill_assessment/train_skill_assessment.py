import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import json
from typing import List, Dict, Any
from pathlib import Path

class SkillAssessmentTrainer:
    def __init__(self):
        # Define skill categories
        self.skill_categories = {
            'strength': ['push-ups', 'pull-ups', 'squats', 'lunges'],
            'endurance': ['running', 'jumping', 'skipping', 'dancing'],
            'flexibility': ['stretching', 'yoga', 'pilates', 'gymnastics'],
            'coordination': ['dribbling', 'throwing', 'catching', 'balancing']
        }
        
        # Define assessment criteria
        self.assessment_criteria = {
            'form': ['alignment', 'technique', 'control'],
            'performance': ['speed', 'accuracy', 'consistency'],
            'progress': ['improvement', 'consistency', 'effort']
        }

    def prepare_dataset(self, data_dir: str) -> tuple:
        """Prepare the dataset for training."""
        X = []
        y = []
        
        # Process each skill in the dataset
        for category, skills in self.skill_categories.items():
            for skill in skills:
                skill_dir = os.path.join(data_dir, category, skill)
                if not os.path.exists(skill_dir):
                    continue
                    
                for data_file in os.listdir(skill_dir):
                    if not data_file.endswith('.json'):
                        continue
                        
                    data_path = os.path.join(skill_dir, data_file)
                    with open(data_path, 'r') as f:
                        data = json.load(f)
                        
                    features = self._prepare_features(
                        skill=skill,
                        performance=data['performance'],
                        previous=data.get('previous', [])
                    )
                    
                    if features is not None:
                        X.append(features)
                        y.append([
                            data['skill_score'],
                            data['progress_score']
                        ])
        
        return np.array(X), np.array(y)

    def _prepare_features(self, skill: str, performance: Dict[str, float], previous: List[Dict[str, float]]) -> np.ndarray:
        """Prepare features for the model."""
        features = []
        
        # Skill category
        category = self._get_skill_category(skill)
        features.extend(self._one_hot_encode(category, list(self.skill_categories.keys())))
        
        # Skill type
        features.extend(self._one_hot_encode(skill, self._get_all_skills()))
        
        # Current performance
        for criterion in self.assessment_criteria['form']:
            features.append(performance.get(criterion, 0.5))
        for criterion in self.assessment_criteria['performance']:
            features.append(performance.get(criterion, 0.5))
            
        # Historical performance
        if previous:
            last_assessment = previous[-1]
            for criterion in self.assessment_criteria['progress']:
                features.append(last_assessment.get(criterion, 0.5))
        else:
            features.extend([0.5] * len(self.assessment_criteria['progress']))
            
        return np.array(features)

    def _get_skill_category(self, skill: str) -> str:
        """Determine the category of a skill."""
        for category, skills in self.skill_categories.items():
            if skill in skills:
                return category
        return 'general'

    def _get_all_skills(self) -> List[str]:
        """Get all skill types."""
        skills = []
        for category_skills in self.skill_categories.values():
            skills.extend(category_skills)
        return skills

    def _one_hot_encode(self, value: str, categories: List[str]) -> List[int]:
        """One-hot encode a categorical value."""
        return [1 if value == cat else 0 for cat in categories]

    def create_model(self) -> RandomForestRegressor:
        """Create the random forest regressor."""
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    def train(self, data_dir: str):
        """Train the skill assessment model."""
        # Prepare dataset
        X, y = self.prepare_dataset(data_dir)
        
        # Create and train model
        model = self.create_model()
        model.fit(X, y)
        
        # Save model
        joblib.dump(model, 'models/skill_assessment.joblib')
        
        # Save model metadata
        metadata = {
            'skill_categories': self.skill_categories,
            'assessment_criteria': self.assessment_criteria
        }
        
        with open('models/skill_assessment_metadata.json', 'w') as f:
            json.dump(metadata, f)

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    Path('models').mkdir(exist_ok=True)
    
    # Initialize trainer
    trainer = SkillAssessmentTrainer()
    
    # Train model
    trainer.train(data_dir='data/skill_assessments') 