# System Prompts for Lesson Plan and Widget Extraction

## Overview

Jasper uses modular system prompts that are loaded dynamically based on user intent. This document shows the prompts used for lesson plan generation and widget extraction.

---

## Lesson Plan System Prompt

**File:** `app/core/prompts/module_lesson_plan.txt`

**When Loaded:** When user intent is classified as `"lesson_plan"`

**Content:**
```
==================================================
LESSON PLAN RULES
==================================================
Lesson plans must include:
- Title
- **Lesson Description** (3–5 sentences)
- Danielson Framework alignment (Domains 1–4, 2–3 sentences each)
- Costa's Levels of Questions (Levels 1, 2, 3)
- Standards (codes + descriptions)
- Objectives
- Materials list
- Introduction
- Activities (5–7 sentences each)
- Assessment (formative + summative)
- Exit Ticket (2–5 minutes, measurable)
- Extensions
- Safety considerations
- Homework (if applicable)

Worksheets/rubrics generated separately upon request.
```

**How It Works:**
1. User requests a lesson plan (e.g., "Create a lesson plan on basketball fundamentals")
2. Intent classifier detects `"lesson_plan"`
3. `load_prompt_modules("lesson_plan")` loads:
   - Root system prompt (`root_system_prompt.txt`)
   - Lesson plan module (`module_lesson_plan.txt`)
4. Both prompts are sent to OpenAI as system messages
5. AI generates lesson plan following the structure above
6. Backend extracts structured data using `_extract_lesson_plan_data()`

---

## Widget Extraction System Prompt

**File:** `app/core/prompts/module_widgets.txt`

**When Loaded:** When user intent is classified as `"widget"`

**Content:**
```
==================================================
DETAILED WIDGET CAPABILITIES
==================================================
When users ask about your capabilities, provide comprehensive details about these widgets:

1. Attendance Management - Track daily attendance, analyze patterns, predict absences, identify at-risk students
2. Team & Squad Management - Create balanced teams, manage multiple teams/squads
3. Adaptive PE Support - Suggest accommodations, create modified activities, track IEP requirements
4. Performance Analytics - Predict performance, analyze trends, identify students needing intervention
5. Safety & Risk Management - Identify safety risks, check medical conditions, generate safety reports
6. Comprehensive Class Insights - Combine data from multiple widgets for class overview
7. Exercise Tracker - Recommend exercises, predict progress, track performance
8. Fitness Challenges - Create challenges, track participation, maintain leaderboards
9. Heart Rate Zones - Calculate optimal zones, recommend targets, track during activities
10. Nutrition Planning - Create personalized meal plans, analyze nutrition intake
11. Parent Communication - Send messages via email/SMS with translation to 100+ languages
12. Game Predictions - Predict game outcomes, analyze matchups
13. Skill Assessment - Generate rubrics, identify skill gaps, track development
14. Sports Psychology - Assess mental health risks, suggest coping strategies
15. Timer Management - Recommend timer settings, manage multiple timers
16. Warmup Routines - Generate activity-specific warmups, create modifications
17. Weather Recommendations - Analyze weather, recommend indoor/outdoor activities
18. Lesson Plan Generation - Create comprehensive, standards-aligned lesson plans
19. Video Processing & Movement Analysis - Process videos, assess technique
20. Workout Planning - Create structured workout plans (cardio, strength, flexibility)
21. Routine Management - Create PE routines, organize activities
22. Activity Scheduling - Schedule activities, manage timing, handle conflicts
23. Activity Tracking - Track performance metrics, monitor completion
24. Fitness Goal Management - Create goals, track progress, adjust goals
25. Activity Planning - Plan activities based on student data and fitness levels
26. Activity Analytics - Analyze performance data, calculate metrics
27. Activity Recommendations - Provide personalized recommendations
28. Activity Visualization - Create charts and graphs, visualize trends
29. Activity Export - Export data in multiple formats (CSV, PDF, JSON)
30. Collaboration System - Enable real-time collaboration, share documents
31. Notification System - Send notifications, track delivery
32. Progress Tracking - Track progress across multiple metrics
33. Health & Fitness Service - Manage health metrics, track wellness
34. Class Management - Create and manage PE classes
35. Student Management - Manage student profiles, track activities
36. Health Metrics Management - Track health metrics (heart rate, BP, weight, BMI)
37. Activity Engagement - Track engagement levels, identify disengaged students
38. Safety Report Generation - Generate comprehensive safety reports
39. Movement Analysis - Analyze movement patterns and biomechanics

Plus: Health Education, Driver's Education, Equipment Management, Email/SMS communication, Microsoft/Azure AD, Outlook Calendar integration, OpenAI features.
```

