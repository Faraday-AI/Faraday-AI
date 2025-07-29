import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.activity_assessment_manager import ActivityAssessmentManager
from datetime import datetime, timedelta
import numpy as np

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_assessment_model():
    with patch('app.models.skill_assessment.SkillAssessmentModel') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def assessment_manager(mock_db, mock_activity_manager, mock_assessment_model):
    return ActivityAssessmentManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_assess_activity(assessment_manager, mock_assessment_model):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    assessment_data = {
        "completion_time": 45,
        "accuracy": 0.85,
        "form_score": 0.9,
        "effort_level": 0.8
    }
    mock_assessment_model.return_value.assess.return_value = {
        "score": 0.88,
        "feedback": "Good performance with room for improvement",
        "criteria_scores": {
            "completion_time": 0.85,
            "accuracy": 0.85,
            "form": 0.9,
            "effort": 0.8
        }
    }
    
    # Test
    result = await assessment_manager.assess_activity(activity_id, student_id, assessment_data)
    
    # Verify
    assert 'score' in result
    assert 'feedback' in result
    assert 'criteria_scores' in result
    mock_assessment_model.return_value.assess.assert_called_once()

@pytest.mark.asyncio
async def test_get_assessment_criteria(assessment_manager, mock_assessment_model):
    # Setup
    activity_id = "test_activity"
    mock_assessment_model.return_value.get_criteria.return_value = {
        "criteria": [
            {"name": "completion_time", "weight": 0.3},
            {"name": "accuracy", "weight": 0.3},
            {"name": "form", "weight": 0.2},
            {"name": "effort", "weight": 0.2}
        ]
    }
    
    # Test
    result = await assessment_manager.get_assessment_criteria(activity_id)
    
    # Verify
    assert 'criteria' in result
    assert len(result['criteria']) == 4
    assert all('name' in item for item in result['criteria'])
    assert all('weight' in item for item in result['criteria'])
    mock_assessment_model.return_value.get_criteria.assert_called_once()

@pytest.mark.asyncio
async def test_record_assessment_result(assessment_manager, mock_db):
    # Setup
    activity_id = "test_activity"
    student_id = "test_student"
    assessment_result = {
        "score": 0.88,
        "feedback": "Good performance",
        "criteria_scores": {
            "completion_time": 0.85,
            "accuracy": 0.85,
            "form": 0.9,
            "effort": 0.8
        }
    }
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    
    # Test
    result = await assessment_manager.record_assessment_result(activity_id, student_id, assessment_result)
    
    # Verify
    assert result['recorded'] is True
    assert 'assessment_id' in result
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_assessment_history(assessment_manager, mock_db):
    # Setup
    student_id = "test_student"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "assess1",
            "activity_id": "test_activity",
            "score": 0.88,
            "timestamp": datetime.now() - timedelta(days=1),
            "feedback": "Good performance"
        }
    ]
    
    # Test
    result = await assessment_manager.get_assessment_history(student_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('activity_id' in item for item in result)
    assert all('score' in item for item in result)
    assert all('timestamp' in item for item in result)
    assert all('feedback' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_assessment_trends(assessment_manager, mock_assessment_model):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    mock_assessment_model.return_value.analyze_trends.return_value = {
        "trends": {
            "score_trend": "improving",
            "improvement_rate": 0.15,
            "weak_areas": ["accuracy"],
            "strong_areas": ["form", "effort"]
        }
    }
    
    # Test
    result = await assessment_manager.analyze_assessment_trends(student_id, activity_id)
    
    # Verify
    assert 'trends' in result
    assert 'score_trend' in result['trends']
    assert 'improvement_rate' in result['trends']
    assert 'weak_areas' in result['trends']
    assert 'strong_areas' in result['trends']
    mock_assessment_model.return_value.analyze_trends.assert_called_once()

@pytest.mark.asyncio
async def test_generate_assessment_report(assessment_manager, mock_assessment_model):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    time_range = {
        "start": datetime.now() - timedelta(days=30),
        "end": datetime.now()
    }
    mock_assessment_model.return_value.generate_report.return_value = {
        "report_id": "report123",
        "summary": {
            "average_score": 0.85,
            "improvement": 0.1,
            "consistency": 0.8
        },
        "detailed_analysis": {
            "by_criteria": {
                "completion_time": {"average": 0.85, "trend": "improving"},
                "accuracy": {"average": 0.82, "trend": "stable"},
                "form": {"average": 0.88, "trend": "improving"},
                "effort": {"average": 0.9, "trend": "stable"}
            }
        }
    }
    
    # Test
    result = await assessment_manager.generate_assessment_report(student_id, activity_id, time_range)
    
    # Verify
    assert 'report_id' in result
    assert 'summary' in result
    assert 'detailed_analysis' in result
    mock_assessment_model.return_value.generate_report.assert_called_once()

@pytest.mark.asyncio
async def test_calculate_criteria_scores(assessment_manager, mock_assessment_model):
    # Setup
    performance_data = {
        "completion_time": 45,
        "accuracy": 0.85,
        "effort_level": 0.7,
        "form_score": 0.8
    }
    criteria = {
        "speed": {"weight": 0.3},
        "accuracy": {"weight": 0.4},
        "form": {"weight": 0.3}
    }
    mock_assessment_model.return_value.predict.return_value = np.array([0.8])
    
    # Test
    result = await assessment_manager.calculate_criteria_scores(performance_data, criteria)
    
    # Verify
    assert len(result) == len(criteria)
    assert all(0 <= score <= 1 for score in result.values())
    mock_assessment_model.return_value.predict.assert_called_once()

@pytest.mark.asyncio
async def test_generate_assessment_feedback(assessment_manager):
    # Setup
    criteria_scores = {
        "speed": 0.7,
        "accuracy": 0.8,
        "form": 0.9
    }
    overall_score = 0.8
    
    # Test
    result = await assessment_manager.generate_assessment_feedback(criteria_scores, overall_score)
    
    # Verify
    assert 'summary' in result
    assert 'strengths' in result
    assert 'areas_for_improvement' in result
    assert 'recommendations' in result

@pytest.mark.asyncio
async def test_track_assessment_progress(assessment_manager, mock_activity_manager):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    assessment_id = "test_assessment"
    mock_activity_manager.get_activity.return_value = {
        "id": activity_id,
        "assessments": [{"id": assessment_id, "completed_at": datetime.now()}]
    }
    
    # Test
    result = await assessment_manager.track_assessment_progress(student_id, activity_id, assessment_id)
    
    # Verify
    assert 'progress' in result
    assert 'improvement_areas' in result
    assert 'recommendations' in result
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_export_assessment_report(assessment_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    assessment_id = "test_assessment"
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "id": assessment_id,
        "completed_at": datetime.now(),
        "overall_score": 0.8,
        "criteria_scores": {"speed": 0.7, "accuracy": 0.8, "form": 0.9},
        "feedback": {
            "summary": "Good performance",
            "strengths": ["Accuracy", "Form"],
            "areas_for_improvement": ["Speed"],
            "recommendations": ["Practice speed drills"]
        }
    }
    
    # Test
    result = await assessment_manager.export_assessment_report(student_id, activity_id, assessment_id)
    
    # Verify
    assert 'report_id' in result
    assert 'download_url' in result
    assert 'expires_at' in result
    mock_db.query.assert_called_once() 