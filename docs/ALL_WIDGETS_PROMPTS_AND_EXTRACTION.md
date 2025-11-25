# All Widgets: Prompts and Data Extraction

## Overview

Jasper has access to **39 widgets** plus additional capabilities. This document details:
- Which widgets have dedicated extraction logic
- Which widgets use GPT function calling
- Which widgets return general responses
- The prompts used for each widget type
- The extraction functions and their implementations

---

## Widget Categories

### 1. **Response-Based Extraction** (3 widgets)
These widgets extract structured data directly from AI text responses:
- ✅ **Meal Plan** (`_extract_meal_plan_data`)
- ✅ **Lesson Plan** (`_extract_lesson_plan_data`)
- ✅ **Workout Plan** (`_extract_workout_data`)

### 2. **GPT Function Calling** (20+ widgets)
These widgets use OpenAI's function calling feature to execute backend operations:
- Attendance Management
- Team & Squad Management
- Adaptive PE Support
- Performance Analytics
- Safety & Risk Management
- Comprehensive Class Insights
- Health Metrics
- Drivers Ed widgets
- Communication widgets
- And more...

### 3. **General Responses** (16+ widgets)
These widgets return general text responses without structured extraction:
- Exercise Tracker (descriptions)
- Fitness Challenges (descriptions)
- Heart Rate Zones (calculations/descriptions)
- Sports Psychology (advice)
- Timer Management (recommendations)
- Warmup Routines (descriptions)
- Weather Recommendations (descriptions)
- And more...

---

## Detailed Widget Breakdown

### ✅ **1. Meal Plan Widget** (Response-Based Extraction)

**Prompt Module**: `app/core/prompts/module_meal_plan.txt`

**Extraction Function**: `_extract_meal_plan_data()` (line 611 in `ai_assistant_service.py`)

**What It Extracts**:
```python
{
    "title": str,                    # Extracted from original message
    "description": str,              # From response text
    "daily_calories": str,           # Total daily calories
    "macros": {
        "protein": str,              # in grams
        "carbs": str,                # in grams
        "fat": str,                  # in grams
        "fiber": str,                # in grams
        "sugar": str                 # in grams
    },
    "micronutrients": {
        "vitamins": {...},           # All B vitamins, A, C, D, E, K, Folate
        "minerals": {...},           # Calcium, Iron, Magnesium, etc.
        "other": {...}               # Omega-3, Omega-6, Choline
    },
    "meals": [],                     # Single-day format (backward compatibility)
    "days": [],                      # Multi-day format: [{"day": "Day 1", "meals": [...], "daily_totals": {...}}]
    "exercise_calories": str          # Calories to burn through exercise
}
```

**Extraction Patterns**:
- Day headers: `**Day 1:**`, `Day 1:`, `*Day 1:*`
- Meal headers: `**Breakfast:**`, `Breakfast:`, `Lunch:`, `Dinner:`, `Snack:`
- Food items: `Food name (serving size: XXX calories)`
- Macros: `Protein: XXg`, `Carbs: XXg`, `Fat: XXg`
- Micronutrients: `Vitamin A: XXX IU`, `Calcium: XXX mg`

**Widget Type**: `"health"`

---

### ✅ **2. Lesson Plan Widget** (Response-Based Extraction)

**Prompt Module**: `app/core/prompts/module_lesson_plan.txt`

**Extraction Function**: `_extract_lesson_plan_data()` (line 1112 in `ai_assistant_service.py`)

**What It Extracts**:
```python
{
    "title": str,                    # Unit title
    "subject": str,                  # Subject area
    "grade_level": str,             # Grade level
    "objectives": List[str],         # Learning objectives
    "standards": List[Dict],         # Curriculum standards with codes
    "materials": List[str],          # Materials list
    "introduction": str,             # Introduction text
    "activities": List[Dict],        # Activities with descriptions and time
    "assessment": str,               # Assessment description
    "exit_ticket": str,              # Exit ticket (2-5 minutes)
    "extensions": str,               # Extension activities
    "safety_considerations": str,    # Safety notes
    "homework": str,                 # Homework assignments
    "danielson_framework": Dict,     # All 4 domains
    "costas_levels": Dict,           # Levels 1, 2, 3
    "worksheets": List[Dict],        # Generated worksheets
    "rubrics": List[Dict]            # Generated rubrics
}
```

