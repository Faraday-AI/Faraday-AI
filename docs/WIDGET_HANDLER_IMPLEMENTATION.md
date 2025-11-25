# Widget Handler Implementation Guide

## Overview

The `WidgetHandler` class provides a comprehensive, production-ready interface for handling all 39+ Jasper widgets. It combines three widget handling methods:

1. **Response-Based Extraction** (3 widgets): Meal Plan, Lesson Plan, Workout
2. **GPT Function Calling** (20+ widgets): Attendance, Teams, Analytics, etc.
3. **General Response** (16+ widgets): Exercise Tracker, Fitness Challenges, etc.

## Architecture

### Class Structure

```python
class WidgetHandler:
    """Comprehensive widget handler for all 39+ Jasper widgets."""
    
    # Static methods for widget handling
    @staticmethod
    def safe_build_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]
    @staticmethod
    def classify_widget_intent(message_content: str, previous_asked_allergies: bool = False) -> str
    @staticmethod
    def extract_meal_plan_data(response_text: str, original_message: str = "") -> Optional[Dict[str, Any]]
    @staticmethod
    def extract_lesson_plan_data(response_text: str, original_message: str = "") -> Optional[Dict[str, Any]]
    @staticmethod
    def extract_workout_data(response_text: str) -> Optional[Dict[str, Any]]
    @staticmethod
    def handle_gpt_function_widget(intent: str, response_text: str) -> WidgetExtractionResult
    @staticmethod
    def handle_general_response_widget(intent: str, response_text: str) -> WidgetExtractionResult
    @staticmethod
    def extract_widget(user_intent: str, response_text: str, original_message: str = "") -> WidgetExtractionResult
    @staticmethod
    def validate_meal_plan(response_text: str, allergy_info_already_recorded: bool = False) -> List[str]
    @staticmethod
    def validate_lesson_plan(response_text: str) -> List[str]
    @staticmethod
    def validate_workout_plan(response_text: str) -> List[str]
```

### WidgetExtractionResult

Structured result object returned by all extraction methods:

```python
class WidgetExtractionResult:
    widget_type: str              # Widget type (e.g., "health", "lesson_planning", "fitness")
    data: Dict[str, Any]          # Extracted structured data
    extraction_method: str         # "response_extraction", "function_call", or "general"
    errors: List[str]             # Validation errors (if any)
    
    def to_dict(self) -> Dict[str, Any]  # Convert to dictionary for API response
```

## Usage Examples

### Example 1: Meal Plan Extraction

```python
from app.services.pe.widget_handler import WidgetHandler

# Classify intent
intent = WidgetHandler.classify_widget_intent(
    "Create a 7-day meal plan for a wrestler",
    previous_asked_allergies=False
)
# Returns: "meal_plan"

# Extract widget data
response_text = "**Day 1:**\n**Breakfast:** Oatmeal (1 cup: 150 calories)..."
result = WidgetHandler.extract_widget(intent, response_text, "Create a 7-day meal plan for a wrestler")

# Access results
print(result.widget_type)          # "health"
print(result.extraction_method)     # "response_extraction"
print(result.data["days"])          # List of day objects with meals
print(result.errors)               # [] (empty if valid)
```

### Example 2: GPT Function Calling Widget

```python
# Classify intent
intent = WidgetHandler.classify_widget_intent("Show me attendance patterns for Period 4")
# Returns: "attendance"

# Extract widget data
result = WidgetHandler.extract_widget(intent, "I'll retrieve attendance patterns...")

# Access results
print(result.widget_type)          # "attendance"
print(result.extraction_method)     # "function_call"
print(result.data["function_name"]) # "get_attendance_patterns"
print(result.data["requires_function_call"])  # True
```

### Example 3: General Response Widget

```python
# Classify intent
intent = WidgetHandler.classify_widget_intent("What can you do?")
# Returns: "widget"

# Extract widget data
result = WidgetHandler.extract_widget(intent, "I can help with attendance, teams, meal plans...")

# Access results
print(result.widget_type)          # "widget"
print(result.extraction_method)     # "general"
print(result.data["response"])      # Full response text
```

