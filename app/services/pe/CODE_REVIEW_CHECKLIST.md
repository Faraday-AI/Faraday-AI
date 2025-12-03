# Code Review Checklist for Extraction Handlers

## 🔒 CRITICAL: Handler Isolation Requirements

Before approving any changes to extraction handlers, verify:

### ✅ Isolation Checks

- [ ] **No shared module-level variables**: Handler doesn't modify or read module-level variables
- [ ] **No global state**: Handler doesn't use or modify global state
- [ ] **Local variables only**: All variables are function-local
- [ ] **Independent data structures**: Handler uses its own data structures (e.g., `lesson_data`, `workout_data`)
- [ ] **No side effects**: Handler doesn't modify input parameters or external state
- [ ] **Separate function**: Handler is in its own function (not shared with other handlers)

### ✅ Function Signature Verification

- [ ] Handler function name is specific (e.g., `_extract_lesson_plan_data`, not `_extract_data`)
- [ ] Handler has its own unique function name
- [ ] Handler doesn't call other extraction handlers directly
- [ ] Handler only uses the router function (`extract_widget`) for routing, not for extraction logic

### ✅ Return Value Verification

- [ ] Handler returns its own dictionary structure
- [ ] Return structure doesn't include fields from other widget types
- [ ] Return structure is consistent with widget type (lesson plan → lesson plan fields, workout → workout fields)

## 🧪 Testing Requirements

### Before Merging

- [ ] **Unit tests pass**: All tests in `tests/physical_education/test_widget_extraction_handlers.py` pass
- [ ] **Isolation tests pass**: `TestHandlerIsolation` tests verify no cross-contamination
- [ ] **Edge case tests pass**: Handler handles empty responses, malformed JSON, missing fields
- [ ] **Regression tests pass**: Existing functionality still works

### Test Coverage

- [ ] Handler has at least 3 test cases
- [ ] Tests verify handler doesn't return other widget types' fields
- [ ] Tests verify handler works independently when called sequentially
- [ ] Tests verify edge cases (empty strings, missing fields, malformed JSON)

## 📋 Code Quality Checks

### Code Structure

- [ ] Handler function is self-contained (all logic within the function)
- [ ] No shared helper functions that modify state
- [ ] Helper functions (if any) are pure functions (no side effects)
- [ ] Clear separation between JSON parsing and regex extraction

### Documentation

- [ ] Handler function has docstring explaining what it extracts
- [ ] Complex extraction logic has inline comments
- [ ] Edge cases are documented
- [ ] Any assumptions are documented

### Error Handling

- [ ] Handler handles empty input gracefully
- [ ] Handler handles malformed JSON gracefully
- [ ] Handler handles missing fields gracefully
- [ ] Handler doesn't raise unhandled exceptions

## 🔍 Specific Checks by Handler Type

### Lesson Plan Handler

- [ ] Worksheets extraction works from JSON, costas_questioning, and raw text
- [ ] Rubrics extraction works from JSON, assessments, and raw text
- [ ] Empty string handling works correctly (`"worksheets": ""` → use regex extraction)
- [ ] Line-by-line regex extraction captures worksheets/rubrics from costas_questioning section

### Workout Handler

- [ ] JSON extraction handles both `plan_name`/`planname` and `strength_training`/`strengthtraining`
- [ ] Week-long workout format (days array) is handled
- [ ] JSON repair logic works for incomplete JSON
- [ ] Free weight exercises specify "Dumbbell" or "Barbell"

### Meal Plan Handler

- [ ] Days array extraction works
- [ ] Meal data structure is consistent
- [ ] Macros and micronutrients are extracted if present

## 🚫 Red Flags (DO NOT APPROVE)

### Critical Issues

- ❌ Handler modifies module-level variables
- ❌ Handler calls another extraction handler directly
- ❌ Handler shares data structures with another handler
- ❌ Handler has side effects (modifies input, external state)
- ❌ Handler returns fields from other widget types
- ❌ Changes to one handler break tests for another handler
- ❌ Handler uses global state or shared state

### Code Smells

- ❌ Complex nested conditionals that could affect other handlers
- ❌ Shared helper functions that modify state
- ❌ Magic numbers or hardcoded values that might conflict
- ❌ Unclear variable names that could be confused with other handlers

## 📝 Review Process

1. **Run Validation Script**: Run `validate_handler_isolation.py` to check for isolation issues
   ```bash
   docker compose exec app python app/services/pe/validate_handler_isolation.py
   ```
2. **Run Tests First**: Always run `test_widget_extraction_handlers.py` before reviewing
   ```bash
   docker compose exec app pytest tests/physical_education/test_widget_extraction_handlers.py -v
   ```
3. **Check Isolation**: Verify no shared state or dependencies
4. **Test Independently**: Test the handler in isolation
5. **Test Sequentially**: Test that calling handlers sequentially doesn't cause issues
6. **Check Return Values**: Verify return structure matches widget type
7. **Review Edge Cases**: Ensure edge cases are handled
8. **Document Changes**: Ensure changes are documented

## 🎯 Success Criteria

A change is approved when:
- ✅ All isolation tests pass
- ✅ Handler-specific tests pass
- ✅ No shared state or dependencies
- ✅ Return structure is correct for widget type
- ✅ Edge cases are handled
- ✅ Documentation is updated
- ✅ No regression in other handlers

## 📚 Related Documentation

- `EXTRACTION_ARCHITECTURE.md` - Architecture overview
- `tests/physical_education/test_widget_extraction_handlers.py` - Test suite
- `IMPLEMENTATION_GUIDELINES.md` - Implementation best practices

