import os
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from generate_injury_data import InjuryDataGenerator

class TestDataGenerator:
    def __init__(self):
        self.data_dir = Path('data/test_data')
        self.injury_generator = InjuryDataGenerator()
        self.movement_categories = {
            'basic': ['jumping', 'running', 'squatting'],
            'ball_sports': ['throwing', 'catching', 'kicking', 'dribbling', 'shooting', 'passing'],
            'swimming': ['freestyle', 'backstroke', 'breaststroke', 'butterfly'],
            'gymnastics': ['cartwheel', 'handstand', 'forward_roll', 'backward_roll', 'roundoff'],
            'dance': ['leap', 'turn', 'balance', 'pirouette', 'grand_jete', 'fouette',
                     'arabesque', 'attitude', 'developpe', 'pas_de_chat', 'saut_de_chat',
                     'tour_en_lair', 'chaines', 'pique_turn', 'penche'],
            'martial_arts': ['punch', 'kick', 'block', 'roundhouse_kick', 'front_kick',
                           'side_kick', 'hook_punch', 'uppercut', 'jab', 'elbow_strike',
                           'knee_strike', 'spinning_back_kick', 'axe_kick', 'crescent_kick',
                           'spinning_hook_kick'],
            'yoga': ['downward_dog', 'warrior_1', 'warrior_2', 'tree_pose', 'plank', 'bridge'],
            'climbing': ['crimp', 'sloper', 'pinch', 'dyno', 'flag', 'heel_hook'],
            'weightlifting': ['deadlift', 'bench_press', 'overhead_press', 'clean', 'snatch', 'front_squat'],
            'track_field': ['sprint_start', 'long_jump', 'high_jump', 'shot_put', 'discus', 'javelin'],
            'combat': ['takedown', 'grapple', 'submission', 'sparring', 'footwork', 'defense'],
            'cycling': ['pedaling', 'climbing', 'sprinting', 'cornering', 'descending', 'standing'],
            'rowing': ['catch', 'drive', 'finish', 'recovery', 'sweep', 'scull'],
            'sports': ['volleyball_spike', 'tennis_serve', 'golf_swing', 'baseball_swing',
                      'cricket_batting', 'hockey_slap_shot']
        }
        self.enhanced_metrics = {
            'form_quality': ['alignment', 'balance', 'coordination', 'timing', 'precision'],
            'power_generation': ['explosiveness', 'force_transfer', 'core_engagement', 'limb_synchronization'],
            'safety_metrics': ['joint_stability', 'muscle_activation', 'range_of_motion', 'impact_absorption'],
            'performance_metrics': ['speed', 'accuracy', 'endurance', 'consistency', 'recovery_rate'],
            'technical_metrics': ['technique_score', 'skill_level', 'movement_efficiency', 'error_rate']
        }

    def generate_test_data(self):
        """Generate test data for all movement types"""
        print("Starting test data generation...")
        
        # Create test data directory if it doesn't exist
        test_data_dir = os.path.join('data', 'test_data')
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Generate data for each category
        for category, movements in self.movement_categories.items():
            category_dir = os.path.join(test_data_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            print(f"\nGenerating data for {category} movements...")
            for movement in movements:
                movement_dir = os.path.join(category_dir, movement)
                os.makedirs(movement_dir, exist_ok=True)
                
                print(f"Generating samples for {movement}...")
                for i in range(1, 101):  # Changed from 51 to 101 to generate 100 samples
                    data = self._generate_movement_data(movement, category)
                    filename = os.path.join(movement_dir, f'sample_{i}.json')
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                
                print(f"Generated 100 samples for {movement}")
        
        print("\nTest data generation completed successfully!")

    def _generate_movement_data(self, movement_type: str, category: str) -> Dict:
        """Generate enhanced movement data with detailed metrics."""
        # Generate base data
        base_data = self.injury_generator.generate_data(movement_type)
        
        # Enhanced metrics
        enhanced_metrics = {
            'power_generation': {
                'explosiveness': random.uniform(0.5, 1.0),
                'force_transfer': random.uniform(0.5, 1.0),
                'efficiency': random.uniform(0.5, 1.0)
            },
            'technical_metrics': {
                'precision': random.uniform(0.5, 1.0),
                'consistency': random.uniform(0.5, 1.0),
                'fluidity': random.uniform(0.5, 1.0)
            },
            'biomechanical_metrics': {
                'joint_loading': random.uniform(0.5, 1.0),
                'muscle_activation': random.uniform(0.5, 1.0),
                'energy_efficiency': random.uniform(0.5, 1.0)
            }
        }
        
        # Combine all data
        enhanced_data = {
            'movement_type': movement_type,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'base_metrics': base_data,
            'enhanced_metrics': enhanced_metrics
        }
        
        return enhanced_data

def main():
    generator = TestDataGenerator()
    generator.generate_test_data()
    print("Test data generation completed successfully!")

if __name__ == "__main__":
    main() 