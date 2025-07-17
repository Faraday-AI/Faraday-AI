import os
import json
import random
from pathlib import Path
from typing import Dict, List, Any

class TrainingDataGenerator:
    def __init__(self):
        # Define activity categories and types
        self.activities = {
            'strength': ['push-ups', 'pull-ups', 'squats', 'lunges'],
            'cardio': ['running', 'jumping', 'skipping', 'dancing'],
            'flexibility': ['stretching', 'yoga', 'pilates', 'gymnastics'],
            'coordination': ['dribbling', 'throwing', 'catching', 'balancing']
        }
        
        # Define student needs
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
        
        # Define assessment criteria
        self.assessment_criteria = {
            'form': ['alignment', 'technique', 'control'],
            'performance': ['speed', 'accuracy', 'consistency'],
            'progress': ['improvement', 'consistency', 'effort']
        }

    def generate_activity_adaptation_data(self, num_samples: int = 10):
        """Generate activity adaptation data."""
        for category, activities in self.activities.items():
            for activity in activities:
                activity_dir = Path(f'data/activity_adaptations/{category}/{activity}')
                activity_dir.mkdir(parents=True, exist_ok=True)
                
                for i in range(num_samples):
                    data = {
                        'activity': activity,
                        'needs': self._generate_needs(),
                        'environment': self._generate_environment(),
                        'adaptation_level': random.choice(['beginner', 'intermediate', 'advanced']),
                        'modifications': self._generate_modifications(activity),
                        'safety_considerations': self._generate_safety_considerations(activity),
                        'equipment_adaptations': self._generate_equipment_adaptations(activity)
                    }
                    
                    with open(activity_dir / f'sample_{i+1}.json', 'w') as f:
                        json.dump(data, f, indent=4)

    def generate_skill_assessment_data(self, num_samples: int = 10):
        """Generate skill assessment data."""
        for category, activities in self.activities.items():
            for activity in activities:
                activity_dir = Path(f'data/skill_assessments/{category}/{activity}')
                activity_dir.mkdir(parents=True, exist_ok=True)
                
                for i in range(num_samples):
                    data = {
                        'skill': activity,
                        'performance': self._generate_performance(),
                        'previous': self._generate_previous_assessments(),
                        'skill_score': random.uniform(0.3, 0.9),
                        'progress_score': random.uniform(0.3, 0.9),
                        'detailed_analysis': self._generate_detailed_analysis(),
                        'recommendations': self._generate_recommendations(),
                        'goals': self._generate_goals()
                    }
                    
                    with open(activity_dir / f'sample_{i+1}.json', 'w') as f:
                        json.dump(data, f, indent=4)

    def generate_movement_analysis_data(self, num_samples: int = 10):
        """Generate movement analysis data."""
        movements = {
            'jumping': ['vertical_jump', 'broad_jump'],
            'running': ['sprint', 'jog'],
            'throwing': ['overhead_throw', 'underhand_throw'],
            'catching': ['two_hand_catch', 'one_hand_catch']
        }
        
        for category, movement_types in movements.items():
            for movement in movement_types:
                movement_dir = Path(f'data/movement_videos/{category}/{movement}')
                movement_dir.mkdir(parents=True, exist_ok=True)
                
                for i in range(num_samples):
                    data = {
                        'movement': movement,
                        'key_points': self._generate_key_points(),
                        'angles': self._generate_angles(),
                        'distances': self._generate_distances(),
                        'analysis': self._generate_analysis(),
                        'recommendations': self._generate_movement_recommendations(movement),
                        'safety_considerations': self._generate_movement_safety(movement),
                        'progression': self._generate_progression()
                    }
                    
                    with open(movement_dir / f'sample_{i+1}.json', 'w') as f:
                        json.dump(data, f, indent=4)

    def _generate_needs(self) -> Dict[str, List[str]]:
        """Generate random student needs."""
        needs = {}
        for category, need_types in self.student_needs.items():
            num_needs = random.randint(0, len(need_types))
            needs[category] = random.sample(need_types, num_needs)
        return needs

    def _generate_environment(self) -> Dict[str, str]:
        """Generate random environment factors."""
        environment = {}
        for factor, levels in self.environment_factors.items():
            environment[factor] = random.choice(levels)
        return environment

    def _generate_modifications(self, activity: str) -> Dict[str, Any]:
        """Generate activity modifications."""
        return {
            'form': f"Modified {activity}",
            'repetitions': random.randint(5, 15),
            'sets': random.randint(2, 4),
            'rest_time': random.randint(30, 90),
            'progression': f"Basic to advanced {activity}"
        }

    def _generate_safety_considerations(self, activity: str) -> List[str]:
        """Generate safety considerations."""
        return [
            f"Maintain proper form during {activity}",
            f"Start with basic variations of {activity}",
            f"Focus on controlled movements during {activity}"
        ]

    def _generate_equipment_adaptations(self, activity: str) -> Dict[str, List[str]]:
        """Generate equipment adaptations."""
        return {
            'required': ['exercise mat'],
            'optional': ['resistance bands', 'weights']
        }

    def _generate_performance(self) -> Dict[str, float]:
        """Generate performance scores."""
        performance = {}
        for criterion in self.assessment_criteria['form']:
            performance[criterion] = random.uniform(0.3, 0.9)
        for criterion in self.assessment_criteria['performance']:
            performance[criterion] = random.uniform(0.3, 0.9)
        return performance

    def _generate_previous_assessments(self) -> List[Dict[str, float]]:
        """Generate previous assessment data."""
        previous = []
        for _ in range(random.randint(1, 3)):
            assessment = {}
            for criterion in self.assessment_criteria['progress']:
                assessment[criterion] = random.uniform(0.3, 0.9)
            previous.append(assessment)
        return previous

    def _generate_detailed_analysis(self) -> Dict[str, Any]:
        """Generate detailed analysis."""
        return {
            'form_analysis': {
                criterion: {
                    'score': random.uniform(0.3, 0.9),
                    'feedback': f"Feedback for {criterion}"
                }
                for criterion in self.assessment_criteria['form']
            },
            'performance_analysis': {
                criterion: {
                    'score': random.uniform(0.3, 0.9),
                    'feedback': f"Feedback for {criterion}"
                }
                for criterion in self.assessment_criteria['performance']
            },
            'strengths': random.sample(
                self.assessment_criteria['form'] + self.assessment_criteria['performance'],
                random.randint(1, 3)
            ),
            'areas_for_improvement': random.sample(
                self.assessment_criteria['form'] + self.assessment_criteria['performance'],
                random.randint(1, 3)
            )
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations."""
        return [
            "Focus on form improvement",
            "Practice consistently",
            "Set achievable goals"
        ]

    def _generate_goals(self) -> List[Dict[str, str]]:
        """Generate goals."""
        return [
            {
                'type': 'short_term',
                'description': "Improve basic skills",
                'timeline': "1-2 weeks"
            },
            {
                'type': 'medium_term',
                'description': "Achieve intermediate level",
                'timeline': "1 month"
            },
            {
                'type': 'long_term',
                'description': "Master advanced techniques",
                'timeline': "3 months"
            }
        ]

    def _generate_key_points(self) -> Dict[str, Dict[str, List[float]]]:
        """Generate key points data."""
        return {
            'shoulders': {
                'left': [random.uniform(0.4, 0.6), random.uniform(0.2, 0.4), 0.0],
                'right': [random.uniform(0.4, 0.6), random.uniform(0.2, 0.4), 0.0]
            },
            'hips': {
                'left': [random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), 0.0],
                'right': [random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), 0.0]
            },
            'knees': {
                'left': [random.uniform(0.4, 0.6), random.uniform(0.6, 0.8), 0.0],
                'right': [random.uniform(0.4, 0.6), random.uniform(0.6, 0.8), 0.0]
            },
            'ankles': {
                'left': [random.uniform(0.4, 0.6), random.uniform(0.8, 1.0), 0.0],
                'right': [random.uniform(0.4, 0.6), random.uniform(0.8, 1.0), 0.0]
            }
        }

    def _generate_angles(self) -> Dict[str, float]:
        """Generate angle measurements."""
        return {
            'shoulder_angle': random.uniform(160, 200),
            'hip_angle': random.uniform(80, 100),
            'knee_angle': random.uniform(80, 100)
        }

    def _generate_distances(self) -> Dict[str, float]:
        """Generate distance measurements."""
        return {
            'shoulder_width': random.uniform(0.3, 0.5),
            'hip_width': random.uniform(0.2, 0.4)
        }

    def _generate_analysis(self) -> Dict[str, float]:
        """Generate analysis scores."""
        return {
            'form_score': random.uniform(0.3, 0.9),
            'alignment_score': random.uniform(0.3, 0.9),
            'stability_score': random.uniform(0.3, 0.9),
            'power_score': random.uniform(0.3, 0.9)
        }

    def _generate_movement_recommendations(self, movement: str) -> List[str]:
        """Generate movement-specific recommendations."""
        return [
            f"Focus on proper form during {movement}",
            f"Maintain alignment during {movement}",
            f"Control movement during {movement}"
        ]

    def _generate_movement_safety(self, movement: str) -> List[str]:
        """Generate movement-specific safety considerations."""
        return [
            f"Ensure proper technique during {movement}",
            f"Start with basic variations of {movement}",
            f"Focus on controlled movements during {movement}"
        ]

    def _generate_progression(self) -> Dict[str, Any]:
        """Generate progression information."""
        return {
            'current_level': random.choice(['beginner', 'intermediate', 'advanced']),
            'next_level': random.choice(['intermediate', 'advanced']),
            'exercises': [
                "Basic variations",
                "Intermediate variations",
                "Advanced variations"
            ]
        }

if __name__ == '__main__':
    # Create data directories
    Path('data').mkdir(exist_ok=True)
    
    # Initialize generator
    generator = TrainingDataGenerator()
    
    # Generate data
    generator.generate_activity_adaptation_data()
    generator.generate_skill_assessment_data()
    generator.generate_movement_analysis_data() 