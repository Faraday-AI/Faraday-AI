# Widget Integration Test Suite

Comprehensive test suite for Jasper widget integrations.

## Running Tests in Docker

```bash
# Run all widget integration tests
docker compose exec app python tests/test_widget_integrations.py

# Run with verbose output
docker compose exec app python -u tests/test_widget_integrations.py

# Run and save output to file
docker compose exec app python tests/test_widget_integrations.py > test_results.log 2>&1
```

## Test Coverage

### Intent Classification Tests
- ✅ Meal Plan intent detection
- ✅ Attendance intent detection
- ✅ Lesson Plan intent detection
- ✅ Workout intent detection
- ✅ Allergy Answer intent detection

### Admin Teacher Query Tests
- ✅ Finding teacher by number (e.g., "teacher 1")
- ✅ Case-insensitive email matching between TeacherRegistration and User

### GPT Function Widget Tests
- ✅ Attendance widget with admin query for teacher 1
- ✅ Meal plan widget with allergy workflow

### Widget Extraction Tests
- ✅ Meal plan data extraction
- ✅ Lesson plan data extraction

## Test Results

Tests will output:
- ✅ Passed tests
- ❌ Failed tests (with error messages)
- ⏭️  Skipped tests (with reasons)

## Adding New Tests

To add a new test:

1. Create a test method in `WidgetIntegrationTestSuite`:
```python
def test_my_new_widget(self):
    """Test description."""
    # Your test logic here
    return {"result": "success"}
```

2. Add it to `run_all_tests()`:
```python
self.test("My New Widget Test", self.test_my_new_widget)
```

## Requirements

- Docker container must be running
- Database must be seeded
- Admin user must exist (jmartucci@faraday-ai.com)

