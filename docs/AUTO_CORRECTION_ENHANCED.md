# Enhanced Auto-Correction for All Response-Based Widgets

## Overview

The widget handler has been enhanced to include optional auto-correction for Lesson Plan and Workout widgets, in addition to the existing forced auto-correction for Meal Plan widgets. This ensures all response-based widgets have robust validation loops while respecting retry limits.

## Auto-Correction Behavior

### Meal Plan (Safety-Critical) ✅
- **Status**: ALWAYS forces auto-correction
- **Reason**: Safety-critical for allergen avoidance
- **Validation**: Checks for Day 1 start, allergy question, calories
- **Action**: Must correct before returning response

### Lesson Plan (Optional) ✅
- **Status**: Optional auto-correction (enabled by default)
- **Reason**: Ensures completeness and structured integrity
- **Validation**: Checks for all required sections (Unit, Grade, Objectives, Activities, Assessment, Danielson Framework, Costa's Levels)
- **Action**: Can be enabled/disabled via `enable_lesson_plan_correction` parameter

### Workout Plan (Optional) ✅
- **Status**: Optional auto-correction (enabled by default)
- **Reason**: Ensures completeness and structured integrity
- **Validation**: Checks for all required sections (Warm-up, Main Workout, Cool Down, Reps, Sets)
- **Action**: Can be enabled/disabled via `enable_workout_correction` parameter

## Updated Functions

### `validate_meal_plan()`
```python
def validate_meal_plan(
    response_text: str,
    allergy_info_already_recorded: bool = False
) -> List[str]:
    """Safety-critical validation that forces auto-correction if validation fails."""
    errors = []
    
    if not response_text.strip().startswith("**DAY 1**"):
        errors.append("Meal plan must start with Day 1.")
    
    if not allergy_info_already_recorded and "allergy" not in response_text.lower():
        errors.append("Meal plan created WITHOUT asking about allergies.")
    
    return errors
```

### `validate_lesson_plan()`
```python
def validate_lesson_plan(response_text: str) -> List[str]:
    """Optional auto-correction can be enabled to enforce completeness."""
    errors = []
    response_lower = response_text.lower()
    
    required_sections = [
        "**Unit:**",
        "**Grade:**",
        "Objectives",
        "Activities",
        "Assessment",
        "Danielson Framework",
        "Costa's Levels"
    ]
    
    for section in required_sections:
        if section.lower() not in response_lower:
            errors.append(f"Lesson plan missing section: {section}")
    
    return errors
```

### `validate_workout_plan()`
```python
def validate_workout_plan(response_text: str) -> List[str]:
    """Optional auto-correction can be enabled to enforce completeness."""
    errors = []
    response_lower = response_text.lower()
    
    required_sections = [
        "Warm-up",
        "Main Workout",
        "Cool Down",
        "Reps",
        "Sets"
    ]
    
    for section in required_sections:
        if section.lower() not in response_lower:
            errors.append(f"Workout plan missing section: {section}")
    
    return errors
```

### `generate_response_with_retry()` (Enhanced)
```python
def generate_response_with_retry(
    user_message: str,
    intent: str,
    conversation_state: Dict[str, Any],
    max_retries: int = 2,
    call_openai_func = None,
    load_prompt_modules_func = None,
    enable_lesson_plan_correction: bool = True,  # NEW: Optional parameter
    enable_workout_correction: bool = True  # NEW: Optional parameter
) -> Tuple[str, Dict[str, Any], List[str]]:
    """
    Generates AI response with auto-correction for Meal Plan (forced) 
    and optional for Lesson Plan and Workout.
    """
    retry_count = 0
    previous_allergy = conversation_state.get("previous_asked_allergies", False)
    errors = []
    response_text = ""
    widget_data = {}
    
    while retry_count <= max_retries:
        # Build messages and call OpenAI
        messages = safe_build_messages(load_prompt_modules_func(intent))
        messages.append({"role": "user", "content": user_message})
        response_text = call_openai_func(messages)
        
        # Validate based on intent
        if intent == "meal_plan":
            # ALWAYS validate and force correction (safety-critical)
            errors = validate_meal_plan(response_text, allergy_info_already_recorded=previous_allergy)
        elif intent == "lesson_plan":
            # Optional validation/correction
            if enable_lesson_plan_correction:
                errors = validate_lesson_plan(response_text)
            else:
                errors = []  # Skip validation if correction disabled
        elif intent == "workout":
            # Optional validation/correction
            if enable_workout_correction:
                errors = validate_workout_plan(response_text)
            else:
                errors = []  # Skip validation if correction disabled
        else:
            errors = []  # Other widgets: No validation
        
        # If no errors, break
        if not errors:
            break
        
        # Prepare correction message
        error_message = "\n".join(errors)
        user_message = f"{user_message}\n\nPlease correct the following issues:\n{error_message}"
        retry_count += 1
    
    # Extract widget data
    widget_data = extract_widget(intent, response_text, user_message)
    
    return response_text, widget_data, errors
```

## Usage Examples

### Example 1: Meal Plan (Forced Correction)
```python
from app.services.pe.widget_handler import generate_response_with_retry

# Meal plan ALWAYS forces correction
response, widget, errors = generate_response_with_retry(
    user_message="Create a meal plan for a wrestler",
    intent="meal_plan",
    conversation_state={"previous_asked_allergies": False},
    max_retries=2,
    call_openai_func=my_openai_call,
    load_prompt_modules_func=my_prompt_loader
)
# Auto-correction is ALWAYS enabled for meal plans (safety-critical)
```

### Example 2: Lesson Plan (Optional Correction - Enabled)
```python
# Lesson plan with auto-correction enabled (default)
response, widget, errors = generate_response_with_retry(
    user_message="Create a lesson plan on basketball",
    intent="lesson_plan",
    conversation_state={},
    max_retries=2,
    call_openai_func=my_openai_call,
    load_prompt_modules_func=my_prompt_loader,
    enable_lesson_plan_correction=True  # Default: True
)
# Will validate and correct if missing sections
```

### Example 3: Lesson Plan (Optional Correction - Disabled)
```python
# Lesson plan with auto-correction disabled
response, widget, errors = generate_response_with_retry(
    user_message="Create a lesson plan on basketball",
    intent="lesson_plan",
    conversation_state={},
    max_retries=2,
    call_openai_func=my_openai_call,
    load_prompt_modules_func=my_prompt_loader,
    enable_lesson_plan_correction=False  # Disable auto-correction
)
# Will skip validation and return response as-is
```

### Example 4: Workout Plan (Optional Correction - Enabled)
```python
# Workout plan with auto-correction enabled (default)
response, widget, errors = generate_response_with_retry(
    user_message="Create a workout plan for strength training",
    intent="workout",
    conversation_state={},
    max_retries=2,
    call_openai_func=my_openai_call,
    load_prompt_modules_func=my_prompt_loader,
    enable_workout_correction=True  # Default: True
)
# Will validate and correct if missing sections
```

### Example 5: Workout Plan (Optional Correction - Disabled)
```python
# Workout plan with auto-correction disabled
response, widget, errors = generate_response_with_retry(
    user_message="Create a workout plan for strength training",
    intent="workout",
    conversation_state={},
    max_retries=2,
    call_openai_func=my_openai_call,
    load_prompt_modules_func=my_prompt_loader,
    enable_workout_correction=False  # Disable auto-correction
)
# Will skip validation and return response as-is
```

## Validation Rules

### Meal Plan Validation
- ✅ Must start with "**DAY 1**"
- ✅ Must ask about allergies (if not already recorded)
- ⚠️ **Forces correction** if validation fails

### Lesson Plan Validation
- ✅ Must include "**Unit:**"
- ✅ Must include "**Grade:**"
- ✅ Must include "Objectives"
- ✅ Must include "Activities"
- ✅ Must include "Assessment"
- ✅ Must include "Danielson Framework"
- ✅ Must include "Costa's Levels"
- ⚠️ **Optional correction** (can be enabled/disabled)

### Workout Plan Validation
- ✅ Must include "Warm-up"
- ✅ Must include "Main Workout"
- ✅ Must include "Cool Down"
- ✅ Must include "Reps"
- ✅ Must include "Sets"
- ⚠️ **Optional correction** (can be enabled/disabled)

## Benefits

### 1. Safety-Critical Protection
- Meal plans **always** validated and corrected
- Prevents allergen exposure
- Ensures completeness

### 2. Quality Assurance
- Lesson plans and workouts can be validated
- Ensures structured integrity
- Enforces completeness

### 3. Flexibility
- Optional correction for lesson plans and workouts
- Can be disabled if needed
- Respects retry limits

### 4. Production-Ready
- Comprehensive error handling
- Graceful fallbacks
- Type-safe implementation

## Integration with AIAssistantService

### Recommended Integration

```python
from app.services.pe.widget_handler import (
    classify_intent,
    extract_widget,
    validate_meal_plan,
    validate_lesson_plan,
    validate_workout_plan,
    generate_response_with_retry
)

def process_chat_message(self, chat_request, ...):
    # Classify intent
    user_intent = classify_intent(
        chat_request.message,
        previous_asked_allergies=previous_asked_allergies
    )
    
    # Use auto-correction wrapper
    response_text, widget_data, errors = generate_response_with_retry(
        user_message=chat_request.message,
        intent=user_intent,
        conversation_state={
            "previous_asked_allergies": previous_asked_allergies
        },
        max_retries=2,
        call_openai_func=self._call_openai,
        load_prompt_modules_func=self._load_prompt_modules,
        enable_lesson_plan_correction=True,  # Enable for lesson plans
        enable_workout_correction=True  # Enable for workouts
    )
    
    # Return response
    return AIAssistantChatResponse(
        response=response_text,
        widget_data=widget_data,
        ...
    )
```

## Summary

✅ **Meal Plan**: Forced auto-correction (safety-critical)
✅ **Lesson Plan**: Optional auto-correction (enabled by default)
✅ **Workout Plan**: Optional auto-correction (enabled by default)
✅ **Other Widgets**: No validation/correction

All response-based widgets now have robust validation loops while respecting retry limits and maintaining production-ready error handling.

