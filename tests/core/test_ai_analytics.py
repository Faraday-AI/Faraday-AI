import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai.ai_analytics import AIAnalytics
from app.core.monitoring import track_metrics, track_model_performance
import json
import asyncio
from datetime import datetime

@pytest.fixture
def ai_analytics():
    """Create AI analytics service instance for testing."""
    with patch('app.services.ai.ai_analytics.openai.Client') as mock_client:
        with patch('app.services.ai.ai_analytics.tf.keras.models.load_model') as mock_tf_model:
            with patch('app.services.ai.ai_analytics.joblib.load') as mock_joblib:
                with patch('app.services.ai.ai_analytics.mp.solutions.pose') as mock_pose:
                    with patch('app.services.ai.ai_analytics.mp.solutions.face_mesh') as mock_face_mesh:
                        # Mock OpenAI client
                        mock_client.return_value.chat.completions.create = AsyncMock()
                        mock_client.return_value.chat.completions.create.return_value.choices = [
                            Mock(message=Mock(content="Test analysis"))
                        ]
                        
                        # Mock TensorFlow model
                        mock_tf_model.return_value.predict = Mock(return_value=np.array([[0.85]]))
                        
                        # Mock scikit-learn model
                        mock_joblib.return_value.predict = Mock(return_value=np.array([0.75]))
                        
                        # Mock MediaPipe models
                        mock_pose.Pose.return_value = Mock()
                        mock_face_mesh.FaceMesh.return_value = Mock()
                        
                        analytics = AIAnalytics()
                        return analytics

@pytest.fixture
def sample_student_data():
    """Create sample student data for testing."""
    return {
        "student_id": "12345",
        "grade": 10,
        "subjects": ["math", "science"],
        "attendance_rate": 0.95,
        "previous_grades": {
            "math": 85,
            "science": 90
        },
        "lesson_history": [
            {"score": 85, "date": "2024-01-01"},
            {"score": 90, "date": "2024-01-08"}
        ]
    }

@pytest.fixture
def sample_classroom_data():
    """Create sample classroom data for testing."""
    return {
        "class_size": 25,
        "subject": "math",
        "average_score": 85,
        "participation_rate": 0.9
    }

@pytest.fixture
def sample_group_data():
    """Create sample group data for testing."""
    return {
        "composition": {
            "total_students": 25,
            "grade_level": "10",
            "subject": "math",
            "diversity_metrics": {
                "learning_styles": ["visual", "auditory", "kinesthetic"],
                "performance_levels": ["high", "medium", "low"]
            }
        },
        "interaction_patterns": {
            "group_work_frequency": "daily",
            "collaboration_level": "high",
            "peer_learning": "active"
        },
        "learning_outcomes": {
            "average_performance": 85,
            "participation_rate": 0.9,
            "completion_rate": 0.95
        }
    }

@pytest.mark.asyncio
async def test_analyze_student_performance(ai_analytics, sample_student_data):
    """Test student performance analysis."""
    result = await ai_analytics.analyze_student_performance(sample_student_data)
    
    assert isinstance(result, dict)
    assert "prediction_score" in result
    assert "ai_analysis" in result
    assert "recommendations" in result
    assert 0 <= result["prediction_score"] <= 1
    assert isinstance(result["recommendations"], list)

@pytest.mark.asyncio
async def test_analyze_behavior_patterns(ai_analytics, sample_student_data, sample_classroom_data):
    """Test behavior pattern analysis."""
    result = await ai_analytics.analyze_behavior_patterns(sample_student_data, sample_classroom_data)
    
    assert isinstance(result, dict)
    assert "engagement_score" in result
    assert "analysis" in result
    assert "recommendations" in result
    assert 0 <= result["engagement_score"] <= 1
    assert isinstance(result["recommendations"], list)

@pytest.mark.asyncio
async def test_analyze_group_dynamics(ai_analytics, sample_group_data):
    """Test group dynamics analysis."""
    result = await ai_analytics.analyze_group_dynamics(sample_group_data)
    
    assert isinstance(result, dict)
    assert "analysis" in result
    assert "group_metrics" in result
    assert "recommendations" in result
    assert all(0 <= score <= 1 for score in result["group_metrics"].values())

