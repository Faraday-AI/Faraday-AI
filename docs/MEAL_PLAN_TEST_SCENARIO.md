# Meal Plan Workflow Test Scenario
## High School Wrestler with Tree Nut Allergy

This document outlines a comprehensive test scenario to validate the complete meal plan workflow, including pending request detection, allergy answer handling, correct module loading, and proper widget data extraction.

---

## Test Scenario Overview

**Scenario**: 16-year-old high school wrestler needs a 7-day meal plan with tree nut allergy

**Goal**: Validate that:
- ✅ Pending meal plan detection works
- ✅ Allergy answer handling triggers meal plan generation
- ✅ Correct module (meal_plan) is loaded (not lesson_plan)
- ✅ Proper widget data (meal_plan) is returned
- ✅ 7-day meal plan output without placeholders
- ✅ All allergens are avoided

---

## 1️⃣ User Inputs (Conversation Flow)

### Step 1: Initial Meal Plan Request
```json
{
  "role": "user",
  "conversation_id": "test_convo_001",
  "content": "I have a student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combined strength and cardio training outside of practice. I need a 7-day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities."
}
```

**Expected Backend Response**:
- ✅ Detects `is_meal_plan_request = True`
- ✅ No allergy info found in conversation
- ✅ Returns hardcoded allergy question (NO API CALL)
- ✅ Saves `pending_meal_plan_request` in assistant message metadata

**Expected Assistant Response**:
```
Before I create your meal plan, do you have any food allergies, dietary restrictions, or foods you'd like me to avoid?
```

**Expected Metadata Saved**:
```json
{
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "forced_allergy_question": true,
  "pending_meal_plan_request": "I have a student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combined strength and cardio training outside of practice. I need a 7-day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities."
}
```

### Step 2: Allergy Answer
```json
{
  "role": "user",
  "conversation_id": "test_convo_001",
  "content": "The student is allergic to tree nuts."
}
```

**Expected Backend Behavior**:
- ✅ Detects `is_allergy_answer = True` (via `detect_allergy_answer()`)
- ✅ Finds `pending_meal_plan_request` in assistant message metadata
- ✅ Forces `user_intent = "meal_plan"`
- ✅ Loads `module_meal_plan.txt` (NOT `module_lesson_plan.txt`)
- ✅ Combines original request + allergy info
- ✅ Makes OpenAI API call with combined request

---

## 2️⃣ Backend Behavior Expected

### Detection & Intent Classification
```
✅ PRE-DETECTED allergy answer: 'The student is allergic to tree nuts.'
✅ Marked as meal plan request based on allergy answer + pending request
🎯 Classified user intent: allergy_answer
✅ Intent classifier detected allergy answer
🎯 FORCED intent to 'meal_plan' because allergy_answer intent detected with pending meal plan request
🔥 DEBUG: is_allergy_answer=True, pending_meal_plan_request exists=True
```

### Module Loading
```
✅ Loading module for intent 'meal_plan': module_meal_plan.txt
✅ Loaded root system prompt
✅ Loaded module: meal_plan
✅ Loaded 2 modular prompt(s) for intent: meal_plan
📋 Module preview: ['You are **Jasper**, an advanced AI assistant...', 'MEAL PLAN WORKFLOW RULES...']
```

### Request Combination
```
🔄🔄🔄 CRITICAL: Detected allergy answer with pending meal plan request - COMBINING NOW
🔄 Detected allergy answer with pending meal plan request - combining
🔍 DEBUG: Original request: I have a student who is a 16 year old high school wrestler...
🔍 DEBUG: Allergy answer: The student is allergic to tree nuts.
✅ Combined message: I have a student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combined strength and cardio training outside of practice. I need a 7-day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities. The student is allergic to tree nuts.
```

### System Prompt Injection
```
✅ Added top priority instruction at the very beginning of system prompt
🔍 skip_allergy_reminder check: is_meal_plan_request=True, is_allergy_answer=True, skip_allergy_reminder=True
✅ Added combined request as user message
✅ Added proceed reminder message to conversation
```