**Extraction Patterns**:
- Title: `**Unit:** Basketball` or `Unit: Basketball`
- Grade: `**Grade:** 10th` or `Grade: 10th`
- Standards: `Standard: SHAPE.MS.1.1` or `SHAPE.MS.1.1`
- Activities: Numbered lists with time allocations
- Danielson: `Domain 1:`, `Domain 2:`, etc.
- Costa's: `Level 1:`, `Level 2:`, `Level 3:`

**Widget Type**: `"lesson_planning"`

**Additional Features**:
- Generates worksheets separately via GPT call
- Generates rubrics separately via GPT call
- Validates all 14 required components

---

### ✅ **3. Workout Plan Widget** (Response-Based Extraction)

**Prompt Module**: `app/core/prompts/module_workout.txt`

**Extraction Function**: `_extract_workout_data()` (line 209 in `ai_assistant_service.py`)

**What It Extracts**:
```python
{
    "exercises": List[Dict],         # All exercises
    "strength_training": List[Dict], # Strength exercises only
    "cardio": List[Dict],            # Cardio exercises only
    "plan_name": str,                # Plan name
    "description": str               # Plan description
}
```

**Exercise Format**:
```python
{
    "name": str,                     # Exercise name
    "sets": str,                     # Number of sets
    "reps": str,                     # Reps per set
    "weight": str,                   # Weight (if applicable)
    "rest": str,                     # Rest time
    "muscle_groups": List[str],      # Targeted muscles
    "description": str               # Exercise description
}
```

**Extraction Patterns**:
- Section headers: `**Strength Training:**`, `**Cardio:**`
- Exercise lists: Numbered or bulleted lists
- Rep/set format: `3 sets of 10 reps`, `3x10`, `10 reps x 3 sets`
- Skips meal plan content (filters out food items, day headers, etc.)

**Widget Type**: `"fitness"`

---

### 🔧 **4-23. GPT Function Calling Widgets**

These widgets use OpenAI's function calling feature. The AI receives function schemas and can call backend functions directly.

**Prompt Module**: `app/core/prompts/module_widgets.txt` (for general widget queries)

**Function Schemas**: `app/dashboard/services/widget_function_schemas.py`

**Service**: `app/dashboard/services/gpt_function_service.py`

#### **Physical Education Widgets**:

**4. Attendance Management**
- **Function**: `get_attendance_patterns()`
- **Function**: `mark_attendance()`
- **Function**: `get_class_roster()`
- **Extraction**: Returns structured JSON from backend service
- **No text extraction needed** - data comes from database queries

**5. Team & Squad Management**
- **Function**: `create_teams()`
- **Extraction**: Returns team configuration JSON
- **No text extraction needed** - data comes from backend algorithm

**6. Adaptive PE Support**
- **Function**: `suggest_adaptive_accommodations()`
- **Function**: `create_adaptive_activity()`
- **Extraction**: Returns accommodation suggestions JSON
- **No text extraction needed** - data comes from backend service

**7. Performance Analytics**
- **Function**: `predict_student_performance()`
- **Function**: `predict_student_performance_advanced()`
- **Extraction**: Returns prediction data JSON
- **No text extraction needed** - data comes from ML models

**8. Safety & Risk Management**
- **Function**: `identify_safety_risks()`
- **Extraction**: Returns risk assessment JSON
- **No text extraction needed** - data comes from backend analysis

**9. Comprehensive Class Insights**
- **Function**: `get_class_insights()`
- **Extraction**: Returns combined insights JSON
- **No text extraction needed** - aggregates data from multiple widgets

#### **Health Widgets**:

