"""
Test AI Assistant System

This module tests the enhanced AI assistant implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime

from app.services.ai.enhanced_assistant_service import EnhancedAssistantService
from app.services.content.content_management_service import ContentManagementService
from app.schemas.content_management import ContentCreate


class TestEnhancedAssistantService:
    """Test enhanced assistant service."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_content_service(self):
        """Mock content management service."""
        return Mock(spec=ContentManagementService)
    
    @pytest.fixture
    def assistant_service(self, mock_db, mock_content_service):
        """Create assistant service instance."""
        return EnhancedAssistantService(mock_db, mock_content_service)
    
    def test_assistant_initialization(self, assistant_service):
        """Test assistant service initialization."""
        assert assistant_service.db is not None
        assert assistant_service.content_service is not None
        assert assistant_service.executor is not None
        assert assistant_service.assistant_config is not None
        assert assistant_service.capabilities is not None
        
        # Check capabilities
        expected_capabilities = [
            "content_generation", "content_optimization", "content_recommendation",
            "content_analysis", "lesson_planning", "assessment_generation",
            "feedback_analysis", "collaboration_support"
        ]
        
        for capability in expected_capabilities:
            assert capability in assistant_service.capabilities
            assert assistant_service.capabilities[capability] is True
    
    @pytest.mark.asyncio
    async def test_generate_content_success(self, assistant_service, mock_content_service):
        """Test successful content generation."""
        # Mock content creation
        mock_content = Mock()
        mock_content.id = 1
        mock_content.title = "AI Generated Content"
        mock_content_service.create_content.return_value = mock_content
        
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "title": "AI Generated Content",
                "content": "This is AI-generated content.",
                "objectives": ["Learn AI content"],
                "materials": ["Computer"],
                "activities": [{"name": "AI Activity", "description": "Description"}],
                "assessment_criteria": {"criteria": "Assessment"},
                "tags": ["ai-generated"]
            }
            '''
            
            result = await assistant_service.generate_content(
                user_id=1,
                content_type="lesson",
                subject="Mathematics",
                grade_level="5th",
                requirements={"difficulty": "intermediate"}
            )
            
            assert result["success"] is True
            assert result["content_id"] == 1
            assert "content" in result
            assert result["generated_at"] is not None
            
            # Verify content service was called
            mock_content_service.create_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_content_failure(self, assistant_service):
        """Test content generation failure."""
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.side_effect = Exception("AI service error")
            
            result = await assistant_service.generate_content(
                user_id=1,
                content_type="lesson",
                subject="Mathematics",
                grade_level="5th",
                requirements={}
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "AI service error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_optimize_content_success(self, assistant_service, mock_content_service):
        """Test successful content optimization."""
        # Mock content retrieval
        mock_content = Mock()
        mock_content.id = 1
        mock_content.title = "Original Title"
        mock_content.content = "Original content"
        mock_content.objectives = ["Original objective"]
        mock_content.materials = ["Original material"]
        mock_content.activities = []
        mock_content_service.get_content_by_id.return_value = mock_content
        
        # Mock content update
        mock_updated_content = Mock()
        mock_updated_content.id = 1
        mock_updated_content.title = "Optimized Title"
        mock_content_service.update_content.return_value = mock_updated_content
        
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "title": "Optimized Title",
                "content": "Optimized content",
                "objectives": ["Optimized objective"],
                "materials": ["Optimized material"],
                "activities": [{"name": "Optimized Activity", "description": "Description"}],
                "assessment_criteria": {"criteria": "Optimized assessment"},
                "tags": ["optimized"]
            }
            '''
            
            result = await assistant_service.optimize_content(
                content_id=1,
                user_id=1,
                optimization_type="engagement"
            )
            
            assert result["success"] is True
            assert result["content_id"] == 1
            assert "optimizations" in result
            assert result["optimized_at"] is not None
            
            # Verify content service calls
            mock_content_service.get_content_by_id.assert_called_once_with(1)
            mock_content_service.update_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recommend_content_success(self, assistant_service, mock_content_service):
        """Test successful content recommendations."""
        # Mock user content
        mock_content1 = Mock()
        mock_content1.id = 1
        mock_content1.title = "Math Lesson"
        
        mock_content2 = Mock()
        mock_content2.id = 2
        mock_content2.title = "Science Lesson"
        
        mock_content_service.get_content_by_user.return_value = [mock_content1, mock_content2]
        
        # Mock content retrieval for recommendations
        mock_content_service.get_content_by_id.side_effect = [mock_content1, mock_content2]
        
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "recommendations": [
                    {
                        "content_id": 1,
                        "reason": "Relevant to user's interests",
                        "relevance_score": 0.95
                    },
                    {
                        "content_id": 2,
                        "reason": "Similar to user's content",
                        "relevance_score": 0.85
                    }
                ]
            }
            '''
            
            recommendations = await assistant_service.recommend_content(
                user_id=1,
                context={"subject": "Mathematics", "grade_level": "5th"},
                limit=5
            )
            
            assert len(recommendations) == 2
            assert recommendations[0]["content"].id == 1
            assert recommendations[0]["reason"] == "Relevant to user's interests"
            assert recommendations[0]["relevance_score"] == 0.95
    
    @pytest.mark.asyncio
    async def test_analyze_content_performance_success(self, assistant_service, mock_content_service):
        """Test successful content performance analysis."""
        # Mock content retrieval
        mock_content = Mock()
        mock_content.id = 1
        mock_content.title = "Test Content"
        mock_content_service.get_content_by_id.return_value = mock_content
        
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "performance_score": 0.85,
                "strengths": ["Clear objectives", "Engaging content"],
                "weaknesses": ["Could use more examples"],
                "recommendations": ["Add more examples", "Include interactive elements"],
                "trends": "Performance is improving over time"
            }
            '''
            
            result = await assistant_service.analyze_content_performance(
                content_id=1,
                metrics={"engagement": 0.8, "completion_rate": 0.9}
            )
            
            assert result["success"] is True
            assert result["content_id"] == 1
            assert "analysis" in result
            assert result["analysis"]["performance_score"] == 0.85
            assert len(result["analysis"]["strengths"]) == 2
            assert len(result["analysis"]["weaknesses"]) == 1
            assert len(result["analysis"]["recommendations"]) == 2
    
    @pytest.mark.asyncio
    async def test_generate_lesson_plan_success(self, assistant_service, mock_content_service):
        """Test successful lesson plan generation."""
        # Mock content creation
        mock_content = Mock()
        mock_content.id = 1
        mock_content.title = "AI Generated Lesson Plan"
        mock_content_service.create_content.return_value = mock_content
        
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "title": "AI Generated Lesson Plan",
                "content": "This is a comprehensive lesson plan.",
                "materials": ["Computer", "Projector"],
                "activities": [{"name": "Introduction", "description": "Introduction activity", "duration": "10 min"}],
                "assessment_criteria": {"criteria": "Lesson assessment"},
                "tags": ["lesson-plan", "mathematics"]
            }
            '''
            
            result = await assistant_service.generate_lesson_plan(
                user_id=1,
                subject="Mathematics",
                grade_level="5th",
                duration="60 minutes",
                objectives=["Learn basic algebra", "Solve equations"]
            )
            
            assert result["success"] is True
            assert result["lesson_plan_id"] == 1
            assert "lesson_plan" in result
            assert result["generated_at"] is not None
    
    @pytest.mark.asyncio
    async def test_generate_assessment_success(self, assistant_service, mock_content_service):
        """Test successful assessment generation."""
        # Mock content retrieval
        mock_content = Mock()
        mock_content.id = 1
        mock_content.title = "Math Lesson"
        mock_content.subject_category_id = 1
        mock_content.grade_level = "5th"
        mock_content_service.get_content_by_id.return_value = mock_content
        
        # Mock assessment content creation
        mock_assessment = Mock()
        mock_assessment.id = 2
        mock_assessment.title = "Assessment: Math Lesson"
        mock_content_service.create_content.return_value = mock_assessment
        
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "questions": [
                    {
                        "question": "What is 2 + 2?",
                        "type": "multiple_choice",
                        "options": ["3", "4", "5", "6"],
                        "correct_answer": "4",
                        "explanation": "Basic addition"
                    }
                ],
                "criteria": {"criteria": "Assessment criteria"},
                "tags": ["assessment", "mathematics"]
            }
            '''
            
            result = await assistant_service.generate_assessment(
                user_id=1,
                content_id=1,
                assessment_type="quiz",
                difficulty="easy",
                num_questions=5
            )
            
            assert result["success"] is True
            assert result["assessment_id"] == 2
            assert "assessment" in result
            assert len(result["assessment"]["questions"]) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_feedback_success(self, assistant_service):
        """Test successful feedback analysis."""
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "sentiment": "positive",
                "key_themes": ["Engagement", "Clarity"],
                "action_items": ["Add more examples", "Improve explanations"],
                "overall_score": 0.85
            }
            '''
            
            feedback_data = [
                {"user_id": 1, "rating": 5, "comment": "Great lesson!"},
                {"user_id": 2, "rating": 4, "comment": "Good content, could use more examples"}
            ]
            
            result = await assistant_service.analyze_feedback(feedback_data)
            
            assert result["success"] is True
            assert "analysis" in result
            assert result["analysis"]["sentiment"] == "positive"
            assert len(result["analysis"]["key_themes"]) == 2
            assert len(result["analysis"]["action_items"]) == 2
            assert result["analysis"]["overall_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_support_collaboration_success(self, assistant_service):
        """Test successful collaboration support."""
        # Mock AI response
        with patch.object(assistant_service, '_get_ai_response') as mock_ai_response:
            mock_ai_response.return_value = '''
            {
                "suggestions": [
                    {
                        "type": "communication",
                        "suggestion": "Use regular team meetings",
                        "priority": "high"
                    }
                ],
                "best_practices": ["Clear communication", "Regular updates"],
                "tools": ["Slack", "Trello"]
            }
            '''
            
            result = await assistant_service.support_collaboration(
                user_id=1,
                team_id=1,
                collaboration_type="content_creation",
                context={"team_size": 5, "project_type": "curriculum_development"}
            )
            
            assert result["success"] is True
            assert "suggestions" in result
            assert len(result["suggestions"]) == 1
            assert result["suggestions"][0]["type"] == "communication"
            assert "best_practices" in result
            assert "tools" in result
    
    def test_build_content_generation_prompt(self, assistant_service):
        """Test content generation prompt building."""
        prompt = assistant_service._build_content_generation_prompt(
            content_type="lesson",
            subject="Mathematics",
            grade_level="5th",
            requirements={"difficulty": "intermediate", "duration": "45 minutes"}
        )
        
        assert "Generate lesson content" in prompt
        assert "Mathematics" in prompt
        assert "5th" in prompt
        assert "intermediate" in prompt
        assert "45 minutes" in prompt
        assert "JSON" in prompt
    
    def test_build_optimization_prompt(self, assistant_service):
        """Test optimization prompt building."""
        mock_content = Mock()
        mock_content.title = "Test Content"
        mock_content.content = "Test content"
        mock_content.objectives = ["Test objective"]
        mock_content.materials = ["Test material"]
        mock_content.activities = []
        
        prompt = assistant_service._build_optimization_prompt(
            content=mock_content,
            optimization_type="engagement"
        )
        
        assert "Optimize the following content" in prompt
        assert "engagement" in prompt
        assert "Test Content" in prompt
        assert "Test content" in prompt
        assert "JSON format" in prompt
    
    def test_parse_content_response_success(self, assistant_service):
        """Test successful content response parsing."""
        ai_response = '''
        {
            "title": "Test Content",
            "content": "Test content",
            "objectives": ["Objective 1"],
            "materials": ["Material 1"],
            "activities": [{"name": "Activity 1", "description": "Description"}],
            "assessment_criteria": {"criteria": "Assessment"},
            "tags": ["test"]
        }
        '''
        
        result = assistant_service._parse_content_response(ai_response, "lesson")
        
        assert result["title"] == "Test Content"
        assert result["content"] == "Test content"
        assert result["objectives"] == ["Objective 1"]
        assert result["materials"] == ["Material 1"]
        assert len(result["activities"]) == 1
        assert result["activities"][0]["name"] == "Activity 1"
        assert result["tags"] == ["test"]
    
    def test_parse_content_response_failure(self, assistant_service):
        """Test content response parsing failure."""
        ai_response = "Invalid JSON response"
        
        result = assistant_service._parse_content_response(ai_response, "lesson")
        
        assert result["title"] == "Generated lesson"
        assert result["content"] == "Invalid JSON response"
        assert result["objectives"] == []
        assert result["materials"] == []
        assert result["activities"] == []
        assert result["tags"] == ["lesson"]
    
    @pytest.mark.asyncio
    async def test_get_ai_response_mock(self, assistant_service):
        """Test AI response generation (mock implementation)."""
        prompt = "Generate test content"
        
        response = await assistant_service._get_ai_response(prompt)
        
        assert response is not None
        assert "title" in response
        assert "content" in response
        assert "objectives" in response
        assert "materials" in response
        assert "activities" in response
        assert "assessment_criteria" in response
        assert "tags" in response


class TestAIAssistantSchemas:
    """Test AI assistant request/response schemas."""
    
    def test_content_generation_request_schema(self):
        """Test ContentGenerationRequest schema."""
        from app.api.v1.endpoints.ai_assistant import ContentGenerationRequest
        
        request = ContentGenerationRequest(
            content_type="lesson",
            subject="Mathematics",
            grade_level="5th",
            requirements={"difficulty": "intermediate", "duration": "45 minutes"}
        )
        
        assert request.content_type == "lesson"
        assert request.subject == "Mathematics"
        assert request.grade_level == "5th"
        assert request.requirements["difficulty"] == "intermediate"
        assert request.requirements["duration"] == "45 minutes"
    
    def test_lesson_plan_request_schema(self):
        """Test LessonPlanRequest schema."""
        from app.api.v1.endpoints.ai_assistant import LessonPlanRequest
        
        request = LessonPlanRequest(
            subject="Science",
            grade_level="6th",
            duration="60 minutes",
            objectives=["Learn about ecosystems", "Understand food chains"]
        )
        
        assert request.subject == "Science"
        assert request.grade_level == "6th"
        assert request.duration == "60 minutes"
        assert len(request.objectives) == 2
        assert "ecosystems" in request.objectives[0]
        assert "food chains" in request.objectives[1]
    
    def test_assessment_request_schema(self):
        """Test AssessmentRequest schema."""
        from app.api.v1.endpoints.ai_assistant import AssessmentRequest
        
        request = AssessmentRequest(
            content_id=1,
            assessment_type="quiz",
            difficulty="medium",
            num_questions=10
        )
        
        assert request.content_id == 1
        assert request.assessment_type == "quiz"
        assert request.difficulty == "medium"
        assert request.num_questions == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 