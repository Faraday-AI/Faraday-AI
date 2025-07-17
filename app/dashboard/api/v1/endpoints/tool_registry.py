from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dashboard.services.tool_registry_service import ToolRegistryService
from app.dashboard.schemas.tool_registry import Tool, ToolCreate, ToolUpdate, UserTool, UserToolCreate

router = APIRouter()

@router.get("/tools", response_model=List[Tool])
def get_tools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    return service.get_tools(skip=skip, limit=limit)

@router.post("/tools", response_model=Tool)
def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    return service.create_tool(tool)

@router.get("/tools/{tool_id}", response_model=Tool)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    tool = service.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.put("/tools/{tool_id}", response_model=Tool)
def update_tool(tool_id: str, tool: ToolUpdate, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    updated_tool = service.update_tool(tool_id, tool)
    if not updated_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return updated_tool

@router.delete("/tools/{tool_id}")
def delete_tool(tool_id: str, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    if not service.delete_tool(tool_id):
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"message": "Tool deleted successfully"}

@router.get("/users/{user_id}/tools", response_model=List[Tool])
def get_user_tools(user_id: str, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    return service.get_user_tools(user_id)

@router.post("/users/{user_id}/tools/{tool_id}/enable", response_model=UserTool)
def enable_tool_for_user(
    user_id: str,
    tool_id: str,
    settings: dict = None,
    db: Session = Depends(get_db)
):
    service = ToolRegistryService(db)
    user_tool = service.enable_tool_for_user(user_id, tool_id, settings)
    if not user_tool:
        raise HTTPException(status_code=404, detail="Tool or user not found")
    return user_tool

@router.post("/users/{user_id}/tools/{tool_id}/disable")
def disable_tool_for_user(user_id: str, tool_id: str, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    if not service.disable_tool_for_user(user_id, tool_id):
        raise HTTPException(status_code=404, detail="Tool or user not found")
    return {"message": "Tool disabled successfully"}

@router.get("/users/{user_id}/tool-schemas")
def get_user_tool_schemas(user_id: str, db: Session = Depends(get_db)):
    service = ToolRegistryService(db)
    return service.get_tool_function_schemas(user_id) 