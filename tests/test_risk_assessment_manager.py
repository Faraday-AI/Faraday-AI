import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.physical_education.services.risk_assessment_manager import RiskAssessmentManager
from app.services.physical_education.models.safety import RiskAssessment

@pytest.fixture
def risk_assessment_manager():
    return RiskAssessmentManager()

@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db

@pytest.fixture
def mock_assessment_data():
    return {
        "class_id": "class123",
        "activity_type": "team_sports",
        "environment": "gymnasium",
        "risk_level": "medium",
        "environmental_risks": ["slippery_surface", "crowded_space"],
        "student_risks": ["lack_of_experience", "physical_limitation"],
        "activity_risks": ["high_impact", "team_interaction"],
        "mitigation_strategies": ["proper_warmup", "supervision"],
        "metadata": {"notes": "Test assessment"}
    }

@pytest.fixture
def mock_assessment():
    assessment = Mock(spec=RiskAssessment)
    assessment.id = "assessment123"
    assessment.class_id = "class123"
    assessment.activity_type = "team_sports"
    assessment.environment = "gymnasium"
    assessment.date = datetime.utcnow()
    assessment.risk_level = "medium"
    assessment.environmental_risks = ["slippery_surface", "crowded_space"]
    assessment.student_risks = ["lack_of_experience", "physical_limitation"]
    assessment.activity_risks = ["high_impact", "team_interaction"]
    assessment.mitigation_strategies = ["proper_warmup", "supervision"]
    assessment.metadata = {"notes": "Test assessment"}
    return assessment

# Tests for initialization
def test_risk_assessment_manager_initialization(risk_assessment_manager):
    assert risk_assessment_manager.activity_types
    assert risk_assessment_manager.risk_levels
    assert risk_assessment_manager.environmental_risks
    assert risk_assessment_manager.student_risks
    assert risk_assessment_manager.activity_risks

# Tests for create_assessment
@pytest.mark.asyncio
async def test_create_assessment_success(risk_assessment_manager, mock_db, mock_assessment_data):
    with patch.object(mock_db, 'add') as mock_add, \
         patch.object(mock_db, 'commit') as mock_commit, \
         patch.object(mock_db, 'refresh') as mock_refresh:
        
        result = await risk_assessment_manager.create_assessment(
            db=mock_db,
            **mock_assessment_data
        )
        
        assert result["success"] is True
        assert "assessment_id" in result
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_assessment_invalid_activity_type(risk_assessment_manager, mock_db, mock_assessment_data):
    mock_assessment_data["activity_type"] = "invalid_type"
    
    result = await risk_assessment_manager.create_assessment(
        db=mock_db,
        **mock_assessment_data
    )
    
    assert result["success"] is False
    assert "Invalid activity type" in result["message"]

# Tests for get_assessment
@pytest.mark.asyncio
async def test_get_assessment_success(risk_assessment_manager, mock_db, mock_assessment):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_assessment
        
        result = await risk_assessment_manager.get_assessment(
            assessment_id="assessment123",
            db=mock_db
        )
        
        assert result == mock_assessment

@pytest.mark.asyncio
async def test_get_assessment_not_found(risk_assessment_manager, mock_db):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        
        result = await risk_assessment_manager.get_assessment(
            assessment_id="nonexistent",
            db=mock_db
        )
        
        assert result is None

# Tests for get_assessments
@pytest.mark.asyncio
async def test_get_assessments_with_filters(risk_assessment_manager, mock_db, mock_assessment):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [mock_assessment]
        
        result = await risk_assessment_manager.get_assessments(
            class_id="class123",
            activity_type="team_sports",
            risk_level="medium",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            db=mock_db
        )
        
        assert len(result) == 1
        assert result[0] == mock_assessment

# Tests for update_assessment
@pytest.mark.asyncio
async def test_update_assessment_success(risk_assessment_manager, mock_db, mock_assessment):
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'commit') as mock_commit, \
         patch.object(mock_db, 'refresh') as mock_refresh:
        
        mock_query.return_value.filter.return_value.first.return_value = mock_assessment
        
        result = await risk_assessment_manager.update_assessment(
            assessment_id="assessment123",
            update_data={"risk_level": "high"},
            db=mock_db
        )
        
        assert result["success"] is True
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()

# Tests for delete_assessment
@pytest.mark.asyncio
async def test_delete_assessment_success(risk_assessment_manager, mock_db, mock_assessment):
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'delete') as mock_delete, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = mock_assessment
        
        result = await risk_assessment_manager.delete_assessment(
            assessment_id="assessment123",
            db=mock_db
        )
        
        assert result["success"] is True
        mock_delete.assert_called_once()
        mock_commit.assert_called_once()

# Tests for get_assessment_statistics
@pytest.mark.asyncio
async def test_get_assessment_statistics(risk_assessment_manager, mock_db):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [
            Mock(risk_level="low"),
            Mock(risk_level="medium"),
            Mock(risk_level="high")
        ]
        
        result = await risk_assessment_manager.get_assessment_statistics(
            class_id="class123",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            db=mock_db
        )
        
        assert "total_assessments" in result
        assert "risk_level_distribution" in result

# Tests for bulk operations
@pytest.mark.asyncio
async def test_bulk_update_assessments(risk_assessment_manager, mock_db):
    updates = [
        {"assessment_id": "assessment1", "risk_level": "high"},
        {"assessment_id": "assessment2", "risk_level": "medium"}
    ]
    
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = Mock()
        
        result = await risk_assessment_manager.bulk_update_assessments(
            updates=updates,
            db=mock_db
        )
        
        assert "successful_updates" in result
        assert "failed_updates" in result

@pytest.mark.asyncio
async def test_bulk_delete_assessments(risk_assessment_manager, mock_db):
    assessment_ids = ["assessment1", "assessment2"]
    
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'delete') as mock_delete, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = Mock()
        
        result = await risk_assessment_manager.bulk_delete_assessments(
            assessment_ids=assessment_ids,
            db=mock_db
        )
        
        assert "successful_deletions" in result
        assert "failed_deletions" in result

# Tests for error handling
@pytest.mark.asyncio
async def test_error_handling_database_error(risk_assessment_manager, mock_db):
    with patch.object(mock_db, 'query', side_effect=Exception("Database error")):
        result = await risk_assessment_manager.get_assessment(
            assessment_id="assessment123",
            db=mock_db
        )
        
        assert result is None

@pytest.mark.asyncio
async def test_error_handling_validation_error(risk_assessment_manager, mock_db, mock_assessment_data):
    mock_assessment_data["risk_level"] = "invalid_level"
    
    result = await risk_assessment_manager.create_assessment(
        db=mock_db,
        **mock_assessment_data
    )
    
    assert result["success"] is False
    assert "Invalid risk level" in result["message"] 