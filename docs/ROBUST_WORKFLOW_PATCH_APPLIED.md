# Robust Workflow Patch Applied - Meal Plan + Lesson Plan

## Overview
This document describes the comprehensive patch applied to ensure meal plan, lesson plan, workout, and widget workflows are robust, consistent, and production-ready.

## Patch Components

### 1. Centralized Safe Message Builder
**Location**: `app/services/pe/ai_assistant_service.py` (line ~2384)

**Function**: `safe_build_messages(message_list)`

**Purpose**: Prevents `NoneType.strip()` crashes by safely handling all message content.

**Applied To**:
- ✅ Main conversation messages
- ✅ Correction messages (meal plan validation failures)
- ✅ Worksheet messages (lesson plan generation)
- ✅ Rubric messages (lesson plan generation)

**Implementation**:
```python
def safe_build_messages(message_list):
    """Safe message builder that prevents NoneType.strip() crashes."""
    safe_list = []
    for m in message_list:
        role = m.get("role", "user")
        content = m.get("content")
        if content is None:
            logger.error("⚠️ WARNING: Found None content in message — replacing with empty string.")
            content = ""
        safe_list.append({
            "role": role,
            "content": str(content).strip()
        })
    return safe_list
```

### 2. Enhanced Intent Classification
**Location**: `app/core/prompt_loader.py` (line ~28)

**Function**: `classify_intent(user_message, previous_asked_allergies=False)`

**Features**:
- ✅ Prioritizes allergy answer detection when `previous_asked_allergies=True`
- ✅ Detects meal plan keywords
- ✅ Detects lesson plan keywords
- ✅ Detects workout keywords
- ✅ Detects widget keywords
- ✅ Falls back to "general" intent

**Key Improvements**:
- Allergy answer detection happens FIRST (before other intents)
- Uses shared `detect_allergy_answer()` utility to avoid duplication
- Returns `"allergy_answer"` intent which maps to `meal_plan` module

### 3. Metadata Tracking

#### Meal Plan Metadata
**Location**: `app/services/pe/ai_assistant_service.py` (line ~1970)

**Saved Fields**:
- `pending_meal_plan_request`: Original meal plan request text
- `allergy_info`: Allergy information provided by user
- `previous_asked_allergies`: Boolean flag indicating allergies were asked

**Usage**:
- Tracks pending meal plan requests across conversation turns
- Enables multi-step workflow (ask allergies → combine → generate plan)
- Prevents duplicate allergy questions

#### Lesson Plan Metadata (NEW)
**Location**: `app/services/pe/ai_assistant_service.py` (line ~1978)

**Saved Fields**:
- `pending_lesson_plan_request`: Original lesson plan request text
- `forced_structure_check`: Boolean flag indicating structure validation should be enforced

**Usage**:
- Tracks pending lesson plan requests
- Enables structure validation for comprehensive lesson plans
- Supports future multi-step lesson plan workflows

#### Workout Metadata (NEW)
**Location**: `app/services/pe/ai_assistant_service.py` (line ~1987)

**Saved Fields**:
- `pending_workout_request`: Original workout request text

**Usage**:
- Tracks pending workout requests
- Enables future multi-step workout workflows
- Supports workout validation

#### Widget Metadata (NEW)
**Location**: `app/services/pe/ai_assistant_service.py` (line ~1994)

**Saved Fields**:
- `pending_widget_request`: Original widget request text

**Usage**:
- Tracks pending widget requests
- Enables widget-specific handling
- Supports widget extraction safety

### 4. Meal Plan Validation
**Location**: `app/services/pe/ai_assistant_service.py` (line ~2484)

**Validation Checks**:
- ✅ Response starts with "Day 1" or "**DAY 1:**" (after allergy answer)
- ✅ No acknowledgment phrases ("Understood", "I have updated", etc.)
- ✅ Allergy question asked (if allergy info not already recorded)
- ✅ Calories included for every food item
- ✅ Daily macros included (protein, carbs, fat)
- ✅ All requested days listed separately (no placeholders)
- ✅ No placeholder text ("repeat", "for the rest", etc.)

**Behavior**:
- Forces correction if validation fails
- Uses low temperature (0.2) for strict compliance
- Provides detailed error messages in correction prompt

### 5. Lesson Plan Validation
**Location**: `app/services/pe/ai_assistant_service.py` (line ~2667)

**Validation Checks**:
- ✅ All 14 required components present:
  - Title
  - Lesson Description
  - Learning Objectives
  - Standards (with codes and descriptions)
  - Materials List
  - Introduction
  - Activities (with time allocations)
  - Assessment
  - Exit Ticket
  - Extensions
  - Safety Considerations
  - Homework
  - Danielson Framework (all 4 domains)
  - Costa's Levels (all 3 levels)
- ✅ Standards include actual codes (not just "aligned with state standards")
- ✅ Activities include time allocations
- ✅ All 4 Danielson domains present
- ✅ All 3 Costa's levels present

