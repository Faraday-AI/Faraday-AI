from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.gpt import GPTRole, GPTInteraction
from app.models.user import User
from app.models.memory import UserMemory
from app.schemas.gpt import GPTRoleCreate, GPTRoleUpdate, GPTInteractionCreate

class GPTService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_gpt_roles(self, user_id: str) -> List[GPTRole]:
        """Get all GPT roles for a user."""
        return self.db.query(GPTRole).filter(GPTRole.user_id == user_id).all()

    def get_gpt_role(self, user_id: str, gpt_name: str) -> Optional[GPTRole]:
        """Get a specific GPT role for a user."""
        return self.db.query(GPTRole).filter(
            GPTRole.user_id == user_id,
            GPTRole.gpt_name == gpt_name
        ).first()

    def create_gpt_role(self, user_id: str, gpt_name: str, preferences: Optional[Dict] = None) -> GPTRole:
        """Create a new GPT role for a user."""
        gpt_role = GPTRole(
            user_id=user_id,
            gpt_name=gpt_name,
            preferences=preferences or {},
            created_at=datetime.utcnow()
        )
        self.db.add(gpt_role)
        self.db.commit()
        self.db.refresh(gpt_role)
        return gpt_role

    def update_gpt_role(self, user_id: str, gpt_name: str, preferences: Dict) -> Optional[GPTRole]:
        """Update preferences for a GPT role."""
        gpt_role = self.get_gpt_role(user_id, gpt_name)
        if gpt_role:
            gpt_role.preferences = preferences
            gpt_role.last_accessed = datetime.utcnow()
            self.db.commit()
            self.db.refresh(gpt_role)
        return gpt_role

    def record_interaction(self, user_id: str, gpt_name: str, memory_id: Optional[int] = None,
                         interaction_type: Optional[str] = None, interaction_data: Optional[Dict] = None) -> GPTInteraction:
        """Record an interaction between a user, GPT, and optionally a memory."""
        interaction = GPTInteraction(
            user_id=user_id,
            gpt_name=gpt_name,
            memory_id=memory_id,
            interaction_type=interaction_type,
            interaction_data=interaction_data or {},
            created_at=datetime.utcnow()
        )
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def get_shared_memories(self, user_id: str, gpt_name: str) -> List[UserMemory]:
        """Get memories that are accessible to a specific GPT."""
        return self.db.query(UserMemory).filter(
            UserMemory.user_id == user_id,
            UserMemory.gpt_access.contains([gpt_name])
        ).all()

    def share_memory(self, memory_id: int, gpt_names: List[str]) -> Optional[UserMemory]:
        """Share a memory with specific GPTs."""
        memory = self.db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        if memory:
            current_access = memory.gpt_access or []
            new_access = list(set(current_access + gpt_names))
            memory.gpt_access = new_access
            self.db.commit()
            self.db.refresh(memory)
        return memory

    def get_gpt_interactions(self, user_id: str, gpt_name: Optional[str] = None) -> List[GPTInteraction]:
        """Get interactions for a user, optionally filtered by GPT name."""
        query = self.db.query(GPTInteraction).filter(GPTInteraction.user_id == user_id)
        if gpt_name:
            query = query.filter(GPTInteraction.gpt_name == gpt_name)
        return query.order_by(GPTInteraction.created_at.desc()).all() 