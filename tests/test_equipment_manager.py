import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.physical_education.services.equipment_manager import EquipmentManager
from app.services.physical_education.models.safety import EquipmentCheck

@pytest.fixture
def equipment_manager():
    return EquipmentManager()

@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db

@pytest.fixture
def mock_equipment_check_data():
    return {
        "class_id": "class123",
        "equipment_id": "equipment123",
        "maintenance_status": "good",
        "damage_status": "none",
        "age_status": "new",
        "last_maintenance": datetime.utcnow() - timedelta(days=30),
        "purchase_date": datetime.utcnow() - timedelta(days=90),
        "max_age_years": 5,
        "metadata": {"notes": "Test equipment check"}
    }

@pytest.fixture
def mock_equipment_check():
    check = Mock(spec=EquipmentCheck)
    check.id = "check123"
    check.class_id = "class123"
    check.equipment_id = "equipment123"
    check.check_date = datetime.utcnow()
    check.maintenance_status = "good"
    check.damage_status = "none"
    check.age_status = "new"
    check.last_maintenance = datetime.utcnow() - timedelta(days=30)
    check.purchase_date = datetime.utcnow() - timedelta(days=90)
    check.max_age_years = 5
    check.metadata = {"notes": "Test equipment check"}
    return check

# Tests for initialization
def test_equipment_manager_initialization(equipment_manager):
    assert equipment_manager.maintenance_statuses
    assert equipment_manager.damage_statuses
    assert equipment_manager.age_statuses

# Tests for create_equipment_check
@pytest.mark.asyncio
async def test_create_equipment_check_success(equipment_manager, mock_db, mock_equipment_check_data):
    with patch.object(mock_db, 'add') as mock_add, \
         patch.object(mock_db, 'commit') as mock_commit, \
         patch.object(mock_db, 'refresh') as mock_refresh:
        
        result = await equipment_manager.create_equipment_check(
            db=mock_db,
            **mock_equipment_check_data
        )
        
        assert result["success"] is True
        assert "check_id" in result
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_equipment_check_invalid_status(equipment_manager, mock_db, mock_equipment_check_data):
    mock_equipment_check_data["maintenance_status"] = "invalid_status"
    
    result = await equipment_manager.create_equipment_check(
        db=mock_db,
        **mock_equipment_check_data
    )
    
    assert result["success"] is False
    assert "Invalid maintenance status" in result["message"]

# Tests for get_equipment_check
@pytest.mark.asyncio
async def test_get_equipment_check_success(equipment_manager, mock_db, mock_equipment_check):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_equipment_check
        
        result = await equipment_manager.get_equipment_check(
            check_id="check123",
            db=mock_db
        )
        
        assert result == mock_equipment_check

@pytest.mark.asyncio
async def test_get_equipment_check_not_found(equipment_manager, mock_db):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        
        result = await equipment_manager.get_equipment_check(
            check_id="nonexistent",
            db=mock_db
        )
        
        assert result is None

# Tests for get_equipment_checks
@pytest.mark.asyncio
async def test_get_equipment_checks_with_filters(equipment_manager, mock_db, mock_equipment_check):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [mock_equipment_check]
        
        result = await equipment_manager.get_equipment_checks(
            class_id="class123",
            equipment_id="equipment123",
            maintenance_status="good",
            damage_status="none",
            age_status="new",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            db=mock_db
        )
        
        assert len(result) == 1
        assert result[0] == mock_equipment_check

# Tests for update_equipment_check
@pytest.mark.asyncio
async def test_update_equipment_check_success(equipment_manager, mock_db, mock_equipment_check):
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'commit') as mock_commit, \
         patch.object(mock_db, 'refresh') as mock_refresh:
        
        mock_query.return_value.filter.return_value.first.return_value = mock_equipment_check
        
        result = await equipment_manager.update_equipment_check(
            check_id="check123",
            update_data={"maintenance_status": "needs_inspection"},
            db=mock_db
        )
        
        assert result["success"] is True
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()

# Tests for delete_equipment_check
@pytest.mark.asyncio
async def test_delete_equipment_check_success(equipment_manager, mock_db, mock_equipment_check):
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'delete') as mock_delete, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = mock_equipment_check
        
        result = await equipment_manager.delete_equipment_check(
            check_id="check123",
            db=mock_db
        )
        
        assert result["success"] is True
        mock_delete.assert_called_once()
        mock_commit.assert_called_once()

# Tests for get_equipment_statistics
@pytest.mark.asyncio
async def test_get_equipment_statistics(equipment_manager, mock_db):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [
            Mock(maintenance_status="good"),
            Mock(maintenance_status="needs_inspection"),
            Mock(maintenance_status="needs_repair")
        ]
        
        result = await equipment_manager.get_equipment_statistics(
            class_id="class123",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            db=mock_db
        )
        
        assert "total_checks" in result
        assert "maintenance_status_distribution" in result

# Tests for bulk operations
@pytest.mark.asyncio
async def test_bulk_update_equipment_checks(equipment_manager, mock_db):
    updates = [
        {"check_id": "check1", "maintenance_status": "needs_inspection"},
        {"check_id": "check2", "maintenance_status": "good"}
    ]
    
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = Mock()
        
        result = await equipment_manager.bulk_update_equipment_checks(
            updates=updates,
            db=mock_db
        )
        
        assert "successful_updates" in result
        assert "failed_updates" in result

@pytest.mark.asyncio
async def test_bulk_delete_equipment_checks(equipment_manager, mock_db):
    check_ids = ["check1", "check2"]
    
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'delete') as mock_delete, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = Mock()
        
        result = await equipment_manager.bulk_delete_equipment_checks(
            check_ids=check_ids,
            db=mock_db
        )
        
        assert "successful_deletions" in result
        assert "failed_deletions" in result

# Tests for error handling
@pytest.mark.asyncio
async def test_error_handling_database_error(equipment_manager, mock_db):
    with patch.object(mock_db, 'query', side_effect=Exception("Database error")):
        result = await equipment_manager.get_equipment_check(
            check_id="check123",
            db=mock_db
        )
        
        assert result is None

@pytest.mark.asyncio
async def test_error_handling_validation_error(equipment_manager, mock_db, mock_equipment_check_data):
    mock_equipment_check_data["maintenance_status"] = "invalid_status"
    
    result = await equipment_manager.create_equipment_check(
        db=mock_db,
        **mock_equipment_check_data
    )
    
    assert result["success"] is False
    assert "Invalid maintenance status" in result["message"] 