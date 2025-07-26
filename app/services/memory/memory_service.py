from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.sql import text
from app.dashboard.models import DashboardUser as User
from app.models.memory import SimpleUserMemory, SimpleMemoryInteraction
from app.models.core.assistant import AssistantProfile
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing user memories and interactions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        
    async def create_memory(
        self,
        user_id: int,
        assistant_id: int,
        content: str,
        category: str,
        context: Dict[str, Any] = None,
        importance: float = 1.0,
        tags: List[str] = None,
        source: str = None,
        confidence: float = None
    ) -> SimpleUserMemory:
        """Create a new memory for a user."""
        try:
            memory = SimpleUserMemory(
                user_id=user_id,
                assistant_profile_id=assistant_id,
                content=content,
                category=category,
                context=context or {},
                importance=importance,
                tags=tags or [],
                source=source,
                confidence=confidence,
                last_accessed=datetime.utcnow()
            )
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            return memory
        except Exception as e:
            logger.error(f"Error creating memory: {str(e)}")
            self.db.rollback()
            raise
            
    async def get_relevant_memories(
        self,
        user_id: int,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.5
    ) -> List[SimpleUserMemory]:
        """Retrieve relevant memories based on query and filters."""
        try:
            query = self.db.query(SimpleUserMemory).filter(
                SimpleUserMemory.user_id == user_id,
                SimpleUserMemory.importance >= min_importance
            )
            
            if category:
                query = query.filter(SimpleUserMemory.category == category)
                
            # Update last_accessed for retrieved memories
            memories = query.order_by(SimpleUserMemory.importance.desc()).limit(limit).all()
            for memory in memories:
                memory.last_accessed = datetime.utcnow()
                
            self.db.commit()
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            self.db.rollback()
            raise
            
    async def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        importance: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> SimpleUserMemory:
        """Update an existing memory."""
        try:
            memory = self.db.query(SimpleUserMemory).filter(SimpleUserMemory.id == memory_id).first()
            if not memory:
                raise ValueError(f"Memory with id {memory_id} not found")
                
            if content is not None:
                memory.content = content
            if importance is not None:
                memory.importance = importance
            if context is not None:
                memory.context = context
            if tags is not None:
                memory.tags = tags
                
            memory.last_accessed = datetime.utcnow()
            self.db.commit()
            self.db.refresh(memory)
            return memory
        except Exception as e:
            logger.error(f"Error updating memory: {str(e)}")
            self.db.rollback()
            raise
            
    async def record_interaction(
        self,
        memory_id: int,
        user_id: int,
        interaction_type: str,
        context: Dict[str, Any] = None,
        feedback: Dict[str, Any] = None
    ) -> SimpleMemoryInteraction:
        """Record a memory interaction."""
        try:
            # Combine context and feedback into interaction_metadata
            interaction_metadata = {}
            if context:
                interaction_metadata['context'] = context
            if feedback:
                interaction_metadata['feedback'] = feedback
                
            interaction = SimpleMemoryInteraction(
                memory_id=memory_id,
                user_id=user_id,
                interaction_type=interaction_type,
                interaction_metadata=interaction_metadata
            )
            self.db.add(interaction)
            self.db.commit()
            self.db.refresh(interaction)
            return interaction
        except Exception as e:
            logger.error(f"Error recording memory interaction: {str(e)}")
            self.db.rollback()
            raise
            
    async def get_memory_history(
        self,
        user_id: int,
        memory_id: Optional[int] = None,
        limit: int = 50
    ) -> List[SimpleMemoryInteraction]:
        """Get history of memory interactions."""
        try:
            query = self.db.query(SimpleMemoryInteraction).filter(
                SimpleMemoryInteraction.user_id == user_id
            )
            
            if memory_id:
                query = query.filter(SimpleMemoryInteraction.memory_id == memory_id)
                
            return query.order_by(SimpleMemoryInteraction.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving memory history: {str(e)}")
            raise
            
    async def get_memories(
        self,
        user_id: int,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SimpleUserMemory]:
        """Get memories for a user with optional filtering."""
        try:
            query = self.db.query(SimpleUserMemory).filter(
                SimpleUserMemory.user_id == user_id
            )
            
            if category:
                query = query.filter(SimpleUserMemory.category == category)
                
            if tags:
                # Filter by tags (assuming tags is a JSON array)
                for tag in tags:
                    query = query.filter(SimpleUserMemory.tags.contains([tag]))
                    
            return query.order_by(SimpleUserMemory.importance.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            raise
            
    async def get_memory(
        self,
        memory_id: int,
        user_id: int
    ) -> Optional[SimpleUserMemory]:
        """Get a specific memory by ID for a user."""
        try:
            memory = self.db.query(SimpleUserMemory).filter(
                SimpleUserMemory.id == memory_id,
                SimpleUserMemory.user_id == user_id
            ).first()
            
            if memory:
                memory.last_accessed = datetime.utcnow()
                self.db.commit()
                
            return memory
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            raise
            
    async def delete_memory(
        self,
        memory_id: int,
        user_id: int
    ) -> bool:
        """Delete a memory for a user."""
        try:
            memory = self.db.query(SimpleUserMemory).filter(
                SimpleUserMemory.id == memory_id,
                SimpleUserMemory.user_id == user_id
            ).first()
            
            if not memory:
                return False
                
            self.db.delete(memory)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            self.db.rollback()
            raise 