import cv2
import mediapipe as mp
import numpy as np
import os
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PoseDetector:
    _instance = None
    _initialized = False
    _model_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PoseDetector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                # Set up mediapipe
                self.mp_pose = mp.solutions.pose
                self.mp_draw = mp.solutions.drawing_utils
                
                # Initialize pose detection with error handling
                try:
                    self.pose = self.mp_pose.Pose(
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5
                    )
                    self._initialized = True
                    logger.info("Pose detection initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize pose detection: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Error in PoseDetector initialization: {str(e)}")
                raise

    def detect_pose(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[dict]]:
        """
        Detect pose in the given frame
        Returns: Tuple of (processed frame, pose data)
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.pose.process(rgb_frame)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )
                
                # Extract pose data
                pose_data = {
                    'landmarks': [
                        {
                            'x': landmark.x,
                            'y': landmark.y,
                            'z': landmark.z,
                            'visibility': landmark.visibility
                        }
                        for landmark in results.pose_landmarks.landmark
                    ]
                }
                
                return frame, pose_data
            
            return frame, None
            
        except Exception as e:
            logger.error(f"Error in pose detection: {str(e)}")
            return frame, None

    def __del__(self):
        """Cleanup when the detector is destroyed"""
        try:
            if hasattr(self, 'pose'):
                self.pose.close()
        except Exception as e:
            logger.error(f"Error cleaning up pose detector: {str(e)}") 