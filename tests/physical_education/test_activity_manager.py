import os
# Set up test environment before any imports
os.environ["TEST_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import WebSocket
from fastapi.exceptions import HTTPException
import time
import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from app.core.database import get_db, get_session_factory, initialize_engines, SessionLocal

from app.services.physical_education.activity_manager import ActivityManager
from app.models.shared_base import SharedBase
from app.models.core.user import User
from app.models.security.api_key import APIKey
from app.models.security.rate_limit import RateLimit, RateLimitPolicy, RateLimitMetrics
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.routine.models import Routine
from app.models.physical_education.activity_adaptation.activity_adaptation import ActivityAdaptation, AdaptationHistory
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    ActivityStatus,
    ActivityCategory,
    ActivityCategoryType,
    ActivityDifficulty as DifficultyLevel,
    EquipmentRequirement,
    RateLimitType,
    RateLimitLevel,
    RateLimitStatus,
    RateLimitTrigger
)

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    return create_engine(os.getenv('DATABASE_URL'))

@pytest.fixture(autouse=True)
def setup_test_db(engine):
    """Set up test database for each test."""
    # Verify environment variables are set
    assert os.getenv('TEST_MODE') == 'true', "TEST_MODE must be set to 'true'"
    assert os.getenv('DATABASE_URL') is not None, "DATABASE_URL must be set"
    assert os.getenv('DATABASE_URL').startswith('sqlite'), "DATABASE_URL must be a SQLite URL in test mode"
    
    # Initialize database with retries
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # Create all tables at once using SharedBase to ensure proper order
            SharedBase.metadata.create_all(bind=engine)
            
            # Create test data
            db = SessionLocal()
            
            # Create test user first with simple string ID
            test_user = User(
                id=1,  # Integer ID
                email="test@example.com",
                first_name="Test",
                last_name="User",
                role="teacher"
            )
            db.add(test_user)
            db.commit()

            # Create test API key next with simple string ID
            test_api_key = APIKey(
                id="test_api_key_123",
                key="test_key",
                name="Test API Key",
                description="Test API Key for testing",
                user_id=1,  # Integer ID
                permissions={},
                is_active=True,
                source="database",
                environment="test",
                service_name="test_service"
            )
            db.add(test_api_key)
            db.commit()

            # Create test rate limit last with integer ID
            test_rate_limit = RateLimit(
                id=1,  # Integer ID
                key="test_rate_limit",
                limit_type=RateLimitType.API,
                limit_level=RateLimitLevel.STANDARD,
                max_requests=100,
                window_size=60,
                burst_size=10,
                current_count=0,
                status=RateLimitStatus.ACTIVE,
                api_key_id="test_api_key_123"
            )
            db.add(test_rate_limit)
            db.commit()

            # Create test rate limit policy with integer foreign key
            test_policy = RateLimitPolicy(
                id=1,  # Integer ID
                rate_limit_id=1,  # Integer foreign key
                name="Test Policy",
                description="Test rate limit policy",
                trigger=RateLimitTrigger.THRESHOLD,
                action="block",
                parameters={"threshold": 80},
                is_active=True
            )
            db.add(test_policy)
            db.commit()

            # Create test rate limit metrics with integer foreign key
            test_metrics = RateLimitMetrics(
                id=1,  # Integer ID
                rate_limit_id=1,  # Integer foreign key
                window_start=datetime.utcnow(),
                request_count=0,
                violation_count=0,
                average_latency=0.0,
                max_latency=0.0,
                burst_count=0,
                metrics_data={}
            )
            db.add(test_metrics)
            db.commit()
            
            db.close()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)
    
    yield

    # Clean up tables
    SharedBase.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    
    # Mock common database operations
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    
    # Mock query chain
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_first = MagicMock()
    
    session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = mock_first
    
    return session

@pytest.fixture
def mock_websocket():
    websocket = AsyncMock(spec=WebSocket)
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    return websocket

@pytest.fixture
def mock_movement_analyzer():
    analyzer = MagicMock()
    analyzer.initialize = AsyncMock()
    analyzer.cleanup = AsyncMock()
    return analyzer

@pytest.fixture
def mock_assessment_system():
    system = MagicMock()
    system.initialize = AsyncMock()
    system.cleanup = AsyncMock()
    return system

@pytest.fixture
def mock_lesson_planner():
    planner = MagicMock()
    planner.initialize = AsyncMock()
    planner.cleanup = AsyncMock()
    return planner

@pytest.fixture
def mock_safety_manager():
    manager = MagicMock()
    manager.initialize = AsyncMock()
    manager.cleanup = AsyncMock()
    return manager

@pytest.fixture
def mock_student_manager():
    manager = MagicMock()
    manager.initialize = AsyncMock()
    manager.cleanup = AsyncMock()
    return manager

@pytest.fixture(autouse=True)
def setup_service_integration(mock_movement_analyzer, mock_assessment_system, mock_lesson_planner, mock_safety_manager, mock_student_manager):
    """Setup service integration for all tests."""
    with patch('app.services.physical_education.activity_manager.service_integration') as mock_service_integration:
        # Set up the services dictionary with the mock services
        mock_service_integration.services = {
            'movement_analyzer': mock_movement_analyzer,
            'assessment_system': mock_assessment_system,
            'lesson_planner': mock_lesson_planner,
            'safety_manager': mock_safety_manager,
            'student_manager': mock_student_manager
        }
        
        # Set up the get_service method
        def get_service_side_effect(service_name):
            if service_name not in mock_service_integration.services:
                raise ValueError(f"Service not found: {service_name}")
            return mock_service_integration.services[service_name]
        
        mock_service_integration.get_service.side_effect = get_service_side_effect
        mock_service_integration._initialized = True
        yield mock_service_integration

