import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session
from app.services.physical_education.services.equipment_manager import EquipmentManager
from app.services.physical_education.models.safety import EquipmentCheck

@pytest.fixture
def equipment_manager():
    """Create EquipmentManager instance for testing."""
    return EquipmentManager()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock(spec=Session)
    return db

@pytest.fixture
def sample_equipment_check():
    """Create sample equipment check data."""
    return {
        "class_id": "class1",
        "equipment_id": "eq1",
        "maintenance_status": "good",
        "damage_status": "none",
        "age_status": "new",
        "last_maintenance": datetime.now() - timedelta(days=30),
        "purchase_date": datetime.now() - timedelta(days=365),
        "max_age_years": 5,
        "metadata": {"notes": "Regular check"}
    }

@pytest.mark.asyncio
async def test_create_equipment_check(equipment_manager, mock_db, sample_equipment_check):
    """Test creating an equipment check."""
    # Mock the database session
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    
    # Create a mock EquipmentCheck object
    mock_check = MagicMock(spec=EquipmentCheck)
    mock_check.id = "check1"
    mock_db.refresh.return_value = mock_check
    
    # Test successful creation
    result = await equipment_manager.create_equipment_check(
        class_id=sample_equipment_check["class_id"],
        equipment_id=sample_equipment_check["equipment_id"],
        maintenance_status=sample_equipment_check["maintenance_status"],
        damage_status=sample_equipment_check["damage_status"],
        age_status=sample_equipment_check["age_status"],
        last_maintenance=sample_equipment_check["last_maintenance"],
        purchase_date=sample_equipment_check["purchase_date"],
        max_age_years=sample_equipment_check["max_age_years"],
        metadata=sample_equipment_check["metadata"],
        db=mock_db
    )
    
    assert result["success"] is True
    assert result["message"] == "Equipment check created successfully"
    assert result["check_id"] == "check1"
    
    # Test with invalid maintenance status
    with pytest.raises(ValueError):
        await equipment_manager.create_equipment_check(
            class_id="class1",
            equipment_id="eq1",
            maintenance_status="invalid",
            damage_status="none",
            age_status="new",
            db=mock_db
        )

@pytest.mark.asyncio
async def test_get_equipment_check(equipment_manager, mock_db):
    """Test retrieving an equipment check."""
    # Create a mock EquipmentCheck object
    mock_check = MagicMock(spec=EquipmentCheck)
    mock_check.id = "check1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_check
    
    # Test successful retrieval
    result = await equipment_manager.get_equipment_check("check1", mock_db)
    assert result == mock_check
    
    # Test with non-existent check
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = await equipment_manager.get_equipment_check("nonexistent", mock_db)
    assert result is None

