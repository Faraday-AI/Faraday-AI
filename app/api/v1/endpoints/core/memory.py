from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.dashboard.models import DashboardUser as User
from app.models.memory import UserMemory, MemoryInteraction, UserMemoryResponse, MemoryInteractionResponse
from pydantic import BaseModel

router = APIRouter()

class MemoryCreate(BaseModel):
    content: str
    category: str
    context: Optional[dict] = None
    importance: Optional[float] = 1.0
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    confidence: Optional[float] = None

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    importance: Optional[float] = None
    context: Optional[dict] = None
    tags: Optional[List[str]] = None

class MemoryInteractionCreate(BaseModel):
    interaction_type: str
    context: Optional[dict] = None
    feedback: Optional[dict] = None

@router.post("/memories", response_model=UserMemoryResponse)
async def create_memory(
    memory: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new memory for the current user."""
    memory_service = MemoryService(db)
    return await memory_service.create_memory(
        user_id=current_user.id,
        assistant_id=1,  # TODO: Get from request context
        content=memory.content,
        category=memory.category,
        context=memory.context,
        importance=memory.importance,
        tags=memory.tags,
        source=memory.source,
        confidence=memory.confidence
    )

@router.get("/memories", response_model=List[UserMemoryResponse])
async def get_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get memories for the current user with optional filtering."""
    memory_service = MemoryService(db)
    return await memory_service.get_memories(
        user_id=current_user.id,
        category=category,
        tags=tags,
        limit=limit,
        offset=offset
    )

@router.get("/memories/{memory_id}", response_model=UserMemoryResponse)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific memory by ID."""
    memory_service = MemoryService(db)
    memory = await memory_service.get_memory(memory_id, current_user.id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.put("/memories/{memory_id}", response_model=UserMemoryResponse)
async def update_memory(
    memory_id: int,
    memory_update: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific memory."""
    memory_service = MemoryService(db)
    memory = await memory_service.update_memory(
        memory_id=memory_id,
        user_id=current_user.id,
        **memory_update.dict(exclude_unset=True)
    )
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific memory."""
    memory_service = MemoryService(db)
    success = await memory_service.delete_memory(memory_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}

@router.post("/memories/{memory_id}/interactions", response_model=MemoryInteractionResponse)
async def create_memory_interaction(
    memory_id: int,
    interaction: MemoryInteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record an interaction with a memory."""
    memory_service = MemoryService(db)
    return await memory_service.create_interaction(
        memory_id=memory_id,
        user_id=current_user.id,
        interaction_type=interaction.interaction_type,
        context=interaction.context,
        feedback=interaction.feedback
    )

@router.get("/memories/{memory_id}/interactions", response_model=List[MemoryInteractionResponse])
async def get_memory_interactions(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all interactions for a specific memory."""
    memory_service = MemoryService(db)
    return await memory_service.get_interactions(memory_id, current_user.id) 