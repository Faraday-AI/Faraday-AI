import pytest
from unittest.mock import AsyncMock, patch
from app.services.grading_service import GradingService
import json

@pytest.fixture
def grading_service():
    return GradingService()

@pytest.fixture
def sample_rubric():
    return {
        "content": 0.4,
        "organization": 0.3,
        "language": 0.3
    }

@pytest.fixture
def sample_code_requirements():
    return [
        "Function should handle edge cases",
        "Code should be well-documented",
        "Should follow PEP 8 style guide"
    ]

@pytest.fixture
def sample_test_cases():
    return [
        {
            "input": "test input",
            "expected_output": "test output",
            "description": "Basic test case"
        }
    ]

@pytest.fixture
def mock_openai_response():
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "score": 85.0,
                    "feedback": {
                        "overall": "Good work overall",
                        "criterion_specific": {
                            "content": "Strong content",
                            "organization": "Well organized"
                        },
                        "strengths": ["Clear structure", "Good examples"],
                        "areas_for_improvement": ["More detail needed"]
                    },
                    "detailed_analysis": {
                        "content": 0.9,
                        "organization": 0.8,
                        "language": 0.8
                    }
                })
            }
        }]
    }

@pytest.mark.asyncio
async def test_grade_submission(grading_service, sample_rubric, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test submission grading
        result = await grading_service.grade_submission(
            content="Test submission content",
            rubric=sample_rubric,
            submission_type="text",
            max_score=100.0
        )
        
        # Verify result structure
        assert "score" in result
        assert "feedback" in result
        assert "detailed_analysis" in result
        assert "submission_type" in result
        assert "max_score" in result
        assert "graded_at" in result
        assert "model_used" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "system" in call_args["messages"][0]["content"]
        assert "user" in call_args["messages"][1]["content"]

@pytest.mark.asyncio
async def test_grade_code_submission(grading_service, sample_code_requirements, 
                                   sample_test_cases, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test code submission grading
        result = await grading_service.grade_code_submission(
            code="def test_function(): pass",
            requirements=sample_code_requirements,
            test_cases=sample_test_cases
        )
        
        # Verify result structure
        assert "score" in result
        assert "feedback" in result
        assert "detailed_analysis" in result
        assert "submission_type" in result
        assert "graded_at" in result
        assert "model_used" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "code reviewer" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_grade_essay(grading_service, sample_rubric, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test essay grading
        result = await grading_service.grade_essay(
            essay="Test essay content",
            rubric=sample_rubric,
            word_count=500
        )
        
        # Verify result structure
        assert "score" in result
        assert "feedback" in result
        assert "detailed_analysis" in result
        assert "submission_type" in result
        assert "graded_at" in result
        assert "model_used" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "essay grader" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_batch_grade(grading_service, sample_rubric, sample_code_requirements, 
                          sample_test_cases, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Prepare test submissions
        submissions = [
            {
                "type": "text",
                "content": "Test content 1",
                "rubric": sample_rubric
            },
            {
                "type": "code",
                "content": "def test(): pass",
                "requirements": sample_code_requirements,
                "test_cases": sample_test_cases
            },
            {
                "type": "essay",
                "content": "Test essay content",
                "rubric": sample_rubric,
                "word_count": 500
            }
        ]
        
        # Test batch grading
        results = await grading_service.batch_grade(submissions)
        
        # Verify results
        assert len(results) == 3
        assert all("score" in result for result in results)
        assert all("feedback" in result for result in results)
        assert all("detailed_analysis" in result for result in results)
        
        # Verify OpenAI API calls
        assert mock_create.call_count == 3

@pytest.mark.asyncio
async def test_error_handling(grading_service, sample_rubric):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock to raise an exception
        mock_create.side_effect = Exception("API Error")
        
        # Test error handling
        with pytest.raises(Exception) as exc_info:
            await grading_service.grade_submission(
                content="Test content",
                rubric=sample_rubric
            )
        
        assert "API Error" in str(exc_info.value) 
