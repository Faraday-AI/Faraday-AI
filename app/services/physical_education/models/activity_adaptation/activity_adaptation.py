import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any, List
import joblib

class ActivityAdaptationModel:
    def __init__(self):
        # Load the trained model
        self.model = joblib.load('/app/services/physical_education/models/activity_adaptation/activity_adaptation.joblib')
        
        # Define activity categories
        self.activity_categories = {
            'strength': ['push-ups', 'pull-ups', 'squats'],
            'endurance': ['running', 'jumping', 'skipping'],
            'flexibility': ['stretching', 'yoga', 'pilates'],
            'coordination': ['dribbling', 'throwing', 'catching']
        }
        
        # Define adaptation levels
        self.adaptation_levels = {
            'beginner': 0,
            'intermediate': 1,
            'advanced': 2
        }

    def adapt_activity(self, activity: str, needs: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt an activity based on student needs and environment."""
        # Prepare features for the model
        features = self._prepare_features(activity, needs, environment)
        
        # Get model predictions
        predictions = self.model.predict_proba([features])[0]
        
        # Generate adaptations
        adaptations = {
            'difficulty_level': self._determine_difficulty(predictions),
            'modifications': self._generate_modifications(activity, needs),
            'safety_considerations': self._generate_safety_guidelines(activity, environment),
            'equipment_adaptations': self._adapt_equipment(activity, environment['equipment'])
        }
        
        return adaptations

    def _prepare_features(self, activity: str, needs: Dict[str, Any], environment: Dict[str, Any]) -> np.ndarray:
        """Prepare features for the model."""
        features = []
        
        # Activity category
        category = self._get_activity_category(activity)
        features.extend(self._one_hot_encode(category, list(self.activity_categories.keys())))
        
        # Student needs
        features.append(needs.get('skill_level', 0.5))
        features.append(needs.get('physical_limitations', 0))
        features.append(needs.get('learning_style', 0.5))
        
        # Environment factors
        features.append(environment.get('space_available', 0.5))
        features.append(environment.get('equipment_available', 0.5))
        features.append(environment.get('weather_conditions', 0.5))
        
        return np.array(features)

    def _get_activity_category(self, activity: str) -> str:
        """Determine the category of an activity."""
        for category, activities in self.activity_categories.items():
            if activity.lower() in [a.lower() for a in activities]:
                return category
        return 'general'

    def _one_hot_encode(self, value: str, categories: List[str]) -> List[int]:
        """One-hot encode a categorical value."""
        return [1 if value == cat else 0 for cat in categories]

    def _determine_difficulty(self, predictions: np.ndarray) -> str:
        """Determine the appropriate difficulty level."""
        level_index = np.argmax(predictions)
        return list(self.adaptation_levels.keys())[level_index]

    def _generate_modifications(self, activity: str, needs: Dict[str, Any]) -> List[str]:
        """Generate activity modifications based on student needs."""
        modifications = []
        
        # Skill level modifications
        if needs.get('skill_level', 0.5) < 0.3:
            modifications.append("Simplify the movement pattern")
            modifications.append("Reduce the number of repetitions")
        elif needs.get('skill_level', 0.5) > 0.7:
            modifications.append("Increase the complexity of the movement")
            modifications.append("Add variations to challenge coordination")
            
        # Physical limitation modifications
        if needs.get('physical_limitations', 0):
            modifications.append("Provide alternative movements")
            modifications.append("Adjust range of motion")
            
        return modifications

    def _generate_safety_guidelines(self, activity: str, environment: Dict[str, Any]) -> List[str]:
        """Generate safety guidelines for the activity."""
        guidelines = []
        
        # Space safety
        if environment.get('space_available', 0.5) < 0.3:
            guidelines.append("Ensure adequate spacing between students")
            guidelines.append("Modify activity to fit available space")
            
        # Equipment safety
        if environment.get('equipment_available', 0.5) < 0.3:
            guidelines.append("Check equipment for safety before use")
            guidelines.append("Ensure proper equipment setup")
            
        # Weather safety
        if environment.get('weather_conditions', 0.5) < 0.3:
            guidelines.append("Monitor weather conditions")
            guidelines.append("Have alternative indoor activities ready")
            
        return guidelines

    def _adapt_equipment(self, activity: str, available_equipment: List[str]) -> List[str]:
        """Adapt equipment usage for the activity."""
        adaptations = []
        
        # Check if required equipment is available
        required_equipment = self._get_required_equipment(activity)
        missing_equipment = [eq for eq in required_equipment if eq not in available_equipment]
        
        if missing_equipment:
            adaptations.append(f"Substitute missing equipment: {', '.join(missing_equipment)}")
            adaptations.append("Modify activity to use available equipment")
            
        return adaptations

    def _get_required_equipment(self, activity: str) -> List[str]:
        """Get the required equipment for an activity."""
        # This would typically come from a database or configuration
        equipment_map = {
            'push-ups': [],
            'pull-ups': ['pull-up bar'],
            'running': ['cones', 'stopwatch'],
            'basketball': ['basketball', 'hoop'],
            'soccer': ['soccer ball', 'cones']
        }
        
        return equipment_map.get(activity.lower(), []) 