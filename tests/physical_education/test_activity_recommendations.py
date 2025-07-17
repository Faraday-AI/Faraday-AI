import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.api.v1.endpoints.physical_education.activity_recommendations import (
    get_activity_recommendations,
    get_recommendation_history,
    clear_recommendations,
    get_category_recommendations,
    get_balanced_recommendations
)
from app.api.v1.models.activity import (
    ActivityRecommendationRequest,
    ActivityRecommendationResponse,
    ActivityType,
    DifficultyLevel
)
from app.services.physical_education.activity_recommendation_service import ActivityRecommendationService

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_service():
    return MagicMock(spec=ActivityRecommendationService)

@pytest.fixture
def sample_recommendation_request():
    return ActivityRecommendationRequest(
        student_id=1,
        class_id=1,
        preferences={
            "difficulty_level": "intermediate",
            "activity_types": ["strength", "cardio"],
            "duration_minutes": 30
        }
    )

@pytest.fixture
def sample_recommendation_response():
    return ActivityRecommendationResponse(
        id=1,
        student_id=1,
        class_id=1,
        activity_id=1,
        recommendation_score=0.85,
        score_breakdown={
            "skill_match": 0.9,
            "fitness_match": 0.8,
            "preference_match": 0.85
        },
        created_at=datetime.now()
    )

@pytest.fixture
def multiple_recommendation_responses() -> List[ActivityRecommendationResponse]:
    return [
        ActivityRecommendationResponse(
            id=i,
            student_id=1,
            class_id=1,
            activity_id=i,
            recommendation_score=0.9 - (i * 0.1),
            score_breakdown={
                "skill_match": 0.9,
                "fitness_match": 0.8,
                "preference_match": 0.85
            },
            created_at=datetime.now() - timedelta(days=i)
        ) for i in range(1, 6)
    ]

@pytest.mark.asyncio
async def test_get_activity_recommendations_success(mock_db, mock_service, sample_recommendation_request):
    # Setup
    mock_service.get_recommendations.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_activity_recommendations(sample_recommendation_request, mock_db)
    
    # Verify
    assert len(result) == 1
    assert result[0].id == 1
    mock_service.get_recommendations.assert_called_once_with(sample_recommendation_request)

@pytest.mark.asyncio
async def test_get_activity_recommendations_error(mock_db, mock_service, sample_recommendation_request):
    # Setup
    mock_service.get_recommendations.side_effect = HTTPException(status_code=404, detail="Student not found")
    
    # Test and Verify
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        with pytest.raises(HTTPException) as exc_info:
            await get_activity_recommendations(sample_recommendation_request, mock_db)
        assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_get_recommendation_history_success(mock_db, mock_service):
    # Setup
    mock_service.get_recommendation_history.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_recommendation_history(1, None, 10, mock_db)
    
    # Verify
    assert len(result) == 1
    assert result[0].id == 1
    mock_service.get_recommendation_history.assert_called_once_with(1, None, 10)

@pytest.mark.asyncio
async def test_clear_recommendations_success(mock_db, mock_service):
    # Setup
    mock_service.clear_recommendations.return_value = True
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await clear_recommendations(1, None, mock_db)
    
    # Verify
    assert result["message"] == "Recommendations cleared successfully"
    mock_service.clear_recommendations.assert_called_once_with(1, None)

@pytest.mark.asyncio
async def test_clear_recommendations_error(mock_db, mock_service):
    # Setup
    mock_service.clear_recommendations.return_value = False
    
    # Test and Verify
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        with pytest.raises(HTTPException) as exc_info:
            await clear_recommendations(1, None, mock_db)
        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_get_category_recommendations_success(mock_db, mock_service):
    # Setup
    mock_service.get_category_recommendations.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_category_recommendations(1, 1, 1, ActivityType.STRENGTH, 5, mock_db)
    
    # Verify
    assert len(result) == 1
    assert result[0].id == 1
    mock_service.get_category_recommendations.assert_called_once_with(
        student_id=1,
        class_id=1,
        category_id=1,
        activity_type=ActivityType.STRENGTH,
        limit=5
    )

@pytest.mark.asyncio
async def test_get_balanced_recommendations_success(mock_db, mock_service):
    # Setup
    mock_service.get_balanced_recommendations.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_balanced_recommendations(1, 1, 5, mock_db)
    
    # Verify
    assert len(result) == 1
    assert result[0].id == 1
    mock_service.get_balanced_recommendations.assert_called_once_with(
        student_id=1,
        class_id=1,
        limit=5
    )

