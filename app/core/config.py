from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
from enum import Enum
from pydantic import Field

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
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_DOMAINS: List[str] = ["epsnj.org"]
    REQUIRE_DISTRICT_EMAIL: bool = True
    
    # Microsoft Graph Settings
    CLIENT_ID: str = Field(env='MSCLIENTID')
    CLIENT_SECRET: str = Field(env='MSCLIENTSECRET')
    TENANT_ID: str = Field(env='MSTENANTID')
    REDIRECT_URI: str
    SCOPE: str = "User.Read Mail.Read Files.ReadWrite.All"

    # OpenAI Settings
    OPENAI_API_KEY: str
    GPT_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 2000

    # Twilio Settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str
    TWILIO_VOICE_URL: str = "http://twimlets.com/message"

    # Google Cloud Settings
    GOOGLE_PROJECT_ID: str
    GOOGLE_CREDENTIALS_FILE: str = "google-credentials.json"
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
    APP_NAME: str = "EPS PE/Health Department API"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def district_email_domains(self) -> List[str]:
        """Get allowed email domains for the district."""
        return [self.DISTRICT_DOMAIN]

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 