@pytest.fixture
def activity_manager(mock_db):
    """Create and initialize an ActivityManager instance."""
    with patch('app.services.physical_education.activity_visualization_manager.ActivityVisualizationManager'), \
         patch('app.services.physical_education.activity_collaboration_manager.ActivityCollaborationManager'), \
         patch('app.services.physical_education.activity_export_manager.ActivityExportManager'), \
         patch('app.services.physical_education.activity_analysis_manager.ActivityAnalysisManager'), \
         patch('app.core.database.get_db', return_value=iter([mock_db])):
        
        # Create and initialize the ActivityManager
        manager = ActivityManager()
        asyncio.run(manager.initialize())
        yield manager
        asyncio.run(manager.cleanup())

@pytest.mark.asyncio
async def test_connect_websocket(activity_manager, mock_websocket):
    # Setup
    student_id = 'test_student'
    
    # Test
    await activity_manager.connect_websocket(student_id, mock_websocket)
    
    # Verify
    assert student_id in activity_manager.active_connections
    assert mock_websocket in activity_manager.active_connections[student_id]
    mock_websocket.accept.assert_called_once()

@pytest.mark.asyncio
async def test_disconnect_websocket(activity_manager, mock_websocket):
    # Setup
    student_id = 'test_student'
    activity_manager.active_connections[student_id] = [mock_websocket]
    
    # Test
    await activity_manager.disconnect_websocket(student_id, mock_websocket)
    
    # Verify
    assert student_id not in activity_manager.active_connections

@pytest.mark.asyncio
async def test_broadcast_update(activity_manager, mock_websocket):
    # Setup
    student_id = 'test_student'
    activity_manager.active_connections[student_id] = [mock_websocket]
    update_data = {'activity_type': 'activity_update', 'data': {'id': 'activity1'}}
    
    # Test
    await activity_manager.broadcast_update(student_id, update_data)
    
    # Verify
    mock_websocket.send_json.assert_called_once_with(update_data)

@pytest.mark.asyncio
async def test_create_activity_success(activity_manager, mock_db):
    # Setup
    activity_data = {
        'name': 'Test Activity',
        'description': 'Test Description',
        'activity_type': ActivityType.STRENGTH_TRAINING.value,
        'difficulty': DifficultyLevel.INTERMEDIATE.value,
        'equipment_required': EquipmentRequirement.NONE.value,
        'categories': [ActivityCategory.FITNESS_TRAINING.value],
        'duration_minutes': 30,
        'instructions': 'Test Instructions',
        'safety_notes': 'Test Safety Notes'
    }
    
    # Mock activity creation
    mock_activity = MagicMock(spec=Activity)
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    # Mock category query
    mock_category = MagicMock()
    mock_category.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_category
    
    # Test
    result = await activity_manager.create_activity(**activity_data)
    
    # Verify
    assert isinstance(result, Activity)
    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_activity_invalid_type(activity_manager):
    # Setup
    activity_data = {
        'name': 'Test Activity',
        'description': 'Test Description',
        'activity_type': 'invalid_type',
        'difficulty': DifficultyLevel.INTERMEDIATE.value,
        'equipment_required': EquipmentRequirement.NONE.value,
        'categories': [ActivityCategory.FITNESS_TRAINING.value],
        'duration_minutes': 30,
        'instructions': 'Test Instructions',
        'safety_notes': 'Test Safety Notes'
    }
    
    # Test and Verify
    with pytest.raises(ValueError):
        await activity_manager.create_activity(**activity_data)

@pytest.mark.asyncio
async def test_create_activity_invalid_difficulty(activity_manager):
    # Setup
    activity_data = {
        'name': 'Test Activity',
        'description': 'Test Description',
        'activity_type': ActivityType.STRENGTH_TRAINING.value,
        'difficulty': 'invalid_difficulty',
        'equipment_required': EquipmentRequirement.NONE.value,
        'categories': [ActivityCategory.FITNESS_TRAINING.value],
        'duration_minutes': 30,
        'instructions': 'Test Instructions',
        'safety_notes': 'Test Safety Notes'
    }
    
    # Test and Verify
    with pytest.raises(ValueError):
        await activity_manager.create_activity(**activity_data)

@pytest.mark.asyncio
async def test_create_activity_invalid_equipment(activity_manager):
    # Setup
    activity_data = {
        'name': 'Test Activity',
        'description': 'Test Description',
        'activity_type': ActivityType.STRENGTH_TRAINING.value,
        'difficulty': DifficultyLevel.INTERMEDIATE.value,
        'equipment_required': 'invalid_equipment',
        'categories': [ActivityCategory.FITNESS_TRAINING.value],
        'duration_minutes': 30,
        'instructions': 'Test Instructions',
        'safety_notes': 'Test Safety Notes'
    }
    
    # Test and Verify
    with pytest.raises(ValueError):
        await activity_manager.create_activity(**activity_data)

@pytest.mark.asyncio
async def test_create_activity_invalid_category(activity_manager):
    # Setup
    activity_data = {
        'name': 'Test Activity',
        'description': 'Test Description',
        'activity_type': ActivityType.STRENGTH_TRAINING.value,
        'difficulty': DifficultyLevel.INTERMEDIATE.value,
        'equipment_required': EquipmentRequirement.NONE.value,
        'categories': ['invalid_category'],
        'duration_minutes': 30,
        'instructions': 'Test Instructions',
        'safety_notes': 'Test Safety Notes'
    }
    
    # Test and Verify
    with pytest.raises(ValueError):
        await activity_manager.create_activity(**activity_data)

