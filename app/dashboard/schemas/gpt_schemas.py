"""
Schemas for GPT manager functionality.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel

class ToolResponse(BaseModel):
    """Response schema for tool operations."""
    status: str
    message: str
    tool_id: Optional[str] = None

class CommandRequest(BaseModel):
    """Request schema for GPT commands."""
    command: str
    context: Optional[Dict] = None

class CommandResponse(BaseModel):
    """Response schema for GPT commands."""
    status: str
    action: Optional[str] = None
    message: Optional[str] = None
    result: Optional[Dict] = None

class ToolMetrics(BaseModel):
    """Schema for tool metrics."""
    performance: Optional[Dict] = None
    usage: Optional[Dict] = None
    health: Optional[Dict] = None

class CommandMetrics(BaseModel):
    """Schema for command metrics."""
    performance: Optional[Dict] = None
    usage: Optional[Dict] = None
    quality: Optional[Dict] = None

class IntegrationResponse(BaseModel):
    """Schema for integration response."""
    id: str
    name: str
    type: str
    status: str
    metadata: Optional[Dict] = None

class ToolStatus(BaseModel):
    """Schema for tool status."""
    name: str
    status: str
    health: Optional[Dict] = None
    performance: Optional[Dict] = None
    dependencies: Optional[Dict] = None

class CommandHistory(BaseModel):
    """Schema for command history."""
    id: str
    command: str
    timestamp: str
    status: str
    result: Optional[Dict] = None
    metrics: Optional[Dict] = None

class GPTToolSpec(BaseModel):
    """Schema for GPT tool specifications."""
    name: str
    description: str
    parameters: Dict

class GPTManagerConfig(BaseModel):
    """Configuration schema for GPT manager."""
    default_model: str
    allowed_categories: List[str]
    max_tools: int = 10
    context_sharing: bool = True
    memory_retention: Dict = {
        "enabled": True,
        "max_history": 100,
        "ttl_hours": 24
    }

class GPTToolMetrics(BaseModel):
    """Schema for GPT tool usage metrics."""
    tool_id: str
    usage_count: int
    average_latency: float
    success_rate: float
    last_used: str
    performance_score: float

class GPTToolRegistry(BaseModel):
    """Schema for user's GPT tool registry."""
    user_id: str
    active_tools: List[str]
    primary_tool: str
    tool_metrics: Dict[str, GPTToolMetrics]
    last_updated: str 