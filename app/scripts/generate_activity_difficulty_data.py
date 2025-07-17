import os
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

class ActivityDifficultyDataGenerator:
    def __init__(self):
        self.activity_types = [
            'strength', 'endurance', 'flexibility', 'coordination',
            'speed', 'agility', 'balance', 'power'
        ]
        
    def generate_activity_data(self, num_samples: int = 100) -> None:
        """Generate sample activity difficulty data."""
        data_dir = Path('data/activity_difficulty')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(num_samples):
            activity_data = {
                'activity_type': random.choice(self.activity_types),
                'current_performance': self._generate_performance(),
                'skill_level': self._generate_skill_level(),
                'practice_frequency': self._generate_practice_frequency(),
                'physical_condition': self._generate_physical_condition(),
                'motivation_level': self._generate_motivation_level(),
                'space_available': self._generate_space_available(),
                'equipment_quality': self._generate_equipment_quality(),
                'group_size': self._generate_group_size(),
                'optimal_difficulty': self._calculate_optimal_difficulty()
            }
            
            # Save activity data
            with open(data_dir / f'activity_{i+1}.json', 'w') as f:
                json.dump(activity_data, f, indent=4)
    
    def _generate_performance(self) -> float:
        """Generate current performance score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_skill_level(self) -> float:
        """Generate skill level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_practice_frequency(self) -> float:
        """Generate practice frequency score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_physical_condition(self) -> float:
        """Generate physical condition score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_motivation_level(self) -> float:
        """Generate motivation level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_space_available(self) -> float:
        """Generate space available score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_equipment_quality(self) -> float:
        """Generate equipment quality score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_group_size(self) -> float:
        """Generate normalized group size."""
        return random.uniform(0.0, 1.0)
    
    def _calculate_optimal_difficulty(self) -> float:
        """Calculate optimal difficulty based on various factors."""
        # Base difficulty
        base_difficulty = random.uniform(0.3, 0.7)
        
        # Adjust based on performance and skill level
        performance_factor = random.uniform(-0.2, 0.2)
        skill_factor = random.uniform(-0.2, 0.2)
        
        # Adjust based on practice frequency and motivation
        practice_factor = random.uniform(-0.1, 0.1)
        motivation_factor = random.uniform(-0.1, 0.1)
        
        # Calculate total difficulty
        total_difficulty = (
            base_difficulty +
            performance_factor +
            skill_factor +
            practice_factor +
            motivation_factor
        )
        
        # Ensure difficulty is between 0 and 1
        return max(0.0, min(1.0, total_difficulty))

def main():
    """Main function to generate activity difficulty data."""
    generator = ActivityDifficultyDataGenerator()
    generator.generate_activity_data()
    print("Activity difficulty data generation completed successfully.")

if __name__ == "__main__":
    main() 