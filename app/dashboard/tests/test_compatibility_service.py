"""
Tests for the compatibility service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import semver

from app.dashboard.services.compatibility_service import CompatibilityService
from app.dashboard.models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTIntegration,
    GPTCategory,
    GPTType
)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def compatibility_service(mock_db):
    return CompatibilityService(mock_db)

@pytest.fixture
def sample_gpt():
    return Mock(
        id="gpt-1",
        name="Math Teacher",
        category=GPTCategory.TEACHER,
        type=GPTType.MATH_TEACHER,
        version="1.0.0",
        requirements={
            "dependencies": {
                "numpy": "^1.20.0",
                "pandas": "^1.3.0"
            },
            "integrations": ["lms", "analytics"],
            "resources": {
                "memory": 2.0,
                "cpu": 1.0
            },
            "integration_requirements": {
                "lms": {
                    "config": {
                        "api_key": {"type": "string"},
                        "max_students": {"type": "number"}
                    },
                    "permissions": ["read", "write"]
                }
            }
        }
    )

@pytest.fixture
def sample_integrations():
    return [
        Mock(
            id="int-1",
            integration_type="lms",
            is_active=True,
            configuration={
                "api_key": "test-key",
                "max_students": 100,
                "permissions": ["read", "write"]
            }
        ),
        Mock(
            id="int-2",
            integration_type="analytics",
            is_active=False,
            configuration={}
        )
    ]

@pytest.fixture
def target_environment():
    return {
        "numpy": "1.21.0",
        "pandas": "1.3.2",
        "memory": 4.0,
        "cpu": 2.0
    }

async def test_check_compatibility(
    compatibility_service,
    mock_db,
    sample_gpt,
    sample_integrations,
    target_environment
):
    """Test compatibility checking."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_gpt
    mock_db.query.return_value.filter.return_value.all.return_value = sample_integrations

    # Test compatibility check
    result = await compatibility_service.check_compatibility(
        gpt_id="gpt-1",
        target_environment=target_environment
    )
    
    assert result["status"] == "success"
    assert "compatibility_score" in result
    assert "checks" in result
    assert "recommendations" in result
    
    # Verify checks
    checks = result["checks"]
    assert "dependencies" in checks
    assert "version" in checks
    assert "integrations" in checks
    assert "resources" in checks
    
    # Verify dependency check
    deps = checks["dependencies"]
    assert deps["status"] == "passed"
    assert len(deps["satisfied_dependencies"]) == 2
    assert not deps["compatibility_issues"]
    
    # Verify integration check
    integrations = checks["integrations"]
    assert len(integrations["integration_issues"]) == 1  # Inactive analytics
    assert len(integrations["available_integrations"]) == 2

async def test_get_compatible_gpts(
    compatibility_service,
    mock_db,
    sample_gpt
):
    """Test getting compatible GPTs."""
    # Create target GPTs
    target_gpts = [
        Mock(
            id="gpt-2",
            name="Science Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.SCIENCE_TEACHER,
            version="1.0.0",
            requirements={
                "integrations": ["lms"],
                "resources": {"memory": 0.8}
            }
        ),
        Mock(
            id="gpt-3",
            name="History Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.HISTORY_TEACHER,
            version="2.0.0",  # Incompatible version
            requirements={
                "integrations": ["lms"],
                "resources": {"memory": 1.0}
            }
        )
    ]

    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_gpt
    mock_db.query.return_value.filter.return_value.all.return_value = target_gpts

    # Test getting compatible GPTs
    result = await compatibility_service.get_compatible_gpts("gpt-1")
    
    assert result["status"] == "success"
    assert "compatible_gpts" in result
    assert "total_compatible" in result
    assert "compatibility_summary" in result
    
    # Verify only compatible GPT is included
    compatible_gpts = result["compatible_gpts"]
    assert len(compatible_gpts) == 1
    assert "gpt-2" in compatible_gpts
    assert "gpt-3" not in compatible_gpts

