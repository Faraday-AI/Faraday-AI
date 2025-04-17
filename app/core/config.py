from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
from enum import Enum
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
import os
import socket
import time

# Load environment variables from .env file
load_dotenv()

def check_service_availability(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a service is available at the given host and port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def get_service_url(service: str, docker_host: str, docker_port: int, local_host: str, local_port: int) -> str:
    """Get the appropriate service URL based on availability."""
    if check_service_availability(docker_host, docker_port):
        return f"{service}://{docker_host}:{docker_port}"
    return f"{service}://{local_host}:{local_port}"

class DistrictRole(str, Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
    HEALTH_STAFF = "health_staff"
    PE_STAFF = "pe_staff"

class Settings(BaseSettings):
    """Application settings."""
    
    # Service availability
    USE_DOCKER: bool = check_service_availability("localhost", 5432)  # Check if PostgreSQL is running
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DOCKER_DATABASE_URL" if check_service_availability("localhost", 5432) else "LOCAL_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/faraday"
    )
    
    # Add Azure-specific database URL with connection parameters
    if "azure" in DATABASE_URL.lower():
        DATABASE_URL = DATABASE_URL + "?connect_timeout=120&keepalives=1&keepalives_idle=60&keepalives_interval=30&keepalives_count=10&application_name=faraday_ai"
    
    # Redis settings
    REDIS_URL: str = os.getenv(
        "DOCKER_REDIS_URL" if check_service_availability("localhost", 6379) else "LOCAL_REDIS_URL",
        "redis://localhost:6379/0"
    )
    REDIS_HOST: str = os.getenv(
        "DOCKER_REDIS_HOST" if check_service_availability("localhost", 6379) else "LOCAL_REDIS_HOST",
        "localhost"
    )
    REDIS_PORT: int = int(os.getenv(
        "DOCKER_REDIS_PORT" if check_service_availability("localhost", 6379) else "LOCAL_REDIS_PORT",
        "6379"
    ))
    REDIS_DB: int = int(os.getenv(
        "DOCKER_REDIS_DB" if check_service_availability("localhost", 6379) else "LOCAL_REDIS_DB",
        "0"
    ))
    REDIS_PASSWORD: str = os.getenv(
        "DOCKER_REDIS_PASSWORD" if check_service_availability("localhost", 6379) else "LOCAL_REDIS_PASSWORD",
        ""
    )
    
    # MinIO settings
    MINIO_ENDPOINT: str = os.getenv(
        "DOCKER_MINIO_URL" if check_service_availability("localhost", 9000) else "LOCAL_MINIO_URL",
        "localhost:9000"
    )
    MINIO_ACCESS_KEY: str = os.getenv(
        "DOCKER_MINIO_ACCESS_KEY" if check_service_availability("localhost", 9000) else "LOCAL_MINIO_ACCESS_KEY",
        "minioadmin"
    )
    MINIO_SECRET_KEY: str = os.getenv(
        "DOCKER_MINIO_SECRET_KEY" if check_service_availability("localhost", 9000) else "LOCAL_MINIO_SECRET_KEY",
        "minioadmin"
    )
    MINIO_BUCKET: str = os.getenv(
        "DOCKER_MINIO_BUCKET" if check_service_availability("localhost", 9000) else "LOCAL_MINIO_BUCKET",
        "faraday-media"
    )
    MINIO_SECURE: bool = os.getenv(
        "DOCKER_MINIO_SECURE" if check_service_availability("localhost", 9000) else "LOCAL_MINIO_SECURE",
        "false"
    ).lower() == "true"
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Monitoring settings
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    PROMETHEUS_MULTIPROC_DIR: str = os.getenv("PROMETHEUS_MULTIPROC_DIR", "/tmp")
    PROMETHEUS_MULTIPROC: bool = os.getenv("PROMETHEUS_MULTIPROC", "true").lower() == "true"
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_DIR: str = os.getenv("LOG_DIR", "/tmp/faraday-ai/logs")
    
    # District Settings (Generic for development)
    DISTRICT_NAME: str = os.getenv("DISTRICT_NAME", "Development District")
    DISTRICT_ID: str = os.getenv("DISTRICT_ID", "DEV")
    DISTRICT_DOMAIN: str = os.getenv("DISTRICT_DOMAIN", "example.com")
    API_VERSION: str = os.getenv("API_VERSION", "1.0")
    
    # Security Settings
    SECRET_KEY: str = Field(default="development_secret_key_replace_in_production")
    ALGORITHM: str = "HS256"
    ALLOWED_DOMAINS: List[str] = Field(default_factory=lambda: os.getenv("ALLOWED_DOMAINS", "[]").strip('[]').split(','))
    REQUIRE_DISTRICT_EMAIL: bool = Field(default=True)
    
    # Microsoft Graph Settings
    CLIENT_ID: str = Field(alias="MSCLIENTID", default="development")
    CLIENT_SECRET: str = Field(alias="MSCLIENTSECRET", default="development")
    TENANT_ID: str = Field(alias="MSTENANTID", default="development")
    REDIRECT_URI: str = Field(default="http://localhost:8000/auth/callback")
    SCOPE: str = "User.Read Mail.Read Files.ReadWrite.All"

    # ML Model Settings
    MODEL_PATH: str = "/app/models"  # Default path for ML models

    # Twilio Settings
    TWILIO_ACCOUNT_SID: str = Field(default="development")
    TWILIO_AUTH_TOKEN: str = Field(default="development")
    TWILIO_FROM_NUMBER: str = Field(default="+1234567890")
    TWILIO_VOICE_URL: str = "http://twimlets.com/message"

    # Google Cloud Settings
    ENABLE_GOOGLE_CLOUD: bool = Field(default=False)  # Disabled by default
    GOOGLE_PROJECT_ID: str = Field(default="development")
    GOOGLE_CREDENTIALS_FILE: Optional[str] = None
    DEFAULT_TARGET_LANGUAGE: str = "en"  # Default to English for development

    # Document Settings
    TEMPLATE_DIR: str = "app/templates"
    TEMP_DIR: str = "app/temp"
    ALLOWED_DOCUMENT_TYPES: List[str] = Field(
        default_factory=lambda: os.getenv("ALLOWED_DOCUMENT_TYPES", "[]").strip('[]').split(',')
    )

    # Application Settings
    APP_NAME: str = Field(default="Faraday AI")
    DEBUG: bool = Field(default=True)
    API_V1_STR: str = "/api/v1"
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = Field(default=100)
    RATE_LIMIT_PERIOD: int = Field(default=60)
    RATELIMIT_STORAGE_URL: str = Field(default="memory://")
    RATELIMIT_DEFAULT: str = Field(default="100/minute")
    RATELIMIT_STRATEGY: str = Field(default="fixed-window")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "[]").strip('[]').split(',')
    )
    CORS_CREDENTIALS: bool = Field(default=True)
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = Field(default=30)
    WS_MAX_CONNECTIONS: int = Field(default=1000)
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in environment
    )

    @property
    def district_email_domains(self) -> List[str]:
        """Get allowed email domains for the district."""
        return [self.DISTRICT_DOMAIN]

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Export settings instance
settings = get_settings() 