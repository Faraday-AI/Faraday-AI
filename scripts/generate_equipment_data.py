import os
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

class EquipmentDataGenerator:
    def __init__(self):
        self.activity_types = [
            'strength', 'endurance', 'flexibility', 'coordination',
            'speed', 'agility', 'balance', 'power',
            'game', 'drill', 'exercise', 'warmup'
        ]
        self.space_shapes = ['rectangular', 'square', 'circular', 'irregular']
        
    def generate_equipment_data(self, num_samples: int = 100) -> None:
        """Generate sample equipment optimization data."""
        data_dir = Path('data/equipment_data')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(num_samples):
            session_data = {
                'activity_type': random.choice(self.activity_types),
                'space_size': self._generate_space_size(),
                'space_shape': random.choice(self.space_shapes),
                'obstacles_count': self._generate_obstacles_count(),
                'clearance_height': self._generate_clearance_height(),
                'group_size': self._generate_group_size(),
                'age_range': self._generate_age_range(),
                'skill_level': self._generate_skill_level(),
                'activity_duration': self._generate_activity_duration(),
                'equipment_count': self._generate_equipment_count(),
                'equipment_quality': self._generate_equipment_quality(),
                'equipment_versatility': self._generate_equipment_versatility(),
                'setup_time': self._generate_setup_time(),
                'equipment_efficiency': self._calculate_equipment_efficiency()
            }
            
            # Save session data
            with open(data_dir / f'session_{i+1}.json', 'w') as f:
                json.dump(session_data, f, indent=4)
    
    def _generate_space_size(self) -> float:
        """Generate space size in square meters."""
        return random.uniform(50.0, 500.0)
    
    def _generate_obstacles_count(self) -> int:
        """Generate number of obstacles in the space."""
        return random.randint(0, 10)
    
    def _generate_clearance_height(self) -> float:
        """Generate clearance height in meters."""
        return random.uniform(2.0, 5.0)
    
    def _generate_group_size(self) -> int:
        """Generate group size."""
        return random.randint(5, 30)
    
    def _generate_age_range(self) -> float:
        """Generate normalized age range."""
        return random.uniform(0.0, 1.0)
    
    def _generate_skill_level(self) -> float:
        """Generate skill level score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_activity_duration(self) -> float:
        """Generate activity duration in minutes."""
        return random.uniform(15.0, 90.0)
    
    def _generate_equipment_count(self) -> int:
        """Generate equipment count."""
        return random.randint(1, 20)
    
    def _generate_equipment_quality(self) -> float:
        """Generate equipment quality score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_equipment_versatility(self) -> float:
        """Generate equipment versatility score."""
        return random.uniform(0.0, 1.0)
    
    def _generate_setup_time(self) -> float:
        """Generate setup time in minutes."""
        return random.uniform(2.0, 15.0)
    
    def _calculate_equipment_efficiency(self) -> float:
        """Calculate equipment efficiency based on various factors."""
        # Base efficiency
        base_efficiency = random.uniform(0.4, 0.8)
        
        # Space utilization factor
        space_factor = random.uniform(-0.2, 0.2)
        
        # Equipment factors
        equipment_factors = {
            'quality': random.uniform(-0.1, 0.1),
            'versatility': random.uniform(-0.1, 0.1),
            'count': random.uniform(-0.1, 0.1)
        }
        
        # Group size factor
        group_factor = random.uniform(-0.1, 0.1)
        
        # Calculate total efficiency
        total_efficiency = (
            base_efficiency +
            space_factor +
            sum(equipment_factors.values()) +
            group_factor
        )
        
        # Ensure efficiency is between 0 and 1
        return max(0.0, min(1.0, total_efficiency))

def main():
    """Main function to generate equipment data."""
    generator = EquipmentDataGenerator()
    generator.generate_equipment_data()
    print("Equipment data generation completed successfully.")

if __name__ == "__main__":
    main() 