# Widget Extraction Architecture Documentation

## Overview

The widget extraction system uses **completely isolated, specialized handlers** for each widget type. Each handler operates independently with no shared state, ensuring that changes to one handler cannot affect another.

## Handler Separation

### Core Principle
**Each widget type has its own dedicated extraction function with zero shared state or dependencies.**

### Extraction Functions

1. **`_extract_lesson_plan_data(response_text, original_message)`**
   - Location: `app/services/pe/widget_handler.py` (line 356)
   - Purpose: Extracts structured lesson plan data
   - Returns: Dictionary with lesson plan fields (title, objectives, activities, worksheets, rubrics, etc.)
   - **Completely independent** - no dependencies on other handlers

2. **`_extract_workout_data(response_text)`**
   - Location: `app/services/pe/widget_handler.py` (line 1196)
   - Purpose: Extracts structured workout plan data
   - Returns: Dictionary with workout fields (plan_name, strength_training, cardio, days, etc.)
   - **Completely independent** - no dependencies on other handlers

3. **`_extract_meal_plan_data(response_text)`**
   - Location: `app/services/pe/widget_handler.py` (line 127)
   - Purpose: Extracts structured meal plan data
   - Returns: Dictionary with meal plan fields (days, meals, macros, etc.)
   - **Completely independent** - no dependencies on other handlers

### Router Function

The `extract_widget(user_intent, response_text)` function (line 1687) routes to the appropriate handler based on intent:

```python
def extract_widget(user_intent: str, response_text: str) -> Dict[str, Any]:
    if user_intent == "meal_plan":
        return _extract_meal_plan_data(response_text)
    elif user_intent == "lesson_plan":
        return _extract_lesson_plan_data(response_text)
    elif user_intent == "workout":
        return _extract_workout_data(response_text)
    else:
        return {"type": "general_response", "data": response_text}
```

**This router is the ONLY shared code path**, and it simply dispatches to the appropriate handler - it does not modify or interfere with the extraction logic.

## Lesson Plan Extraction Logic

### Two-Phase Extraction

The lesson plan extraction uses a **two-phase approach** to ensure maximum data capture:

#### Phase 1: Line-by-Line Regex Extraction
- Processes the raw response text line by line
- Detects sections (worksheets, rubrics, activities, etc.) using regex patterns
- Populates `lesson_data` dictionary with extracted content
- **Critical**: This phase captures worksheets/rubrics even when embedded in other sections (e.g., `costas_questioning`)

#### Phase 2: JSON Parsing and Merging
- Extracts JSON from markdown code blocks (if present)
- Merges JSON data with regex-extracted data
- **Critical Logic**: 
  - JSON data takes precedence for most fields
  - **BUT**: If JSON has empty strings for worksheets/rubrics, regex-extracted data is used
  - This handles cases where AI generates worksheets/rubrics in text but JSON has `"worksheets": ""`

### Worksheets/Rubrics Extraction

Worksheets and rubrics can appear in multiple locations:

1. **Direct JSON fields**: `"worksheets": "..."` or `"rubrics": "..."` in the JSON
2. **Embedded in costas_questioning**: Often the AI embeds worksheets/rubrics in the `costas_questioning` field
3. **In raw response text**: May appear in markdown sections

#### Extraction Strategy

**During Line-by-Line Processing:**
- When processing `costas_questioning` section, the handler detects:
  - Worksheet markers: `"### Worksheets"`, `"Student Worksheet:"`, `"Worksheet with Answer Keys"`
  - Rubric markers: `"### Grading Rubric"`, `"Rubric"`, `"Assessment Rubric"`
  - Multiple-choice questions: Lines starting with `"A)"`, `"B)"`, etc.
  - Answer keys: Lines containing `"Answer Key:"`
- When detected, content is extracted to `lesson_data["worksheets"]` or `lesson_data["rubrics"]`
- Content is also preserved in `costas_questioning` for backward compatibility

**During JSON Merge:**
```python
# Check if JSON has empty strings (not just missing keys)
json_worksheets = final_data.get("worksheets", "")
json_rubrics = final_data.get("rubrics", "")

# Use regex-extracted data if JSON is empty
if lesson_data.get("worksheets") and (not json_worksheets or not json_worksheets.strip()):
    final_data["worksheets"] = lesson_data["worksheets"]
if lesson_data.get("rubrics") and (not json_rubrics or not json_rubrics.strip()):
    final_data["rubrics"] = lesson_data["rubrics"]
```

**Post-Merge Extraction (Fallback):**
- If worksheets/rubrics still empty after merge, search `costas_questioning` field directly
- If still not found, search raw `response_text`
- Uses flexible regex patterns to find embedded content

## Why Handlers Don't Affect Each Other

### Isolation Guarantees

1. **Separate Functions**: Each handler is a completely separate function
2. **No Shared Variables**: Each function uses local variables only
3. **No Global State**: No module-level variables are modified
4. **Independent Logic**: Each handler has its own regex patterns, data structures, and processing logic
5. **Separate Return Values**: Each handler returns its own dictionary structure

### Example: Workout vs Lesson Plan

```python
# Workout handler - completely independent
def _extract_workout_data(response_text: str) -> Dict[str, Any]:
    workout_data = {}  # Local variable
    # ... workout-specific extraction logic ...
    return workout_data

# Lesson plan handler - completely independent  
def _extract_lesson_plan_data(response_text: str, original_message: str = "") -> Dict[str, Any]:
    lesson_data = {}  # Local variable (different name, different structure)
    # ... lesson plan-specific extraction logic ...
    return lesson_data
```

**These functions cannot affect each other because:**
- Different function names
- Different local variables
- Different data structures
- No shared state
- No side effects

