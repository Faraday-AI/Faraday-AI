"""
API Key model for authentication and access control.
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.shared_base import SharedBase

class KeySource(str, enum.Enum):
    """Enumeration of possible API key sources."""
    ENV = "environment"
    SHELL = "shell_script"
    DATABASE = "database"
    RENDER = "render"
    OTHER = "other"

class APIKey(SharedBase):
    """API Key model for authentication."""
    __tablename__ = "api_keys"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permissions = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    source = Column(SQLEnum(KeySource, name='key_source_enum'), nullable=False, default=KeySource.DATABASE)
    environment = Column(String)  # e.g., 'development', 'production'
    service_name = Column(String)  # e.g., 'openai', 'azure', etc.

    # Relationships
    teacher = relationship("app.models.core.user.User", foreign_keys=[user_id], back_populates="api_keys")
    created_by_teacher = relationship("app.models.core.user.User", foreign_keys=[created_by])
    rate_limits = relationship("app.models.security.rate_limit.rate_limit.RateLimit", back_populates="api_key")
    rate_limit_logs = relationship("app.models.security.rate_limit.rate_limit.RateLimitLog", back_populates="api_key")

    @classmethod
    def from_environment(cls, key: str, name: str, service_name: str, environment: str = "production"):
        """Create an API key instance from an environment variable."""
        return cls(
            key=key,
            name=name,
            source=KeySource.ENV,
            environment=environment,
            service_name=service_name,
            description=f"API key for {service_name} loaded from environment"
        )

    @classmethod
    def from_shell_script(cls, key: str, name: str, service_name: str, environment: str = "development"):
        """Create an API key instance from a shell script."""
        return cls(
            key=key,
            name=name,
            source=KeySource.SHELL,
            environment=environment,
            service_name=service_name,
            description=f"API key for {service_name} loaded from shell script"
        )

    @classmethod
    def from_render(cls, key: str, name: str, service_name: str):
        """Create an API key instance from Render environment."""
        return cls(
            key=key,
            name=name,
            source=KeySource.RENDER,
            environment="production",
            service_name=service_name,
            description=f"API key for {service_name} loaded from Render environment"
        ) 