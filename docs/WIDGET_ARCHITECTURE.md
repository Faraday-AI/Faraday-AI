# Jasper Hybrid Widget Architecture

## Overview

Jasper uses a **hybrid widget architecture** that combines:
- **Shared extraction functions** for common parsing patterns
- **Per-service handlers** for widget-specific logic
- **Model tiering** for performance and cost optimization

This architecture provides modularity, scalability, and maintainability while reducing code duplication.

---

## Architecture Flow

```
                                ┌─────────────────────────┐
                                │       User Request       │
                                │  "Show attendance",      │
                                │  "Meal plan for X"       │
                                └─────────────┬───────────┘
                                              │
                                              ▼
                                ┌─────────────────────────┐
                                │ Intent Classification   │
                                │ classify_intent()       │
                                │ Model: gpt-4o-mini     │
                                │ (fast, in-memory OK)    │
                                └─────────────┬───────────┘
                                              │
                                              ▼
                                ┌─────────────────────────┐
                                │     ModelRouter /       │
                                │    ServiceRegistry      │
                                │ route(intent) → service │
                                └─────────────┬───────────┘
                                              │
               ┌──────────────────────────────┴──────────────────────────────┐
               │                                                              │
               ▼                                                              ▼
      ┌──────────────────────┐                                      ┌──────────────────────┐
      │  Specialized Service │                                      │ General Widget /     │
      │  AttendanceService   │                                      │ Response Service     │
      │  Model: gpt-4o-mini  │                                      │ Model: gpt-4o-mini   │
      └─────────────┬────────┘                                      └─────────────┬────────┘
                    │                                                              │
                    ▼                                                              ▼
       ┌──────────────────────────┐                                  ┌──────────────────────────┐
       │ extract_widget_data()     │                                  │ extract_widget_data()     │
       │ Custom logic / GPT fn     │                                  │ GPT function outputs      │
       └─────────────┬───────────┘                                  └─────────────┬───────────┘
                     │                                                              │
         ┌───────────┴────────────┐                              ┌──────────────────┴─────────────┐
         │ Optional Shared Helpers │                              │ Optional Shared Helpers         │
         │ (widget_handler.py)     │                              │ (widget_handler.py)            │
         │ _extract_meal_plan_data │                              │ _extract_workout_data etc.     │
         │ _extract_lesson_plan    │                              │                                 │
         └───────────┬────────────┘                              └──────────────────┬─────────────┘
                     │                                                              │
                     ▼                                                              ▼
          ┌───────────────────────┐                                    ┌───────────────────────┐
          │ Parsed Widget Data     │                                    │ Parsed Widget Data     │
          │ (JSON, structured)    │                                    │ (JSON, structured)    │
          └─────────────┬─────────┘                                    └─────────────┬─────────┘
                        │                                                      │
                        ▼                                                      ▼
                             ┌─────────────────────────┐
                             │   Response to User     │
                             │  (Message + Widgets)   │
                             └─────────────────────────┘
```

---

## Components

### 1. Intent Classification

**Location:** `app/services/pe/widget_handler.py::classify_intent()`

**Purpose:** Fast, keyword-based intent classification (no API call needed)

**Model:** None (in-memory keyword matching)

**Returns:** Intent string (`"attendance"`, `"meal_plan"`, `"lesson_plan"`, `"workout"`, `"widget"`, `"general"`)

---

### 2. ModelRouter / ServiceRegistry

**Location:** 
- `app/services/pe/model_router.py`
- `app/services/pe/specialized_services/service_registry.py`

**Purpose:** Routes intents to specialized services or fallback

**Flow:**
1. `ModelRouter.route(intent, user_request, context)` called
2. `ServiceRegistry.get_service(intent)` looks up service
3. If service found → call `service.process(user_request, context)`
4. If no service → fallback to lightweight router prompt

**Fallback Model:** `gpt-4o-mini`

---

### 3. Specialized Services

Each widget has its own specialized service in `app/services/pe/specialized_services/`:

#### AttendanceService
- **Model:** `gpt-4o-mini`
- **Extraction:** Custom logic (GPT function calling, data from backend)
- **Prompt:** `specialized_attendance.txt`
- **Intents:** `["attendance", "attendance_patterns", "attendance_analysis"]`

#### LessonPlanService
- **Model:** `gpt-4o`
- **Extraction:** Delegates to `widget_handler._extract_lesson_plan_data()`
- **Prompt:** `specialized_lesson_plan.txt`
- **Intents:** `["lesson_plan", "lesson", "unit_plan", "curriculum"]`

#### MealPlanService
- **Model:** `gpt-4o`
- **Extraction:** Delegates to `widget_handler._extract_meal_plan_data()`
- **Prompt:** `specialized_meal_plan.txt`
- **Intents:** `["meal_plan", "allergy_answer", "nutrition", "diet"]`

