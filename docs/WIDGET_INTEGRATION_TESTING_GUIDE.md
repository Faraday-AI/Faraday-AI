# Widget Integration Testing Guide

## Overview

This guide provides step-by-step instructions for testing the complete widget handler integration, including GPT function widgets, meal/lesson/workout extraction, and error handling.

**Last Updated:** After Docker rebuild with widget handler integration

---

## Quick Reference

### 🚀 Start Here
1. **First Test (Recommended):** Test 1.1 - Attendance Patterns
2. **Quick Validation:** `docker compose logs app | tail -20` before each test
3. **Performance Tracking:** Record response times in Performance Metrics Summary

### 📋 Test Phases
- **Phase 1:** Core Widget Routing (Tests 1.1-1.3) - ~5 minutes
- **Phase 2:** Error Handling (Tests 2.1-2.2) - ~3 minutes
- **Phase 3:** Complex Widgets (Tests 3.1-3.2) - ~5 minutes
- **Phase 4:** Response-Based Extraction (Tests 4.1-4.3) - ~15 minutes
- **Phase 5:** Not Implemented (Test 5.1) - ~1 minute
- **Phase 6:** Combined Tests (Tests 6.1-6.3) - ~10 minutes
- **Phase 7:** Caching Tests (Tests 7.1-7.2) - ~5 minutes

**Total Estimated Time:** ~45 minutes for complete test suite

### 🔍 Quick Commands
```bash
# Watch widget routing
docker compose logs -f app | grep -i "widget\|intent\|routed"

# Check for errors
docker compose logs -f app | grep -i "error\|failed\|exception"

# Sanity check before test
docker compose logs app | tail -20
```

---

## Pre-Testing Checklist

Before starting, verify:
- [ ] Docker containers are running (`docker compose ps`)
- [ ] No errors in startup logs (`docker compose logs app | tail -50`)
- [ ] Admin users are created (check login works)
- [ ] Browser console is open (F12 → Console tab)
- [ ] Network tab is open (F12 → Network tab, filter by "chat")
- [ ] If code changes aren't being picked up: `docker compose restart app`

---

## Before/After Each Test Sanity Check

**Before Each Test:**
```bash
# Quick sanity check - verify app is healthy
docker compose logs app | tail -20
```

Look for:
- ✅ No recent errors
- ✅ App is running normally
- ✅ No import errors
- ✅ Database connections healthy

**After Each Test:**
```bash
# Check for any errors introduced by the test
docker compose logs app | tail -30 | grep -i "error\|exception\|failed"
```

If errors found:
- Document the error
- Check if it's related to the test
- Proceed to troubleshooting section

---

## Test Execution Order

### ✅ Phase 1: Core Widget Routing (Quick Wins)

#### Test 1.1: Attendance Patterns Widget

**Purpose:** Validate basic widget routing, intent classification, parameter extraction, and async backend calls.

**Ask Jasper:**
```
Show me the attendance patterns for period 3 for the next 30 days.
```

**Expected Results:**
- ✅ Intent classified as `"attendance"` or `"widget"`
- ✅ Class period extracted: `"3"`
- ✅ `predict_attendance_patterns()` called with correct parameters
- ✅ Widget data returned in response

**What to Check:**
1. **Browser Console:** Look for widget data in response
2. **Docker Logs:** 
   ```
   ✅ Routed GPT function widget: attendance -> attendance
   ✅ Created GPT function widget: attendance
   ```
3. **Response:** Should contain attendance predictions, at-risk students, recommendations

**Success Criteria:**
- [ ] No errors in logs
- [ ] Widget data structure returned
- [ ] Response contains attendance information

**If It Fails:**
- Check logs for: `❌ Error handling GPT function widget`
- Verify class period extraction worked
- Check if `class_id` or `period` is required

---

#### Test 1.2: Team Generator Widget

**Purpose:** Test parameter extraction (team count, activity type) and team configuration backend call.

**Ask Jasper:**
```
Make 4 balanced teams for period 2 for a basketball activity.
```

**Expected Results:**
- ✅ Intent classified as `"teams"`
- ✅ `team_count` extracted: `4`
- ✅ `activity_type` extracted: `"basketball"`
- ✅ `period` extracted: `"2"`
- ✅ `suggest_team_configurations()` called
- ✅ Widget data with team suggestions returned

