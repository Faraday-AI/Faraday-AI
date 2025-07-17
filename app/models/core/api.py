from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum

class MessageType(str, Enum):
    SMS = "sms"
    VOICE = "voice"

class DocumentRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_type": "report",
                "title": "Monthly Report",
                "content": "This is the content of the report",
                "output_format": "docx"
            }
        }
    )
    
    document_type: str
    title: str
    content: str
    output_format: str = "docx"

class TextRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Generate a summary of the quarterly results",
                "structured_output": False
            }
        }
    )
    
    prompt: str
    structured_output: bool = False
    document_request: Optional[DocumentRequest] = None

class TokenResponse(BaseModel):
    status: str
    token: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class UserInfoResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TextResponse(BaseModel):
    status: str
    content: Optional[str] = None
    error: Optional[str] = None

class SMSRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_number": "+1234567890",
                "message": "Hello from FastAPI!"
            }
        }
    )
    
    to_number: str = Field(..., description="Recipient's phone number in E.164 format (e.g., +1234567890)")
    message: str = Field(..., description="Message content to send")

class SMSResponse(BaseModel):
    status: str
    message_sid: Optional[str] = None
    to: Optional[str] = None
    from_: Optional[str] = Field(None, alias="from")
    message_status: Optional[str] = None
    error: Optional[str] = None
    code: Optional[int] = None

class TranslationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Hello, how are you?",
                "target_language": "es",
                "source_language": "en"
            }
        }
    )
    
    text: str = Field(..., description="Text to translate")
    target_language: str = Field("es", description="Target language code (e.g., 'es' for Spanish)")
    source_language: str = Field("en", description="Source language code (e.g., 'en' for English)")

class TranslationResponse(BaseModel):
    status: str
    translated_text: Optional[str] = None
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    error: Optional[str] = None

class TranslatedMessageRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_number": "+1234567890",
                "message": "Your child has performed exceptionally well in today's class.",
                "message_type": "sms",
                "target_language": "es",
                "source_language": "en"
            }
        }
    )
    
    to_number: str = Field(..., description="Recipient's phone number in E.164 format")
    message: str = Field(..., description="Message to translate and send")
    message_type: MessageType = Field(MessageType.SMS, description="Type of message to send (sms or voice)")
    target_language: str = Field("es", description="Target language code")
    source_language: str = Field("en", description="Source language code")

class TranslatedMessageResponse(BaseModel):
    status: str
    original_text: str
    translated_text: str
    message_type: str
    delivery_status: str
    message_sid: Optional[str] = None
    call_sid: Optional[str] = None
    error: Optional[str] = None 