**10. Health Metrics Management**
- **Function**: `analyze_health_trends()`
- **Function**: `identify_health_risks()`
- **Function**: `generate_health_recommendations()`
- **Extraction**: Returns health data JSON
- **No text extraction needed** - data comes from health metrics database

#### **Drivers Ed Widgets**:

**11. Drivers Ed Lesson Plans**
- **Function**: `create_drivers_ed_lesson_plan()`
- **Extraction**: Returns lesson plan JSON
- **No text extraction needed** - structured data from function

**12. Student Driving Progress**
- **Function**: `track_student_driving_progress()`
- **Extraction**: Returns progress data JSON
- **No text extraction needed** - data from database

**13. Safety Incidents**
- **Function**: `record_safety_incident()`
- **Extraction**: Returns incident record JSON
- **No text extraction needed** - data saved to database

**14. Vehicle Management**
- **Function**: `manage_vehicle()`
- **Extraction**: Returns vehicle data JSON
- **No text extraction needed** - data from inventory system

#### **Communication Widgets**:

**15. Parent Communication**
- **Function**: `send_parent_message()`
- **Extraction**: Returns message status JSON
- **No text extraction needed** - message sent via email/SMS

**16. Student Communication**
- **Function**: `send_student_message()`
- **Extraction**: Returns message status JSON
- **No text extraction needed** - message sent via email/SMS

**17. Teacher Communication**
- **Function**: `send_teacher_message()`
- **Extraction**: Returns message status JSON
- **No text extraction needed** - message sent via email

**18. Administrator Communication**
- **Function**: `send_administrator_message()`
- **Extraction**: Returns message status JSON
- **No text extraction needed** - message sent via email

**19. Assignment Distribution**
- **Function**: `send_assignment_to_students()`
- **Extraction**: Returns distribution status JSON
- **No text extraction needed** - assignments sent via email

**20. Translation Services**
- **Function**: `translate_assignment_submission()`
- **Extraction**: Returns translated text
- **No text extraction needed** - translation service result

#### **Enhancement Widgets**:

**21. Automated Reporting**
- **Function**: `generate_automated_report()`
- **Extraction**: Returns report JSON/PDF/HTML
- **No text extraction needed** - report generated by backend

**22. Automated Notifications**
- **Function**: `send_automated_notification()`
- **Extraction**: Returns notification status JSON
- **No text extraction needed** - notification sent

**23. Workflow Automation**
- **Function**: `execute_workflow()`
- **Extraction**: Returns workflow status JSON
- **No text extraction needed** - workflow executed by backend

**24. Cross-Widget Intelligence**
- **Function**: `analyze_cross_widget_correlations()`
- **Extraction**: Returns correlation analysis JSON
- **No text extraction needed** - analysis from backend

**25. Anomaly Detection**
- **Function**: `detect_anomalies()`
- **Extraction**: Returns anomaly data JSON
- **No text extraction needed** - detection from ML models

**26. Smart Alerts**
- **Function**: `create_smart_alert()`
- **Extraction**: Returns alert configuration JSON
- **No text extraction needed** - alert created in system

**27. Student Self-Service**
- **Function**: `get_student_dashboard_data()`
- **Extraction**: Returns dashboard data JSON
- **No text extraction needed** - data from database

**28. Equipment Management**
- **Function**: `predict_equipment_failure()`
- **Function**: `optimize_equipment_inventory()`
- **Extraction**: Returns equipment data JSON
- **No text extraction needed** - data from inventory system

---

### 📝 **24-39. General Response Widgets**

These widgets return general text responses. No structured extraction is performed - the AI response is displayed directly.

**Prompt Module**: `app/core/prompts/module_widgets.txt` (for capability descriptions)

**No Extraction Function** - Response text is used directly

**24. Exercise Tracker**
- **Response Type**: General text (exercise recommendations, progress tracking advice)
- **No extraction** - User sees AI's text response

**25. Fitness Challenges**
- **Response Type**: General text (challenge descriptions, leaderboard info)
- **No extraction** - User sees AI's text response

**26. Heart Rate Zones**
- **Response Type**: General text (zone calculations, recommendations)
- **No extraction** - User sees AI's text response