### Example 4: Validation

```python
# Validate meal plan
meal_plan_text = "**Day 1:**\n**Breakfast:** Oatmeal (1 cup: 150 calories)..."
errors = WidgetHandler.validate_meal_plan(meal_plan_text, allergy_info_already_recorded=True)

if errors:
    print(f"Validation failed: {errors}")
    # Handle errors (e.g., request correction)
else:
    print("Meal plan is valid!")
```

## Integration with AIAssistantService

### Step 1: Import WidgetHandler

```python
from app.services.pe.widget_handler import WidgetHandler, WidgetExtractionResult
```

### Step 2: Use in Chat Processing

```python
def process_chat_message(self, chat_request: AIAssistantChatRequest, ...):
    # Classify intent
    user_intent = WidgetHandler.classify_widget_intent(
        chat_request.message,
        previous_asked_allergies=previous_asked_allergies
    )
    
    # Get AI response
    ai_response = self._call_openai(...)
    
    # Extract widget data
    widget_result = WidgetHandler.extract_widget(
        user_intent,
        ai_response,
        chat_request.message
    )
    
    # Validate (for response-based widgets)
    if user_intent == "meal_plan":
        validation_errors = WidgetHandler.validate_meal_plan(
            ai_response,
            allergy_info_already_recorded=previous_asked_allergies
        )
        if validation_errors:
            # Request correction (auto-correction logic)
            corrected_response = self._request_correction(ai_response, validation_errors)
            widget_result = WidgetHandler.extract_widget(
                user_intent,
                corrected_response,
                chat_request.message
            )
    
    # Return response with widget data
    return AIAssistantChatResponse(
        response=ai_response,
        widget_data=widget_result.to_dict() if widget_result else None,
        ...
    )
```

## Widget Categories

### Response-Based Extraction Widgets

These widgets extract structured data from AI text responses:

1. **Meal Plan** (`extract_meal_plan_data`)
   - Extracts: Days, meals, calories, macros, micronutrients
   - Widget type: `"health"`
   - Validation: Required (safety-critical)

2. **Lesson Plan** (`extract_lesson_plan_data`)
   - Extracts: Title, objectives, activities, standards, Danielson, Costa's
   - Widget type: `"lesson_planning"`
   - Validation: Optional (logs errors)

3. **Workout Plan** (`extract_workout_data`)
   - Extracts: Exercises, sets, reps, strength/cardio sections
   - Widget type: `"fitness"`
   - Validation: Optional (logs errors)

### GPT Function Calling Widgets

These widgets use OpenAI's function calling feature:

- Attendance Management → `get_attendance_patterns`
- Team & Squad Management → `create_teams`
- Adaptive PE Support → `suggest_adaptive_accommodations`
- Performance Analytics → `predict_student_performance`
- Safety & Risk Management → `identify_safety_risks`
- Class Insights → `get_class_insights`
- Health Metrics → `analyze_health_trends`
- Drivers Ed → `create_drivers_ed_lesson_plan`
- Parent Communication → `send_parent_message`
- Student Communication → `send_student_message`
- Notifications → `send_automated_notification`
- And more...

### General Response Widgets

These widgets return general text responses:

- Exercise Tracker
- Fitness Challenges
- Heart Rate Zones
- Game Predictions
- Skill Assessment
- Sports Psychology
- Timer Management
- Warmup Routines
- Weather Recommendations
- And more...

## Validation

### Meal Plan Validation (Safety-Critical)

```python
errors = WidgetHandler.validate_meal_plan(
    response_text,
    allergy_info_already_recorded=False
)
```

**Checks:**
- Response starts with "Day 1"
- Allergy question asked (if allergies not recorded)
- Calories included for every food item
- No acknowledgment phrases

**Action:** Forces auto-correction if validation fails

### Lesson Plan Validation (Optional)

```python
errors = WidgetHandler.validate_lesson_plan(response_text)
```

**Checks:**
- Objectives present
- Activities present
- Assessment present
- Danielson Framework present
- Costa's Levels present