**What to Check:**
1. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: teams -> teams
   ```
2. **Response:** Should contain team configuration suggestions

**Success Criteria:**
- [ ] Team count correctly extracted
- [ ] Activity type correctly identified
- [ ] Team configuration data returned

---

#### Test 1.3: Safety Widget

**Purpose:** Test auto class resolution from period and safety risk identification.

**Ask Jasper:**
```
Are there any safety risks for period 1 during a weightlifting unit?
```

**Expected Results:**
- ✅ Intent classified as `"safety"`
- ✅ Period extracted: `"1"`
- ✅ Class ID auto-resolved from period
- ✅ `identify_safety_risks()` called
- ✅ Safety risk data returned

**What to Check:**
1. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: safety -> safety
   ```
2. **Response:** Should contain identified safety risks and recommendations

**Success Criteria:**
- [ ] Class ID found from period
- [ ] Safety risks identified
- [ ] Recommendations provided

---

### ✅ Phase 2: Error Handling & Edge Cases

#### Test 2.1: Adaptive PE (Missing Student ID)

**Purpose:** Test error handling for missing required parameters.

**Ask Jasper:**
```
Suggest adaptive accommodations for dodgeball.
```

**Expected Results:**
- ✅ Intent classified as `"adaptive"`
- ✅ Error detected: `student_id` required
- ✅ User-friendly error message returned

**What to Check:**
1. **Response:** Should say something like:
   ```
   "Student ID required for adaptive accommodations"
   ```
2. **Docker Logs:**
   ```
   ⚠️ Student ID required for adaptive accommodations
   ```

**Success Criteria:**
- [ ] Error message is clear and helpful
- [ ] No crash or exception
- [ ] User knows what's missing

---

#### Test 2.2: Adaptive PE (With Student ID)

**Purpose:** Test successful adaptive accommodations with required parameter.

**Ask Jasper:**
```
Suggest adaptive accommodations for student 1123 for dodgeball.
```

**Expected Results:**
- ✅ Intent classified as `"adaptive"`
- ✅ `student_id` extracted: `1123`
- ✅ `activity_type` extracted: `"dodgeball"`
- ✅ `suggest_adaptive_accommodations()` called
- ✅ Accommodation suggestions returned

**What to Check:**
1. **Response:** Should contain equipment modifications, activity adaptations, safety considerations
2. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: adaptive -> adaptive_pe
   ```

**Success Criteria:**
- [ ] Student ID correctly extracted
- [ ] Accommodations provided
- [ ] Structured data returned

---

### ✅ Phase 3: Complex Widgets

#### Test 3.1: Class Insights Widget

**Purpose:** Test comprehensive data aggregation from multiple widgets.

**Ask Jasper:**
```
Give me a full class insights summary for period 4.
```

**Expected Results:**
- ✅ Intent classified as `"class_insights"`
- ✅ Period extracted: `"4"`
- ✅ Class ID auto-resolved
- ✅ `generate_comprehensive_insights()` called
- ✅ Comprehensive insights combining attendance, performance, health data

**What to Check:**
1. **Response:** Should contain combined insights from multiple data sources
2. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: class_insights -> class_insights
   ```

**Success Criteria:**
- [ ] Multiple data sources combined
- [ ] Insights are comprehensive
- [ ] Recommendations provided

---

#### Test 3.2: Driver's Ed Lesson Creator

**Purpose:** Test topic extraction and required field validation.

**Ask Jasper:**
```
Create a driver's ed lesson about parallel parking.
```

**Expected Results:**
- ✅ Intent classified as `"drivers_ed"`
- ✅ Topic extracted: `"parallel parking"`
- ✅ Title auto-generated from topic
- ✅ `create_drivers_ed_lesson_plan()` called
- ✅ Lesson plan created and saved

