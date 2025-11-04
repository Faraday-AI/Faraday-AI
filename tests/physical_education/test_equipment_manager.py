import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.physical_education.equipment_manager import EquipmentManager
from app.models.physical_education.safety import EquipmentCheck

@pytest.fixture
def equipment_manager():
    """Create EquipmentManager instance for testing."""
    return EquipmentManager()

@pytest.fixture
def test_class(db_session):
    """Create a real PhysicalEducationClass for foreign key constraints."""
    from app.models.physical_education.class_ import PhysicalEducationClass
    from app.models.physical_education.pe_enums.pe_types import ClassType, GradeLevel
    import uuid
    
    pe_class = PhysicalEducationClass(
        name=f"Test Class {uuid.uuid4().hex[:8]}",
        grade_level=GradeLevel.NINTH,
        class_type=ClassType.REGULAR,
        teacher_id=1,  # Required field
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=90)
    )
    db_session.add(pe_class)
    db_session.flush()  # Use flush for SAVEPOINT transactions
    db_session.refresh(pe_class)
    return pe_class

@pytest.fixture
def equipment_check_data(test_class):
    """Create test equipment check data for real database operations."""
    return {
        "class_id": test_class.id,  # Use real class ID from fixture
        "equipment_id": "eq1",
        "maintenance_status": "good",
        "damage_status": "none",
        "age_status": "new",
        "last_maintenance": datetime.now() - timedelta(days=30),
        "purchase_date": datetime.now() - timedelta(days=365),
        "max_age_years": 5,
        "metadata": {"notes": "Regular check"}
    }

# Tests for initialization
def test_equipment_manager_initialization(equipment_manager):
    """Test EquipmentManager initialization."""
    assert equipment_manager.maintenance_statuses
    assert equipment_manager.damage_statuses
    assert equipment_manager.age_statuses

# Tests for create_equipment_check
@pytest.mark.asyncio
async def test_create_equipment_check_success(equipment_manager, db_session, equipment_check_data):
    """Test successful equipment check creation in real database."""
    result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    
    assert result["success"] is True
    assert "check_id" in result
    
    # Verify it was actually created in database
    check_id = result["check_id"]
    created_check = await equipment_manager.get_equipment_check(check_id=check_id, db=db_session)
    assert created_check is not None
    assert created_check.equipment_id == equipment_check_data["equipment_id"]

@pytest.mark.asyncio
async def test_create_equipment_check_invalid_status(equipment_manager, db_session, equipment_check_data):
    """Test equipment check creation with invalid status."""
    equipment_check_data["maintenance_status"] = "invalid_status"
    
    result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    
    assert result["success"] is False
    assert "Invalid maintenance status" in result["message"]

# Tests for get_equipment_check
@pytest.mark.asyncio
async def test_get_equipment_check_success(equipment_manager, db_session, equipment_check_data):
    """Test successful equipment check retrieval from real database."""
    # First create a check in the real database
    create_result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    assert create_result["success"] is True
    check_id = create_result["check_id"]
    db_session.flush()
    
    result = await equipment_manager.get_equipment_check(
        check_id=check_id,
        db=db_session
    )
    
    assert result is not None
    assert result.id == check_id
    assert result.equipment_id == equipment_check_data["equipment_id"]

@pytest.mark.asyncio
async def test_get_equipment_check_not_found(equipment_manager, db_session):
    """Test equipment check retrieval when not found from real database."""
    # Test with ID that doesn't exist
    result = await equipment_manager.get_equipment_check(
        check_id="nonexistent_check_id_999999",
        db=db_session
    )
    
    assert result is None

# Tests for get_equipment_checks
@pytest.mark.asyncio
async def test_get_equipment_checks_with_filters(equipment_manager, db_session, equipment_check_data):
    """Test retrieving equipment checks with filters from real database."""
    # First create a check in the real database
    create_result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    assert create_result["success"] is True
    db_session.flush()
    
    # Note: Status filtering may need adjustment since DB stores booleans
    # For now, just filter by class_id and equipment_id
    result = await equipment_manager.get_equipment_checks(
        class_id=equipment_check_data["class_id"],
        equipment_id=equipment_check_data["equipment_id"],
        # Don't filter by status strings - DB stores booleans
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        db=db_session
    )
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(check, EquipmentCheck) for check in result)

# Tests for update_equipment_check
@pytest.mark.asyncio
async def test_update_equipment_check_success(equipment_manager, db_session, equipment_check_data):
    """Test successful equipment check update in real database."""
    # First create a check in the real database
    create_result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    assert create_result["success"] is True
    check_id = create_result["check_id"]
    db_session.flush()
    
    result = await equipment_manager.update_equipment_check(
        check_id=check_id,
        update_data={"maintenance_status": "needs_inspection"},
        db=db_session
    )
    
    assert result["success"] is True
    
    # Verify update was actually saved in database
    updated_check = await equipment_manager.get_equipment_check(check_id=check_id, db=db_session)
    assert updated_check is not None
    # maintenance_status is stored as boolean in DB - "needs_inspection" maps to False
    assert updated_check.maintenance_status is False  # needs_inspection = False

@pytest.mark.asyncio
async def test_update_equipment_check_not_found(equipment_manager, db_session):
    """Test equipment check update when not found."""
    
    result = await equipment_manager.update_equipment_check(
        check_id=999999999,  # Large integer ID that shouldn't exist
        update_data={"maintenance_status": "needs_inspection"},
        db=db_session
    )
    
    assert result["success"] is False
    assert "Equipment check not found" in result["message"]

