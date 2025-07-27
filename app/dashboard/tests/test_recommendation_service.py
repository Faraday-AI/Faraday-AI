"""
Tests for the recommendation service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.dashboard.models import (
    User,
    GPTDefinition,
    DashboardGPTSubscription,
    GPTContext,
    GPTPerformance,
    ContextInteraction
)
from app.dashboard.services.recommendation_service import RecommendationService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def recommendation_service(mock_db):
    return RecommendationService(mock_db)

@pytest.fixture
def sample_gpt():
    return Mock(
        id="gpt-1",
        name="Test GPT",
        category="TEACHER",
        type="MATH_TEACHER",
        description="A math teacher GPT",
        capabilities={
            "keywords": ["math", "algebra", "teaching"],
            "use_cases": ["lesson_planning", "problem_solving"]
        },
        requirements={"math_knowledge": True}
    )

@pytest.fixture
def sample_subscriptions():
    return [
        Mock(
            id="sub-1",
            gpt_definition=Mock(
                id="gpt-2",
                category="STUDENT",
                capabilities={"math_knowledge": True}
            )
        ),
        Mock(
            id="sub-2",
            gpt_definition=Mock(
                id="gpt-3",
                category="TEACHER",
                capabilities={"language": True}
            )
        )
    ]

@pytest.fixture
def sample_context_data():
    return {
        "keywords": ["math", "teaching", "homework"],
        "subject": "mathematics",
        "level": "intermediate"
    }

@pytest.fixture
def sample_interactions():
    return [
        Mock(
            id="int-1",
            interaction_type="lesson_planning",
            timestamp=datetime.utcnow() - timedelta(days=1)
        ),
        Mock(
            id="int-2",
            interaction_type="problem_solving",
            timestamp=datetime.utcnow() - timedelta(days=2)
        )
    ]

async def test_calculate_gpt_score_full(
    recommendation_service,
    sample_gpt,
    sample_subscriptions,
    sample_context_data,
    sample_interactions,
    mock_db
):
    """Test full score calculation with all components."""
    # Mock database queries
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = sample_interactions
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = await recommendation_service.calculate_gpt_score(
        gpt=sample_gpt,
        user_id="user-1",
        current_subscriptions=sample_subscriptions,
        context_data=sample_context_data
    )

    assert isinstance(result, dict)
    assert "score" in result
    assert "components" in result
    assert "reasons" in result
    assert 0 <= result["score"] <= 1
    assert len(result["components"]) == 5
    assert all(0 <= score <= 1 for score in result["components"].values())

def test_calculate_category_score(
    recommendation_service,
    sample_gpt,
    sample_subscriptions
):
    """Test category score calculation."""
    score = recommendation_service._calculate_category_score(
        sample_gpt,
        sample_subscriptions
    )
    assert 0 <= score <= 1

def test_calculate_compatibility_score(
    recommendation_service,
    sample_gpt,
    sample_subscriptions
):
    """Test compatibility score calculation."""
    score = recommendation_service._calculate_compatibility_score(
        sample_gpt,
        sample_subscriptions
    )
    assert 0 <= score <= 1

def test_calculate_context_score(
    recommendation_service,
    sample_gpt,
    sample_context_data
):
    """Test context relevance score calculation."""
    score = recommendation_service._calculate_context_score(
        sample_gpt,
        sample_context_data
    )
    assert 0 <= score <= 1

def test_calculate_usage_score(
    recommendation_service,
    sample_gpt,
    sample_interactions
):
    """Test usage pattern score calculation."""
    score = recommendation_service._calculate_usage_score(
        sample_gpt,
        sample_interactions
    )
    assert 0 <= score <= 1

def test_calculate_performance_score(
    recommendation_service,
    sample_gpt,
    mock_db
):
    """Test performance metrics score calculation."""
    # Mock performance metrics
    mock_metrics = [
        Mock(
            metrics={
                "accuracy": 0.8,
                "response_time_score": 0.7,
                "user_satisfaction": 0.9
            }
        )
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_metrics

    score = recommendation_service._calculate_performance_score(sample_gpt)
    assert 0 <= score <= 1

def test_error_handling(recommendation_service, sample_gpt):
    """Test error handling in score calculations."""
    # Test with invalid data
    score = recommendation_service._calculate_category_score(
        sample_gpt,
        None  # Invalid subscriptions
    )
    assert score == 0.5  # Should return default score

    score = recommendation_service._calculate_context_score(
        sample_gpt,
        None  # Invalid context data
    )
    assert score == 0.5  # Should return default score

async def test_get_user_interactions(
    recommendation_service,
    mock_db,
    sample_interactions
):
    """Test retrieval of user interactions."""
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = sample_interactions
    
    interactions = recommendation_service._get_user_interactions("user-1")
    assert len(interactions) == len(sample_interactions)
    # Since we're using Mock objects, just verify they have the expected attributes
    assert all(hasattr(i, 'id') for i in interactions)

async def test_reason_generation(
    recommendation_service,
    sample_gpt,
    sample_subscriptions,
    sample_context_data
):
    """Test generation of recommendation reasons."""
    # Mock high scores for all components
    with patch.object(
        recommendation_service,
        '_calculate_category_score',
        return_value=0.8
    ), patch.object(
        recommendation_service,
        '_calculate_compatibility_score',
        return_value=0.8
    ), patch.object(
        recommendation_service,
        '_calculate_context_score',
        return_value=0.8
    ), patch.object(
        recommendation_service,
        '_calculate_usage_score',
        return_value=0.8
    ), patch.object(
        recommendation_service,
        '_calculate_performance_score',
        return_value=0.8
    ):
        result = await recommendation_service.calculate_gpt_score(
            sample_gpt,
            "user-1",
            sample_subscriptions,
            sample_context_data
        )
        
        assert len(result["reasons"]) > 0
        assert all(isinstance(reason, str) for reason in result["reasons"]) 