**Action:** Logs errors (doesn't force correction)

### Workout Plan Validation (Optional)

```python
errors = WidgetHandler.validate_workout_plan(response_text)
```

**Checks:**
- Warmup section present
- Strength training section present
- Cardio section present
- Cool down section present
- Rep/set information present

**Action:** Logs errors (doesn't force correction)

## Intent Classification

The `classify_widget_intent` method uses keyword matching to determine widget intent:

**Priority Order:**
1. Allergy answers (if `previous_asked_allergies=True`)
2. Meal plan keywords
3. Lesson plan keywords
4. Workout keywords
5. GPT function calling widget keywords
6. General widget keywords
7. Default: `"general"`

**Example Keywords:**
- Meal Plan: "meal plan", "nutrition", "diet", "calories", "macros"
- Lesson Plan: "lesson plan", "teach", "curriculum", "unit plan"
- Workout: "workout", "training", "lifting", "exercise plan"
- Attendance: "attendance", "absent", "present", "attendance pattern"
- Teams: "teams", "squads", "team creation", "balanced teams"

## Error Handling

All extraction methods return `Optional[Dict[str, Any]]` or `WidgetExtractionResult`:

- **Success:** Returns structured data
- **Failure:** Returns `None` or `WidgetExtractionResult` with errors

**Example:**
```python
result = WidgetHandler.extract_meal_plan_data(response_text)
if result:
    # Success - use result
    widget_data = result
else:
    # Failure - handle gracefully
    logger.warning("Failed to extract meal plan data")
    widget_data = {"response": response_text}  # Fallback to general response
```

## Type Safety

All methods use Python type hints for better IDE support and static analysis:

```python
def extract_meal_plan_data(
    response_text: str,
    original_message: str = ""
) -> Optional[Dict[str, Any]]:
    """Extract structured meal plan data."""
    ...
```

## Production Considerations

1. **Performance:** All extraction methods use efficient regex patterns
2. **Error Handling:** Graceful fallbacks for extraction failures
3. **Validation:** Safety-critical validation for meal plans
4. **Type Safety:** Full type hints for better maintainability
5. **Logging:** Comprehensive logging for debugging
6. **Extensibility:** Easy to add new widgets or extraction methods

## Future Enhancements

### Potential Additions:

1. **Exercise Tracker Extraction**
   - Extract exercise recommendations into structured format
   - Track sets, reps, progress over time

2. **Fitness Challenge Extraction**
   - Extract challenge details, rules, leaderboard data
   - Track participation and completion

3. **Heart Rate Zone Extraction**
   - Extract calculated zones, target heart rates
   - Format for visualization

4. **Warmup Routine Extraction**
   - Extract structured warmup exercises with timing
   - Organize by activity type

5. **Skill Assessment Extraction**
   - Extract rubric data, skill levels, assessment criteria
   - Format for grading

## Testing

### Unit Tests

```python
def test_meal_plan_extraction():
    response = "**Day 1:**\n**Breakfast:** Oatmeal (1 cup: 150 calories)"
    result = WidgetHandler.extract_meal_plan_data(response)
    assert result is not None
    assert "days" in result
    assert len(result["days"]) > 0

def test_intent_classification():
    intent = WidgetHandler.classify_widget_intent("Create a meal plan")
    assert intent == "meal_plan"

def test_validation():
    response = "**Day 1:**\n**Breakfast:** Oatmeal (1 cup: 150 calories)"
    errors = WidgetHandler.validate_meal_plan(response, allergy_info_already_recorded=True)
    assert len(errors) == 0
```

## Conclusion

The `WidgetHandler` class provides a unified, production-ready interface for handling all 39+ Jasper widgets. It combines response-based extraction, GPT function calling, and general response handling into a single, easy-to-use API.

**Key Benefits:**
- ✅ Type-safe with full type hints
- ✅ Comprehensive error handling
- ✅ Safety-critical validation for meal plans
- ✅ Extensible architecture for new widgets
- ✅ Production-ready with logging and error recovery
- ✅ Follows the same robust pattern as Meal + Lesson + Workout patches