### Widget Extraction
```
🔍 Widget extraction: user_intent='meal_plan', is_meal_plan_request=True
✅ Meal plan request confirmed - extracting meal plan widget data (intent: meal_plan)
Extracted meal plan data: {...}
✅ Created health widget_data with meal plan (meals: False, days: True, calories: True)
```

---

## 3️⃣ OpenAI API Call Input

### Expected Messages Array
```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "🚨🚨🚨🚨🚨 ABSOLUTE TOP PRIORITY - READ THIS FIRST 🚨🚨🚨🚨🚨\n\nTHE USER'S MESSAGE BELOW IS A COMPLETE MEAL PLAN REQUEST WITH ALLERGY INFORMATION. YOU MUST CREATE THE MEAL PLAN IMMEDIATELY.\n\nFORBIDDEN: \"Understood\", \"I will\", \"I've noted\", \"profile\", \"I have updated\", or any acknowledgment.\n\nREQUIRED: Start your response IMMEDIATELY with \"Day 1\" or \"**DAY 1:**\".\n\n...\n\n[Root system prompt + meal_plan module]"
    },
    {
      "role": "user",
      "content": "I have a student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combined strength and cardio training outside of practice. I need a 7-day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities. The student is allergic to tree nuts."
    },
    {
      "role": "user",
      "content": "I have provided my complete meal plan request above, which includes my original request plus my allergy information. CREATE THE MEAL PLAN NOW. DO NOT acknowledge the allergy. DO NOT say 'Understood' or 'I will' or 'I've noted'. DO NOT explain what you will do. DO NOT ask questions. DO NOT update profiles. START YOUR RESPONSE WITH THE MEAL PLAN (Day 1, Breakfast:...)."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.7
}
```

---

## 4️⃣ Expected OpenAI Response

### Response Format Requirements
- ✅ Starts with `Day 1:` or `**DAY 1:**`
- ✅ Lists all 7 days separately (Day 1, Day 2, ..., Day 7)
- ✅ NO placeholders (no "repeat", "for the rest", "continue this pattern")
- ✅ Each food item includes serving size and calories
- ✅ Daily totals with calories, protein, carbs, fat
- ✅ Key micronutrients for each day
- ✅ All tree nuts avoided

### Example Response Snippet
```
**DAY 1:**

**Breakfast:**
- Scrambled eggs (serving size: 2 large, 140 calories)
- Whole grain toast (serving size: 2 slices, 160 calories)
- Oatmeal with blueberries (serving size: 1 cup, 150 calories)
- Orange juice (serving size: 8 oz, 110 calories)

**Morning Snack:**
- Greek yogurt (serving size: 1 cup, 150 calories)
- Banana (serving size: 1 medium, 105 calories)

**Lunch:**
- Grilled chicken breast (serving size: 6 oz, 280 calories)
- Brown rice (serving size: 1 cup, 215 calories)
- Steamed broccoli (serving size: 1 cup, 55 calories)
- Apple (serving size: 1 medium, 95 calories)

**Afternoon Snack:**
- Protein shake (serving size: 1 serving, 200 calories)
- Granola bar (serving size: 1 bar, 150 calories)

**Dinner:**
- Baked salmon (serving size: 6 oz, 350 calories)
- Sweet potato (serving size: 1 large, 250 calories)
- Green beans (serving size: 1 cup, 44 calories)
- Whole grain roll (serving size: 1 roll, 80 calories)

**Evening Snack:**
- Cottage cheese (serving size: 1 cup, 163 calories)
- Berries (serving size: 1 cup, 85 calories)

**Daily Totals:**
- Calories: 2,378
- Protein: 185g
- Carbohydrates: 280g
- Fat: 65g

**Key Micronutrients:**
- Vitamin A: 1,200 IU
- Vitamin C: 120mg
- Vitamin D: 400 IU
- Calcium: 850mg
- Iron: 18mg
- Magnesium: 420mg
- Potassium: 3,200mg
- Zinc: 12mg

**DAY 2:**

[Similar format for all 7 days...]

**DAY 7:**

[Similar format...]
```

---

## 5️⃣ Widget Data Output

