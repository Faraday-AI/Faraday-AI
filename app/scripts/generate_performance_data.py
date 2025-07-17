import os
import json
import random
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

class PerformanceDataGenerator:
    def __init__(self):
        self.learning_styles = ['visual', 'auditory', 'kinesthetic', 'reading/writing']
        self.environment_factors = ['indoor', 'outdoor', 'gym', 'field']
        self.equipment_types = ['none', 'basic', 'advanced', 'specialized']
        
    def generate_student_data(self, num_students: int = 100) -> None:
        """Generate sample performance data for students."""
        data_dir = Path('data/performance_data')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(num_students):
            student_data = {
                'student_id': f'student_{i+1}',
                'previous_performance': random.uniform(0.3, 0.9),
                'attendance_rate': random.uniform(0.7, 1.0),
                'engagement_score': random.uniform(0.4, 0.95),
                'practice_frequency': random.randint(1, 7),  # days per week
                'skill_level': random.uniform(0.2, 0.8),
                'physical_condition': random.uniform(0.5, 1.0),
                'motivation_level': random.uniform(0.3, 0.9),
                'learning_style': random.choice(self.learning_styles),
                'environment_factors': random.choice(self.environment_factors),
                'equipment_usage': random.choice(self.equipment_types),
                'current_performance': self._calculate_current_performance()
            }
            
            # Add some realistic correlations
            student_data = self._add_correlations(student_data)
            
            # Save student data
            with open(data_dir / f'student_{i+1}.json', 'w') as f:
                json.dump(student_data, f, indent=4)
    
    def _calculate_current_performance(self) -> float:
        """Calculate current performance based on various factors."""
        # Base performance influenced by multiple factors
        base_performance = random.uniform(0.3, 0.9)
        
        # Add some noise
        noise = random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, base_performance + noise))
    
    def _add_correlations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add realistic correlations between features."""
        # Attendance affects performance
        data['current_performance'] *= (0.8 + 0.2 * data['attendance_rate'])
        
        # Practice frequency affects skill level
        data['skill_level'] *= (0.7 + 0.3 * (data['practice_frequency'] / 7))
        
        # Physical condition affects engagement
        data['engagement_score'] *= (0.8 + 0.2 * data['physical_condition'])
        
        # Motivation affects practice frequency
        data['practice_frequency'] = int(
            min(7, max(1, data['practice_frequency'] * (0.8 + 0.4 * data['motivation_level'])))
        )
        
        # Ensure all values are within valid ranges
        for key, value in data.items():
            if isinstance(value, float):
                data[key] = max(0.0, min(1.0, value))
            elif key == 'practice_frequency':
                data[key] = int(max(1, min(7, value)))
        
        return data

def main():
    """Main function to generate performance data."""
    generator = PerformanceDataGenerator()
    generator.generate_student_data()
    print("Performance data generation completed successfully.")

if __name__ == "__main__":
    main() 