**What to Check:**
1. **Response:** Should contain complete lesson plan
2. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: drivers_ed -> drivers_ed
   ```

**Success Criteria:**
- [ ] Topic correctly extracted
- [ ] Lesson plan created
- [ ] All required fields present

---

### ✅ Phase 4: Response-Based Extraction Workflows

#### Test 4.1: Meal Plan Workflow (Full Multi-Step)

**Purpose:** Test complete meal plan workflow with allergy handling and widget extraction.

**Step 1 - Trigger Meal Plan Intent:**

**Ask Jasper:**
```
Can you make me a 7-day meal plan?
```

**Expected Results:**
- ✅ Intent classified as `"meal_plan"`
- ✅ Jasper MUST ask: "Do you have any food allergies or dietary restrictions?"
- ✅ `pending_meal_plan_request` stored in metadata

**Step 2 - Provide Allergies:**

**Ask Jasper:**
```
I'm allergic to peanuts.
```

**Expected Results:**
- ✅ Intent classified as `"allergy_answer"` then forced to `"meal_plan"`
- ✅ `previous_asked_allergies` set to `True`
- ✅ `allergy_info` stored: `"I'm allergic to peanuts"`
- ✅ Original request + allergy info combined
- ✅ Meal plan generated immediately (NO acknowledgment)
- ✅ Meal plan starts with "Day 1" or "**DAY 1:**"
- ✅ Widget data extracted using `widget_handler.extract_widget("meal_plan", ...)`

**What to Check:**
1. **First Response:** Must ask about allergies
2. **Second Response:** Must start with meal plan (not acknowledgment)
3. **Widget Data:** Should contain structured meal plan data
4. **Docker Logs:**
   ```
   🎯 Classified user intent: meal_plan
   ✅ Meal plan request confirmed - extracting meal plan widget data
   ```

**Success Criteria:**
- [ ] Allergy question asked first
- [ ] No acknowledgment after allergy answer
- [ ] Meal plan generated immediately
- [ ] Widget data extracted correctly
- [ ] All 7 days listed separately
- [ ] Calories included for every food item

---

#### Test 4.2: Lesson Plan Workflow

**Purpose:** Test comprehensive lesson plan extraction with validation.

**Ask Jasper:**
```
Create a 5th grade PE lesson plan for volleyball.
```

**Expected Results:**
- ✅ Intent classified as `"lesson_plan"`
- ✅ Comprehensive lesson plan generated
- ✅ All 14 required components present:
  1. Title
  2. Lesson Description
  3. Learning Objectives
  4. Standards (with codes)
  5. Materials List
  6. Introduction
  7. Activities (with time allocations)
  8. Assessment (formative + summative)
  9. Exit Ticket
  10. Extensions
  11. Safety Considerations
  12. Homework (if applicable)
  13. Danielson Framework Alignment (all 4 domains)
  14. Costa's Levels of Questioning (all 3 levels)
- ✅ Widget data extracted using `widget_handler.extract_widget("lesson_plan", ...)`
- ✅ Worksheets and rubrics generated in separate calls

**What to Check:**
1. **Response:** Should contain all 14 components
2. **Widget Data:** Should contain structured lesson plan data
3. **Docker Logs:**
   ```
   ✅ Loaded module for intent 'lesson_plan'
   ✅ Created comprehensive lesson plan widget_data
   ```

**Success Criteria:**
- [ ] All 14 components present
- [ ] Standards have codes and descriptions
- [ ] Activities have time allocations
- [ ] Widget data extracted correctly
- [ ] Worksheets and rubrics generated

---

#### Test 4.3: Workout Workflow

**Purpose:** Test workout plan extraction and structured data return.

**Ask Jasper:**
```
Create a 3-day workout plan.
```

**Expected Results:**
- ✅ Intent classified as `"workout"`
- ✅ Structured workout plan generated
- ✅ Includes: Warm-up, Main Workout, Cool Down
- ✅ Exercises with sets and reps
- ✅ Widget data extracted using `widget_handler.extract_widget("workout", ...)`

**What to Check:**
1. **Response:** Should contain structured workout plan
2. **Widget Data:** Should contain exercises with sets/reps
3. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: workout -> workout
   ```

**Success Criteria:**
- [ ] All workout sections present
- [ ] Exercises have sets and reps
- [ ] Widget data extracted correctly

---

### ✅ Phase 5: Not Implemented Widgets

#### Test 5.1: Notifications Widget (Not Implemented)

**Purpose:** Test graceful handling of widgets that don't have backend services yet.

**Ask Jasper:**
```
Send notifications to all parents.
```

**Expected Results:**
- ✅ Intent classified as `"notifications"` or `"widget"`
- ✅ Widget routed to `_handle_gpt_function_widget()`
- ✅ Returns: `{"type": "notifications", "status": "not_implemented", "message": "..."}`
- ✅ No crash or error

**What to Check:**
1. **Response:** Should indicate service not yet implemented
2. **Docker Logs:**
   ```
   ✅ Routed GPT function widget: notifications -> notifications
   ```