async def test_validate_integration_requirements(
    compatibility_service,
    mock_db,
    sample_gpt,
    sample_integrations
):
    """Test integration requirement validation."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        sample_gpt,
        sample_integrations[0]
    ]

    # Test validation
    result = await compatibility_service.validate_integration_requirements(
        gpt_id="gpt-1",
        integration_type="lms"
    )
    
    assert result["status"] == "success"
    assert result["is_valid"]
    assert "validation_results" in result
    assert "recommendations" in result
    
    # Verify validation checks
    validation = result["validation_results"]
    assert validation["integration_type"] == "lms"
    assert validation["total_checks"] > 0
    assert validation["passed_checks"] == validation["total_checks"]

def test_check_dependencies(compatibility_service, sample_gpt, target_environment):
    """Test dependency checking."""
    result = compatibility_service._check_dependencies(sample_gpt, target_environment)
    
    assert result["status"] == "passed"
    assert len(result["satisfied_dependencies"]) == 2
    assert not result["compatibility_issues"]
    assert result["score"] == 1.0
    
    # Test with missing dependency
    env_missing = {k: v for k, v in target_environment.items() if k != "numpy"}
    result = compatibility_service._check_dependencies(sample_gpt, env_missing)
    
    assert result["status"] == "failed"
    assert len(result["compatibility_issues"]) == 1
    assert result["score"] < 1.0

def test_check_version_compatibility(compatibility_service, sample_gpt):
    """Test version compatibility checking."""
    result = compatibility_service._check_version_compatibility(sample_gpt)
    
    assert result["status"] == "passed"
    assert result["is_compatible"]
    assert result["score"] == 1.0
    assert not result["issues"]
    
    # Test with incompatible version
    sample_gpt.version = "2.0.0"
    result = compatibility_service._check_version_compatibility(sample_gpt)
    
    assert result["status"] == "failed"
    assert not result["is_compatible"]
    assert result["score"] == 0.0
    assert len(result["issues"]) == 1

def test_check_integrations(compatibility_service, sample_gpt, sample_integrations):
    """Test integration checking."""
    result = compatibility_service._check_integrations(sample_gpt, sample_integrations)
    
    assert result["status"] == "failed"  # Due to inactive analytics
    assert len(result["available_integrations"]) == 2
    assert not result["missing_integrations"]
    assert len(result["integration_issues"]) == 1
    assert 0 < result["score"] < 1
    
    # Test with missing integration
    sample_gpt.requirements["integrations"].append("missing")
    result = compatibility_service._check_integrations(sample_gpt, sample_integrations)
    
    assert result["status"] == "failed"
    assert len(result["missing_integrations"]) == 1
    assert result["score"] < 1.0

def test_check_resource_requirements(compatibility_service, sample_gpt, target_environment):
    """Test resource requirement checking."""
    result = compatibility_service._check_resource_requirements(
        sample_gpt,
        target_environment
    )
    
    assert result["status"] == "passed"
    assert len(result["satisfied_resources"]) == 2
    assert not result["resource_issues"]
    assert result["score"] == 1.0
    
    # Test with insufficient resources
    env_insufficient = {
        **target_environment,
        "memory": 1.0  # Less than required
    }
    result = compatibility_service._check_resource_requirements(
        sample_gpt,
        env_insufficient
    )
    
    assert result["status"] == "failed"
    assert len(result["resource_issues"]) == 1
    assert result["score"] < 1.0

def test_check_gpt_compatibility(compatibility_service, sample_gpt):
    """Test GPT compatibility checking."""
    target_gpt = Mock(
        id="gpt-2",
        version="1.0.0",
        requirements={
            "integrations": ["lms"],
            "resources": {"memory": 0.8}
        }
    )
    
    result = compatibility_service._check_gpt_compatibility(sample_gpt, target_gpt)
    
    assert result["is_compatible"]
    assert result["score"] > 0.8
    assert "checks" in result["details"]
    assert "resource_conflicts" in result["details"]
    assert "shared_integrations" in result["details"]
    
    # Test with incompatible GPT
    target_gpt.version = "2.0.0"
    target_gpt.requirements["resources"]["memory"] = 0.9  # Creates conflict
    result = compatibility_service._check_gpt_compatibility(sample_gpt, target_gpt)
    
    assert not result["is_compatible"]
    assert result["score"] < 0.8
    assert len(result["details"]["resource_conflicts"]) > 0

def test_validate_integration(compatibility_service, sample_gpt, sample_integrations):
    """Test integration validation."""
    result = compatibility_service._validate_integration(
        sample_gpt,
        sample_integrations[0]
    )
    
    assert result["integration_type"] == "lms"
    assert result["total_checks"] > 0
    assert result["passed_checks"] == result["total_checks"]
    
    # Test with invalid configuration
    invalid_integration = Mock(
        integration_type="lms",
        configuration={
            "api_key": 123,  # Should be string
            "max_students": "100"  # Should be number
        }
    )
    result = compatibility_service._validate_integration(sample_gpt, invalid_integration)
    
    assert result["passed_checks"] < result["total_checks"]

def test_calculate_compatibility_score(compatibility_service):
    """Test compatibility score calculation."""
    checks = [
        {"score": 1.0},  # Dependencies
        {"score": 1.0},  # Version
        {"score": 0.5},  # Integrations
        {"score": 0.8}   # Resources
    ]
    
    score = compatibility_service._calculate_compatibility_score(checks)
    assert 0 <= score <= 1
    assert score == 0.3 * 1.0 + 0.2 * 1.0 + 0.3 * 0.5 + 0.2 * 0.8

def test_generate_compatibility_recommendations(compatibility_service):
    """Test recommendation generation."""
    checks = [
        {
            "status": "failed",
            "compatibility_issues": [
                {"dependency": "numpy", "installed_version": "1.19.0"}
            ]
        },
        {"status": "passed"},
        {
            "status": "failed",
            "missing_integrations": ["analytics"],
            "integration_issues": [{"integration": "lms", "message": "inactive"}]
        },
        {
            "status": "failed",
            "resource_issues": [{"resource": "memory", "available": 1, "required": 2}]
        }
    ]
    
    recommendations = compatibility_service._generate_compatibility_recommendations(checks)
    assert len(recommendations) > 0
    
    # Verify recommendation structure
    for rec in recommendations:
        assert "type" in rec
        assert "priority" in rec
        assert "message" in rec

def test_generate_compatibility_summary(compatibility_service):
    """Test compatibility summary generation."""
    compatibility_results = {
        "gpt-1": {
            "category": "TEACHER",
            "type": "MATH_TEACHER",
            "compatibility_score": 0.9
        },
        "gpt-2": {
            "category": "TEACHER",
            "type": "SCIENCE_TEACHER",
            "compatibility_score": 0.7
        }
    }
    
    summary = compatibility_service._generate_compatibility_summary(compatibility_results)
    
    assert "average_compatibility_score" in summary
    assert "compatibility_by_category" in summary
    assert "compatibility_by_type" in summary
    assert "high_compatibility_count" in summary
    
    assert summary["average_compatibility_score"] == 0.8
    assert summary["compatibility_by_category"]["TEACHER"] == 2
    assert summary["high_compatibility_count"] == 1

def test_generate_integration_recommendations(compatibility_service):
    """Test integration recommendation generation."""
    validation_results = {
        "checks": [
            {
                "check": "config_api_key",
                "status": "failed",
                "message": "Missing required configuration: api_key"
            },
            {
                "check": "permission_write",
                "status": "failed",
                "message": "Missing required permission: write"
            }
        ]
    }
    
    recommendations = compatibility_service._generate_integration_recommendations(
        validation_results
    )
    
    assert len(recommendations) == 2
    
    # Verify recommendation types
    rec_types = [r["type"] for r in recommendations]
    assert "configuration" in rec_types
    assert "permission" in rec_types 