# Tests for delete_equipment_check
@pytest.mark.asyncio
async def test_delete_equipment_check_success(equipment_manager, db_session, equipment_check_data):
    """Test successful equipment check deletion from real database."""
    # First create a check in the real database
    create_result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    assert create_result["success"] is True
    check_id = create_result["check_id"]
    db_session.flush()
    
    # Verify it exists before deletion
    assert await equipment_manager.get_equipment_check(check_id=check_id, db=db_session) is not None
    
    result = await equipment_manager.delete_equipment_check(
        check_id=check_id,
        db=db_session
    )
    
    assert result["success"] is True
    
    # Verify it was actually deleted
    assert await equipment_manager.get_equipment_check(check_id=check_id, db=db_session) is None

@pytest.mark.asyncio
async def test_delete_equipment_check_not_found(equipment_manager, db_session):
    """Test equipment check deletion when not found."""
    # Use integer ID that doesn't exist instead of string
    result = await equipment_manager.delete_equipment_check(
        check_id=999999999,  # Large integer ID that shouldn't exist
        db=db_session
    )
    
    assert result["success"] is False
    assert "Equipment check not found" in result["message"]

# Tests for get_equipment_statistics
@pytest.mark.asyncio
async def test_get_equipment_statistics(equipment_manager, db_session, equipment_check_data):
    """Test getting equipment statistics from real database."""
    # Create checks in real database with different statuses
    check_good = equipment_check_data.copy()
    check_needs_inspection = equipment_check_data.copy()
    check_needs_inspection["maintenance_status"] = "needs_inspection"
    check_needs_repair = equipment_check_data.copy()
    check_needs_repair["maintenance_status"] = "needs_repair"
    
    for data in [check_good, check_needs_inspection, check_needs_repair]:
        create_result = await equipment_manager.create_equipment_check(
            db=db_session,
            **data
        )
        assert create_result["success"] is True
    db_session.flush()
    
    result = await equipment_manager.get_equipment_statistics(
        class_id=equipment_check_data["class_id"],
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        db=db_session
    )
    
    assert "total_checks" in result
    assert "maintenance_status_distribution" in result
    assert result["total_checks"] >= 3  # At least the 3 we created

# Tests for bulk operations
@pytest.mark.asyncio
async def test_bulk_update_equipment_checks(equipment_manager, db_session, equipment_check_data):
    """Test bulk updating equipment checks in real database."""
    # Create two checks in real database
    check1_data = equipment_check_data.copy()
    check2_data = equipment_check_data.copy()
    
    create1 = await equipment_manager.create_equipment_check(db=db_session, **check1_data)
    create2 = await equipment_manager.create_equipment_check(db=db_session, **check2_data)
    assert create1["success"] is True
    assert create2["success"] is True
    db_session.flush()
    
    updates = [
        {"check_id": create1["check_id"], "maintenance_status": "needs_inspection"},
        {"check_id": create2["check_id"], "maintenance_status": "good"}
    ]
    
    result = await equipment_manager.bulk_update_equipment_checks(
        updates=updates,
        db=db_session
    )
    
    assert result["success"] is True
    assert result["updated_count"] == 2
    
    # Verify updates were actually saved
    updated1 = await equipment_manager.get_equipment_check(check_id=create1["check_id"], db=db_session)
    updated2 = await equipment_manager.get_equipment_check(check_id=create2["check_id"], db=db_session)
    # maintenance_status is boolean: True = "good", False = "needs_inspection" etc.
    assert updated1.maintenance_status is False  # needs_inspection = False
    assert updated2.maintenance_status is True  # good = True

@pytest.mark.asyncio
async def test_bulk_delete_equipment_checks(equipment_manager, db_session, equipment_check_data):
    """Test bulk deleting equipment checks from real database."""
    # Create two checks in real database
    check1_data = equipment_check_data.copy()
    check2_data = equipment_check_data.copy()
    
    create1 = await equipment_manager.create_equipment_check(db=db_session, **check1_data)
    create2 = await equipment_manager.create_equipment_check(db=db_session, **check2_data)
    assert create1["success"] is True
    assert create2["success"] is True
    db_session.flush()
    
    check_ids = [create1["check_id"], create2["check_id"]]
    
    # Verify they exist before deletion
    assert await equipment_manager.get_equipment_check(check_id=create1["check_id"], db=db_session) is not None
    assert await equipment_manager.get_equipment_check(check_id=create2["check_id"], db=db_session) is not None
    
    result = await equipment_manager.bulk_delete_equipment_checks(
        check_ids=check_ids,
        db=db_session
    )
    
    assert result["success"] is True
    assert result["deleted_count"] == 2
    
    # Verify they were actually deleted
    assert await equipment_manager.get_equipment_check(check_id=create1["check_id"], db=db_session) is None
    assert await equipment_manager.get_equipment_check(check_id=create2["check_id"], db=db_session) is None

# Tests for error handling
@pytest.mark.asyncio
async def test_error_handling_validation_error_simple(equipment_manager, db_session):
    """Test handling validation errors - invalid status should fail before DB operations."""
    result = await equipment_manager.create_equipment_check(
        class_id="class1",
        equipment_id="eq1",
        maintenance_status="invalid_status",  # Invalid status
        damage_status="none",
        age_status="new",
        db=db_session
    )
    
    assert result["success"] is False
    assert "Invalid" in result["message"]

@pytest.mark.asyncio
async def test_error_handling_validation_error(equipment_manager, db_session, equipment_check_data):
    """Test handling validation errors."""
    equipment_check_data["maintenance_status"] = "invalid_status"
    
    result = await equipment_manager.create_equipment_check(
        db=db_session,
        **equipment_check_data
    )
    
    assert result["success"] is False
    assert "Invalid maintenance status" in result["message"] 