"""
Test Configuration Module

This module contains tests for the configuration settings and functionality.
"""

import pytest
import os
from datetime import datetime
from app.core.config import (
    Settings,
    get_settings,
    ServiceConfig,
    SecurityConfig,
    PerformanceConfig,
    MonitoringConfig,
    DeploymentConfig,
    FeatureFlagConfig,
    AnalyticsConfig,
    AlertConfig
)

@pytest.fixture
def settings():
    """Fixture for settings instance."""
    # Clear the settings cache before each test
    get_settings.cache_clear()
    return get_settings()

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set mock environment variables."""
    # Clear any existing environment variables
    for key in ["DATABASE_URL", "REDIS_URL", "MINIO_ENDPOINT", "OPENAI_API_KEY", 
                "JWT_SECRET_KEY", "DISTRICT_NAME", "DISTRICT_ID", "DISTRICT_DOMAIN"]:
        monkeypatch.delenv(key, raising=False)
    
    # Set new environment variables
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("MINIO_ENDPOINT", "localhost:9000")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("DISTRICT_NAME", "Test District")
    monkeypatch.setenv("DISTRICT_ID", "TEST")
    monkeypatch.setenv("DISTRICT_DOMAIN", "test.com")

class TestSettings:
    def test_settings_initialization(self, settings):
        """Test settings initialization."""
        assert isinstance(settings, Settings)
        assert settings.DATABASE_URL is not None
        assert settings.REDIS_URL is not None
        assert settings.MINIO_ENDPOINT is not None

    def test_settings_caching(self):
        """Test settings caching functionality."""
        # Clear the cache first
        get_settings.cache_clear()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2  # Should return cached instance

    def test_environment_variables(self, mock_env_vars):
        """Test environment variable loading."""
        # Clear the cache first
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.DATABASE_URL == "postgresql://test:test@localhost:5432/test"
        assert settings.REDIS_URL == "redis://localhost:6379/0"
        assert settings.MINIO_ENDPOINT == "localhost:9000"
        assert settings.DISTRICT_NAME == "Test District"
        assert settings.DISTRICT_ID == "TEST"
        assert settings.DISTRICT_DOMAIN == "test.com"

    def test_validation_rules(self):
        """Test settings validation rules."""
        # Test upload types validation
        with pytest.raises(ValueError):
            Settings(ALLOWED_UPLOAD_TYPES=[])

        # Test health check endpoints validation
        with pytest.raises(ValueError):
            Settings(HEALTH_CHECK_ENDPOINTS=[])

        # Test backup retention validation
        with pytest.raises(ValueError):
            Settings(BACKUP_RETENTION_DAYS=0)

        # Test upload size validation
        with pytest.raises(ValueError):
            Settings(MAX_UPLOAD_SIZE=500)  # Less than 1KB

        # Test service discovery type validation
        with pytest.raises(ValueError):
            Settings(SERVICE_DISCOVERY_TYPE="invalid")

        # Test feature flags provider validation
        with pytest.raises(ValueError):
            Settings(FEATURE_FLAGS_PROVIDER="invalid")

        # Test A/B testing provider validation
        with pytest.raises(ValueError):
            Settings(AB_TESTING_PROVIDER="invalid")

        # Test analytics provider validation
        with pytest.raises(ValueError):
            Settings(ANALYTICS_PROVIDER="invalid")

        # Test metrics provider validation
        with pytest.raises(ValueError):
            Settings(METRICS_PROVIDER="invalid")

        # Test alerts provider validation
        with pytest.raises(ValueError):
            Settings(ALERTS_PROVIDER="invalid")

        # Test deployment environment validation
        with pytest.raises(ValueError):
            Settings(DEPLOYMENT_ENVIRONMENT="invalid")

        # Test A/B testing sample rate validation
        with pytest.raises(ValueError):
            Settings(AB_TESTING_SAMPLE_RATE=1.5)

        # Test analytics sample rate validation
        with pytest.raises(ValueError):
            Settings(ANALYTICS_SAMPLE_RATE=-0.1)

        # Test metrics buckets validation
        with pytest.raises(ValueError):
            Settings(METRICS_BUCKETS=[])

        # Test alerts severity levels validation
        with pytest.raises(ValueError):
            Settings(ALERTS_SEVERITY_LEVELS=["invalid"])

class TestServiceConfig:
    def test_service_config_initialization(self, settings):
        """Test service configuration initialization."""
        service_config = ServiceConfig(settings)
        assert isinstance(service_config, ServiceConfig)
        assert "database" in service_config.services
        assert "redis" in service_config.services
        assert "minio" in service_config.services

    def test_get_service_config(self, settings):
        """Test getting specific service configuration."""
        service_config = ServiceConfig(settings)
        db_config = service_config.get_service_config("database")
        assert isinstance(db_config, dict)
        assert "url" in db_config
        assert "pool_size" in db_config

class TestSecurityConfig:
    def test_security_config_initialization(self, settings):
        """Test security configuration initialization."""
        security_config = SecurityConfig(settings)
        assert isinstance(security_config, SecurityConfig)
        assert "jwt" in security_config.security
        assert "password" in security_config.security
        assert "session" in security_config.security

    def test_get_security_config(self, settings):
        """Test getting specific security configuration."""
        security_config = SecurityConfig(settings)
        jwt_config = security_config.get_security_config("jwt")
        assert isinstance(jwt_config, dict)
        assert "secret_key" in jwt_config
        assert "algorithm" in jwt_config

class TestPerformanceConfig:
    def test_performance_config_initialization(self, settings):
        """Test performance configuration initialization."""
        perf_config = PerformanceConfig(settings)
        assert isinstance(perf_config, PerformanceConfig)
        assert "workers" in perf_config.performance
        assert "timeouts" in perf_config.performance
        assert "caching" in perf_config.performance

    def test_get_performance_config(self, settings):
        """Test getting specific performance configuration."""
        perf_config = PerformanceConfig(settings)
        workers_config = perf_config.get_performance_config("workers")
        assert isinstance(workers_config, dict)
        assert "count" in workers_config
        assert "max_requests" in workers_config

class TestMonitoringConfig:
    def test_monitoring_config_initialization(self, settings):
        """Test monitoring configuration initialization."""
        monitoring_config = MonitoringConfig(settings)
        assert isinstance(monitoring_config, MonitoringConfig)
        assert "metrics" in monitoring_config.monitoring
        assert "apm" in monitoring_config.monitoring
        assert "tracing" in monitoring_config.monitoring

    def test_get_monitoring_config(self, settings):
        """Test getting specific monitoring configuration."""
        monitoring_config = MonitoringConfig(settings)
        metrics_config = monitoring_config.get_monitoring_config("metrics")
        assert isinstance(metrics_config, dict)
        assert "enabled" in metrics_config
        assert "provider" in metrics_config

class TestDeploymentConfig:
    def test_deployment_config_initialization(self, settings):
        """Test deployment configuration initialization."""
        deployment_config = DeploymentConfig(settings)
        assert isinstance(deployment_config, DeploymentConfig)
        assert "environment" in deployment_config.deployment
        assert "version" in deployment_config.deployment
        assert "region" in deployment_config.deployment

    def test_get_deployment_config(self, settings):
        """Test getting deployment configuration."""
        deployment_config = DeploymentConfig(settings)
        config = deployment_config.get_deployment_config()
        assert isinstance(config, dict)
        assert "environment" in config
        assert "version" in config
        assert "region" in config

class TestFeatureFlagConfig:
    def test_feature_flag_config_initialization(self, settings):
        """Test feature flag configuration initialization."""
        feature_flag_config = FeatureFlagConfig(settings)
        assert isinstance(feature_flag_config, FeatureFlagConfig)
        assert "enabled" in feature_flag_config.feature_flags
        assert "provider" in feature_flag_config.feature_flags

    def test_get_feature_flag_config(self, settings):
        """Test getting feature flag configuration."""
        feature_flag_config = FeatureFlagConfig(settings)
        config = feature_flag_config.get_feature_flag_config()
        assert isinstance(config, dict)
        assert "enabled" in config
        assert "provider" in config

class TestAnalyticsConfig:
    def test_analytics_config_initialization(self, settings):
        """Test analytics configuration initialization."""
        analytics_config = AnalyticsConfig(settings)
        assert isinstance(analytics_config, AnalyticsConfig)
        assert "enabled" in analytics_config.analytics
        assert "provider" in analytics_config.analytics

    def test_get_analytics_config(self, settings):
        """Test getting analytics configuration."""
        analytics_config = AnalyticsConfig(settings)
        config = analytics_config.get_analytics_config()
        assert isinstance(config, dict)
        assert "enabled" in config
        assert "provider" in config

class TestAlertConfig:
    def test_alert_config_initialization(self, settings):
        """Test alert configuration initialization."""
        alert_config = AlertConfig(settings)
        assert isinstance(alert_config, AlertConfig)
        assert "enabled" in alert_config.alerts
        assert "provider" in alert_config.alerts

    def test_get_alert_config(self, settings):
        """Test getting alert configuration."""
        alert_config = AlertConfig(settings)
        config = alert_config.get_alert_config()
        assert isinstance(config, dict)
        assert "enabled" in config
        assert "provider" in config 