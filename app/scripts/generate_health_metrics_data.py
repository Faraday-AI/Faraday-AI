import os
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, Any

class HealthMetricsDataGenerator:
    def __init__(self):
        self.data_dir = 'data/health_metrics'
        
    def generate_student_data(self, num_students: int = 100) -> None:
        """Generate sample health metrics data for students."""
        # Create data directory if it doesn't exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        for i in range(num_students):
            student_data = self._generate_student_metrics()
            
            # Save student data
            file_path = Path(self.data_dir) / f'student_{i+1}.json'
            with open(file_path, 'w') as f:
                json.dump(student_data, f, indent=4)
    
    def _generate_student_metrics(self) -> Dict[str, Any]:
        """Generate health metrics for a single student."""
        # Physical metrics
        height = random.uniform(150, 190)  # cm
        weight = random.uniform(40, 100)   # kg
        bmi = weight / ((height/100) ** 2)
        body_fat_percentage = random.uniform(5, 30)
        muscle_mass = random.uniform(20, 50)
        
        # Vital signs
        resting_heart_rate = random.uniform(60, 100)
        blood_pressure_systolic = random.uniform(90, 140)
        blood_pressure_diastolic = random.uniform(60, 90)
        oxygen_saturation = random.uniform(95, 100)
        respiratory_rate = random.uniform(12, 20)
        
        # Activity metrics
        activity_level = random.uniform(0, 1)
        exercise_frequency = random.uniform(0, 1)
        exercise_duration = random.uniform(0, 1)
        exercise_intensity = random.uniform(0, 1)
        daily_steps = random.randint(2000, 15000)
        sedentary_time = random.uniform(4, 12)  # hours
        
        # Performance metrics
        strength_score = random.uniform(0, 1)
        endurance_score = random.uniform(0, 1)
        flexibility_score = random.uniform(0, 1)
        coordination_score = random.uniform(0, 1)
        agility_score = random.uniform(0, 1)
        balance_score = random.uniform(0, 1)
        power_score = random.uniform(0, 1)
        speed_score = random.uniform(0, 1)
        
        # Health indicators
        sleep_quality = random.uniform(0, 1)
        sleep_duration = random.uniform(6, 9)  # hours
        nutrition_score = random.uniform(0, 1)
        hydration_level = random.uniform(0, 1)
        stress_level = random.uniform(0, 1)
        recovery_rate = random.uniform(0, 1)
        immune_function = random.uniform(0, 1)
        
        # Mental health indicators
        mood_score = random.uniform(0, 1)
        anxiety_level = random.uniform(0, 1)
        focus_score = random.uniform(0, 1)
        motivation_level = random.uniform(0, 1)
        confidence_score = random.uniform(0, 1)
        
        # Injury history
        injury_history = {
            'total_injuries': random.randint(0, 5),
            'recent_injuries': random.randint(0, 2),
            'injury_severity': random.uniform(0, 1),
            'recovery_status': random.uniform(0, 1)
        }
        
        # Lifestyle factors
        lifestyle_factors = {
            'screen_time': random.uniform(2, 8),  # hours
            'social_activity': random.uniform(0, 1),
            'academic_stress': random.uniform(0, 1),
            'family_support': random.uniform(0, 1),
            'peer_support': random.uniform(0, 1)
        }
        
        # Calculate overall health score
        health_score = self._calculate_health_score(
            activity_level=activity_level,
            exercise_frequency=exercise_frequency,
            exercise_duration=exercise_duration,
            exercise_intensity=exercise_intensity,
            strength_score=strength_score,
            endurance_score=endurance_score,
            flexibility_score=flexibility_score,
            coordination_score=coordination_score,
            sleep_quality=sleep_quality,
            nutrition_score=nutrition_score,
            stress_level=stress_level,
            recovery_rate=recovery_rate,
            mood_score=mood_score,
            anxiety_level=anxiety_level,
            focus_score=focus_score,
            motivation_level=motivation_level,
            confidence_score=confidence_score,
            immune_function=immune_function,
            hydration_level=hydration_level,
            injury_severity=injury_history['injury_severity'],
            recovery_status=injury_history['recovery_status'],
            social_activity=lifestyle_factors['social_activity'],
            family_support=lifestyle_factors['family_support'],
            peer_support=lifestyle_factors['peer_support']
        )
        
        return {
            'physical_metrics': {
                'height': height,
                'weight': weight,
                'bmi': bmi,
                'body_fat_percentage': body_fat_percentage,
                'muscle_mass': muscle_mass
            },
            'vital_signs': {
                'resting_heart_rate': resting_heart_rate,
                'blood_pressure_systolic': blood_pressure_systolic,
                'blood_pressure_diastolic': blood_pressure_diastolic,
                'oxygen_saturation': oxygen_saturation,
                'respiratory_rate': respiratory_rate
            },
            'activity_metrics': {
                'activity_level': activity_level,
                'exercise_frequency': exercise_frequency,
                'exercise_duration': exercise_duration,
                'exercise_intensity': exercise_intensity,
                'daily_steps': daily_steps,
                'sedentary_time': sedentary_time
            },
            'performance_metrics': {
                'strength_score': strength_score,
                'endurance_score': endurance_score,
                'flexibility_score': flexibility_score,
                'coordination_score': coordination_score,
                'agility_score': agility_score,
                'balance_score': balance_score,
                'power_score': power_score,
                'speed_score': speed_score
            },
            'health_indicators': {
                'sleep_quality': sleep_quality,
                'sleep_duration': sleep_duration,
                'nutrition_score': nutrition_score,
                'hydration_level': hydration_level,
                'stress_level': stress_level,
                'recovery_rate': recovery_rate,
                'immune_function': immune_function
            },
            'mental_health': {
                'mood_score': mood_score,
                'anxiety_level': anxiety_level,
                'focus_score': focus_score,
                'motivation_level': motivation_level,
                'confidence_score': confidence_score
            },
            'injury_history': injury_history,
            'lifestyle_factors': lifestyle_factors,
            'health_score': health_score
        }
    
    def _calculate_health_score(self, **metrics: float) -> float:
        """Calculate overall health score based on various metrics."""
        # Weights for different components
        weights = {
            # Physical activity (25%)
            'activity_level': 0.1,
            'exercise_frequency': 0.05,
            'exercise_duration': 0.05,
            'exercise_intensity': 0.05,
            
            # Performance (20%)
            'strength_score': 0.05,
            'endurance_score': 0.05,
            'flexibility_score': 0.05,
            'coordination_score': 0.05,
            
            # Health indicators (20%)
            'sleep_quality': 0.05,
            'nutrition_score': 0.05,
            'hydration_level': 0.05,
            'immune_function': 0.05,
            
            # Mental health (15%)
            'mood_score': 0.05,
            'anxiety_level': -0.05,  # Negative weight
            'focus_score': 0.05,
            'motivation_level': 0.05,
            'confidence_score': 0.05,
            
            # Recovery and injury (10%)
            'stress_level': -0.05,  # Negative weight
            'recovery_rate': 0.05,
            'injury_severity': -0.05,  # Negative weight
            'recovery_status': 0.05,
            
            # Social support (10%)
            'social_activity': 0.03,
            'family_support': 0.03,
            'peer_support': 0.04
        }
        
        # Calculate weighted sum
        weighted_sum = sum(metrics[metric] * weight 
                         for metric, weight in weights.items())
        
        # Normalize to 0-1 range
        health_score = max(0, min(1, weighted_sum))
        
        return health_score

def main():
    """Main function to generate health metrics data."""
    generator = HealthMetricsDataGenerator()
    generator.generate_student_data()
    print("Health metrics data generation completed successfully")

if __name__ == "__main__":
    main() 