**Success Criteria:**
- [ ] Graceful error message
- [ ] No crash
- [ ] User informed service is not available

---

## Combined Test (Optional)

### Test 6.1: Multiple Widgets in Single Request

If you want to test multiple widgets in one conversation:

**Ask Jasper:**
```
Show me attendance patterns for period 3, then create 4 balanced teams for period 2 for basketball, and identify any safety risks for period 1.
```

**Expected Results:**
- ✅ Multiple widget intents detected
- ✅ Each widget processed separately
- ✅ Multiple widget data objects returned
- ✅ All widgets in `widgets` array

**What to Check:**
1. **Response:** Should address all three requests
2. **Widget Data:** Should contain multiple widgets
3. **Docker Logs:** Should show routing for all three widgets

---

### Test 6.2: Cross-Widget Multi-Step Conversation (Context Retention)

**Purpose:** Test that Jasper maintains context across multiple widget requests in a conversation.

**Step 1 - Initial Request:**

**Ask Jasper:**
```
Show me attendance patterns for period 3.
```

**Step 2 - Follow-up Request (Uses Context):**

**Ask Jasper:**
```
Now create 4 balanced teams for that same class.
```

**Expected Results:**
- ✅ Jasper remembers "period 3" from previous message
- ✅ Uses same class/period for team creation
- ✅ Context maintained across widget types
- ✅ No need to re-specify period

**Step 3 - Another Follow-up:**

**Ask Jasper:**
```
What are the safety risks for that class?
```

**Expected Results:**
- ✅ Still uses period 3 context
- ✅ Safety analysis for same class
- ✅ Context retention working

**What to Check:**
1. **Response:** Should reference previous context
2. **Docker Logs:** Should show period extracted from conversation history
3. **Context:** Verify `conversation_id` is same for all messages

**Success Criteria:**
- [ ] Context maintained across multiple widget requests
- [ ] No need to re-specify parameters
- [ ] Conversation history properly used

---

### Test 6.3: Widget + Extraction Workflow Combination

**Purpose:** Test combining GPT function widget with response-based extraction in one conversation.

**Step 1 - Widget Request:**

**Ask Jasper:**
```
Show me attendance patterns for period 2.
```

**Step 2 - Follow-up with Extraction Widget:**

**Ask Jasper:**
```
Now create a lesson plan for that class on basketball fundamentals.
```

**Expected Results:**
- ✅ Attendance widget processed first
- ✅ Lesson plan generated for same class
- ✅ Lesson plan widget data extracted
- ✅ Both widgets returned in response

**What to Check:**
1. **Response:** Should contain both widget types
2. **Widget Data:** Should have both attendance and lesson_planning widgets
3. **Docker Logs:** Should show both widget types processed

**Success Criteria:**
- [ ] Multiple widget types in one conversation
- [ ] Context shared between widgets
- [ ] All widget data extracted correctly

---

## Troubleshooting Guide

### Issue: Widget Not Detected

**Symptoms:**
- Intent classified as `"general"` instead of widget type
- No widget data returned

**Check:**
1. Verify intent classification in logs: `🎯 Classified user intent: ...`
2. Check if widget keywords are in message
3. Verify `widget_handler.classify_intent()` is being called

**Fix:**
- Add more specific keywords to user message
- Check `widget_handler.py` keyword lists

---

### Issue: Async Call Fails

**Symptoms:**
- Error: "Event loop already running"
- Widget returns `"requires_async_call"` status

**Check:**
1. Look for: `⚠️ Event loop already running - async call deferred`
2. Check if `run_async()` helper is working

**Fix:**
- This is expected if event loop is running
- May need to convert `send_chat_message` to async

---

### Issue: Missing Required Parameters

**Symptoms:**
- Error message: "Student ID required" or "Class ID required"
- Widget returns error status

**Check:**
1. Verify parameter extraction in logs
2. Check if user message contains required info

**Fix:**
- Provide required parameters in message
- Or use kwargs if calling directly

---

### Issue: Widget Data Not Extracted

**Symptoms:**
- Response text is good, but no widget data
- `widget_data` is `None` in response

**Check:**
1. Verify `widget_handler.extract_widget()` is called
2. Check extraction regex patterns
3. Verify response format matches extraction patterns

