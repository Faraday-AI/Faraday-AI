"""
AI Assistant Schemas
Pydantic schemas for AI assistant integration
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from enum import Enum


class AssistantType(str, Enum):
    """AI Assistant Types"""
    LESSON_PLANNING = "lesson_planning"
    ASSESSMENT_CREATION = "assessment_creation"
    RESOURCE_GENERATION = "resource_generation"
    CONTENT_ANALYSIS = "content_analysis"
    GENERAL_ASSISTANT = "general_assistant"


class ConversationType(str, Enum):
    """Conversation Types"""
    LESSON_PLANNING = "lesson_planning"
    ASSESSMENT_CREATION = "assessment_creation"
    RESOURCE_GENERATION = "resource_generation"
    CONTENT_ANALYSIS = "content_analysis"
    GENERAL_CHAT = "general_chat"


class MessageType(str, Enum):
    """Message Types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class FeedbackType(str, Enum):
    """Feedback Types"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"
    COMMENT = "comment"


# ==================== CONFIGURATION SCHEMAS ====================

class AIAssistantConfigBase(BaseModel):
    """Base AI Assistant Configuration"""
    config_name: str = Field(..., min_length=1, max_length=255)
    config_description: Optional[str] = None
    assistant_type: AssistantType
    is_active: bool = True
    config_data: Dict[str, Any] = Field(default_factory=dict)


class AIAssistantConfigCreate(AIAssistantConfigBase):
    """Create AI Assistant Configuration"""
    pass


class AIAssistantConfigUpdate(BaseModel):
    """Update AI Assistant Configuration"""
    config_name: Optional[str] = Field(None, min_length=1, max_length=255)
    config_description: Optional[str] = None
    assistant_type: Optional[AssistantType] = None
    is_active: Optional[bool] = None
    config_data: Optional[Dict[str, Any]] = None


class AIAssistantConfigResponse(AIAssistantConfigBase):
    """AI Assistant Configuration Response"""
    id: str
    teacher_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CONVERSATION SCHEMAS ====================

class AIAssistantConversationBase(BaseModel):
    """Base AI Assistant Conversation"""
    config_id: Optional[str] = None
    conversation_title: Optional[str] = Field(None, max_length=255)
    conversation_type: ConversationType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIAssistantConversationCreate(AIAssistantConversationBase):
    """Create AI Assistant Conversation"""
    pass


class AIAssistantConversationUpdate(BaseModel):
    """Update AI Assistant Conversation"""
    conversation_title: Optional[str] = Field(None, max_length=255)
    conversation_type: Optional[ConversationType] = None
    metadata: Optional[Dict[str, Any]] = None


class AIAssistantConversationResponse(AIAssistantConversationBase):
    """AI Assistant Conversation Response"""
    id: str
    teacher_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== MESSAGE SCHEMAS ====================

class AIAssistantMessageBase(BaseModel):
    """Base AI Assistant Message"""
    message_type: MessageType
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIAssistantMessageCreate(AIAssistantMessageBase):
    """Create AI Assistant Message"""
    pass


class AIAssistantMessageResponse(AIAssistantMessageBase):
    """AI Assistant Message Response"""
    id: str
    conversation_id: str
    token_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CHAT SCHEMAS ====================

class AIAssistantChatRequest(BaseModel):
    """AI Assistant Chat Request"""
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    config_id: Optional[str] = None
    conversation_title: Optional[str] = Field(None, max_length=255)
    conversation_type: Optional[ConversationType] = ConversationType.GENERAL_CHAT
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIAssistantChatResponse(BaseModel):
    """AI Assistant Chat Response"""
    conversation_id: str
    message_id: str
    response: str
    token_count: int
    processing_time_ms: int
    model_used: str


# ==================== USAGE SCHEMAS ====================

class AIAssistantUsageResponse(BaseModel):
    """AI Assistant Usage Response"""
    id: str
    teacher_id: str
    config_id: Optional[str] = None
    usage_type: str
    tokens_used: int
    requests_count: int
    processing_time_ms: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any]
    usage_date: date
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== TEMPLATE SCHEMAS ====================

class AIAssistantTemplateResponse(BaseModel):
    """AI Assistant Template Response"""
    id: str
    template_name: str
    template_description: Optional[str] = None
    template_type: str
    template_content: str
    template_variables: Dict[str, Any]
    is_system_template: bool
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== FEEDBACK SCHEMAS ====================

class AIAssistantFeedbackBase(BaseModel):
    """Base AI Assistant Feedback"""
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    feedback_type: FeedbackType
    feedback_value: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None
    is_helpful: Optional[bool] = None


class AIAssistantFeedbackCreate(AIAssistantFeedbackBase):
    """Create AI Assistant Feedback"""
    pass


class AIAssistantFeedbackResponse(AIAssistantFeedbackBase):
    """AI Assistant Feedback Response"""
    id: str
    teacher_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ANALYTICS SCHEMAS ====================

class AIAssistantAnalyticsResponse(BaseModel):
    """AI Assistant Analytics Response"""
    id: str
    teacher_id: str
    analytics_date: date
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens_used: int
    total_processing_time_ms: int
    average_response_time_ms: Optional[float] = None
    most_used_type: Optional[str] = None
    satisfaction_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SUMMARY SCHEMAS ====================

class AIAssistantUsageSummary(BaseModel):
    """AI Assistant Usage Summary"""
    total_tokens: int
    total_requests: int
    total_processing_time_ms: int
    average_response_time_ms: float
    usage_by_type: Dict[str, Dict[str, int]]
    satisfaction_score: float
    period_days: int


class AIAssistantDashboardSummary(BaseModel):
    """AI Assistant Dashboard Summary"""
    total_conversations: int
    active_conversations: int
    total_messages: int
    total_tokens_used: int
    average_satisfaction: float
    most_used_type: str
    recent_activity_count: int
    last_interaction: Optional[datetime] = None


# ==================== VALIDATION SCHEMAS ====================

class AIAssistantConfigValidation(BaseModel):
    """AI Assistant Configuration Validation"""
    config_name: str = Field(..., min_length=1, max_length=255)
    assistant_type: AssistantType
    config_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('config_data')
    def validate_config_data(cls, v):
        """Validate configuration data"""
        required_fields = ['model', 'temperature', 'max_tokens']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(v.get('temperature'), (int, float)) or not (0 <= v.get('temperature') <= 2):
            raise ValueError("Temperature must be between 0 and 2")
        
        if not isinstance(v.get('max_tokens'), int) or v.get('max_tokens') <= 0:
            raise ValueError("Max tokens must be a positive integer")
        
        return v


class AIAssistantMessageValidation(BaseModel):
    """AI Assistant Message Validation"""
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: MessageType
    
    @validator('content')
    def validate_content(cls, v):
        """Validate message content"""
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


# ==================== ERROR SCHEMAS ====================

class AIAssistantError(BaseModel):
    """AI Assistant Error"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIAssistantRateLimitError(AIAssistantError):
    """AI Assistant Rate Limit Error"""
    retry_after: int
    limit_type: str


# ==================== BULK OPERATIONS SCHEMAS ====================

class AIAssistantBulkCreateRequest(BaseModel):
    """Bulk Create AI Assistant Configurations"""
    configs: List[AIAssistantConfigCreate] = Field(..., min_items=1, max_items=10)


class AIAssistantBulkCreateResponse(BaseModel):
    """Bulk Create AI Assistant Configurations Response"""
    created_count: int
    failed_count: int
    created_configs: List[AIAssistantConfigResponse]
    errors: List[AIAssistantError]


class AIAssistantBulkDeleteRequest(BaseModel):
    """Bulk Delete AI Assistant Configurations"""
    config_ids: List[str] = Field(..., min_items=1, max_items=10)


class AIAssistantBulkDeleteResponse(BaseModel):
    """Bulk Delete AI Assistant Configurations Response"""
    deleted_count: int
    failed_count: int
    errors: List[AIAssistantError]
