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
    
    def _generate_safety_considerations(self, movement_type: str, 
                                      analysis: Dict[str, float]) -> List[str]:
        """Generate safety considerations based on movement type and analysis."""
        considerations = []
        
        # General safety considerations
        if analysis['form'] < 0.6:
            considerations.append("High risk of injury due to poor form")
        if analysis['stability'] < 0.6:
            considerations.append("High risk of falls or loss of balance")
        
        # Parkour-specific considerations
        if movement_type in ['precision_jump', 'kong_vault', 'dash_vault', 'lazy_vault', 'speed_vault', 'wall_run']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics to prevent impingement")
            if analysis['wrist'] < 0.7:
                considerations.append("Maintain proper wrist alignment to prevent sprains")
            if analysis['ankle'] < 0.7:
                considerations.append("Ensure proper ankle positioning to prevent sprains")
        
        # Acrobatics-specific considerations
        elif movement_type in ['handspring', 'aerial_cartwheel', 'side_flip', 'webster', 'gainer', 'barani']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder stability to prevent injury")
            if analysis['spine'] < 0.7:
                considerations.append("Maintain proper spinal alignment to prevent back injuries")
            if analysis['alignment'] < 0.7:
                considerations.append("Ensure proper body alignment during rotation")
        
        # Functional fitness-specific considerations
        elif movement_type in ['box_jump', 'wall_ball', 'rope_climb', 'sandbag_lift', 'kettlebell_swing', 'medicine_ball_throw']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics for overhead movements")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment during explosive movements")
            if analysis['knee'] < 0.7:
                considerations.append("Ensure proper knee tracking during jumps and lifts")
        
        # Advanced yoga-specific considerations
        elif movement_type in ['crow_pose', 'headstand', 'shoulderstand', 'wheel_pose', 'scorpion_pose', 'flying_pigeon']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder alignment to prevent impingement")
            if analysis['wrist'] < 0.7:
                considerations.append("Maintain proper wrist positioning to prevent strain")
            if analysis['spine'] < 0.7:
                considerations.append("Ensure proper spinal alignment to prevent injury")
        
        # Advanced climbing-specific considerations
        elif movement_type in ['toe_hook', 'heel_toe_cam', 'gaston', 'layback', 'stemming', 'mantle']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics to prevent impingement")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment to prevent tendonitis")
            if analysis['hip'] < 0.7:
                considerations.append("Ensure proper hip positioning to prevent strain")
        
        # Movement-specific considerations
        if movement_type == 'jumping':
            if analysis['power'] > 0.8:
                considerations.append("Consider reducing jump height to prevent joint stress")
            if analysis['alignment'] < 0.7:
                considerations.append("Ensure proper landing technique to prevent knee injuries")
        
        elif movement_type == 'running':
            if analysis['form'] < 0.7:
                considerations.append("Focus on proper running form to prevent overuse injuries")
            if analysis['stability'] < 0.7:
                considerations.append("Consider running on softer surfaces to reduce impact")
        
        elif movement_type == 'squatting':
            if analysis['knee'] < 0.7:
                considerations.append("Ensure knees track over toes to prevent knee injuries")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment to prevent lower back strain")
        
        elif movement_type in ['throwing', 'shooting']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics to prevent rotator cuff injuries")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment to prevent tennis elbow")
        
        elif movement_type in ['kicking', 'dribbling']:
            if analysis['knee'] < 0.7:
                considerations.append("Ensure proper knee alignment during kicking motion")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain hip stability to prevent groin injuries")
        
        elif movement_type == 'catching':
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder positioning to prevent impingement")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow flexion to prevent hyperextension")
        
        elif movement_type == 'passing':
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics for accurate passing")
            if analysis['wrist'] < 0.7:
                considerations.append("Maintain proper wrist alignment for ball control")
        
        # Add swimming-specific considerations
        if movement_type in ['freestyle', 'backstroke', 'breaststroke', 'butterfly']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder rotation to prevent swimmer's shoulder")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment to prevent lower back strain")
            if analysis['knee'] < 0.7:
                considerations.append("Ensure proper kick technique to prevent knee injuries")
        
        # Add gymnastics-specific considerations
        elif movement_type in ['cartwheel', 'handstand']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder stability to prevent shoulder injuries")
            if analysis['wrist'] < 0.7:
                considerations.append("Maintain proper wrist alignment to prevent wrist sprains")
            if analysis['alignment'] < 0.7:
                considerations.append("Ensure proper body alignment to prevent falls")
        
        # Add dance-specific considerations
        elif movement_type in ['leap', 'turn']:
            if analysis['knee'] < 0.7:
                considerations.append("Focus on proper knee alignment during jumps and turns")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment to prevent hip injuries")
            if analysis['stability'] < 0.7:
                considerations.append("Work on balance and stability to prevent falls")
        
        # Add martial arts-specific considerations
        elif movement_type in ['punch', 'block']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics to prevent rotator cuff injuries")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment to prevent hyperextension")
            if analysis['wrist'] < 0.7:
                considerations.append("Ensure proper wrist alignment to prevent sprains")
        
        # Add yoga-specific considerations
        if movement_type in ['downward_dog', 'plank']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder alignment to prevent impingement")
            if analysis['wrist'] < 0.7:
                considerations.append("Maintain proper wrist alignment to prevent strain")
            if analysis['alignment'] < 0.7:
                considerations.append("Ensure proper body alignment to prevent injury")
        
        elif movement_type in ['warrior_1', 'warrior_2']:
            if analysis['knee'] < 0.7:
                considerations.append("Ensure proper knee alignment to prevent strain")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment to prevent injury")
            if analysis['stability'] < 0.7:
                considerations.append("Focus on balance and stability")
        
        elif movement_type == 'tree_pose':
            if analysis['alignment'] < 0.7:
                considerations.append("Focus on maintaining proper alignment")
            if analysis['stability'] < 0.7:
                considerations.append("Work on balance and stability")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment")
        
        # Add climbing-specific considerations
        elif movement_type in ['crimp', 'sloper', 'pinch']:
            if analysis['wrist'] < 0.7:
                considerations.append("Focus on proper wrist positioning to prevent strain")
            if analysis['shoulder'] < 0.7:
                considerations.append("Ensure proper shoulder engagement to prevent impingement")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment to prevent tendonitis")
        
        elif movement_type in ['dyno', 'flag']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics during dynamic movements")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip control to prevent injury")
            if analysis['stability'] < 0.7:
                considerations.append("Work on body tension and control")
        
        elif movement_type == 'heel_hook':
            if analysis['hip'] < 0.7:
                considerations.append("Focus on proper hip positioning to prevent strain")
            if analysis['knee'] < 0.7:
                considerations.append("Maintain proper knee alignment to prevent injury")
            if analysis['ankle'] < 0.7:
                considerations.append("Ensure proper ankle positioning to prevent sprains")
        
        # Add weightlifting-specific considerations
        if movement_type in ['deadlift', 'clean', 'snatch']:
            if analysis['back'] < 0.7:
                considerations.append("Focus on maintaining proper back alignment to prevent injury")
            if analysis['hip'] < 0.7:
                considerations.append("Ensure proper hip hinge mechanics")
            if analysis['knee'] < 0.7:
                considerations.append("Maintain proper knee tracking")
        
        elif movement_type in ['bench_press', 'overhead_press']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder positioning to prevent impingement")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment")
            if analysis['wrist'] < 0.7:
                considerations.append("Ensure proper wrist positioning")
        
        # Add track and field-specific considerations
        elif movement_type in ['sprint_start', 'long_jump']:
            if analysis['hip'] < 0.7:
                considerations.append("Focus on proper hip positioning for power generation")
            if analysis['knee'] < 0.7:
                considerations.append("Maintain proper knee alignment during takeoff")
            if analysis['ankle'] < 0.7:
                considerations.append("Ensure proper ankle stability")
        
        elif movement_type in ['shot_put', 'discus', 'javelin']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics for throwing")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip rotation")
            if analysis['alignment'] < 0.7:
                considerations.append("Ensure proper body alignment during throw")
        
        # Add combat sports-specific considerations
        elif movement_type in ['takedown', 'grapple']:
            if analysis['back'] < 0.7:
                considerations.append("Focus on maintaining proper back alignment during takedowns")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip positioning for stability")
            if analysis['knee'] < 0.7:
                considerations.append("Ensure proper knee alignment to prevent injury")
        
        elif movement_type in ['sparring', 'footwork']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder positioning for defense")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip alignment for movement")
            if analysis['stability'] < 0.7:
                considerations.append("Work on balance and stability during movement")
        
        # Add cycling-specific considerations
        if movement_type in ['pedaling', 'climbing', 'sprinting']:
            if analysis['knee'] < 0.7:
                considerations.append("Focus on proper knee alignment to prevent overuse injuries")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip positioning to prevent strain")
            if analysis['alignment'] < 0.7:
                considerations.append("Ensure proper bike fit and body alignment")
        
        # Add rowing-specific considerations
        elif movement_type in ['catch', 'drive', 'finish']:
            if analysis['back'] < 0.7:
                considerations.append("Focus on maintaining proper back alignment to prevent injury")
            if analysis['shoulder'] < 0.7:
                considerations.append("Maintain proper shoulder mechanics to prevent impingement")
            if analysis['wrist'] < 0.7:
                considerations.append("Ensure proper wrist positioning to prevent strain")
        
        # Add overhead sports considerations
        elif movement_type in ['volleyball_spike', 'tennis_serve']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics to prevent rotator cuff injuries")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment to prevent tennis elbow")
            if analysis['wrist'] < 0.7:
                considerations.append("Ensure proper wrist positioning to prevent sprains")
        
        # Add rotational sports considerations
        elif movement_type in ['golf_swing', 'baseball_swing']:
            if analysis['back'] < 0.7:
                considerations.append("Focus on maintaining proper back alignment during rotation")
            if analysis['hip'] < 0.7:
                considerations.append("Maintain proper hip rotation mechanics")
            if analysis['shoulder'] < 0.7:
                considerations.append("Ensure proper shoulder mechanics during swing")
        
        # Add striking sports considerations
        elif movement_type in ['cricket_batting', 'hockey_slap_shot']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics for power generation")
            if analysis['wrist'] < 0.7:
                considerations.append("Maintain proper wrist alignment to prevent strain")
            if analysis['hip'] < 0.7:
                considerations.append("Ensure proper hip rotation for power transfer")
        
        # Add martial arts-specific considerations
        if movement_type in ['roundhouse_kick', 'front_kick', 'side_kick']:
            if analysis['hip'] < 0.7:
                considerations.append("Focus on proper hip rotation for power and safety")
            if analysis['knee'] < 0.7:
                considerations.append("Maintain proper knee alignment to prevent injury")
            if analysis['ankle'] < 0.7:
                considerations.append("Ensure proper ankle positioning for stability")
        
        elif movement_type in ['hook_punch', 'uppercut', 'jab']:
            if analysis['shoulder'] < 0.7:
                considerations.append("Focus on proper shoulder mechanics to prevent rotator cuff injuries")
            if analysis['elbow'] < 0.7:
                considerations.append("Maintain proper elbow alignment to prevent hyperextension")
            if analysis['wrist'] < 0.7:
                considerations.append("Ensure proper wrist alignment to prevent sprains")
        
        # Add dance-specific considerations
        elif movement_type in ['pirouette', 'grand_jete', 'fouette']:
            if analysis['alignment'] < 0.7:
                considerations.append("Focus on maintaining proper body alignment")
            if analysis['balance'] < 0.7:
                considerations.append("Work on balance and stability")
            if analysis['ankle'] < 0.7:
                considerations.append("Ensure proper ankle strength and alignment")
        
        return considerations

def main():
    """Main function to generate injury data."""
    generator = InjuryDataGenerator()
    generator.generate_data()
    print("Injury data generation completed successfully")

if __name__ == "__main__":
    main() 