**Fix:**
- Check response format matches expected patterns
- Verify extraction functions in `widget_handler.py`

---

### Issue: Meal Plan Acknowledgment Error

**Symptoms:**
- Jasper acknowledges allergy instead of creating meal plan
- Response starts with "Understood" or "I have updated"

**Check:**
1. Look for: `🚨 VALIDATION FAILED: Response starts with acknowledgment`
2. Check if `pending_meal_plan_request` was found
3. Verify allergy answer was detected

**Fix:**
- Check metadata storage/retrieval
- Verify intent forcing logic
- Check system message ordering

---

## Log Monitoring Commands

### Watch Widget Routing
```bash
docker compose logs -f app | grep -i "widget\|intent\|routed"
```

### Watch for Errors
```bash
docker compose logs -f app | grep -i "error\|failed\|exception"
```

### Watch Intent Classification
```bash
docker compose logs -f app | grep -i "classified user intent"
```

### Watch Widget Extraction
```bash
docker compose logs -f app | grep -i "extracting.*widget\|widget.*extract"
```

---

## Success Indicators

After completing all tests, you should see:

✅ **Intent Classification Working:**
- All intents correctly classified
- Allergy detection working
- Widget intents properly identified

✅ **Widget Routing Working:**
- All 9 implemented widgets route correctly
- Error handling for missing parameters
- Graceful handling of not-implemented widgets

✅ **Widget Extraction Working:**
- Meal plan data extracted correctly
- Lesson plan data extracted correctly
- Workout data extracted correctly

✅ **Backend Calls Working:**
- Async methods called successfully
- Widget data returned from services
- No event loop errors

✅ **Error Handling Working:**
- Clear error messages for missing parameters
- No crashes or exceptions
- Graceful degradation

---

## Test Results Template

Use this to track your progress:

```
Test 1.1: Attendance Patterns
[ ] Passed
[ ] Failed - Notes: _______________

Test 1.2: Team Generator
[ ] Passed
[ ] Failed - Notes: _______________

Test 1.3: Safety Widget
[ ] Passed
[ ] Failed - Notes: _______________

Test 2.1: Adaptive PE (Missing Student ID)
[ ] Passed
[ ] Failed - Notes: _______________

Test 2.2: Adaptive PE (With Student ID)
[ ] Passed
[ ] Failed - Notes: _______________

Test 3.1: Class Insights
[ ] Passed
[ ] Failed - Notes: _______________

Test 3.2: Driver's Ed
[ ] Passed
[ ] Failed - Notes: _______________

Test 4.1: Meal Plan Workflow
[ ] Passed
[ ] Failed - Notes: _______________

Test 4.2: Lesson Plan Workflow
[ ] Passed
[ ] Failed - Notes: _______________

Test 4.3: Workout Workflow
[ ] Passed
[ ] Failed - Notes: _______________

Test 5.1: Notifications (Not Implemented)
[ ] Passed
[ ] Failed - Notes: _______________

Test 6.1: Multiple Widgets in Single Request
[ ] Passed
[ ] Failed - Notes: _______________

Test 6.2: Cross-Widget Multi-Step Conversation
[ ] Passed
[ ] Failed - Notes: _______________

Test 6.3: Widget + Extraction Workflow Combination
[ ] Passed
[ ] Failed - Notes: _______________

Test 7.1: Widget Response Caching
[ ] Passed
[ ] Failed - Notes: _______________

Test 7.2: Parameter-Based Cache Invalidation
[ ] Passed
[ ] Failed - Notes: _______________

---

## Performance Metrics Summary

Record average response times for each widget type:

| Widget Type | Test # | Response Time (ms) | Status |
|------------|--------|-------------------|--------|
| Attendance | 1.1 | _____ | [ ] Pass / [ ] Fail |
| Teams | 1.2 | _____ | [ ] Pass / [ ] Fail |
| Safety | 1.3 | _____ | [ ] Pass / [ ] Fail |
| Adaptive PE | 2.2 | _____ | [ ] Pass / [ ] Fail |
| Class Insights | 3.1 | _____ | [ ] Pass / [ ] Fail |
| Driver's Ed | 3.2 | _____ | [ ] Pass / [ ] Fail |
| Meal Plan | 4.1 | _____ | [ ] Pass / [ ] Fail |
| Lesson Plan | 4.2 | _____ | [ ] Pass / [ ] Fail |
| Workout | 4.3 | _____ | [ ] Pass / [ ] Fail |

**Average Response Time:** _____ ms

**Slowest Widget:** _______________ (_____ ms)

**Fastest Widget:** _______________ (_____ ms)
```

