from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
from enum import Enum
from pydantic import Field
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class DistrictRole(str, Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
    HEALTH_STAFF = "health_staff"
    PE_STAFF = "pe_staff"

class Settings(BaseSettings):
    # District Settings
    DISTRICT_NAME: str = "Elizabeth Public Schools"
    DISTRICT_ID: str = "EPSNJ"
    DISTRICT_DOMAIN: str = "epsnj.org"
    API_VERSION: str = "1.0"
    
    # Security Settings
    SECRET_KEY: str = Field(default="development_secret_key_replace_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_DOMAINS: List[str] = ["epsnj.org"]
    REQUIRE_DISTRICT_EMAIL: bool = True
    
    # Microsoft Graph Settings - map to environment variable names
    CLIENT_ID: str = Field(alias="MSCLIENTID", default="development")
    CLIENT_SECRET: str = Field(alias="MSCLIENTSECRET", default="development")
    TENANT_ID: str = Field(alias="MSTENANTID", default="development")
    REDIRECT_URI: str = Field(default="http://localhost:8000/auth/callback")
    SCOPE: str = "User.Read Mail.Read Files.ReadWrite.All"

    # OpenAI Settings
    OPENAI_API_KEY: str = Field(default="development")
    GPT_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 2000

    # Twilio Settings
    TWILIO_ACCOUNT_SID: str = Field(default="development")
    TWILIO_AUTH_TOKEN: str = Field(default="development")
    TWILIO_FROM_NUMBER: str = Field(default="+1234567890")
    TWILIO_VOICE_URL: str = "http://twimlets.com/message"

    # Google Cloud Settings
    ENABLE_GOOGLE_CLOUD: bool = Field(default=False)  # Disabled by default
    GOOGLE_PROJECT_ID: str = Field(default="development")
    GOOGLE_CREDENTIALS_FILE: Optional[str] = None
    DEFAULT_TARGET_LANGUAGE: str = "es"  # Spanish default for EPS

    # Document Settings
    TEMPLATE_DIR: str = "app/templates"
    TEMP_DIR: str = "app/temp"
    ALLOWED_DOCUMENT_TYPES: List[str] = [
        "lesson_plan",
        "assessment",
        "progress_report",
        "parent_notification",
        "health_record"
    ]

    # Application Settings
    APP_NAME: str = Field(default="Faraday AI")
    DEBUG: bool = Field(default=True)
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in environment

    @property
    def district_email_domains(self) -> List[str]:
        """Get allowed email domains for the district."""
        return [self.DISTRICT_DOMAIN]

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 