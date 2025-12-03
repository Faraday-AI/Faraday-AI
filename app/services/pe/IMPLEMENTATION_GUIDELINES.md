# Implementation Guidelines for Extraction Handlers

## 🎯 Core Principles

1. **Isolation First**: Each handler must be completely independent
2. **Test Before Merge**: All tests must pass before merging
3. **No Shared State**: Never share state between handlers
4. **Clear Separation**: Keep extraction logic separate from routing logic

## 📝 Adding a New Extraction Handler

### Step 1: Create the Handler Function

```python
def _extract_new_widget_data(response_text: str) -> Dict[str, Any]:
    """
    Extract structured data for new widget type.
    
    Args:
        response_text: The AI's response text
        
    Returns:
        Dictionary with extracted widget data
    """
    if not response_text:
        return {}
    
    # Use LOCAL variables only
    widget_data = {}  # Local variable
    
    # Your extraction logic here
    # ...
    
    return widget_data  # Return local data
```

### Step 2: Add to Router

```python
def extract_widget(user_intent: str, response_text: str) -> Dict[str, Any]:
    if user_intent == "new_widget":
        return _extract_new_widget_data(response_text)
    # ... existing handlers ...
```

### Step 3: Create Tests

Create tests in `tests/physical_education/test_widget_extraction_handlers.py`:

```python
class TestNewWidgetExtraction:
    def test_new_widget_extraction(self):
        """Test new widget extraction."""
        response_text = '{"field": "value"}'
        result = widget_handler._extract_new_widget_data(response_text)
        assert result.get("field") == "value"
    
    def test_new_widget_independent(self):
        """Verify new widget handler is independent."""
        # Test that it doesn't return other widget types' fields
        result = widget_handler._extract_new_widget_data("...")
        assert "objectives" not in result  # Lesson plan field
        assert "strength_training" not in result  # Workout field
```

### Step 4: Verify Isolation

Run isolation tests:
```bash
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestHandlerIsolation -v
```

## 🔧 Modifying an Existing Handler

### Before Making Changes

1. **Run existing tests**: Ensure all tests pass before changes
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v
   ```

2. **Understand the handler**: Read the handler function and understand its logic

3. **Check dependencies**: Verify the handler doesn't depend on other handlers

### Making Changes

1. **Keep changes local**: Only modify the specific handler function
2. **Don't touch router**: Don't modify `extract_widget()` unless adding a new handler
3. **Use local variables**: Don't create module-level variables
4. **Test frequently**: Run tests after each significant change

### After Making Changes

1. **Run all tests**: Ensure no regressions
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v
   ```

2. **Run isolation tests**: Verify handlers still don't affect each other
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestHandlerIndependence -v
   ```

3. **Test the specific handler**: Run handler-specific tests
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestLessonPlanExtraction -v
   ```

## 🚫 What NOT to Do

### ❌ DON'T: Share State

```python
# BAD - Don't do this
shared_data = {}  # Module-level variable

def _extract_lesson_plan_data(...):
    shared_data["something"] = value

def _extract_workout_data(...):
    if shared_data.get("something"):  # Depends on lesson plan handler!
        ...
```

### ❌ DON'T: Call Other Handlers

```python
# BAD - Don't do this
def _extract_lesson_plan_data(...):
    workout_data = _extract_workout_data(...)  # Calling another handler!
    # ...
```

### ❌ DON'T: Modify Global Patterns

```python
# BAD - Don't do this
GLOBAL_PATTERN = re.compile(r'...')

def _extract_workout_data(...):
    GLOBAL_PATTERN.pattern = new_pattern  # Affects other handlers!
```

### ❌ DON'T: Return Mixed Widget Types

```python
# BAD - Don't do this
def _extract_lesson_plan_data(...):
    return {
        "title": "Lesson",  # Lesson plan field
        "strength_training": [...]  # Workout field - WRONG!
    }
```

## ✅ What TO Do

### ✅ DO: Use Local Variables