## Common Pitfalls to Avoid

### ❌ DON'T: Share State Between Handlers
```python
# BAD - Don't do this
shared_data = {}  # Module-level variable

def _extract_lesson_plan_data(...):
    shared_data["something"] = value  # Affects other handlers!

def _extract_workout_data(...):
    if shared_data.get("something"):  # Depends on lesson plan handler!
        ...
```

### ❌ DON'T: Modify Global Patterns
```python
# BAD - Don't do this
GLOBAL_PATTERN = re.compile(r'...')

def _extract_workout_data(...):
    GLOBAL_PATTERN.pattern = new_pattern  # Affects other handlers!
```

### ✅ DO: Keep Handlers Isolated
```python
# GOOD - Each handler is self-contained
def _extract_lesson_plan_data(...):
    local_pattern = re.compile(r'...')  # Local to this function
    local_data = {}  # Local to this function
    # ... extraction logic ...
    return local_data
```

## Debugging Extraction Issues

### When Worksheets/Rubrics Are Missing

1. **Check Line-by-Line Extraction**:
   - Look for logs: `🔍 Regex extracted - worksheets: X chars`
   - Verify that worksheets/rubrics are being detected during line processing

2. **Check JSON Merge**:
   - Look for logs: `🔍 JSON worksheets/rubrics check - worksheets: X chars`
   - Verify that empty string check is working: `not json_worksheets.strip()`

3. **Check Post-Merge Extraction**:
   - Look for logs: `🔍 Checking costas_questioning for worksheets`
   - Verify that embedded content is being found

4. **Check Frontend Display**:
   - Verify that frontend `formatWidgetData` function checks for non-empty strings:
   ```javascript
   if (data.worksheets && (typeof data.worksheets !== 'string' || data.worksheets.trim().length > 0)) {
       // Display worksheets
   }
   ```

### Logging

The extraction logic includes comprehensive logging:
- `🔍` - Debug/check messages
- `✅` - Success messages
- `⚠️` - Warning messages
- `❌` - Error messages

Check Docker logs for these messages to trace extraction flow.

## Best Practices

1. **Always Keep Handlers Separate**: Never share state or modify global variables
2. **Test Each Handler Independently**: Changes to one handler should not require testing others
3. **Use Local Variables**: All extraction logic should use function-local variables
4. **Document Extraction Patterns**: When adding new extraction patterns, document what they match
5. **Add Logging**: Include debug logs to trace extraction flow
6. **Handle Edge Cases**: Empty strings, missing fields, embedded content, etc.

## File Structure

```
app/services/pe/
├── widget_handler.py          # All extraction functions
│   ├── _extract_meal_plan_data()
│   ├── _extract_lesson_plan_data()
│   ├── _extract_workout_data()
│   └── extract_widget()       # Router function
├── specialized_services/
│   ├── lesson_plan_service.py    # Uses _extract_lesson_plan_data()
│   ├── workout_service.py         # Uses _extract_workout_data()
│   └── meal_plan_service.py       # Uses _extract_meal_plan_data()
└── EXTRACTION_ARCHITECTURE.md     # This file
```

## Summary

- **Handlers are completely isolated** - no shared state
- **Each handler is independent** - changes to one don't affect others
- **Two-phase extraction** ensures maximum data capture
- **Worksheets/rubrics** are extracted from multiple sources (JSON, costas_questioning, raw text)
- **Empty string handling** is critical - JSON may have `"worksheets": ""` which needs special handling
- **Logging** helps debug extraction issues

If worksheets/rubrics stop working, the issue is in `_extract_lesson_plan_data()` only - not in workout or meal plan handlers.

## Implementation Guidelines

To prevent issues in the future, follow these guidelines:

### 1. Keep Extraction Functions Isolated

**✅ DO:**
- Use only local variables within each handler function
- Keep each handler in its own separate function
- Return only widget-specific fields

**❌ DON'T:**
- Create module-level variables
- Share state between handlers
- Call one handler from another
- Return fields from other widget types

### 2. Add Tests for Each Handler

**Test Structure:**
- `TestHandlerIsolation` - Verifies handlers don't share state
- `TestLessonPlanExtraction` - Tests lesson plan-specific extraction
- `TestWorkoutExtraction` - Tests workout-specific extraction
- `TestHandlerIndependence` - Tests sequential handler calls
- `TestEdgeCases` - Tests error handling

**Running Tests:**
```bash
# Run all extraction handler tests
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v

# Run isolation tests only
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestHandlerIsolation -v

# Run specific handler tests
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestLessonPlanExtraction -v
```

**Before Merging:**
- ✅ All tests must pass
- ✅ Isolation tests verify no cross-contamination
- ✅ Handler-specific tests verify correct extraction
- ✅ Edge case tests verify error handling

### 3. Avoid Modifying Shared Code Paths

**Router Function (`extract_widget`):**
- Only modify to add new handlers
- Never add extraction logic to router
- Router should only dispatch to handlers

**Shared Patterns:**
- If creating helper functions, make them pure functions (no side effects)
- Don't create shared extraction logic that modifies state
- Each handler should have its own extraction patterns

**Code Review:**
- Use `CODE_REVIEW_CHECKLIST.md` before approving changes
- Verify no shared state is introduced
- Verify handlers remain independent
- Verify tests pass

## Related Documentation

- **`CODE_REVIEW_CHECKLIST.md`** - Checklist for reviewing extraction handler changes
- **`IMPLEMENTATION_GUIDELINES.md`** - Step-by-step guidelines for implementing handlers
- **`tests/physical_education/test_widget_extraction_handlers.py`** - Test suite for handlers

