import pytest
from datetime import datetime, timedelta
from app.core.security.compliance_engine import ComplianceEngine, DataClassification
from app.core.security.regional_compliance import Region, DataProtectionRegulation

@pytest.fixture
def compliance_engine():
    return ComplianceEngine()

@pytest.fixture
def sample_student_data():
    return {
        "student_id": "12345",
        "name": "John Doe",
        "age": 15,
        "grade": "10",
        "email": "john.doe@example.com"
    }

@pytest.mark.asyncio
async def test_encrypt_decrypt_north_america(compliance_engine, sample_student_data):
    """Test encryption and decryption with North American compliance"""
    # Encrypt data
    encrypted_data = await compliance_engine.encrypt_student_data(
        sample_student_data,
        DataClassification.SENSITIVE,
        Region.NORTH_AMERICA.value
    )
    
    # Verify encryption structure
    assert all(key in encrypted_data for key in sample_student_data.keys())
    assert all('value' in encrypted_data[key] for key in encrypted_data)
    assert all('classification' in encrypted_data[key] for key in encrypted_data)
    assert all('encryption_timestamp' in encrypted_data[key] for key in encrypted_data)
    assert all('region' in encrypted_data[key] for key in encrypted_data)
    
    # Decrypt data
    decrypted_data = await compliance_engine.decrypt_student_data(
        encrypted_data,
        "admin",
        ["read", "write"],
        Region.NORTH_AMERICA.value
    )
    
    # Verify decrypted data matches original
    assert decrypted_data == sample_student_data

@pytest.mark.asyncio
async def test_encrypt_decrypt_europe(compliance_engine, sample_student_data):
    """Test encryption and decryption with European compliance"""
    # Encrypt data
    encrypted_data = await compliance_engine.encrypt_student_data(
        sample_student_data,
        DataClassification.SENSITIVE,
        Region.EUROPE.value
    )
    
    # Verify encryption structure
    assert all(key in encrypted_data for key in sample_student_data.keys())
    assert all('value' in encrypted_data[key] for key in encrypted_data)
    assert all('classification' in encrypted_data[key] for key in encrypted_data)
    assert all('encryption_timestamp' in encrypted_data[key] for key in encrypted_data)
    assert all('region' in encrypted_data[key] for key in encrypted_data)
    
    # Decrypt data
    decrypted_data = await compliance_engine.decrypt_student_data(
        encrypted_data,
        "admin",
        ["read", "write"],
        Region.EUROPE.value
    )
    
    # Verify decrypted data matches original
    assert decrypted_data == sample_student_data

@pytest.mark.asyncio
async def test_audit_log_generation(compliance_engine):
    """Test audit log generation with regional compliance"""
    # Generate audit log for North America
    audit_log = await compliance_engine.generate_audit_log(
        "user123",
        "data_access",
        "student_records",
        Region.NORTH_AMERICA.value
    )
    
    # Verify audit log structure
    assert 'timestamp' in audit_log
    assert 'user_id' in audit_log
    assert 'action' in audit_log
    assert 'data_accessed' in audit_log
    assert 'region' in audit_log
    assert 'compliance_requirements' in audit_log
    
    # Verify timestamp format
    datetime.fromisoformat(audit_log['timestamp'])

@pytest.mark.asyncio
async def test_parental_consent_validation(compliance_engine):
    """Test parental consent validation with regional compliance"""
    # Test North America
    result = await compliance_engine.validate_parental_consent(
        "student123",
        "data_access",
        Region.NORTH_AMERICA.value
    )
    assert isinstance(result, bool)
    
    # Test Europe
    result = await compliance_engine.validate_parental_consent(
        "student123",
        "data_access",
        Region.EUROPE.value
    )
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_mfa_token_generation(compliance_engine):
    """Test MFA token generation with regional compliance"""
    # Test North America
    token = await compliance_engine.generate_mfa_token(
        "user123",
        Region.NORTH_AMERICA.value
    )
    assert isinstance(token, str)
    
    # Test Europe
    token = await compliance_engine.generate_mfa_token(
        "user123",
        Region.EUROPE.value
    )
    assert isinstance(token, str)

@pytest.mark.asyncio
async def test_compliance_report_generation(compliance_engine):
    """Test compliance report generation"""
    # Test North America
    report = await compliance_engine.get_compliance_report(Region.NORTH_AMERICA.value)
    assert 'region' in report
    assert 'timestamp' in report
    assert 'data_protection_status' in report
    assert 'content_restrictions_status' in report
    assert 'privacy_settings_status' in report
    assert 'audit_requirements_status' in report
    
    # Test Europe
    report = await compliance_engine.get_compliance_report(Region.EUROPE.value)
    assert 'region' in report
    assert 'timestamp' in report
    assert 'data_protection_status' in report
    assert 'content_restrictions_status' in report
    assert 'privacy_settings_status' in report
    assert 'audit_requirements_status' in report

@pytest.mark.asyncio
async def test_invalid_region_handling(compliance_engine, sample_student_data):
    """Test handling of invalid regions"""
    with pytest.raises(ValueError):
        await compliance_engine.encrypt_student_data(
            sample_student_data,
            DataClassification.SENSITIVE,
            "invalid_region"
        )
    
    with pytest.raises(ValueError):
        await compliance_engine.generate_audit_log(
            "user123",
            "data_access",
            "student_records",
            "invalid_region"
        )
    
    with pytest.raises(ValueError):
        await compliance_engine.validate_parental_consent(
            "student123",
            "data_access",
            "invalid_region"
        )

@pytest.mark.asyncio
async def test_access_permission_validation(compliance_engine):
    """Test access permission validation"""
    # Test public data access
    assert compliance_engine._check_access_permission(
        DataClassification.PUBLIC.value,
        "student",
        ["read"]
    )
    
    # Test internal data access
    assert not compliance_engine._check_access_permission(
        DataClassification.INTERNAL.value,
        "student",
        ["read"]
    )
    assert compliance_engine._check_access_permission(
        DataClassification.INTERNAL.value,
        "teacher",
        ["read"]
    )
    
    # Test sensitive data access
    assert not compliance_engine._check_access_permission(
        DataClassification.SENSITIVE.value,
        "teacher",
        ["read"]
    )
    assert compliance_engine._check_access_permission(
        DataClassification.SENSITIVE.value,
        "admin",
        ["read"]
    ) 