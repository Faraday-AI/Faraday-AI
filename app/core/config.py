"""
Configuration Module

This module provides comprehensive configuration settings for the Faraday AI Dashboard.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import Field, ConfigDict, field_validator
from dotenv import load_dotenv
import os
import socket
import time
import json
from pathlib import Path

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

def get_region_db_url(region: str) -> str:
    """Get database URL for a specific region."""
    return f"postgresql://postgres:postgres@{region}-db:5432/faraday"

class Settings(BaseSettings):
    """Application settings."""
    
    # Service availability
    USE_DOCKER: bool = check_service_availability("localhost", 5432)  # Check if PostgreSQL is running
    
    # Environment
    ENVIRONMENT: str = Field(default="development")
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/faraday"
    )
    
    # Redis settings
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://redis:6379/0"
    )
    REDIS_HOST: str = os.getenv(
        "REDIS_HOST",
        "redis"
    )
    REDIS_PORT: int = int(os.getenv(
        "REDIS_PORT",
        "6379"
    ))
    REDIS_DB: int = int(os.getenv(
        "REDIS_DB",
        "0"
    ))
    REDIS_PASSWORD: str = os.getenv(
        "REDIS_PASSWORD",
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
    
    # Notification Rate Limits
    SMTP_RATE_LIMIT: int = 100  # Max emails per time window
    SMTP_RATE_WINDOW: int = 3600  # 1 hour in seconds
    SLACK_RATE_LIMIT: int = 20  # Max Slack messages per time window
    SLACK_RATE_WINDOW: int = 60  # 1 minute in seconds
    WEBHOOK_RATE_LIMIT: int = 50  # Max webhook calls per time window
    WEBHOOK_RATE_WINDOW: int = 300  # 5 minutes in seconds
    
    # Email Batching Settings
    EMAIL_BATCH_SIZE: int = Field(default=10)  # Maximum emails per batch
    EMAIL_BATCH_WAIT: float = Field(default=5.0)  # Maximum seconds to wait before sending batch
    
    # Enhanced Security Settings
    PASSWORD_MIN_LENGTH: int = Field(default=8)
    PASSWORD_REQUIRE_LOWER: bool = Field(default=True)
    PASSWORD_REQUIRE_NUMBERS: bool = Field(default=True)
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True)
    SESSION_TIMEOUT: int = Field(default=3600)  # 1 hour
    MAX_LOGIN_ATTEMPTS: int = Field(default=5)
    LOGIN_TIMEOUT: int = Field(default=300)  # 5 minutes
    PASSWORD_RESET_TIMEOUT: int = Field(default=3600)  # 1 hour
    MFA_REQUIRED: bool = Field(default=False)
    MFA_TIMEOUT: int = Field(default=300)  # 5 minutes
    
    # Caching Settings
    CACHE_TYPE: str = Field(default="redis")
    CACHE_REDIS_URL: str = Field(default="redis://redis:6379/1")
    CACHE_DEFAULT_TIMEOUT: int = Field(default=300)  # 5 minutes
    CACHE_KEY_PREFIX: str = Field(default="faraday:")
    CACHE_OPTIONS: Dict[str, Any] = Field(default_factory=dict)
    
    # Session Settings
    SESSION_TYPE: str = Field(default="redis")
    SESSION_REDIS_URL: str = Field(default="redis://redis:6379/2")
    SESSION_COOKIE_NAME: str = Field(default="faraday_session")
    SESSION_COOKIE_SECURE: bool = Field(default=True)
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True)
    SESSION_COOKIE_SAMESITE: str = Field(default="Lax")
    
    # File Upload Settings
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_UPLOAD_TYPES: List[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "application/pdf"]
    )
    UPLOAD_CHUNK_SIZE: int = Field(default=1024 * 1024)  # 1MB
    UPLOAD_TIMEOUT: int = Field(default=300)  # 5 minutes
    
    # API Documentation Settings
    API_TITLE: str = Field(default="Faraday AI API")
    API_DESCRIPTION: str = Field(default="API for Faraday AI Physical Education Platform")
    API_VERSION: str = Field(default="1.0.0")
    API_DOCS_URL: str = Field(default="/docs")
    API_REDOC_URL: str = Field(default="/redoc")
    API_OPENAPI_URL: str = Field(default="/openapi.json")
    API_TERMS_OF_SERVICE: str = Field(default="https://faraday.ai/terms")
    API_CONTACT: Dict[str, str] = Field(
        default_factory=lambda: {
            "name": "Faraday AI Support",
            "url": "https://faraday.ai/support",
            "email": "support@faraday.ai"
        }
    )
    API_LICENSE: Dict[str, str] = Field(
        default_factory=lambda: {
            "name": "Proprietary",
            "url": "https://faraday.ai/license"
        }
    )
    
    # Health Check Settings
    HEALTH_CHECK_INTERVAL: int = Field(default=60)  # 1 minute
    HEALTH_CHECK_TIMEOUT: int = Field(default=5)  # 5 seconds
    HEALTH_CHECK_RETRIES: int = Field(default=3)
    HEALTH_CHECK_ENDPOINTS: List[str] = Field(
        default_factory=lambda: ["/health", "/ready", "/live"]
    )
    
    # Backup Settings
    BACKUP_ENABLED: bool = Field(default=True)
    BACKUP_SCHEDULE: str = Field(default="0 0 * * *")  # Daily at midnight
    BACKUP_RETENTION_DAYS: int = Field(default=30)
    BACKUP_DIR: str = Field(default="/backups")
    BACKUP_COMPRESSION: bool = Field(default=True)
    BACKUP_ENCRYPTION: bool = Field(default=True)
    BACKUP_NOTIFICATION: bool = Field(default=True)
    
    # Enhanced Monitoring Settings
    ENABLE_APM: bool = Field(default=False)
    APM_SERVER_URL: str = Field(default="http://localhost:8200")
    APM_SERVICE_NAME: str = Field(default="faraday-ai")
    APM_ENVIRONMENT: str = Field(default="development")
    ENABLE_TRACING: bool = Field(default=False)
    TRACING_SERVICE_NAME: str = Field(default="faraday-ai")
    TRACING_SAMPLING_RATE: float = Field(default=0.1)
    ENABLE_PROFILING: bool = Field(default=False)
    PROFILING_INTERVAL: int = Field(default=60)  # 1 minute
    PROFILING_DURATION: int = Field(default=30)  # 30 seconds
    
    # Performance Settings
    WORKER_COUNT: int = Field(default=4)
    MAX_REQUESTS: int = Field(default=1000)
    MAX_REQUESTS_JITTER: int = Field(default=50)
    TIMEOUT_KEEP_ALIVE: int = Field(default=5)
    TIMEOUT_GRACEFUL_SHUTDOWN: int = Field(default=10)
    
    # Service Discovery Settings
    SERVICE_DISCOVERY_ENABLED: bool = Field(default=False)
    SERVICE_DISCOVERY_TYPE: str = Field(default="consul")  # consul, etcd, zookeeper
    SERVICE_DISCOVERY_HOST: str = Field(default="localhost")
    SERVICE_DISCOVERY_PORT: int = Field(default=8500)
    SERVICE_DISCOVERY_TTL: int = Field(default=30)
    SERVICE_DISCOVERY_TAGS: List[str] = Field(default_factory=list)
    SERVICE_DISCOVERY_META: Dict[str, str] = Field(default_factory=dict)
    
    # Circuit Breaker Settings
    CIRCUIT_BREAKER_ENABLED: bool = Field(default=True)
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5)
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=30)
    CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS: int = Field(default=3)
    CIRCUIT_BREAKER_EXCLUDED_EXCEPTIONS: List[str] = Field(default_factory=list)
    
    # Feature Flag Settings
    FEATURE_FLAGS_ENABLED: bool = Field(default=True)
    FEATURE_FLAGS_PROVIDER: str = Field(default="redis")  # redis, launchdarkly, split
    FEATURE_FLAGS_DEFAULT_VALUE: bool = Field(default=False)
    FEATURE_FLAGS_CACHE_TTL: int = Field(default=60)
    FEATURE_FLAGS_REFRESH_INTERVAL: int = Field(default=30)
    
    # A/B Testing Settings
    AB_TESTING_ENABLED: bool = Field(default=True)
    AB_TESTING_PROVIDER: str = Field(default="redis")  # redis, optimizely, split
    AB_TESTING_DEFAULT_VARIANT: str = Field(default="control")
    AB_TESTING_SAMPLE_RATE: float = Field(default=1.0)
    AB_TESTING_MIN_SAMPLE_SIZE: int = Field(default=100)
    
    # Analytics Settings
    ANALYTICS_ENABLED: bool = Field(default=True)
    ANALYTICS_PROVIDER: str = Field(default="mixpanel")  # mixpanel, amplitude, segment
    ANALYTICS_API_KEY: str = Field(default="")
    ANALYTICS_PROJECT_ID: str = Field(default="")
    ANALYTICS_ENVIRONMENT: str = Field(default="development")
    ANALYTICS_SAMPLE_RATE: float = Field(default=1.0)
    
    # Metrics Settings
    METRICS_ENABLED: bool = Field(default=True)
    METRICS_PROVIDER: str = Field(default="prometheus")  # prometheus, datadog, newrelic
    METRICS_HOST: str = Field(default="localhost")
    METRICS_PORT: int = Field(default=9090)
    METRICS_PREFIX: str = Field(default="faraday_")
    METRICS_LABELS: Dict[str, str] = Field(default_factory=dict)
    METRICS_BUCKETS: List[float] = Field(default_factory=lambda: [0.1, 0.5, 1.0, 2.0, 5.0])
    
    # Alert Settings
    ALERTS_ENABLED: bool = Field(default=True)
    ALERTS_PROVIDER: str = Field(default="pagerduty")  # pagerduty, opsgenie, slack
    ALERTS_API_KEY: str = Field(default="")
    ALERTS_SERVICE_KEY: str = Field(default="")
    ALERTS_ENVIRONMENT: str = Field(default="development")
    ALERTS_SEVERITY_LEVELS: List[str] = Field(
        default_factory=lambda: ["critical", "error", "warning", "info"]
    )
    
    # Deployment Settings
    DEPLOYMENT_ENVIRONMENT: str = Field(default="development")
    DEPLOYMENT_VERSION: str = Field(default="1.0.0")
    DEPLOYMENT_REGION: str = Field(default="us-east-1")
    DEPLOYMENT_ZONE: str = Field(default="us-east-1a")
    DEPLOYMENT_INSTANCE: str = Field(default="default")
    DEPLOYMENT_TAGS: Dict[str, str] = Field(default_factory=dict)
    
    # Initialize configuration components
    service_config: Optional['ServiceConfig'] = None
    security_config: Optional['SecurityConfig'] = None
    performance_config: Optional['PerformanceConfig'] = None
    monitoring_config: Optional['MonitoringConfig'] = None
    deployment_config: Optional['DeploymentConfig'] = None
    feature_flag_config: Optional['FeatureFlagConfig'] = None
    analytics_config: Optional['AnalyticsConfig'] = None
    alert_config: Optional['AlertConfig'] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize configs after super().__init__ to ensure all settings are loaded
        self.service_config = ServiceConfig(self)
        self.security_config = SecurityConfig(self)
        self.performance_config = PerformanceConfig(self)
        self.monitoring_config = MonitoringConfig(self)
        self.deployment_config = DeploymentConfig(self)
        self.feature_flag_config = FeatureFlagConfig(self)
        self.analytics_config = AnalyticsConfig(self)
        self.alert_config = AlertConfig(self)
    
    # Validation
    @field_validator("ALLOWED_UPLOAD_TYPES")
    @classmethod
    def validate_upload_types(cls, v):
        if not v:
            raise ValueError("At least one upload type must be specified")
        return v
    
    @field_validator("HEALTH_CHECK_ENDPOINTS")
    @classmethod
    def validate_health_endpoints(cls, v):
        if not v:
            raise ValueError("At least one health check endpoint must be specified")
        return v
    
    @field_validator("BACKUP_RETENTION_DAYS")
    @classmethod
    def validate_backup_retention(cls, v):
        if v < 1:
            raise ValueError("Backup retention must be at least 1 day")
        return v
    
    @field_validator("MAX_UPLOAD_SIZE")
    @classmethod
    def validate_upload_size(cls, v):
        if v < 1024:  # 1KB
            raise ValueError("Maximum upload size must be at least 1KB")
        return v
    
    @field_validator("SERVICE_DISCOVERY_TYPE")
    @classmethod
    def validate_service_discovery_type(cls, v):
        valid_types = ["consul", "etcd", "zookeeper"]
        if v not in valid_types:
            raise ValueError(f"Service discovery type must be one of {valid_types}")
        return v
    
    @field_validator("FEATURE_FLAGS_PROVIDER")
    @classmethod
    def validate_feature_flags_provider(cls, v):
        valid_providers = ["redis", "launchdarkly", "split"]
        if v not in valid_providers:
            raise ValueError(f"Feature flags provider must be one of {valid_providers}")
        return v
    
    @field_validator("AB_TESTING_PROVIDER")
    @classmethod
    def validate_ab_testing_provider(cls, v):
        valid_providers = ["redis", "optimizely", "split"]
        if v not in valid_providers:
            raise ValueError(f"A/B testing provider must be one of {valid_providers}")
        return v
    
    @field_validator("ANALYTICS_PROVIDER")
    @classmethod
    def validate_analytics_provider(cls, v):
        valid_providers = ["mixpanel", "amplitude", "segment"]
        if v not in valid_providers:
            raise ValueError(f"Analytics provider must be one of {valid_providers}")
        return v
    
    @field_validator("METRICS_PROVIDER")
    @classmethod
    def validate_metrics_provider(cls, v):
        valid_providers = ["prometheus", "datadog", "newrelic"]
        if v not in valid_providers:
            raise ValueError(f"Metrics provider must be one of {valid_providers}")
        return v
    
    @field_validator("ALERTS_PROVIDER")
    @classmethod
    def validate_alerts_provider(cls, v):
        valid_providers = ["pagerduty", "opsgenie", "slack"]
        if v not in valid_providers:
            raise ValueError(f"Alerts provider must be one of {valid_providers}")
        return v
    
    @field_validator("DEPLOYMENT_ENVIRONMENT")
    @classmethod
    def validate_deployment_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Deployment environment must be one of {valid_environments}")
        return v
    
    @field_validator("AB_TESTING_SAMPLE_RATE")
    @classmethod
    def validate_ab_testing_sample_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("A/B testing sample rate must be between 0 and 1")
        return v
    
    @field_validator("ANALYTICS_SAMPLE_RATE")
    @classmethod
    def validate_analytics_sample_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Analytics sample rate must be between 0 and 1")
        return v
    
    @field_validator("METRICS_BUCKETS")
    @classmethod
    def validate_metrics_buckets(cls, v):
        if not v:
            raise ValueError("Metrics buckets cannot be empty")
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Metrics buckets must be numbers")
        if not all(x > 0 for x in v):
            raise ValueError("Metrics buckets must be positive")
        return sorted(v)
    
    @field_validator("ALERTS_SEVERITY_LEVELS")
    @classmethod
    def validate_alerts_severity_levels(cls, v):
        valid_levels = ["critical", "error", "warning", "info"]
        if not all(level in valid_levels for level in v):
            raise ValueError(f"Alert severity levels must be one of {valid_levels}")
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='allow'
    )
    
    @property
    def district_email_domains(self) -> List[str]:
        """Get list of allowed email domains for the district."""
        return [self.DISTRICT_DOMAIN]

class ServiceConfig:
    """Service configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_service_config()
    
    def _load_service_config(self):
        """Load service configuration from environment or defaults."""
        self.services = {
            'database': {
                'url': self.settings.DATABASE_URL,
                'pool_size': 20,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_recycle': 1800
            },
            'redis': {
                'url': self.settings.REDIS_URL,
                'host': self.settings.REDIS_HOST,
                'port': self.settings.REDIS_PORT,
                'db': self.settings.REDIS_DB,
                'password': self.settings.REDIS_PASSWORD,
                'pool_size': 10,
                'socket_timeout': 5
            },
            'minio': {
                'endpoint': self.settings.MINIO_ENDPOINT,
                'access_key': self.settings.MINIO_ACCESS_KEY,
                'secret_key': self.settings.MINIO_SECRET_KEY,
                'bucket': self.settings.MINIO_BUCKET,
                'secure': self.settings.MINIO_SECURE
            }
        }
    
    def get_service_config(self, service: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        return self.services.get(service, {})

class SecurityConfig:
    """Security configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_security_config()
    
    def _load_security_config(self):
        """Load security configuration from environment or defaults."""
        self.security = {
            'jwt': {
                'secret_key': self.settings.JWT_SECRET_KEY,
                'algorithm': self.settings.JWT_ALGORITHM,
                'access_token_expire_minutes': self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            },
            'password': {
                'min_length': self.settings.PASSWORD_MIN_LENGTH,
                'require_lower': self.settings.PASSWORD_REQUIRE_LOWER,
                'require_numbers': self.settings.PASSWORD_REQUIRE_NUMBERS,
                'require_special': self.settings.PASSWORD_REQUIRE_SPECIAL
            },
            'session': {
                'timeout': self.settings.SESSION_TIMEOUT,
                'max_login_attempts': self.settings.MAX_LOGIN_ATTEMPTS,
                'login_timeout': self.settings.LOGIN_TIMEOUT,
                'password_reset_timeout': self.settings.PASSWORD_RESET_TIMEOUT
            },
            'mfa': {
                'required': self.settings.MFA_REQUIRED,
                'timeout': self.settings.MFA_TIMEOUT
            }
        }
    
    def get_security_config(self, component: str) -> Dict[str, Any]:
        """Get configuration for a specific security component."""
        return self.security.get(component, {})

class PerformanceConfig:
    """Performance configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_performance_config()
    
    def _load_performance_config(self):
        """Load performance configuration from environment or defaults."""
        self.performance = {
            'workers': {
                'count': self.settings.WORKER_COUNT,
                'max_requests': self.settings.MAX_REQUESTS,
                'max_requests_jitter': self.settings.MAX_REQUESTS_JITTER
            },
            'timeouts': {
                'keep_alive': self.settings.TIMEOUT_KEEP_ALIVE,
                'graceful_shutdown': self.settings.TIMEOUT_GRACEFUL_SHUTDOWN
            },
            'caching': {
                'type': self.settings.CACHE_TYPE,
                'redis_url': self.settings.CACHE_REDIS_URL,
                'default_timeout': self.settings.CACHE_DEFAULT_TIMEOUT,
                'key_prefix': self.settings.CACHE_KEY_PREFIX
            }
        }
    
    def get_performance_config(self, component: str) -> Dict[str, Any]:
        """Get configuration for a specific performance component."""
        return self.performance.get(component, {})

class MonitoringConfig:
    """Monitoring configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_monitoring_config()
    
    def _load_monitoring_config(self):
        """Load monitoring configuration from environment or defaults."""
        self.monitoring = {
            'metrics': {
                'enabled': self.settings.METRICS_ENABLED,
                'provider': self.settings.METRICS_PROVIDER,
                'host': self.settings.METRICS_HOST,
                'port': self.settings.METRICS_PORT,
                'prefix': self.settings.METRICS_PREFIX,
                'labels': self.settings.METRICS_LABELS,
                'buckets': self.settings.METRICS_BUCKETS
            },
            'apm': {
                'enabled': self.settings.ENABLE_APM,
                'server_url': self.settings.APM_SERVER_URL,
                'service_name': self.settings.APM_SERVICE_NAME,
                'environment': self.settings.APM_ENVIRONMENT
            },
            'tracing': {
                'enabled': self.settings.ENABLE_TRACING,
                'service_name': self.settings.TRACING_SERVICE_NAME,
                'sampling_rate': self.settings.TRACING_SAMPLING_RATE
            },
            'profiling': {
                'enabled': self.settings.ENABLE_PROFILING,
                'interval': self.settings.PROFILING_INTERVAL,
                'duration': self.settings.PROFILING_DURATION
            }
        }
    
    def get_monitoring_config(self, component: str) -> Dict[str, Any]:
        """Get configuration for a specific monitoring component."""
        return self.monitoring.get(component, {})

class DeploymentConfig:
    """Deployment configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_deployment_config()
    
    def _load_deployment_config(self):
        """Load deployment configuration from environment or defaults."""
        self.deployment = {
            'environment': self.settings.DEPLOYMENT_ENVIRONMENT,
            'version': self.settings.DEPLOYMENT_VERSION,
            'region': self.settings.DEPLOYMENT_REGION,
            'zone': self.settings.DEPLOYMENT_ZONE,
            'instance': self.settings.DEPLOYMENT_INSTANCE,
            'tags': self.settings.DEPLOYMENT_TAGS,
            'service_discovery': {
                'enabled': self.settings.SERVICE_DISCOVERY_ENABLED,
                'type': self.settings.SERVICE_DISCOVERY_TYPE,
                'host': self.settings.SERVICE_DISCOVERY_HOST,
                'port': self.settings.SERVICE_DISCOVERY_PORT,
                'ttl': self.settings.SERVICE_DISCOVERY_TTL,
                'tags': self.settings.SERVICE_DISCOVERY_TAGS,
                'meta': self.settings.SERVICE_DISCOVERY_META
            }
        }
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration."""
        return self.deployment

class FeatureFlagConfig:
    """Feature flag configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_feature_flag_config()
    
    def _load_feature_flag_config(self):
        """Load feature flag configuration from environment or defaults."""
        self.feature_flags = {
            'enabled': self.settings.FEATURE_FLAGS_ENABLED,
            'provider': self.settings.FEATURE_FLAGS_PROVIDER,
            'default_value': self.settings.FEATURE_FLAGS_DEFAULT_VALUE,
            'cache_ttl': self.settings.FEATURE_FLAGS_CACHE_TTL,
            'refresh_interval': self.settings.FEATURE_FLAGS_REFRESH_INTERVAL
        }
    
    def get_feature_flag_config(self) -> Dict[str, Any]:
        """Get feature flag configuration."""
        return self.feature_flags

class AnalyticsConfig:
    """Analytics configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_analytics_config()
    
    def _load_analytics_config(self):
        """Load analytics configuration from environment or defaults."""
        self.analytics = {
            'enabled': self.settings.ANALYTICS_ENABLED,
            'provider': self.settings.ANALYTICS_PROVIDER,
            'api_key': self.settings.ANALYTICS_API_KEY,
            'project_id': self.settings.ANALYTICS_PROJECT_ID,
            'environment': self.settings.ANALYTICS_ENVIRONMENT,
            'sample_rate': self.settings.ANALYTICS_SAMPLE_RATE,
            'ab_testing': {
                'enabled': self.settings.AB_TESTING_ENABLED,
                'provider': self.settings.AB_TESTING_PROVIDER,
                'default_variant': self.settings.AB_TESTING_DEFAULT_VARIANT,
                'sample_rate': self.settings.AB_TESTING_SAMPLE_RATE,
                'min_sample_size': self.settings.AB_TESTING_MIN_SAMPLE_SIZE
            }
        }
    
    def get_analytics_config(self) -> Dict[str, Any]:
        """Get analytics configuration."""
        return self.analytics

class AlertConfig:
    """Alert configuration settings."""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
        self._load_alert_config()
    
    def _load_alert_config(self):
        """Load alert configuration from environment or defaults."""
        self.alerts = {
            'enabled': self.settings.ALERTS_ENABLED,
            'provider': self.settings.ALERTS_PROVIDER,
            'api_key': self.settings.ALERTS_API_KEY,
            'service_key': self.settings.ALERTS_SERVICE_KEY,
            'environment': self.settings.ALERTS_ENVIRONMENT,
            'severity_levels': self.settings.ALERTS_SEVERITY_LEVELS,
            'circuit_breaker': {
                'enabled': self.settings.CIRCUIT_BREAKER_ENABLED,
                'failure_threshold': self.settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                'recovery_timeout': self.settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
                'half_open_max_calls': self.settings.CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS,
                'excluded_exceptions': self.settings.CIRCUIT_BREAKER_EXCLUDED_EXCEPTIONS
            }
        }
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alert configuration."""
        return self.alerts

# Create settings instance at module level
@lru_cache()
def get_settings() -> 'Settings':
    """Get cached settings instance."""
    return Settings()

# Export settings instance
settings = get_settings()

class DistrictRole(str, Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
    HEALTH_STAFF = "health_staff"
    PE_STAFF = "pe_staff" 