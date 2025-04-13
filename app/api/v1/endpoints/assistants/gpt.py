from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.gpt import (
    GPTRoleCreate,
    GPTRoleUpdate,
    GPTRoleInDB,
    GPTInteractionCreate,
    GPTInteractionInDB,
    MemoryShare,
    GPTMemoryAccess
)
from app.services.gpt_service import GPTService

router = APIRouter()

@router.get("/roles", response_model=List[GPTRoleInDB])
def get_user_gpt_roles(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Get all GPT roles for the current user."""
    gpt_service = GPTService(db)
    return gpt_service.get_user_gpt_roles(current_user.id)

@router.post("/roles", response_model=GPTRoleInDB)
def create_gpt_role(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    gpt_role_in: GPTRoleCreate
):
    """Create a new GPT role for the current user."""
    gpt_service = GPTService(db)
    return gpt_service.create_gpt_role(
        user_id=current_user.id,
        gpt_name=gpt_role_in.gpt_name,
        preferences=gpt_role_in.preferences
    )

@router.put("/roles/{gpt_name}", response_model=GPTRoleInDB)
def update_gpt_role(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    gpt_name: str,
    gpt_role_in: GPTRoleUpdate
):
    """Update preferences for a GPT role."""
    gpt_service = GPTService(db)
    gpt_role = gpt_service.update_gpt_role(
        user_id=current_user.id,
        gpt_name=gpt_name,
        preferences=gpt_role_in.preferences
    )
    if not gpt_role:
        raise HTTPException(status_code=404, detail="GPT role not found")
    return gpt_role

@router.post("/interactions", response_model=GPTInteractionInDB)
def create_interaction(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    interaction_in: GPTInteractionCreate
):
    """Record a GPT interaction."""
    gpt_service = GPTService(db)
    return gpt_service.record_interaction(
        user_id=current_user.id,
        gpt_name=interaction_in.gpt_name,
        memory_id=interaction_in.memory_id,
        interaction_type=interaction_in.interaction_type,
        interaction_data=interaction_in.interaction_data
    )

@router.post("/memories/share", response_model=GPTMemoryAccess)
def share_memory(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    memory_share: MemoryShare
):
    """Share a memory with specific GPTs."""
    gpt_service = GPTService(db)
    memory = gpt_service.share_memory(
        memory_id=memory_share.memory_id,
        gpt_names=memory_share.gpt_names
    )
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return GPTMemoryAccess(
        memory_id=memory.id,
        gpt_access=memory.gpt_access,
        gpt_source=memory.gpt_source
    )

@router.get("/memories/shared/{gpt_name}", response_model=List[GPTMemoryAccess])
def get_shared_memories(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    gpt_name: str
):
    """Get memories shared with a specific GPT."""
    gpt_service = GPTService(db)
    memories = gpt_service.get_shared_memories(
        user_id=current_user.id,
        gpt_name=gpt_name
    )
    return [
        GPTMemoryAccess(
            memory_id=memory.id,
            gpt_access=memory.gpt_access,
            gpt_source=memory.gpt_source
        )
        for memory in memories
    ] 