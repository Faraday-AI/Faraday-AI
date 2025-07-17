from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime

class GPTRoleBase(BaseModel):
    gpt_name: str
    preferences: Optional[Dict] = None

class GPTRoleCreate(GPTRoleBase):
    pass

class GPTRoleUpdate(GPTRoleBase):
    pass

class GPTRoleInDB(GPTRoleBase):
    id: int
    user_id: str
    created_at: datetime
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True

class GPTInteractionBase(BaseModel):
    gpt_name: str
    memory_id: Optional[int] = None
    interaction_type: Optional[str] = None
    interaction_data: Optional[Dict] = None

class GPTInteractionCreate(GPTInteractionBase):
    pass

class GPTInteractionInDB(GPTInteractionBase):
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class MemoryShare(BaseModel):
    memory_id: int
    gpt_names: List[str]

class GPTMemoryAccess(BaseModel):
    memory_id: int
    gpt_access: List[str]
    gpt_source: Optional[str] = None 