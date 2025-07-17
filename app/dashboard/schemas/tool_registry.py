from typing import Optional, Dict, Any
from pydantic import BaseModel

class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    function_schema: Optional[Dict[str, Any]] = None
    is_active: bool = True
    requires_approval: bool = False
    version: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class ToolCreate(ToolBase):
    id: str

class ToolUpdate(ToolBase):
    pass

class Tool(ToolBase):
    id: str

    class Config:
        from_attributes = True

class UserToolBase(BaseModel):
    is_enabled: bool = True
    settings: Optional[Dict[str, Any]] = None
    last_used: Optional[str] = None
    usage_count: Optional[str] = None

class UserToolCreate(UserToolBase):
    user_id: str
    tool_id: str

class UserToolUpdate(UserToolBase):
    pass

class UserTool(UserToolBase):
    user_id: str
    tool_id: str

    class Config:
        from_attributes = True 