#### WorkoutService
- **Model:** `gpt-4o`
- **Extraction:** Delegates to `widget_handler._extract_workout_data()`
- **Prompt:** `specialized_workout.txt`
- **Intents:** `["workout", "training", "exercise_plan", "fitness_plan"]`

#### GeneralWidgetService
- **Model:** `gpt-4o-mini`
- **Extraction:** Custom logic (GPT function calling widgets)
- **Prompt:** `specialized_general_widgets.txt`
- **Intents:** All GPT function calling widgets (Teams, Analytics, Safety, etc.)

#### GeneralResponseService
- **Model:** `gpt-4o-mini`
- **Extraction:** Custom logic (text-based responses)
- **Prompt:** `specialized_general_response.txt`
- **Intents:** General text-based response widgets

---

### 4. Shared Extraction Functions

**Location:** `app/services/pe/widget_handler.py`

**Purpose:** Reusable parsing functions for response-based widgets

**Functions:**
- `_extract_meal_plan_data(response_text)` → Extracts meal plan structure from text
- `_extract_lesson_plan_data(response_text)` → Extracts lesson plan structure from text
- `_extract_workout_data(response_text)` → Extracts workout structure from text

**Usage:** Called by specialized services that need structured parsing:
- `MealPlanService.extract_widget_data()` → calls `_extract_meal_plan_data()`
- `LessonPlanService.extract_widget_data()` → calls `_extract_lesson_plan_data()`
- `WorkoutService.extract_widget_data()` → calls `_extract_workout_data()`

**Note:** Services call these functions directly (not through `extract_widget()` router)

---

## Model Tiering Strategy

### Model Selection by Service

| Service / Component               | GPT Model       | Rationale                                         |
|----------------------------------|----------------|---------------------------------------------------|
| Intent Classification             | None (in-memory) | Fast keyword matching, no API call needed        |
| Router Prompt (Fallback)          | gpt-4o-mini    | Lightweight routing, fast responses              |
| Attendance Widget                 | gpt-4o-mini    | Simple data queries, low token usage             |
| General Widgets / Safety / Others | gpt-4o-mini    | Fast widget handling, sufficient quality         |
| Lesson Plan Service                | gpt-4o         | High-quality educational content required        |
| Meal Plan Service                  | gpt-4o         | Critical for nutrition accuracy and safety       |
| Workout Plan Service               | gpt-4o         | Detailed exercise plans, safety considerations   |
| Complex Analysis / Fallback       | gpt-4-turbo    | Advanced reasoning for complex requests          |

### Performance Benefits

- **Speed:** ~60-70% faster on most requests (gpt-4o-mini for majority)
- **Cost:** ~60-70% reduction (cheaper model for most widgets)
- **Quality:** High-value outputs (plans) use gpt-4o for best results

---

## Adding New Widgets

### Step-by-Step Guide

1. **Create Specialized Service**
   ```python
   # app/services/pe/specialized_services/new_widget_service.py
   class NewWidgetService(BaseWidgetService, BaseSpecializedService):
       def __init__(self, db, openai_client):
           BaseWidgetService.__init__(self, db, openai_client)
           BaseSpecializedService.__init__(self, db, openai_client)
           self.prompt_file = "prompts/new_widget.txt"
           self.model = os.getenv("JASPER_MODEL", "gpt-4o")  # or gpt-4o-mini
           self.widget_type = "new_widget"
       
       def get_supported_intents(self) -> List[str]:
           return ["new_widget", "related_intent"]
       
       def extract_widget_data(self, response_text: str, intent: str) -> Dict[str, Any]:
           # Option 1: Use shared extraction function
           return widget_handler._extract_new_widget_data(response_text)
           
           # Option 2: Custom logic
           return {"type": "new_widget", "data": response_text}
   ```

2. **Create Specialized Prompt** (if needed)
   ```text
   # app/core/prompts/specialized_new_widget.txt
   You are Jasper, specialized in [Widget Name]...
   ```

3. **Add Shared Extraction Function** (if response-based parsing needed)
   ```python
   # app/services/pe/widget_handler.py
   def _extract_new_widget_data(response_text: str) -> Dict[str, Any]:
       # Parse response_text and return structured data
       return {"type": "new_widget", "data": {...}}
   ```

4. **Register in ServiceRegistry**
   ```python
   # app/services/pe/specialized_services/service_registry.py
   from app.services.pe.specialized_services.new_widget_service import NewWidgetService
   
   def register_defaults(self):
       self._services.update({
           # ... existing services ...
           "new_widget": NewWidgetService,
       })
   ```

5. **Update Intent Classification** (if needed)
   ```python
   # app/services/pe/widget_handler.py::classify_intent()
   if "new_widget_keyword" in msg_lower:
       return "new_widget"
   ```

