import unittest
import numpy as np
import tensorflow as tf
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from app.services.physical_education.models.movement_analysis.movement_models import MovementModels

class TestMovementModels(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            "pose_estimation": {
                "model_path": "test_pose.tflite",
                "input_size": [256, 256],
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5
            },
            "movement_classification": {
                "model_path": "test_classifier.h5",
                "input_size": [224, 224],
                "classes": [
                    "walking",
                    "running",
                    "jumping"
                ]
            }
        }
        
        # Mock config file reading
        self.config_patcher = patch('builtins.open', mock_open(read_data=json.dumps(self.test_config)))
        self.mock_config_file = self.config_patcher.start()
        
        # Mock MediaPipe pose
        self.mock_pose = MagicMock()
        self.pose_patcher = patch('mediapipe.solutions.pose.Pose', return_value=self.mock_pose)
        self.mock_pose_class = self.pose_patcher.start()
        
        # Create test instance
        self.movement_models = MovementModels(config_path="test_config.json")

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        self.config_patcher.stop()
        self.pose_patcher.stop()

    def test_init_loads_config(self):
        """Test initialization loads config correctly."""
        self.assertEqual(self.movement_models.config, self.test_config)
        self.mock_config_file.assert_called_once_with("test_config.json", 'r')

    def test_movement_classes_property(self):
        """Test movement classes property returns correct classes."""
        expected_classes = ["walking", "running", "jumping"]
        self.assertEqual(self.movement_models.movement_classes, expected_classes)

    def test_get_input_size(self):
        """Test input size retrieval for different model types."""
        pose_size = self.movement_models.get_input_size("pose_estimation")
        classifier_size = self.movement_models.get_input_size("movement_classification")
        
        self.assertEqual(pose_size, [256, 256])
        self.assertEqual(classifier_size, [224, 224])

    @patch('tensorflow.keras.models.load_model')
    def test_load_movement_classifier(self, mock_load_model):
        """Test loading of movement classifier model."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        model = self.movement_models.load_movement_classifier()
        
        self.assertEqual(model, mock_model)
        mock_load_model.assert_called_once_with("test_classifier.h5")

    def test_create_movement_classifier(self):
        """Test creation of movement classifier model."""
        model = self.movement_models.create_movement_classifier()
        
        self.assertIsInstance(model, tf.keras.Model)
        self.assertEqual(model.input_shape[1:], (224, 224, 3))
        self.assertEqual(model.output_shape[1], 3)  # 3 classes

    @patch('tensorflow.keras.Model.save')
    def test_save_movement_classifier(self, mock_save):
        """Test saving of movement classifier model."""
        model = MagicMock()
        self.movement_models.save_movement_classifier(model)
        
        mock_save.assert_called_once_with("test_classifier.h5")

    def test_process_frame(self):
        """Test frame processing functionality."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        processed_frame = self.movement_models.process_frame(frame)
        
        self.assertEqual(processed_frame.shape, (224, 224, 3))
        self.assertTrue(np.all(processed_frame >= 0) and np.all(processed_frame <= 1))

    @patch('tensorflow.keras.Model.predict')
    def test_classify_movement(self, mock_predict):
        """Test movement classification."""
        mock_predict.return_value = np.array([[0.1, 0.8, 0.1]])  # High probability for "running"
        
        frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        result = self.movement_models.classify_movement(frame)
        
        self.assertEqual(result, "running")
        mock_predict.assert_called_once()

    @patch('mediapipe.solutions.pose.Pose')
    def test_analyze_movement_sequence(self, mock_pose):
        """Test movement sequence analysis."""
        mock_pose_instance = MagicMock()
        mock_pose.return_value.__enter__.return_value = mock_pose_instance
        
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(5)]
        result = self.movement_models.analyze_movement_sequence(frames)
        
        self.assertIsInstance(result, dict)
        self.assertIn("landmarks", result)
        self.assertIn("scores", result)

    def test_sequence_metrics_calculation(self):
        """Test calculation of sequence metrics."""
        test_sequence = {
            "landmarks": [
                {"x": 0.5, "y": 0.5, "z": 0.5} for _ in range(10)
            ],
            "scores": [0.8 for _ in range(10)]
        }
        
        metrics = self.movement_models.calculate_sequence_metrics(test_sequence)
        
        self.assertIn("stability", metrics)
        self.assertIn("consistency", metrics)
        self.assertIn("fluency", metrics)

    def test_sequence_buffer_management(self):
        """Test sequence buffer management."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Add frames to buffer
        for _ in range(15):
            self.movement_models.add_to_sequence_buffer(frame)
        
        # Buffer should maintain only last 10 frames
        self.assertEqual(len(self.movement_models.sequence_buffer), 10)

    def test_error_handling(self):
        """Test error handling in various operations."""
        # Test invalid frame
        with self.assertRaises(ValueError):
            self.movement_models.process_frame(None)
        
        # Test invalid config
        with self.assertRaises(ValueError):
            MovementModels(config_path="invalid_config.json")

    def test_performance_tracking(self):
        """Test performance tracking functionality."""
        start_time = datetime.now()
        
        # Perform some operations
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.movement_models.process_frame(frame)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.assertLess(duration, 1.0)  # Should complete in under 1 second

    def test_movement_score_calculation(self):
        """Test movement score calculation."""
        test_metrics = {
            "stability": 0.8,
            "consistency": 0.7,
            "fluency": 0.9
        }
        
        score = self.movement_models.calculate_movement_score(test_metrics)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_session_metrics(self):
        """Test session metrics tracking."""
        # Add some test data
        self.movement_models.add_session_metric("test_metric", 0.8)
        self.movement_models.add_session_metric("test_metric", 0.9)
        
        metrics = self.movement_models.get_session_metrics()
        
        self.assertIn("test_metric", metrics)
        self.assertEqual(len(metrics["test_metric"]), 2)

    def test_session_management(self):
        """Test session management functionality."""
        # Start new session
        self.movement_models.start_new_session()
        
        # Add some data
        self.movement_models.add_session_metric("test_metric", 0.8)
        
        # End session
        summary = self.movement_models.end_session()
        
        self.assertIn("test_metric", summary)
        self.assertIn("duration", summary)

    def test_performance_summary(self):
        """Test performance summary generation."""
        # Add test data
        self.movement_models.add_session_metric("test_metric", 0.8)
        self.movement_models.add_session_metric("test_metric", 0.9)
        
        summary = self.movement_models.get_performance_summary()
        
        self.assertIn("test_metric", summary)
        self.assertIn("average", summary["test_metric"])
        self.assertIn("max", summary["test_metric"])
        self.assertIn("min", summary["test_metric"])

    def test_error_handling_performance(self):
        """Test error handling performance under load."""
        start_time = datetime.now()
        
        # Try to process invalid frames
        for _ in range(100):
            try:
                self.movement_models.process_frame(None)
            except ValueError:
                pass
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.assertLess(duration, 2.0)  # Should handle errors quickly 