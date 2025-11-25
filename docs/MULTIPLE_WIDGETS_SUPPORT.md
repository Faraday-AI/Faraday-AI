# Multiple Widgets from Single Response

## Current Status

✅ **Infrastructure Supports Multiple Widgets**
- Response schema has both `widget_data` (single) and `widgets` (list)
- Code handles multiple widgets correctly
- When multiple widgets are found, first goes to `widget_data`, all go to `widgets` list

⚠️ **Current Limitation**
- Specialized services extract only ONE widget per response
- `extract_widget_data()` returns a single widget dict

## How to Enable Multiple Widget Extraction

### Option 1: Return List from `extract_widget_data()`

Modify `extract_widget_data()` to return a list of widgets instead of a single widget:

```python
def extract_widget_data(self, response_text: str, intent: str) -> List[Dict[str, Any]]:
    """
    Extract widget data from response.
    Can return multiple widgets from a single response.
    
    Returns:
        List of widget dictionaries, each with {"type": "...", "data": {...}}
    """
    widgets = []
    
    # Extract meal plan widget
    meal_data = widget_handler._extract_meal_plan_data(response_text)
    if meal_data.get("days"):
        widgets.append({
            "type": "meal_plan",
            "data": meal_data
        })
    
    # Extract workout widget if also present
    workout_data = widget_handler._extract_workout_data(response_text)
    if workout_data.get("exercises"):
        widgets.append({
            "type": "workout",
            "data": workout_data
        })
    
    # Extract lesson plan widget if also present
    lesson_data = widget_handler._extract_lesson_plan_data(response_text)
    if lesson_data.get("title") or lesson_data.get("objectives"):
        widgets.append({
            "type": "lesson_plan",
            "data": lesson_data
        })
    
    return widgets  # Return list instead of single dict
```

### Option 2: Add `extract_multiple_widgets()` Method

Add a new method alongside `extract_widget_data()`:

```python
def extract_widget_data(self, response_text: str, intent: str) -> Dict[str, Any]:
    """Extract primary widget (backward compatible)."""
    # Current implementation
    return widget_handler._extract_meal_plan_data(response_text)

def extract_multiple_widgets(self, response_text: str, intent: str) -> List[Dict[str, Any]]:
    """
    Extract all widgets from response.
    Returns list of widgets if multiple found, empty list if none.
    """
    widgets = []
    
    # Check for meal plan
    meal_data = widget_handler._extract_meal_plan_data(response_text)
    if meal_data.get("days"):
        widgets.append({"type": "meal_plan", "data": meal_data})
    
    # Check for workout
    workout_data = widget_handler._extract_workout_data(response_text)
    if workout_data.get("exercises"):
        widgets.append({"type": "workout", "data": workout_data})
    
    # Check for lesson plan
    lesson_data = widget_handler._extract_lesson_plan_data(response_text)
    if lesson_data.get("title") or lesson_data.get("objectives"):
        widgets.append({"type": "lesson_plan", "data": lesson_data})
    
    return widgets
```

### Option 3: Update `ai_assistant_service.py` to Handle Lists

Modify the extraction logic in `ai_assistant_service.py`:

```python
# In ai_assistant_service.py, around line 2734
if service and hasattr(service, 'extract_widget_data'):
    try:
        extracted_data = service.extract_widget_data(ai_response, user_intent)
        
        # Handle both single widget (dict) and multiple widgets (list)
        if isinstance(extracted_data, list):
            # Multiple widgets extracted
            widgets_list.extend(extracted_data)
            logger.info(f"✅ Extracted {len(extracted_data)} widgets from {service.__class__.__name__}")
        elif isinstance(extracted_data, dict):
            # Single widget (backward compatible)
            if "type" in extracted_data and "data" in extracted_data:
                widgets_list.append(extracted_data)
            else:
                widget_type = getattr(service, 'widget_type', user_intent)
                widgets_list.append({
                    "type": widget_type,
                    "data": extracted_data
                })
            logger.info(f"✅ Extracted single widget from {service.__class__.__name__}")
```

## Example Use Cases

### Use Case 1: Combined Meal + Workout Plan
**User Request:** "Create a meal plan and workout routine for my student athlete"

**Response could contain:**
- Meal plan widget (7 days of meals)
- Workout widget (weekly exercise routine)

**Result:**
```json
{
  "widget_data": {
    "type": "meal_plan",
    "data": { "days": [...] }
  },
  "widgets": [
    {
      "type": "meal_plan",
      "data": { "days": [...] }
    },
    {
      "type": "workout",
      "data": { "exercises": [...] }
    }
  ]
}
```

### Use Case 2: Lesson Plan + Attendance Analysis
**User Request:** "Create a basketball lesson plan and show attendance patterns"

**Response could contain:**
- Lesson plan widget (structured lesson)
- Attendance widget (patterns/charts)

### Use Case 3: Comprehensive Student Profile
**User Request:** "Give me everything for my student: meal plan, workout, and lesson plan"

**Response could contain:**
- Meal plan widget
- Workout widget
- Lesson plan widget

## Implementation Recommendation

**Recommended Approach: Option 3** (Update `ai_assistant_service.py`)

**Why:**
1. ✅ Backward compatible (services can still return single widget)
2. ✅ Flexible (services can return list when multiple widgets found)
3. ✅ Minimal changes to existing services
4. ✅ Centralized logic in one place

**Steps:**
1. Update `ai_assistant_service.py` extraction logic to handle lists
2. Optionally add `extract_multiple_widgets()` to services that need it
3. Update specialized service prompts to generate multiple widgets when requested
4. Test with multi-widget requests

## Testing

```python
# Test case: Multiple widgets from single response
def test_multiple_widgets():
    response = """
    **DAY 1:**
    Breakfast: Eggs and toast
    
    **Workout Plan:**
    1. Bench Press: 3x10
    2. Squats: 3x10
    """
    
    service = MealPlanService()
    widgets = service.extract_multiple_widgets(response, "meal_plan")
    
    assert len(widgets) == 2
    assert widgets[0]["type"] == "meal_plan"
    assert widgets[1]["type"] == "workout"
```

## Benefits

1. **Better User Experience:** Single request can generate multiple related widgets
2. **Efficiency:** One API call instead of multiple
3. **Context Preservation:** All widgets share the same conversation context
4. **Flexibility:** Services can choose when to extract multiple widgets

