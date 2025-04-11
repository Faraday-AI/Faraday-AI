import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import numpy as np
from app.services.physical_education.services.assessment_system import AssessmentSystem

class TestAssessmentSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.assessment_system = AssessmentSystem()
        self.student_id = "test_student_001"
        self.test_data = {
            "elementary": {
                "running": {
                    "technique": 0.7,
                    "performance": 0.6,
                    "safety": 0.8,
                    "consistency": 0.5,
                    "improvement": 0.3,
                    "adaptability": 0.4
                },
                "jumping": {
                    "technique": 0.8,
                    "performance": 0.7,
                    "safety": 0.9,
                    "consistency": 0.6,
                    "improvement": 0.4,
                    "adaptability": 0.5
                }
            },
            "middle": {
                "running": {
                    "technique": 0.8,
                    "performance": 0.7,
                    "safety": 0.9,
                    "consistency": 0.6,
                    "improvement": 0.4,
                    "adaptability": 0.5
                },
                "jumping": {
                    "technique": 0.9,
                    "performance": 0.8,
                    "safety": 0.95,
                    "consistency": 0.7,
                    "improvement": 0.5,
                    "adaptability": 0.6
                }
            }
        }

    def test_test_data_validity(self):
        """Test that test data is valid."""
        for age_group in self.test_data:
            for skill in self.test_data[age_group]:
                for metric in self.test_data[age_group][skill]:
                    value = self.test_data[age_group][skill][metric]
                    self.assertGreaterEqual(value, 0.0)
                    self.assertLessEqual(value, 1.0)

    async def asyncSetUp(self):
        """Set up async test fixtures."""
        await self.assessment_system.initialize()

    async def asyncTearDown(self):
        """Clean up async test fixtures."""
        await self.assessment_system.cleanup()

    async def test_elementary_assessment(self):
        """Test assessment for elementary school students."""
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        self.assertIn("score", result)
        self.assertIn("feedback", result)
        self.assertIn("recommendations", result)

    async def test_middle_school_assessment(self):
        """Test assessment for middle school students."""
        result = await self.assessment_system.assess_student(
            self.student_id,
            "middle",
            "jumping",
            self.test_data["middle"]["jumping"]
        )
        self.assertIn("score", result)
        self.assertIn("feedback", result)
        self.assertIn("recommendations", result)

    async def test_invalid_age_group(self):
        """Test assessment with invalid age group."""
        with self.assertRaises(ValueError):
            await self.assessment_system.assess_student(
                self.student_id,
                "invalid",
                "running",
                self.test_data["elementary"]["running"]
            )

    async def test_invalid_skill(self):
        """Test assessment with invalid skill."""
        with self.assertRaises(ValueError):
            await self.assessment_system.assess_student(
                self.student_id,
                "elementary",
                "invalid",
                self.test_data["elementary"]["running"]
            )

    async def test_invalid_video_data(self):
        """Test assessment with invalid video data."""
        with self.assertRaises(ValueError):
            await self.assessment_system.assess_student(
                self.student_id,
                "elementary",
                "running",
                {"invalid": "data"}
            )

    async def test_score_calculation(self):
        """Test score calculation accuracy."""
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        expected_score = (
            self.test_data["elementary"]["running"]["technique"] * 0.3 +
            self.test_data["elementary"]["running"]["performance"] * 0.3 +
            self.test_data["elementary"]["running"]["safety"] * 0.2 +
            self.test_data["elementary"]["running"]["consistency"] * 0.1 +
            self.test_data["elementary"]["running"]["improvement"] * 0.05 +
            self.test_data["elementary"]["running"]["adaptability"] * 0.05
        )
        self.assertAlmostEqual(result["score"], expected_score, places=2)

    async def test_milestone_achievement(self):
        """Test milestone achievement tracking."""
        await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        milestones = await self.assessment_system.get_milestones(self.student_id)
        self.assertIsInstance(milestones, list)
        self.assertGreater(len(milestones), 0)

    async def test_achievement_unlocking(self):
        """Test achievement unlocking system."""
        await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        achievements = await self.assessment_system.get_achievements(self.student_id)
        self.assertIsInstance(achievements, list)
        self.assertGreater(len(achievements), 0)

    async def test_peer_comparison(self):
        """Test peer comparison functionality."""
        await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        comparison = await self.assessment_system.compare_with_peers(
            self.student_id,
            "elementary",
            "running"
        )
        self.assertIn("percentile", comparison)
        self.assertIn("rank", comparison)
        self.assertIn("total_students", comparison)

    async def test_minimum_scores(self):
        """Test minimum score validation."""
        min_data = {
            "technique": 0.0,
            "performance": 0.0,
            "safety": 0.0,
            "consistency": 0.0,
            "improvement": 0.0,
            "adaptability": 0.0
        }
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            min_data
        )
        self.assertEqual(result["score"], 0.0)

    async def test_maximum_scores(self):
        """Test maximum score validation."""
        max_data = {
            "technique": 1.0,
            "performance": 1.0,
            "safety": 1.0,
            "consistency": 1.0,
            "improvement": 1.0,
            "adaptability": 1.0
        }
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            max_data
        )
        self.assertEqual(result["score"], 1.0)

    async def test_optional_video_fields(self):
        """Test assessment with optional video fields."""
        data = self.test_data["elementary"]["running"].copy()
        data.pop("improvement")
        data.pop("adaptability")
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            data
        )
        self.assertIn("score", result)
        self.assertIn("feedback", result)

    async def test_assessment_performance(self):
        """Test assessment performance under load."""
        start_time = datetime.now()
        for _ in range(10):
            await self.assessment_system.assess_student(
                self.student_id,
                "elementary",
                "running",
                self.test_data["elementary"]["running"]
            )
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.assertLess(duration, 5.0)  # Should complete in under 5 seconds

    async def test_concurrent_assessments(self):
        """Test concurrent assessment processing."""
        async def run_assessment(student_id, skill):
            return await self.assessment_system.assess_student(
                student_id,
                "elementary",
                skill,
                self.test_data["elementary"][skill]
            )

        tasks = [
            run_assessment(f"student_{i}", "running")
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIn("score", result)
            self.assertIn("feedback", result)

    async def test_data_persistence(self):
        """Test data persistence between assessments."""
        # First assessment
        await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        
        # Second assessment
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        
        # Check that history is maintained
        history = await self.assessment_system.get_assessment_history(self.student_id)
        self.assertGreater(len(history), 1)

    async def test_feedback_quality(self):
        """Test quality of generated feedback."""
        result = await self.assessment_system.assess_student(
            self.student_id,
            "elementary",
            "running",
            self.test_data["elementary"]["running"]
        )
        feedback = result["feedback"]
        self.assertIsInstance(feedback, str)
        self.assertGreater(len(feedback), 0)
        self.assertIn("strengths", feedback.lower())
        self.assertIn("improvements", feedback.lower()) 