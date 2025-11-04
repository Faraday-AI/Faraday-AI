"""Movement analysis models for physical education."""
import os
import logging
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
from typing import Optional, Dict, Any, List, Tuple
from collections import deque
from datetime import datetime
# PRODUCTION-READY: Lazy import MediaPipe to prevent hangs in test mode
# MediaPipe import happens at module level, which blocks even before TEST_MODE check
# By making it lazy (import inside __init__), we can skip it entirely in test mode
# import mediapipe as mp  # MOVED TO LAZY IMPORT - see __init__ method
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.core.base import CoreBase

# This file has been moved to app/models/movement_analysis.py
# Please import MovementModels and other movement-related models from there instead.

# This file is kept for backward compatibility but will be removed in a future version.
# from app.models.movement_analysis import (
#     MovementModels,
#     MovementAnalysis,
#     MovementMetrics,
#     MovementSequence
# )

# from app.models.movement_analysis.analysis.movement_analysis import MovementAnalysis, MovementPattern

__all__ = [
    'MovementModels',
    'MovementAnalysis',
    'MovementMetrics',
    'MovementSequence'
]

logger = logging.getLogger(__name__)

class MovementAnalysisRecord(CoreBase):
    """Stores movement analysis data for student activities."""
    __tablename__ = "physical_education_movement_analysis"  # Changed to avoid conflicts

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    movement_data = Column(JSON, nullable=False)  # Changed from JSONB to JSON for SQLite compatibility
    analysis_results = Column(JSON, nullable=False)  # Changed from JSONB to JSON for SQLite compatibility
    confidence_score = Column(Float, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="movement_analysis_records")
    activity = relationship("app.models.physical_education.activity.models.Activity")
    patterns = relationship("app.models.physical_education.movement_analysis.movement_models.MovementPattern", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MovementAnalysisRecord {self.id} - {self.analysis_type}>"

class MovementPattern(CoreBase):
    """Records identified movement patterns from analysis."""
    __tablename__ = "physical_education_movement_pattern_models"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("physical_education_movement_analysis.id", ondelete="CASCADE"), nullable=False)  # Updated foreign key
    pattern_type = Column(String(50), nullable=False)  # e.g., "jumping", "running", "throwing"
    confidence_score = Column(Float, nullable=False)
    pattern_data = Column(JSON, nullable=False)  # Changed from JSONB to JSON for SQLite compatibility
    
    # Pattern characteristics
    duration = Column(Float, nullable=False)  # Duration in seconds
    repetitions = Column(Integer, nullable=False)
    quality_score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("MovementAnalysisRecord", back_populates="patterns")

