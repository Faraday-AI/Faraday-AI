"""Content Management Service for managing educational content."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)

class ContentManagementService:
    """Service for managing educational content."""
    
    def __init__(self):
        """Initialize the content management service."""
        self.contents = {}
        self.categories = {}
        self.tags = set()
        logger.info("Content Management Service initialized")
    
    async def create_content(self, content_data: Dict[str, Any], creator_id: str) -> str:
        """Create new content."""
        content_id = str(uuid4())
        self.contents[content_id] = {
            "id": content_id,
            "title": content_data.get("title", ""),
            "description": content_data.get("description", ""),
            "content_type": content_data.get("content_type", "general"),
            "content_data": content_data.get("content_data", {}),
            "tags": content_data.get("tags", []),
            "category": content_data.get("category"),
            "difficulty_level": content_data.get("difficulty_level"),
            "target_audience": content_data.get("target_audience", []),
            "metadata": content_data.get("metadata", {}),
            "created_by": creator_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "view_count": 0,
            "rating": None,
            "review_count": 0
        }
        
        # Update tags and categories
        self.tags.update(content_data.get("tags", []))
        if content_data.get("category"):
            self.categories[content_data["category"]] = self.categories.get(content_data["category"], 0) + 1
        
        logger.info(f"Created content: {content_id}")
        return content_id
    
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID."""
        return self.contents.get(content_id)
    
    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update content."""
        if content_id in self.contents:
            self.contents[content_id].update(updates)
            self.contents[content_id]["updated_at"] = datetime.utcnow()
            logger.info(f"Updated content: {content_id}")
            return True
        return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content."""
        if content_id in self.contents:
            del self.contents[content_id]
            logger.info(f"Deleted content: {content_id}")
            return True
        return False
    
    async def search_content(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search content based on parameters."""
        results = []
        query = search_params.get("query", "").lower()
        
        for content in self.contents.values():
            # Simple text search
            if query and query not in content["title"].lower() and query not in content.get("description", "").lower():
                continue
            
            # Filter by content type
            if search_params.get("content_type") and content["content_type"] != search_params["content_type"]:
                continue
            
            # Filter by category
            if search_params.get("category") and content.get("category") != search_params["category"]:
                continue
            
            # Filter by difficulty level
            if search_params.get("difficulty_level") and content.get("difficulty_level") != search_params["difficulty_level"]:
                continue
            
            # Filter by active status
            if search_params.get("is_active") is not None and content["is_active"] != search_params["is_active"]:
                continue
            
            results.append(content)
        
        # Apply limit and offset
        limit = search_params.get("limit", 100)
        offset = search_params.get("offset", 0)
        return results[offset:offset + limit]
    
    async def get_content_statistics(self) -> Dict[str, Any]:
        """Get content statistics."""
        total_content = len(self.contents)
        active_content = len([c for c in self.contents.values() if c["is_active"]])
        total_views = sum(c["view_count"] for c in self.contents.values())
        avg_rating = sum(c["rating"] or 0 for c in self.contents.values() if c["rating"]) / max(1, len([c for c in self.contents.values() if c["rating"]]))
        
        return {
            "total_content": total_content,
            "active_content": active_content,
            "total_views": total_views,
            "average_rating": avg_rating,
            "total_categories": len(self.categories),
            "total_tags": len(self.tags)
        }
    
    async def publish_content(self, content_id: str) -> bool:
        """Publish content."""
        if content_id in self.contents:
            self.contents[content_id]["is_active"] = True
            self.contents[content_id]["published_at"] = datetime.utcnow()
            logger.info(f"Published content: {content_id}")
            return True
        return False
    
    async def duplicate_content(self, content_id: str, creator_id: str) -> Optional[str]:
        """Duplicate content."""
        if content_id in self.contents:
            original = self.contents[content_id]
            new_content_data = {
                "title": f"Copy of {original['title']}",
                "description": original["description"],
                "content_type": original["content_type"],
                "content_data": original["content_data"],
                "tags": original["tags"],
                "category": original["category"],
                "difficulty_level": original["difficulty_level"],
                "target_audience": original["target_audience"],
                "metadata": original["metadata"]
            }
            return await self.create_content(new_content_data, creator_id)
        return None 