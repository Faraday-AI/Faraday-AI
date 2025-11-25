# Meal Plan Workflow Patches - Applied

## ✅ All 5 Critical Patches Applied

### Patch 1: NoneType.strip() Crash Fix ✅

**Location:** `app/services/pe/ai_assistant_service.py` (lines ~2318-2340)

**What it does:**
- Prevents crashes when message content is `None`
- Safely converts all message content to strings before calling `.strip()`
- Applied to all OpenAI API calls (main request, correction, worksheets, rubrics)

**Code:**
```python
safe_messages = []
for m in messages:
    role = m.get("role", "user")
    content = m.get("content")
    if content is None:
        logger.error("⚠️ WARNING: Found None content in message — replacing with empty string.")
        content = ""
    safe_messages.append({
        "role": role,
        "content": str(content).strip()
    })
```

### Patch 2: System Message Ordering Fix ✅

**Location:** `app/services/pe/ai_assistant_service.py` (lines ~2340-2375)

**What it does:**
- Moves TOP PRIORITY rules to be the **LAST** system message
- Ensures top priority instructions override all module prompts
- Prevents Jasper from ignoring critical meal plan rules

**Code:**
```python
# Extract top priority message if it exists
# Find it, remove it, then insert it as the LAST system message
# This ensures it overrides all other system prompts
```

### Patch 3: Module Prompt Safety Wrapper ✅

**Location:** `app/core/prompt_loader.py` (lines ~100-110)

**What it does:**
- Wraps all module prompts with a header stating they are "SECONDARY AUTHORITY"
- Prevents module prompts from overriding top-priority system rules
- Ensures meal_plan module doesn't contradict critical instructions

**Code:**
```python
wrapped_module_content = (
    "### MODULE INSTRUCTIONS (SECONDARY AUTHORITY)\n"
    "These rules support the top-priority system rules and must NOT override them.\n"
    "If a top-priority system message exists, it takes precedence over these module instructions.\n\n"
    + module_content
)
```

### Patch 4: Allergy + Pending Request Detection Fix ✅

**Location:** `app/services/pe/ai_assistant_service.py` (lines ~1886-1912)

**What it does:**
- Robustly searches for pending meal plan request in metadata
- Falls back to scanning message history for meal plan keywords
- Forces `meal_plan` intent when allergy answer + pending request detected

**Code:**
```python
# Search metadata first
# Fallback to keyword search in message history
# Force intent to meal_plan if pending request found
```

### Patch 5: Widget Extraction Safety ✅

**Location:** `app/services/pe/ai_assistant_service.py` (lines ~2614-2620, ~2828-2847)

**What it does:**
- Ensures meal plan requests extract meal plan widgets ONLY
- Prevents lesson plan widgets from being extracted for meal plans
- Clear logging to show which widget type is being extracted

**Code:**
```python
if is_meal_plan_request:
    logger.error("🥗 Extracting MEAL PLAN widget")
    # Extract meal plan data
else:
    logger.error("🏫 Extracting LESSON PLAN widget")
    # Extract lesson plan data
```

## Testing

All patches have been applied and linted. The system should now:

1. ✅ Never crash on NoneType.strip()
2. ✅ Always respect top-priority meal plan rules
3. ✅ Never let module prompts override critical instructions
4. ✅ Always detect allergy answers + pending requests correctly
5. ✅ Always extract the correct widget type

## Next Steps

1. Rebuild Docker: `docker compose build --no-cache`
2. Test the meal plan workflow:
   - Request meal plan
   - Answer allergy question
   - Verify meal plan is generated immediately (no acknowledgment)
   - Verify correct widget is extracted

## Expected Behavior

**Before patches:**
- ❌ Crashed with `NoneType.strip()` error
- ❌ Jasper repeated allergy question
- ❌ Wrong widget extracted (lesson plan instead of meal plan)

**After patches:**
- ✅ No crashes
- ✅ Meal plan generated immediately after allergy answer
- ✅ Correct meal plan widget extracted
- ✅ All 7 days with calories, macros, micronutrients

