import os
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

class InjuryDataGenerator:
    def __init__(self):
        self.data_dir = Path('data/injury_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.movement_types = [
            # Basic movements
            'jumping', 'running', 'squatting',
            # Ball sports
            'throwing', 'catching', 'kicking',
            'dribbling', 'shooting', 'passing',
            # Swimming strokes
            'freestyle', 'backstroke', 'breaststroke',
            'butterfly',
            # Gymnastics
            'cartwheel', 'handstand', 'roundoff', 'backflip', 'frontflip', 'aerial',
            # Dance
            'leap', 'turn', 'pirouette', 'grand_jete', 'fouette', 'arabesque',
            # Martial Arts
            'punch', 'block', 'kick', 'roundhouse_kick', 'front_kick', 'side_kick',
            # Yoga poses
            'downward_dog', 'warrior_1', 'warrior_2',
            'tree_pose', 'plank', 'bridge',
            # Climbing movements
            'crimp', 'sloper', 'pinch',
            'dyno', 'flag', 'heel_hook',
            # Weightlifting
            'deadlift', 'bench_press', 'overhead_press',
            'clean', 'snatch', 'front_squat',
            # Track and Field
            'sprint_start', 'long_jump', 'high_jump',
            'shot_put', 'discus', 'javelin',
            # Combat Sports
            'takedown', 'grapple', 'submission',
            'sparring', 'footwork', 'defense',
            # Cycling
            'pedaling', 'climbing', 'sprinting',
            'cornering', 'descending', 'standing',
            # Rowing
            'catch', 'drive', 'finish',
            'recovery', 'sweep', 'scull',
            # Additional Sports
            'volleyball_spike', 'tennis_serve',
            'golf_swing', 'baseball_swing',
            'cricket_batting', 'hockey_slap_shot',
            # Parkour
            'precision_jump', 'kong_vault', 'dash_vault', 'lazy_vault', 'speed_vault', 'wall_run',
            # Acrobatics
            'handspring', 'aerial_cartwheel', 'side_flip', 'webster', 'gainer', 'barani',
            # Functional Fitness
            'box_jump', 'wall_ball', 'rope_climb', 'sandbag_lift', 'kettlebell_swing', 'medicine_ball_throw',
            # Martial Arts Advanced
            'spinning_back_kick', 'axe_kick', 'crescent_kick', 'spinning_hook_kick', 'flying_knee', 'elbow_strike',
            # Dance Advanced
            'attitude', 'developpe', 'pas_de_chat', 'saut_de_chat', 'tour_en_lair', 'chaines',
            # Yoga Advanced
            'crow_pose', 'headstand', 'shoulderstand', 'wheel_pose', 'scorpion_pose', 'flying_pigeon',
            # Climbing Advanced
            'toe_hook', 'heel_toe_cam', 'gaston', 'layback', 'stemming', 'mantle'
        ]
        
    def generate_data(self, movement_type: str, num_samples: int = 1) -> Dict:
        """Generate injury data for a specific movement type."""
        data = {
            'key_points': self._generate_key_points(movement_type),
            'angles': self._calculate_angles(self._generate_key_points(movement_type)),
            'analysis_scores': self._generate_analysis_scores(
                movement_type,
                self._generate_key_points(movement_type),
                self._calculate_angles(self._generate_key_points(movement_type))
            ),
            'recommendations': self._generate_recommendations(
                movement_type,
                self._generate_analysis_scores(
                    movement_type,
                    self._generate_key_points(movement_type),
                    self._calculate_angles(self._generate_key_points(movement_type))
                )
            ),
            'safety_considerations': self._generate_safety_considerations(
                movement_type,
                self._generate_analysis_scores(
                    movement_type,
                    self._generate_key_points(movement_type),
                    self._calculate_angles(self._generate_key_points(movement_type))
                )
            )
        }
        return data
    
    def _generate_key_points(self, movement_type: str) -> Dict[str, List[float]]:
        """Generate key points for a specific movement type."""
        if movement_type in ['precision_jump', 'kong_vault', 'dash_vault', 'lazy_vault', 'speed_vault', 'wall_run']:
            # Parkour movements
            return {
                'shoulders': [random.uniform(-0.2, 0.2), random.uniform(0.4, 0.8), random.uniform(-0.2, 0.2)],
                'elbows': [random.uniform(-0.3, 0.3), random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)],
                'wrists': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.6), random.uniform(-0.3, 0.3)],
                'hips': [random.uniform(-0.2, 0.2), random.uniform(0.3, 0.7), random.uniform(-0.2, 0.2)],
                'knees': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.6), random.uniform(-0.3, 0.3)],
                'ankles': [random.uniform(-0.2, 0.2), random.uniform(0.1, 0.5), random.uniform(-0.2, 0.2)]
            }
        elif movement_type in ['handspring', 'aerial_cartwheel', 'side_flip', 'webster', 'gainer', 'barani']:
            # Acrobatic movements
            return {
                'shoulders': [random.uniform(-0.3, 0.3), random.uniform(0.5, 0.9), random.uniform(-0.3, 0.3)],
                'elbows': [random.uniform(-0.4, 0.4), random.uniform(0.4, 0.8), random.uniform(-0.4, 0.4)],
                'wrists': [random.uniform(-0.3, 0.3), random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)],
                'hips': [random.uniform(-0.3, 0.3), random.uniform(0.4, 0.8), random.uniform(-0.3, 0.3)],
                'knees': [random.uniform(-0.4, 0.4), random.uniform(0.3, 0.7), random.uniform(-0.4, 0.4)],
                'ankles': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.6), random.uniform(-0.3, 0.3)]
            }
        elif movement_type in ['box_jump', 'wall_ball', 'rope_climb', 'sandbag_lift', 'kettlebell_swing', 'medicine_ball_throw']:
            # Functional fitness movements
            return {
                'shoulders': [random.uniform(-0.2, 0.2), random.uniform(0.4, 0.8), random.uniform(-0.2, 0.2)],
                'elbows': [random.uniform(-0.3, 0.3), random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)],
                'wrists': [random.uniform(-0.2, 0.2), random.uniform(0.2, 0.6), random.uniform(-0.2, 0.2)],
                'hips': [random.uniform(-0.2, 0.2), random.uniform(0.3, 0.7), random.uniform(-0.2, 0.2)],
                'knees': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.6), random.uniform(-0.3, 0.3)],
                'ankles': [random.uniform(-0.2, 0.2), random.uniform(0.1, 0.5), random.uniform(-0.2, 0.2)]
            }
        elif movement_type in ['crow_pose', 'headstand', 'shoulderstand', 'wheel_pose', 'scorpion_pose', 'flying_pigeon']:
            # Advanced yoga poses
            return {
                'shoulders': [random.uniform(-0.3, 0.3), random.uniform(0.5, 0.9), random.uniform(-0.3, 0.3)],
                'elbows': [random.uniform(-0.4, 0.4), random.uniform(0.4, 0.8), random.uniform(-0.4, 0.4)],
                'wrists': [random.uniform(-0.3, 0.3), random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)],
                'hips': [random.uniform(-0.3, 0.3), random.uniform(0.4, 0.8), random.uniform(-0.3, 0.3)],
                'knees': [random.uniform(-0.4, 0.4), random.uniform(0.3, 0.7), random.uniform(-0.4, 0.4)],
                'ankles': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.6), random.uniform(-0.3, 0.3)]
            }
        elif movement_type in ['toe_hook', 'heel_toe_cam', 'gaston', 'layback', 'stemming', 'mantle']:
            # Advanced climbing techniques
            return {
                'shoulders': [random.uniform(-0.3, 0.3), random.uniform(0.4, 0.8), random.uniform(-0.3, 0.3)],
                'elbows': [random.uniform(-0.4, 0.4), random.uniform(0.3, 0.7), random.uniform(-0.4, 0.4)],
                'wrists': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.6), random.uniform(-0.3, 0.3)],
                'hips': [random.uniform(-0.3, 0.3), random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)],
                'knees': [random.uniform(-0.4, 0.4), random.uniform(0.2, 0.6), random.uniform(-0.4, 0.4)],
                'ankles': [random.uniform(-0.3, 0.3), random.uniform(0.1, 0.5), random.uniform(-0.3, 0.3)]
            }
        else:
            # Default case for all other movements
            key_points = {
                'shoulders': [random.uniform(-0.2, 0.2), random.uniform(0.5, 0.7), random.uniform(-0.1, 0.1)],
                'elbows': [random.uniform(-0.3, 0.3), random.uniform(0.4, 0.6), random.uniform(-0.1, 0.1)],
                'wrists': [random.uniform(-0.4, 0.4), random.uniform(0.3, 0.5), random.uniform(-0.1, 0.1)],
                'hips': [random.uniform(-0.2, 0.2), random.uniform(0.3, 0.5), random.uniform(-0.1, 0.1)],
                'knees': [random.uniform(-0.3, 0.3), random.uniform(0.2, 0.4), random.uniform(-0.1, 0.1)],
                'ankles': [random.uniform(-0.4, 0.4), random.uniform(0.1, 0.3), random.uniform(-0.1, 0.1)]
            }
            return key_points
    
    def _calculate_angles(self, key_points: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate joint angles from key points."""
        angles = {}
        
        # Calculate knee angle
        if 'hips' in key_points and 'knees' in key_points and 'ankles' in key_points:
            hip = np.array(key_points['hips'])
            knee = np.array(key_points['knees'])
            ankle = np.array(key_points['ankles'])
            
            # Calculate vectors
            thigh = hip - knee
            shin = ankle - knee
            
            # Calculate angle
            angle = self._angle_between_vectors(thigh, shin)
            angles['knee'] = angle
        
        # Calculate hip angle
        if 'shoulders' in key_points and 'hips' in key_points and 'knees' in key_points:
            shoulder = np.array(key_points['shoulders'])
            hip = np.array(key_points['hips'])
            knee = np.array(key_points['knees'])
            
            # Calculate vectors
            trunk = shoulder - hip
            thigh = knee - hip
            
            # Calculate angle
            angle = self._angle_between_vectors(trunk, thigh)
            angles['hip'] = angle
        
        # Calculate shoulder angle
        if 'shoulders' in key_points and 'hips' in key_points:
            shoulder = np.array(key_points['shoulders'])
            hip = np.array(key_points['hips'])
            
            # Calculate angle relative to vertical
            vertical = np.array([0, 1, 0])
            trunk = shoulder - hip
            
            angle = self._angle_between_vectors(trunk, vertical)
            angles['shoulder'] = angle
        
        # Calculate elbow angle
        if 'shoulders' in key_points and 'elbows' in key_points and 'wrists' in key_points:
            shoulder = np.array(key_points['shoulders'])
            elbow = np.array(key_points['elbows'])
            wrist = np.array(key_points['wrists'])
            
            # Calculate vectors
            upper_arm = elbow - shoulder
            forearm = wrist - elbow
            
            # Calculate angle
            angle = self._angle_between_vectors(upper_arm, forearm)
            angles['elbow'] = angle
        
        return angles
    
    def _angle_between_vectors(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle between two vectors in degrees."""
        # Normalize vectors
        v1_u = v1 / np.linalg.norm(v1)
        v2_u = v2 / np.linalg.norm(v2)
        
        # Calculate angle
        angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
        return np.degrees(angle)
    
    def _generate_analysis_scores(self, movement_type: str, key_points: Dict[str, List[float]], 
                                angles: Dict[str, float]) -> Dict[str, float]:
        """Generate analysis scores for movement."""
        scores = {
            'alignment': random.uniform(0.6, 1.0),
            'balance': random.uniform(0.6, 1.0),
            'form': random.uniform(0.6, 1.0),
            'stability': random.uniform(0.6, 1.0),
            'coordination': random.uniform(0.6, 1.0),
            'precision': random.uniform(0.6, 1.0),
            'power': random.uniform(0.6, 1.0),
            'efficiency': random.uniform(0.6, 1.0),
            'safety': random.uniform(0.6, 1.0),
            'overall': random.uniform(0.6, 1.0),
            # Joint-specific scores
            'shoulder': random.uniform(0.6, 1.0),
            'elbow': random.uniform(0.6, 1.0),
            'wrist': random.uniform(0.6, 1.0),
            'hip': random.uniform(0.6, 1.0),
            'knee': random.uniform(0.6, 1.0),
            'ankle': random.uniform(0.6, 1.0),
            'back': random.uniform(0.6, 1.0),
            'neck': random.uniform(0.6, 1.0)
        }
        
        # Adjust scores based on movement type
        if movement_type in ['roundhouse_kick', 'front_kick', 'side_kick']:
            scores['hip'] *= 1.2
            scores['knee'] *= 1.2
            scores['ankle'] *= 1.2
            
        elif movement_type in ['hook_punch', 'uppercut', 'jab']:
            scores['shoulder'] *= 1.2
            scores['elbow'] *= 1.2
            scores['wrist'] *= 1.2
            
        elif movement_type in ['pirouette', 'grand_jete', 'fouette']:
            scores['balance'] *= 1.2
            scores['alignment'] *= 1.2
            scores['ankle'] *= 1.2
            
        # Ensure all scores are between 0 and 1
        for key in scores:
            scores[key] = min(max(scores[key], 0.0), 1.0)
            
        return scores
    
    def _generate_recommendations(self, movement_type: str, analysis: Dict[str, float]) -> Dict[str, str]:
        """Generate recommendations based on analysis scores."""
        recommendations = {}
        
        # Form recommendations
        if analysis['form'] < 0.7:
            recommendations['form'] = "Focus on maintaining proper joint angles during movement"
        else:
            recommendations['form'] = "Good form, continue practicing with current technique"
        
        # Alignment recommendations
        if analysis['alignment'] < 0.7:
            recommendations['alignment'] = "Work on maintaining symmetrical movement patterns"
        else:
            recommendations['alignment'] = "Good alignment, maintain current technique"
        
        # Stability recommendations
        if analysis['stability'] < 0.7:
            recommendations['stability'] = "Focus on maintaining proper posture and balance"
        else:
            recommendations['stability'] = "Good stability, continue with current technique"
        
        # Power recommendations
        if analysis['power'] < 0.7:
            recommendations['power'] = "Consider increasing intensity gradually"
        else:
            recommendations['power'] = "Good power output, maintain current intensity"
        
        return recommendations
    
    def _generate_safety_considerations(self, movement_type: str, analysis: Dict) -> List[str]:
        """Generate safety considerations based on movement type and analysis data."""
        considerations = []
        
        # General safety considerations
        if analysis.get('form', 0) < 0.7:
            considerations.append("Focus on maintaining proper form throughout the movement")
        if analysis.get('stability', 0) < 0.7:
            considerations.append("Work on improving stability and balance")
        
        # Movement-specific safety considerations
        if movement_type in ['jumping', 'running', 'squatting']:
            if analysis.get('knee', 0) < 0.7:
                considerations.append("Ensure proper knee alignment and tracking")
            if analysis.get('ankle', 0) < 0.7:
                considerations.append("Maintain proper ankle stability")
        
        elif movement_type in ['throwing', 'catching', 'kicking']:
            if analysis.get('shoulder', 0) < 0.7:
                considerations.append("Focus on proper shoulder mechanics")
            if analysis.get('elbow', 0) < 0.7:
                considerations.append("Maintain proper elbow alignment")
        
        elif movement_type in ['swimming', 'gymnastics']:
            if analysis.get('shoulder', 0) < 0.7:
                considerations.append("Ensure proper shoulder stability and rotation")
            if analysis.get('back', 0) < 0.7:
                considerations.append("Maintain proper spinal alignment")
        
        elif movement_type in ['dance', 'yoga']:
            if analysis.get('balance', 0) < 0.7:
                considerations.append("Focus on maintaining balance and control")
            if analysis.get('back', 0) < 0.7:
                considerations.append("Ensure proper spinal alignment")
        
        elif movement_type in ['martial_arts', 'combat']:
            if analysis.get('knee', 0) < 0.7:
                considerations.append("Maintain proper knee alignment during strikes")
            if analysis.get('back', 0) < 0.7:
                considerations.append("Keep spine neutral during movements")
        
        elif movement_type in ['climbing']:
            if analysis.get('shoulder', 0) < 0.7:
                considerations.append("Focus on proper shoulder mechanics during holds")
            if analysis.get('elbow', 0) < 0.7:
                considerations.append("Maintain proper elbow alignment")
        
        elif movement_type in ['weightlifting']:
            if analysis.get('back', 0) < 0.7:
                considerations.append("Maintain proper spinal alignment during lifts")
            if analysis.get('knee', 0) < 0.7:
                considerations.append("Ensure proper knee tracking")
        
        elif movement_type in ['track_field']:
            if analysis.get('ankle', 0) < 0.7:
                considerations.append("Focus on proper ankle stability")
            if analysis.get('knee', 0) < 0.7:
                considerations.append("Maintain proper knee alignment")
        
        elif movement_type in ['cycling']:
            if analysis.get('knee', 0) < 0.7:
                considerations.append("Ensure proper knee alignment during pedaling")
            if analysis.get('back', 0) < 0.7:
                considerations.append("Maintain proper spinal alignment")
        
        elif movement_type in ['rowing']:
            if analysis.get('back', 0) < 0.7:
                considerations.append("Focus on proper back alignment during stroke")
            if analysis.get('shoulder', 0) < 0.7:
                considerations.append("Maintain proper shoulder mechanics")
        
        elif movement_type in ['sports']:
            if analysis.get('knee', 0) < 0.7:
                considerations.append("Ensure proper knee alignment during movements")
            if analysis.get('ankle', 0) < 0.7:
                considerations.append("Maintain proper ankle stability")
        
        elif movement_type in ['parkour']:
            if analysis.get('ankle', 0) < 0.7:
                considerations.append("Focus on proper landing technique")
            if analysis.get('back', 0) < 0.7:
                considerations.append("Maintain proper spinal alignment during rolls")
        
        elif movement_type in ['acrobatics']:
            if analysis.get('back', 0) < 0.7:
                considerations.append("Ensure proper spinal alignment during flips")
            if analysis.get('shoulder', 0) < 0.7:
                considerations.append("Maintain proper shoulder stability")
        
        elif movement_type in ['functional_fitness']:
            if analysis.get('back', 0) < 0.7:
                considerations.append("Maintain proper spinal alignment during movements")
            if analysis.get('shoulder', 0) < 0.7:
                considerations.append("Focus on proper shoulder mechanics")
        
        return considerations

def main():
    """Main function to generate injury data."""
    generator = InjuryDataGenerator()
    generator.generate_data()
    print("Injury data generation completed successfully")

if __name__ == "__main__":
    main() 