### Expected Widget Structure
```json
{
  "type": "health",
  "data": {
    "days": [
      {
        "day": "Day 1",
        "meals": [
          {
            "meal": "Breakfast",
            "foods": "Scrambled eggs (serving size: 2 large, 140 calories), Whole grain toast (serving size: 2 slices, 160 calories), Oatmeal with blueberries (serving size: 1 cup, 150 calories), Orange juice (serving size: 8 oz, 110 calories)",
            "calories": "560"
          },
          {
            "meal": "Morning Snack",
            "foods": "Greek yogurt (serving size: 1 cup, 150 calories), Banana (serving size: 1 medium, 105 calories)",
            "calories": "255"
          },
          {
            "meal": "Lunch",
            "foods": "Grilled chicken breast (serving size: 6 oz, 280 calories), Brown rice (serving size: 1 cup, 215 calories), Steamed broccoli (serving size: 1 cup, 55 calories), Apple (serving size: 1 medium, 95 calories)",
            "calories": "645"
          },
          {
            "meal": "Afternoon Snack",
            "foods": "Protein shake (serving size: 1 serving, 200 calories), Granola bar (serving size: 1 bar, 150 calories)",
            "calories": "350"
          },
          {
            "meal": "Dinner",
            "foods": "Baked salmon (serving size: 6 oz, 350 calories), Sweet potato (serving size: 1 large, 250 calories), Green beans (serving size: 1 cup, 44 calories), Whole grain roll (serving size: 1 roll, 80 calories)",
            "calories": "724"
          },
          {
            "meal": "Evening Snack",
            "foods": "Cottage cheese (serving size: 1 cup, 163 calories), Berries (serving size: 1 cup, 85 calories)",
            "calories": "248"
          }
        ],
        "daily_calories": "2,378",
        "daily_protein": "185g",
        "daily_carbs": "280g",
        "daily_fat": "65g",
        "micronutrients": "Vitamin A: 1,200 IU, Vitamin C: 120mg, Vitamin D: 400 IU, Calcium: 850mg, Iron: 18mg, Magnesium: 420mg, Potassium: 3,200mg, Zinc: 12mg"
      },
      {
        "day": "Day 2",
        "meals": [...]
      },
      ...
      {
        "day": "Day 7",
        "meals": [...]
      }
    ]
  }
}
```

### Widget Validation
- ✅ `widget_data.type` = `"health"` (NOT `"lesson-planning"`)
- ✅ `widget_data.data.days` contains exactly 7 days
- ✅ Each day has 6 meals (3 meals + 3 snacks)
- ✅ Each meal has foods with calories
- ✅ Daily totals present (calories, protein, carbs, fat)
- ✅ Micronutrients present
- ❌ NO lesson plan fields (`title`, `objectives`, `worksheets`, `rubrics`, etc.)

---

## 6️⃣ Validation Checks

### Response Validation
- ✅ Response starts with `Day 1:` or `**DAY 1:**`
- ✅ Response does NOT start with acknowledgment ("Understood", "I will", etc.)
- ✅ Exactly 7 days listed separately
- ✅ NO placeholder text ("repeat", "for the rest", "continue this pattern")
- ✅ Each food item includes serving size and calories
- ✅ Daily totals present for each day
- ✅ Micronutrients present for each day
- ✅ All tree nuts avoided (no almonds, walnuts, pecans, cashews, etc.)

### Backend Validation
- ✅ `is_meal_plan_request = True`
- ✅ `is_allergy_answer = True`
- ✅ `pending_meal_plan_request` found in metadata
- ✅ `user_intent = "meal_plan"` (forced)
- ✅ `module_meal_plan.txt` loaded (NOT `module_lesson_plan.txt`)
- ✅ Combined message created correctly
- ✅ Meal plan widget data extracted
- ✅ NO lesson plan widget data extracted

### Log Validation
Check logs for these key messages:
```
✅ PRE-DETECTED allergy answer: 'The student is allergic to tree nuts.'
✅ Marked as meal plan request based on allergy answer + pending request
🎯 FORCED intent to 'meal_plan' because allergy_answer intent detected with pending meal plan request
✅ Loading module for intent 'meal_plan': module_meal_plan.txt
✅ Loaded 2 modular prompt(s) for intent: meal_plan
🔄🔄🔄 CRITICAL: Detected allergy answer with pending meal plan request - COMBINING NOW
✅ Combined message: [combined request]
✅ Meal plan request confirmed - extracting meal plan widget data (intent: meal_plan)
✅ Created health widget_data with meal plan
```

