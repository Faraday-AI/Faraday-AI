# Meal Plan Workflow Test Checklist
## Quick Reference for Testing

Use this checklist when testing the meal plan workflow to ensure all components work correctly.

---

## Pre-Test Setup
- [ ] Docker containers running (`docker compose up -d`)
- [ ] Backend logs visible (`docker compose logs -f app`)
- [ ] Frontend accessible in browser
- [ ] Clear conversation history (new conversation)

---

## Test Step 1: Initial Meal Plan Request

**User Input:**
```
I have a student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combined strength and cardio training outside of practice. I need a 7-day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities.
```

**Expected Results:**
- [ ] Response: "Before I create your meal plan, do you have any food allergies..."
- [ ] `token_count = 0` (hardcoded response, no API call)
- [ ] `processing_time_ms = 0`
- [ ] Backend logs show: `forced_allergy_question: True`
- [ ] Backend logs show: `pending_meal_plan_request` saved in metadata
- [ ] Conversation ID saved in sessionStorage (frontend)

---

## Test Step 2: Allergy Answer

**User Input:**
```
The student is allergic to tree nuts.
```

**Expected Backend Logs:**
- [ ] `✅ PRE-DETECTED allergy answer: 'The student is allergic to tree nuts.'`
- [ ] `✅ Marked as meal plan request based on allergy answer + pending request`
- [ ] `🎯 Classified user intent: allergy_answer`
- [ ] `🎯 FORCED intent to 'meal_plan' because allergy_answer intent detected with pending meal plan request`
- [ ] `✅ Loading module for intent 'meal_plan': module_meal_plan.txt`
- [ ] `✅ Loaded 2 modular prompt(s) for intent: meal_plan`
- [ ] `🔄🔄🔄 CRITICAL: Detected allergy answer with pending meal plan request - COMBINING NOW`
- [ ] `✅ Combined message: [original request + allergy info]`
- [ ] `✅ Meal plan request confirmed - extracting meal plan widget data (intent: meal_plan)`
- [ ] `✅ Created health widget_data with meal plan`

**Expected Response:**
- [ ] Response starts with `Day 1:` or `**DAY 1:**`
- [ ] Response does NOT start with "Understood", "I will", "I've noted", etc.
- [ ] Response does NOT contain "profile" or "updated"
- [ ] Response contains exactly 7 days (Day 1 through Day 7)
- [ ] NO placeholder text ("repeat", "for the rest", "continue this pattern")
- [ ] Each food item includes serving size and calories
- [ ] Daily totals present (calories, protein, carbs, fat)
- [ ] Micronutrients present for each day
- [ ] All tree nuts avoided (no almonds, walnuts, pecans, cashews, etc.)

---

## Widget Data Validation

**Check widget_data in response:**
- [ ] `widget_data.type = "health"` (NOT `"lesson-planning"`)
- [ ] `widget_data.data.days` exists and has 7 items
- [ ] Each day has 6 meals (3 meals + 3 snacks)
- [ ] Each meal has `foods` and `calories` fields
- [ ] Daily totals present (`daily_calories`, `daily_protein`, etc.)
- [ ] Micronutrients present
- [ ] NO lesson plan fields (`title`, `objectives`, `worksheets`, `rubrics`, `assessments`)

---

## Common Issues & Quick Fixes

### Issue: Wrong Widget Type (Lesson Plan)
**Check:**
- [ ] Backend logs show `is_meal_plan_request = True`
- [ ] Backend logs show `user_intent = 'meal_plan'` (not `'lesson_plan'`)
- [ ] Backend logs show `module_meal_plan.txt` loaded (not `module_lesson_plan.txt`)

**Fix:** Verify lesson plan detection happens AFTER meal plan check

---

### Issue: No Meal Plan Generated (Acknowledgment Instead)
**Check:**
- [ ] Backend logs show "COMBINING NOW"
- [ ] Backend logs show combined message created
- [ ] Backend logs show "proceed reminder" added to messages
- [ ] System prompt includes "ABSOLUTE TOP PRIORITY" instruction

**Fix:** Verify system prompt injection and proceed reminder are working

---

### Issue: Only 2 Days Generated (Placeholders)
**Check:**
- [ ] Validation detected missing days
- [ ] Correction prompt triggered
- [ ] `meal_plan_reminder` defined correctly
- [ ] Correction API call made

**Fix:** Check validation logic and correction_messages construction

---

### Issue: Metadata Not Found
**Check:**
- [ ] Backend logs show "FOUND pending_meal_plan_request"
- [ ] Metadata saved to `conversation_metadata` (not `metadata`)
- [ ] Conversation ID matches between requests
- [ ] Frontend persists conversation_id in sessionStorage

**Fix:** Verify all metadata references use `conversation_metadata`

---

### Issue: Wrong Module Loaded
**Check:**
- [ ] Backend logs show correct intent: `meal_plan`
- [ ] `INTENT_MODULE_MAPPING` in `prompt_loader.py` is correct
- [ ] `allergy_answer` maps to `module_meal_plan.txt`

**Fix:** Verify `INTENT_MODULE_MAPPING` and intent forcing logic

---

## Success Criteria

**All of the following must be true:**
- [ ] Response starts with Day 1 (no acknowledgment)
- [ ] 7 days listed separately (no placeholders)
- [ ] Each food item has serving size + calories
- [ ] Daily totals present (calories, macros, micronutrients)
- [ ] All allergens avoided
- [ ] Widget data is `health` type (NOT `lesson-planning`)
- [ ] Backend logs show correct intent forcing and module loading
- [ ] No errors in backend logs
- [ ] Response time is reasonable (< 10 seconds)

---

## Test Results

**Date:** _______________
**Tester:** _______________
**Environment:** Docker / Production
**Status:** ✅ Pass / ❌ Fail

**Notes:**
```
[Add any observations, issues, or edge cases discovered during testing]
```

---

**Quick Test Commands:**

```bash
# View backend logs
docker compose logs -f app

# Rebuild Docker (if needed)
docker compose down
docker compose build --no-cache
docker compose up -d

# Check conversation metadata in database
docker compose exec db psql -U postgres -d faraday_ai -c "SELECT id, message_type, content, conversation_metadata FROM ai_assistant_messages ORDER BY created_at DESC LIMIT 5;"
```

