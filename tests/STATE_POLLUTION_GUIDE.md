# State Pollution Guide

## What is State Pollution?

**State pollution** occurs when one test modifies shared/global state that persists and affects subsequent tests. This causes:
- ✅ Tests pass when run individually
- ❌ Tests fail when run together in the full suite
- 🔄 Inconsistent test results depending on execution order

## Sources of State Pollution

### 1. Singleton Instances (24+ Services)
**Problem:** Services use `_instance = None` singleton pattern. If Test A creates an instance with database session X, and Test B expects a clean instance, Test B gets the polluted instance from Test A.

**Example:**
```python
class MovementAnalyzer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance  # Returns same instance across tests!
```

**Fix:** Reset `ServiceClass._instance = None` before/after each test.

### 2. FastAPI Dependency Overrides
**Problem:** `app.dependency_overrides` persists between tests. Test A overrides `get_db()`, Test B uses the stale override.

**Fix:** `app.dependency_overrides.clear()` before/after each test.

### 3. Context Variables (Database Sessions)
**Problem:** `contextvars.ContextVar` stores test database session. If not cleared, Test B might use Test A's session.

**Fix:** `clear_test_session()` before/after each test.

### 4. Module-Level Caches/Variables
**Problem:** Module-level dictionaries, lists, or variables accumulate data across tests.

**Example:**
```python
# Module-level cache
_cache = {}  # Bad - persists across tests
```

**Fix:** Clear caches in fixtures or use instance-level caches.

### 5. Redis Connection State
**Problem:** Redis connections, keys, or state persists between tests.

**Fix:** Use test-specific Redis databases or clear keys in fixtures.

### 6. Thread-Local Storage
**Problem:** `threading.local()` or similar persists across test threads.

**Fix:** Clear thread-local storage in fixtures.

## Comprehensive Cleanup Strategy

The `ensure_global_app_state_clean` fixture in `tests/conftest.py` handles ALL sources:

```python
@pytest.fixture(autouse=True, scope="function")
def ensure_global_app_state_clean():
    """
    Resets ALL state pollution sources before and after EVERY test.
    """
    # 1. Clear FastAPI overrides
    app.dependency_overrides.clear()
    
    # 2. Clear context variables
    clear_test_session()
    
    # 3. Reset ALL singleton instances (24+ services)
    for module_path, class_name in singleton_services:
        service_class._instance = None
    
    yield
    
    # Cleanup again after test
    # ... same cleanup ...
```

## Best Practices

### ✅ DO:
1. **Use the global cleanup fixture** - It handles most cases automatically
2. **Reset singletons in test fixtures** if creating instances
3. **Use `db_session` fixture** - It provides isolated database sessions
4. **Clear overrides after setting them** in test fixtures

### ❌ DON'T:
1. **Don't rely on test execution order** - Tests should be independent
2. **Don't assume singletons are clean** - Always reset them
3. **Don't store state in module-level variables** - Use instance variables
4. **Don't forget to clean up** - Use `try-finally` blocks in fixtures

## How to Identify State Pollution

**Symptoms:**
- Test passes individually but fails in suite
- Test results change based on execution order
- Tests fail with "instance already exists" errors
- Tests hang or timeout only in full suite

**Debugging:**
1. Run test individually: `pytest tests/path/to/test.py::test_name -xvs`
2. Run test in suite: `pytest tests/` and find where it fails
3. Compare: What state exists when test runs individually vs in suite?
4. Check: Are singletons being reset? Are overrides cleared?

## Fixed Services

All 24+ singleton services are now automatically reset:
- MovementAnalyzer
- SafetyManager
- StudentManager
- ActivityManager
- LessonPlanner
- AssessmentSystem
- ... and 18+ more

See `tests/conftest.py` for complete list.