---

## 7️⃣ Test Execution Steps

### Manual Testing (Docker)
1. Start Docker containers: `docker compose up -d`
2. Open frontend in browser
3. Send first message: "I have a student who is a 16 year old high school wrestler..."
4. Verify allergy question appears (NO API CALL)
5. Check backend logs for `pending_meal_plan_request` saved
6. Send second message: "The student is allergic to tree nuts."
7. Verify meal plan is generated immediately (NO acknowledgment)
8. Check backend logs for intent forcing and module loading
9. Verify widget data is `health` type (NOT `lesson-planning`)
10. Verify response has 7 days, no placeholders, all requirements met

### Automated Testing (Future)
```python
def test_meal_plan_workflow_with_allergy():
    # Step 1: Send meal plan request
    response1 = send_chat_message(
        "I have a student who is a 16 year old high school wrestler..."
    )
    assert "allergy" in response1.lower()
    assert response1.token_count == 0  # Hardcoded, no API call
    
    # Step 2: Send allergy answer
    response2 = send_chat_message(
        "The student is allergic to tree nuts.",
        conversation_id=response1.conversation_id
    )
    
    # Validate response
    assert response2.startswith("Day 1") or response2.startswith("**DAY 1:**")
    assert "understood" not in response2.lower()
    assert "I will" not in response2.lower()
    assert response2.count("Day") >= 7
    assert "repeat" not in response2.lower()
    assert "for the rest" not in response2.lower()
    
    # Validate widget data
    assert response2.widget_data.type == "health"
    assert len(response2.widget_data.data.days) == 7
    assert "title" not in response2.widget_data.data  # No lesson plan fields
    assert "objectives" not in response2.widget_data.data
```

---

## 8️⃣ Common Failure Modes & Debugging

### Failure: Wrong Widget Type (Lesson Plan)
**Symptom**: Widget data contains `title`, `objectives`, `worksheets`
**Cause**: Lesson plan detection triggered (keyword "student" matched)
**Fix**: Verify `is_meal_plan_request` is checked BEFORE lesson plan detection

### Failure: No Meal Plan Generated
**Symptom**: Response is acknowledgment or asks for more info
**Cause**: System prompt not strong enough or combined message not sent
**Fix**: Check logs for "COMBINING NOW" and verify combined message in API call

### Failure: Only 2 Days Generated
**Symptom**: Response has placeholders or only partial days
**Cause**: Validation failed but correction prompt not working
**Fix**: Check `meal_plan_reminder` is defined and correction_messages are correct

### Failure: Wrong Module Loaded
**Symptom**: Logs show `module_lesson_plan.txt` instead of `module_meal_plan.txt`
**Cause**: Intent not forced to `meal_plan` or `INTENT_MODULE_MAPPING` incorrect
**Fix**: Verify intent forcing logic and `INTENT_MODULE_MAPPING` in `prompt_loader.py`

### Failure: Metadata Not Found
**Symptom**: Logs show "NO pending meal plan request found"
**Cause**: Metadata saved to wrong field (`metadata` vs `conversation_metadata`)
**Fix**: Verify all references use `conversation_metadata` (not `metadata`)

---

## 9️⃣ Success Criteria

✅ **All validation checks pass**
✅ **Response starts with Day 1 (no acknowledgment)**
✅ **7 days listed separately (no placeholders)**
✅ **Each food item has serving size + calories**
✅ **Daily totals present (calories, macros, micronutrients)**
✅ **All allergens avoided**
✅ **Widget data is `health` type (NOT `lesson-planning`)**
✅ **Backend logs show correct intent forcing and module loading**
✅ **No errors in backend logs**

---

## 🔟 Next Steps After Test Passes

1. Document any edge cases discovered
2. Add automated test to test suite
3. Test with other allergens (peanuts, shellfish, dairy, etc.)
4. Test with multiple allergens
5. Test with "no allergies" response
6. Test with partial meal plan requests (missing days, etc.)

---

**Last Updated**: 2025-01-23
**Test Status**: Ready for execution
**Test Environment**: Docker (local)

