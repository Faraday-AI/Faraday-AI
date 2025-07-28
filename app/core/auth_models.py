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