import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
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
        
        # Additional test data for assessment operations
        self.mock_assessment_data = {
            'assessment_id': 'assess1',
            'student_id': 'student1',
            'type': 'fitness_test',
            'date': datetime.now(),
            'components': {
                'endurance': {
                    'score': 85,
                    'max_score': 100,
                    'metrics': ['distance', 'time', 'heart_rate']
                },
                'strength': {
                    'score': 75,
                    'max_score': 100,
                    'metrics': ['reps', 'weight', 'form']
                },
                'flexibility': {
                    'score': 90,
                    'max_score': 100,
                    'metrics': ['range', 'form', 'balance']
                }
            },
            'overall_score': 83.3,
            'notes': 'Good performance overall, needs improvement in strength'
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

    async def test_assessment_operations(self):
        """Test basic assessment operations (CRUD)."""
        # Create assessment
        assessment = await self.assessment_system.create_assessment(self.mock_assessment_data)
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment['assessment_id'], self.mock_assessment_data['assessment_id'])
        
        # Get assessment
        retrieved = await self.assessment_system.get_assessment(assessment['assessment_id'])
        self.assertEqual(retrieved['assessment_id'], assessment['assessment_id'])
        
        # Update assessment
        updated_data = self.mock_assessment_data.copy()
        updated_data['components']['strength']['score'] = 80
        updated = await self.assessment_system.update_assessment(assessment['assessment_id'], updated_data)
        self.assertEqual(updated['components']['strength']['score'], 80)
        
        # Delete assessment
        result = await self.assessment_system.delete_assessment(assessment['assessment_id'])
        self.assertTrue(result)
        with self.assertRaises(Exception):
            await self.assessment_system.get_assessment(assessment['assessment_id'])

    async def test_assessment_configuration(self):
        """Test assessment configuration functionality."""
        await self.assessment_system.configure_assessment(
            assessment_types=['fitness_test', 'skill_test', 'performance_test'],
            scoring_rules={
                'weighted_average': True,
                'component_weights': {'endurance': 0.4, 'strength': 0.3, 'flexibility': 0.3}
            },
            grading_criteria={
                'A': 90,
                'B': 80,
                'C': 70,
                'D': 60
            }
        )
        
        config = self.assessment_system.assessment_config
        self.assertIn('fitness_test', config['assessment_types'])
        self.assertTrue(config['scoring_rules']['weighted_average'])
        self.assertEqual(config['grading_criteria']['A'], 90)

    async def test_assessment_report_generation(self):
        """Test assessment report generation."""
        assessment = await self.assessment_system.create_assessment(self.mock_assessment_data)
        report = await self.assessment_system.generate_assessment_report(assessment)
        
        self.assertIn('summary', report)
        self.assertIn('component_scores', report)
        self.assertIn('strengths', report)
        self.assertIn('areas_for_improvement', report)
        self.assertIn('recommendations', report)

    async def test_assessment_trend_analysis(self):
        """Test assessment trend analysis."""
        assessment1 = await self.assessment_system.create_assessment(self.mock_assessment_data)
        assessment2_data = self.mock_assessment_data.copy()
        assessment2_data['assessment_id'] = 'assess2'
        assessment2_data['date'] = datetime.now() + timedelta(days=30)
        assessment2 = await self.assessment_system.create_assessment(assessment2_data)
        
        trends = await self.assessment_system.analyze_assessment_trends('student1')
        self.assertIn('progress', trends)
        self.assertIn('improvement_areas', trends)
        self.assertIn('consistency', trends)
        self.assertIn('predictions', trends)

    async def test_assessment_comparison(self):
        """Test assessment comparison functionality."""
        assessment1 = await self.assessment_system.create_assessment(self.mock_assessment_data)
        assessment2_data = self.mock_assessment_data.copy()
        assessment2_data['assessment_id'] = 'assess2'
        assessment2_data['components']['strength']['score'] = 85
        assessment2 = await self.assessment_system.create_assessment(assessment2_data)
        
        comparison = await self.assessment_system.compare_assessments(
            assessment1['assessment_id'],
            assessment2['assessment_id']
        )
        self.assertIn('score_differences', comparison)
        self.assertIn('improvements', comparison)
        self.assertIn('regressions', comparison)
        self.assertIn('overall_change', comparison)

    async def test_assessment_export(self):
        """Test assessment export functionality."""
        assessment = await self.assessment_system.create_assessment(self.mock_assessment_data)
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            await self.assessment_system.export_assessment(assessment, 'csv', 'assessment.csv')
            mock_to_csv.assert_called_once()
        
        with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
            await self.assessment_system.export_assessment(assessment, 'pdf', 'assessment.pdf')
            mock_canvas.assert_called_once()

    async def test_assessment_validation(self):
        """Test assessment data validation."""
        valid_data = {
            'assessment_id': 'assess1',
            'student_id': 'student1',
            'type': 'fitness_test',
            'components': {
                'endurance': {'score': 85, 'max_score': 100}
            }
        }
        
        self.assertTrue(await self.assessment_system._validate_assessment_data(valid_data))
        
        invalid_data = valid_data.copy()
        invalid_data['components']['endurance']['score'] = 150  # Score above maximum
        self.assertFalse(await self.assessment_system._validate_assessment_data(invalid_data)) 