**27. Game Predictions**
- **Response Type**: General text (game outcome predictions, matchup analysis)
- **No extraction** - User sees AI's text response

**28. Skill Assessment**
- **Response Type**: General text (rubric generation, skill gap analysis)
- **No extraction** - User sees AI's text response

**29. Sports Psychology**
- **Response Type**: General text (mental health assessments, coping strategies)
- **No extraction** - User sees AI's text response

**30. Timer Management**
- **Response Type**: General text (timer recommendations, settings)
- **No extraction** - User sees AI's text response

**31. Warmup Routines**
- **Response Type**: General text (warmup descriptions, modifications)
- **No extraction** - User sees AI's text response

**32. Weather Recommendations**
- **Response Type**: General text (indoor/outdoor activity recommendations)
- **No extraction** - User sees AI's text response

**33. Video Processing & Movement Analysis**
- **Response Type**: General text (technique assessments, movement analysis)
- **No extraction** - User sees AI's text response

**34. Routine Management**
- **Response Type**: General text (routine descriptions, organization advice)
- **No extraction** - User sees AI's text response

**35. Activity Scheduling**
- **Response Type**: General text (scheduling recommendations, conflict resolution)
- **No extraction** - User sees AI's text response

**36. Activity Tracking**
- **Response Type**: General text (tracking recommendations, metric descriptions)
- **No extraction** - User sees AI's text response

**37. Fitness Goal Management**
- **Response Type**: General text (goal recommendations, progress tracking advice)
- **No extraction** - User sees AI's text response

**38. Activity Planning**
- **Response Type**: General text (activity recommendations based on student data)
- **No extraction** - User sees AI's text response

**39. Activity Analytics**
- **Response Type**: General text (analytics descriptions, metric explanations)
- **No extraction** - User sees AI's text response

**40. Activity Recommendations**
- **Response Type**: General text (personalized activity recommendations)
- **No extraction** - User sees AI's text response

**41. Activity Visualization**
- **Response Type**: General text (chart descriptions, visualization recommendations)
- **No extraction** - User sees AI's text response

**42. Activity Export**
- **Response Type**: General text (export format recommendations)
- **No extraction** - User sees AI's text response

**43. Collaboration System**
- **Response Type**: General text (collaboration features, sharing advice)
- **No extraction** - User sees AI's text response

**44. Notification System**
- **Response Type**: General text (notification recommendations)
- **No extraction** - User sees AI's text response

**45. Progress Tracking**
- **Response Type**: General text (progress tracking advice, metric descriptions)
- **No extraction** - User sees AI's text response

**46. Activity Engagement**
- **Response Type**: General text (engagement recommendations, disengagement analysis)
- **No extraction** - User sees AI's text response

**47. Safety Report Generation**
- **Response Type**: General text (safety report descriptions)
- **No extraction** - User sees AI's text response

**48. Movement Analysis**
- **Response Type**: General text (movement pattern analysis, biomechanics)
- **No extraction** - User sees AI's text response

---

## Prompt Loading System

### Root System Prompt
**File**: `app/core/prompts/root_system_prompt.txt`
- **Always loaded** for all interactions
- Contains core identity, memory model, conversation rules, universal behavior

### Module Prompts
**File**: `app/core/prompt_loader.py`

**Intent-Based Loading**:
- `"meal_plan"` → `module_meal_plan.txt`
- `"lesson_plan"` → `module_lesson_plan.txt`
- `"workout"` → `module_workout.txt`
- `"widget"` → `module_widgets.txt`
- `"general"` → root prompt only

**Module Wrapper**:
All module prompts are wrapped with:
```
### MODULE INSTRUCTIONS (SECONDARY AUTHORITY)
These rules support the top-priority system rules and must NOT override them.
```

---

## Widget Extraction Priority

**Location**: `app/services/pe/ai_assistant_service.py` (line ~3045)

**Priority Order**:
1. **Meal Plan** (highest priority - skips lesson plan detection)
2. **Lesson Plan** (requires specific keywords)
3. **Health/Nutrition** (meal plan data extraction)
4. **Fitness/Workout** (workout data extraction)

