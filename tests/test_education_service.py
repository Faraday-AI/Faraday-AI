import pytest
from unittest.mock import AsyncMock, patch
from app.services.education_service import EducationService
import json

@pytest.fixture
def education_service():
    return EducationService()

@pytest.fixture
def sample_learning_objectives():
    return [
        "Understand basic algebraic concepts",
        "Solve linear equations",
        "Apply mathematical principles to real-world problems"
    ]

@pytest.fixture
def sample_learning_standards():
    return [
        "CCSS.MATH.CONTENT.8.EE.A.1",
        "CCSS.MATH.CONTENT.8.EE.A.2",
        "CCSS.MATH.CONTENT.8.EE.A.3"
    ]

@pytest.fixture
def sample_student_profiles():
    return [
        {
            "name": "Student 1",
            "learning_style": "visual",
            "needs": ["extra time", "visual aids"],
            "strengths": ["problem-solving", "creativity"]
        },
        {
            "name": "Student 2",
            "learning_style": "auditory",
            "needs": ["verbal instructions", "repetition"],
            "strengths": ["listening", "verbal communication"]
        }
    ]

@pytest.fixture
def sample_student_data():
    return {
        "assignments": [
            {"name": "Quiz 1", "score": 85, "date": "2024-01-01"},
            {"name": "Quiz 2", "score": 92, "date": "2024-01-15"},
            {"name": "Final", "score": 88, "date": "2024-02-01"}
        ],
        "attendance": 0.95,
        "participation": 0.8
    }

@pytest.fixture
def mock_openai_response():
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "lesson_title": "Introduction to Algebra",
                    "materials_needed": ["textbook", "worksheet"],
                    "prerequisites": ["basic arithmetic"],
                    "lesson_steps": [
                        {"step": "Introduction", "description": "Review basic concepts"},
                        {"step": "Main Activity", "description": "Practice problems"}
                    ],
                    "assessment_methods": ["quiz", "homework"],
                    "extension_activities": ["real-world applications"],
                    "differentiation_strategies": ["visual aids", "group work"]
                })
            }
        }]
    }

@pytest.mark.asyncio
async def test_create_lesson_plan(education_service, sample_learning_objectives, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test lesson plan creation
        result = await education_service.create_lesson_plan(
            subject="Mathematics",
            grade_level="8th Grade",
            topic="Introduction to Algebra",
            duration="45 minutes",
            learning_objectives=sample_learning_objectives
        )
        
        # Verify result structure
        assert "lesson_title" in result
        assert "materials_needed" in result
        assert "lesson_steps" in result
        assert "assessment_methods" in result
        assert "created_at" in result
        assert "subject" in result
        assert "grade_level" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "curriculum designer" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_generate_assessment_questions(education_service, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test assessment generation
        result = await education_service.generate_assessment_questions(
            subject="Mathematics",
            topic="Linear Equations",
            difficulty="medium",
            question_type="multiple_choice",
            num_questions=5
        )
        
        # Verify result structure
        assert "questions" in result
        assert "answer_key" in result
        assert "explanations" in result
        assert "learning_objectives_covered" in result
        assert "created_at" in result
        assert "subject" in result
        assert "topic" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "assessment designer" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_analyze_student_progress(education_service, sample_student_data, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test progress analysis
        result = await education_service.analyze_student_progress(
            student_data=sample_student_data,
            subject="Mathematics",
            time_period="semester"
        )
        
        # Verify result structure
        assert "overall_progress" in result
        assert "strengths" in result
        assert "areas_for_improvement" in result
        assert "recommendations" in result
        assert "analyzed_at" in result
        assert "subject" in result
        assert "time_period" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "educational analyst" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_create_curriculum_outline(education_service, sample_learning_standards, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test curriculum outline creation
        result = await education_service.create_curriculum_outline(
            subject="Mathematics",
            grade_level="8th Grade",
            duration="semester",
            learning_standards=sample_learning_standards
        )
        
        # Verify result structure
        assert "course_overview" in result
        assert "units" in result
        assert "learning_sequence" in result
        assert "assessment_strategies" in result
        assert "resources" in result
        assert "timeline" in result
        assert "created_at" in result
        assert "subject" in result
        assert "grade_level" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "curriculum designer" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_generate_differentiated_instruction(education_service, sample_student_profiles, mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock
        mock_create.return_value = mock_openai_response
        
        # Test differentiated instruction generation
        result = await education_service.generate_differentiated_instruction(
            lesson_content="Introduction to Algebra",
            student_profiles=sample_student_profiles
        )
        
        # Verify result structure
        assert "strategies" in result
        assert "accommodations" in result
        assert "modifications" in result
        assert "enrichment_activities" in result
        assert "support_resources" in result
        assert "created_at" in result
        assert "num_students" in result
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert "differentiated instruction" in call_args["messages"][0]["content"]

@pytest.mark.asyncio
async def test_error_handling(education_service, sample_learning_objectives):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        # Setup mock to raise an exception
        mock_create.side_effect = Exception("API Error")
        
        # Test error handling
        with pytest.raises(Exception) as exc_info:
            await education_service.create_lesson_plan(
                subject="Mathematics",
                grade_level="8th Grade",
                topic="Algebra",
                duration="45 minutes",
                learning_objectives=sample_learning_objectives
            )
        
        assert "API Error" in str(exc_info.value) 
