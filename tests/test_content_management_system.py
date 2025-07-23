"""
Test Content Management System

This module tests the content management implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

from app.schemas.content_management import ContentCreate, ContentUpdate, ContentSearch, ContentFilter


class TestContentManagementService:
    """Test content management service."""
    
    def test_get_content_by_id_nonexistent(self):
        """Test getting non-existent content by ID."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.content.content_management_service.Lesson') as mock_lesson:
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            content = service.get_content_by_id(1)
            
            assert content is None
            mock_db.query.assert_called_once_with(mock_lesson)
    
    def test_create_content_success(self):
        """Test creating content successfully."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        mock_content_instance = Mock()
        mock_content_instance.id = 1
        mock_content_instance.title = "Test Lesson"
        mock_content_instance.status = "draft"
        mock_content_instance.version = 1
        
        with patch('app.services.content.content_management_service.Lesson') as mock_lesson:
            mock_lesson.return_value = mock_content_instance
            
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            content_data = ContentCreate(
                title="Test Lesson",
                subject_category_id=1,
                grade_level="5th",
                content="This is a test lesson content.",
                objectives=["Learn about testing"],
                materials=["Computer", "Internet"],
                tags=["test", "lesson"]
            )
            
            content = service.create_content(content_data, 1)
            
            assert content.id == 1
            assert content.title == "Test Lesson"
            assert content.status == "draft"
            assert content.version == 1
            
            mock_db.add.assert_called_once_with(mock_content_instance)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_content_instance)
    
    def test_create_content_already_exists(self):
        """Test creating content when it already exists."""
        mock_existing_content = Mock()
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_content
        mock_db.query.return_value = mock_query
        
        with patch('app.services.content.content_management_service.Lesson'):
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            content_data = ContentCreate(
                title="Existing Lesson",
                subject_category_id=1
            )
            
            with pytest.raises(Exception):
                service.create_content(content_data, 1)
    
    def test_update_content_success(self):
        """Test updating content successfully."""
        mock_content = Mock()
        mock_content.id = 1
        mock_content.user_id = 1
        mock_content.title = "Original Title"
        mock_content.status = "draft"
        mock_content.version = 1
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_content
        
        with patch('app.services.content.content_management_service.Lesson'):
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            content_data = ContentUpdate(
                title="Updated Title",
                status="published"
            )
            
            content = service.update_content(1, content_data, 1)
            
            assert content.title == "Updated Title"
            assert content.status == "published"
            assert content.version == 2  # Version should increment for published content
            
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_content)
    
    def test_publish_content_success(self):
        """Test publishing content successfully."""
        mock_content = Mock()
        mock_content.id = 1
        mock_content.user_id = 1
        mock_content.status = "draft"
        mock_content.version = 1
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_content
        
        with patch('app.services.content.content_management_service.Lesson'):
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            content = service.publish_content(1, 1)
            
            assert content.status == "published"
            assert content.version == 2
            
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_content)
    
    def test_duplicate_content_success(self):
        """Test duplicating content successfully."""
        mock_original_content = Mock()
        mock_original_content.id = 1
        mock_original_content.title = "Original Lesson"
        mock_original_content.subject_category_id = 1
        mock_original_content.grade_level = "5th"
        mock_original_content.content = "Original content"
        mock_original_content.objectives = ["Learn something"]
        mock_original_content.materials = ["Materials"]
        mock_original_content.tags = ["tag1"]
        mock_original_content.related_lessons = []
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_original_content
        
        mock_new_content = Mock()
        mock_new_content.id = 2
        mock_new_content.title = "Copy of Original Lesson"
        mock_new_content.status = "draft"
        mock_new_content.version = 1
        
        with patch('app.services.content.content_management_service.Lesson') as mock_lesson:
            mock_lesson.return_value = mock_new_content
            
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            content = service.duplicate_content(1, 1, "Copy of Original Lesson")
            
            assert content.id == 2
            assert content.title == "Copy of Original Lesson"
            assert content.status == "draft"
            assert content.version == 1
            
            mock_db.add.assert_called_once_with(mock_new_content)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_new_content)
    
    def test_search_content(self):
        """Test searching content."""
        mock_content1 = Mock()
        mock_content1.id = 1
        mock_content1.title = "Math Lesson"
        
        mock_content2 = Mock()
        mock_content2.id = 2
        mock_content2.title = "Science Lesson"
        
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.limit.return_value.all.return_value = [mock_content1, mock_content2]
        mock_db.query.return_value = mock_query
        
        with patch('app.services.content.content_management_service.Lesson'):
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            results = service.search_content("lesson", 1, 10)
            
            assert len(results) == 2
            assert results[0].id == 1
            assert results[1].id == 2
    
    def test_get_content_statistics(self):
        """Test getting content statistics."""
        mock_content1 = Mock()
        mock_content1.status = "published"
        mock_content1.version = 2
        mock_content1.subject_category_id = 1
        
        mock_content2 = Mock()
        mock_content2.status = "draft"
        mock_content2.version = 1
        mock_content2.subject_category_id = 1
        
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 2
        mock_query.filter.return_value.filter.return_value.count.side_effect = [1, 1, 0]
        mock_query.filter.return_value.all.return_value = [mock_content1, mock_content2]
        mock_db.query.return_value = mock_query
        
        with patch('app.services.content.content_management_service.Lesson'):
            from app.services.content.content_management_service import ContentManagementService
            
            service = ContentManagementService(mock_db)
            
            stats = service.get_content_statistics(1)
            
            assert stats["total_content"] == 2
            assert stats["published_content"] == 1
            assert stats["draft_content"] == 1
            assert stats["archived_content"] == 0
            assert stats["average_version"] == 1.5


class TestContentSchemas:
    """Test content schemas."""
    
    def test_content_create_schema(self):
        """Test ContentCreate schema."""
        content_data = ContentCreate(
            title="Test Lesson",
            subject_category_id=1,
            grade_level="5th",
            content="This is a test lesson content.",
            objectives=["Learn about testing"],
            materials=["Computer", "Internet"],
            tags=["test", "lesson"],
            status="draft"
        )
        
        assert content_data.title == "Test Lesson"
        assert content_data.subject_category_id == 1
        assert content_data.grade_level == "5th"
        assert content_data.content == "This is a test lesson content."
        assert content_data.objectives == ["Learn about testing"]
        assert content_data.materials == ["Computer", "Internet"]
        assert content_data.tags == ["test", "lesson"]
        assert content_data.status == "draft"
    
    def test_content_update_schema(self):
        """Test ContentUpdate schema."""
        content_data = ContentUpdate(
            title="Updated Lesson",
            status="published"
        )
        
        assert content_data.title == "Updated Lesson"
        assert content_data.status == "published"
        assert content_data.subject_category_id is None  # Not set
    
    def test_content_search_schema(self):
        """Test ContentSearch schema."""
        search_data = ContentSearch(
            query="math lesson",
            user_id=1,
            status="published",
            subject_category_id=1,
            grade_level="5th",
            tags=["math"],
            limit=20
        )
        
        assert search_data.query == "math lesson"
        assert search_data.user_id == 1
        assert search_data.status == "published"
        assert search_data.subject_category_id == 1
        assert search_data.grade_level == "5th"
        assert search_data.tags == ["math"]
        assert search_data.limit == 20
    
    def test_content_filter_schema(self):
        """Test ContentFilter schema."""
        filter_data = ContentFilter(
            user_id=1,
            status="published",
            subject_category_id=1,
            grade_level="5th",
            content_area="Mathematics",
            tags=["math", "algebra"],
            created_after=datetime(2024, 1, 1),
            created_before=datetime(2024, 12, 31),
            sort_by="created_at",
            limit=50
        )
        
        assert filter_data.user_id == 1
        assert filter_data.status == "published"
        assert filter_data.subject_category_id == 1
        assert filter_data.grade_level == "5th"
        assert filter_data.content_area == "Mathematics"
        assert filter_data.tags == ["math", "algebra"]
        assert filter_data.sort_by == "created_at"
        assert filter_data.limit == 50


class TestContentAPIEndpoints:
    """Test content API endpoints."""
    
    def test_get_all_content_endpoint(self):
        """Test get all content endpoint."""
        # This would test the actual API endpoint
        # For now, we'll test the schema validation
        from app.schemas.content_management import ContentResponse
        
        content_response = ContentResponse(
            id=1,
            title="Test Lesson",
            user_id=1,
            subject_category_id=1,
            assistant_profile_id=None,
            grade_level="5th",
            week_of=date(2024, 1, 1),
            content_area="Mathematics",
            content="Test content",
            lesson_data={},
            objectives=["Learn math"],
            materials=["Calculator"],
            activities=[],
            assessment_criteria={},
            feedback={},
            status="published",
            version=1,
            tags=["math"],
            related_lessons=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert content_response.id == 1
        assert content_response.title == "Test Lesson"
        assert content_response.status == "published"
        assert content_response.version == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 