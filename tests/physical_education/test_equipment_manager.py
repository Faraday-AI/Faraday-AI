import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session
from app.services.physical_education.equipment_manager import EquipmentManager
from app.models.physical_education.safety import EquipmentCheck

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

@pytest.fixture
def mock_equipment_check():
    """Create a mock EquipmentCheck object."""
    check = MagicMock(spec=EquipmentCheck)
    check.id = "check1"
    check.class_id = "class1"
    check.equipment_id = "eq1"
    check.maintenance_status = "good"
    check.damage_status = "none"
    check.age_status = "new"
    check.last_maintenance = datetime.now() - timedelta(days=30)
    check.purchase_date = datetime.now() - timedelta(days=365)
    check.max_age_years = 5
    check.metadata = {"notes": "Test equipment check"}
    return check

# Tests for initialization
def test_equipment_manager_initialization(equipment_manager):
    """Test EquipmentManager initialization."""
    assert equipment_manager.maintenance_statuses
    assert equipment_manager.damage_statuses
    assert equipment_manager.age_statuses

# Tests for create_equipment_check
@pytest.mark.asyncio
async def test_create_equipment_check_success(equipment_manager, mock_db, sample_equipment_check):
    """Test successful equipment check creation."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    
    result = await equipment_manager.create_equipment_check(
        db=mock_db,
        **sample_equipment_check
    )
    
    assert result["success"] is True
    assert "check_id" in result
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_equipment_check_invalid_status(equipment_manager, mock_db, sample_equipment_check):
    """Test equipment check creation with invalid status."""
    sample_equipment_check["maintenance_status"] = "invalid_status"
    
    result = await equipment_manager.create_equipment_check(
        db=mock_db,
        **sample_equipment_check
    )
    
    assert result["success"] is False
    assert "Invalid maintenance status" in result["message"]

# Tests for get_equipment_check
@pytest.mark.asyncio
async def test_get_equipment_check_success(equipment_manager, mock_db, mock_equipment_check):
    """Test successful equipment check retrieval."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_equipment_check
    
    result = await equipment_manager.get_equipment_check(
        check_id="check1",
        db=mock_db
    )
    
    assert result == mock_equipment_check

@pytest.mark.asyncio
async def test_get_equipment_check_not_found(equipment_manager, mock_db):
    """Test equipment check retrieval when not found."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = await equipment_manager.get_equipment_check(
        check_id="nonexistent",
        db=mock_db
    )
    
    assert result is None

# Tests for get_equipment_checks
@pytest.mark.asyncio
async def test_get_equipment_checks_with_filters(equipment_manager, mock_db, mock_equipment_check):
    """Test retrieving equipment checks with filters."""
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_equipment_check]
    
    result = await equipment_manager.get_equipment_checks(
        class_id="class1",
        equipment_id="eq1",
        maintenance_status="good",
        damage_status="none",
        age_status="new",
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        db=mock_db
    )
    
    assert len(result) == 1
    assert result[0] == mock_equipment_check

# Tests for update_equipment_check
@pytest.mark.asyncio
async def test_update_equipment_check_success(equipment_manager, mock_db, mock_equipment_check):
    """Test successful equipment check update."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_equipment_check
    
    result = await equipment_manager.update_equipment_check(
        check_id="check1",
        update_data={"maintenance_status": "needs_inspection"},
        db=mock_db
    )
    
    assert result["success"] is True
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_update_equipment_check_not_found(equipment_manager, mock_db):
    """Test equipment check update when not found."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = await equipment_manager.update_equipment_check(
        check_id="nonexistent",
        update_data={"maintenance_status": "needs_inspection"},
        db=mock_db
    )
    
    assert result["success"] is False
    assert "Equipment check not found" in result["message"]

# Tests for delete_equipment_check
@pytest.mark.asyncio
async def test_delete_equipment_check_success(equipment_manager, mock_db, mock_equipment_check):
    """Test successful equipment check deletion."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_equipment_check
    
    result = await equipment_manager.delete_equipment_check(
        check_id="check1",
        db=mock_db
    )
    
    assert result["success"] is True
    mock_db.delete.assert_called_once_with(mock_equipment_check)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_equipment_check_not_found(equipment_manager, mock_db):
    """Test equipment check deletion when not found."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = await equipment_manager.delete_equipment_check(
        check_id="nonexistent",
        db=mock_db
    )
    
    assert result["success"] is False
    assert "Equipment check not found" in result["message"]

# Tests for get_equipment_statistics
@pytest.mark.asyncio
async def test_get_equipment_statistics(equipment_manager, mock_db):
    """Test getting equipment statistics."""
    mock_checks = [
        MagicMock(maintenance_status="good"),
        MagicMock(maintenance_status="needs_inspection"),
        MagicMock(maintenance_status="needs_repair")
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_checks
    
    result = await equipment_manager.get_equipment_statistics(
        class_id="class1",
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        db=mock_db
    )
    
    assert "total_checks" in result
    assert "maintenance_status_distribution" in result

# Tests for bulk operations
@pytest.mark.asyncio
async def test_bulk_update_equipment_checks(equipment_manager, mock_db):
    """Test bulk updating equipment checks."""
    updates = [
        {"check_id": "check1", "maintenance_status": "needs_inspection"},
        {"check_id": "check2", "maintenance_status": "good"}
    ]
    
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    result = await equipment_manager.bulk_update_equipment_checks(
        updates=updates,
        db=mock_db
    )
    
    assert result["success"] is True
    assert result["updated_count"] == 2

@pytest.mark.asyncio
async def test_bulk_delete_equipment_checks(equipment_manager, mock_db):
    """Test bulk deleting equipment checks."""
    check_ids = ["check1", "check2"]
    
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    result = await equipment_manager.bulk_delete_equipment_checks(
        check_ids=check_ids,
        db=mock_db
    )
    
    assert result["success"] is True
    assert result["deleted_count"] == 2

# Tests for error handling
@pytest.mark.asyncio
async def test_error_handling_database_error(equipment_manager, mock_db):
    """Test handling database errors."""
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
    assert "Database error" in result["message"]

@pytest.mark.asyncio
async def test_error_handling_validation_error(equipment_manager, mock_db, sample_equipment_check):
    """Test handling validation errors."""
    sample_equipment_check["maintenance_status"] = "invalid_status"
    
    result = await equipment_manager.create_equipment_check(
        db=mock_db,
        **sample_equipment_check
    )
    
    assert result["success"] is False
    assert "Invalid maintenance status" in result["message"] 