---

## Key Principles

### ✅ DO

1. **One handler per service/widget**
   - Each widget gets its own specialized service
   - Service encapsulates prompt, model, extraction, formatting

2. **Use shared extraction for common patterns**
   - Response-based widgets (meal, lesson, workout) use shared functions
   - Reduces code duplication

3. **Keep extraction functions focused**
   - Each `_extract_*_data()` function handles one widget type
   - Avoid monolithic functions

4. **Model tiering for optimization**
   - Use `gpt-4o-mini` for fast/simple widgets
   - Use `gpt-4o` for high-quality plans
   - Use `gpt-4-turbo` for complex analysis

5. **Service encapsulation**
   - Service owns its prompt, model, extraction logic
   - Shared functions are utilities, not core service logic

### ❌ DON'T

1. **Don't create monolithic extraction functions**
   - Avoid `extract_all_widgets()` with massive if/else chains
   - Keep functions small and focused

2. **Don't tightly couple services**
   - Services should be independent
   - Shared functions are utilities, not dependencies

3. **Don't skip service registration**
   - Always register new services in `ServiceRegistry`
   - Update intent classification if needed

4. **Don't mix extraction patterns**
   - Response-based widgets → use shared extraction
   - GPT function widgets → use custom logic
   - Don't force one pattern on all widgets

---

## Architecture Benefits

### Modularity
- Each widget is fully encapsulated
- Easy to test and optimize independently
- Clear separation of concerns

### Performance
- Small, focused extraction functions
- No parsing overhead for unrelated widgets
- Model tiering optimizes speed and cost

### Scalability
- Adding new widgets is plug-and-play
- Minimal changes to existing code
- Clear extension points

### Maintainability
- Shared logic reduces duplication
- No tightly coupled spaghetti code
- Easy to debug and modify

### Flexibility
- Mix of regex extraction and GPT function outputs
- Services can override shared extraction if needed
- Supports different widget patterns

---

## File Structure

```
app/services/pe/
├── widget_handler.py              # Shared extraction functions + intent classification
├── model_router.py                 # Routes intents to services
├── base_widget_service.py         # Base class for widget services
├── ai_assistant_service.py        # Main AI assistant (uses ModelRouter)
└── specialized_services/
    ├── __init__.py
    ├── service_registry.py         # Service registration
    ├── base_specialized_service.py # Base class for specialized services
    ├── attendance_service.py       # Attendance widget
    ├── lesson_plan_service.py      # Lesson plan widget
    ├── meal_plan_service.py        # Meal plan widget
    ├── workout_service.py          # Workout widget
    ├── general_widget_service.py   # GPT function calling widgets
    └── general_response_service.py # Text-based response widgets

app/core/prompts/
├── specialized_attendance.txt
├── specialized_lesson_plan.txt
├── specialized_meal_plan.txt
├── specialized_workout.txt
├── specialized_general_widgets.txt
├── specialized_general_response.txt
└── jasper_router.txt              # Fallback router prompt
```

---

## Testing

See `tests/test_hybrid_architecture.py` for:
- Intent classification tests
- Service registry routing tests
- Model router tests
- Widget data extraction tests
- End-to-end flow tests

---

## Implementation Status

### ✅ Fully Implemented

- **Intent Classification:** Keyword-based, in-memory (no API call)
- **ModelRouter:** Routes intents to specialized services with fallback
- **ServiceRegistry:** Maps intents to services, supports `should_handle()` checks
- **Specialized Services:** All 6 services implemented with correct model tiering
- **Shared Extraction:** Meal plan, lesson plan, workout extraction functions
- **Model Tiering:** Correct models assigned per service
- **Widget Data Extraction:** Automatic extraction after ModelRouter responses

### Recent Adjustments Made

1. **ServiceRegistry Fallbacks:**
   - Added fallback to `GeneralResponseService` for "general" intent
   - Improved fallback logic for widget vs general intents

2. **Intent Support:**
   - `GeneralWidgetService` now explicitly supports "widget" intent
   - `GeneralResponseService` now explicitly supports "general" intent
   - Added additional widget keywords to `GeneralWidgetService`

3. **Documentation:**
   - Created comprehensive architecture documentation
   - Documented model tiering strategy
   - Added step-by-step guide for new widgets

---

## Related Documentation

- `docs/WIDGET_MAINTENANCE_GUIDE.md` - Maintenance and expansion guide
- `docs/HYBRID_ARCHITECTURE_FLOW.md` - Detailed flow diagrams
- `docs/MODEL_MAPPING_IMPLEMENTATION.md` - Model tiering details
- `docs/TESTING_HYBRID_ARCHITECTURE.md` - Testing guide

