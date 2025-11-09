from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dashboard.dependencies import get_current_user
from app.dashboard.services.gpt_function_service import GPTFunctionService
from pydantic import BaseModel

router = APIRouter()

class CommandRequest(BaseModel):
    command: str

class ContextRequest(BaseModel):
    context: str

@router.post("/users/{user_id}/command", response_model=Dict[str, Any])
async def process_command(
    user_id: str,
    request: CommandRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process user command with AI widget support for both main and beta systems."""
    # Convert user_id to int if possible (main system), otherwise keep as string (beta)
    try:
        user_id_int = int(user_id) if user_id.isdigit() else None
    except (ValueError, AttributeError):
        user_id_int = None
    
    service = GPTFunctionService(db, user_id=user_id_int or current_user.get("id"))
    try:
        return await service.process_user_command(user_id, request.command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/suggest-tools", response_model=Dict[str, Any])
async def suggest_tools(
    user_id: str,
    request: ContextRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Suggest tools for user command with AI widget support for both main and beta systems."""
    # Convert user_id to int if possible (main system), otherwise keep as string (beta)
    try:
        user_id_int = int(user_id) if user_id.isdigit() else None
    except (ValueError, AttributeError):
        user_id_int = None
    
    service = GPTFunctionService(db, user_id=user_id_int or current_user.get("id"))
    try:
        return await service.suggest_tools(user_id, request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 