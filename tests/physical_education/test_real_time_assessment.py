import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import numpy as np
from app.services.physical_education.services.assessment_system import AssessmentSystem, AssessmentState, RealTimeMetrics

class TestRealTimeAssessment(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.assessment_system = AssessmentSystem()
        self.student_id = "test_student_001"
        self.skill = "running"
        self.mock_video_stream = AsyncMock()
        self.mock_frame = MagicMock()
        self.mock_analysis_results = {
            "score": 0.8,
            "technique": 0.7,
            "performance": 0.8,
            "safety": 0.9
        }

    async def asyncSetUp(self):
        """Set up async test fixtures."""
        await self.assessment_system.initialize()

    async def asyncTearDown(self):
        """Clean up async test fixtures."""
        await self.assessment_system.cleanup()

    @patch('app.services.physical_education.services.assessment_system.MovementAnalyzer.analyze_movement')
    async def test_real_time_assessment_flow(self, mock_analyze_movement):
        """Test the complete real-time assessment flow."""
        # Setup mock
        mock_analyze_movement.return_value = self.mock_analysis_results
        self.mock_video_stream.__aiter__.return_value = [self.mock_frame] * 10

        # Start assessment
        start_result = await self.assessment_system.start_real_time_assessment(
            self.student_id,
            self.skill,
            self.mock_video_stream
        )

        # Verify start result
        self.assertEqual(start_result["status"], "started")
        self.assertEqual(start_result["student_id"], self.student_id)
        self.assertEqual(start_result["skill"], self.skill)
        self.assertIn("timestamp", start_result)

        # Wait for assessment to process
        await asyncio.sleep(1)

        # Stop assessment
        final_report = await self.assessment_system.stop_real_time_assessment(
            self.student_id,
            self.skill
        )

        # Verify final report
        self.assertIn("overall_score", final_report)
        self.assertIn("performance_trend", final_report)
        self.assertIn("confidence", final_report)
        self.assertIn("recommendations", final_report)
        self.assertIn("analytics_summary", final_report)

    async def test_real_time_metrics_calculation(self):
        """Test real-time metrics calculation."""
        # Setup test data
        buffer_data = [
            {"score": 0.8},
            {"score": 0.7},
            {"score": 0.9}
        ]
        self.assessment_system.assessment_buffer[self.skill] = buffer_data

        # Calculate metrics
        metrics = await self.assessment_system._calculate_real_time_metrics(
            self.student_id,
            self.skill
        )

        # Verify metrics
        self.assertIsInstance(metrics, RealTimeMetrics)
        self.assertGreater(metrics.current_score, 0.0)
        self.assertLess(metrics.current_score, 1.0)
        self.assertIn(metrics.trend, ["improving", "stable", "declining"])
        self.assertGreaterEqual(metrics.confidence, 0.0)
        self.assertLessEqual(metrics.confidence, 1.0)

    async def test_trend_calculation(self):
        """Test trend calculation."""
        # Setup test data
        self.assessment_system.trend_analysis[self.skill]["scores"] = [
            0.6, 0.7, 0.8, 0.9
        ]

        # Calculate trend
        trend = self.assessment_system._calculate_trend(self.skill)

        # Verify trend
        self.assertEqual(trend, "improving")

        # Test declining trend
        self.assessment_system.trend_analysis[self.skill]["scores"] = [
            0.9, 0.8, 0.7, 0.6
        ]
        trend = self.assessment_system._calculate_trend(self.skill)
        self.assertEqual(trend, "declining")

        # Test stable trend
        self.assessment_system.trend_analysis[self.skill]["scores"] = [
            0.7, 0.7, 0.7, 0.7
        ]
        trend = self.assessment_system._calculate_trend(self.skill)
        self.assertEqual(trend, "stable")

    async def test_confidence_calculation(self):
        """Test confidence calculation."""
        # Test with consistent scores
        buffer_data = [{"score": 0.8}] * 5
        confidence = self.assessment_system._calculate_confidence(buffer_data)
        self.assertGreater(confidence, 0.8)

        # Test with varying scores
        buffer_data = [
            {"score": 0.8},
            {"score": 0.2},
            {"score": 0.9},
            {"score": 0.1}
        ]
        confidence = self.assessment_system._calculate_confidence(buffer_data)
        self.assertLess(confidence, 0.5)

    async def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Setup test metrics
        metrics = RealTimeMetrics(
            current_score=0.4,
            trend="declining",
            confidence=0.8,
            recommendations=[],
            warnings=[],
            last_update=datetime.now()
        )

        # Update recommendations
        await self.assessment_system._update_recommendations(
            self.student_id,
            self.skill
        )

        # Verify recommendations and warnings
        self.assertGreater(len(metrics.recommendations), 0)
        self.assertGreater(len(metrics.warnings), 0)

    async def test_analytics_update(self):
        """Test analytics data update."""
        # Setup test metrics
        metrics = RealTimeMetrics(
            current_score=0.8,
            trend="improving",
            confidence=0.9,
            recommendations=[],
            warnings=[],
            last_update=datetime.now()
        )

        # Update analytics
        await self.assessment_system._update_analytics(
            self.student_id,
            self.skill,
            metrics
        )

        # Verify analytics update
        self.assertGreater(
            len(self.assessment_system.performance_trends[self.skill]["daily_scores"]),
            0
        )

    async def test_skill_correlation(self):
        """Test skill correlation calculation."""
        # Setup test data
        self.assessment_system.performance_trends[self.skill]["daily_scores"] = [
            {"score": 0.8, "timestamp": datetime.now()},
            {"score": 0.7, "timestamp": datetime.now()},
            {"score": 0.9, "timestamp": datetime.now()}
        ]
        self.assessment_system.performance_trends["jumping"]["daily_scores"] = [
            {"score": 0.7, "timestamp": datetime.now()},
            {"score": 0.6, "timestamp": datetime.now()},
            {"score": 0.8, "timestamp": datetime.now()}
        ]

        # Calculate correlation
        correlation = self.assessment_system._calculate_skill_correlation(
            self.skill,
            "jumping"
        )

        # Verify correlation
        self.assertGreater(correlation, 0.0)
        self.assertLess(correlation, 1.0)

    async def test_performance_prediction(self):
        """Test performance prediction."""
        # Setup test data
        self.assessment_system.performance_trends[self.skill]["daily_scores"] = [
            {"score": 0.6 + (i * 0.05), "timestamp": datetime.now()}
            for i in range(10)
        ]

        # Update predictions
        self.assessment_system._update_predictions(self.skill)

        # Verify predictions
        predictions = self.assessment_system.performance_trends[self.skill]["predictions"]
        self.assertGreater(len(predictions), 0)
        for prediction in predictions:
            self.assertIn("days_ahead", prediction)
            self.assertIn("predicted_score", prediction)
            self.assertGreaterEqual(prediction["predicted_score"], 0.0)
            self.assertLessEqual(prediction["predicted_score"], 1.0)

    async def test_error_handling(self):
        """Test error handling in real-time assessment."""
        # Test invalid state
        self.assessment_system.assessment_state = AssessmentState.ERROR
        with self.assertRaises(RuntimeError):
            await self.assessment_system.start_real_time_assessment(
                self.student_id,
                self.skill,
                self.mock_video_stream
            )

        # Test invalid video stream
        self.assessment_system.assessment_state = AssessmentState.READY
        with self.assertRaises(Exception):
            await self.assessment_system.start_real_time_assessment(
                self.student_id,
                self.skill,
                None
            )

        # Test stopping non-existent assessment
        with self.assertRaises(RuntimeError):
            await self.assessment_system.stop_real_time_assessment(
                self.student_id,
                self.skill
            ) 