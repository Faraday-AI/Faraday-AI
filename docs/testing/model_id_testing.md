# Model ID Testing Guide

## Overview
This guide provides instructions for testing the recent changes to model primary keys and foreign keys, which have been standardized to use Integer type.

## Test Preparation

### Environment Setup
1. Ensure test database is properly configured
2. Clear any existing test data
3. Run migrations to update schema

### Test Data
1. Update all test fixtures to use integer IDs
2. Verify foreign key relationships in test data
3. Create test cases for edge cases

## Test Cases

### Unit Tests

#### 1. Model Creation
```python
def test_model_creation():
    # Test creating models with integer IDs
    model = Model(id=1)
    assert isinstance(model.id, int)
```

#### 2. Foreign Key Relationships
```python
def test_foreign_key_relationship():
    # Test foreign key relationships with integer IDs
    parent = ParentModel(id=1)
    child = ChildModel(id=1, parent_id=1)
    assert child.parent_id == parent.id
```

#### 3. CRUD Operations
```python
def test_crud_operations():
    # Test create, read, update, delete with integer IDs
    model = Model(id=1)
    db.add(model)
    db.commit()
    
    retrieved = db.query(Model).filter_by(id=1).first()
    assert retrieved.id == 1
```

### Integration Tests

#### 1. API Endpoints
```python
def test_api_endpoints():
    # Test API endpoints with integer IDs
    response = client.get("/api/models/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
```

#### 2. Data Serialization
```python
def test_serialization():
    # Test serialization of integer IDs
    model = Model(id=1)
    serialized = model.to_dict()
    assert isinstance(serialized["id"], int)
```

## Test Coverage

### Required Coverage Areas
1. All model classes
2. All foreign key relationships
3. All API endpoints
4. All database operations

### Test Categories
1. Unit Tests
   - Model creation
   - Foreign key relationships
   - CRUD operations
   - Validation rules

2. Integration Tests
   - API endpoints
   - Database operations
   - Data serialization
   - Error handling

3. Performance Tests
   - Database query performance
   - API response times
   - Memory usage

## Running Tests

### Command Line
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=app tests/
```

### Test Environment
1. Use test database
2. Clear test data before each test
3. Use transaction rollback
4. Mock external services

## Common Issues

### 1. Type Mismatches
- Ensure all ID fields are integers
- Check foreign key relationships
- Verify API response types

### 2. Database Constraints
- Check foreign key constraints
- Verify unique constraints
- Test cascade operations

### 3. API Compatibility
- Test backward compatibility
- Verify error handling
- Check response formats

## Reporting

### Test Results
1. Record test coverage
2. Document any failures
3. Track performance metrics
4. Note any edge cases

### Documentation
1. Update test documentation
2. Record known issues
3. Document workarounds
4. Update API documentation

## Maintenance

### Regular Tasks
1. Update test data
2. Review test coverage
3. Update test cases
4. Monitor performance

### Best Practices
1. Use meaningful test data
2. Follow naming conventions
3. Document test cases
4. Maintain test isolation 