**Logic**:
```python
if is_meal_plan_request:
    # Extract meal plan widget
    meal_plan_data = _extract_meal_plan_data(response)
    widget = {"type": "health", "data": meal_plan_data}
elif is_lesson_request:
    # Extract lesson plan widget
    lesson_data = _extract_lesson_plan_data(response)
    widget = {"type": "lesson_planning", "data": lesson_data}
elif is_health_request:
    # Try meal plan extraction
    meal_plan_data = _extract_meal_plan_data(response)
    widget = {"type": "health", "data": meal_plan_data}
elif is_fitness_request:
    # Extract workout data
    workout_data = _extract_workout_data(response)
    widget = {"type": "fitness", "data": workout_data}
```

---

## Summary Table

| Widget # | Widget Name | Extraction Type | Function/Module | Status |
|----------|-------------|-----------------|----------------|--------|
| 1 | Meal Plan | ✅ Response Extraction | `_extract_meal_plan_data()` | ✅ Implemented |
| 2 | Lesson Plan | ✅ Response Extraction | `_extract_lesson_plan_data()` | ✅ Implemented |
| 3 | Workout Plan | ✅ Response Extraction | `_extract_workout_data()` | ✅ Implemented |
| 4 | Attendance | 🔧 GPT Function | `get_attendance_patterns()` | ✅ Implemented |
| 5 | Teams | 🔧 GPT Function | `create_teams()` | ✅ Implemented |
| 6 | Adaptive PE | 🔧 GPT Function | `suggest_adaptive_accommodations()` | ✅ Implemented |
| 7 | Performance Analytics | 🔧 GPT Function | `predict_student_performance()` | ✅ Implemented |
| 8 | Safety Management | 🔧 GPT Function | `identify_safety_risks()` | ✅ Implemented |
| 9 | Class Insights | 🔧 GPT Function | `get_class_insights()` | ✅ Implemented |
| 10-23 | Health/Drivers Ed/Communication/Enhancements | 🔧 GPT Function | Various functions | ✅ Implemented |
| 24-39 | Exercise/Fitness/Activity Widgets | 📝 General Response | No extraction | ✅ Implemented |

---

## Recommendations for Future Enhancement

### Widgets That Could Benefit from Extraction:

1. **Exercise Tracker** - Extract exercise recommendations into structured format
2. **Fitness Challenges** - Extract challenge details, rules, leaderboard data
3. **Heart Rate Zones** - Extract calculated zones, target heart rates
4. **Warmup Routines** - Extract structured warmup exercises with timing
5. **Skill Assessment** - Extract rubric data, skill levels, assessment criteria
6. **Game Predictions** - Extract prediction scores, probabilities, matchup data
7. **Sports Psychology** - Extract assessment results, risk levels, recommendations

### Implementation Pattern:

For any widget that needs extraction, follow the pattern:

1. **Create extraction function** in `ai_assistant_service.py`:
   ```python
   def _extract_[widget_name]_data(self, response_text: str) -> Optional[Dict[str, Any]]:
       # Parse response_text using regex patterns
       # Return structured dictionary
   ```

2. **Add to widget extraction logic** (line ~3045):
   ```python
   if is_[widget]_request:
       widget_data = self._extract_[widget_name]_data(ai_response)
       widget = {"type": "[widget_type]", "data": widget_data}
   ```

3. **Update intent classification** in `prompt_loader.py`:
   ```python
   if "[widget_keyword]" in text:
       return "[widget_intent]"
   ```

4. **Create/update prompt module** if needed:
   - Add to `module_widgets.txt` or create `module_[widget].txt`
   - Define required structure and format

---

## Conclusion

- **3 widgets** have full response-based extraction (Meal Plan, Lesson Plan, Workout)
- **20+ widgets** use GPT function calling (no extraction needed - data from backend)
- **16+ widgets** return general text responses (no extraction needed)

**Total**: 39 widgets + enhancements, all functional with appropriate data handling methods.

