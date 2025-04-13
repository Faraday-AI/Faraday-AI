from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import User, LearningProgress, Memory
from app.database.database import get_db

logger = logging.getLogger(__name__)

class MemoryRecallService:
    def __init__(self, db: Session):
        self.db = db

    async def store_interaction(
        self,
        user_id: str,
        interaction_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store a user interaction in memory."""
        try:
            memory = Memory(
                user_id=user_id,
                interaction_type=interaction_type,
                content=content,
                user_metadata=metadata or {},
                timestamp=datetime.utcnow()
            )
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            return {"status": "success", "memory_id": memory.id}
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)}

    async def get_recent_interactions(
        self,
        user_id: str,
        limit: int = 10,
        interaction_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve recent user interactions."""
        try:
            query = self.db.query(Memory).filter(Memory.user_id == user_id)
            if interaction_type:
                query = query.filter(Memory.interaction_type == interaction_type)
            
            memories = query.order_by(Memory.timestamp.desc()).limit(limit).all()
            return [
                {
                    "id": memory.id,
                    "interaction_type": memory.interaction_type,
                    "content": memory.content,
                    "metadata": memory.user_metadata,
                    "timestamp": memory.timestamp
                }
                for memory in memories
            ]
        except Exception as e:
            logger.error(f"Error retrieving interactions: {str(e)}")
            return []

    async def update_learning_progress(
        self,
        user_id: str,
        topic: str,
        progress: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user's learning progress for a topic."""
        try:
            progress_entry = self.db.query(LearningProgress).filter(
                LearningProgress.user_id == user_id,
                LearningProgress.topic == topic
            ).first()

            if progress_entry:
                progress_entry.progress = progress
                progress_entry.user_metadata = metadata or progress_entry.user_metadata
                progress_entry.last_updated = datetime.utcnow()
            else:
                progress_entry = LearningProgress(
                    user_id=user_id,
                    topic=topic,
                    progress=progress,
                    user_metadata=metadata or {},
                    last_updated=datetime.utcnow()
                )
                self.db.add(progress_entry)

            self.db.commit()
            self.db.refresh(progress_entry)
            return {
                "status": "success",
                "progress": progress_entry.progress,
                "metadata": progress_entry.user_metadata
            }
        except Exception as e:
            logger.error(f"Error updating learning progress: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)}

    async def get_learning_progress(
        self,
        user_id: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's learning progress."""
        try:
            query = self.db.query(LearningProgress).filter(
                LearningProgress.user_id == user_id
            )
            if topic:
                query = query.filter(LearningProgress.topic == topic)

            progress_records = query.all()
            return {
                "status": "success",
                "progress": [
                    {
                        "topic": record.topic,
                        "progress": record.progress,
                        "metadata": record.user_metadata,
                        "last_updated": record.last_updated.isoformat()
                    }
                    for record in progress_records
                ]
            }
        except Exception as e:
            logger.error(f"Error retrieving learning progress: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_user_context(
        self,
        user_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get comprehensive user context including recent interactions and progress."""
        try:
            recent_interactions = await self.get_recent_interactions(user_id, limit)
            learning_progress = await self.get_learning_progress(user_id)
            
            return {
                "status": "success",
                "recent_interactions": recent_interactions,
                "learning_progress": learning_progress.get("progress", []),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def clear_user_memory(
        self,
        user_id: str,
        before_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Clear user's memory records, optionally before a specific date."""
        try:
            query = self.db.query(Memory).filter(Memory.user_id == user_id)
            if before_date:
                query = query.filter(Memory.timestamp < before_date)
            
            deleted_count = query.delete()
            self.db.commit()
            return {"status": "success", "deleted_count": deleted_count}
        except Exception as e:
            logger.error(f"Error clearing user memory: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)} 
