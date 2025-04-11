from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CollaborationSessionRequest(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the session")
    participants: List[str] = Field(..., description="List of participant IDs")
    activity_ids: List[str] = Field(..., description="List of activity IDs to collaborate on")
    settings: Dict[str, Any] = Field(..., description="Session settings")

class CollaborationSessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the session")
    participants: List[str] = Field(..., description="List of participant IDs")
    activity_ids: List[str] = Field(..., description="List of activity IDs")
    settings: Dict[str, Any] = Field(..., description="Session settings")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="When the session was created")
    updated_at: datetime = Field(..., description="When the session was last updated")

class ChatMessageResponse(BaseModel):
    message_id: str = Field(..., description="Unique identifier for the message")
    session_id: str = Field(..., description="ID of the collaboration session")
    user_id: str = Field(..., description="ID of the user who sent the message")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata") 