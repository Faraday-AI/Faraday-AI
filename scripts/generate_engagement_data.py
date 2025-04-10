import os
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

class EngagementDataGenerator:
    def __init__(self):
        self.activity_types = [
            'strength', 'endurance', 'flexibility', 'coordination',
            'speed', 'agility', 'balance', 'power',
            'game', 'drill', 'exercise', 'warmup'
        ]
        
    def generate_engagement_data(self, num_samples: int = 100) -> None:
        """Generate sample engagement data."""
        data_dir = Path('data/engagement_data')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(num_samples):
            session_data = {
                'activity_type': random.choice(self.activity_types),
                'skill_level': self._generate_skill_level(),
                'previous_engagement': self._generate_previous_engagement(),
                'motivation_level': self._generate_motivation_level(),
                'fatigue_level': self._generate_fatigue_level(),
                'activity_difficulty': self._generate_activity_difficulty(),
                'activity_duration': self._generate_activity_duration(),
                'group_size': self._generate_group_size(),
                'interaction_frequency': self._generate_interaction_frequency(),
                'space_quality': self._generate_space_quality(),
                'equipment_quality': self._generate_equipment_quality(),
                'noise_level': self._generate_noise_level(),
                'temperature': self._generate_temperature(),
                'engagement_score': self._calculate_engagement_score()
            }
            
            # Save session data
            with open(data_dir / f'session_{i+1}.json', 'w') as f:
                json.dump(session_data, f, indent=4)
    
    def _generate_skill_level(self) -> float:
        """Generate skill level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_previous_engagement(self) -> float:
        """Generate previous engagement score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_motivation_level(self) -> float:
        """Generate motivation level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_fatigue_level(self) -> float:
        """Generate fatigue level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_activity_difficulty(self) -> float:
        """Generate activity difficulty score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_activity_duration(self) -> float:
        """Generate activity duration in minutes."""
        return random.uniform(5.0, 60.0)
    
    def _generate_group_size(self) -> float:
        """Generate normalized group size."""
        return random.uniform(0.0, 1.0)
    
    def _generate_interaction_frequency(self) -> float:
        """Generate interaction frequency score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_space_quality(self) -> float:
        """Generate space quality score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_equipment_quality(self) -> float:
        """Generate equipment quality score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_noise_level(self) -> float:
        """Generate noise level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_temperature(self) -> float:
        """Generate temperature in Celsius."""
        return random.uniform(15.0, 30.0)
    
    def _calculate_engagement_score(self) -> float:
        """Calculate engagement score based on various factors."""
        # Base engagement
        base_engagement = random.uniform(0.3, 0.7)
        
        # Activity type factors
        activity_factors = {
            'game': 0.2,
            'drill': 0.1,
            'exercise': 0.0,
            'warmup': -0.1
        }
        
        # Adjust based on skill level and motivation
        skill_factor = random.uniform(-0.2, 0.2)
        motivation_factor = random.uniform(-0.2, 0.2)
        
        # Adjust based on environmental factors
        space_factor = random.uniform(-0.1, 0.1)
        equipment_factor = random.uniform(-0.1, 0.1)
        noise_factor = random.uniform(-0.1, 0.1)
        temperature_factor = random.uniform(-0.1, 0.1)
        
        # Calculate total engagement
        total_engagement = (
            base_engagement +
            skill_factor +
            motivation_factor +
            space_factor +
            equipment_factor +
            noise_factor +
            temperature_factor
        )
        
        # Ensure engagement is between 0 and 1
        return max(0.0, min(1.0, total_engagement))

def main():
    """Main function to generate engagement data."""
    generator = EngagementDataGenerator()
    generator.generate_engagement_data()
    print("Engagement data generation completed successfully.")

if __name__ == "__main__":
    main() 