def test_validate_student_data(ai_analytics, sample_student_data):
    """Test student data validation."""
    # Test valid data
    ai_analytics._validate_student_data(sample_student_data)
    
    # Test missing required field
    invalid_data = sample_student_data.copy()
    del invalid_data["student_id"]
    with pytest.raises(ValueError, match="Missing required field"):
        ai_analytics._validate_student_data(invalid_data)
    
    # Test invalid attendance rate
    invalid_data = sample_student_data.copy()
    invalid_data["attendance_rate"] = 1.5
    with pytest.raises(ValueError, match="attendance_rate must be between 0 and 1"):
        ai_analytics._validate_student_data(invalid_data)

def test_validate_classroom_data(ai_analytics, sample_classroom_data):
    """Test classroom data validation."""
    # Test valid data
    ai_analytics._validate_classroom_data(sample_classroom_data)
    
    # Test missing required field
    invalid_data = sample_classroom_data.copy()
    del invalid_data["class_size"]
    with pytest.raises(ValueError, match="Missing required field"):
        ai_analytics._validate_classroom_data(invalid_data)
    
    # Test invalid participation rate
    invalid_data = sample_classroom_data.copy()
    invalid_data["participation_rate"] = 1.5
    with pytest.raises(ValueError, match="participation_rate must be between 0 and 1"):
        ai_analytics._validate_classroom_data(invalid_data)

def test_calculate_engagement_score(ai_analytics, sample_student_data, sample_classroom_data):
    """Test engagement score calculation."""
    score = ai_analytics._calculate_engagement_score(sample_student_data, sample_classroom_data)
    assert 0 <= score <= 1

def test_calculate_group_metrics(ai_analytics, sample_group_data):
    """Test group metrics calculation."""
    metrics = ai_analytics._calculate_group_metrics(sample_group_data)
    assert all(0 <= score <= 1 for score in metrics.values())
    assert "diversity_score" in metrics
    assert "interaction_score" in metrics
    assert "performance_score" in metrics
    assert "overall_score" in metrics

def test_generate_cache_key(ai_analytics):
    """Test cache key generation."""
    data = {"test": "data"}
    key1 = ai_analytics._generate_cache_key(data, "test")
    key2 = ai_analytics._generate_cache_key(data, "test")
    assert key1 == key2
    assert isinstance(key1, str)
    assert len(key1) == 64  # SHA-256 hash length

@pytest.mark.asyncio
async def test_rate_limiting(ai_analytics):
    """Test rate limiting functionality."""
    client_id = "test_client"
    
    # Test within rate limit
    for _ in range(100):
        assert not ai_analytics.rate_limiter.is_rate_limited(client_id)
    
    # Test exceeding rate limit
    assert ai_analytics.rate_limiter.is_rate_limited(client_id)
    
    # Test remaining requests
    assert ai_analytics.rate_limiter.get_remaining_requests(client_id) == 0

@pytest.mark.asyncio
async def test_error_handling(ai_analytics, sample_student_data):
    """Test error handling in analytics methods."""
    # Test OpenAI API error
    ai_analytics.openai_client.chat.completions.create.side_effect = Exception("API Error")
    
    with pytest.raises(Exception):
        await ai_analytics.analyze_student_performance(sample_student_data)
    
    # Test model prediction error
    ai_analytics.performance_model.predict.side_effect = Exception("Model Error")
    
    with pytest.raises(Exception):
        await ai_analytics.analyze_student_performance(sample_student_data)

@pytest.mark.asyncio
async def test_caching(ai_analytics, sample_student_data):
    """Test caching functionality."""
    # First call should cache the result
    result1 = await ai_analytics.analyze_student_performance(sample_student_data)
    
    # Second call should return cached result
    result2 = await ai_analytics.analyze_student_performance(sample_student_data)
    
    assert result1 == result2
    assert ai_analytics.openai_client.chat.completions.create.call_count == 1

def test_model_loading(ai_analytics):
    """Test model loading functionality."""
    assert ai_analytics.performance_model is not None
    assert ai_analytics.behavior_model is not None
    assert ai_analytics.audio_model is not None
    assert ai_analytics.pose is not None
    assert ai_analytics.face_mesh is not None 