**Behavior**:
- Logs validation errors (doesn't force correction)
- Lesson plans are more flexible than meal plans (no safety-critical requirements)
- Extraction logic handles missing components gracefully

### 6. Workout Validation (NEW)
**Location**: `app/services/pe/ai_assistant_service.py` (line ~2748)

**Validation Checks**:
- ✅ Required sections present:
  - Warmup/Warm-up
  - Strength Training
  - Cardio/Cardiovascular
  - Cool Down/Stretching
  - Reps/Repetitions
  - Sets
- ✅ Exercise details include rep/set information (e.g., "3 sets of 10 reps" or "3x10")

**Behavior**:
- Logs validation errors (doesn't force correction)
- Workouts are less critical than meal plans (no safety requirements)
- Extraction logic handles missing components gracefully

### 7. Widget Extraction Safety
**Location**: `app/services/pe/ai_assistant_service.py` (line ~2770)

**Priority Order**:
1. **Meal Plan Requests** (highest priority - skip lesson plan detection)
2. **Lesson Plan Requests** (requires specific keywords)
3. **Health/Nutrition Requests**
4. **Fitness/Workout Requests**

**Safety Features**:
- ✅ Meal plan requests skip lesson plan detection entirely
- ✅ Lesson plan detection requires primary keywords OR multiple secondary keywords
- ✅ Prevents false positives (e.g., "student" in meal plan requests)
- ✅ Extracts structured data only when appropriate intent is detected

### 8. Module Prompt Safety Wrapper
**Location**: `app/core/prompt_loader.py` (line ~116)

**Purpose**: Prevents module prompts from overriding top-priority system rules.

**Implementation**:
```python
wrapped_module_content = (
    "### MODULE INSTRUCTIONS (SECONDARY AUTHORITY)\n"
    "These rules support the top-priority system rules and must NOT override them.\n"
    "If a top-priority system message exists, it takes precedence over these module instructions.\n\n"
    + module_content
)
```

**Applied To**:
- ✅ Meal plan module
- ✅ Lesson plan module
- ✅ Workout module
- ✅ Widget module

## Workflow Comparison

| Feature | Meal Plan | Lesson Plan | Workout | Widget |
|---------|-----------|-------------|---------|--------|
| Safe Message Builder | ✅ Centralized | ✅ Centralized | ✅ Centralized | ✅ Centralized |
| Intent Classification | ✅ Enhanced | ✅ Enhanced | ✅ Enhanced | ✅ Enhanced |
| Metadata Tracking | ✅ Yes | ✅ Yes | ✅ Yes (NEW) | ✅ Yes (NEW) |
| Validation Logic | ✅ Strict (forces correction) | ✅ Logs errors (flexible) | ✅ Logs errors (flexible) | ❌ N/A |
| Top-Priority Instructions | ✅ Yes | ✅ Yes | ❌ N/A | ❌ N/A |
| Extraction Fixes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Duplication Prevention | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Module Safety Wrapper | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

## Files Modified

1. **`app/services/pe/ai_assistant_service.py`**:
   - Added centralized `safe_build_messages()` function
   - Applied safe message builder to all message types
   - Added lesson plan metadata tracking
   - Added workout metadata tracking (NEW)
   - Added widget metadata tracking (NEW)
   - Enhanced validation for meal plan, lesson plan, and workout workflows
   - Workout validation added (NEW)

2. **`app/core/prompt_loader.py`**:
   - Enhanced intent classification (already handles all 4 workflows)
   - Module safety wrapper already applied

3. **`app/core/prompts/module_lesson_plan.txt`**:
   - Strengthened system prompt (from previous optimization)

## Testing Recommendations

### Meal Plan Testing
1. Test multi-step workflow:
   - Request meal plan → Allergy question → Provide allergy → Generate plan
2. Verify validation:
   - Response starts with "Day 1"
   - No acknowledgment phrases
   - All days listed separately
   - Calories included for every item

### Lesson Plan Testing
1. Test comprehensive lesson plan request:
   - Request with all requirements → Verify all 14 components present
2. Verify widget extraction:
   - No duplicated headers in Curriculum Standards
   - No duplicated headers in Danielson Framework
   - No duplicated headers in Costa's Levels
3. Verify validation:
   - All required components present
   - Standards include actual codes
   - Activities include time allocations

### Workout Testing
1. Test workout request:
   - Request workout plan → Verify all required sections present
2. Verify validation:
   - Warmup section present
   - Strength training section present
   - Cardio section present
   - Cool down section present
   - Rep/set information included

### Widget Testing
1. Test widget inquiry:
   - Request widget capabilities → Verify proper widget extraction
2. Verify metadata tracking:
   - Widget request saved to metadata

## Benefits

1. **Consistency**: Both workflows use the same patterns and safety mechanisms
2. **Reliability**: Safe message builders prevent crashes
3. **Maintainability**: Centralized functions reduce code duplication
4. **Robustness**: Validation ensures quality responses
5. **Extensibility**: Metadata tracking enables future multi-step workflows

## Next Steps

1. Test both workflows on live site
2. Monitor validation logs for patterns
3. Adjust validation thresholds if needed
4. Consider adding forced correction for critical lesson plan components (similar to meal plans)

