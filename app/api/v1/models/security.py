from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (bearer)")
    refresh_token: str = Field(..., description="JWT refresh token")

class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Optional[str] = Field(None, description="Username from token")
    scopes: List[str] = Field([], description="List of token scopes")

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    disabled: Optional[bool] = Field(None, description="Whether the user is disabled")
    scopes: List[str] = Field([], description="List of user scopes")

class UserInDB(User):
    model_config = ConfigDict(from_attributes=True)
    hashed_password: str = Field(..., description="Hashed password")

class SecurityRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    request_type: str = Field(..., description="Type of security request")
    details: dict = Field(..., description="Request details")
    priority: str = Field("medium", description="Request priority level")
    user_id: Optional[str] = Field(None, description="User ID making the request")

class SecurityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    success: bool = Field(..., description="Whether the security operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class ThreatAssessmentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    assessment_type: str = Field(..., description="Type of threat assessment")
    target: str = Field(..., description="Target of the assessment")
    context: dict = Field(..., description="Assessment context")
    urgency: str = Field("normal", description="Assessment urgency level")

class ThreatAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    assessment_id: str = Field(..., description="Unique assessment identifier")
    threat_level: str = Field(..., description="Assessed threat level")
    recommendations: List[str] = Field(..., description="Security recommendations")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score (0.0 to 1.0)")
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    valid_until: datetime = Field(..., description="Assessment validity period") 