@pytest.mark.asyncio
async def test_get_equipment_checks(equipment_manager, mock_db):
    """Test retrieving multiple equipment checks with filters."""
    # Create mock EquipmentCheck objects
    mock_checks = [
        MagicMock(spec=EquipmentCheck),
        MagicMock(spec=EquipmentCheck)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_checks
    
    # Test with all filters
    result = await equipment_manager.get_equipment_checks(
        class_id="class1",
        equipment_id="eq1",
        maintenance_status="good",
        damage_status="none",
        age_status="new",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        db=mock_db
    )
    
    assert len(result) == 2
    assert result == mock_checks

@pytest.mark.asyncio
async def test_update_equipment_check(equipment_manager, mock_db):
    """Test updating an equipment check."""
    # Create a mock EquipmentCheck object
    mock_check = MagicMock(spec=EquipmentCheck)
    mock_check.id = "check1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_check
    
    # Test successful update
    update_data = {
        "maintenance_status": "needs_inspection",
        "damage_status": "minor",
        "age_status": "good"
    }
    
    result = await equipment_manager.update_equipment_check("check1", update_data, mock_db)
    assert result["success"] is True
    assert result["message"] == "Equipment check updated successfully"
    
    # Test with non-existent check
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = await equipment_manager.update_equipment_check("nonexistent", update_data, mock_db)
    assert result["success"] is False
    assert result["message"] == "Equipment check not found"
    
    # Test with invalid status
    with pytest.raises(ValueError):
        await equipment_manager.update_equipment_check(
            "check1",
            {"maintenance_status": "invalid"},
            mock_db
        )

@pytest.mark.asyncio
async def test_delete_equipment_check(equipment_manager, mock_db):
    """Test deleting an equipment check."""
    # Create a mock EquipmentCheck object
    mock_check = MagicMock(spec=EquipmentCheck)
    mock_check.id = "check1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_check
    
    # Test successful deletion
    result = await equipment_manager.delete_equipment_check("check1", mock_db)
    assert result["success"] is True
    assert result["message"] == "Equipment check deleted successfully"
    
    # Test with non-existent check
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = await equipment_manager.delete_equipment_check("nonexistent", mock_db)
    assert result["success"] is False
    assert result["message"] == "Equipment check not found"

@pytest.mark.asyncio
async def test_get_equipment_statistics(equipment_manager, mock_db):
    """Test getting equipment statistics."""
    # Create mock EquipmentCheck objects
    mock_checks = [
        MagicMock(spec=EquipmentCheck),
        MagicMock(spec=EquipmentCheck)
    ]
    mock_checks[0].equipment_id = "eq1"
    mock_checks[0].maintenance_status = "good"
    mock_checks[0].damage_status = "none"
    mock_checks[0].age_status = "new"
    mock_checks[1].equipment_id = "eq2"
    mock_checks[1].maintenance_status = "needs_inspection"
    mock_checks[1].damage_status = "minor"
    mock_checks[1].age_status = "good"
    
    mock_db.query.return_value.filter.return_value.all.return_value = mock_checks
    
    # Test getting statistics
    result = await equipment_manager.get_equipment_statistics(
        class_id="class1",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        db=mock_db
    )
    
    assert "total" in result
    assert "by_equipment" in result
    assert "by_maintenance" in result
    assert "by_damage" in result
    assert "by_age" in result
    assert "trends" in result

@pytest.mark.asyncio
async def test_bulk_update_equipment_checks(equipment_manager, mock_db):
    """Test bulk updating equipment checks."""
    updates = [
        {"check_id": "check1", "maintenance_status": "good"},
        {"check_id": "check2", "damage_status": "none"}
    ]
    
    # Mock the database operations
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(spec=EquipmentCheck),
        MagicMock(spec=EquipmentCheck)
    ]
    
    result = await equipment_manager.bulk_update_equipment_checks(updates, mock_db)
    assert "successful" in result
    assert "failed" in result
    assert result["successful"] == 2
    assert result["failed"] == 0

@pytest.mark.asyncio
async def test_bulk_delete_equipment_checks(equipment_manager, mock_db):
    """Test bulk deleting equipment checks."""
    check_ids = ["check1", "check2"]
    
    # Mock the database operations
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(spec=EquipmentCheck),
        MagicMock(spec=EquipmentCheck)
    ]
    
    result = await equipment_manager.bulk_delete_equipment_checks(check_ids, mock_db)
    assert "successful" in result
    assert "failed" in result
    assert result["successful"] == 2
    assert result["failed"] == 0

@pytest.mark.asyncio
async def test_error_handling(equipment_manager, mock_db):
    """Test error handling in equipment manager operations."""
    # Test database error in create
    mock_db.commit.side_effect = Exception("Database error")
    result = await equipment_manager.create_equipment_check(
        class_id="class1",
        equipment_id="eq1",
        maintenance_status="good",
        damage_status="none",
        age_status="new",
        db=mock_db
    )
    assert result["success"] is False
    assert "Error creating equipment check" in result["message"]
    
    # Test database error in update
    mock_db.commit.side_effect = Exception("Database error")
    result = await equipment_manager.update_equipment_check(
        "check1",
        {"maintenance_status": "good"},
        mock_db
    )
    assert result["success"] is False
    assert "Error updating equipment check" in result["message"]
    
    # Test database error in delete
    mock_db.commit.side_effect = Exception("Database error")
    result = await equipment_manager.delete_equipment_check("check1", mock_db)
    assert result["success"] is False
    assert "Error deleting equipment check" in result["message"] 