@pytest.mark.asyncio
async def test_get_category_recommendations_invalid_category(mock_db, mock_service):
    # Setup
    mock_service.get_category_recommendations.side_effect = HTTPException(status_code=404, detail="Category not found")
    
    # Test and Verify
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        with pytest.raises(HTTPException) as exc_info:
            await get_category_recommendations(1, 1, 999, ActivityType.STRENGTH, 5, mock_db)
        assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_get_balanced_recommendations_no_data(mock_db, mock_service):
    # Setup
    mock_service.get_balanced_recommendations.return_value = []
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_balanced_recommendations(1, 1, 5, mock_db)
    
    # Verify
    assert len(result) == 0
    mock_service.get_balanced_recommendations.assert_called_once_with(
        student_id=1,
        class_id=1,
        limit=5
    )

@pytest.mark.asyncio
async def test_get_activity_recommendations_empty_preferences(mock_db, mock_service):
    # Setup
    request = ActivityRecommendationRequest(
        student_id=1,
        class_id=1,
        preferences={}
    )
    mock_service.get_recommendations.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_activity_recommendations(request, mock_db)
    
    # Verify
    assert len(result) == 1
    mock_service.get_recommendations.assert_called_once_with(request)

@pytest.mark.asyncio
async def test_get_activity_recommendations_invalid_preferences(mock_db, mock_service):
    # Setup
    request = ActivityRecommendationRequest(
        student_id=1,
        class_id=1,
        preferences={
            "difficulty_level": "invalid_level",
            "activity_types": ["invalid_type"],
            "duration_minutes": -30
        }
    )
    mock_service.get_recommendations.side_effect = ValueError("Invalid preferences")
    
    # Test and Verify
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        with pytest.raises(HTTPException) as exc_info:
            await get_activity_recommendations(request, mock_db)
        assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_get_recommendation_history_pagination(mock_db, mock_service, multiple_recommendation_responses):
    # Setup
    mock_service.get_recommendation_history.return_value = multiple_recommendation_responses[:3]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_recommendation_history(1, None, 3, mock_db)
    
    # Verify
    assert len(result) == 3
    assert result[0].id == 1
    assert result[2].id == 3
    mock_service.get_recommendation_history.assert_called_once_with(1, None, 3)

@pytest.mark.asyncio
async def test_get_recommendation_history_date_filter(mock_db, mock_service, multiple_recommendation_responses):
    # Setup
    mock_service.get_recommendation_history.return_value = multiple_recommendation_responses[2:]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_recommendation_history(1, None, 10, mock_db)
    
    # Verify
    assert len(result) == 3
    assert result[0].id == 3
    mock_service.get_recommendation_history.assert_called_once_with(1, None, 10)

@pytest.mark.asyncio
async def test_get_category_recommendations_multiple_activity_types(mock_db, mock_service):
    # Setup
    mock_service.get_category_recommendations.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_category_recommendations(1, 1, 1, None, 5, mock_db)
    
    # Verify
    assert len(result) == 1
    mock_service.get_category_recommendations.assert_called_once_with(
        student_id=1,
        class_id=1,
        category_id=1,
        activity_type=None,
        limit=5
    )

@pytest.mark.asyncio
async def test_get_balanced_recommendations_single_category(mock_db, mock_service):
    # Setup
    mock_service.get_balanced_recommendations.return_value = [sample_recommendation_response]
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_balanced_recommendations(1, 1, 1, mock_db)
    
    # Verify
    assert len(result) == 1
    mock_service.get_balanced_recommendations.assert_called_once_with(
        student_id=1,
        class_id=1,
        limit=1
    )

@pytest.mark.asyncio
async def test_get_balanced_recommendations_high_limit(mock_db, mock_service, multiple_recommendation_responses):
    # Setup
    mock_service.get_balanced_recommendations.return_value = multiple_recommendation_responses
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await get_balanced_recommendations(1, 1, 100, mock_db)
    
    # Verify
    assert len(result) == 5
    mock_service.get_balanced_recommendations.assert_called_once_with(
        student_id=1,
        class_id=1,
        limit=100
    )

@pytest.mark.asyncio
async def test_clear_recommendations_with_class_filter(mock_db, mock_service):
    # Setup
    mock_service.clear_recommendations.return_value = True
    
    # Test
    with patch('app.api.v1.endpoints.physical_education.activity_recommendations.ActivityRecommendationService', return_value=mock_service):
        result = await clear_recommendations(1, 1, mock_db)
    
    # Verify
    assert result["message"] == "Recommendations cleared successfully"
    mock_service.clear_recommendations.assert_called_once_with(1, 1) 