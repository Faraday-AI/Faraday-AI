# Testing Hybrid Architecture

## Overview

The Hybrid Architecture test suite validates all components of the new routing system, specialized services, and model tiering.

## Test File

**Location**: `tests/test_hybrid_architecture.py`

## Running Tests

### In Docker (Recommended)

```bash
# Run all hybrid architecture tests
docker compose exec app pytest tests/test_hybrid_architecture.py -v

# Run specific test
docker compose exec app pytest tests/test_hybrid_architecture.py::test_intent_classification -v

# Run with coverage
docker compose exec app pytest tests/test_hybrid_architecture.py --cov=app.services.pe --cov-report=term-missing
```

### Local (if dependencies installed)

```bash
# Run all tests
pytest tests/test_hybrid_architecture.py -v

# Run specific test
pytest tests/test_hybrid_architecture.py::test_intent_classification -v
```

## Test Coverage

### 1. Intent Classification (`test_intent_classification`)
- Tests keyword-based intent classification
- Validates correct intent mapping for various user messages
- No API calls required (instant)

**Test Cases:**
- Attendance queries → `"attendance"`
- Lesson plan requests → `"lesson_plan"`
- Meal plan requests → `"meal_plan"`
- Workout requests → `"workout"`
- Widget queries → `"widget"`
- General queries → `"general"`

### 2. Service Registry (`test_service_registry`)
- Tests ServiceRegistry routing logic
- Validates intent → service mapping
- Tests fallback for unknown intents

**Requirements:**
- `db_session` fixture (from `tests/conftest.py`)
- `openai_client` fixture

### 3. ModelRouter (`test_model_router`)
- Tests ModelRouter routing
- Validates specialized service selection
- Tests fallback router for general queries

**Requirements:**
- `db_session` fixture
- `openai_client` fixture

### 4. Prompt Loading (`test_prompt_loading`)
- Tests prompt file loading for all specialized services
- Validates prompts are not empty
- No database or API required

**Services Tested:**
- AttendanceService
- LessonPlanService
- MealPlanService
- WorkoutService

### 5. Model Selection (`test_model_selection`)
- Tests model tiering configuration
- Validates correct models per service
- Tests ModelRouter fallback model

**Expected Models:**
- `gpt-4o-mini`: Attendance, GeneralWidget, GeneralResponse, Router fallback
- `gpt-4o`: LessonPlan, MealPlan, Workout

**Requirements:**
- `db_session` fixture
- `openai_client` fixture

### 6. End-to-End Flow (`test_end_to_end_flow`)
- Tests complete request flow through ModelRouter
- Validates response generation
- **Skipped by default** (requires valid OpenAI API key)

**To Run:**
```bash
# Set valid API key
export OPENAI_API_KEY=your-key-here

# Run test
docker compose exec app pytest tests/test_hybrid_architecture.py::test_end_to_end_flow -v
```

## Pytest Fixtures

### `db_session`
- Provided by `tests/conftest.py`
- Creates isolated database session
- Automatically rolls back after each test
- Works in both local and Docker environments

### `openai_client`
- Defined in `tests/test_hybrid_architecture.py`
- Creates OpenAI client from environment variable
- Uses `OPENAI_API_KEY` or `'test-key'` as fallback

## Environment Variables

Tests use environment variables from Docker Compose:

- `DATABASE_URL`: Database connection (set by `run.sh`)
- `OPENAI_API_KEY`: OpenAI API key (optional for most tests)
- `TEST_MODE`: Set to `"true"` by `tests/conftest.py`

## Expected Results

All tests should pass:

```
tests/test_hybrid_architecture.py::test_intent_classification PASSED
tests/test_hybrid_architecture.py::test_service_registry PASSED
tests/test_hybrid_architecture.py::test_model_router PASSED
tests/test_hybrid_architecture.py::test_prompt_loading PASSED
tests/test_hybrid_architecture.py::test_model_selection PASSED
tests/test_hybrid_architecture.py::test_end_to_end_flow SKIPPED
```

## Troubleshooting

### Tests fail in Docker
- Ensure containers are running: `docker compose ps`
- Check database connection: `docker compose exec app python -c "from app.core.database import SessionLocal; SessionLocal()"`
- Verify environment variables: `docker compose exec app env | grep DATABASE_URL`

### Import errors
- Ensure you're running from project root
- Check Python path: `docker compose exec app python -c "import sys; print(sys.path)"`

### Database connection issues
- Verify `DATABASE_URL` is set in `.env` file
- Check database is accessible: `docker compose exec app psql $DATABASE_URL -c "SELECT 1"`

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Hybrid Architecture Tests
  run: |
    docker compose exec app pytest tests/test_hybrid_architecture.py -v
```

