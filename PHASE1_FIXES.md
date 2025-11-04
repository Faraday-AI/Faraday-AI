# Phase 1 Fixes - test_activity_recommendations.py

## Issues Fixed

### 1. API Endpoint Signature Mismatch
**File:** `app/api/v1/endpoints/physical_education/activity_recommendations.py`
**Change:** Updated `get_activity_recommendations` endpoint to pass the full `request` object to `service.get_recommendations()` instead of individual parameters.

**Before:**
```python
return await service.get_recommendations(
    request.student_id,
    request.class_id,
    request.preferences,
    ...
)
```

**After:**
```python
return await service.get_recommendations(
    request,  # Pass the full request object
    ...
)
```

### 2. PhysicalEducationClass Fixture
**File:** `tests/integration/test_activity_recommendations.py`
**Change:** Fixed `test_class` fixture to:
- Use proper enum values (`GradeLevel.NINTH`, `ClassType.PHYSICAL_EDUCATION`)
- Remove invalid `duration_minutes` field (belongs to `ClassRoutine`, not `PhysicalEducationClass`)
- Add required fields: `teacher_id`, `start_date`, `end_date`

### 3. AlertType Fix (Partial Phase 3)
**File:** `tests/physical_education/test_safety_manager.py`
**Change:** Updated `alert_data` fixture to use `AlertType.HIGH_RISK` instead of `AlertType.RISK_THRESHOLD` (which doesn't exist in the PE enum).

## Remaining Issues (Need Testing)

### Student 'name' Field Error
**Issue:** Tests are failing with `TypeError: 'name' is an invalid keyword argument for Student`

**Root Cause:** SQLAlchemy is receiving kwargs with `'name'` when constructing Student objects. This could be from:
1. Database query results that include 'name' from joins
2. Serialization/deserialization that converts first_name/last_name to 'name'
3. Relationship loading that includes 'name' field

**Investigation Needed:**
- Check if Student model has any hybrid properties that return 'name'
- Check if there are any database views or joins that include 'name'
- Verify that API responses don't include 'name' when serializing Student objects

**Test Command:**
```bash
docker-compose exec app python -m pytest tests/integration/test_activity_recommendations.py -xvs
```

## Next Steps
1. Test Phase 1 fixes in Docker environment
2. If Student 'name' errors persist, investigate RecommendationEngine and Student model relationships
3. Check API response serialization for Student objects

