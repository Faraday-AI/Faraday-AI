from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
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
    db: Session = Depends(get_db)
):
    service = GPTFunctionService(db)
    try:
        return await service.process_user_command(user_id, request.command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/suggest-tools", response_model=Dict[str, Any])
async def suggest_tools(
    user_id: str,
    request: ContextRequest,
    db: Session = Depends(get_db)
):
    service = GPTFunctionService(db)
    try:
        return await service.suggest_tools(user_id, request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 