---

---

## Performance Monitoring

### Response Time Tracking

For each widget test, record the response time:

**How to Measure:**
1. Open browser Network tab (F12 → Network)
2. Filter by "chat" endpoint
3. Check `processing_time_ms` in response
4. Record in test results

**Expected Response Times:**
- **Simple Widgets (Attendance, Teams):** < 3 seconds
- **Complex Widgets (Class Insights):** < 5 seconds
- **Meal Plan (with extraction):** < 8 seconds
- **Lesson Plan (with worksheets/rubrics):** < 15 seconds
- **Workout Plan:** < 5 seconds

**Performance Test Template:**
```
Test 1.1: Attendance Patterns
Response Time: _____ ms
[ ] Within expected range (< 3000ms)
[ ] Slow (> 5000ms) - Notes: _______________

Test 1.2: Team Generator
Response Time: _____ ms
[ ] Within expected range (< 3000ms)
[ ] Slow (> 5000ms) - Notes: _______________
```

### Async Call Performance

Monitor async backend calls:

**Check Logs:**
```bash
docker compose logs app | grep -i "async\|processing_time"
```

**What to Look For:**
- Async calls completing successfully
- No timeout errors
- Reasonable processing times

### Performance Bottlenecks

If response times are slow, check:
1. **Database Queries:** Are queries optimized?
2. **Async Calls:** Are they completing quickly?
3. **Widget Extraction:** Is regex extraction fast?
4. **OpenAI API:** Is response generation slow?

---

## Caching Tests

### Test 7.1: Widget Response Caching

**Purpose:** Test if repeated widget requests are cached (if caching is implemented).

**Step 1 - Initial Request:**

**Ask Jasper:**
```
Show me attendance patterns for period 3.
```

**Record:** Response time and data

**Step 2 - Repeat Same Request:**

**Ask Jasper:**
```
Show me attendance patterns for period 3.
```

**Expected Results (If Caching Enabled):**
- ✅ Faster response time (cached)
- ✅ Same data returned
- ✅ Cache hit logged

**Expected Results (If Caching Disabled):**
- ✅ Similar response time
- ✅ Fresh data (may differ slightly)
- ✅ No cache hit logged

**What to Check:**
1. **Response Time:** Compare first vs second request
2. **Docker Logs:** Look for cache hit/miss messages
3. **Data:** Verify data is correct (cached or fresh)

**Success Criteria:**
- [ ] Caching behavior matches implementation
- [ ] No stale data returned
- [ ] Performance improved if caching enabled

---

### Test 7.2: Parameter-Based Cache Invalidation

**Purpose:** Test that cache is invalidated when parameters change.

**Step 1 - Request with Period 3:**

**Ask Jasper:**
```
Show me attendance patterns for period 3.
```

**Step 2 - Request with Period 4:**

**Ask Jasper:**
```
Show me attendance patterns for period 4.
```

**Expected Results:**
- ✅ Different data returned (different period)
- ✅ Cache not used (different parameters)
- ✅ Fresh data for period 4

**What to Check:**
1. **Data:** Should be different for different periods
2. **Logs:** Should show cache miss or fresh query
3. **Response Time:** Should be similar to first request

**Success Criteria:**
- [ ] Cache properly invalidated for different parameters
- [ ] Correct data for each parameter set
- [ ] No data leakage between cached entries

---

## Next Steps After Testing

1. **If All Tests Pass:**
   - Integration is production-ready
   - Can proceed with additional widget implementations
   - Consider adding more parameter extraction logic
   - Review performance metrics and optimize if needed

2. **If Tests Fail:**
   - Document specific failures
   - Check logs for error details
   - Review integration points
   - Fix issues and retest

3. **Performance Optimization:**
   - Monitor response times
   - Check async call performance
   - Consider caching for frequently accessed widgets
   - Optimize slow database queries
   - Review OpenAI API usage patterns

4. **Caching Implementation:**
   - If caching not yet implemented, consider adding it
   - Test cache invalidation strategies
   - Monitor cache hit rates
   - Optimize cache TTL values

---

**Ready to start testing!** Begin with Test 1.1 (Attendance Patterns) and work through each test systematically.

