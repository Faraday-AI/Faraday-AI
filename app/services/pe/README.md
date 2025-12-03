# Widget Extraction Handler System

## Overview

This directory contains the widget extraction system for the Physical Education AI assistant. The system uses **completely isolated, specialized handlers** for each widget type to ensure that changes to one handler never affect another.

## Quick Start

### Running Tests

```bash
# Run all extraction handler tests
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v

# Run validation script
docker compose exec app python app/services/pe/validate_handler_isolation.py
```

### Before Making Changes

1. **Read the documentation**: Start with `EXTRACTION_ARCHITECTURE.md`
2. **Review guidelines**: Check `IMPLEMENTATION_GUIDELINES.md`
3. **Run tests**: Ensure all tests pass before making changes

### Making Changes

1. **Make your changes** to the handler function
2. **Run validation**: `docker compose exec app python app/services/pe/validate_handler_isolation.py`
3. **Run tests**: `docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v`
4. **Review checklist**: Use `CODE_REVIEW_CHECKLIST.md` before committing

## Core Principles

1. **Isolation First**: Each handler must be completely independent
2. **Test Before Merge**: All tests must pass before merging
3. **No Shared State**: Never share state between handlers
4. **Clear Separation**: Keep extraction logic separate from routing logic

## Documentation

### Essential Reading

1. **`EXTRACTION_ARCHITECTURE.md`** - Complete architecture overview
   - Handler separation
   - Extraction logic
   - Why handlers don't affect each other
   - Implementation guidelines

2. **`IMPLEMENTATION_GUIDELINES.md`** - Step-by-step implementation guide
   - Adding new handlers
   - Modifying existing handlers
   - Testing workflow
   - Common pitfalls

3. **`CODE_REVIEW_CHECKLIST.md`** - Code review requirements
   - Isolation checks
   - Testing requirements
   - Red flags to avoid
   - Success criteria

### Tools

- **`validate_handler_isolation.py`** - Automated validation script
  - Checks for shared state
  - Verifies handler independence
  - Run before committing

- **`tests/physical_education/test_widget_extraction_handlers.py`** - Test suite
  - Isolation tests
  - Handler-specific tests
  - Edge case tests

## Handler Functions

### Current Handlers

1. **`_extract_meal_plan_data(response_text)`**
   - Extracts meal plan data
   - Returns: `{"days": [...], "meals": [...], ...}`

2. **`_extract_lesson_plan_data(response_text, original_message)`**
   - Extracts lesson plan data
   - Returns: `{"title": "...", "objectives": [...], "worksheets": "...", "rubrics": "...", ...}`
   - **Special**: Two-phase extraction (regex + JSON merge)
   - **Special**: Extracts worksheets/rubrics from multiple sources

3. **`_extract_workout_data(response_text)`**
   - Extracts workout plan data
   - Returns: `{"plan_name": "...", "strength_training": [...], "cardio": [...], ...}`

### Router Function

**`extract_widget(user_intent, response_text)`**
- Routes to appropriate handler based on intent
- **DO NOT** add extraction logic here
- **ONLY** dispatch to handlers

## Common Issues and Solutions

### Issue: Worksheets/Rubrics Missing

**Cause**: Empty strings in JSON not being handled correctly

**Solution**: 
- Check `_extract_lesson_plan_data()` merge logic
- Verify empty string check: `not json_worksheets.strip()`
- Check post-processing extraction from `costas_questioning` and `assessments`

### Issue: Handler Returns Wrong Widget Type Fields

**Cause**: Handler calling another handler or returning mixed fields

**Solution**:
- Ensure handler only returns its own widget type's fields
- Verify handler doesn't call other handlers
- Check return structure matches widget type

### Issue: Changes to One Handler Break Another

**Cause**: Shared state or dependencies

**Solution**:
- Remove any shared state
- Ensure handlers use only local variables
- Verify handlers are independent

## Testing

### Test Structure

- **`TestHandlerIsolation`** - Verifies handlers don't share state
- **`TestLessonPlanExtraction`** - Tests lesson plan-specific extraction
- **`TestWorkoutExtraction`** - Tests workout-specific extraction
- **`TestHandlerIndependence`** - Tests sequential handler calls
- **`TestEdgeCases`** - Tests error handling

### Running Tests

```bash
# All tests
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v

# Specific test class
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestHandlerIsolation -v

# Specific test
docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py::TestHandlerIsolation::test_lesson_plan_handler_independent -v
```

## Validation

### Automated Validation

```bash
# Run validation script
docker compose exec app python app/services/pe/validate_handler_isolation.py
```

The script checks for:
- Module-level variables
- Handlers calling other handlers
- Shared state
- Handler independence

### Pre-Commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
docker compose exec app python app/services/pe/validate_handler_isolation.py
if [ $? -ne 0 ]; then
    echo "Handler isolation validation failed. Commit aborted."
    exit 1
fi
```

## Golden Rules

1. ✅ Each handler is a separate function
2. ✅ Each handler uses only local variables
3. ✅ Each handler returns only its widget type's fields
4. ✅ Handlers never call each other
5. ✅ Handlers never share state
6. ✅ All tests must pass before merging

**If you follow these rules, handlers will remain isolated and changes to one will never affect another.**

## File Structure

```
app/services/pe/
├── widget_handler.py                    # All extraction functions
│   ├── _extract_meal_plan_data()
│   ├── _extract_lesson_plan_data()
│   ├── _extract_workout_data()
│   └── extract_widget()                # Router function
├── specialized_services/
│   ├── lesson_plan_service.py          # Uses _extract_lesson_plan_data()
│   ├── workout_service.py              # Uses _extract_workout_data()
│   └── meal_plan_service.py            # Uses _extract_meal_plan_data()
├── EXTRACTION_ARCHITECTURE.md          # Architecture documentation
├── IMPLEMENTATION_GUIDELINES.md        # Implementation guide
├── CODE_REVIEW_CHECKLIST.md            # Code review checklist
├── validate_handler_isolation.py      # Validation script
└── README.md                           # This file

tests/physical_education/
└── test_widget_extraction_handlers.py   # Test suite
```

## Support

If you encounter issues:

1. **Check the documentation**: Start with `EXTRACTION_ARCHITECTURE.md`
2. **Run tests**: Verify tests pass
3. **Run validation**: Check for isolation issues
4. **Review logs**: Check Docker logs for extraction debug messages
5. **Check edge cases**: Verify empty strings, missing fields, malformed JSON

## Summary

The widget extraction system is designed with **isolation as the core principle**. Each handler operates independently, ensuring that changes to one handler never affect another. By following the guidelines and running tests before merging, we maintain this isolation and prevent regressions.