**How It Works:**
1. User asks about capabilities (e.g., "What can you do?", "Show me attendance patterns")
2. Intent classifier detects `"widget"`
3. `load_prompt_modules("widget")` loads:
   - Root system prompt (`root_system_prompt.txt`)
   - Widget module (`module_widgets.txt`)
4. AI responds with detailed widget information
5. Backend may extract widget data if the request is for a specific widget operation

---

## Root System Prompt

**File:** `app/core/prompts/root_system_prompt.txt`

**When Loaded:** Always (for all intents)

**Key Sections:**
- Memory Model (no persistent memory, rely on conversation history)
- Conversation Following Rules
- Universal Behavior Rules
- Widget List (condensed)
- Safety/Allergy Policy
- Output Clarity Rules

---

## How Module Loading Works

**File:** `app/core/prompt_loader.py`

**Function:** `load_prompt_modules(intent: str)`

**Process:**
1. Always loads `root_system_prompt.txt` first
2. Based on intent, loads additional module:
   - `"meal_plan"` → `module_meal_plan.txt`
   - `"lesson_plan"` → `module_lesson_plan.txt`
   - `"workout"` → `module_workout.txt`
   - `"widget"` → `module_widgets.txt`
   - `"general"` → root prompt only
3. Wraps module content with "SECONDARY AUTHORITY" header to prevent overriding top-priority rules
4. Returns list of system messages to send to OpenAI

**Example:**
```python
# User asks: "Create a lesson plan on basketball"
intent = classify_intent("Create a lesson plan on basketball")  # Returns "lesson_plan"
messages = load_prompt_modules("lesson_plan")
# Returns:
# [
#   {"role": "system", "content": "<root_system_prompt.txt>"},
#   {"role": "system", "content": "### MODULE INSTRUCTIONS (SECONDARY AUTHORITY)\n<module_lesson_plan.txt>"}
# ]
```

---

## Lesson Plan Data Extraction

**Function:** `_extract_lesson_plan_data(response_text: str, original_message: str)`

**Location:** `app/services/pe/ai_assistant_service.py` (line ~1112)

**What It Extracts:**
- Title
- Subject
- Grade Level
- Objectives (list)
- Standards (list)
- Materials (list)
- Introduction
- Activities (list with descriptions)
- Assessment
- Exit Ticket
- Extensions
- Safety Considerations
- Homework
- Danielson Framework alignment
- Costa's Levels of Questions

**How It Works:**
1. Parses AI response text using regex patterns
2. Extracts structured data into a dictionary
3. Returns `Dict[str, Any]` with all lesson plan components
4. Used to populate lesson plan widget on dashboard

---

## Widget Extraction Logic

**Location:** `app/services/pe/ai_assistant_service.py` (line ~2670)

**Process:**
1. Check user intent and request type
2. If `is_meal_plan_request` → Extract meal plan widget data
3. Else if `is_lesson_request` → Extract lesson plan widget data
4. Else if `is_health_request` → Extract health/nutrition widget data
5. Else if `is_fitness_request` → Extract fitness/workout widget data
6. Create widget object with extracted data
7. Return widget to frontend for display

**Priority Order:**
1. Meal plan requests (highest priority - skip lesson plan detection)
2. Lesson plan requests (requires specific keywords)
3. Health/nutrition requests
4. Fitness/workout requests

---

## Intent Classification

**Function:** `classify_intent(user_message: str, previous_asked_allergies: bool = False)`

**Location:** `app/core/prompt_loader.py` (line ~28)

**Returns:** `"meal_plan"`, `"workout"`, `"lesson_plan"`, `"widget"`, `"allergy_answer"`, or `"general"`

**Keywords:**
- **Lesson Plan:** "lesson plan", "teach", "unit plan", "curriculum", "lesson", "teaching plan", "class plan"
- **Widget:** "attendance", "teams", "adaptive", "analytics", "skill", "video", "schedule", "tracking", "progress", "heart rate", "challenge", "fitness goal", "export", "safety report", "widget", "capabilities", "what can you do", "features", "tools"
- **Meal Plan:** "meal plan", "nutrition", "diet", "meal", "food plan", "eating plan", "calories", "macros", "micronutrients"
- **Workout:** "workout", "training", "lifting", "exercise plan", "fitness plan", "strength training", "cardio", "conditioning"

---

## Summary

- **Lesson Plan Prompt:** Defines structure and required components for lesson plans
- **Widget Prompt:** Lists all 39 widget capabilities for when users ask "what can you do"
- **Root Prompt:** Base instructions that apply to all interactions
- **Module Loading:** Dynamic loading based on user intent
- **Data Extraction:** Backend extracts structured data from AI responses for widget display

All prompts work together to ensure Jasper generates appropriate responses and structured data for the dashboard widgets.