@pytest.mark.asyncio
async def test_get_activity_found(activity_manager, mock_db):
    # Setup
    activity_id = 'test_activity'
    mock_activity = MagicMock(spec=Activity)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_activity
    
    # Test
    result = await activity_manager.get_activity(activity_id)
    
    # Verify
    assert result == mock_activity
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_get_activity_not_found(activity_manager, mock_db):
    # Setup
    activity_id = 'test_activity'
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Test
    result = await activity_manager.get_activity(activity_id)
    
    # Verify
    assert result is None
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_update_activity_success(activity_manager, mock_db):
    # Setup
    activity_id = 'test_activity'
    update_data = {
        'name': 'Updated Activity',
        'description': 'Updated Description',
        'difficulty': DifficultyLevel.ADVANCED.value
    }
    mock_activity = MagicMock(spec=Activity)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_activity
    
    # Test
    result = await activity_manager.update_activity(activity_id, **update_data)
    
    # Verify
    assert result == mock_activity
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_activity_not_found(activity_manager, mock_db):
    # Setup
    activity_id = 'test_activity'
    update_data = {
        'name': 'Updated Activity',
        'description': 'Updated Description',
        'difficulty': DifficultyLevel.ADVANCED.value
    }
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Test
    result = await activity_manager.update_activity(activity_id, **update_data)
    
    # Verify
    assert result is None
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_delete_activity_success(activity_manager, mock_db):
    # Setup
    activity_id = 'test_activity'
    mock_activity = MagicMock(spec=Activity)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_activity
    
    # Test
    result = await activity_manager.delete_activity(activity_id)
    
    # Verify
    assert result is True
    mock_db.delete.assert_called_once_with(mock_activity)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_activity_not_found(activity_manager, mock_db):
    # Setup
    activity_id = 'test_activity'
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Test
    result = await activity_manager.delete_activity(activity_id)
    
    # Verify
    assert result is False
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

class TestActivityManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        # Create mock services
        cls.mock_movement_analyzer = MagicMock()
        cls.mock_movement_analyzer.initialize = AsyncMock()
        cls.mock_movement_analyzer.cleanup = AsyncMock()
        
        cls.mock_assessment_system = MagicMock()
        cls.mock_assessment_system.initialize = AsyncMock()
        cls.mock_assessment_system.cleanup = AsyncMock()
        
        cls.mock_lesson_planner = MagicMock()
        cls.mock_lesson_planner.initialize = AsyncMock()
        cls.mock_lesson_planner.cleanup = AsyncMock()
        
        cls.mock_safety_manager = MagicMock()
        cls.mock_safety_manager.initialize = AsyncMock()
        cls.mock_safety_manager.cleanup = AsyncMock()
        
        cls.mock_student_manager = MagicMock()
        cls.mock_student_manager.initialize = AsyncMock()
        cls.mock_student_manager.cleanup = AsyncMock()
        
        # Patch service integration
        cls.service_integration_patcher = patch('app.services.physical_education.activity_manager.service_integration')
        cls.mock_service_integration = cls.service_integration_patcher.start()
        
        # Set up the services dictionary
        cls.mock_service_integration.services = {
            'movement_analyzer': cls.mock_movement_analyzer,
            'assessment_system': cls.mock_assessment_system,
            'lesson_planner': cls.mock_lesson_planner,
            'safety_manager': cls.mock_safety_manager,
            'student_manager': cls.mock_student_manager
        }
        
        # Set up the get_service method
        def get_service_side_effect(service_name):
            if service_name not in cls.mock_service_integration.services:
                raise ValueError(f"Service not found: {service_name}")
            return cls.mock_service_integration.services[service_name]
        
        cls.mock_service_integration.get_service.side_effect = get_service_side_effect
        cls.mock_service_integration._initialized = True

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures for the entire test class."""
        cls.service_integration_patcher.stop()

    def setUp(self):
        """Set up test fixtures for each test method."""
        # Create mock database session
        self.mock_db = MagicMock(spec=Session)
        
        # Patch database
        self.get_db_patcher = patch('app.core.database.get_db', return_value=iter([self.mock_db]))
        self.get_db_patcher.start()
        
        # Create and initialize the ActivityManager
        self.activity_manager = ActivityManager()
        asyncio.run(self.activity_manager.initialize())

        # Test data
        self.test_activity = {
            "name": "Test Activity",
            "description": "Test Description",
            "activity_type": ActivityType.STRENGTH_TRAINING.value,
            "difficulty": DifficultyLevel.INTERMEDIATE.value,
            "equipment_required": EquipmentRequirement.MINIMAL.value,
            "categories": [ActivityCategory.CARDIO.value],
            "duration_minutes": 30,
            "instructions": "Test Instructions",
            "safety_notes": "Test Safety Notes"
        }
        
        self.test_exercise = {
            "name": "Test Exercise",
            "description": "Test Description",
            "activity_id": "test_activity_id",
            "sets": 3,
            "reps": 10,
            "rest_time_seconds": 60,
            "technique_notes": "Test Technique Notes"
        }
        
        self.test_routine = {
            "name": "Test Routine",
            "description": "Test Description",
            "class_id": "test_class_id",
            "activities": [
                {
                    "activity_id": "test_activity_id",
                    "duration_minutes": 15
                }
            ],
            "duration_minutes": 30
        }

    def tearDown(self):
        """Clean up test fixtures for each test method."""
        self.get_db_patcher.stop()
        asyncio.run(self.activity_manager.cleanup())

    async def asyncSetUp(self):
        """Set up async test fixtures."""
        self.mock_websocket = MagicMock(spec=WebSocket)
        await self.activity_manager.connect_websocket("test_student_id", self.mock_websocket)

    async def asyncTearDown(self):
        """Clean up async test fixtures."""
        await self.activity_manager.disconnect_websocket("test_student_id", self.mock_websocket)

    async def test_create_activity(self):
        """Test activity creation."""
        result = await self.activity_manager.create_activity(**self.test_activity)
        
        self.assertIsInstance(result, Activity)
        self.assertEqual(result.name, self.test_activity["name"])
        self.assertEqual(result.description, self.test_activity["description"])
        self.assertEqual(result.activity_type, self.test_activity["activity_type"])
        self.assertEqual(result.difficulty_level, self.test_activity["difficulty_level"])
        self.assertEqual(result.equipment_required, self.test_activity["equipment_required"])
        self.assertEqual(result.categories, self.test_activity["categories"])
        self.assertEqual(result.duration_minutes, self.test_activity["duration_minutes"])

    async def test_get_activity(self):
        """Test retrieving an activity."""
        activity_id = "test_activity_id"
        result = await self.activity_manager.get_activity(activity_id)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Activity)
        self.assertEqual(result.id, activity_id)

    async def test_get_activities_filtering(self):
        """Test filtering activities."""
        activities = await self.activity_manager.get_activities(
            activity_type=ActivityType.STRENGTH_TRAINING.value,
            difficulty_level=DifficultyLevel.INTERMEDIATE.value,
            equipment_required=EquipmentRequirement.MINIMAL.value,
            category=ActivityCategory.CARDIO.value,
            duration_min=20,
            duration_max=40
        )
        
        self.assertIsInstance(activities, list)
        for activity in activities:
            self.assertIsInstance(activity, Activity)
            self.assertEqual(activity.activity_type, ActivityType.STRENGTH_TRAINING.value)
            self.assertEqual(activity.difficulty_level, DifficultyLevel.INTERMEDIATE.value)
            self.assertEqual(activity.equipment_required, EquipmentRequirement.MINIMAL.value)
            self.assertIn(ActivityCategory.CARDIO.value, activity.categories)
            self.assertGreaterEqual(activity.duration_minutes, 20)
            self.assertLessEqual(activity.duration_minutes, 40)

    async def test_create_exercise(self):
        """Test exercise creation."""
        result = await self.activity_manager.create_exercise(**self.test_exercise)
        
        self.assertIsInstance(result, Exercise)
        self.assertEqual(result.name, self.test_exercise["name"])
        self.assertEqual(result.description, self.test_exercise["description"])
        self.assertEqual(result.activity_id, self.test_exercise["activity_id"])
        self.assertEqual(result.sets, self.test_exercise["sets"])
        self.assertEqual(result.reps, self.test_exercise["reps"])
        self.assertEqual(result.rest_time_seconds, self.test_exercise["rest_time_seconds"])

    async def test_create_routine(self):
        """Test routine creation."""
        result = await self.activity_manager.create_routine(**self.test_routine)
        
        self.assertIsInstance(result, Routine)
        self.assertEqual(result.name, self.test_routine["name"])
        self.assertEqual(result.description, self.test_routine["description"])
        self.assertEqual(result.class_id, self.test_routine["class_id"])
        self.assertEqual(len(result.activities), len(self.test_routine["activities"]))
        self.assertEqual(result.duration_minutes, self.test_routine["duration_minutes"])

    async def test_track_activity_performance(self):
        """Test tracking activity performance."""
        result = await self.activity_manager.track_activity_performance(
            activity_id="test_activity_id",
            student_id="test_student_id",
            score=0.85,
            notes="Test performance notes"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("performance_id", result)
        self.assertIn("score", result)
        self.assertIn("notes", result)
        self.assertEqual(result["score"], 0.85)
        self.assertEqual(result["notes"], "Test performance notes")

    async def test_get_recommended_activities(self):
        """Test getting recommended activities."""
        result = await self.activity_manager.get_recommended_activities(
            student_id="test_student_id",
            class_id="test_class_id",
            limit=5
        )
        
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)
        for activity in result:
            self.assertIsInstance(activity, dict)
            self.assertIn("activity_id", activity)
            self.assertIn("name", activity)
            self.assertIn("score", activity)

    async def test_generate_activity_plan(self):
        """Test generating an activity plan."""
        result = await self.activity_manager.generate_activity_plan(
            student_id="test_student_id",
            class_id="test_class_id",
            duration_minutes=60,
            focus_areas=["strength", "cardio"]
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("plan_id", result)
        self.assertIn("activities", result)
        self.assertIn("duration_minutes", result)
        self.assertEqual(result["duration_minutes"], 60)
        self.assertIsInstance(result["activities"], list)

    async def test_analyze_student_performance(self):
        """Test analyzing student performance."""
        result = await self.activity_manager.analyze_student_performance(
            student_id="test_student_id",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("overall_score", result)
        self.assertIn("performance_by_type", result)
        self.assertIn("progress_trend", result)
        self.assertIn("recommendations", result)

    async def test_websocket_connection(self):
        """Test WebSocket connection handling."""
        # Connection already established in asyncSetUp
        self.assertIn("test_student_id", self.activity_manager.active_connections)
        self.assertIn(self.mock_websocket, self.activity_manager.active_connections["test_student_id"])

    async def test_broadcast_update(self):
        """Test broadcasting updates via WebSocket."""
        test_data = {"activity_type": "update", "data": "test"}
        await self.activity_manager.broadcast_update("test_student_id", test_data)
        
        self.mock_websocket.send_json.assert_called_once_with(test_data)

    async def test_export_visualizations(self):
        """Test exporting visualizations."""
        test_visualizations = {
            "performance": {"type": "line", "data": {"x": [1, 2, 3], "y": [4, 5, 6]}},
            "progress": {"type": "bar", "data": {"x": [1, 2, 3], "y": [7, 8, 9]}}
        }
        
        result = await self.activity_manager.export_visualizations(
            student_id="test_student_id",
            visualizations=test_visualizations,
            format="png"
        )
        
        self.assertIsInstance(result, dict)
        for key, value in result.items():
            self.assertIsInstance(value, str)
            self.assertTrue(value.endswith(".png"))

    async def test_collaborative_features(self):
        """Test collaborative features."""
        # Start collaborative session
        session = await self.activity_manager.start_collaborative_analysis(
            student_id="test_student_id",
            participants=["participant1", "participant2"]
        )
        
        self.assertIsInstance(session, dict)
        self.assertIn("session_id", session)
        
        # Add annotation
        annotation = await self.activity_manager.add_collaborative_annotation(
            session_id=session["session_id"],
            user_id="participant1",
            annotation_data={"type": "note", "content": "Test annotation"}
        )
        
        self.assertIsInstance(annotation, dict)
        self.assertIn("annotation_id", annotation)
        self.assertIn("user_id", annotation)
        self.assertEqual(annotation["user_id"], "participant1")
        
        # Get session annotations
        annotations = await self.activity_manager.get_collaborative_annotations(session["session_id"])
        
        self.assertIsInstance(annotations, list)
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0]["annotation_id"], annotation["annotation_id"])
        
        # End session
        await self.activity_manager.end_collaborative_analysis(session["session_id"])
        
        # Verify session is ended
        with self.assertRaises(ValueError):
            await self.activity_manager.get_collaborative_annotations(session["session_id"])

    async def test_invalid_activity_creation(self):
        """Test handling invalid activity creation."""
        # Test missing required fields
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="Test Activity",
                # Missing description
                activity_type=ActivityType.STRENGTH_TRAINING.value
            )
        
        # Test invalid activity type
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="Test Activity",
                description="Test Description",
                activity_type="invalid_type"
            )
        
        # Test invalid difficulty level
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="Test Activity",
                description="Test Description",
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level="invalid_difficulty"
            )

    async def test_invalid_exercise_creation(self):
        """Test handling invalid exercise creation."""
        # Test missing required fields
        with self.assertRaises(ValueError):
            await self.activity_manager.create_exercise(
                name="Test Exercise",
                # Missing activity_id
                sets=3,
                reps=10
            )
        
        # Test invalid sets value
        with self.assertRaises(ValueError):
            await self.activity_manager.create_exercise(
                name="Test Exercise",
                activity_id="test_activity_id",
                sets=-1,  # Invalid negative value
                reps=10
            )
        
        # Test invalid reps value
        with self.assertRaises(ValueError):
            await self.activity_manager.create_exercise(
                name="Test Exercise",
                activity_id="test_activity_id",
                sets=3,
                reps=0  # Invalid zero value
            )

    async def test_invalid_routine_creation(self):
        """Test handling invalid routine creation."""
        # Test missing required fields
        with self.assertRaises(ValueError):
            await self.activity_manager.create_routine(
                name="Test Routine",
                # Missing class_id
                activities=[]
            )
        
        # Test empty activities list
        with self.assertRaises(ValueError):
            await self.activity_manager.create_routine(
                name="Test Routine",
                class_id="test_class_id",
                activities=[]  # Empty activities list
            )
        
        # Test invalid duration
        with self.assertRaises(ValueError):
            await self.activity_manager.create_routine(
                name="Test Routine",
                class_id="test_class_id",
                activities=[{"activity_id": "test_activity_id", "duration_minutes": 15}],
                duration_minutes=0  # Invalid zero duration
            )

    async def test_performance_tracking_edge_cases(self):
        """Test edge cases in performance tracking."""
        # Test maximum score
        result = await self.activity_manager.track_activity_performance(
            activity_id="test_activity_id",
            student_id="test_student_id",
            score=1.0,
            notes="Perfect score"
        )
        
        self.assertEqual(result["score"], 1.0)
        
        # Test minimum score
        result = await self.activity_manager.track_activity_performance(
            activity_id="test_activity_id",
            student_id="test_student_id",
            score=0.0,
            notes="Minimum score"
        )
        
        self.assertEqual(result["score"], 0.0)
        
        # Test score out of range
        with self.assertRaises(ValueError):
            await self.activity_manager.track_activity_performance(
                activity_id="test_activity_id",
                student_id="test_student_id",
                score=1.1,  # Above maximum
                notes="Invalid score"
            )
        
        with self.assertRaises(ValueError):
            await self.activity_manager.track_activity_performance(
                activity_id="test_activity_id",
                student_id="test_student_id",
                score=-0.1,  # Below minimum
                notes="Invalid score"
            )

    async def test_activity_plan_edge_cases(self):
        """Test edge cases in activity plan generation."""
        # Test minimum duration
        result = await self.activity_manager.generate_activity_plan(
            student_id="test_student_id",
            class_id="test_class_id",
            duration_minutes=1,
            focus_areas=["strength"]
        )
        
        self.assertEqual(result["duration_minutes"], 1)
        
        # Test maximum duration
        result = await self.activity_manager.generate_activity_plan(
            student_id="test_student_id",
            class_id="test_class_id",
            duration_minutes=240,  # 4 hours
            focus_areas=["strength", "cardio"]
        )
        
        self.assertEqual(result["duration_minutes"], 240)
        
        # Test invalid duration
        with self.assertRaises(ValueError):
            await self.activity_manager.generate_activity_plan(
                student_id="test_student_id",
                class_id="test_class_id",
                duration_minutes=0,
                focus_areas=["strength"]
            )
        
        with self.assertRaises(ValueError):
            await self.activity_manager.generate_activity_plan(
                student_id="test_student_id",
                class_id="test_class_id",
                duration_minutes=241,  # Above maximum
                focus_areas=["strength"]
            )
        
        # Test empty focus areas
        with self.assertRaises(ValueError):
            await self.activity_manager.generate_activity_plan(
                student_id="test_student_id",
                class_id="test_class_id",
                duration_minutes=60,
                focus_areas=[]  # Empty focus areas
            )

    async def test_websocket_error_handling(self):
        """Test WebSocket error handling."""
        # Test duplicate connection
        await self.activity_manager.connect_websocket("test_student_id", self.mock_websocket)
        
        with self.assertRaises(ValueError):
            await self.activity_manager.connect_websocket("test_student_id", self.mock_websocket)
        
        # Test disconnecting non-existent connection
        await self.activity_manager.disconnect_websocket("test_student_id", self.mock_websocket)
        
        with self.assertRaises(ValueError):
            await self.activity_manager.disconnect_websocket("test_student_id", self.mock_websocket)
        
        # Test broadcasting to non-existent connection
        with self.assertRaises(ValueError):
            await self.activity_manager.broadcast_update("non_existent_student", {"activity_type": "test"})

    async def test_collaborative_session_error_handling(self):
        """Test error handling in collaborative sessions."""
        # Test starting session with invalid participants
        with self.assertRaises(ValueError):
            await self.activity_manager.start_collaborative_analysis(
                student_id="test_student_id",
                participants=[]  # Empty participants list
            )
        
        # Test adding annotation to non-existent session
        with self.assertRaises(ValueError):
            await self.activity_manager.add_collaborative_annotation(
                session_id="non_existent_session",
                user_id="participant1",
                annotation_data={"type": "note", "content": "Test annotation"}
            )
        
        # Test getting annotations from non-existent session
        with self.assertRaises(ValueError):
            await self.activity_manager.get_collaborative_annotations("non_existent_session")
        
        # Test ending non-existent session
        with self.assertRaises(ValueError):
            await self.activity_manager.end_collaborative_analysis("non_existent_session")

    async def test_performance_analysis_edge_cases(self):
        """Test edge cases in performance analysis."""
        # Test analysis with no data
        result = await self.activity_manager.analyze_student_performance(
            student_id="test_student_id",
            start_date=datetime.now(),
            end_date=datetime.now()
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["overall_score"], 0.0)
        self.assertEqual(len(result["performance_by_type"]), 0)
        self.assertEqual(len(result["progress_trend"]), 0)
        self.assertEqual(len(result["recommendations"]), 0)
        
        # Test analysis with invalid date range
        with self.assertRaises(ValueError):
            await self.activity_manager.analyze_student_performance(
                student_id="test_student_id",
                start_date=datetime.now(),
                end_date=datetime.now() - timedelta(days=1)  # End date before start date
            )
        
        # Test analysis with too large date range
        with self.assertRaises(ValueError):
            await self.activity_manager.analyze_student_performance(
                student_id="test_student_id",
                start_date=datetime.now() - timedelta(days=366),  # More than a year
                end_date=datetime.now()
            )

    async def test_export_visualizations_edge_cases(self):
        """Test edge cases in visualization export."""
        # Test empty visualizations
        with self.assertRaises(ValueError):
            await self.activity_manager.export_visualizations(
                student_id="test_student_id",
                visualizations={},  # Empty visualizations
                format="png"
            )
        
        # Test invalid format
        with self.assertRaises(ValueError):
            await self.activity_manager.export_visualizations(
                student_id="test_student_id",
                visualizations={"test": {"type": "line", "data": {"x": [1], "y": [1]}}},
                format="invalid_format"
            )
        
        # Test invalid visualization data
        with self.assertRaises(ValueError):
            await self.activity_manager.export_visualizations(
                student_id="test_student_id",
                visualizations={"test": {"type": "invalid_type", "data": {}}},
                format="png"
            )

    async def test_concurrent_operations(self):
        """Test handling concurrent operations."""
        # Create multiple activities concurrently
        tasks = [
            self.activity_manager.create_activity(
                name=f"Test Activity {i}",
                description=f"Test Description {i}",
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level=DifficultyLevel.INTERMEDIATE.value,
                equipment_required=EquipmentRequirement.MINIMAL.value,
                categories=[ActivityCategory.CARDIO.value],
                duration_minutes=30
            )
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        self.assertEqual(len(results), 5)
        for i, result in enumerate(results):
            self.assertIsInstance(result, Activity)
            self.assertEqual(result.name, f"Test Activity {i}")
        
        # Track multiple performances concurrently
        tasks = [
            self.activity_manager.track_activity_performance(
                activity_id="test_activity_id",
                student_id=f"student_{i}",
                score=0.8,
                notes=f"Test notes {i}"
            )
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        self.assertEqual(len(results), 5)
        for i, result in enumerate(results):
            self.assertIsInstance(result, dict)
            self.assertEqual(result["score"], 0.8)
            self.assertEqual(result["notes"], f"Test notes {i}")

    async def test_data_validation(self):
        """Test data validation in various operations."""
        # Test activity name validation
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="",  # Empty name
                description="Test Description",
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level=DifficultyLevel.INTERMEDIATE.value
            )
        
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="a" * 256,  # Name too long
                description="Test Description",
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level=DifficultyLevel.INTERMEDIATE.value
            )
        
        # Test description validation
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="Test Activity",
                description="",  # Empty description
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level=DifficultyLevel.INTERMEDIATE.value
            )
        
        # Test duration validation
        with self.assertRaises(ValueError):
            await self.activity_manager.create_activity(
                name="Test Activity",
                description="Test Description",
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level=DifficultyLevel.INTERMEDIATE.value,
                duration_minutes=-1  # Negative duration
            )

    async def test_performance_monitoring(self):
        """Test performance monitoring features."""
        # Monitor activity creation performance
        start_time = time.time()
        await self.activity_manager.create_activity(**self.test_activity)
        creation_time = time.time() - start_time
        
        self.assertLess(creation_time, 1.0)  # Should complete within 1 second
        
        # Monitor performance tracking
        start_time = time.time()
        await self.activity_manager.track_activity_performance(
            activity_id="test_activity_id",
            student_id="test_student_id",
            score=0.8,
            notes="Test notes"
        )
        tracking_time = time.time() - start_time
        
        self.assertLess(tracking_time, 0.5)  # Should complete within 0.5 seconds
        
        # Monitor analysis performance
        start_time = time.time()
        await self.activity_manager.analyze_student_performance(
            student_id="test_student_id",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )
        analysis_time = time.time() - start_time
        
        self.assertLess(analysis_time, 2.0)  # Should complete within 2 seconds

    async def test_cleanup_procedures(self):
        """Test cleanup procedures."""
        # Create test data
        await self.activity_manager.create_activity(**self.test_activity)
        await self.activity_manager.create_exercise(**self.test_exercise)
        await self.activity_manager.create_routine(**self.test_routine)
        
        # Test cleanup of old activities
        result = await self.activity_manager.cleanup_old_activities(days=0)  # Cleanup all
        
        self.assertIsInstance(result, dict)
        self.assertIn("deleted_count", result)
        self.assertGreater(result["deleted_count"], 0)
        
        # Test cleanup of old performance data
        result = await self.activity_manager.cleanup_old_performance_data(days=0)  # Cleanup all
        
        self.assertIsInstance(result, dict)
        self.assertIn("deleted_count", result)
        self.assertGreater(result["deleted_count"], 0)
        
        # Verify cleanup
        activities = await self.activity_manager.get_activities()
        self.assertEqual(len(activities), 0)

    async def test_resource_limits(self):
        """Test handling of resource limits."""
        # Test activity limit
        for i in range(1000):  # Create many activities
            await self.activity_manager.create_activity(
                name=f"Test Activity {i}",
                description=f"Test Description {i}",
                activity_type=ActivityType.STRENGTH_TRAINING.value,
                difficulty_level=DifficultyLevel.INTERMEDIATE.value
            )
        
        # Verify limit enforcement
        activities = await self.activity_manager.get_activities()
        self.assertLessEqual(len(activities), 100)  # Should be limited to 100
        
        # Test performance data limit
        for i in range(1000):  # Create many performance records
            await self.activity_manager.track_activity_performance(
                activity_id="test_activity_id",
                student_id=f"student_{i}",
                score=0.8,
                notes=f"Test notes {i}"
            )
        
        # Verify limit enforcement
        result = await self.activity_manager.analyze_student_performance(
            student_id="test_student_id",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        
        self.assertLessEqual(len(result["progress_trend"]), 100)  # Should be limited to 100 data points

    async def test_system_recovery(self):
        """Test system recovery procedures."""
        # Simulate system failure during activity creation
        with patch.object(self.activity_manager, '_save_activity', side_effect=Exception("Simulated failure")):
            with self.assertRaises(Exception):
                await self.activity_manager.create_activity(**self.test_activity)
        
        # Verify system state after failure
        activities = await self.activity_manager.get_activities()
        self.assertEqual(len(activities), 0)  # Should be no activities after failed creation
        
        # Test recovery after performance tracking failure
        with patch.object(self.activity_manager, '_save_performance', side_effect=Exception("Simulated failure")):
            with self.assertRaises(Exception):
                await self.activity_manager.track_activity_performance(
                    activity_id="test_activity_id",
                    student_id="test_student_id",
                    score=0.8,
                    notes="Test notes"
                )
        
        # Verify system state after failure
        result = await self.activity_manager.analyze_student_performance(
            student_id="test_student_id",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )
        
        self.assertEqual(result["overall_score"], 0.0)  # Should have no performance data

    async def test_data_persistence(self):
        """Test data persistence features."""
        # Create test data
        activity = await self.activity_manager.create_activity(**self.test_activity)
        exercise = await self.activity_manager.create_exercise(**self.test_exercise)
        routine = await self.activity_manager.create_routine(**self.test_routine)
        
        # Test activity persistence
        retrieved_activity = await self.activity_manager.get_activity(activity.id)
        self.assertIsNotNone(retrieved_activity)
        self.assertEqual(retrieved_activity.name, activity.name)
        
        # Test exercise persistence
        retrieved_exercise = await self.activity_manager.get_exercise(exercise.id)
        self.assertIsNotNone(retrieved_exercise)
        self.assertEqual(retrieved_exercise.name, exercise.name)
        
        # Test routine persistence
        retrieved_routine = await self.activity_manager.get_routine(routine.id)
        self.assertIsNotNone(retrieved_routine)
        self.assertEqual(retrieved_routine.name, routine.name)
        
        # Test performance data persistence
        performance = await self.activity_manager.track_activity_performance(
            activity_id=activity.id,
            student_id="test_student_id",
            score=0.8,
            notes="Test notes"
        )
        
        result = await self.activity_manager.analyze_student_performance(
            student_id="test_student_id",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )
        
        self.assertGreater(result["overall_score"], 0.0)  # Should have performance data

    async def test_security_measures(self):
        """Test security measures."""
        # Test unauthorized access
        with self.assertRaises(HTTPException):
            await self.activity_manager.get_activity(
                activity_id="test_activity_id",
                user_id="unauthorized_user"
            )
        
        # Test data access control
        activity = await self.activity_manager.create_activity(
            **self.test_activity,
            created_by="teacher1"
        )
        
        # Teacher should have access
        retrieved_activity = await self.activity_manager.get_activity(
            activity_id=activity.id,
            user_id="teacher1"
        )
        self.assertIsNotNone(retrieved_activity)
        
        # Other teacher should not have access
        with self.assertRaises(HTTPException):
            await self.activity_manager.get_activity(
                activity_id=activity.id,
                user_id="teacher2"
            )
        
        # Test performance data access
        performance = await self.activity_manager.track_activity_performance(
            activity_id=activity.id,
            student_id="student1",
            score=0.8,
            notes="Test notes"
        )
        
        # Student should have access to their own data
        result = await self.activity_manager.analyze_student_performance(
            student_id="student1",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            user_id="student1"
        )
        self.assertGreater(result["overall_score"], 0.0)
        
        # Other student should not have access
        with self.assertRaises(HTTPException):
            await self.activity_manager.analyze_student_performance(
                student_id="student1",
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now(),
                user_id="student2"
            )

    async def test_integration_with_other_components(self):
        """Test integration with other system components."""
        # Test integration with safety manager
        activity = await self.activity_manager.create_activity(**self.test_activity)
        
        safety_check = await self.activity_manager.check_activity_safety(
            activity_id=activity.id,
            environment={"surface": "hardwood", "temperature": 72}
        )
        
        self.assertIsInstance(safety_check, dict)
        self.assertIn("risk_level", safety_check)
        self.assertIn("recommendations", safety_check)
        
        # Test integration with assessment system
        assessment = await self.activity_manager.get_activity_assessment(
            activity_id=activity.id,
            student_id="test_student_id"
        )
        
        self.assertIsInstance(assessment, dict)
        self.assertIn("score", assessment)
        self.assertIn("feedback", assessment)
        
        # Test integration with visualization system
        visualizations = await self.activity_manager.get_activity_visualizations(
            activity_id=activity.id,
            student_id="test_student_id"
        )
        
        self.assertIsInstance(visualizations, dict)
        self.assertIn("performance", visualizations)
        self.assertIn("progress", visualizations)

    async def test_backup_and_recovery(self):
        """Test backup and recovery procedures."""
        # Create test data
        activity = await self.activity_manager.create_activity(**self.test_activity)
        exercise = await self.activity_manager.create_exercise(**self.test_exercise)
        routine = await self.activity_manager.create_routine(**self.test_routine)
        
        # Create backup
        backup = await self.activity_manager.create_backup()
        
        self.assertIsInstance(backup, dict)
        self.assertIn("backup_id", backup)
        self.assertIn("timestamp", backup)
        
        # Simulate data loss
        await self.activity_manager.cleanup_old_activities(days=0)
        await self.activity_manager.cleanup_old_performance_data(days=0)
        
        # Restore from backup
        await self.activity_manager.restore_from_backup(backup["backup_id"])
        
        # Verify restoration
        retrieved_activity = await self.activity_manager.get_activity(activity.id)
        self.assertIsNotNone(retrieved_activity)
        self.assertEqual(retrieved_activity.name, activity.name)
        
        retrieved_exercise = await self.activity_manager.get_exercise(exercise.id)
        self.assertIsNotNone(retrieved_exercise)
        self.assertEqual(retrieved_exercise.name, exercise.name)
        
        retrieved_routine = await self.activity_manager.get_routine(routine.id)
        self.assertIsNotNone(retrieved_routine)
        self.assertEqual(retrieved_routine.name, routine.name)

    async def test_system_monitoring(self):
        """Test system monitoring features."""
        # Test performance metrics
        metrics = await self.activity_manager.get_system_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("activity_count", metrics)
        self.assertIn("exercise_count", metrics)
        self.assertIn("routine_count", metrics)
        self.assertIn("performance_count", metrics)
        
        # Test error logging
        with patch.object(self.activity_manager, '_save_activity', side_effect=Exception("Test error")):
            try:
                await self.activity_manager.create_activity(**self.test_activity)
            except Exception:
                pass
        
        # Verify error was logged
        logs = await self.activity_manager.get_system_logs()
        self.assertGreater(len(logs), 0)
        self.assertTrue(any("Test error" in log["message"] for log in logs))
        
        # Test resource usage monitoring
        usage = await self.activity_manager.get_resource_usage()
        
        self.assertIsInstance(usage, dict)
        self.assertIn("memory_usage", usage)
        self.assertIn("cpu_usage", usage)
        self.assertIn("disk_usage", usage) 