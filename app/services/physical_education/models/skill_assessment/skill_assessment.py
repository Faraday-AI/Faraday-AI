import numpy as np
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Any, List
import joblib

class SkillAssessmentModel:
    def __init__(self):
        # Load the trained model
        self.model = joblib.load('/app/services/physical_education/models/skill_assessment/skill_assessment.joblib')
        
        # Define skill categories
        self.skill_categories = {
            'strength': ['push-ups', 'pull-ups', 'squats'],
            'endurance': ['running', 'jumping', 'skipping'],
            'flexibility': ['stretching', 'yoga', 'pilates'],
            'coordination': ['dribbling', 'throwing', 'catching']
        }
        
        # Define assessment criteria
        self.assessment_criteria = {
            'form': ['alignment', 'technique', 'control'],
            'performance': ['speed', 'accuracy', 'consistency'],
            'progress': ['improvement', 'consistency', 'effort']
        }

    def assess_skill(self, activity: str, performance: Dict[str, Any], previous: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess a student's skill level and progress."""
        # Prepare features for the model
        features = self._prepare_features(activity, performance, previous)
        
        # Get model predictions
        predictions = self.model.predict([features])[0]
        
        # Generate assessment results
        assessment = {
            'skill_score': float(predictions[0]),
            'progress_score': float(predictions[1]),
            'detailed_analysis': self._generate_detailed_analysis(activity, performance),
            'recommendations': self._generate_recommendations(predictions, previous),
            'goals': self._generate_goals(predictions, previous)
        }
        
        return assessment

    def _prepare_features(self, activity: str, performance: Dict[str, Any], previous: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare features for the model."""
        features = []
        
        # Activity category
        category = self._get_skill_category(activity)
        features.extend(self._one_hot_encode(category, list(self.skill_categories.keys())))
        
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

    def _get_skill_category(self, activity: str) -> str:
        """Determine the category of a skill."""
        for category, activities in self.skill_categories.items():
            if activity.lower() in [a.lower() for a in activities]:
                return category
        return 'general'

    def _one_hot_encode(self, value: str, categories: List[str]) -> List[int]:
        """One-hot encode a categorical value."""
        return [1 if value == cat else 0 for cat in categories]

    def _generate_detailed_analysis(self, activity: str, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed analysis of the performance."""
        analysis = {
            'form_analysis': self._analyze_form(performance),
            'performance_analysis': self._analyze_performance(performance),
            'strengths': self._identify_strengths(performance),
            'areas_for_improvement': self._identify_improvements(performance)
        }
        
        return analysis

    def _analyze_form(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the form aspects of the performance."""
        form_analysis = {}
        
        for criterion in self.assessment_criteria['form']:
            score = performance.get(criterion, 0.5)
            form_analysis[criterion] = {
                'score': score,
                'feedback': self._generate_form_feedback(criterion, score)
            }
            
        return form_analysis

    def _analyze_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the performance aspects."""
        performance_analysis = {}
        
        for criterion in self.assessment_criteria['performance']:
            score = performance.get(criterion, 0.5)
            performance_analysis[criterion] = {
                'score': score,
                'feedback': self._generate_performance_feedback(criterion, score)
            }
            
        return performance_analysis

    def _generate_form_feedback(self, criterion: str, score: float) -> str:
        """Generate feedback for form criteria."""
        if score < 0.3:
            return f"Needs significant improvement in {criterion}"
        elif score < 0.7:
            return f"Shows basic understanding of {criterion}"
        else:
            return f"Demonstrates excellent {criterion}"

    def _generate_performance_feedback(self, criterion: str, score: float) -> str:
        """Generate feedback for performance criteria."""
        if score < 0.3:
            return f"Struggles with {criterion}"
        elif score < 0.7:
            return f"Shows moderate {criterion}"
        else:
            return f"Excels in {criterion}"

    def _identify_strengths(self, performance: Dict[str, Any]) -> List[str]:
        """Identify strengths in the performance."""
        strengths = []
        
        for criterion, score in performance.items():
            if score > 0.7:
                strengths.append(criterion)
                
        return strengths

    def _identify_improvements(self, performance: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement."""
        improvements = []
        
        for criterion, score in performance.items():
            if score < 0.3:
                improvements.append(criterion)
                
        return improvements

    def _generate_recommendations(self, predictions: np.ndarray, previous: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on assessment results."""
        recommendations = []
        
        # Skill level recommendations
        if predictions[0] < 0.3:
            recommendations.append("Focus on fundamental skills and techniques")
        elif predictions[0] < 0.7:
            recommendations.append("Practice consistently to improve skills")
        else:
            recommendations.append("Challenge yourself with more advanced variations")
            
        # Progress recommendations
        if predictions[1] < 0.3:
            recommendations.append("Increase practice frequency")
        elif predictions[1] < 0.7:
            recommendations.append("Maintain current practice routine")
        else:
            recommendations.append("Consider setting more challenging goals")
            
        return recommendations

    def _generate_goals(self, predictions: np.ndarray, previous: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized goals based on assessment."""
        goals = []
        
        # Short-term goals
        goals.append({
            'type': 'short_term',
            'description': self._generate_short_term_goal(predictions),
            'timeline': '1-2 weeks'
        })
        
        # Medium-term goals
        goals.append({
            'type': 'medium_term',
            'description': self._generate_medium_term_goal(predictions),
            'timeline': '1 month'
        })
        
        # Long-term goals
        goals.append({
            'type': 'long_term',
            'description': self._generate_long_term_goal(predictions),
            'timeline': '3 months'
        })
        
        return goals

    def _generate_short_term_goal(self, predictions: np.ndarray) -> str:
        """Generate a short-term goal."""
        if predictions[0] < 0.3:
            return "Master basic form and technique"
        elif predictions[0] < 0.7:
            return "Improve consistency in performance"
        else:
            return "Refine advanced techniques"

    def _generate_medium_term_goal(self, predictions: np.ndarray) -> str:
        """Generate a medium-term goal."""
        if predictions[0] < 0.3:
            return "Build fundamental skills to intermediate level"
        elif predictions[0] < 0.7:
            return "Achieve consistent performance at current level"
        else:
            return "Master advanced variations and combinations"

    def _generate_long_term_goal(self, predictions: np.ndarray) -> str:
        """Generate a long-term goal."""
        if predictions[0] < 0.3:
            return "Develop comprehensive skill set"
        elif predictions[0] < 0.7:
            return "Achieve advanced skill level"
        else:
            return "Master complex skill combinations and variations" 