```python
# GOOD - Local variables only
def _extract_lesson_plan_data(...):
    lesson_data = {}  # Local variable
    pattern = re.compile(r'...')  # Local pattern
    # ...
    return lesson_data
```

### ✅ DO: Keep Functions Separate

```python
# GOOD - Separate functions
def _extract_lesson_plan_data(...):
    # Lesson plan logic only
    return lesson_data

def _extract_workout_data(...):
    # Workout logic only
    return workout_data
```

### ✅ DO: Test Isolation

```python
# GOOD - Test that handlers don't affect each other
def test_handlers_independent():
    lesson_result = _extract_lesson_plan_data(...)
    workout_result = _extract_workout_data(...)
    
    # Verify they don't cross-contaminate
    assert "strength_training" not in lesson_result
    assert "objectives" not in workout_result
```

## 🧪 Testing Workflow

### Before Committing

1. **Run all extraction tests**:
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v
   ```

2. **Run specific handler tests** (if modifying a specific handler):
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestLessonPlanExtraction -v
   ```

3. **Run isolation tests**:
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestHandlerIndependence -v
   ```

### Continuous Testing

Add to your development workflow:
```bash
# Watch mode (if available)
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v --watch

# Or run on file save (using a file watcher)
```

## 📋 Pre-Commit Checklist

Before committing changes to extraction handlers:

- [ ] All tests pass
- [ ] No shared state introduced
- [ ] Handler is self-contained
- [ ] Return structure is correct
- [ ] Edge cases handled
- [ ] Documentation updated
- [ ] Code review checklist reviewed

## 🔍 Debugging Extraction Issues

### When Extraction Fails

1. **Check logs**: Look for extraction debug logs
   ```bash
   docker compose logs app | grep "🔍\|✅\|⚠️"
   ```

2. **Test in isolation**: Create a minimal test case
   ```python
   def test_debug():
       response = "..."  # Your failing case
       result = widget_handler._extract_lesson_plan_data(response)
       print(result)  # Inspect the result
   ```

3. **Check JSON parsing**: Verify JSON is being parsed correctly
4. **Check regex patterns**: Verify regex patterns match the content
5. **Check merge logic**: Verify empty string handling works

### Common Issues

**Issue**: Worksheets/rubrics not extracted
- **Check**: Are they in JSON? In costas_questioning? In raw text?
- **Fix**: Ensure extraction logic checks all three sources

**Issue**: Handler returns wrong widget type fields
- **Check**: Is handler calling another handler?
- **Fix**: Ensure handler only returns its own widget type fields

**Issue**: Changes to one handler break another
- **Check**: Is there shared state?
- **Fix**: Remove any shared state, ensure handlers are independent

## 🔧 Validation Tools

### Automated Validation Script

Run the validation script before committing:
```bash
# In Docker
docker compose exec app python app/services/pe/validate_handler_isolation.py

# Locally (if dependencies installed)
python app/services/pe/validate_handler_isolation.py
```

The script checks for:
- Module-level variables that might be shared
- Handlers calling other handlers
- Shared state between handlers
- Handler independence

### Pre-Commit Hook (Optional)

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run handler isolation validation
docker compose exec app python app/services/pe/validate_handler_isolation.py
if [ $? -ne 0 ]; then
    echo "Handler isolation validation failed. Commit aborted."
    exit 1
fi
```

## 📚 Additional Resources

- `EXTRACTION_ARCHITECTURE.md` - Architecture documentation
- `CODE_REVIEW_CHECKLIST.md` - Code review guidelines
- `IMPLEMENTATION_GUIDELINES.md` - This file
- `validate_handler_isolation.py` - Automated validation script
- `tests/physical_education/test_widget_extraction_handlers.py` - Test suite

## 🎯 Summary

**Golden Rules:**
1. Each handler is a separate function
2. Each handler uses only local variables
3. Each handler returns only its widget type's fields
4. Handlers never call each other
5. Handlers never share state
6. All tests must pass before merging

**If you follow these rules, handlers will remain isolated and changes to one will never affect another.**