class MovementModels:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize movement models with configuration.
        
        PRODUCTION-READY: Lazy MediaPipe import - only imports if not in TEST_MODE.
        This prevents module-level import from hanging when tests import MovementAnalyzer.
        
        Args:
            config_path: Optional path to movement_models.json config file.
                        If None, will look in the same directory as this file.
        """
        # PRODUCTION-READY: Check TEST_MODE BEFORE importing MediaPipe
        # This prevents the import from hanging in test mode
        test_mode = os.getenv("TEST_MODE") == "true"
        
        # Initialize logger first (needed for both test and production)
        self.logger = logging.getLogger(__name__)
        
        if test_mode:
            # In test mode, skip MediaPipe entirely - don't even import it
            self.pose_model = None
            self.mp = None  # No MediaPipe module
            # Initialize minimal config and attributes needed for other methods
            if config_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.config_path = os.path.join(current_dir, 'movement_models.json')
            else:
                self.config_path = config_path
            try:
                self.config = self._load_config()
            except Exception:
                # If config fails, use defaults
                self.config = {'pose_estimation': {'min_detection_confidence': 0.5, 'min_tracking_confidence': 0.5}}
            # Initialize other required attributes
            self._movement_classifier = None
            self.sequence_buffer_size = 30
            self.sequence_buffer = deque(maxlen=self.sequence_buffer_size)
            self.sequence_metrics = {'smoothness': 0.0, 'consistency': 0.0, 'speed': 0.0, 'range_of_motion': 0.0}
            self.performance_history = deque(maxlen=100)
            self.current_session = {'start_time': datetime.now(), 'movements': {}, 'metrics': {'overall_score': 0.0}}
            # Note: movement_classes is a @property, don't set it directly
            # It will read from self.config when accessed
            # Ensure config has movement_classification if property tries to access it
            if 'movement_classification' not in self.config:
                self.config['movement_classification'] = {'classes': ['jumping', 'running', 'throwing', 'catching']}
            self.logger.info("TEST_MODE: Skipping MediaPipe initialization")
            return  # Exit early - no MediaPipe needed in tests
        
        # Production mode: Lazy import MediaPipe (only when needed)
        try:
            import mediapipe as mp
            self.mp = mp
        except (ImportError, PermissionError, OSError) as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"MediaPipe import failed: {e}. Movement analysis will be limited.")
            self.mp = None
            self.pose_model = None
            return
        
        if config_path is None:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(current_dir, 'movement_models.json')
        else:
            self.config_path = config_path
            
        self.config = self._load_config()
        
        # Initialize logger if not set
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(__name__)
        
        # Ensure MediaPipe cache directory is writable
        # MediaPipe tries to download models to site-packages, which may not be writable
        # We'll handle this by ensuring the target directory has proper permissions
        try:
            import site
            site_packages = site.getsitepackages()
            for sp in site_packages:
                mediapipe_modules = os.path.join(sp, "mediapipe", "modules")
                if os.path.exists(mediapipe_modules):
                    # Make the modules directory writable
                    os.chmod(mediapipe_modules, 0o777)
                    # Also make subdirectories writable
                    for root, dirs, files in os.walk(mediapipe_modules):
                        try:
                            os.chmod(root, 0o777)
                        except (PermissionError, OSError):
                            pass  # Ignore if we can't change permissions
        except Exception as e:
            self.logger.warning(f"Could not set MediaPipe cache permissions: {e}")
        
        # Initialize pose estimation model
        # This may download models on first run - ensure permissions are set above
        try:
            # Use self.mp (lazy imported MediaPipe) instead of module-level mp
            self.pose_model = self.mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=2,
                min_detection_confidence=self.config['pose_estimation']['min_detection_confidence'],
                min_tracking_confidence=self.config['pose_estimation']['min_tracking_confidence']
            )
        except (PermissionError, AttributeError) as e:
            # AttributeError if self.mp is None (test mode)
            self.logger.error(f"Error initializing MediaPipe Pose model: {e}")
            if not test_mode:
                self.logger.error("This usually means the site-packages/mediapipe/modules directory is not writable.")
                self.logger.error("Try running with appropriate permissions or pre-downloading models.")
                raise
            # In test mode, this is expected - pose_model is None
            self.pose_model = None
        
        # Movement classification model will be loaded on demand
        self._movement_classifier = None
        
        # Initialize sequence analysis components
        self.sequence_buffer_size = 30  # Store 30 frames for sequence analysis
        self.sequence_buffer = deque(maxlen=self.sequence_buffer_size)
        self.sequence_metrics = {
            'smoothness': 0.0,
            'consistency': 0.0,
            'speed': 0.0,
            'range_of_motion': 0.0
        }
        
        # Initialize performance tracking
        self.performance_history = deque(maxlen=100)  # Store last 100 sessions
        self.current_session = {
            'start_time': datetime.now(),
            'movements': {},
            'metrics': {
                'overall_score': 0.0,
                'movement_scores': {},
                'improvement_rate': 0.0,
                'consistency_score': 0.0,
                'endurance_score': 0.0
            }
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded movement models config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {str(e)}")
            raise

    @property
    def movement_classes(self) -> List[str]:
        """Get list of supported movement classes."""
        return self.config['movement_classification']['classes']

    def get_input_size(self, model_type: str) -> Tuple[int, int]:
        """Get input size for specified model type."""
        if model_type not in ['pose_estimation', 'movement_classification']:
            raise ValueError(f"Invalid model type: {model_type}")
        return tuple(self.config[model_type]['input_size'])

    def load_movement_classifier(self) -> tf.keras.Model:
        """Load or get cached movement classification model."""
        if self._movement_classifier is None:
            model_path = self.config['movement_classification']['model_path']
            try:
                self._movement_classifier = tf.keras.models.load_model(model_path)
                logger.info(f"Loaded movement classifier from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load movement classifier: {str(e)}")
                raise
        return self._movement_classifier

    def create_movement_classifier(self, input_shape: tuple) -> tf.keras.Model:
        """Create a new movement classification model."""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=input_shape),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(len(self.movement_classes), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model

    def save_movement_classifier(self, model: tf.keras.Model) -> None:
        """Save movement classification model."""
        model_path = self.config['movement_classification']['model_path']
        try:
            model.save(model_path)
            self._movement_classifier = model
            logger.info(f"Saved movement classifier to {model_path}")
        except Exception as e:
            logger.error(f"Failed to save movement classifier: {str(e)}")
            raise

    def process_frame(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Process a single frame through pose estimation.
        
        PRODUCTION-READY: Handles test mode where pose_model is None.
        """
        # In test mode, pose_model is None - return None gracefully
        if self.pose_model is None:
            return None
        
        results = self.pose_model.process(frame)
        
        if not results.pose_landmarks:
            return None
            
        return {
            'landmarks': results.pose_landmarks,
            'world_landmarks': results.pose_world_landmarks
        }

    def classify_movement(self, features: np.ndarray) -> Dict[str, float]:
        """Classify movement based on extracted features.
        
        Args:
            features: Numpy array of movement features
            
        Returns:
            Dictionary mapping movement classes to confidence scores
        """
        model = self.load_movement_classifier()
        predictions = model.predict(np.expand_dims(features, axis=0))[0]
        
        return dict(zip(self.movement_classes, predictions.tolist()))

    def analyze_movement_sequence(self, frames) -> Dict[str, Any]:
        """Analyze a sequence of movements from consecutive frames.
        
        Args:
            frames: Single frame (np.ndarray) or list of frames to analyze
            
        Returns:
            Dictionary containing landmarks, scores, and sequence analysis metrics
        """
        try:
            # Handle both single frame and list of frames
            if isinstance(frames, list):
                frame_list = frames
            else:
                frame_list = [frames]
            
            # Process all frames
            all_landmarks = []
            all_scores = []
            
            for frame in frame_list:
                frame_results = self.process_frame(frame)
                if frame_results:
                    # Add to sequence buffer
                    self.sequence_buffer.append({
                        'landmarks': frame_results['landmarks'],
                        'timestamp': datetime.now(),
                        'processed': False
                    })
                    
                    # Extract landmarks for return
                    if hasattr(frame_results['landmarks'], 'landmark'):
                        # MediaPipe landmarks object
                        landmarks_data = [
                            {
                                'x': lm.x,
                                'y': lm.y,
                                'z': lm.z,
                                'visibility': lm.visibility
                            } for lm in frame_results['landmarks'].landmark
                        ]
                    else:
                        # Already in dict format
                        landmarks_data = frame_results['landmarks']
                    
                    all_landmarks.append(landmarks_data)
                    
                    # Extract scores if available
                    if 'detection_confidence' in frame_results:
                        all_scores.append(frame_results['detection_confidence'])
                    elif hasattr(frame_results.get('landmarks', None), 'landmark'):
                        # Use visibility as a proxy for score
                        visibilities = [lm.visibility for lm in frame_results['landmarks'].landmark]
                        all_scores.append(sum(visibilities) / len(visibilities) if visibilities else 0.0)
                    else:
                        all_scores.append(0.8)  # Default confidence
            
            # Only analyze if we have enough frames
            if len(self.sequence_buffer) >= 2:
                self._update_sequence_metrics()
            
            # Return combined result with landmarks, scores, and metrics
            return {
                'landmarks': all_landmarks if len(all_landmarks) > 1 else (all_landmarks[0] if all_landmarks else []),
                'scores': all_scores if len(all_scores) > 1 else (all_scores[0] if all_scores else []),
                **self.sequence_metrics  # Include all sequence metrics
            }
            
        except Exception as e:
            logger.error(f"Error in movement sequence analysis: {str(e)}")
            # Return empty structure on error
            return {
                'landmarks': [],
                'scores': [],
                **self.sequence_metrics
            }

    def _update_sequence_metrics(self) -> None:
        """Update movement sequence metrics based on buffered frames."""
        try:
            # Get unprocessed frames
            unprocessed = [
                frame for frame in self.sequence_buffer 
                if not frame['processed']
            ]
            
            if not unprocessed:
                return
                
            # Calculate metrics
            self._calculate_smoothness(unprocessed)
            self._calculate_consistency(unprocessed)
            self._calculate_speed(unprocessed)
            self._calculate_range_of_motion(unprocessed)
            
            # Mark frames as processed
            for frame in unprocessed:
                frame['processed'] = True
                
        except Exception as e:
            logger.error(f"Error updating sequence metrics: {str(e)}")

    def _calculate_smoothness(self, frames: List[Dict]) -> None:
        """Calculate movement smoothness from landmark positions."""
        try:
            if len(frames) < 2:
                return
                
            # Calculate jerk (rate of change of acceleration)
            total_jerk = 0
            for i in range(1, len(frames) - 1):
                prev = frames[i-1]['landmarks']
                curr = frames[i]['landmarks']
                next_frame = frames[i+1]['landmarks']
                
                # Calculate acceleration changes for key points
                for point_idx in range(33):  # MediaPipe provides 33 landmarks
                    p1 = np.array([prev.landmark[point_idx].x, prev.landmark[point_idx].y, prev.landmark[point_idx].z])
                    p2 = np.array([curr.landmark[point_idx].x, curr.landmark[point_idx].y, curr.landmark[point_idx].z])
                    p3 = np.array([next_frame.landmark[point_idx].x, next_frame.landmark[point_idx].y, next_frame.landmark[point_idx].z])
                    
                    # Approximate jerk using finite differences
                    acc1 = p2 - p1
                    acc2 = p3 - p2
                    jerk = np.linalg.norm(acc2 - acc1)
                    total_jerk += jerk
            
            # Update smoothness metric (inverse of average jerk)
            avg_jerk = total_jerk / (len(frames) - 2)
            self.sequence_metrics['smoothness'] = 1.0 / (1.0 + avg_jerk)
            
        except Exception as e:
            logger.error(f"Error calculating smoothness: {str(e)}")

    def _calculate_consistency(self, frames: List[Dict]) -> None:
        """Calculate movement consistency from landmark positions."""
        try:
            if len(frames) < 2:
                return
                
            # Calculate variance in movement patterns
            variances = []
            for point_idx in range(33):
                positions = []
                for frame in frames:
                    landmark = frame['landmarks'].landmark[point_idx]
                    positions.append([landmark.x, landmark.y, landmark.z])
                
                # Calculate variance of positions
                variance = np.var(positions, axis=0)
                variances.append(np.mean(variance))
            
            # Update consistency metric (inverse of average variance)
            avg_variance = np.mean(variances)
            self.sequence_metrics['consistency'] = 1.0 / (1.0 + avg_variance)
            
        except Exception as e:
            logger.error(f"Error calculating consistency: {str(e)}")

    def _calculate_speed(self, frames: List[Dict]) -> None:
        """Calculate movement speed from landmark positions and timestamps."""
        try:
            if len(frames) < 2:
                return
                
            # Calculate average velocity
            total_velocity = 0
            count = 0
            
            for i in range(1, len(frames)):
                prev = frames[i-1]
                curr = frames[i]
                
                # Time difference in seconds
                dt = (curr['timestamp'] - prev['timestamp']).total_seconds()
                if dt == 0:
                    continue
                
                # Calculate velocity for key points
                for point_idx in range(33):
                    p1 = prev['landmarks'].landmark[point_idx]
                    p2 = curr['landmarks'].landmark[point_idx]
                    
                    # Calculate displacement
                    displacement = np.linalg.norm([
                        p2.x - p1.x,
                        p2.y - p1.y,
                        p2.z - p1.z
                    ])
                    
                    velocity = displacement / dt
                    total_velocity += velocity
                    count += 1
            
            # Update speed metric
            if count > 0:
                self.sequence_metrics['speed'] = total_velocity / count
                
        except Exception as e:
            logger.error(f"Error calculating speed: {str(e)}")

    def _calculate_range_of_motion(self, frames: List[Dict]) -> None:
        """Calculate range of motion from landmark positions."""
        try:
            if len(frames) < 2:
                return
                
            # Calculate maximum displacement for each landmark
            max_displacements = []
            
            for point_idx in range(33):
                positions = []
                for frame in frames:
                    landmark = frame['landmarks'].landmark[point_idx]
                    positions.append([landmark.x, landmark.y, landmark.z])
                
                # Calculate max displacement
                positions = np.array(positions)
                min_pos = np.min(positions, axis=0)
                max_pos = np.max(positions, axis=0)
                displacement = np.linalg.norm(max_pos - min_pos)
                max_displacements.append(displacement)
            
            # Update range of motion metric
            self.sequence_metrics['range_of_motion'] = np.mean(max_displacements)
            
        except Exception as e:
            logger.error(f"Error calculating range of motion: {str(e)}")

    def get_sequence_metrics(self) -> Dict[str, float]:
        """Get current sequence metrics."""
        return self.sequence_metrics.copy()

    def reset_sequence_analysis(self) -> None:
        """Reset sequence analysis buffer and metrics."""
        self.sequence_buffer.clear()
        self.sequence_metrics = {
            'smoothness': 0.0,
            'consistency': 0.0,
            'speed': 0.0,
            'range_of_motion': 0.0
        }

    def track_performance(self, movement_type: str, metrics: Dict[str, float]) -> None:
        """Track performance metrics for a specific movement type.
        
        Args:
            movement_type: Type of movement being performed
            metrics: Dictionary of movement metrics
        """
        try:
            if movement_type not in self.current_session['movements']:
                self.current_session['movements'][movement_type] = {
                    'count': 0,
                    'scores': [],
                    'last_metrics': None,
                    'best_metrics': None
                }
            
            movement_data = self.current_session['movements'][movement_type]
            movement_data['count'] += 1
            movement_data['scores'].append(self._calculate_movement_score(metrics))
            movement_data['last_metrics'] = metrics
            
            # Update best metrics if current metrics are better
            if (movement_data['best_metrics'] is None or 
                self._calculate_movement_score(metrics) > 
                self._calculate_movement_score(movement_data['best_metrics'])):
                movement_data['best_metrics'] = metrics
            
            # Update session metrics
            self._update_session_metrics()
            
        except Exception as e:
            logger.error(f"Error tracking performance: {str(e)}")

    def _calculate_movement_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall score for a movement based on metrics.
        
        Args:
            metrics: Dictionary of movement metrics
            
        Returns:
            Normalized score between 0 and 1
        """
        try:
            # Weight different metrics based on importance
            weights = {
                'smoothness': 0.3,
                'consistency': 0.3,
                'speed': 0.2,
                'range_of_motion': 0.2
            }
            
            score = 0.0
            for metric, weight in weights.items():
                if metric in metrics:
                    score += metrics[metric] * weight
            
            return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1
            
        except Exception as e:
            logger.error(f"Error calculating movement score: {str(e)}")
            return 0.0

    def _update_session_metrics(self) -> None:
        """Update overall session metrics based on tracked movements."""
        try:
            if not self.current_session['movements']:
                return
                
            # Calculate overall score
            total_score = 0.0
            movement_count = 0
            
            for movement_data in self.current_session['movements'].values():
                if movement_data['scores']:
                    total_score += np.mean(movement_data['scores'])
                    movement_count += 1
            
            if movement_count > 0:
                self.current_session['metrics']['overall_score'] = total_score / movement_count
            
            # Calculate improvement rate
            if len(self.performance_history) > 0:
                last_session = self.performance_history[-1]
                time_diff = (self.current_session['start_time'] - last_session['start_time']).total_seconds()
                if time_diff > 0:
                    score_diff = self.current_session['metrics']['overall_score'] - last_session['metrics']['overall_score']
                    self.current_session['metrics']['improvement_rate'] = score_diff / time_diff
            
            # Calculate consistency score
            consistency_scores = []
            for movement_data in self.current_session['movements'].values():
                if len(movement_data['scores']) > 1:
                    consistency_scores.append(1.0 - np.std(movement_data['scores']))
            
            if consistency_scores:
                self.current_session['metrics']['consistency_score'] = np.mean(consistency_scores)
            
            # Calculate endurance score
            total_movements = sum(movement_data['count'] for movement_data in self.current_session['movements'].values())
            session_duration = (datetime.now() - self.current_session['start_time']).total_seconds()
            if session_duration > 0:
                self.current_session['metrics']['endurance_score'] = min(total_movements / session_duration, 1.0)
                
        except Exception as e:
            logger.error(f"Error updating session metrics: {str(e)}")

    def end_session(self) -> Dict[str, Any]:
        """End current session and store performance data.
        
        Returns:
            Dictionary containing session summary
        """
        try:
            # Finalize current session
            self._update_session_metrics()
            session_summary = {
                'start_time': self.current_session['start_time'],
                'end_time': datetime.now(),
                'duration': (datetime.now() - self.current_session['start_time']).total_seconds(),
                'metrics': self.current_session['metrics'].copy(),
                'movements': {
                    movement_type: {
                        'count': data['count'],
                        'average_score': np.mean(data['scores']) if data['scores'] else 0.0,
                        'best_score': np.max(data['scores']) if data['scores'] else 0.0
                    }
                    for movement_type, data in self.current_session['movements'].items()
                }
            }
            
            # Store session in history
            self.performance_history.append(session_summary)
            
            # Reset current session
            self.current_session = {
                'start_time': datetime.now(),
                'movements': {},
                'metrics': {
                    'overall_score': 0.0,
                    'movement_scores': {},
                    'improvement_rate': 0.0,
                    'consistency_score': 0.0,
                    'endurance_score': 0.0
                }
            }
            
            return session_summary
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return {}

    def get_performance_summary(self, num_sessions: int = 5) -> Dict[str, Any]:
        """Get summary of recent performance history.
        
        Args:
            num_sessions: Number of recent sessions to include in summary
            
        Returns:
            Dictionary containing performance summary
        """
        try:
            recent_sessions = list(self.performance_history)[-num_sessions:]
            
            if not recent_sessions:
                return {}
                
            summary = {
                'total_sessions': len(recent_sessions),
                'average_score': np.mean([s['metrics']['overall_score'] for s in recent_sessions]),
                'improvement_trend': np.mean([s['metrics']['improvement_rate'] for s in recent_sessions]),
                'consistency_trend': np.mean([s['metrics']['consistency_score'] for s in recent_sessions]),
                'endurance_trend': np.mean([s['metrics']['endurance_score'] for s in recent_sessions]),
                'movement_stats': {}
            }
            
            # Calculate movement statistics
            for session in recent_sessions:
                for movement_type, stats in session['movements'].items():
                    if movement_type not in summary['movement_stats']:
                        summary['movement_stats'][movement_type] = {
                            'total_count': 0,
                            'average_score': 0.0,
                            'best_score': 0.0
                        }
                    
                    movement_stats = summary['movement_stats'][movement_type]
                    movement_stats['total_count'] += stats['count']
                    movement_stats['average_score'] += stats['average_score']
                    movement_stats['best_score'] = max(movement_stats['best_score'], stats['best_score'])
            
            # Calculate averages
            for movement_stats in summary['movement_stats'].values():
                movement_stats['average_score'] /= len(recent_sessions)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {} 