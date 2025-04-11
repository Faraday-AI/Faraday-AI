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
            'basic': [
                'jumping', 'running', 'squatting', 'lunging', 'pushing', 'pulling',
                'crawling', 'rolling', 'balancing', 'twisting', 'bending', 'reaching',
                'stepping', 'hopping', 'skipping', 'galloping', 'sliding', 'leaping',
                'walking', 'marching', 'jogging', 'shuffling', 'backpedaling', 'side_stepping',
                'crouching', 'kneeling', 'sitting', 'standing', 'turning', 'pivoting',
                'swinging', 'rocking', 'bouncing', 'dodging', 'weaving', 'jumping_jack'
            ],
            'ball_sports': [
                'throwing', 'catching', 'kicking', 'dribbling', 'shooting', 'passing',
                'volleyball_serve', 'basketball_layup', 'soccer_header', 'baseball_pitch',
                'tennis_forehand', 'golf_drive'
            ],
            'swimming': [
                'freestyle', 'backstroke', 'breaststroke', 'butterfly', 'sidestroke',
                'elementary_backstroke', 'treading_water', 'diving'
            ],
            'gymnastics': [
                'cartwheel', 'handstand', 'forward_roll', 'backward_roll', 'roundoff',
                'back_handspring', 'front_handspring', 'aerial', 'back_tuck', 'front_tuck',
                'back_walkover', 'front_walkover'
            ],
            'dance': [
                'leap', 'turn', 'balance', 'pirouette', 'grand_jete', 'fouette',
                'arabesque', 'attitude', 'developpe', 'pas_de_chat', 'saut_de_chat',
                'tour_en_lair', 'chaines', 'pique_turn', 'penche', 'jete', 'sissonne',
                'entrechat', 'cabriole', 'echappe', 'glissade'
            ],
            'martial_arts': [
                'punch', 'kick', 'block', 'roundhouse_kick', 'front_kick', 'side_kick',
                'hook_punch', 'uppercut', 'jab', 'elbow_strike', 'knee_strike',
                'spinning_back_kick', 'axe_kick', 'crescent_kick', 'spinning_hook_kick',
                'sweep', 'takedown', 'throw', 'joint_lock', 'choke', 'defense_roll'
            ],
            'yoga': [
                'downward_dog', 'warrior_1', 'warrior_2', 'tree_pose', 'plank', 'bridge',
                'crow_pose', 'headstand', 'shoulderstand', 'wheel', 'pigeon', 'camel',
                'cobra', 'childs_pose', 'lotus'
            ],
            'climbing': [
                'crimp', 'sloper', 'pinch', 'dyno', 'flag', 'heel_hook', 'toe_hook',
                'heel_toe_cam', 'drop_knee', 'back_step', 'gaston', 'undercling', 'mantle'
            ],
            'weightlifting': [
                'deadlift', 'bench_press', 'overhead_press', 'clean', 'snatch',
                'front_squat', 'back_squat', 'split_jerk', 'power_clean', 'power_snatch',
                'push_press', 'good_morning', 'bent_over_row',
                # Squat variations
                'zercher_squat', 'hack_squat', 'bulgarian_split_squat', 'paused_squat',
                'box_squat', 'safety_bar_squat', 'jefferson_squat', 'belt_squat',
                # Deadlift variations
                'sumo_deadlift', 'deficit_deadlift', 'block_pull', 'rack_pull',
                # Bench press variations
                'incline_bench', 'decline_bench', 'close_grip_bench', 'floor_press',
                'board_press', 'pin_press', 'spoto_press',
                # Press variations
                'z_press', 'seated_press', 'bottoms_up_press', 'log_press', 'axle_press',
                # Olympic lift variations
                'clean_and_jerk', 'power_clean_and_jerk', 'hang_clean', 'block_clean',
                'clean_pull', 'snatch_pull', 'hang_snatch', 'block_snatch',
                'power_snatch_and_jerk', 'squat_snatch', 'split_snatch',
                # Accessory movements
                'sots_press', 'overhead_squat', 'front_rack_lunge', 'back_rack_lunge',
                'zercher_lunge', 'safety_squat_lunge', 'split_jerk', 'push_jerk',
                'power_jerk', 'squat_jerk'
            ],
            'track_field': [
                'sprint_start', 'long_jump', 'high_jump', 'shot_put', 'discus',
                'javelin', 'hurdles', 'pole_vault', 'triple_jump', 'hammer_throw',
                'steeplechase'
            ],
            'combat': [
                'takedown', 'grapple', 'submission', 'sparring', 'footwork', 'defense',
                'clinch', 'ground_and_pound', 'guard_pass', 'sweep', 'escape'
            ],
            'cycling': [
                'pedaling', 'climbing', 'sprinting', 'cornering', 'descending',
                'standing', 'track_stand', 'bunny_hop', 'wheelie', 'manual', 'enduro',
                'downhill'
            ],
            'rowing': [
                'catch', 'drive', 'finish', 'recovery', 'sweep', 'scull', 'power_ten',
                'high_ten', 'sprint', 'steady_state', 'race_pace'
            ],
            'sports': [
                'volleyball_spike', 'tennis_serve', 'golf_swing', 'baseball_swing',
                'cricket_batting', 'hockey_slap_shot', 'basketball_dunk', 'soccer_volley',
                'rugby_tackle', 'badminton_smash', 'table_tennis_serve',
                # Volleyball movements
                'volleyball_block', 'volleyball_dig', 'volleyball_set', 'volleyball_receive',
                'volleyball_attack', 'volleyball_serve_receive',
                # Tennis movements
                'tennis_backhand', 'tennis_volley', 'tennis_smash', 'tennis_slice',
                'tennis_drop_shot', 'tennis_lob',
                # Golf movements
                'golf_chip', 'golf_pitch', 'golf_putt', 'golf_bunker_shot',
                'golf_flop_shot', 'golf_punch_shot',
                # Baseball movements
                'baseball_catch', 'baseball_throw', 'baseball_slide', 'baseball_tag',
                'baseball_bunt', 'baseball_steal',
                # Cricket movements
                'cricket_bowling', 'cricket_fielding', 'cricket_wicket_keeping',
                'cricket_sweep_shot', 'cricket_pull_shot', 'cricket_cut_shot',
                # Hockey movements
                'hockey_wrist_shot', 'hockey_backhand', 'hockey_snap_shot',
                'hockey_slap_pass', 'hockey_saucer_pass', 'hockey_deke',
                # Basketball movements
                'basketball_jump_shot', 'basketball_hook_shot', 'basketball_crossover',
                'basketball_layup', 'basketball_rebound', 'basketball_block',
                # Soccer movements
                'soccer_throw_in', 'soccer_corner_kick', 'soccer_free_kick',
                'soccer_penalty_kick', 'soccer_tackle', 'soccer_header',
                # Rugby movements
                'rugby_scrum', 'rugby_lineout', 'rugby_maul', 'rugby_ruck',
                'rugby_grubber_kick', 'rugby_garryowen',
                # Badminton movements
                'badminton_clear', 'badminton_drop', 'badminton_drive',
                'badminton_smash', 'badminton_net_shot', 'badminton_lift',
                # Table Tennis movements
                'table_tennis_forehand', 'table_tennis_backhand', 'table_tennis_chop',
                'table_tennis_loop', 'table_tennis_flick', 'table_tennis_push'
            ],
            'parkour': [
                'precision_jump', 'kong_vault', 'dash_vault', 'lazy_vault', 'speed_vault',
                'wall_run', 'cat_leap', 'tic_tac', 'underbar', 'roll'
            ],
            'acrobatics': [
                'handspring', 'aerial_cartwheel', 'backflip', 'frontflip', 'sideflip',
                'butterfly_twist', 'webster', 'gainer', 'full_twist', 'double_full'
            ],
            'functional_fitness': [
                'box_jump', 'wall_ball', 'kettlebell_swing', 'burpee', 'muscle_up',
                'toes_to_bar', 'handstand_pushup', 'pistol_squat', 'rope_climb',
                'sandbag_clean',
                # New functional fitness movements
                'double_unders', 'box_step_up', 'wall_walk', 'devils_press',
                'sandbag_over_shoulder', 'sandbag_shoulder', 'sandbag_squat',
                'sandbag_deadlift', 'sandbag_clean_and_press', 'sandbag_snatch',
                'sandbag_lunge', 'sandbag_carry', 'sandbag_shoulder_to_overhead',
                'sandbag_front_rack_lunge', 'sandbag_zercher_squat', 'sandbag_shoulder_to_shoulder',
                'sandbag_shoulder_to_ground', 'sandbag_shoulder_to_shoulder_press',
                'sandbag_shoulder_to_shoulder_squat', 'sandbag_shoulder_to_shoulder_lunge',
                'sandbag_shoulder_to_shoulder_walk', 'sandbag_shoulder_to_shoulder_carry',
                'sandbag_shoulder_to_shoulder_clean', 'sandbag_shoulder_to_shoulder_snatch',
                'sandbag_shoulder_to_shoulder_jerk', 'sandbag_shoulder_to_shoulder_thruster',
                'sandbag_shoulder_to_shoulder_press_out', 'sandbag_shoulder_to_shoulder_squat_out',
                'sandbag_shoulder_to_shoulder_lunge_out', 'sandbag_shoulder_to_shoulder_walk_out',
                'sandbag_shoulder_to_shoulder_carry_out', 'sandbag_shoulder_to_shoulder_clean_out',
                'sandbag_shoulder_to_shoulder_snatch_out', 'sandbag_shoulder_to_shoulder_jerk_out',
                'sandbag_shoulder_to_shoulder_thruster_out', 'sandbag_shoulder_to_shoulder_press_out_out'
            ]
        }
        self.enhanced_metrics = {
            'form_quality': ['alignment', 'balance', 'coordination', 'timing', 'precision',
                           'symmetry', 'posture', 'technique', 'control', 'fluidity'],
            'power_generation': ['explosiveness', 'force_transfer', 'core_engagement', 'limb_synchronization',
                               'acceleration', 'deceleration', 'power_output', 'energy_efficiency',
                               'reaction_time', 'impulse'],
            'safety_metrics': ['joint_stability', 'muscle_activation', 'range_of_motion', 'impact_absorption',
                             'spinal_alignment', 'joint_loading', 'muscle_balance', 'injury_risk',
                             'recovery_rate', 'fatigue_level'],
            'performance_metrics': ['speed', 'accuracy', 'endurance', 'consistency', 'recovery_rate',
                                  'agility', 'flexibility', 'strength', 'power', 'stamina'],
            'technical_metrics': ['technique_score', 'skill_level', 'movement_efficiency', 'error_rate',
                                'complexity', 'adaptability', 'precision', 'control', 'rhythm',
                                'timing']
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
        
        # Enhanced metrics with more detailed parameters
        enhanced_metrics = {
            'power_generation': {
                'explosiveness': random.uniform(0.4, 1.0),
                'force_transfer': random.uniform(0.4, 1.0),
                'efficiency': random.uniform(0.4, 1.0),
                'acceleration': random.uniform(0.4, 1.0),
                'deceleration': random.uniform(0.4, 1.0),
                'power_output': random.uniform(0.4, 1.0),
                'energy_efficiency': random.uniform(0.4, 1.0),
                'reaction_time': random.uniform(0.4, 1.0),
                'impulse': random.uniform(0.4, 1.0)
            },
            'technical_metrics': {
                'precision': random.uniform(0.4, 1.0),
                'consistency': random.uniform(0.4, 1.0),
                'fluidity': random.uniform(0.4, 1.0),
                'complexity': random.uniform(0.4, 1.0),
                'adaptability': random.uniform(0.4, 1.0),
                'control': random.uniform(0.4, 1.0),
                'rhythm': random.uniform(0.4, 1.0),
                'timing': random.uniform(0.4, 1.0)
            },
            'biomechanical_metrics': {
                'joint_loading': random.uniform(0.4, 1.0),
                'muscle_activation': random.uniform(0.4, 1.0),
                'energy_efficiency': random.uniform(0.4, 1.0),
                'spinal_alignment': random.uniform(0.4, 1.0),
                'muscle_balance': random.uniform(0.4, 1.0),
                'injury_risk': random.uniform(0.4, 1.0),
                'recovery_rate': random.uniform(0.4, 1.0),
                'fatigue_level': random.uniform(0.4, 1.0)
            },
            'performance_metrics': {
                'speed': random.uniform(0.4, 1.0),
                'accuracy': random.uniform(0.4, 1.0),
                'endurance': random.uniform(0.4, 1.0),
                'consistency': random.uniform(0.4, 1.0),
                'recovery_rate': random.uniform(0.4, 1.0),
                'agility': random.uniform(0.4, 1.0),
                'flexibility': random.uniform(0.4, 1.0),
                'strength': random.uniform(0.4, 1.0),
                'power': random.uniform(0.4, 1.0),
                'stamina': random.uniform(0.4, 1.0)
            }
        }
        
        # Add movement-specific parameters
        movement_params = {
            'difficulty_level': random.uniform(0.1, 1.0),
            'skill_requirement': random.uniform(0.1, 1.0),
            'physical_demand': random.uniform(0.1, 1.0),
            'technical_complexity': random.uniform(0.1, 1.0),
            'risk_factor': random.uniform(0.1, 1.0),
            'learning_curve': random.uniform(0.1, 1.0)
        }
        
        # Combine all data
        enhanced_data = {
            'movement_type': movement_type,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'base_metrics': base_data,
            'enhanced_metrics': enhanced_metrics,
            'movement_parameters': movement_params
        }
        
        return enhanced_data

def main():
    generator = TestDataGenerator()
    generator.generate_test_data()
    print("Test data generation completed successfully!")

if __name__ == "__main__":
    main() 